import os
import pytest
from decimal import Decimal
from dotenv import load_dotenv
from ostium_python_sdk import OstiumSDK
from ostium_python_sdk.config import NetworkConfig
from eth_account import Account
from web3 import Web3


@pytest.fixture(scope="module")
def sdk():
    # Load environment variables
    load_dotenv()

    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError("RPC_URL not found in .env file")

    # Initialize SDK with testnet config
    config = NetworkConfig.testnet()
    return OstiumSDK(config)


@pytest.fixture(scope="module")
def account():
    if not os.getenv('PRIVATE_KEY'):
        pytest.skip("PRIVATE_KEY not found in .env file")
    return Account.from_key(os.getenv('PRIVATE_KEY'))


def test_convert_to_shares(sdk):
    """Test converting assets to shares"""
    # Test with 1000 USDC
    assets = Decimal('1000.0')
    shares = sdk.vault.convert_to_shares(assets)

    # Shares should be greater than 0
    assert shares > 0

    # If TVL is available, we can make more specific assertions
    tvl = sdk.vault.get_tvl()
    if tvl > 0:
        # Shares should be proportional to assets
        total_supply = sdk.vault.get_total_supply()
        expected_shares = (assets * total_supply) / tvl
        # Allow for small rounding differences
        assert abs(shares - expected_shares) < Decimal('0.01')


def test_convert_to_assets(sdk):
    """Test converting shares to assets"""
    # Test with 1000 shares
    shares = Decimal('1000.0')
    assets = sdk.vault.convert_to_assets(shares)

    # Assets should be greater than 0
    assert assets > 0

    # If TVL is available, we can make more specific assertions
    tvl = sdk.vault.get_tvl()
    if tvl > 0:
        # Assets should be proportional to shares
        total_supply = sdk.vault.get_total_supply()
        expected_assets = (shares * tvl) / total_supply

        # Calculate relative difference instead of absolute
        relative_diff = abs(assets - expected_assets) / expected_assets
        # Allow for 0.1% difference due to rounding
        assert relative_diff < Decimal(
            '0.001'), f"Relative difference {relative_diff} exceeds tolerance"


def test_convert_roundtrip(sdk):
    """Test that converting assets to shares and back gives approximately the same amount"""
    original_assets = Decimal('1000.0')
    shares = sdk.vault.convert_to_shares(original_assets)
    converted_assets = sdk.vault.convert_to_assets(shares)

    # The roundtrip conversion should be close to the original amount
    # Allow for small rounding differences
    assert abs(original_assets - converted_assets) < Decimal('0.01')


def test_vault_metrics(sdk):
    """Test various vault metrics"""
    # Test TVL
    tvl = sdk.vault.get_tvl()
    assert tvl >= 0

    # Test total supply
    total_supply = sdk.vault.get_total_supply()
    assert total_supply >= 0

    # Test total assets
    total_assets = sdk.vault.get_total_assets()
    assert total_assets >= 0

    # Test available assets
    available_assets = sdk.vault.get_available_assets()
    assert available_assets >= 0
    assert available_assets <= total_assets


def test_share_price_calculation(sdk):
    """Test share price calculation using convert functions"""
    # Get 1 share worth of assets
    one_share = Decimal('1.0')
    assets_for_one_share = sdk.vault.convert_to_assets(one_share)

    # Get 1 asset worth of shares
    one_asset = Decimal('1.0')
    shares_for_one_asset = sdk.vault.convert_to_shares(one_asset)

    # These should be reciprocals of each other (allowing for rounding)
    assert abs(assets_for_one_share * shares_for_one_asset -
               Decimal('1.0')) < Decimal('0.01')

# def test_max_deposit_and_mint(sdk, account):
#     """Test max deposit and mint calculations"""
#     # Test max deposit
#     max_deposit = sdk.vault.max_deposit(account.address)
#     assert max_deposit >= 0

#     # Test max mint
#     max_mint = sdk.vault.max_mint(account.address)
#     assert max_mint >= 0

#     # If we have a max deposit, we should be able to convert it to shares
#     if max_deposit > 0:
#         shares = sdk.vault.convert_to_shares(max_deposit)
#         assert shares > 0


