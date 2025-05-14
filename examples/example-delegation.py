#!/usr/bin/env python3

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import the local module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ostium_python_sdk import OstiumSDK
from ostium_python_sdk.config import NetworkConfig

async def main():
    """
    Example demonstrating how to use delegatedAction to trade on behalf of another user.
    
    This uses the contract's native delegatedAction functionality, which allows an approved
    address (delegate) to execute trades on behalf of another address (trader).
    
    Requirements for delegation to work:
    1. The delegate must be approved at the contract level to act on behalf of the trader
    2. The trader address must have approved the trading contract to spend their USDC
    """
    # Load environment variables
    load_dotenv()

    # Get delegate private key and trader address
    delegate_private_key = os.getenv('PRIVATE_KEY')
    if not delegate_private_key:
        raise ValueError("PRIVATE_KEY not found in .env file")
        
    trader_address = os.getenv('TRADER_ADDRESS')
    if not trader_address:
        raise ValueError("TRADER_ADDRESS not found in .env file")

    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError("RPC_URL not found in .env file")

    # Initialize with network config
    config = NetworkConfig.mainnet()  # Use testnet() for testing
    
    # Initialize SDK with the delegate's private key and enable delegation
    sdk = OstiumSDK(config, delegate_private_key, rpc_url, verbose=True, use_delegation=True)
    
    # Get the delegate's address (the account executing trades)
    delegate_address = sdk.ostium.get_public_address()
    print(f"Delegate address: {delegate_address}")
    print(f"Trading on behalf of: {trader_address}")
    
    # Define trade parameters - specify the trader_address for delegation
    trade_params = {
        'collateral': 20,        # USDC amount
        'leverage': 100,          # Leverage multiplier
        'asset_type': 0,         # 0 for BTC, see pair_details in README for other asset types
        'direction': True,       # True for Long, False for Short
        'order_type': 'MARKET',  # 'MARKET', 'LIMIT', or 'STOP'
        'trader_address': trader_address  # The address that owns the position (not the delegate)
    }

    try:
        # Get latest price for BTC
        latest_price, _ = await sdk.price.get_price("BTC", "USD")
        print(f"Latest BTC/USD price: ${latest_price:,.2f}")

        # Execute trade at current market price using delegatedAction
        print(f"Placing market order on behalf of {trader_address} using delegatedAction...")
        
        try:
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
                print(f"  Trader: {order.get('trader', 'N/A')}")  # Should match the trader_address
                print(f"  Collateral: {order.get('collateral', 'N/A')} USDC")
                print(f"  Leverage: {order.get('leverage', 'N/A')}x")
                print(f"  Direction: {'Long' if order.get('isBuy', True) else 'Short'}")
                print(f"  Price: ${float(order.get('price', 0)):,.2f}")
            
                # After a successful order, demonstrate closing part of the position
                if not order.get('isPending', True) and result['trade']:
                    trade = result['trade']
                    pair_id = int(order['pair']['id'])
                    trade_index = int(trade['index'])
                    
                    print("\n\nNow demonstrating closing 100% of the position...")
                    close_percentage = 100
                    
                    # Close part of the trade using delegatedAction
                    close_result = sdk.ostium.close_trade(
                        pair_id, 
                        trade_index, 
                        close_percentage=close_percentage, 
                        trader_address=trader_address
                    )
                    
                    close_receipt = close_result['receipt']
                    close_order_id = close_result['order_id']
                    
                    print(f"Close order placed!")
                    print(f"Transaction hash: {close_receipt['transactionHash'].hex()}")
                    print(f"Close order ID: {close_order_id}")
                    
                    # Track the closing order
                    print("\nTracking close order status...")
                    close_result = await sdk.ostium.track_order_and_trade(sdk.subgraph, close_order_id)
                    
                    if close_result['order']:
                        close_order = close_result['order']
                        print("\nClose order details:")
                        print(f"  Status: {'Pending' if close_order.get('isPending', True) else 'Processed'}")
                        print(f"  Order action: {close_order.get('orderAction', 'N/A')}")
                        print(f"  Close percentage: {close_order.get('closePercent', close_percentage)}%")
                        
                        if 'profitPercent' in close_order:
                            print(f"  Profit percent: {close_order['profitPercent']}%")
                        
                        if 'amountSentToTrader' in close_order:
                            print(f"  Amount sent to trader: {close_order['amountSentToTrader']} USDC")
        
        except ValueError as e:
            print(f"Error: {str(e)}")
            print("\nPossible reasons for failure:")
            print("1. The delegate is not authorized to trade on behalf of the trader at the contract level")
            print("2. The trader has not approved enough USDC allowance for the trading contract")
            print("3. The trader does not have enough USDC balance")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 