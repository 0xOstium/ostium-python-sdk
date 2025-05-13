from datetime import datetime
from decimal import Decimal
import time
from ostium_python_sdk.abi.usdc_abi import usdc_abi
from web3 import Web3

REFRESH_BALANCE_SECONDS_INTERVAL = 60 * 5


class Balance:
    def __init__(self, w3: Web3, usdc_address: str, verbose=False) -> None:
        self.web3 = w3
        self.usdc_address = usdc_address
        self.verbose = verbose
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address, abi=usdc_abi)
        # Format: {address: {'ether': value, 'usdc': value, 'last_refresh': timestamp}}
        self.balances = {}

    def log(self, message):
        if self.verbose:
            print(message)

    def get_balance(self, address, refresh=False):
        if address not in self.balances:
            self.balances[address] = {'ether': None,
                                      'usdc': None, 'last_refresh': None}

        balance_info = self.balances[address]
        if balance_info['last_refresh'] is None:
            too_old = True
        else:
            too_old = time.time() - \
                balance_info['last_refresh'] > REFRESH_BALANCE_SECONDS_INTERVAL

        if (refresh or too_old or balance_info['ether'] is None or balance_info['usdc'] is None):
            self.read_balances(address)

        return self.balances[address]['ether'], self.balances[address]['usdc']

    def read_balances(self, address):
        start_time = time.time()
        self.balances[address] = {
            'ether': Decimal(self.get_ether_balance(address)),
            'usdc': Decimal(self.get_usdc_balance(address)),
            'last_refresh': start_time
        }
        end_time = time.time()

    def get_usdc_balance(self, address):
        balance = self.usdc_contract.functions.balanceOf(address).call()
        balance = Web3.to_wei(balance, 'szabo')
        balance = Web3.from_wei(balance, 'ether')
        return balance

    def get_ether_balance(self, address):
        ret = Web3.from_wei(self.web3.eth.get_balance(address), 'ether')
        return ret
