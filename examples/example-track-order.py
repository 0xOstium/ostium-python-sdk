import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import the local module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import from the local module
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
    # Or use testnet:
    # config = NetworkConfig.testnet()

    # Initialize SDK
    sdk = OstiumSDK(config, private_key, rpc_url, verbose=True)

    # Define trade parameters
    trade_params = {
        'collateral': 16,       # USDC amount
        'leverage': 100,        # Leverage multiplier
        'asset_type': 0,        # 0 for BTC, see pair_details in README for other asset types
        'direction': True,      # True for Long, False for Short
        'order_type': 'MARKET'  # 'MARKET', 'LIMIT', or 'STOP'
        # Optional: set take profit/stop loss
        # 'tp': 0,              # Take Profit price - if not specified or Zero means no TP
        # 'sl': 0,              # Stop Loss price - if not specified or Zero means no SL
    }

    try:
        # Set slippage percentage (default is 2%)
        sdk.ostium.set_slippage_percentage(1)
        print(f"Slippage percentage set to: {sdk.ostium.get_slippage_percentage()}%")

        # Get latest price for BTC
        latest_price, _ = await sdk.price.get_price("BTC", "USD")
        print(f"Latest BTC/USD price: ${latest_price:,.2f}")

        # Execute trade at current market price
        print("Placing market order...")
        trade_result = sdk.ostium.perform_trade(trade_params, at_price=latest_price)
        
        # Get transaction receipt and order ID
        receipt = trade_result['receipt']
        order_id = trade_result['order_id']
        
        print(f"Order placed!")
        print(f"Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"Order ID: {order_id}")
        
        # Track the order until it's processed and get the resulting trade
        print("\nTracking order status...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)
        
        if result['order']:
            order = result['order']
            print("\nOrder details:")
            print(f"  Status: {'Pending' if order.get('isPending', True) else 'Processed'}")
            print(f"  Cancelled: {order.get('isCancelled', False)}")
            if order.get('isCancelled', False):
                print(f"  Cancel reason: {order.get('cancelReason', 'Unknown')}")
            print(f"  Collateral: {order.get('collateral', 'N/A')} USDC")
            print(f"  Leverage: {order.get('leverage', 'N/A')}x")
            print(f"  Direction: {'Long' if order.get('isBuy', True) else 'Short'}")
            print(f"  Order type: {order.get('orderType', 'N/A')}")
            print(f"  Order action: {order.get('orderAction', 'N/A')}")
            print(f"  Price: ${float(order.get('price', 0)):,.2f}")
            print(f"  Trade ID: {order.get('tradeID', 'N/A')}")
        
        if result['trade']:
            trade = result['trade']
            print("\nTrade details:")
            print(f"  Trade ID: {trade.get('tradeID', 'N/A')}")
            print(f"  Is Open: {trade.get('isOpen', 'N/A')}")
            print(f"  Collateral: {trade.get('collateral', 'N/A')} USDC")
            print(f"  Leverage: {trade.get('leverage', 'N/A')}x")
            print(f"  Highest Leverage: {trade.get('highestLeverage', 'N/A')}x")
            print(f"  Direction: {'Long' if trade.get('isBuy', True) else 'Short'}")
            print(f"  Open Price: ${float(trade.get('openPrice', 0)):,.2f}")
            print(f"  Close Price: ${float(trade.get('closePrice', 0)):,.2f if trade.get('closePrice') else 0:,.2f}")
            print(f"  Take Profit: ${float(trade.get('takeProfitPrice', 0)):,.2f}")
            print(f"  Stop Loss: ${float(trade.get('stopLossPrice', 0)):,.2f}")
            print(f"  Pair: {trade.get('pair', {}).get('from', '')}/{trade.get('pair', {}).get('to', '')}")
            print(f"  Index: {trade.get('index', 'N/A')}")
            print(f"  Trade Type: {trade.get('tradeType', 'N/A')}")
        else:
            print("\nNo trade found for this order. It may still be pending or was cancelled.")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 