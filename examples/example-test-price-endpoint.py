import asyncio
from ostium_python_sdk.price import Price


async def main():
    price = Price(verbose=True)
    print(f"Endpoint: {price.base_url}")

    prices = await price.get_latest_prices()
    assert isinstance(prices, list) and len(prices) > 0, "no prices returned"
    print(f"OK: fetched {len(prices)} feeds")

    btc = await price.get_latest_price_json("BTC", "USD")
    assert btc.get("mid"), "BTC/USD missing mid price"
    mid, is_open, is_day_closed = await price.get_price("BTC", "USD")
    print(f"BTC/USD mid={mid:,.2f} open={is_open} dayClosed={is_day_closed}")


if __name__ == "__main__":
    asyncio.run(main())
