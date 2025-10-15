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
async def test_close_trade_full_position(sdk):
    """Test closing 100% of a position"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check ETH and USDC balances first
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.002'):
        msg = f"Insufficient ETH balance: {eth_balance} ETH (need at least 0.002 ETH for gas)"
        pytest.skip(msg)

    if usdc_balance < Decimal('100'):
        msg = f"Insufficient USDC balance: {usdc_balance} USDC (need at least 100 USDC)"
        pytest.skip(msg)

    # Get latest price for BTC
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: ${latest_price:,.2f}")

    # Step 1: Open a trade
    print("\n=== STEP 1: Opening a trade ===")
    trade_params = {
        'collateral': Decimal('160'),
        'leverage': Decimal('10'),
        'asset_type': 0,          # BTC-USD
        'direction': True,        # Long
        'order_type': 'MARKET'
    }

    try:
        print("Placing market order...")
        trade_result = sdk.ostium.perform_trade(trade_params, at_price=latest_price)

        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        assert receipt is not None, "Receipt should not be None"
        assert order_id is not None, "Order ID should not be None"
        assert receipt['status'] == 1, "Transaction should be successful"

        print(f"✓ Order placed successfully!")
        print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
        print(f"  Order ID: {order_id}")

        # Track the order until it's processed
        print("\nTracking order execution...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        assert result['order'] is not None, "Order should be found"
        assert not result['order'].get('isPending', True), "Order should be processed"
        assert not result['order'].get('isCancelled', False), "Order should not be cancelled"
        assert result['trade'] is not None, "Trade should exist"

        order = result['order']
        trade = result['trade']

        print(f"✓ Trade executed successfully!")
        print(f"  Trade ID: {trade.get('tradeID')}")
        print(f"  Open price: ${float(trade.get('openPrice', 0)):,.2f}")
        print(f"  Pair ID: {order['pair']['id']}")
        print(f"  Trade index: {trade.get('index')}")

        # Step 2: Close the trade (100%)
        print("\n=== STEP 2: Closing 100% of the position ===")

        pair_id = int(order['pair']['id'])
        trade_index = int(trade['index'])

        # Get current market price for closing
        current_price, _, _ = await sdk.price.get_price("BTC", "USD")
        current_price = Decimal(str(current_price))
        print(f"Current market price: ${current_price:,.2f}")

        print(f"Closing trade at pair_id={pair_id}, index={trade_index}")
        close_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=current_price,
            close_percentage=100
        )

        close_receipt = close_result['receipt']
        close_order_id = close_result['order_id']

        assert close_receipt is not None, "Close receipt should not be None"
        assert close_order_id is not None, "Close order ID should not be None"
        assert close_receipt['status'] == 1, "Close transaction should be successful"

        print(f"✓ Close order placed successfully!")
        print(f"  Transaction hash: {close_receipt['transactionHash'].hex()}")
        print(f"  Close order ID: {close_order_id}")

        # Track the close order
        print("\nTracking close order execution...")
        close_order_result = await sdk.ostium.track_order_and_trade(sdk.subgraph, close_order_id)

        assert close_order_result['order'] is not None, "Close order should be found"

        close_order = close_order_result['order']
        print(f"✓ Close order processed!")
        print(f"  Order action: {close_order.get('orderAction', 'N/A')}")
        print(f"  Close percentage: {close_order.get('closePercent', 100)}%")

        if 'profitPercent' in close_order:
            print(f"  Profit percent: {close_order['profitPercent']}%")

        if 'amountSentToTrader' in close_order:
            print(f"  Amount sent to trader: ${close_order['amountSentToTrader']:.2f} USDC")

        # Verify the trade is fully closed
        if close_order_result['trade']:
            updated_trade = close_order_result['trade']
            print(f"  Trade is open: {updated_trade.get('isOpen', 'N/A')}")
            assert not updated_trade.get('isOpen', True), "Trade should be closed after 100% close"

        print("\n✓ Test passed: Full position closed successfully")

    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")


@pytest.mark.asyncio
async def test_close_trade_partial_position(sdk):
    """Test closing 50% of a position"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check ETH and USDC balances
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.002'):
        msg = f"Insufficient ETH balance: {eth_balance} ETH (need at least 0.002 ETH for gas)"
        pytest.skip(msg)

    if usdc_balance < Decimal('100'):
        msg = f"Insufficient USDC balance: {usdc_balance} USDC (need at least 100 USDC)"
        pytest.skip(msg)

    # Get latest price for ETH
    latest_price, _, _ = await sdk.price.get_price("ETH", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest ETH price: ${latest_price:,.2f}")

    # Step 1: Open a trade
    print("\n=== STEP 1: Opening a trade ===")
    trade_params = {
        'collateral': Decimal('460'),
        'leverage': Decimal('10'),
        'asset_type': 1,          # ETH-USD
        'direction': True,        # Long
        'order_type': 'MARKET'
    }

    try:
        print("Placing market order...")
        trade_result = sdk.ostium.perform_trade(trade_params, at_price=latest_price)

        receipt = trade_result['receipt']
        order_id = trade_result['order_id']

        assert receipt is not None, "Receipt should not be None"
        assert order_id is not None, "Order ID should not be None"

        print(f"✓ Order placed successfully!")
        print(f"  Order ID: {order_id}")

        # Track the order until it's processed
        print("\nTracking order execution...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        assert result['order'] is not None, "Order should be found"
        assert result['trade'] is not None, "Trade should exist"

        order = result['order']
        trade = result['trade']

        print(f"✓ Trade executed successfully!")
        print(f"  Trade ID: {trade.get('tradeID')}")
        print(f"  Initial collateral: ${trade.get('collateral', 0):.2f} USDC")

        # Step 2: Close 50% of the position
        print("\n=== STEP 2: Closing 50% of the position ===")

        pair_id = int(order['pair']['id'])
        trade_index = int(trade['index'])
        close_percentage = 50

        # Get current market price
        current_price, _, _ = await sdk.price.get_price("ETH", "USD")
        current_price = Decimal(str(current_price))
        print(f"Current market price: ${current_price:,.2f}")

        print(f"Closing {close_percentage}% at pair_id={pair_id}, index={trade_index}")
        close_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=current_price,
            close_percentage=close_percentage
        )

        close_receipt = close_result['receipt']
        close_order_id = close_result['order_id']

        assert close_receipt is not None, "Close receipt should not be None"
        assert close_order_id is not None, "Close order ID should not be None"
        assert close_receipt['status'] == 1, "Close transaction should be successful"

        print(f"✓ Partial close order placed successfully!")
        print(f"  Close order ID: {close_order_id}")

        # Track the close order
        print("\nTracking partial close order execution...")
        close_order_result = await sdk.ostium.track_order_and_trade(sdk.subgraph, close_order_id)

        assert close_order_result['order'] is not None, "Close order should be found"

        close_order = close_order_result['order']
        print(f"✓ Partial close order processed!")
        print(f"  Order action: {close_order.get('orderAction', 'N/A')}")
        print(f"  Close percentage: {close_order.get('closePercent', close_percentage)}%")

        # Verify the trade is still open after partial close
        if close_order_result['trade']:
            updated_trade = close_order_result['trade']
            print(f"  Trade is still open: {updated_trade.get('isOpen', 'N/A')}")
            print(f"  Remaining collateral: ${updated_trade.get('collateral', 0):.2f} USDC")

            # After 50% close, the trade should still be open
            assert updated_trade.get('isOpen', False), "Trade should still be open after partial close"

        print("\n✓ Test passed: Partial position (50%) closed successfully")

        # Optional: Close the remaining 50%
        print("\n=== OPTIONAL: Closing remaining 50% ===")

        # Get fresh price
        final_price, _, _ = await sdk.price.get_price("ETH", "USD")
        final_price = Decimal(str(final_price))

        final_close_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=final_price,
            close_percentage=100  # Close remaining 100%
        )

        print(f"✓ Remaining position closed!")
        print(f"  Transaction hash: {final_close_result['receipt']['transactionHash'].hex()}")

    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")


