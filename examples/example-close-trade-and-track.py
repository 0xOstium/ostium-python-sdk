#!/usr/bin/env python3

import asyncio
import os
import sys
from decimal import Decimal
from dotenv import load_dotenv
from pprint import pprint

# Add the parent directory to the Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ostium_python_sdk import OstiumSDK
from ostium_python_sdk.config import NetworkConfig

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get private key and RPC URL from environment variables
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        raise ValueError("PRIVATE_KEY not found in .env file")

    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError("RPC_URL not found in .env file")
    
    # Initialize with network config (use testnet or mainnet as needed)
    config = NetworkConfig.mainnet()  # Change to mainnet() for production
    
    # Initialize SDK
    sdk = OstiumSDK(config, private_key, rpc_url, verbose=True)
    
    # Retrieve open trades for the user
    print("\nFetching open trades...")
    open_trades, trader_address = await sdk.get_open_trades()
    
    if not open_trades:
        print(f"No open trades found for address {trader_address}")
        return
    
    # Display available trades to close
    print("\nAvailable trades:")
    for i, trade in enumerate(open_trades):
        pair_name = f"{trade['pair']['from']}/{trade['pair']['to']}"
        direction = "LONG" if trade.get('isBuy', True) else "SHORT"
        
        # Format values with proper decimal places
        leverage = trade.get('leverage', 0)
        collateral = trade.get('collateral', 0)
        open_price = trade.get('openPrice', 0)
        
        try:
            leverage = float(leverage)
            leverage_formatted = f"{leverage:.2f}x"
        except (ValueError, TypeError):
            leverage_formatted = f"{leverage}x"
            
        try:
            collateral = float(collateral)
            collateral_formatted = f"${collateral:.2f}"
        except (ValueError, TypeError):
            collateral_formatted = f"{collateral}"
            
        try:
            open_price = float(open_price)
            open_price_formatted = f"${open_price:,.2f}"
        except (ValueError, TypeError):
            open_price_formatted = f"{open_price}"
            
        print(f"{i+1}. {direction} {pair_name} (ID: {trade['pair']['id']}, Index: {trade['index']})")
        print(f"   Collateral: {collateral_formatted}, Leverage: {leverage_formatted}")
        print(f"   Open Price: {open_price_formatted}")
    
    # Prompt user to select a trade to close (could be hardcoded in a real script)
    try:
        selected_index = int(input("\nEnter number of trade to close (or Ctrl+C to cancel): ")) - 1
        if selected_index < 0 or selected_index >= len(open_trades):
            print("Invalid selection")
            return
    except ValueError:
        print("Please enter a valid number")
        return
    
    selected_trade = open_trades[selected_index]
    pair_id = selected_trade['pair']['id']
    trade_index = selected_trade['index']
    pair_name = f"{selected_trade['pair']['from']}/{selected_trade['pair']['to']}"
    direction = "LONG" if selected_trade.get('isBuy', True) else "SHORT"
    
    # Get the current trade details before closing
    trade_id = selected_trade.get('tradeID')
    print(f"\nPreparing to close trade: {direction} {pair_name} (ID: {pair_id}, Index: {trade_index})")
    print(f"Trade ID: {trade_id}")
    print(f"Current status: {'OPEN' if selected_trade.get('isOpen', True) else 'CLOSED'}")
    
    # Close the trade (default is 100% close)
    print(f"\nClosing trade...")
    close_result = sdk.ostium.close_trade(pair_id, trade_index)
    
    # Extract the order ID from the result
    receipt = close_result['receipt']
    order_id = close_result['order_id']
    if not order_id:
        print("Failed to get order ID from close trade transaction")
        return
    
    print(f"Trade close order submitted with order ID: {order_id}")
    print(f"Transaction hash: {receipt['transactionHash'].hex()}")
    
    # Track the order until it's processed and get the resulting trade
    print("\nTracking order status...")
    result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)
    
    if result['order']:
        order = result['order']
        print("\nOrder details:")
        print(f"  Status: {'Pending' if order.get('isPending', True) else 'Processed'}")
        print(f"  Order action: {order.get('orderAction', 'N/A')}")
        print(f"  Order type: {order.get('orderType', 'N/A')}")
        print(f"  Cancelled: {order.get('isCancelled', False)}")
        
        if order.get('isCancelled', False):
            print(f"  Cancel reason: {order.get('cancelReason', 'Unknown')}")
        
        if 'price' in order:
            print(f"  Price: ${float(order['price']):,.2f}")
        
        if 'profitPercent' in order:
            print(f"  Profit percent: {order['profitPercent']}%")
        
        if 'amountSentToTrader' in order:
            print(f"  Amount sent to trader: {order['amountSentToTrader']} USDC")
        
        if result['trade']:
            trade = result['trade']
            print("\nTrade details:")
            print(f"  Trade ID: {trade.get('id') or trade.get('tradeID', 'N/A')}")
            print(f"  Status: {'OPEN' if trade.get('isOpen', True) else 'CLOSED'}")
            print(f"  Collateral: {trade.get('collateral', 'N/A')} USDC")
            print(f"  Leverage: {trade.get('leverage', 'N/A')}x")
            print(f"  Direction: {'Long' if trade.get('isBuy', True) else 'Short'}")
            
            if 'openPrice' in trade:
                print(f"  Open Price: ${float(trade['openPrice']):,.2f}")
            
            if 'closePrice' in trade and trade['closePrice']:
                print(f"  Close Price: ${float(trade['closePrice']):,.2f}")
            
            # Show fees if available
            if 'fundingFee' in order:
                print(f"  Funding Fee: {order.get('fundingFee', 'N/A')} USDC")
            
            if 'rolloverFee' in order:
                print(f"  Rollover Fee: {order.get('rolloverFee', 'N/A')} USDC")
        else:
            print("\nNo trade details found (order may be pending or cancelled)")
    else:
        print("\nFailed to find order information")

if __name__ == "__main__":
    asyncio.run(main()) 