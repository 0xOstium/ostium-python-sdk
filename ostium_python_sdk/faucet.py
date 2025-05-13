from web3 import Web3
from .exceptions import NetworkError
import time
from datetime import datetime
from ostium_python_sdk.abi.faucet_testnet_abi import faucet_abi  # Import the ABI

# Class for testnet usage only - to get testnet USDC tokens


class Faucet:
    def __init__(self, w3: Web3, private_key: str, verbose=False) -> None:
        self.web3 = w3
        self.verbose = verbose
        self.private_key = private_key
        self.faucet_address = "0x6830C550814105d8B27bDAEC0DB391cAa7B967c8"
        self.faucet_contract = self.web3.eth.contract(
            address=self.faucet_address,
            abi=faucet_abi
        )

    def log(self, message):
        if self.verbose:
            print(message)

    def _format_waiting_time(self, next_request_time: int) -> str:
        """Format the waiting time into a human-readable string"""
        current_time = int(time.time())
        wait_seconds = next_request_time - current_time

        if wait_seconds <= 0:
            return "now"

        wait_minutes = wait_seconds // 60
        if wait_minutes < 60:
            return f"{wait_minutes} minute{'s' if wait_minutes != 1 else ''}"

        wait_hours = wait_minutes // 60
        remaining_minutes = wait_minutes % 60
        if wait_hours < 24:
            time_str = f"{wait_hours} hour{'s' if wait_hours != 1 else ''}"
            if remaining_minutes > 0:
                time_str += f" and {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
            return time_str

        wait_days = wait_hours // 24
        return f"{wait_days} day{'s' if wait_days != 1 else ''}"

    def _check_private_key(self):
        if not self.private_key:
            raise ValueError(
                "Private key is required for Faucet operations")

    def _get_account(self):
        self._check_private_key()
        return self.web3.eth.account.from_key(self.private_key)

    def request_tokens(self) -> dict:
        account = self._get_account()
        self.log("Requesting tokens from faucet")
        """
        Request testnet USDC tokens from the faucet.
        Raises:
            - NetworkError if called on mainnet
            - Exception if request is not allowed or fails
        Returns:
            Transaction receipt
        """
        try:
            # Get the current base fee and add a buffer
            base_fee = self.web3.eth.get_block('latest')['baseFeePerGas']
            # Add 50% buffer to ensure it's above base fee
            gas_price = int(base_fee * 1.5)

            # Build the transaction
            tx = self.faucet_contract.functions.requestTokens().build_transaction({
                'from': account.address,
                'nonce': self.web3.eth.get_transaction_count(account.address),
                'gas': 300000,  # Add gas limit
                'gasPrice': gas_price,  # Use calculated gas price
                'chainId': self.web3.eth.chain_id,  # Add chain ID
            })

            # Sign the transaction
            signed_tx = account.sign_transaction(tx)

            # Send the raw transaction using raw_transaction
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)

            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt

        except Exception as e:
            if "NotAllowed" in str(e):
                next_time = self.get_next_request_time(account.address)
                wait_time = self._format_waiting_time(next_time)
                next_time_str = datetime.fromtimestamp(
                    next_time).strftime('%Y-%m-%d %H:%M:%S')
                raise Exception(
                    f"Cannot request tokens yet. You can request again in {wait_time} "
                    f"(at {next_time_str})"
                )
            elif "NotWhitelisted" in str(e):
                raise Exception(
                    "Address is not whitelisted for token requests")
            else:
                raise Exception(f"Failed to request tokens: {str(e)}")

    def can_request_tokens(self, address: str) -> bool:
        """Check if an address can request tokens"""
        try:
            next_request_time = self.get_next_request_time(address)
            current_time = int(time.time())
            return current_time >= next_request_time
        except Exception as e:
            raise Exception(
                f"Failed to check token request eligibility: {str(e)}")

    def get_token_amount(self) -> int:
        """Get the amount of tokens that will be received from the faucet"""
        try:
            self.log("Calling tokenAmount() function")  # Add debug print
            return self.faucet_contract.functions.tokenAmount().call()
        except Exception as e:
            self.log(f"Error details: {str(e)}")  # Add debug print
            raise Exception(f"Failed to get token amount: {str(e)}")

    def get_next_request_time(self, address: str) -> int:
        """Get the next time tokens can be requested for an address"""
        try:
            return self.faucet_contract.functions.nextRequestTime(address).call()
        except Exception as e:
            raise Exception(f"Failed to get next request time: {str(e)}")