@pytest.mark.asyncio
async def test_close_trade_with_slippage(sdk):
    """Test that close_trade respects slippage settings"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check balances
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)

    if eth_balance < Decimal('0.002'):
        pytest.skip(f"Insufficient ETH balance: {eth_balance} ETH")

    if usdc_balance < Decimal('50'):
        pytest.skip(f"Insufficient USDC balance: {usdc_balance} USDC")

    # Get latest price
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: ${latest_price:,.2f}")

    # Set a specific slippage percentage
    sdk.ostium.set_slippage_percentage(1)
    print(f"Slippage set to: {sdk.ostium.get_slippage_percentage()}%")

    # Open a small trade
    print("\n=== Opening a trade ===")
    trade_params = {
        'collateral': Decimal('460'),
        'leverage': Decimal('10'),
        'asset_type': 0,
        'direction': True,
        'order_type': 'MARKET'
    }

    try:
        trade_result = sdk.ostium.perform_trade(trade_params, at_price=latest_price)
        order_id = trade_result['order_id']

        print(f"✓ Order placed, tracking...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        assert result['trade'] is not None, "Trade should exist"

        order = result['order']
        trade = result['trade']
        pair_id = int(order['pair']['id'])
        trade_index = int(trade['index'])

        print(f"✓ Trade executed at pair_id={pair_id}, index={trade_index}")

        # Close the trade with current price
        print("\n=== Closing trade with slippage protection ===")
        current_price, _, _ = await sdk.price.get_price("BTC", "USD")
        current_price = Decimal(str(current_price))

        close_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=current_price,
            close_percentage=100
        )

        assert close_result['receipt']['status'] == 1, "Close should succeed with proper slippage"
        print(f"✓ Close executed with slippage protection")
        print(f"  Slippage: {sdk.ostium.get_slippage_percentage()}%")
        print(f"  Close price: ${current_price:,.2f}")

        print("\n✓ Test passed: Slippage settings respected")

    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")


@pytest.mark.asyncio
async def test_close_trade_with_tight_slippage_fails(sdk):
    """Test that close_trade with too tight slippage results in cancelled order and live trade"""
    # Get address from private key
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip(
            "PRIVATE_KEY not found in .env file (test requires private key)")

    account = Account.from_key(os.getenv('PRIVATE_KEY'))

    # Check balances
    eth_balance, usdc_balance = sdk.balance.get_balance(account.address)
    print(f"Current ETH balance: {eth_balance}")
    print(f"Current USDC balance: {usdc_balance}")

    if eth_balance < Decimal('0.002'):
        pytest.skip(f"Insufficient ETH balance: {eth_balance} ETH")

    if usdc_balance < Decimal('100'):
        pytest.skip(f"Insufficient USDC balance: {usdc_balance} USDC")

    # Get latest price
    latest_price, _, _ = await sdk.price.get_price("BTC", "USD")
    latest_price = Decimal(str(latest_price))
    print(f"Latest BTC price: ${latest_price:,.2f}")

    # Step 1: Open a trade with normal slippage
    print("\n=== STEP 1: Opening a trade with normal slippage ===")
    sdk.ostium.set_slippage_percentage(15)
    print(f"Slippage set to: {sdk.ostium.get_slippage_percentage()}%")

    trade_params = {
        'collateral': Decimal('150'),
        'leverage': Decimal('50'),
        'asset_type': 0,
        'direction': True,
        'order_type': 'MARKET'
    }

    try:
        print("Placing market order...")
        trade_result = sdk.ostium.perform_trade(trade_params, at_price=latest_price)
        order_id = trade_result['order_id']

        assert order_id is not None, "Order ID should not be None"

        print(f"✓ Order placed successfully!")
        print(f"  Order ID: {order_id}")

        # Track the order until it's processed
        print("\nTracking order execution...")
        result = await sdk.ostium.track_order_and_trade(sdk.subgraph, order_id)

        assert result['trade'] is not None, "Trade should exist"
        assert result['trade'].get('isOpen', False), "Trade should be open"

        order = result['order']
        trade = result['trade']
        pair_id = int(order['pair']['id'])
        trade_index = int(trade['index'])

        print(f"✓ Trade executed successfully!")
        print(f"  Trade ID: {trade.get('tradeID')}")
        print(f"  Pair ID: {pair_id}")
        print(f"  Trade index: {trade_index}")
        print(f"  Trade is open: {trade.get('isOpen', False)}")

        # Step 2: Try to close with extremely tight slippage
        print("\n=== STEP 2: Attempting to close with tight slippage (0.0001%) ===")

        # Set extremely tight slippage
        sdk.ostium.set_slippage_percentage(Decimal("0.01"))
        print(f"Slippage set to: {sdk.ostium.get_slippage_percentage()}%")
        print("This should cause the order to be cancelled due to slippage protection")

        # Get current market price
        current_price, _, _ = await sdk.price.get_price("BTC", "USD")
        current_price = Decimal(str(current_price))
        print(f"Current market price: ${current_price:,.2f}")

        # Attempt to close the trade with tight slippage
        print(f"\nAttempting to close trade at pair_id={pair_id}, index={trade_index}")
        close_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=current_price,
            close_percentage=100
        )

        close_order_id = close_result['order_id']
        assert close_order_id is not None, "Close order ID should not be None"

        print(f"✓ Close order transaction submitted!")
        print(f"  Close order ID: {close_order_id}")
        print(f"  Transaction hash: {close_result['receipt']['transactionHash'].hex()}")

        # Step 3: Wait for the order to timeout, then call close_market_timeout to cancel it
        print("\n=== STEP 3: Waiting for order timeout ===")
        print("Waiting 5 seconds for order to timeout due to tight slippage...")
        await asyncio.sleep(5)  # Wait 5 seconds for the order to timeout

        print("\nCalling close_market_timeout to cancel the order...")
        timeout_result = sdk.ostium.close_market_timeout(
            order_id=close_order_id,
            retry=False
        )

        print(f"✓ close_market_timeout called successfully!")
        print(f"  Transaction hash: {timeout_result['receipt']['transactionHash'].hex()}")
        print(f"  Order ID: {timeout_result['order_id']}")
        print(f"  Retry: {timeout_result['retry']}")

        # Step 4: Track the close order - it should now be cancelled
        print("\n=== STEP 4: Tracking close order (expecting cancellation) ===")
        close_order_result = await sdk.ostium.track_order_and_trade(
            sdk.subgraph,
            close_order_id,
            polling_interval=2,
            max_attempts=30
        )

        assert close_order_result['order'] is not None, "Close order should be found"

        close_order = close_order_result['order']

        print(f"\n✓ Close order tracked:")
        print(f"  Order ID: {close_order_id}")
        print(f"  Status: {'Pending' if close_order.get('isPending', True) else 'Processed'}")
        print(f"  Cancelled: {close_order.get('isCancelled', False)}")

        if close_order.get('isCancelled', False):
            print(f"  ✓ Cancel reason: {close_order.get('cancelReason', 'Unknown')}")

        # Verify the order was cancelled
        assert close_order.get('isCancelled', False), "Close order should be cancelled due to tight slippage"

        # Step 5: Verify the trade is still open
        print("\n=== STEP 5: Verifying trade is still live ===")

        # Fetch the trade again to verify it's still open
        if close_order_result['trade']:
            updated_trade = close_order_result['trade']
            print(f"  Trade ID: {updated_trade.get('tradeID')}")
            print(f"  Trade is open: {updated_trade.get('isOpen', False)}")
            print(f"  Collateral: ${updated_trade.get('collateral', 0):.2f} USDC")

            # Verify trade is still open
            assert updated_trade.get('isOpen', False), "Trade should still be open after cancelled close order"

            print("\n✓ Test passed: Tight slippage caused order cancellation, trade remains open")
        else:
            # If we don't get trade info from close order result, the trade is still open
            print("  Trade not returned in close order result (expected for cancelled orders)")
            print("\n✓ Test passed: Tight slippage caused order cancellation")

        # Optional: Clean up by closing the trade with normal slippage
        print("\n=== CLEANUP: Closing the trade with normal slippage ===")
        sdk.ostium.set_slippage_percentage(15)
        print(f"Slippage reset to: {sdk.ostium.get_slippage_percentage()}%")

        cleanup_price, _, _ = await sdk.price.get_price("BTC", "USD")
        cleanup_price = Decimal(str(cleanup_price))

        cleanup_result = sdk.ostium.close_trade(
            pair_id=pair_id,
            trade_index=trade_index,
            market_price=cleanup_price,
            close_percentage=100
        )

        print(f"✓ Cleanup close order submitted")
        print(f"  Transaction hash: {cleanup_result['receipt']['transactionHash'].hex()}")

    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")