def test_current_epoch_info(sdk):
    """Test current epoch related functions"""
    # Test current epoch
    current_epoch = sdk.vault.get_current_epoch()
    assert current_epoch >= 0

    # Test current epoch start
    epoch_start = sdk.vault.get_current_epoch_start()
    assert epoch_start > 0

    # Test withdraw epochs timelock
    timelock = sdk.vault.get_withdraw_epochs_timelock()
    assert timelock > 0


def test_pnl_related_functions(sdk):
    """Test PnL related functions"""
    # Test accPnlPerToken
    acc_pnl = sdk.vault.get_acc_pnl_per_token()
    assert isinstance(acc_pnl, (int, Decimal))

    # Test currentEpochPositiveOpenPnl
    open_pnl = sdk.vault.get_current_epoch_positive_open_pnl()
    assert open_pnl >= 0


def test_balance_and_allowance(sdk, account):
    """Test balance and allowance functions"""
    # Test balance
    balance = sdk.vault.get_balance(account.address)
    assert balance >= 0

    # Test allowance
    allowance = sdk.vault.allowance(account.address, sdk.vault.vault_address)
    assert allowance >= 0


def test_withdraw_request_functions(sdk, account):
    """Test withdraw request related functions"""
    # Test total shares being withdrawn
    shares_being_withdrawn = sdk.vault.total_shares_being_withdrawn(
        account.address)
    assert shares_being_withdrawn >= 0

    # Test withdraw requests
    current_epoch = sdk.vault.get_current_epoch()
    withdraw_request = sdk.vault.withdraw_requests(
        account.address, current_epoch)
    assert withdraw_request >= 0


def test_token_info(sdk):
    """Test token information functions"""
    # Test token name
    name = sdk.vault.get_name()
    assert name == "ostiumLP"

    # Test token symbol
    symbol = sdk.vault.get_symbol()
    assert symbol == "oLP"

    # Test token decimals
    decimals = sdk.vault.get_decimals()
    assert decimals == 6


def test_zero_address_balance(sdk):
    """Test balance for zero address"""
    zero_address = "0x0000000000000000000000000000000000000000"
    balance = sdk.vault.get_balance(zero_address)
    assert balance == 0


def test_max_redeem(sdk, account):
    """Test max redeem function"""
    max_redeem = sdk.vault.max_redeem(account.address)
    assert max_redeem >= 0


def test_withdrawal_timelock(sdk):
    """Test withdrawal epochs timelock"""
    timelock = sdk.vault.get_withdraw_epochs_timelock()
    assert timelock > 0
    assert isinstance(timelock, int)


def test_vault_parameters(sdk):
    """Test various vault parameters"""
    # Test max supply
    max_supply = sdk.vault.get_current_max_supply()
    assert max_supply > 0

    # Test max supply increase daily percentage
    max_supply_increase = sdk.vault.get_max_supply_increase_daily_p()
    assert max_supply_increase > 0
    assert max_supply_increase <= 1000  # Should be reasonable percentage

    # Test max discount percentage
    max_discount = sdk.vault.get_max_discount_p()
    assert max_discount > 0
    assert max_discount <= 100  # Should be reasonable percentage

    # Test max discount threshold percentage
    max_discount_threshold = sdk.vault.get_max_discount_threshold_p()
    assert max_discount_threshold > 0
    assert max_discount_threshold <= 1000  # Should be reasonable percentage


def test_discount_metrics(sdk):
    """Test discount related metrics"""
    # Test total discounts
    total_discounts = sdk.vault.get_total_discounts()
    assert total_discounts >= 0

    # Test total locked discounts
    total_locked_discounts = sdk.vault.get_total_locked_discounts()
    assert total_locked_discounts >= 0
    assert total_locked_discounts <= total_discounts


def test_collateralization(sdk):
    """Test collateralization metrics"""
    # Test collateralization percentage
    collat_p = sdk.vault.get_collateralization_p()
    assert collat_p > 0
    assert collat_p <= 100  # Should be percentage

    # Test total deposited
    total_deposited = sdk.vault.get_total_deposited()
    assert total_deposited >= 0

    # Test total liability
    total_liability = sdk.vault.get_total_liability()
    assert isinstance(total_liability, (int, Decimal))


