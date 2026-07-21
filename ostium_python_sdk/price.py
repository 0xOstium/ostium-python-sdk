import aiohttp
import ssl
from typing import Tuple


class Price:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.base_url = "https://metadata-backend.prod.bedrock.ostium.io"

    def log(self, message):
        if self.verbose:
            print(message)

    async def get_latest_prices(self):
        """
        Fetches the latest prices from the Ostium metadata-backend service.
        Returns a dictionary of price data.
        """
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with SSL context and additional options for better compatibility
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            use_dns_cache=True,
            ttl_dns_cache=300,
            limit=100,
            limit_per_host=30
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(f"{self.base_url}/PricePublish/latest-prices") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"Failed to fetch prices: {response.status}")
        except aiohttp.ClientConnectorCertificateError as e:
            # If SSL certificate verification fails, try with a more permissive approach
            self.log(f"SSL certificate verification failed, trying alternative approach: {e}")
            
            # Create a completely unverified SSL context
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                use_dns_cache=True,
                ttl_dns_cache=300,
                limit=100,
                limit_per_host=30
            )
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(f"{self.base_url}/PricePublish/latest-prices") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"Failed to fetch prices: {response.status}")
        except Exception as e:
            raise Exception(f"Error fetching prices: {str(e)}")

    # Returns a json, e.g: {'feed_id': '0x00039d9e45394f473ab1f050a1b963e6b05351e52d71e507509ada0c95ed75b8', 'bid': 107646.01338169997, 'mid': 107646.03680130735, 'ask': 107646.06022091472, 'isMarketOpen': True, 'isDayTradingClosed': False, 'secondsToToggleIsDayTradingClosed': -1, 'from': 'BTC', 'to': 'USD', 'timestampSeconds': 1748460056}
    async def get_latest_price_json(self, from_asset: str, to_asset: str):
        prices = await self.get_latest_prices()
        for price_data in prices:
            if (price_data.get('from') == from_asset and
                    price_data.get('to') == to_asset):
                self.log(f"get_latest_price_json: {price_data}")
                return price_data
        raise ValueError(f"No price found for pair: {from_asset}/{to_asset}")

    # Returns a mid price and isMarketOpen tuple, e.g: (97243.36503172085, True)
    async def get_price(self, from_currency, to_currency) -> Tuple[float, bool, bool]:
        self.log(f"Getting price for {from_currency}/{to_currency}")
        prices = await self.get_latest_prices()
        for price_data in prices:
            if (price_data.get('from') == from_currency and
                    price_data.get('to') == to_currency):
                return float(price_data.get('mid', 0)), price_data.get('isMarketOpen', False), price_data.get('isDayTradingClosed', False)
        raise ValueError(
            f"No price found for pair: {from_currency}/{to_currency}")
