from dotenv import load_dotenv
import os
from decimal import Decimal

from ostium_python_sdk.formulae import GetFundingRate
from ostium_python_sdk.utils import calculate_fee_per_hours, format_with_precision

from .formulae_wrapper import get_funding_fee_long_short, get_trade_metrics
from .constants import CHAIN_ID_ARBITRUM_MAINNET, CHAIN_ID_ARBITRUM_TESTNET, PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, PRECISION_9

from ostium_python_sdk.faucet import Faucet
from .balance import Balance
from .price import Price
from web3 import Web3
from .ostium import Ostium
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

    async def get_open_trades(self):
        trader_public_address = self.ostium.get_public_address()
        self.log(f"Trader public address: {trader_public_address}")
        open_trades = await self.subgraph.get_open_trades(trader_public_address)
        return open_trades, trader_public_address

    # if SDK instantiated with a private key, this function will return a given open trade metrics,
    # such as: funding fee, roll over fee, Unrealized Pnl, Profit Percent, etc.
    #
    # Will thorw in case SDK instantiated with no private key
    async def get_open_trade_metrics(self, pair_id, trade_index):
        open_trades, trader_public_address = await self.get_open_trades()

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
            f"\nPrice data: {price_data} (need here bid, mid, ask prices)")
        # get the block number
        block_number = self.ostium.get_block_number()
        self.log(f"\nBlock number: {block_number}")
        return get_trade_metrics(trade_details, price_data, block_number, verbose=self.verbose)

    async def get_pair_net_rate_percent_per_hours(self, pair_id, period_hours=24):
        raise RuntimeError(
            f"Old version of function. Use get_funding_rate_for_pair_id(pair_id, period_hours=24).")

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

    async def get_formatted_pairs_details(self) -> list:
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
                'makerFeeP': Decimal(pair_details['makerFeeP']) / PRECISION_6,
                'takerFeeP': Decimal(pair_details['takerFeeP']) / PRECISION_6,
                'maxLeverage': Decimal(pair_details['group']['maxLeverage']) / PRECISION_2,
                'minLeverage': Decimal(pair_details['group']['minLeverage']) / PRECISION_2,
                'makerMaxLeverage': Decimal(pair_details['makerMaxLeverage']) / PRECISION_2,
                'group': pair_details['group']['name'],
                'groupMaxCollateralP': Decimal(pair_details['group']['maxCollateralP']) / PRECISION_2,
                'minLevPos': Decimal(pair_details['fee']['minLevPos']) / PRECISION_9,
                'lastFundingRate': Decimal(pair_details['lastFundingRate']) / PRECISION_9,
                'curFundingLong': Decimal(pair_details['curFundingLong']) / PRECISION_9,
                'curFundingShort': Decimal(pair_details['curFundingShort']) / PRECISION_9,
                'lastFundingBlock': int(pair_details['lastFundingBlock'])
            }
            formatted_pairs.append(formatted_pair)

        return formatted_pairs