def test_rewards(sdk):
    """Test rewards related functions"""
    # Test total rewards
    total_rewards = sdk.vault.get_total_rewards()
    assert total_rewards >= 0

    # Test acc rewards per token
    acc_rewards = sdk.vault.get_acc_rewards_per_token()
    assert acc_rewards >= 0


def test_daily_metrics(sdk):
    """Test daily metrics"""
    # Test daily acc PnL delta per token
    daily_pnl_delta = sdk.vault.get_daily_acc_pnl_delta_per_token()
    assert isinstance(daily_pnl_delta, (int, Decimal))

    # Test last daily acc PnL delta reset timestamp
    last_reset = sdk.vault.get_last_daily_acc_pnl_delta_reset_ts()
    assert last_reset > 0
    assert isinstance(last_reset, int)


def test_share_price(sdk):
    """Test share price calculation"""
    # Test share to assets price
    share_price = sdk.vault.get_share_to_assets_price()
    assert share_price > 0

    # Verify price calculation
    one_share = Decimal('1.0')
    assets = sdk.vault.convert_to_assets(one_share)

    # Print values for debugging
    print(f"\nShare price (18 decimals): {share_price}")
    print(f"Assets (6 decimals): {assets}")

    # Convert share_price to 6 decimals for comparison
    share_price_6_decimals = share_price * \
        Decimal('1000000000000')  # Convert from 18 to 6 decimals

    # Calculate relative difference
    relative_diff = abs(assets - share_price_6_decimals) / \
        share_price_6_decimals
    # Allow for 0.1% difference due to rounding
    assert relative_diff < Decimal(
        '0.001'), f"Relative difference {relative_diff} exceeds tolerance"


def test_locked_deposits(sdk):
    """Test locked deposits related functions"""
    # Test locked deposits count
    count = sdk.vault.get_locked_deposits_count()
    assert count >= 0

    # If there are locked deposits, test getting deposit info
    if count > 0:
        # Test getting first locked deposit
        deposit = sdk.vault.get_locked_deposit(0)
        assert deposit is not None
        assert 'owner' in deposit
        assert 'shares' in deposit
        assert 'assetsDeposited' in deposit
        assert 'lockDuration' in deposit

        # Test getting deposit through locked_deposits function
        deposit_info = sdk.vault.locked_deposits(0)
        assert deposit_info is not None
        assert len(deposit_info) == 6  # Should return tuple of 6 values


def test_market_metrics(sdk):
    """Test market cap and current balance"""
    # Test market cap
    market_cap = sdk.vault.get_market_cap()
    assert market_cap >= 0

    # Test current balance
    current_balance = sdk.vault.get_current_balance()
    assert current_balance >= 0

    # Market cap should be related to total supply and share price
    total_supply = sdk.vault.get_total_supply()
    share_price = sdk.vault.get_share_to_assets_price()
    expected_market_cap = total_supply * share_price

    # Allow for small rounding differences
    relative_diff = abs(market_cap - expected_market_cap) / expected_market_cap
    assert relative_diff < Decimal('0.001')


def test_preview_functions(sdk):
    """Test preview functions for deposits and withdrawals"""
    # Test preview deposit
    assets = Decimal('1000.0')
    preview_shares = sdk.vault.preview_deposit(assets)
    assert preview_shares > 0

    # Test preview mint
    shares = Decimal('1000.0')
    preview_assets = sdk.vault.preview_mint(shares)
    assert preview_assets > 0

    # Test preview redeem
    preview_redeem_assets = sdk.vault.preview_redeem(shares)
    assert preview_redeem_assets > 0

    # Test preview withdraw
    preview_withdraw_shares = sdk.vault.preview_withdraw(assets)
    assert preview_withdraw_shares > 0

    # Verify relationships between preview functions
    # preview_deposit and preview_mint should be related
    relative_diff = abs(preview_shares * preview_assets -
                        assets * shares) / (assets * shares)
    assert relative_diff < Decimal('0.001')

    # preview_redeem and preview_withdraw should be related
    relative_diff = abs(preview_redeem_assets *
                        preview_withdraw_shares - assets * shares) / (assets * shares)
    assert relative_diff < Decimal('0.001')


