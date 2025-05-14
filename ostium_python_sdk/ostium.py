import traceback
import asyncio
from decimal import Decimal
from enum import Enum
from ostium_python_sdk.constants import PRECISION_2
from web3 import Web3
from .abi.abi import usdc_abi, ostium_trading_abi, ostium_trading_storage_abi
from .utils import convert_to_scaled_integer, fromErrorCodeToMessage, get_tp_sl_prices, to_base_units
from eth_account.account import Account


class OpenOrderType(Enum):
    MARKET = 0
    LIMIT = 1
    STOP = 2


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
    def __init__(self, w3: Web3, usdc_address: str, ostium_trading_storage_address: str, ostium_trading_address: str, private_key: str, verbose=False, use_delegation=False) -> None:
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
            address=self.ostium_trading_storage_address, abi=ostium_trading_storage_abi)
        self.ostium_trading_contract = self.web3.eth.contract(
            address=self.ostium_trading_address, abi=ostium_trading_abi)

        self.slippage_percentage = 2  # 2%

    def log(self, message):
        if self.verbose:
            print(message)

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

    def _check_private_key(self):
        if not self.private_key:
            raise ValueError(
                "Private key is required for Ostium platform write-operations")

    def perform_trade(self, trade_params, at_price):
        self.log(f"Performing trade with params: {trade_params}")
        account = self._get_account()
        amount = to_base_units(trade_params['collateral'], decimals=6)
        self.__approve(account, amount, self.use_delegation, trade_params.get('trader_address'))

        try:
            self.log(f"Final trade parameters being sent: {trade_params}")
            tp_price, sl_price = get_tp_sl_prices(trade_params)

            trade = {
                'collateral': convert_to_scaled_integer(trade_params['collateral'], precision=5, scale=6),
                'openPrice': convert_to_scaled_integer(at_price),
                'tp': convert_to_scaled_integer(tp_price),
                'sl': convert_to_scaled_integer(sl_price),
                'trader': account.address,
                'leverage': to_base_units(trade_params['leverage'], decimals=2),
                'pairIndex': int(trade_params['asset_type']),
                'index': 0,
                'buy': trade_params['direction']
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

            slippage = int(self.slippage_percentage * PRECISION_2)

            if self.use_delegation and 'trader_address' in trade_params:
                # Use delegatedAction when delegation is enabled
                trader_address = trade_params['trader_address']
                self.log(f"Using delegatedAction to trade on behalf of {trader_address}")
                
                # The correct way to encode the function call in Web3.py
                # Create the function object for openTrade
                open_trade_func = self.ostium_trading_contract.functions.openTrade(
                    trade, order_type, slippage
                )
                
                # Get the encoded data for the openTrade function call
                inner_encoded_data = open_trade_func.build_transaction({'gas': 0})['data']
                
                # Create the outer delegatedAction transaction
                trade_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction({'from': account.address})
            else:
                # Standard direct function call (no delegation)
                trade_tx = self.ostium_trading_contract.functions.openTrade(
                    trade, order_type, slippage
                ).build_transaction({'from': account.address})
                
            trade_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=self.private_key)
            trade_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            # self.log(f"Order Receipt: {trade_receipt}")
            
            # Extract orderId from logs
            order_id = None
            for log in trade_receipt.logs:
                # Define PriceRequested event signature
                price_requested_signature = self.web3.keccak(text="PriceRequested(uint256,bytes32,uint256)").hex()
                
                # Look at the event topic to identify the event type
                if len(log['topics']) > 0 and log['topics'][0].hex() == price_requested_signature:
                    # orderId is the indexed parameter (second topic)
                    order_id = int(log['topics'][1].hex(), 16)
                    self.log(f"Found orderId from PriceRequested: {order_id}")
                    break
                
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

    def cancel_limit_order(self, pair_id, trade_index):
        account = self._get_account()

        trade_tx = self.ostium_trading_contract.functions.cancelOpenLimitOrder(
            int(pair_id), int(trade_index)).build_transaction({'from': account.address})
        trade_tx['nonce'] = self.get_nonce(account.address)

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.raw_transaction)
        self.log(f"Cancel Limit Order TX Hash: {trade_tx_hash.hex()}")

        trade_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        self.log(f"Cancel Limit Order Receipt: {trade_receipt}")
        return trade_receipt

    def close_trade(self, pair_id, trade_index, close_percentage=100, trader_address=None):
        """
        Close a trade partially or completely
        
        Args:
            pair_id: The ID of the trading pair
            trade_index: The index of the trade
            close_percentage: The percentage of the position to close (1-100, default: 100)
            trader_address: Optional address of the trader if different from the account (for delegation)
        
        Returns:
            A dictionary containing the transaction receipt and order ID
        """
        self.log(f"Closing trade for pair {pair_id}, index {trade_index}")
        account = self._get_account()

        close_percentage = to_base_units(close_percentage, decimals=2)

        if self.use_delegation and trader_address:
            self.log(f"Using delegatedAction to close trade on behalf of {trader_address}")
            
            # The correct way to encode the function call in Web3.py
            # Create the function object for closeTradeMarket
            close_trade_func = self.ostium_trading_contract.functions.closeTradeMarket(
                int(pair_id), int(trade_index), int(close_percentage)
            )
            
            # Get the encoded data for the closeTradeMarket function call
            inner_encoded_data = close_trade_func.build_transaction({'gas': 0})['data']
            
            # Create the outer delegatedAction transaction
            trade_tx = self.ostium_trading_contract.functions.delegatedAction(
                trader_address, inner_encoded_data
            ).build_transaction({'from': account.address})
        else:
            # Standard direct function call (no delegation)
            trade_tx = self.ostium_trading_contract.functions.closeTradeMarket(
                int(pair_id), int(trade_index), int(close_percentage)
            ).build_transaction({'from': account.address})

        trade_tx['nonce'] = self.get_nonce(account.address)

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.raw_transaction)
        self.log(f"Trade TX Hash: {trade_tx_hash.hex()}")

        trade_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        # self.log(f"Trade Receipt: {trade_receipt}")
        
        # Extract orderId from logs
        order_id = None
        for log in trade_receipt.logs:
            # Define PriceRequested event signature
            price_requested_signature = self.web3.keccak(text="PriceRequested(uint256,bytes32,uint256)").hex()
            
            # Look at the event topic to identify the event type
            if len(log['topics']) > 0 and log['topics'][0].hex() == price_requested_signature:
                # orderId is the indexed parameter (second topic)
                order_id = int(log['topics'][1].hex(), 16)
                self.log(f"Found orderId from PriceRequested: {order_id}")
                break
                
        return {
            'receipt': trade_receipt,
            'order_id': order_id
        }

    def remove_collateral(self, pair_id, trade_index, remove_amount):
        self.log(f"Remove collateral for trade for pair {pair_id}, index {trade_index}: {remove_amount} USDC")
        account = self._get_account()

        amount = to_base_units(remove_amount, decimals=6)

        trade_tx = self.ostium_trading_contract.functions.removeCollateral(
            int(pair_id), int(trade_index), int(amount)).build_transaction({'from': account.address})
        trade_tx['nonce'] = self.get_nonce(account.address)

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.raw_transaction)
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
            self.__approve(account, amount, self.use_delegation, trader_address)

            if self.use_delegation and trader_address:
                self.log(f"Using delegatedAction to add collateral on behalf of {trader_address}")
                
                # The correct way to encode the function call in Web3.py
                # Create the function object for topUpCollateral
                top_up_func = self.ostium_trading_contract.functions.topUpCollateral(
                    int(pairID), int(index), amount
                )
                
                # Get the encoded data for the topUpCollateral function call
                inner_encoded_data = top_up_func.build_transaction({'gas': 0})['data']
                
                # Create the outer delegatedAction transaction
                add_collateral_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction({'from': account.address})
            else:
                # Standard direct function call (no delegation)
                add_collateral_tx = self.ostium_trading_contract.functions.topUpCollateral(
                    int(pairID), int(index), amount
                ).build_transaction({'from': account.address})

            add_collateral_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                add_collateral_tx, private_key=self.private_key)
            add_collateral_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
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
                self.log(f"Using delegatedAction to update TP on behalf of {trader_address}")
                
                # The correct way to encode the function call in Web3.py
                # Create the function object for updateTp
                update_tp_func = self.ostium_trading_contract.functions.updateTp(
                    int(pair_id), int(trade_index), tp_value
                )
                
                # Get the encoded data for the updateTp function call
                inner_encoded_data = update_tp_func.build_transaction({'gas': 0})['data']
                
                # Create the outer delegatedAction transaction
                update_tp_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction({'from': account.address})
            else:
                # Standard direct function call (no delegation)
                update_tp_tx = self.ostium_trading_contract.functions.updateTp(
                    int(pair_id), int(trade_index), tp_value
                ).build_transaction({'from': account.address})

            update_tp_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                update_tp_tx, private_key=self.private_key)
            update_tp_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
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
                self.log(f"Using delegatedAction to update SL on behalf of {trader_address}")
                
                # The correct way to encode the function call in Web3.py
                # Create the function object for updateSl
                update_sl_func = self.ostium_trading_contract.functions.updateSl(
                    int(pairID), int(index), sl_value
                )
                
                # Get the encoded data for the updateSl function call
                inner_encoded_data = update_sl_func.build_transaction({'gas': 0})['data']
                
                # Create the outer delegatedAction transaction
                update_sl_tx = self.ostium_trading_contract.functions.delegatedAction(
                    trader_address, inner_encoded_data
                ).build_transaction({'from': account.address})
            else:
                # Standard direct function call (no delegation)
                update_sl_tx = self.ostium_trading_contract.functions.updateSl(
                    int(pairID), int(index), sl_value
                ).build_transaction({'from': account.address})

            update_sl_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                update_sl_tx, private_key=self.private_key)
            update_sl_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
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

    def __approve(self, account, collateral, use_delegation, trader_address=None):
        trader_address = trader_address if trader_address and use_delegation else account.address
        allowance = self.usdc_contract.functions.allowance(
             trader_address, self.ostium_trading_storage_address).call()

        if allowance < collateral:
            if not use_delegation:
                approve_tx = self.usdc_contract.functions.approve(
                    self.ostium_trading_storage_address,
                    self.web3.to_wei(1000000, 'mwei')
                ).build_transaction({'from': account.address})

                approve_tx['nonce'] = self.get_nonce(account.address)

                signed_tx = self.web3.eth.account.sign_transaction(
                    approve_tx, private_key=self.private_key)
                approve_tx_hash = self.web3.eth.send_raw_transaction(
                    signed_tx.raw_transaction)
                self.log(f"Approval TX Hash: {approve_tx_hash.hex()}")

                approve_receipt = self.web3.eth.wait_for_transaction_receipt(
                    approve_tx_hash)
                self.log(f"Approval Receipt: {approve_receipt}")
            else:            
                raise Exception(f"Sufficient allowance for {trader_address} not present. Please approve the trading contract to spend USDC.")

    def withdraw(self, amount, receiving_address):
        account = self._get_account()

        try:
            amount_in_base_units = to_base_units(amount, decimals=6)

            if not self.web3.is_address(receiving_address):
                raise ValueError("Invalid Arbitrum address format")

            transfer_tx = self.usdc_contract.functions.transfer(
                receiving_address,
                amount_in_base_units
            ).build_transaction({'from': account.address})

            transfer_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                transfer_tx, private_key=self.private_key)
            transfer_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
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
            ).build_transaction({'from': account.address})

            trade_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=account.key)
            trade_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
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

    async def track_order_and_trade(self, subgraph_client, order_id, polling_interval=1, max_attempts=30):
        """
        Track an order by its ID and get the resulting trade once the order is executed.
        Formats the blockchain values to proper decimal representation.
        
        Args:
            subgraph_client: The SubgraphClient instance to use for queries
            order_id: The ID of the order to track
            polling_interval: Time in seconds between polling attempts
            max_attempts: Maximum number of polling attempts
            
        Returns:
            A dictionary containing both the order and trade data with formatted values
        """
        self.log(f"Tracking order ID: {order_id}")
        
        # Fields that should be formatted to proper decimal values
        price_fields = [
            'price', 'priceAfterImpact', 'openPrice', 'closePrice', 
            'takeProfitPrice', 'stopLossPrice'
        ]
        collateral_fields = [
            'collateral', 'notional', 'tradeNotional', 'amountSentToTrader',
            'devFee', 'vaultFee', 'oracleFee', 'liquidationFee', 'fundingFee', 'rolloverFee'
        ]
        percentage_fields = [
            'profitPercent', 'totalProfitPercent', 'priceImpactP', 'leverage', 'highestLeverage',
            'closePercent'
        ]
        
        for attempt in range(max_attempts):
            order = await subgraph_client.get_order_by_id(order_id)
            
            if not order:
                self.log(f"Order {order_id} not found yet, waiting... (attempt {attempt + 1}/{max_attempts})")
                await asyncio.sleep(polling_interval)
                continue
                
            # Format numeric values in order
            formatted_order = self._format_entity_values(order, price_fields, collateral_fields, percentage_fields)
                
            if not formatted_order.get('isPending', True):
                self.log(f"Order {order_id} has been processed")
                
                # Check if it was cancelled
                if formatted_order.get('isCancelled', False):
                    self.log(f"Order {order_id} was cancelled: {formatted_order.get('cancelReason', 'Unknown reason')}")
                    return {'order': formatted_order, 'trade': None}
                    
                # If not cancelled, look for the trade using tradeID from the order
                trade_id = formatted_order.get('tradeID')
                if trade_id:
                    self.log(f"Looking for trade with ID: {trade_id}")
                    trade = await subgraph_client.get_trade_by_id(trade_id)
                    
                    if trade:
                        # Format numeric values in trade
                        formatted_trade = self._format_entity_values(trade, price_fields, collateral_fields, percentage_fields)
                        
                        # Special handling for closing orders - we need to verify the trade is actually closed
                        if formatted_order.get('orderAction') == 'Close':
                            # For a close order, we need to check if the trade is actually closed (isOpen = false)
                            if formatted_trade.get('isOpen', True):
                                self.log(f"Trade {trade_id} is closing but not fully closed yet, waiting... (attempt {attempt + 1}/{max_attempts})")
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
            
            self.log(f"Order {order_id} is still pending, waiting... (attempt {attempt + 1}/{max_attempts})")
            await asyncio.sleep(polling_interval)
        
        self.log(f"Max polling attempts reached for order {order_id}")
        order = await subgraph_client.get_order_by_id(order_id)
        if order:
            formatted_order = self._format_entity_values(order, price_fields, collateral_fields, percentage_fields)
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
