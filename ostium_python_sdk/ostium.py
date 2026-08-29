import decimal
import time
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from enum import Enum
from ostium_python_sdk.constants import PRECISION_2
from web3 import Web3
from .abi.usdc_abi import usdc_abi
from .abi.trading_abi import trading_abi
from .abi.trading_storage_abi import trading_storage_abi
from .abi.callbacks_abi import callbacks_abi
from .utils import convert_to_scaled_integer, fromErrorCodeToMessage, get_tp_sl_prices, to_base_units
from eth_account.account import Account


class OpenOrderType(Enum):
    MARKET = 0
    LIMIT = 1
    STOP = 2


# Emitted by the OstiumPriceUpKeep (oracle) contract for every order that
# requests a price (opens, closes, etc.); orderId is the indexed topic.
# Replaced the old PriceRequested(uint256,bytes32,uint256) event.
PRICE_REQUESTED_V2_TOPIC = Web3.keccak(
    text="PriceRequestedV2(uint256,uint8,bytes32,uint256)")

# Arbitrum sequencer feeds accept eth_sendRawTransaction directly, skipping
# third-party RPC ingestion (~1s faster than e.g. Alchemy broadcast).
DEFAULT_SEQUENCER_URLS = {
    42161: 'https://arb1-sequencer.arbitrum.io/rpc',
    421614: 'https://sepolia-rollup-sequencer.arbitrum.io/rpc',
}

# Minimal registry interface for resolving Ostium contract addresses at
# runtime (the trading contract exposes its registry).
REGISTRY_ABI = [{
    "inputs": [{"internalType": "bytes32", "name": "name", "type": "bytes32"}],
    "name": "getContractAddress",
    "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view", "type": "function",
}]

# Callbacks-contract events that settle an order; all index orderId as
# topic 1, and they land in the same tx as the oracle's price answer.
ORDER_SETTLED_EVENTS = [
    'MarketOpenExecuted', 'MarketOpenCanceled',
    'MarketCloseExecutedV2', 'MarketCloseExecuted', 'MarketCloseCanceled',
    'LimitOpenExecuted', 'LimitCloseExecuted',
    'AutomationOpenOrderCanceled', 'AutomationCloseOrderCanceled',
]

# Field groups used to format order/trade entities (raw subgraph units ->
# human units). Shared by subgraph-sourced and chain-event-sourced results.
ENTITY_PRICE_FIELDS = [
    'price', 'priceAfterImpact', 'openPrice', 'closePrice',
    'takeProfitPrice', 'stopLossPrice'
]
ENTITY_COLLATERAL_FIELDS = [
    'collateral', 'notional', 'tradeNotional', 'amountSentToTrader',
    'devFee', 'vaultFee', 'oracleFee', 'liquidationFee', 'fundingFee', 'rolloverFee'
]
ENTITY_PERCENTAGE_FIELDS = [
    'profitPercent', 'totalProfitPercent', 'priceImpactP', 'leverage', 'highestLeverage',
    'closePercent'
]