def test_total_supply(sdk):
    """Test total supply"""
    # Get total supply
    total_supply = sdk.vault.get_total_supply()
    print(f"\nTotal supply: {total_supply}")
    
    # Check if it's 1 billion (10^9)
    expected_supply = Decimal('1000000000')
    assert total_supply == expected_supply, f"Total supply {total_supply} is not equal to expected {expected_supply}"


def test_locked_deposits(sdk):
    """Test locked deposits related functions"""
    # Test locked deposits count
    count = sdk.vault.get_locked_deposits_count()
    assert count >= 0

    # If there are locked deposits, test getting deposit info
    if count > 0:
        # Test getting first locked deposit
        deposit = sdk.vault.get_locked_deposit(0)
        assert deposit is not None
        assert 'owner' in deposit
        assert 'shares' in deposit
        assert 'assetsDeposited' in deposit
        assert 'lockDuration' in deposit

        # Test getting deposit through locked_deposits function
        deposit_info = sdk.vault.locked_deposits(0)
        assert deposit_info is not None
        assert len(deposit_info) == 6  # Should return tuple of 6 values


def test_market_metrics(sdk):
    """Test market cap and current balance"""
    # Test market cap
    market_cap = sdk.vault.get_market_cap()
    assert market_cap >= 0

    # Test current balance
    current_balance = sdk.vault.get_current_balance()
    assert current_balance >= 0

    # Market cap should be related to total supply and share price
    total_supply = sdk.vault.get_total_supply()
    share_price = sdk.vault.get_share_to_assets_price()
    expected_market_cap = total_supply * share_price

    # Allow for small rounding differences
    relative_diff = abs(market_cap - expected_market_cap) / expected_market_cap
    assert relative_diff < Decimal('0.001')


def test_preview_functions(sdk):
    """Test preview functions for deposits and withdrawals"""
    # Test preview deposit
    assets = Decimal('1000.0')
    preview_shares = sdk.vault.preview_deposit(assets)
    assert preview_shares > 0

    # Test preview mint
    shares = Decimal('1000.0')
    preview_assets = sdk.vault.preview_mint(shares)
    assert preview_assets > 0

    # Test preview redeem
    preview_redeem_assets = sdk.vault.preview_redeem(shares)
    assert preview_redeem_assets > 0

    # Test preview withdraw
    preview_withdraw_shares = sdk.vault.preview_withdraw(assets)
    assert preview_withdraw_shares > 0

    # Verify relationships between preview functions
    # preview_deposit and preview_mint should be related
    relative_diff = abs(preview_shares * preview_assets -
                        assets * shares) / (assets * shares)
    assert relative_diff < Decimal('0.001')

    # preview_redeem and preview_withdraw should be related
    relative_diff = abs(preview_redeem_assets *
                        preview_withdraw_shares - assets * shares) / (assets * shares)
    assert relative_diff < Decimal('0.001')


def test_total_supply(sdk):
    """Test total supply and its relationships with other metrics"""
    # Get total supply
    total_supply = sdk.vault.get_total_supply()
    assert total_supply >= 0
    
    # Get total assets and TVL
    total_assets = sdk.vault.get_total_assets()
    tvl = sdk.vault.get_tvl()
    
    # Get share price
    share_price = sdk.vault.get_share_to_assets_price()
    
    # Print values for debugging
    print(f"\nTotal supply: {total_supply}")
    print(f"Total assets: {total_assets}")
    print(f"TVL: {tvl}")
    print(f"Share price: {share_price}")
    
    # Total supply should be related to TVL and share price
    # TVL = total_supply * share_price
    expected_tvl = total_supply * share_price
    
    # Calculate relative difference
    relative_diff = abs(tvl - expected_tvl) / expected_tvl if expected_tvl > 0 else 0
    # Allow for 0.1% difference due to rounding
    assert relative_diff < Decimal('0.001'), f"Relative difference {relative_diff} exceeds tolerance"
    
    # Total assets should be less than or equal to TVL
    assert total_assets <= tvl, "Total assets should not exceed TVL"
    
    # If there are assets, total supply should be positive
    if total_assets > 0:
        assert total_supply > 0, "Total supply should be positive when there are assets"
    