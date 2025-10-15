import os
import asyncio
from decimal import Decimal
import pytest
from dotenv import load_dotenv
from ostium_python_sdk import OstiumSDK
from ostium_python_sdk.config import NetworkConfig
from eth_account import Account


@pytest.fixture(scope="module")
def sdk():
    """Initialize SDK with testnet configuration"""
    load_dotenv()

    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError("RPC_URL not found in .env file")

    # Initialize SDK with testnet config
    config = NetworkConfig.testnet()
    return OstiumSDK(config)


@pytest.mark.asyncio
async def test_perform_trade_without_builder_fee(sdk):
    """Test perform_trade with default builder fee (zero address, zero fee)"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check ETH and USDC balances first
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.001'):
        msg = f"Insufficient ETH balance: {eth_balance} ETH (need at least 0.001 ETH for gas)"
        pytest.skip(msg)

    if usdc_balance < Decimal('50'):
        msg = f"Insufficient USDC balance: {usdc_balance} USDC (need at least 50 USDC)"
        pytest.skip(msg)

    # Get latest price for BTC
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: {latest_price}")

    # Define trade parameters without builder fee
    trade_params = {
        'collateral': Decimal('15.5'),
        'leverage': Decimal('100'),
        'asset_type': 0,          # BTC-USD
        'direction': True,        # Long
        'order_type': 'MARKET'
    }

    print("\nPlacing market order without builder fee...")
    try:
        trade_result = sdk.ostium.perform_trade(
            trade_params, at_price=latest_price)

        # Get transaction receipt and order ID
        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        assert receipt is not None, "Receipt should not be None"
        assert order_id is not None, "Order ID should not be None"
        assert receipt['status'] == 1, "Transaction should be successful"

        print(f" Trade placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")

        # Track the order until it's processed
        print("\nTracking order status...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        if result['order']:
            print(f" Order processed successfully")
            print(f"  Order status: {'Cancelled' if result['order'].get('isCancelled') else 'Executed'}")

            if result['trade']:
                print(f"  Trade ID: {result['trade'].get('id')}")
                print(f"  Open price: {result['trade'].get('openPrice')}")
        else:
            print("� Order tracking timed out (this is not necessarily an error)")

    except Exception as e:
        pytest.fail(f"Trade without builder fee should not fail: {str(e)}")


@pytest.mark.asyncio
async def test_perform_trade_with_builder_fee(sdk):
    """Test perform_trade with custom builder fee"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check ETH and USDC balances first
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.001'):
        msg = f"Insufficient ETH balance: {eth_balance} ETH (need at least 0.001 ETH for gas)"
        pytest.skip(msg)

    if usdc_balance < Decimal('10'):
        msg = f"Insufficient USDC balance: {usdc_balance} USDC (need at least 50 USDC)"
        pytest.skip(msg)

    # Get latest price for ETH
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: {latest_price}")

    # Define a builder address (using a valid Ethereum address)
    # In production, this would be the actual builder's address
    builder_address = "0x5346C41883F75136522df9eaD7399A38482019a3"
    builder_fee_pct = 0.1  # Fee in pct (0.1%)

    # Define trade parameters with builder fee
    trade_params = {
        'collateral': Decimal('15.5'),
        'leverage': Decimal('100'),
        'asset_type': 0,                      # BTC-USD
        'direction': True,                     # Long
        'order_type': 'MARKET',
        'builder_address': builder_address,    # Custom builder address
        'builder_fee': builder_fee_pct      # Custom builder fee
    }

    print(f"\nPlacing market order with builder fee...")
    print(f"  Builder address: {builder_address}")
    print(f"  Builder fee: {builder_fee_pct}%")

    try:
        trade_result = sdk.ostium.perform_trade(
            trade_params, at_price=latest_price)

        # Get transaction receipt and order ID
        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        assert receipt is not None, "Receipt should not be None"
        assert order_id is not None, "Order ID should not be None"
        assert receipt['status'] == 1, "Transaction should be successful"

        print(f" Trade with builder fee placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")

        # Track the order until it's processed
        print("\nTracking order status...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        if result['order']:
            print(f" Order processed successfully")
            print(f"  Order status: {'Cancelled' if result['order'].get('isCancelled') else 'Executed'}")

            if result['trade']:
                print(f"  Trade ID: {result['trade'].get('id')}")
                print(f"  Open price: {result['trade'].get('openPrice')}")
        else:
            print("� Order tracking timed out (this is not necessarily an error)")

    except Exception as e:
        pytest.fail(f"Trade with builder fee should not fail: {str(e)}")


@pytest.mark.asyncio
async def test_perform_trade_with_limit_order_and_builder_fee(sdk):
    """Test perform_trade with LIMIT order type and builder fee"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check ETH and USDC balances
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.001'):
        msg = f"Insufficient ETH balance: {eth_balance} ETH (need at least 0.001 ETH for gas)"
        pytest.skip(msg)

    if usdc_balance < Decimal('50'):
        msg = f"Insufficient USDC balance: {usdc_balance} USDC (need at least 50 USDC)"
        pytest.skip(msg)

    # Get latest price for BTC
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: {latest_price}")

    # Set limit price 1% below current price (for a long position)
    limit_price = latest_price * Decimal('0.99')
    print(f"Limit order price: {limit_price}")

    # Define builder address and fee
    builder_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    builder_fee_pct = 0.3  # 0.3%

    # Define trade parameters with LIMIT order and builder fee
    trade_params = {
        'collateral': Decimal('15.5'),
        'leverage': Decimal('10'),
        'asset_type': 0,                      # BTC-USD
        'direction': True,                     # Long
        'order_type': 'LIMIT',                 # LIMIT order
        'builder_address': builder_address,
        'builder_fee': builder_fee_pct
    }

    print(f"\nPlacing LIMIT order with builder fee...")
    print(f"  Builder address: {builder_address}")
    print(f"  Builder fee: {builder_fee_pct}%")

    try:
        trade_result = sdk.ostium.perform_trade(
            trade_params, at_price=limit_price)

        # Get transaction receipt and order ID
        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        assert receipt is not None, "Receipt should not be None"
        assert order_id is not None, "Order ID should not be None"
        assert receipt['status'] == 1, "Transaction should be successful"

        print(f" LIMIT order with builder fee placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")

        # Note: For limit orders, we don't wait for execution as it may not trigger immediately
        print("\n Test passed: LIMIT order with builder fee created successfully")

    except Exception as e:
        pytest.fail(f"LIMIT order with builder fee should not fail: {str(e)}")
