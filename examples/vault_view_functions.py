from ostium_python_sdk import OstiumVault
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Web3 and vault
w3 = Web3(Web3.HTTPProvider(os.getenv('ARBITRUM_RPC_URL')))
vault = OstiumVault(
    w3=w3,
    vault_address=os.getenv('VAULT_ADDRESS'),
    usdc_address=os.getenv('USDC_ADDRESS'),
    private_key=os.getenv('PRIVATE_KEY'),
    verbose=True
)

def print_vault_info():
    # Basic token information
    asset = vault.get_asset()
    print(f"OLP Token Address: {asset}")

    name = vault.get_name()
    print(f"Token Name: {name}")

    symbol = vault.get_symbol()
    print(f"Token Symbol: {symbol}")

    decimals = vault.get_decimals()
    print(f"Token Decimals: {decimals}")

    # Balance and supply information
    balance = vault.get_balance()
    print(f"My OLP Balance: {balance}")

    total_assets = vault.get_total_assets()
    print(f"Total Assets in Vault: {total_assets} USDC")

    available_assets = vault.get_available_assets()
    print(f"Available Assets: {available_assets} USDC")

    tvl = vault.get_tvl()
    print(f"Total Value Locked: {tvl} USDC")

    market_cap = vault.get_market_cap()
    print(f"Market Cap: {market_cap}")

    # PnL related information
    acc_pnl = vault.get_acc_pnl_per_token()
    print(f"Accumulated PnL per Token: {acc_pnl}")

    current_epoch_pnl = vault.get_current_epoch_positive_open_pnl()
    print(f"Current Epoch Positive Open PnL: {current_epoch_pnl}")

    daily_pnl_delta = vault.get_daily_acc_pnl_delta_per_token()
    print(f"Daily Accumulated PnL Delta per Token: {daily_pnl_delta}")

    total_closed_pnl = vault.get_total_closed_pnl()
    print(f"Total Closed PnL: {total_closed_pnl}")

    # Epoch information
    current_epoch = vault.get_current_epoch()
    print(f"Current Epoch: {current_epoch}")

    epoch_start = vault.get_current_epoch_start()
    print(f"Current Epoch Start: {epoch_start}")

    withdraw_timelock = vault.get_withdraw_epochs_timelock()
    print(f"Withdrawal Epochs Timelock: {withdraw_timelock}")

    # Supply and limits
    max_supply = vault.get_current_max_supply()
    print(f"Current Max Supply: {max_supply}")

    max_supply_increase = vault.get_max_supply_increase_daily_p()
    print(f"Max Supply Increase Daily %: {max_supply_increase}")

    # Discount information
    max_discount = vault.get_max_discount_p()
    print(f"Max Discount %: {max_discount}")

    max_discount_threshold = vault.get_max_discount_threshold_p()
    print(f"Max Discount Threshold %: {max_discount_threshold}")

    total_discounts = vault.get_total_discounts()
    print(f"Total Discounts: {total_discounts}")

    total_locked_discounts = vault.get_total_locked_discounts()
    print(f"Total Locked Discounts: {total_locked_discounts}")

    # Other metrics
    collateralization = vault.get_collateralization_p()
    print(f"Collateralization %: {collateralization}")

    total_deposited = vault.get_total_deposited()
    print(f"Total Deposited: {total_deposited} USDC")

    total_liability = vault.get_total_liability()
    print(f"Total Liability: {total_liability}")

    total_rewards = vault.get_total_rewards()
    print(f"Total Rewards: {total_rewards}")

    # Conversion examples
    assets = 1000  # 1000 USDC
    shares = vault.convert_to_shares(assets)
    print(f"\nConversion Examples:")
    print(f"{assets} USDC = {shares} shares")

    converted_assets = vault.convert_to_assets(shares)
    print(f"{shares} shares = {converted_assets} USDC")

if __name__ == "__main__":
    print_vault_info() 