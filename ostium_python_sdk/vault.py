from decimal import Decimal, ROUND_DOWN, ROUND_UP
from web3 import Web3
from .abi.vault_abi import vault_abi
from .abi.usdc_abi import usdc_abi
from .utils import convert_to_scaled_integer, to_base_units, approve_usdc, get_account, fromErrorCodeToMessage
from eth_account.account import Account

# Precision constants
PRECISION_2 = Decimal(1e2)
QUANTIZATION_2 = Decimal('0.01')

PRECISION_6 = Decimal(1e6)
QUANTIZATION_6 = Decimal('0.000001')

PRECISION_18 = Decimal(1e18)
QUANTIZATION_18 = Decimal('0.000000000000000001')

# Minimum lock duration in seconds (1 week)
MIN_LOCK_DURATION = 7 * 24 * 60 * 60  # 7 days in seconds


class OstiumVault:
    """
    Client for interacting with the Ostium vault on the Arbitrum network.

    Supports vault operations like deposits, withdrawals, and managing locked positions.
    This class is designed for market makers and liquidity providers who want to
    interact with the vault directly.

    Args:
        w3: Web3 instance connected to the Arbitrum network
        vault_address: Contract address for the Ostium vault
        usdc_address: Contract address for USDC token
        private_key: Optional private key for transaction signing. If not provided,
                    only read-only operations will be available.
        verbose: Whether to log detailed information
    """

    def __init__(self, w3: Web3, vault_address: str, usdc_address: str, private_key: str = None, verbose=False) -> None:
        self.web3 = w3
        self.verbose = verbose
        self.private_key = private_key
        self.vault_address = vault_address
        self.usdc_address = usdc_address

        # Create contract instances
        self.vault_contract = self.web3.eth.contract(
            address=self.vault_address, abi=vault_abi)
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address, abi=usdc_abi)

        if (verbose):
            print(f"Vault contract: {self.vault_contract.address}")
            print(f"USDC contract: {self.usdc_contract.address}")

    def log(self, message):
        if self.verbose:
            print(message)

    def get_nonce(self, address):
        return self.web3.eth.get_transaction_count(address)

    def deposit(self, amount: float, receiver: str = None):
        """
        Deposit USDC into the vault.

        Args:
            amount: Amount of USDC to deposit
            receiver: Optional address to receive the vault shares (defaults to sender)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization
        """
        account = get_account(self.web3, self.private_key)
        receiver = receiver or account.address

        # Convert amount to base units (6 decimals for USDC)
        amount_base = to_base_units(amount, decimals=6)

        # First approve the vault to spend USDC
        self.log("Approving USDC spend for vault...")
        approve_usdc(
            self.web3,
            self.usdc_contract,
            self.vault_address,
            amount_base,
            self.private_key,
            self.verbose
        )

        try:
            # Build and send deposit transaction
            self.log("Depositing USDC to vault...")
            tx = self.vault_contract.functions.deposit(
                amount_base,
                receiver
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the deposit process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def deposit_with_lock(self, amount: float, lock_period_seconds: int, receiver: str = None):
        """
        Deposit USDC into the vault with a lock period.

        Args:
            amount: Amount of USDC to deposit
            lock_period_seconds: Lock period in seconds (minimum 1 week)
            receiver: Optional address to receive the vault shares (defaults to sender)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization or if lock period is less than 1 week
        """
        if lock_period_seconds < MIN_LOCK_DURATION:
            raise ValueError(
                f"Lock period must be at least {MIN_LOCK_DURATION} seconds (1 week)")

        account = get_account(self.web3, self.private_key)
        receiver = receiver or account.address

        # Convert amount to base units (6 decimals for USDC)
        amount_base = to_base_units(amount, decimals=6)

        # First approve the vault to spend USDC
        self.log("Approving USDC spend for vault...")
        approve_usdc(
            self.web3,
            self.usdc_contract,
            self.vault_address,
            amount_base,
            self.private_key,
            self.verbose
        )

        try:
            # Build and send transaction
            self.log("Depositing USDC to vault with lock...")
            tx = self.vault_contract.functions.depositWithDiscountAndLock(
                amount_base,
                lock_period_seconds,
                receiver
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the deposit with discount and lock process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def withdraw(self, shares: float, receiver: str = None):
        """
        Withdraw USDC from the vault by burning shares.

        Args:
            shares: Amount of vault shares to burn
            receiver: Optional address to receive the USDC (defaults to sender)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization
        """
        account = get_account(self.web3, self.private_key)
        receiver = receiver or account.address

        # Convert shares to base units (18 decimals for vault shares)
        shares_base = to_base_units(shares, decimals=18)

        try:
            # Build and send transaction
            tx = self.vault_contract.functions.redeem(
                shares_base,
                receiver,
                account.address
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the withdraw process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def get_balance(self, address: str = None):
        """
        Get the vault share (OLP) balance for an address.

        Args:
            address: Address to check balance for (defaults to sender if private key provided)

        Returns:
            Balance in vault shares
        """
        if address is None and self.private_key:
            account = get_account(self.web3, self.private_key)
            address = account.address
        elif address is None:
            raise ValueError(
                "Either address parameter or private_key must be provided")

        balance = self.vault_contract.functions.balanceOf(address).call()
        return Decimal(balance) / Decimal(10**6)

    def get_total_assets(self):
        """
        Get the total assets in the vault.

        Returns:
            Total assets in USDC
        """
        total_assets = self.vault_contract.functions.totalAssets().call()
        # Convert from base units
        return Decimal(total_assets) / Decimal(10**6)

    def get_total_supply(self) -> Decimal:
        """
        Get the total supply of vault shares.

        Returns:
            Total supply of vault shares
        """
        total_supply = self.vault_contract.functions.totalSupply().call()
        # Convert from base units (18 decimals)
        return Decimal(total_supply) / Decimal(10**18)

    def get_asset_per_share(self):
        """
        Get the current asset per share ratio.

        Returns:
            Asset per share ratio
        """
        total_assets = self.get_total_assets()
        total_supply = self.get_total_supply()

        if (self.verbose):
            print(f"total_assets TVL???: {total_assets}")
            print(f"total_supply OLP Supply: {total_supply}")

        if total_supply == 0:
            return Decimal(1)

        return total_assets / total_supply

    def get_acc_pnl_per_token(self) -> Decimal:
        """
        Get the accumulated PnL per token.

        Returns:
            Accumulated PnL per token
        """
        pnl = self.vault_contract.functions.accPnlPerToken().call()
        return Decimal(pnl) / Decimal(10**18)  # PRECISION_18

    def get_asset(self) -> str:
        """
        Get the OLP token address.

        Returns:
            OLP token address
        """
        return self.vault_contract.functions.asset().call()

    def get_available_assets(self) -> Decimal:
        """
        Get the available assets in the vault.

        Returns:
            Available assets in USDC
        """
        available = self.vault_contract.functions.availableAssets().call()
        return Decimal(available) / Decimal(10**6)

    def get_collateralization_p(self) -> Decimal:
        """
        Get the collateralization percentage.

        Returns:
            Collateralization percentage (e.g., 99.13 for 99.13%)
        """
        collat = self.vault_contract.functions.collateralizationP().call()
        return Decimal(collat) / Decimal(10**2)  # PRECISION_2

    def convert_to_shares(self, assets: float) -> Decimal:
        """
        Convert assets to shares.

        Args:
            assets: Amount of assets in USDC

        Returns:
            Amount of shares
        """
        assets_base = to_base_units(assets, decimals=6)
        shares = self.vault_contract.functions.convertToShares(
            assets_base).call()
        return Decimal(shares) / Decimal(10**18)

    def convert_to_assets(self, shares: float) -> Decimal:
        """
        Convert shares to assets.

        Args:
            shares: Amount of shares

        Returns:
            Amount of assets in USDC
        """
        shares_base = to_base_units(shares, decimals=18)
        assets = self.vault_contract.functions.convertToAssets(
            shares_base).call()
        return Decimal(assets) / Decimal(10**6)

    def get_current_epoch(self) -> int:
        """
        Get the current epoch number.

        Returns:
            Current epoch number
        """
        return self.vault_contract.functions.currentEpoch().call()

    def get_current_epoch_positive_open_pnl(self) -> Decimal:
        """
        Get the current epoch's positive open PnL.

        Returns:
            Current epoch positive open PnL in USDC
        """
        pnl = self.vault_contract.functions.currentEpochPositiveOpenPnl().call()
        return Decimal(pnl) / Decimal(10**6)  # PRECISION_6

    def get_current_epoch_start(self) -> int:
        """
        Get the timestamp when the current epoch started.

        Returns:
            Current epoch start timestamp
        """
        return self.vault_contract.functions.currentEpochStart().call()

    def get_current_max_supply(self) -> int:
        """
        Get the current maximum supply.

        Returns:
            Current maximum supply as an integer
        """
        return self.vault_contract.functions.currentMaxSupply().call()

    def get_daily_acc_pnl_delta_per_token(self) -> Decimal:
        """
        Get the daily accumulated PnL delta per token.

        Returns:
            Daily accumulated PnL delta per token
        """
        delta = self.vault_contract.functions.dailyAccPnlDeltaPerToken().call()
        return Decimal(delta) / Decimal(10**18)  # PRECISION_18

    def get_market_cap(self) -> Decimal:
        """
        Get the market cap of the vault.

        Returns:
            Market cap in USDC
        """
        market_cap = self.vault_contract.functions.marketCap().call()
        return Decimal(market_cap) / Decimal(10**6)  # PRECISION_6

    def get_max_acc_open_pnl_delta_per_token(self) -> int:
        """
        Get the maximum accumulated open PnL delta per token.

        Returns:
            Maximum accumulated open PnL delta per token as an integer
        """
        return self.vault_contract.functions.maxAccOpenPnlDeltaPerToken().call()

    def get_max_acc_pnl_per_token(self) -> int:
        """
        Get the maximum accumulated PnL per token.

        Returns:
            Maximum accumulated PnL per token as an integer
        """
        return self.vault_contract.functions.maxAccPnlPerToken().call()

    def get_max_daily_acc_pnl_delta_per_token(self) -> int:
        """
        Get the maximum daily accumulated PnL delta per token.

        Returns:
            Maximum daily accumulated PnL delta per token as an integer
        """
        return self.vault_contract.functions.maxDailyAccPnlDeltaPerToken().call()

    def get_max_discount_p(self) -> Decimal:
        """
        Get the maximum discount percentage.

        Returns:
            Maximum discount percentage (e.g., 50.00 for 50%)
        """
        discount = self.vault_contract.functions.maxDiscountP().call()
        return Decimal(discount) / Decimal(10**2)  # PRECISION_2

    def get_max_discount_threshold_p(self) -> Decimal:
        """
        Get the maximum discount threshold percentage.

        Returns:
            Maximum discount threshold percentage (e.g., 120.00 for 120%)
        """
        threshold = self.vault_contract.functions.maxDiscountThresholdP().call()
        return Decimal(threshold) / Decimal(10**2)  # PRECISION_2

    def get_max_supply_increase_daily_p(self) -> Decimal:
        """
        Get the maximum supply increase daily percentage.

        Returns:
            Maximum supply increase daily percentage (e.g., 300.00 for 300%)
        """
        increase = self.vault_contract.functions.maxSupplyIncreaseDailyP().call()
        return Decimal(increase) / Decimal(10**2)  # PRECISION_2

    def get_name(self) -> str:
        """
        Get the name of the vault token.

        Returns:
            Token name
        """
        return self.vault_contract.functions.name().call()

    def get_symbol(self) -> str:
        """
        Get the symbol of the vault token.

        Returns:
            Token symbol
        """
        return self.vault_contract.functions.symbol().call()

    def get_decimals(self) -> int:
        """
        Get the number of decimals for the vault token.

        Returns:
            Number of decimals
        """
        return self.vault_contract.functions.decimals().call()

    def get_total_closed_pnl(self) -> Decimal:
        """
        Get the total closed PnL.

        Returns:
            Total closed PnL in USDC
        """
        pnl = self.vault_contract.functions.totalClosedPnl().call()
        return Decimal(pnl) / Decimal(10**6)  # PRECISION_6

    def get_total_deposited(self) -> Decimal:
        """
        Get the total amount deposited in the vault.

        Returns:
            Total deposited amount in USDC
        """
        total = self.vault_contract.functions.totalDeposited().call()
        return Decimal(total) / Decimal(10**6)

    def get_total_discounts(self) -> Decimal:
        """
        Get the total discounts.

        Returns:
            Total discounts in USDC
        """
        discounts = self.vault_contract.functions.totalDiscounts().call()
        return Decimal(discounts) / Decimal(10**6)  # PRECISION_6

    def get_total_liability(self) -> Decimal:
        """
        Get the total liability.

        Returns:
            Total liability in USDC
        """
        liability = self.vault_contract.functions.totalLiability().call()
        return Decimal(liability) / Decimal(10**6)  # PRECISION_6

    def get_total_locked_discounts(self) -> Decimal:
        """
        Get the total locked discounts.

        Returns:
            Total locked discounts in USDC
        """
        discounts = self.vault_contract.functions.totalLockedDiscounts().call()
        return Decimal(discounts) / Decimal(10**6)  # PRECISION_6

    def get_total_rewards(self) -> Decimal:
        """
        Get the total rewards.

        Returns:
            Total rewards in USDC
        """
        rewards = self.vault_contract.functions.totalRewards().call()
        return Decimal(rewards) / Decimal(10**6)  # PRECISION_6

    def get_tvl(self) -> Decimal:
        """
        Get the total value locked in the vault.

        Returns:
            Total value locked in USDC
        """
        tvl = self.vault_contract.functions.tvl().call()
        return Decimal(tvl) / Decimal(10**6)

    def get_withdraw_epochs_timelock(self) -> int:
        """
        Get the number of epochs required for withdrawal timelock.

        Returns:
            Number of epochs for withdrawal timelock
        """
        return self.vault_contract.functions.withdrawEpochsTimelock().call()

    def get_share_to_assets_price(self) -> Decimal:
        """Get the share to assets price."""
        price = self.vault_contract.functions.shareToAssetsPrice().call()
        return Decimal(price) / Decimal(10**18)

    def preview_deposit(self, assets: Decimal) -> Decimal:
        """
        Preview how many shares would be received for depositing assets.

        Args:
            assets: Amount of assets to deposit in USDC

        Returns:
            Amount of shares that would be received
        """
        try:
            share_to_assets_price = self.get_share_to_assets_price()
            if share_to_assets_price != Decimal(0):
                return (assets / share_to_assets_price).quantize(QUANTIZATION_6, rounding=ROUND_DOWN)
            return Decimal(0)
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the preview deposit process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def preview_mint(self, shares: Decimal) -> Decimal:
        """
        Preview how many assets would be needed to mint shares.

        Args:
            shares: Amount of shares to mint

        Returns:
            Amount of assets needed in USDC
        """
        share_to_assets_price = self.get_share_to_assets_price()
        uint256_max = Decimal((2**256 - 1) / PRECISION_6)
        if shares == uint256_max and share_to_assets_price >= Decimal(1):
            return shares
        return (shares * share_to_assets_price).quantize(QUANTIZATION_6, rounding=ROUND_UP)

    def preview_redeem(self, shares: Decimal) -> Decimal:
        """
        Preview how many assets would be received for redeeming shares.

        Args:
            shares: Amount of shares to redeem

        Returns:
            Amount of assets that would be received in USDC
        """
        return self.convert_to_assets(shares)

    def preview_withdraw(self, assets: Decimal) -> Decimal:
        """
        Preview how many shares would be burned for withdrawing assets.

        Args:
            assets: Amount of assets to withdraw in USDC

        Returns:
            Amount of shares that would be burned
        """
        return self.convert_to_shares(assets)

    def get_lock_discount_p(self, lock_duration_seconds: int) -> Decimal:
        """
        Calculate the lock discount percentage based on lock duration and current collateralization.

        Args:
            lock_duration: Lock duration in seconds

        Returns:
            Lock discount percentage (e.g., 50.00 for 50%)
        """
        max_discount_threshold_p = self.get_max_discount_threshold_p()
        max_lock_duration = 365 * 24 * 60 * 60  # 1 year in seconds
        max_discount_p = self.get_max_discount_p()
        collateralization_p = self.get_collateralization_p()

        lock_discount_p = Decimal(0)

        if collateralization_p <= Decimal(100):
            result = max_discount_p
        elif collateralization_p <= max_discount_threshold_p:
            numerator1 = max_discount_p * \
                (max_discount_threshold_p - collateralization_p)
            denominator1 = (max_discount_threshold_p - Decimal(100))
            if denominator1 != Decimal(0):
                result = (
                    numerator1 / denominator1).quantize(QUANTIZATION_2, rounding=ROUND_DOWN)
        else:
            result = Decimal(0)

        lock_discount_p = (result * Decimal(lock_duration_seconds) / Decimal(
            max_lock_duration)).quantize(QUANTIZATION_2, rounding=ROUND_DOWN)

        return lock_discount_p

    def preview_deposit_with_discount_and_lock(self, assets: Decimal, lock_duration_seconds: int) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Preview the result of depositing assets with discount and lock.

        Args:
            assets: Amount of assets to deposit in USDC
            lock_duration: Lock duration in seconds

        Returns:
            Tuple of (shares, assets_deposited, assets_discount, lock_discount_p)
        """
        lock_discount_p = self.get_lock_discount_p(lock_duration_seconds)

        simulated_assets = assets * \
            ((Decimal(100) + lock_discount_p) / Decimal(100)
             ).quantize(QUANTIZATION_2, rounding=ROUND_DOWN)
        shares = self.preview_deposit(simulated_assets)
        assets_deposited = assets
        assets_discount = simulated_assets - assets_deposited

        return shares, assets_deposited, assets_discount, lock_discount_p

    def preview_mint_with_discount_and_lock(self, shares: Decimal, lock_duration_seconds: int) -> tuple[Decimal, Decimal, Decimal]:
        """
        Preview the result of minting shares with discount and lock.

        Args:
            shares: Amount of shares to mint
            lock_duration: Lock duration in seconds

        Returns:
            Tuple of (shares, assets_deposited, assets_discount)
        """
        lock_discount_p = self.get_lock_discount_p(lock_duration_seconds)

        assets = self.preview_mint(shares)
        assets_deposited = (assets * (Decimal(100) / (Decimal(100) +
                            lock_discount_p))).quantize(QUANTIZATION_6, rounding=ROUND_DOWN)
        assets_discount = assets - assets_deposited

        return shares, assets_deposited, assets_discount

    def redeem(self, shares: float, receiver: str = None, owner: str = None):
        """
        Redeem shares for assets.

        Args:
            shares: Amount of shares to redeem
            receiver: Optional address to receive the assets (defaults to sender)
            owner: Optional address that owns the shares (defaults to sender)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization
        """
        if shares > self.max_redeem():
            raise ValueError(
                f"Shares to redeem ({shares}) exceeds maximum redeemable amount ({self.max_redeem()})")

        account = get_account(self.web3, self.private_key)
        receiver = receiver or account.address
        owner = owner or account.address

        # Convert shares to base units (18 decimals for vault shares)
        shares_base = to_base_units(shares, decimals=18)

        try:
            # Build and send transaction
            tx = self.vault_contract.functions.redeem(
                shares_base,
                receiver,
                owner
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the redeem process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def max_withdraw(self, owner: str = None) -> Decimal:
        """
        Get the maximum amount of assets that can be withdrawn by an owner.

        Args:
            owner: Address to check max withdrawal for (defaults to sender if private key provided)

        Returns:
            Maximum amount of assets that can be withdrawn in USDC
        """
        if owner is None and self.private_key:
            account = get_account(self.web3, self.private_key)
            owner = account.address
        elif owner is None:
            raise ValueError(
                "Either owner parameter or private_key must be provided")

        try:
            max_assets = self.vault_contract.functions.maxWithdraw(
                owner).call()
            return Decimal(max_assets) / PRECISION_6
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the max withdraw process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def max_mint(self, owner: str = None) -> Decimal:
        """
        Get the maximum amount of shares that can be minted by an owner.

        Args:
            owner: Address to check max mint for (defaults to sender if private key provided)

        Returns:
            Maximum amount of shares that can be minted
        """
        if owner is None and self.private_key:
            account = get_account(self.web3, self.private_key)
            owner = account.address
        elif owner is None:
            raise ValueError(
                "Either owner parameter or private_key must be provided")

        try:
            max_shares = self.vault_contract.functions.maxMint(owner).call()
            return Decimal(max_shares) / PRECISION_18
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the max mint process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def max_redeem(self, owner: str = None) -> Decimal:
        """
        Get the maximum amount of shares that can be redeemed by an owner.

        Args:
            owner: Address to check max redeem for (defaults to sender if private key provided)

        Returns:
            Maximum amount of shares that can be redeemed
        """
        if owner is None and self.private_key:
            account = get_account(self.web3, self.private_key)
            owner = account.address
        elif owner is None:
            raise ValueError(
                "Either owner parameter or private_key must be provided")

        try:
            max_shares = self.vault_contract.functions.maxRedeem(owner).call()
            return Decimal(max_shares) / PRECISION_18
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the max redeem process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def mint_with_discount_and_lock(self, shares: float, lock_duration_seconds: int, receiver: str = None):
        """
        Mint shares with discount and lock period.

        Args:
            shares: Amount of shares to mint
            lock_duration_seconds: Lock period in seconds (minimum 1 week)
            receiver: Optional address to receive the shares (defaults to sender)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization or if lock period is less than 1 week
        """
        if lock_duration_seconds < MIN_LOCK_DURATION:
            raise ValueError(
                f"Lock period must be at least {MIN_LOCK_DURATION} seconds (1 week)")

        account = get_account(self.web3, self.private_key)
        receiver = receiver or account.address

        if (self.verbose):
            print(f"shares: {shares}")
            print(f"lock_duration_seconds: {lock_duration_seconds}")
            print(f"receiver: {receiver}")

        # Convert shares to base units (18 decimals for vault shares)
        shares_base = to_base_units(shares, decimals=18)

        if (self.verbose):
            print(f"shares_base: {shares_base}")

        # Calculate required USDC amount
        assets_needed = self.preview_mint(Decimal(shares))

        if (self.verbose):
            print(f"assets_needed: {assets_needed}")

        assets_base = to_base_units(assets_needed, decimals=6)

        # First approve the vault to spend USDC
        self.log(
            f"Approving {assets_needed} = {assets_base} USDC spend for vault...")
        approve_usdc(
            self.web3,
            self.usdc_contract,
            self.vault_address,
            assets_base,
            self.private_key,
            self.verbose
        )

        try:
            # Build and send transaction
            tx = self.vault_contract.functions.mintWithDiscountAndLock(
                shares_base,
                lock_duration_seconds,
                receiver
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the mint with discount and lock process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def make_withdraw_request(self, shares: float, owner: str = None):
        """
        Make a withdrawal request for the specified number of shares.

        Args:
            shares: The number of shares to withdraw
            owner: Optional address of the owner if different from the account (for delegation)

        Returns:
            The transaction receipt
        """

        try:
            account = get_account(self.web3, self.private_key)
            owner = owner or account.address

            # Convert shares to base units (18 decimals for vault shares)
            shares_base = to_base_units(shares, decimals=18)

            # Build and send transaction
            tx = self.vault_contract.functions.makeWithdrawRequest(
                shares_base,
                owner
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the make withdraw request process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def cancel_withdraw_request(self, shares: float, owner: str = None, unlock_epoch: int = None):
        """
        Cancel a withdrawal request for shares.

        Args:
            shares: Amount of shares to cancel withdrawal for
            owner: Optional address that owns the shares (defaults to sender)
            unlock_epoch: Optional epoch number when the withdrawal would unlock (defaults to current epoch + timelock)

        Returns:
            Transaction receipt

        Raises:
            ValueError: If no private key is provided during initialization
        """

        try:
            account = get_account(self.web3, self.private_key)
            owner = owner or account.address

            if unlock_epoch is None:
                current_epoch = self.get_current_epoch()
                timelock = self.get_withdraw_epochs_timelock()
                unlock_epoch = current_epoch + timelock

            # Convert shares to base units (18 decimals for vault shares)
            shares_base = to_base_units(shares, decimals=18)

            # Build and send transaction
            tx = self.vault_contract.functions.cancelWithdrawRequest(
                shares_base,
                owner,
                unlock_epoch
            ).build_transaction({
                'from': account.address,
                'nonce': self.get_nonce(account.address)
            })

            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return receipt
        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(
                str(e), verbose=self.verbose)
            print(
                f"An error occurred during the make withdraw request process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def get_acc_rewards_per_token(self) -> Decimal:
        """Get the accumulated rewards per token."""
        rewards = self.vault_contract.functions.accRewardsPerToken().call()
        return Decimal(rewards) / Decimal(10**18)  # Adjust precision as needed

    def get_last_daily_acc_pnl_delta_reset_ts(self) -> int:
        """Get the last daily accumulated PnL delta reset timestamp."""
        return self.vault_contract.functions.lastDailyAccPnlDeltaResetTs().call()
