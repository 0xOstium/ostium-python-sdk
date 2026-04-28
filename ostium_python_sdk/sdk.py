from dotenv import load_dotenv
import os
from decimal import Decimal, ROUND_DOWN

from ostium_python_sdk.formulae import GetFundingRate
from ostium_python_sdk.scscript.funding import getTargetFundingRate
from ostium_python_sdk.utils import calculate_fee_per_hours, format_with_precision

from .formulae_wrapper import get_trade_metrics
from .constants import CHAIN_ID_ARBITRUM_MAINNET, CHAIN_ID_ARBITRUM_TESTNET, PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, PRECISION_9

from ostium_python_sdk.faucet import Faucet
from .balance import Balance
from .price import Price
from web3 import Web3
from .ostium import Ostium
from .vault import OstiumVault
from .config import NetworkConfig
from typing import Union
from .subgraph import SubgraphClient


class OstiumSDK:
    def __init__(self, network: Union[str, NetworkConfig], private_key: str = None, rpc_url: str = None, verbose=False, use_delegation=False):
        self.verbose = verbose
        load_dotenv()
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        self.use_delegation = use_delegation

        self.rpc_url = rpc_url or os.getenv('RPC_URL')
        if not self.rpc_url:
            network_name = "mainnet" if isinstance(
                network, str) and network == "mainnet" else "testnet"
            raise ValueError(
                f"No RPC_URL provided for {network_name}. Please provide via constructor or RPC_URL environment variable")

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Get network configuration
        if isinstance(network, NetworkConfig):
            self.network_config = network
        elif isinstance(network, str):
            if network == "mainnet":
                self.network_config = NetworkConfig.mainnet()
            elif network == "testnet":
                self.network_config = NetworkConfig.testnet()
            else:
                raise ValueError(
                    f"Unsupported network: {network}. Use 'mainnet' or 'testnet'")
        else:
            raise ValueError(
                "Network must be either a NetworkConfig instance or a string ('mainnet' or 'testnet')")

        # Validate chain ID
        expected_chain_id = CHAIN_ID_ARBITRUM_MAINNET if not self.network_config.is_testnet else CHAIN_ID_ARBITRUM_TESTNET
        actual_chain_id = self.w3.eth.chain_id
        if actual_chain_id != expected_chain_id:
            raise ValueError(
                f"Chain ID mismatch. Expected {expected_chain_id} for {'testnet' if self.network_config.is_testnet else 'mainnet'}, "
                f"but RPC is connected to chain ID {actual_chain_id}. Please check your RPC_URL."
            )

        if self.verbose:
            print(
                f"network_config: {'TESTNET' if self.network_config.is_testnet else 'MAINNET'}")

        # Initialize Ostium instance
        self.ostium = Ostium(
            self.w3,
            self.network_config.contracts["usdc"],
            self.network_config.contracts["tradingStorage"],
            self.network_config.contracts["trading"],
            private_key=self.private_key,
            verbose=self.verbose,
            use_delegation=self.use_delegation
        )

        # Initialize vault instance
        self.vault = OstiumVault(
            self.w3,
            self.network_config.contracts["vault"],
            self.network_config.contracts["usdc"],
            private_key=self.private_key,
            verbose=self.verbose
        )

        # Initialize subgraph client
        self.subgraph = SubgraphClient(
            url=self.network_config.graph_url, verbose=self.verbose)

        self.balance = Balance(
            self.w3, self.network_config.contracts["usdc"], verbose=self.verbose)
        self.price = Price(verbose=self.verbose)

        if self.network_config.is_testnet:
            self.faucet = Faucet(self.w3, self.private_key,
                                 verbose=self.verbose)
        else:
            self.faucet = None

    def log(self, message):
        if self.verbose:
            print(message)

    async def get_open_trades(self, trader_address=None):
        if trader_address is None:
            trader_public_address = self.ostium.get_public_address()
        else:
            trader_public_address = trader_address

        self.log(f"Trader public address: {trader_public_address}")
        open_trades = await self.subgraph.get_open_trades(trader_public_address)
        return open_trades, trader_public_address

    # if SDK instantiated with a private key, this function will return a given open trade metrics,
    # such as: funding fee, roll over fee, Unrealized Pnl, Profit Percent, etc.
    #
    # Will thorw in case SDK instantiated with no private key
    async def get_open_trade_metrics(self, pair_id, trade_index, trader_address=None):
        open_trades, trader_public_address = await self.get_open_trades(trader_address)

        liq_margin_threshold_p = await self.subgraph.get_liq_margin_threshold_p()
        self.log(
            f"SDK: get_open_trade_metrics: {liq_margin_threshold_p}, will use it for liquidation price calculation - call to get_trade_metrics()")

        trade_details = None

        if len(open_trades) == 0:
            raise ValueError(f"No Open Trades for {trader_public_address}")

        for t in open_trades:
            if int(t['pair']['id']) == int(pair_id) and int(t['index']) == int(trade_index):
                trade_details = t
                break

        if trade_details is None:
            raise ValueError(
                f"Trade not found for {trader_public_address} pair {pair_id} and index {trade_index}")

        self.log(f"\nTrade details: {trade_details}")
        # get the price for this trade's asset/feed
        price_data = await self.price.get_latest_price_json(trade_details['pair']['from'], trade_details['pair']['to'])
        self.log(
            f"\nPrice data: {price_data} (contains bid, mid, ask prices among other things)")
        # get the block number
        block_number = self.ostium.get_block_number()
        self.log(f"\nBlock number: {block_number}")

        pair_max_leverage = await self.get_pair_max_leverage(trade_details['pair']['id'])

        return get_trade_metrics(trade_details, price_data, block_number, pair_max_leverage, liq_margin_threshold_p, verbose=self.verbose)

    async def get_target_funding_rate(self, pair_id):
        pair_details = await self.subgraph.get_pair_details(pair_id)

        hillInflectionPoint = Decimal(
            pair_details['hillInflectionPoint']) / PRECISION_18

        maxFundingFeePerBlock = Decimal(
            pair_details['maxFundingFeePerBlock']) / PRECISION_18

        hillPosScale = Decimal(pair_details['hillPosScale']) / PRECISION_2
        hillNegScale = Decimal(pair_details['hillNegScale']) / PRECISION_2

        currLongOI = Decimal(pair_details['longOI']) / PRECISION_6
        currShortOI = Decimal(pair_details['shortOI']) / PRECISION_6
        maxOI = Decimal(pair_details['maxOI']) / PRECISION_6  # maxOI is in USD

        openInterestMax = max(currLongOI, currShortOI)
        normalizedOiDelta = ((currLongOI - currShortOI).quantize(PRECISION_6, rounding=ROUND_DOWN) / max(
            maxOI, openInterestMax).quantize(PRECISION_6, rounding=ROUND_DOWN)).quantize(PRECISION_6, rounding=ROUND_DOWN)

        targetFundingRate = getTargetFundingRate(
            normalizedOiDelta,
            hillInflectionPoint,
            maxFundingFeePerBlock,
            hillPosScale,
            hillNegScale
        )

        self.log(
            f"{pair_details['from']}{pair_details['to']} Traget Funding rate: {targetFundingRate}\n\nPair details: {pair_details}")

        return targetFundingRate

    # max leverage for overnight trades (Stocks) - 100 means 100x, None if not set
    async def get_pair_overnight_max_leverage(self, pair_id):
        obj = await self.subgraph.get_pair_details(pair_id)

        maxLeverage = int(obj['overnightMaxLeverage'])/PRECISION_2 if int(
            obj['overnightMaxLeverage']) != 0 else None
        return maxLeverage

    # either by group of pair or by pair id (e.g: maxLeverage 100 means 100x)
    async def get_pair_max_leverage(self, pair_id):
        obj = await self.subgraph.get_pair_details(pair_id)

        maxLeverage = int(obj['maxLeverage']) / PRECISION_2 if int(
            obj['group']['maxLeverage']) == 0 else int(obj['group']['maxLeverage']) / PRECISION_2
        return maxLeverage

    async def get_pair_net_rate_percent_per_hours(self, pair_id, period_hours=24):
        raise RuntimeError(
            f"Old version of function. Use get_funding_rate_for_pair_id(pair_id, period_hours=24).")

    async def get_rollover_rate_for_pair_id(self, pair_id, period_hours=24):
        pair_details = await self.subgraph.get_pair_details(pair_id)
        rollover_fee_per_block = Decimal(
            pair_details['rolloverFeePerBlock']) / Decimal('1e18')
        rollover = calculate_fee_per_hours(
            rollover_fee_per_block, hours=period_hours)
        return rollover

    async def get_funding_rate_for_pair_id(self, pair_id, period_hours=24):
        pair_details = await self.subgraph.get_pair_details(pair_id)
        # get the block number
        block_number = self.ostium.get_block_number()

        # Get current price
        last_trade_price = pair_details['lastTradePrice']

        long_oi = int(
            (Decimal(pair_details['longOI']) *
             Decimal(last_trade_price) / PRECISION_18 / PRECISION_12)
        )
        short_oi = int(
            (Decimal(pair_details['shortOI']) *
             Decimal(last_trade_price) / PRECISION_18 / PRECISION_12)
        )

        ret = GetFundingRate(
            pair_details['accFundingLong'],
            pair_details['accFundingShort'],
            pair_details['lastFundingRate'],
            pair_details['maxFundingFeePerBlock'],
            pair_details['lastFundingBlock'],
            block_number,
            str(long_oi),  # Needs to be in USD
            str(short_oi),  # Needs to be in USD
            str(pair_details['maxOI']),
            pair_details['hillInflectionPoint'],
            pair_details['hillPosScale'],
            pair_details['hillNegScale'],
            pair_details['springFactor'],
            pair_details['sFactorUpScaleP'],
            pair_details['sFactorDownScaleP'],
            self.verbose
        )

        accFundingLong = ret['accFundingLong']
        accFundingShort = ret['accFundingShort']
        fundingRate = float(ret['latestFundingRate']) * \
            (10 / 3) * 60 * 60 * 100 * period_hours
        targetFundingRate = float(ret['targetFundingRate']) * \
            (10 / 3) * 60 * 60 * 100 * period_hours

        self.log(
            f"{pair_details['from']}{pair_details['to']} Funding rate ({period_hours} hours): {fundingRate}%")
        self.log(
            f"{pair_details['from']}{pair_details['to']} Traget Funding rate ({period_hours} hours): {targetFundingRate}%")

        return accFundingLong, accFundingShort, fundingRate, targetFundingRate

    async def get_formatted_pairs_details(self, including_current_price_and_market_status=True) -> list:
        pairs = await self.subgraph.get_pairs()
        formatted_pairs = []

        for pair in pairs:
            formatted_pair = {
                'id': int(pair['id']),
                'from': pair['from'],
                'to': pair['to'],
                'group': pair['group']['name'],
                'longOI': Decimal(pair['longOI']) / PRECISION_18,
                'shortOI': Decimal(pair['shortOI']) / PRECISION_18,
                'maxOI': Decimal(pair['maxOI']) / PRECISION_6,
                'makerFeeP': Decimal(pair['makerFeeP']) / PRECISION_6,
                'takerFeeP': Decimal(pair['takerFeeP']) / PRECISION_6,
                'minLeverage': int(pair['minLeverage']) / PRECISION_2 if int(
                    pair['group']['minLeverage']) == 0 else Decimal(pair['group']['minLeverage']) / PRECISION_2,
                'maxLeverage': int(pair['maxLeverage']) / PRECISION_2 if int(
                    pair['group']['maxLeverage']) == 0 else Decimal(pair['group']['maxLeverage']) / PRECISION_2,
                'makerMaxLeverage': Decimal(pair['makerMaxLeverage']) / PRECISION_2,
                'groupMaxCollateralP': Decimal(pair['group']['maxCollateralP']) / PRECISION_2,
                'minLevPos': Decimal(pair['fee']['minLevPos']) / PRECISION_6,
                'lastFundingRate': Decimal(pair['lastFundingRate']) / PRECISION_9,
                'curFundingLong': Decimal(pair['curFundingLong']) / PRECISION_9,
                'curFundingShort': Decimal(pair['curFundingShort']) / PRECISION_9,
                'lastFundingBlock': int(pair['lastFundingBlock'])
            }

            if int(pair['overnightMaxLeverage']) != 0:
                formatted_pair['overnightMaxLeverage'] = Decimal(
                    pair['overnightMaxLeverage']) / PRECISION_2

            if including_current_price_and_market_status:
                # Get current price and market status
                try:
                    price, is_market_open, is_day_trading_closed = await self.price.get_price(
                        pair['from'],
                        pair['to']
                    )
                    if price is not None:
                        formatted_pair['price'] = price
                    if is_market_open is not None:
                        formatted_pair['isMarketOpen'] = is_market_open
                    if is_day_trading_closed is not None:
                        formatted_pair['isDayTradingClosed'] = is_day_trading_closed
                except ValueError:
                    pass

            formatted_pairs.append(formatted_pair)

        formatted_pairs.sort(key=lambda x: x['id'])
        return formatted_pairs