class Ostium:
    """
    Main client for interacting with the Ostium trading platform on the Arbitrum network.

    Supports opening and closing trades, managing positions, and other trading operations.
    Also supports delegation through the contract's native delegatedAction functionality,
    which allows an approved address to execute trades on behalf of another address.

    Args:
        w3: Web3 instance connected to the Arbitrum network
        usdc_address: Contract address for USDC token
        ostium_trading_storage_address: Contract address for the Ostium trading storage
        ostium_trading_address: Contract address for the Ostium trading contract
        private_key: Private key for transaction signing
        verbose: Whether to log detailed information
        use_delegation: Whether to enable the delegatedAction functionality

    Delegation Usage:
        1. Initialize the SDK with the delegate's private key
        2. Set use_delegation=True when initializing or set the use_delegation property to True later
        3. When calling trade methods, specify the trader_address parameter which is the address
           on whose behalf the transaction will be executed
        4. The delegate address must be approved at the contract level to act on behalf of the trader
        5. The trader address must have approved enough USDC allowance for the trading contract
    """

    def __init__(self, w3: Web3, usdc_address: str, ostium_trading_storage_address: str, ostium_trading_address: str, private_key: str, verbose=False, use_delegation=False, chain_id=None, submit_rpc_url=None) -> None:
        self.web3 = w3
        self.verbose = verbose
        self.private_key = private_key
        self.usdc_address = usdc_address
        self.ostium_trading_storage_address = ostium_trading_storage_address
        self.ostium_trading_address = ostium_trading_address
        self.use_delegation = use_delegation
        # Create contract instances
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address, abi=usdc_abi)
        self.ostium_trading_storage_contract = self.web3.eth.contract(
            address=self.ostium_trading_storage_address, abi=trading_storage_abi)
        self.ostium_trading_contract = self.web3.eth.contract(
            address=self.ostium_trading_address, abi=trading_abi)

        self.slippage_percentage = 2  # 2%

        # Transactions are built fully offline to avoid per-trade RPC
        # round-trips (chainId, eth_estimateGas, fee history). Gas limit is an
        # upper bound only - Arbitrum refunds unused gas. Fee caps reserve
        # balance but the actual charge is the network base fee.
        self._chain_id = chain_id
        self.gas_limit = 2_500_000
        self.max_fee_per_gas = Web3.to_wei('0.5', 'gwei')
        self.max_priority_fee_per_gas = 0
        self._allowance_cache = {}
        self._callbacks_contract = None
        # Seconds between eth_getLogs polls while waiting for the oracle to
        # settle an order (the oracle typically answers within ~1s)
        self.order_poll_interval = 0.25
        # Transactions are broadcast through a dedicated submit endpoint
        # (defaults to the network's Arbitrum sequencer feed); all reads and
        # receipt polling stay on the primary RPC. Change with
        # set_submit_rpc_url(); pass the primary RPC's URL to disable.
        self.submit_rpc_url = submit_rpc_url
        self._submit_web3 = None

    def log(self, message):
        if self.verbose:
            print(message)

    def get_opening_fee(self, trade_size, leverage, pair_id):
        pass

    def set_slippage_percentage(self, slippage_percentage):
        self.slippage_percentage = slippage_percentage

    def get_slippage_percentage(self):
        return self.slippage_percentage

    def get_public_address(self):
        public_address = self._get_account().address
        return public_address

    def _get_account(self) -> Account:
        self._check_private_key()
        """Get account from stored private key"""
        return self.web3.eth.account.from_key(self.private_key)

    def get_block_number(self):
        return self.web3.eth.get_block('latest')['number']

    def get_nonce(self, address):
        return self.web3.eth.get_transaction_count(address)

    @property
    def chain_id(self):
        if self._chain_id is None:
            self._chain_id = self.web3.eth.chain_id
        return self._chain_id

    def set_submit_rpc_url(self, url):
        """
        Set the endpoint used to broadcast transactions (reads and receipt
        polling stay on the primary RPC). Pass None to restore the default
        (the network's Arbitrum sequencer feed); pass your primary RPC URL
        to broadcast through it instead.
        """
        self.submit_rpc_url = url
        self._submit_web3 = None

    def _get_submit_web3(self):
        if self._submit_web3 is None:
            url = self.submit_rpc_url or DEFAULT_SEQUENCER_URLS.get(self.chain_id)
            if url is None:
                self._submit_web3 = self.web3
            else:
                self._submit_web3 = Web3(Web3.HTTPProvider(
                    url, request_kwargs={'timeout': 10}))
        return self._submit_web3

    def _send_signed(self, signed_tx):
        """
        Broadcast a signed transaction through the submit endpoint, falling
        back to the primary RPC if the submit endpoint errors.
        """
        raw = signed_tx.raw_transaction
        submit_w3 = self._get_submit_web3()
        if submit_w3 is not self.web3:
            try:
                return submit_w3.eth.send_raw_transaction(raw)
            except Exception as e:
                self.log(
                    f"Submit RPC failed ({e}); falling back to primary RPC")
        return self.web3.eth.send_raw_transaction(raw)

    def _get_callbacks_contract(self):
        """
        Resolve the callbacks contract through the on-chain registry (the
        trading contract exposes it), cached for the session. The callbacks
        contract emits the settlement events for every order.
        """
        if self._callbacks_contract is None:
            registry_address = self.ostium_trading_contract.functions.registry().call()
            registry = self.web3.eth.contract(
                address=registry_address, abi=REGISTRY_ABI)
            callbacks_address = registry.functions.getContractAddress(
                b'callbacks'.ljust(32, b'\0')).call()
            self._callbacks_contract = self.web3.eth.contract(
                address=callbacks_address, abi=callbacks_abi)
            self.log(f"Resolved callbacks contract: {callbacks_address}")
        return self._callbacks_contract

    async def _wait_for_order_settlement(self, order_id, from_block=None, timeout=20):
        """
        Watch the chain for the callbacks event that settles order_id
        (executed or canceled). All settlement events index orderId as
        topic 1, so a single eth_getLogs filter catches every outcome.
        Returns (event_name, event_args) or None on timeout.
        """
        callbacks = self._get_callbacks_contract()
        if from_block is None:
            # orders settle within seconds; a few minutes of lookback is ample
            from_block = max(0, self.web3.eth.block_number - 1200)
        order_topic = '0x' + format(int(order_id), '064x')
        deadline = time.monotonic() + timeout

        while True:
            logs = self.web3.eth.get_logs({
                'address': callbacks.address,
                'fromBlock': from_block,
                'toBlock': 'latest',
                'topics': [None, order_topic],
            })
            for log in logs:
                for name in ORDER_SETTLED_EVENTS:
                    event = getattr(callbacks.events, name, None)
                    if event is None:
                        continue
                    try:
                        decoded = event().process_log(log)
                    except Exception:
                        continue
                    return name, decoded['args']
            if time.monotonic() >= deadline:
                return None
            await asyncio.sleep(self.order_poll_interval)

    def _chain_settlement_to_result(self, event_name, args):
        """
        Build the {'order': ..., 'trade': ...} result from a settlement
        event, in the same shape and units as the subgraph-sourced result.
        Values are converted to subgraph raw units first so
        _format_entity_values applies uniformly. The order dict carries
        'source': 'chain' so callers can tell it apart from the (more
        detailed) subgraph payload.
        """
        executed = 'Executed' in event_name
        is_open_action = 'Open' in event_name
        order = {
            'id': str(args['orderId']),
            'orderAction': 'Open' if is_open_action else 'Close',
            'isPending': False,
            'isCancelled': not executed,
            'cancelReason': None if executed else int(args['cancelReason']),
            'source': 'chain',
        }
        trade = None

        if event_name in ('MarketOpenExecuted', 'LimitOpenExecuted'):
            t = args['t']
            # priceImpactP: 1e18-scaled percent on-chain -> 1e2-scaled (subgraph raw)
            order.update({
                'price': t['openPrice'],
                'priceAfterImpact': t['openPrice'],
                'priceImpactP': int(args['priceImpactP']) // 10**16,
                'collateral': t['collateral'],
                'leverage': t['leverage'],
                'isBuy': t['buy'],
                'tradeNotional': args['tradeNotional'],
                'pair': {'id': str(t['pairIndex'])},
            })
            trade = {
                'index': t['index'],
                'trader': t['trader'],
                'collateral': t['collateral'],
                'leverage': t['leverage'],
                'openPrice': t['openPrice'],
                'takeProfitPrice': t['tp'],
                'stopLossPrice': t['sl'],
                'isBuy': t['buy'],
                'isOpen': True,
                'pair': {'id': str(t['pairIndex'])},
            }
        elif event_name in ('MarketCloseExecutedV2', 'MarketCloseExecuted', 'LimitCloseExecuted'):
            close_percent = int(args.get('percentageClosed', 10000))
            # percentProfit: 1e6-scaled percent on-chain -> 1e2-scaled (subgraph raw)
            order.update({
                'price': args['price'],
                'priceAfterImpact': args['price'],
                'priceImpactP': int(args['priceImpactP']) // 10**16,
                'profitPercent': int(args['percentProfit']) // 10**4,
                'amountSentToTrader': args['usdcSentToTrader'],
                'closePercent': close_percent,
                'tradeID': str(args['tradeId']),
            })
            trade = {
                'tradeID': str(args['tradeId']),
                'closePrice': args['price'],
                'isOpen': close_percent < 10000,
            }
        else:
            # cancellations: MarketOpenCanceled, MarketCloseCanceled,
            # AutomationOpenOrderCanceled, AutomationCloseOrderCanceled
            if 'pairIndex' in args:
                order['pair'] = {'id': str(args['pairIndex'])}
            if 'tradeId' in args:
                order['tradeID'] = str(args['tradeId'])

        formatted_order = self._format_entity_values(
            order, ENTITY_PRICE_FIELDS, ENTITY_COLLATERAL_FIELDS, ENTITY_PERCENTAGE_FIELDS)
        formatted_trade = self._format_entity_values(
            trade, ENTITY_PRICE_FIELDS, ENTITY_COLLATERAL_FIELDS, ENTITY_PERCENTAGE_FIELDS) if trade else None
        return {'order': formatted_order, 'trade': formatted_trade}

    def _extract_order_id(self, receipt, fallback_event_names):
        """
        Pull the orderId out of a receipt. Primary source is the oracle's
        PriceRequestedV2 event (successor of PriceRequested), which is emitted
        for every price-requesting order with orderId as the indexed topic.
        Falls back to decoding the trading contract's order-initiated events.
        """
        for log in receipt.logs:
            if len(log['topics']) > 1 and bytes(log['topics'][0]) == bytes(PRICE_REQUESTED_V2_TOPIC):
                order_id = int(log['topics'][1].hex(), 16)
                self.log(f"Found orderId from PriceRequestedV2: {order_id}")
                return order_id

        from web3.logs import DISCARD
        for name in fallback_event_names:
            event = getattr(self.ostium_trading_contract.events, name, None)
            if event is None:
                continue
            entries = event().process_receipt(receipt, errors=DISCARD)
            if entries:
                order_id = entries[0]['args']['orderId']
                self.log(f"Found orderId from {name}: {order_id}")
                return order_id

        self.log("No order-initiated event found in receipt")
        return None

    def _encode_trading_call(self, fn_name, args):
        """Encode a trading-contract call locally (no RPC round-trips).
        web3 v7 renamed encodeABI to encode_abi; support both."""
        contract = self.ostium_trading_contract
        if hasattr(contract, 'encode_abi'):
            return contract.encode_abi(fn_name, args)
        return contract.encodeABI(fn_name, args)

    def _build_tx_params(self, account, nonce=None):
        """
        Transaction fields for build_transaction. Supplying chainId, gas and
        fee caps here keeps web3 from fetching each of them over RPC on every
        transaction; the nonce is the only per-transaction chain read.
        """
        if nonce is None:
            nonce = self.get_nonce(account.address)
        return {
            'from': account.address,
            'chainId': self.chain_id,
            'gas': self.gas_limit,
            'maxFeePerGas': self.max_fee_per_gas,
            'maxPriorityFeePerGas': self.max_priority_fee_per_gas,
            'nonce': nonce,
        }

    def _check_private_key(self):
        if not self.private_key:
            raise ValueError(
                "Private key is required for Ostium platform write-operations")

    def perform_trade(self, trade_params, at_price):
        self.log(f"Performing trade with params: {trade_params}")
        account = self._get_account()
        amount = to_base_units(trade_params['collateral'], decimals=6)

        # The address the trade is opened for: the trader when delegating, the signer
        # otherwise. Both the USDC allowance and the trade struct below are keyed to it.
        on_behalf_of = self._allowance_owner(
            account, trade_params.get('trader_address'))
        # Nonce and allowance are independent chain reads - fetch concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            nonce_future = executor.submit(self.get_nonce, account.address)
            allowance_future = executor.submit(
                self._check_allowance, on_behalf_of, amount)
            nonce = nonce_future.result()
            allowance_future.result()

        nonce = self.__approve(account, amount, self.use_delegation,
                               trade_params.get('trader_address'), nonce=nonce)

        try:
            self.log(f"Final trade parameters being sent: {trade_params}")
            tp_price, sl_price = get_tp_sl_prices(trade_params)

            trade = {
                'collateral': convert_to_scaled_integer(trade_params['collateral'], precision=5, scale=6),
                'openPrice': convert_to_scaled_integer(at_price),
                'tp': convert_to_scaled_integer(tp_price),
                'sl': convert_to_scaled_integer(sl_price),
                'trader': on_behalf_of,
                'leverage': to_base_units(trade_params['leverage'], decimals=2),
                'pairIndex': int(trade_params['asset_type']),
                'index': 0,
                'buy': trade_params['direction'],
                'isDayTrade': trade_params.get('is_day_trade', False)
            }

            order_type = OpenOrderType.MARKET.value

            if 'order_type' in trade_params:
                if trade_params['order_type'] == 'LIMIT':
                    order_type = OpenOrderType.LIMIT.value
                elif trade_params['order_type'] == 'STOP':
                    order_type = OpenOrderType.STOP.value
                elif trade_params['order_type'] == 'MARKET':
                    pass
                else:
                    raise Exception('Invalid order type')

            # Slippage only applies to market orders; limit/stop orders must use 0
            if order_type == OpenOrderType.MARKET.value:
                slippage = int(self.slippage_percentage * PRECISION_2)
            else:
                slippage = 0

            # Create BuilderFee struct with default values (zero address and zero fee)
            # Can be customized if builder fees are needed in the future
            builder_fee = {
                'builder': '0x0000000000000000000000000000000000000000',  # Zero address
                'builderFee': 0  # Zero fee
            }
            
            # Check if custom builder fee is provided in trade_params
            if 'builder_address' in trade_params and 'builder_fee' in trade_params:

                if not self.web3.is_address(trade_params['builder_address']):
                    raise Exception('Invalid builder address format')
                
                if trade_params['builder_fee'] > 0.5:
                    raise Exception('Builder fee too high: Max 0.5 (0.5%)')
                
                builder_fee = {
                    'builder': trade_params['builder_address'],
                    'builderFee': convert_to_scaled_integer(trade_params['builder_fee'], precision=4, scale=6)
                }

            if self.use_delegation and 'trader_address' in trade_params:
                # Use delegatedAction when delegation is enabled
                trader_address = trade_params['trader_address']
                self.log(
                    f"Using delegatedAction to trade on behalf of {trader_address}")

                # Encode the openTrade call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='openTrade', args=[trade, builder_fee, order_type, slippage])

                # Create the outer delegatedAction transaction
                trade_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account, nonce=nonce))
            else:
                # Standard direct function call (no delegation) with BuilderFee parameter
                trade_tx = self.ostium_trading_contract.functions.openTrade(
                    trade, builder_fee, order_type, slippage
                ).build_transaction(self._build_tx_params(account, nonce=nonce))

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=self.private_key)
            trade_tx_hash = self._send_signed(signed_tx)
            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            # self.log(f"Order Receipt: {trade_receipt}")

            order_id = self._extract_order_id(
                trade_receipt, ['MarketOpenOrderInitiated'])

            return {
                'receipt': trade_receipt,
                'order_id': order_id
            }

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                e, verbose=self.verbose)
            print(
                f"An error ({str(e)}) occurred during the trading process - parsed as {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def cancel_limit_order(self, pair_id, trade_index, trader_address=None):
        account = self._get_account()

        try:
            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to cancel limit order on behalf of {trader_address}")

                # Encode the cancelOpenLimitOrder call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='cancelOpenLimitOrder', args=[int(pair_id), int(trade_index)])

                # Create the outer delegatedAction transaction
                trade_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account))
            else:
                trade_tx = self.ostium_trading_contract.functions.cancelOpenLimitOrder(
                    int(pair_id), int(trade_index)).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=self.private_key)
            trade_tx_hash = self._send_signed(signed_tx)
            self.log(f"Cancel Limit Order TX Hash: {trade_tx_hash.hex()}")

            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            self.log(f"Cancel Limit Order Receipt: {trade_receipt}")
            return trade_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the update sl process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def close_trade(self, pair_id, trade_index, market_price, close_percentage=100, trader_address=None):
        """
        Close a trade partially or completely

        Args:
            pair_id: The ID of the trading pair
            trade_index: The index of the trade
            market_price: The current market price for the trade
            close_percentage: The percentage of the position to close (1-100, default: 100)
            trader_address: Optional address of the trader if different from the account (for delegation)

        Returns:
            A dictionary containing the transaction receipt and order ID
        """
        self.log(f"Closing trade for pair {pair_id}, index {trade_index}")
        account = self._get_account()

        close_percentage = to_base_units(close_percentage, decimals=2)
        
        # Convert market price to the correct format (uint192)
        market_price_scaled = convert_to_scaled_integer(market_price)
        
        # Calculate slippage using the same percentage as for opening trades
        slippage = int(self.slippage_percentage * PRECISION_2)

        if self.use_delegation and trader_address:
            self.log(
                f"Using delegatedAction to close trade on behalf of {trader_address}")

            # Encode the closeTradeMarket call locally (no RPC round-trips)
            inner_encoded_data = self._encode_trading_call(
                fn_name='closeTradeMarket',
                args=[int(pair_id), int(trade_index), int(close_percentage),
                      market_price_scaled, slippage])

            # Create the outer delegatedAction transaction
            trade_tx = self.ostium_trading_contract.functions.delegatedAction(
                trader_address, inner_encoded_data
            ).build_transaction(self._build_tx_params(account))
        else:
            # Standard direct function call (no delegation) with new parameters
            trade_tx = self.ostium_trading_contract.functions.closeTradeMarket(
                int(pair_id), int(trade_index), int(close_percentage),
                market_price_scaled, slippage
            ).build_transaction(self._build_tx_params(account))

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self._send_signed(signed_tx)
        self.log(f"Trade TX Hash: {trade_tx_hash.hex()}")

        trade_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        # self.log(f"Trade Receipt: {trade_receipt}")

        order_id = self._extract_order_id(
            trade_receipt, ['MarketCloseOrderInitiatedV2', 'MarketCloseOrderInitiated'])

        return {
            'receipt': trade_receipt,
            'order_id': order_id
        }

    def close_market_timeout(self, order_id, retry=False, trader_address=None):
        """
        Close a trade that has timed out in the market
        
        Args:
            order_id: The ID of the order that has timed out
            retry: Whether to retry the close operation (True) or cancel it (False)
            trader_address: Optional address of the trader if different from the account (for delegation)
        
        Returns:
            A dictionary containing the transaction receipt
        """
        self.log(f"Closing market timeout for order {order_id}, retry={retry}")
        account = self._get_account()
        
        try:
            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to close market timeout on behalf of {trader_address}")
                
                # Encode the closeTradeMarketTimeout call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='closeTradeMarketTimeout', args=[int(order_id), bool(retry)])

                tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account))
            else:
                tx = self.ostium_trading_contract.functions.closeTradeMarketTimeout(
                    int(order_id), bool(retry)
                ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, private_key=self.private_key)
            tx_hash = self._send_signed(signed_tx)
            self.log(f"Close Market Timeout TX Hash: {tx_hash.hex()}")
            
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.log(f"Close Market Timeout successful for order {order_id}")
            
            return {
                'receipt': receipt,
                'order_id': order_id,
                'retry': retry
            }
            
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                e, verbose=self.verbose)
            print(
                f"An error ({str(e)}) occurred during close market timeout - parsed as {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def open_market_timeout(self, order_id, trader_address=None):
        """
        Open/execute a trade that has timed out in the market
        
        Args:
            order_id: The ID of the order that has timed out
            trader_address: Optional address of the trader if different from the account (for delegation)
        
        Returns:
            A dictionary containing the transaction receipt
        """
        self.log(f"Opening market timeout for order {order_id}")
        account = self._get_account()
        
        try:
            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to open market timeout on behalf of {trader_address}")
                
                # Encode the openTradeMarketTimeout call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='openTradeMarketTimeout', args=[int(order_id)])

                tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account))
            else:
                tx = self.ostium_trading_contract.functions.openTradeMarketTimeout(
                    int(order_id)
                ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, private_key=self.private_key)
            tx_hash = self._send_signed(signed_tx)
            self.log(f"Open Market Timeout TX Hash: {tx_hash.hex()}")
            
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.log(f"Open Market Timeout successful for order {order_id}")
            
            return {
                'receipt': receipt,
                'order_id': order_id
            }
            
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                e, verbose=self.verbose)
            print(
                f"An error ({str(e)}) occurred during open market timeout - parsed as {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def remove_collateral(self, pair_id, trade_index, remove_amount):
        self.log(
            f"Remove collateral for trade for pair {pair_id}, index {trade_index}: {remove_amount} USDC")
        account = self._get_account()

        amount = to_base_units(remove_amount, decimals=6)

        trade_tx = self.ostium_trading_contract.functions.removeCollateral(
            int(pair_id), int(trade_index), int(amount)).build_transaction(self._build_tx_params(account))

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self._send_signed(signed_tx)
        self.log(f"Remove Collateral TX Hash: {trade_tx_hash.hex()}")

        remove_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        self.log(f"Remove Collateral Receipt: {remove_receipt}")
        return remove_receipt

    def add_collateral(self, pairID, index, collateral, trader_address=None):
        """
        Add collateral to an existing position

        Args:
            pairID: The ID of the trading pair
            index: The index of the trade
            collateral: The amount of collateral to add
            trader_address: Optional address of the trader if different from the account (for delegation)

        Returns:
            The transaction receipt
        """
        account = self._get_account()
        try:
            amount = to_base_units(collateral, decimals=6)
            nonce = self.get_nonce(account.address)
            nonce = self.__approve(account, amount,
                                   self.use_delegation, trader_address, nonce=nonce)

            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to add collateral on behalf of {trader_address}")

                # Encode the topUpCollateral call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='topUpCollateral', args=[int(pairID), int(index), amount])

                # Create the outer delegatedAction transaction
                add_collateral_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account, nonce=nonce))
            else:
                # Standard direct function call (no delegation)
                add_collateral_tx = self.ostium_trading_contract.functions.topUpCollateral(
                    int(pairID), int(index), amount
                ).build_transaction(self._build_tx_params(account, nonce=nonce))

            signed_tx = self.web3.eth.account.sign_transaction(
                add_collateral_tx, private_key=self.private_key)
            add_collateral_tx_hash = self._send_signed(signed_tx)
            self.log(f"Add Collateral TX Hash: {add_collateral_tx_hash.hex()}")

            add_collateral_receipt = self.web3.eth.wait_for_transaction_receipt(
                add_collateral_tx_hash)
            self.log(f"Add Collateral Receipt: {add_collateral_receipt}")
            return add_collateral_receipt

        except Exception as e:
            print("An error occurred during the add collateral process:")
            traceback.print_exc()
            raise e

    def update_tp(self, pair_id, trade_index, tp_price, trader_address=None):
        """
        Update take profit price for an existing position

        Args:
            pair_id: The ID of the trading pair
            trade_index: The index of the trade
            tp_price: The new take profit price
            trader_address: Optional address of the trader if different from the account (for delegation)

        Returns:
            The transaction receipt
        """
        self.log(
            f"Updating TP for pair {pair_id}, index {trade_index} to {tp_price}")
        account = self._get_account()
        try:
            tp_value = to_base_units(tp_price, decimals=18)

            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to update TP on behalf of {trader_address}")

                # Encode the updateTp call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='updateTp', args=[int(pair_id), int(trade_index), tp_value])

                # Create the outer delegatedAction transaction
                update_tp_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account))
            else:
                # Standard direct function call (no delegation)
                update_tp_tx = self.ostium_trading_contract.functions.updateTp(
                    int(pair_id), int(trade_index), tp_value
                ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                update_tp_tx, private_key=self.private_key)
            update_tp_tx_hash = self._send_signed(signed_tx)
            self.log(f"Update TP TX Hash: {update_tp_tx_hash.hex()}")

            update_tp_receipt = self.web3.eth.wait_for_transaction_receipt(
                update_tp_tx_hash)
            return update_tp_receipt

        except Exception as e:
            print("An error occurred during the update tp process:")
            traceback.print_exc()
            raise e

    def update_sl(self, pairID, index, sl, trader_address=None):
        """
        Update stop loss price for an existing position

        Args:
            pairID: The ID of the trading pair
            index: The index of the trade
            sl: The new stop loss price
            trader_address: Optional address of the trader if different from the account (for delegation)

        Returns:
            The transaction receipt
        """
        account = self._get_account()
        try:
            sl_value = to_base_units(sl, decimals=18)

            if self.use_delegation and trader_address:
                self.log(
                    f"Using delegatedAction to update SL on behalf of {trader_address}")

                # Encode the updateSl call locally (no RPC round-trips)
                inner_encoded_data = self._encode_trading_call(
                    fn_name='updateSl', args=[int(pairID), int(index), sl_value])

                # Create the outer delegatedAction transaction
                update_sl_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction(self._build_tx_params(account))
            else:
                # Standard direct function call (no delegation)
                update_sl_tx = self.ostium_trading_contract.functions.updateSl(
                    int(pairID), int(index), sl_value
                ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                update_sl_tx, private_key=self.private_key)
            update_sl_tx_hash = self._send_signed(signed_tx)
            self.log(f"Update SL TX Hash: {update_sl_tx_hash.hex()}")

            update_sl_receipt = self.web3.eth.wait_for_transaction_receipt(
                update_sl_tx_hash)
            return update_sl_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the update sl process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def _allowance_owner(self, account, trader_address=None):
        return trader_address if trader_address and self.use_delegation else account.address

    def _check_allowance(self, owner, amount):
        """
        Return the USDC allowance for owner, reading from chain only when the
        cached value can't cover the requested amount.
        """
        cached = self._allowance_cache.get(owner)
        if cached is not None and cached >= amount:
            return cached
        allowance = self.usdc_contract.functions.allowance(
            owner, self.ostium_trading_storage_address).call()
        self._allowance_cache[owner] = allowance
        return allowance

    def __approve(self, account, collateral, use_delegation, trader_address=None, nonce=None):
        """
        Ensure the allowance covers the collateral, sending an approve tx if
        needed. Returns the nonce the caller should use for its own
        transaction (the prefetched nonce advances by one when an approve tx
        was sent), or None if no nonce was prefetched.
        """
        owner = trader_address if trader_address and use_delegation else account.address
        allowance = self._check_allowance(owner, collateral)

        if allowance < collateral:
            if not use_delegation:
                approve_amount = self.web3.to_wei(1000000, 'mwei')
                approve_tx = self.usdc_contract.functions.approve(
                    self.ostium_trading_storage_address,
                    approve_amount
                ).build_transaction(self._build_tx_params(account, nonce=nonce))

                signed_tx = self.web3.eth.account.sign_transaction(
                    approve_tx, private_key=self.private_key)
                approve_tx_hash = self._send_signed(signed_tx)
                self.log(f"Approval TX Hash: {approve_tx_hash.hex()}")

                approve_receipt = self.web3.eth.wait_for_transaction_receipt(
                    approve_tx_hash)
                self.log(f"Approval Receipt: {approve_receipt}")
                self._allowance_cache[owner] = approve_amount
                if nonce is not None:
                    nonce += 1
            else:
                raise Exception(
                    f"Sufficient allowance for {trader_address} not present. Please approve the trading contract to spend USDC.")

        # The pending transaction will consume this much of the allowance
        self._allowance_cache[owner] -= collateral
        return nonce

    def withdraw(self, amount, receiving_address):
        account = self._get_account()

        try:
            amount_in_base_units = to_base_units(amount, decimals=6)

            if not self.web3.is_address(receiving_address):
                raise ValueError("Invalid Arbitrum address format")

            transfer_tx = self.usdc_contract.functions.transfer(
                receiving_address,
                amount_in_base_units
            ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                transfer_tx, private_key=self.private_key)
            transfer_tx_hash = self._send_signed(signed_tx)
            self.log(f"Transfer TX Hash: {transfer_tx_hash.hex()}")

            transfer_receipt = self.web3.eth.wait_for_transaction_receipt(
                transfer_tx_hash)
            self.log(f"Transfer Receipt: {transfer_receipt}")
            return transfer_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the transfer process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def update_limit_order(self, pair_id, index, pvt_key, price=None, tp=None, sl=None):
        try:
            account = self.web3.eth.account.from_key(pvt_key)
            # Get existing order details (tbd why read from storage)
            existing_order = self.ostium_trading_storage_contract.functions.getOpenLimitOrder(
                account.address,
                int(pair_id),
                int(index)
            ).call()

            self.log(f"existing_order {existing_order}")
            # Use existing values if new values are not provided
            price_value = convert_to_scaled_integer(
                price) if price is not None else existing_order[1]  # openPrice
            tp_value = convert_to_scaled_integer(
                tp) if tp is not None else existing_order[2]    # tp
            sl_value = convert_to_scaled_integer(
                sl) if sl is not None else existing_order[3]    # sl

            trade_tx = self.ostium_trading_contract.functions.updateOpenLimitOrder(
                int(pair_id),
                int(index),
                price_value,
                tp_value,
                sl_value
            ).build_transaction(self._build_tx_params(account))

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=account.key)
            trade_tx_hash = self._send_signed(signed_tx)
            self.log(f"Update Limit Order TX Hash: {trade_tx_hash.hex()}")

            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            self.log(f"Update Limit Order Receipt: {trade_receipt}")
            return trade_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the update limit order process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    async def track_order_and_trade(self, subgraph_client, order_id, polling_interval=1, max_attempts=30, from_block=None):
        """
        Track an order by its ID and get the resulting trade once the order is executed.
        Formats the blockchain values to proper decimal representation.

        Watches the chain directly for the settlement event (the oracle
        answers within ~1s), then tries the subgraph once for the enriched
        payload. If the subgraph hasn't indexed the order yet, returns a
        result built from the settlement event itself (order carries
        'source': 'chain'). Falls back to legacy subgraph polling if
        on-chain tracking is unavailable.

        Args:
            subgraph_client: The SubgraphClient instance to use for queries
            order_id: The ID of the order to track
            polling_interval: Time in seconds between subgraph polling attempts
            max_attempts: Maximum number of subgraph polling attempts
            from_block: Block to watch from (e.g. the send receipt's
                blockNumber); defaults to a recent lookback window

        Returns:
            A dictionary containing both the order and trade data with formatted values
        """
        self.log(f"Tracking order ID: {order_id}")

        if not order_id:
            raise ValueError("Order ID is required")

        budget = polling_interval * max_attempts
        try:
            settled = await self._wait_for_order_settlement(
                order_id, from_block=from_block, timeout=min(budget, 20))
        except Exception as e:
            self.log(
                f"On-chain order tracking unavailable ({e}); using subgraph polling")
            return await self._track_order_via_subgraph(subgraph_client, order_id, polling_interval, max_attempts)

        if settled:
            event_name, args = settled
            self.log(f"Order {order_id} settled on-chain via {event_name}")
            # One shot at the richer subgraph payload; usually not indexed yet
            try:
                order = await subgraph_client.get_order_by_id(order_id)
                if order and not order.get('isPending', True):
                    return await self._track_order_via_subgraph(subgraph_client, order_id, polling_interval, max_attempts=2)
            except Exception as e:
                self.log(f"Subgraph enrichment failed: {e}")
            return self._chain_settlement_to_result(event_name, args)

        # Chain watch timed out (e.g. order never settled); legacy behavior
        return await self._track_order_via_subgraph(subgraph_client, order_id, polling_interval, max_attempts)

    async def _track_order_via_subgraph(self, subgraph_client, order_id, polling_interval=1, max_attempts=30):
        """Legacy tracking: poll the subgraph until the order settles."""
        price_fields = ENTITY_PRICE_FIELDS
        collateral_fields = ENTITY_COLLATERAL_FIELDS
        percentage_fields = ENTITY_PERCENTAGE_FIELDS

        for attempt in range(max_attempts):
            order = await subgraph_client.get_order_by_id(order_id)

            if not order:
                self.log(
                    f"Order {order_id} not found yet, waiting... (attempt {attempt + 1}/{max_attempts})")
                await asyncio.sleep(polling_interval)
                continue

            # Format numeric values in order
            formatted_order = self._format_entity_values(
                order, price_fields, collateral_fields, percentage_fields)

            if not formatted_order.get('isPending', True):
                self.log(f"Order {order_id} has been processed")

                # Check if it was cancelled
                if formatted_order.get('isCancelled', False):
                    self.log(
                        f"Order {order_id} was cancelled: {formatted_order.get('cancelReason', 'Unknown reason')}")
                    return {'order': formatted_order, 'trade': None}

                # If not cancelled, look for the trade using tradeID from the order
                trade_id = formatted_order.get('tradeID')
                if trade_id:
                    self.log(f"Looking for trade with ID: {trade_id}")
                    trade = await subgraph_client.get_trade_by_id(trade_id)

                    if trade:
                        # Format numeric values in trade
                        formatted_trade = self._format_entity_values(
                            trade, price_fields, collateral_fields, percentage_fields)

                        # Special handling for closing orders - we need to verify the trade is actually closed
                        if formatted_order.get('orderAction') == 'Close':
                            # For a close order, we need to check if the trade is actually closed (isOpen = false)
                            if formatted_trade.get('isOpen', True):
                                self.log(
                                    f"Trade {trade_id} is closing but not fully closed yet, waiting... (attempt {attempt + 1}/{max_attempts})")
                                await asyncio.sleep(polling_interval)
                                continue

                        self.log(f"Found trade for order {order_id}")
                        return {'order': formatted_order, 'trade': formatted_trade}
                    else:
                        self.log(f"No trade found with ID {trade_id}")
                        return {'order': formatted_order, 'trade': None}
                else:
                    self.log(f"No tradeID found in order {order_id}")
                    return {'order': formatted_order, 'trade': None}

            self.log(
                f"Order {order_id} is still pending, waiting... (attempt {attempt + 1}/{max_attempts})")
            await asyncio.sleep(polling_interval)

        self.log(f"Max polling attempts reached for order {order_id}")
        order = await subgraph_client.get_order_by_id(order_id)
        if order:
            formatted_order = self._format_entity_values(
                order, price_fields, collateral_fields, percentage_fields)
            return {'order': formatted_order, 'trade': None}
        return {'order': None, 'trade': None}

    def _format_entity_values(self, entity, price_fields, collateral_fields, percentage_fields):
        """
        Format values in an entity (order or trade) to proper decimal representations

        Args:
            entity: The entity (order or trade) to format values for
            price_fields: List of field names that represent prices
            collateral_fields: List of field names that represent collateral/token amounts
            percentage_fields: List of field names that represent percentages

        Returns:
            A new dictionary with formatted values
        """
        if not entity:
            return None

        formatted_entity = {}

        for key, value in entity.items():
            if value is None:
                formatted_entity[key] = value
                continue

            if key in price_fields and isinstance(value, (int, str, Decimal)):
                # Format prices with 18 decimals
                try:
                    formatted_entity[key] = float(value) / 10**18
                except (ValueError, TypeError):
                    formatted_entity[key] = value
            elif key in collateral_fields and isinstance(value, (int, str, Decimal)):
                # Format collateral values with 6 decimals (USDC-like precision)
                try:
                    formatted_entity[key] = float(value) / 10**6
                except (ValueError, TypeError):
                    formatted_entity[key] = value
            elif key in percentage_fields and isinstance(value, (int, str, Decimal)):
                # Format percentage values with 2 decimals
                try:
                    formatted_entity[key] = float(value) / 10**2
                except (ValueError, TypeError):
                    formatted_entity[key] = value
            else:
                formatted_entity[key] = value

        return formatted_entity
