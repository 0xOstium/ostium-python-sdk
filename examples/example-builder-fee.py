import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import the local module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ostium_python_sdk import OstiumSDK
from ostium_python_sdk.config import NetworkConfig


async def main():
    # Load environment variables
    load_dotenv()

    # Get private key and RPC URL from environment variables
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        raise ValueError("PRIVATE_KEY not found in .env file")

    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError("RPC_URL not found in .env file")

    # Initialize with testnet config
    config = NetworkConfig.mainnet()
    # Or for testnet:
    # config = NetworkConfig.testnet()

    # Initialize SDK
    sdk = OstiumSDK(config, private_key, rpc_url, verbose=True)

    # Example 1: Trade without builder fee (default behavior)
    print("=" * 80)
    print("Example 1: Trade WITHOUT builder fee")
    print("=" * 80)

    trade_params_no_fee = {
        'collateral': 10,
        'leverage': 100,
        'asset_type': 0,        # BTC-USD
        'direction': True,      # Long
        'order_type': 'MARKET'
    }

    try:
        latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
        print(f"Latest BTC/USD price: ${latest_price:,.2f}")

        print("\nPlacing market order WITHOUT builder fee...")
        print("Builder fee will default to: 0x0000000000000000000000000000000000000000 with 0 fee\n")

        trade_result = sdk.ostium.perform_trade(trade_params_no_fee, at_price=latest_price)

        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        print(f"✓ Order placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")
        print(f"  Gas used: {receipt['gasUsed']}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # Example 2: Trade with builder fee
    print("\n" + "=" * 80)
    print("Example 2: Trade WITH builder fee")
    print("=" * 80)

    # Specify a builder address that will receive the fee
    builder_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    builder_fee_pct = 0.1  # 0.1%

    trade_params_with_fee = {
        'collateral': 10,
        'leverage': 100,
        'asset_type': 1,              # ETH-USD
        'direction': True,            # Long
        'order_type': 'MARKET',
        'builder_address': builder_address,
        'builder_fee': builder_fee_pct 
    }

    try:
        latest_price, _, _ = await sdk.price.get_price("ETH", "USD")
        print(f"Latest ETH/USD price: ${latest_price:,.2f}")

        print(f"\nPlacing market order WITH builder fee...")
        print(f"  Builder address: {builder_address}")
        print(f"  Builder fee: {builder_fee_pct}%)")

        # Calculate approximate fee amount
        position_size = trade_params_with_fee['collateral'] * trade_params_with_fee['leverage']
        approx_fee = position_size * (builder_fee_pct / 100) / 100
        print(f"  Approximate builder fee amount: ${approx_fee:.2f} USDC\n")

        trade_result = sdk.ostium.perform_trade(trade_params_with_fee, at_price=latest_price)

        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        print(f"✓ Order placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")
        print(f"  Gas used: {receipt['gasUsed']}")

        # Track the order to see the execution details
        print("\nTracking order status...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        if result['order'] and not result['order'].get('isPending', True):
            order = result['order']
            print(f"\n✓ Order executed!")
            print(f"  Status: {'Cancelled' if order.get('isCancelled') else 'Executed'}")
            print(f"  Execution price: ${float(order.get('price', 0)):,.2f}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # Example 3: Invalid builder fee (too high)
    print("\n" + "=" * 80)
    print("Example 3: Trade with INVALID builder fee (demonstrating validation)")
    print("=" * 80)

    trade_params_invalid_fee = {
        'collateral': 10,
        'leverage': 100,
        'asset_type': 0,
        'direction': True,
        'order_type': 'MARKET',
        'builder_address': builder_address,
        'builder_fee': 1.5  # 1.5% - exceeds maximum of 0.5%
    }

    try:
        latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
        print(f"Attempting to place order with builder fee of 1.5%...")
        print(f"Maximum allowed: 0.5%\n")

        trade_result = sdk.ostium.perform_trade(trade_params_invalid_fee, at_price=latest_price)

        print("✗ This should not succeed!")

    except Exception as e:
        print(f"✓ Expected error caught: {str(e)}")
        print(f"  Builder fee validation is working correctly!")

    print("\n" + "=" * 80)
    print("Builder Fee Examples Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
