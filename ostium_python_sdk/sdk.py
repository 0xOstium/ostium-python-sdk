from dotenv import load_dotenv
import os
from decimal import Decimal

from ostium_python_sdk.formulae import get_funding_rate
from ostium_python_sdk.utils import calculate_fee_per_hours, format_with_precision

from .formulae_wrapper import get_funding_fee_long_short, get_trade_metrics
from .constants import PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, PRECISION_9

from ostium_python_sdk.faucet import Faucet
from .balance import Balance
from .price import Price
from web3 import Web3
from .ostium import Ostium
from .config import NetworkConfig
from typing import Union
from .subgraph import SubgraphClient


class OstiumSDK:
    def __init__(self, network: Union[str, NetworkConfig], private_key: str = None, rpc_url: str = None, verbose=False):
        self.verbose = verbose
        load_dotenv()
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        # if not self.private_key:
        #     raise ValueError(
        #         "No private key provided. Please provide via constructor or PRIVATE_KEY environment variable")

        self.rpc_url = rpc_url or os.getenv('RPC_URL')
        if not self.rpc_url:
            network_name = "mainnet" if isinstance(
                network, str) and network == "mainnet" else "testnet"
            raise ValueError(
                f"No RPC URL provided for {network_name}. Please provide via constructor or RPC_URL environment variable")

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

        # Initialize Ostium instance
        self.ostium = Ostium(
            self.w3,
            self.network_config.contracts["usdc"],
            self.network_config.contracts["tradingStorage"],
            self.network_config.contracts["trading"],
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

    # if SDK instantiated with a private key, this function will return a given open trade metrics,
    # such as: funding fee, roll over fee, Unrealized Pnl, Profit Percent, etc.
    #
    # Will thorw in case SDK instantiated with no private key
    async def get_open_trade_metrics(self, pair_id, trade_index):
        trader_public_address = self.ostium.get_public_address()
        self.log(f"Trader public address: {trader_public_address}")
        open_trades = await self.subgraph.get_open_trades(trader_public_address)

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

        self.log(f"Trade details: {trade_details}")
        # get the price for this trade's asset/feed
        price_data = await self.price.get_latest_price_json(trade_details['pair']['from'], trade_details['pair']['to'])
        self.log(f"Price data: {price_data} (need here bid, mid, ask prices)")
        # get the block number
        block_number = self.ostium.get_block_number()
        self.log(f"Block number: {block_number}")
        return get_trade_metrics(trade_details, price_data, block_number, verbose=self.verbose)

    async def get_pair_net_rate_percent_per_hours(self, pair_id, period_hours=24):
        pair_details = await self.subgraph.get_pair_details(pair_id)
        block_number = self.ostium.get_block_number()

        funding_fee_long_per_block, funding_fee_short_per_block = get_funding_fee_long_short(
            pair_details, block_number)
        rollover_fee_per_block = Decimal(
            pair_details['rolloverFeePerBlock']) / Decimal('1e18')

        ff_long = calculate_fee_per_hours(
            funding_fee_long_per_block, hours=period_hours)
        ff_short = calculate_fee_per_hours(
            funding_fee_short_per_block, hours=period_hours)
        rollover = calculate_fee_per_hours(
            rollover_fee_per_block, hours=period_hours)

        rollover_value = Decimal('0') if rollover == 0 else rollover
        net_long_percent = format_with_precision(
            ff_long-rollover_value, precision=4)
        net_short_percent = format_with_precision(
            ff_short-rollover_value, precision=4)
        return net_long_percent, net_short_percent

    async def get_funding_rate_for_pair_id(self, pair_id):
        pair_details = await self.subgraph.get_pair_details(pair_id)
        # get the block number
        block_number = self.ostium.get_block_number()

        self.log(f"Pair details: {pair_details}")
        self.log(f"Block number: {block_number}")

        # Get current price
        price, _ = await self.price.get_price(
            pair_details['from'],
            pair_details['to']
        )
        self.log(f"Price: {price}")

        notional_long_oi = int(
            (Decimal(pair_details['longOI']) / PRECISION_18) * Decimal(price) * PRECISION_6)
        notional_short_oi = int(
            (Decimal(pair_details['shortOI']) / PRECISION_18) * Decimal(price) * PRECISION_6)

        self.log(f"notional_long_oi: {notional_long_oi}")
        self.log(f"notional_short_oi: {notional_short_oi}")

        ret = get_funding_rate(
            pair_details['curFundingLong'],
            pair_details['curFundingShort'],
            pair_details['lastFundingRate'],
            # pair_details['lastFundingVelocity'],
            pair_details['maxFundingFeePerBlock'],
            pair_details['lastFundingBlock'],
            block_number,
            notional_long_oi,  # Needs to be in notional aka usd
            notional_short_oi,  # Needs to be in notional aka usd
            pair_details['maxOI'],
            pair_details['hillInflectionPoint'],
            pair_details['hillPosScale'],
            pair_details['hillNegScale'],
            pair_details['springFactor'],
            pair_details['sFactorUpScaleP'],
            pair_details['sFactorDownScaleP'],
            self.verbose
        )

        self.log(f"Funding rate: {ret}")
        return ret

    async def get_formatted_pairs_details(self) -> list:
        """
        Get formatted details for all trading pairs, with proper decimal conversion.

        Crypto pairs example:
        BTC-USD:
            - price: 65432.50
            - longOI: 0.41008148 (410.08148 BTC)
            - shortOI: 2.59812309 (2,598.12309 BTC)
            - maxOI: 1000.00000000
            - utilizationP: 80.00%
            - makerFeeP: 0.01%
            - takerFeeP: 0.10%
            - maxLeverage: 50x
            - group: crypto

        ETH-USD:
            - price: 3050.50
            - longOI: 5.90560023 (5,905.60023 ETH)
            - shortOI: 0.00000000
            - maxOI: 1000.00000000
            - utilizationP: 80.00%
            - makerFeeP: 0.01%
            - takerFeeP: 0.10%
            - maxLeverage: 50x
            - group: crypto

        Returns:
            list: List of dictionaries containing formatted pair details including:
                - id: Pair ID
                - from: Base asset (e.g., 'BTC')
                - to: Quote asset (e.g., 'USD')
                - price: Current market price
                - isMarketOpen: Market open status
                - longOI: Total long open interest in notional value
                - shortOI: Total short open interest in notional value
                - maxOI: Maximum allowed open interest
                - utilizationP: Utilization threshold percentage
                - makerFeeP: Maker fee percentage
                - takerFeeP: Taker fee percentage
                - usageFeeP: Usage fee percentage
                - maxLeverage: Maximum allowed leverage
                - minLeverage: Minimum allowed leverage
                - makerMaxLeverage: Maximum leverage for makers
                - group: Trading group name
                - groupMaxCollateralP: Maximum collateral percentage for the group
                - minLevPos: Minimum leverage position size
                - lastFundingRate: Latest funding rate
                - curFundingLong: Current funding for longs
                - curFundingShort: Current funding for shorts
                - lastFundingBlock: Block number of last funding update
                - lastFundingVelocity: Velocity of last funding rate change
        """
        pairs = await self.subgraph.get_pairs()
        formatted_pairs = []

        for pair in pairs:
            pair_details = await self.subgraph.get_pair_details(pair['id'])

            # Get current price and market status
            try:
                price, is_market_open = await self.price.get_price(
                    pair_details['from'],
                    pair_details['to']
                )
            except ValueError:
                price = 0
                is_market_open = False

            formatted_pair = {
                'id': int(pair_details['id']),
                'from': pair_details['from'],
                'to': pair_details['to'],
                'price': price,
                'isMarketOpen': is_market_open,
                'longOI': Decimal(pair_details['longOI']) / PRECISION_18,
                'shortOI': Decimal(pair_details['shortOI']) / PRECISION_18,
                'maxOI': Decimal(pair_details['maxOI']) / PRECISION_6,
                'utilizationP': Decimal(pair_details['utilizationThresholdP']) / PRECISION_2,
                'makerFeeP': Decimal(pair_details['makerFeeP']) / PRECISION_6,
                'takerFeeP': Decimal(pair_details['takerFeeP']) / PRECISION_6,
                'usageFeeP': Decimal(pair_details['usageFeeP']) / PRECISION_6,
                'maxLeverage': Decimal(pair_details['group']['maxLeverage']) / PRECISION_2,
                'minLeverage': Decimal(pair_details['group']['minLeverage']) / PRECISION_2,
                'makerMaxLeverage': Decimal(pair_details['makerMaxLeverage']) / PRECISION_2,
                'group': pair_details['group']['name'],
                'groupMaxCollateralP': Decimal(pair_details['group']['maxCollateralP']) / PRECISION_2,
                'minLevPos': Decimal(pair_details['fee']['minLevPos']) / PRECISION_9,
                'lastFundingRate': Decimal(pair_details['lastFundingRate']) / PRECISION_9,
                'curFundingLong': Decimal(pair_details['curFundingLong']) / PRECISION_9,
                'curFundingShort': Decimal(pair_details['curFundingShort']) / PRECISION_9,
                'lastFundingBlock': int(pair_details['lastFundingBlock']),
                'lastFundingVelocity': int(pair_details['lastFundingVelocity'])
            }
            formatted_pairs.append(formatted_pair)

        return formatted_pairs
