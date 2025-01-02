import os
import traceback
from enum import Enum
from web3 import Web3
from .abi import usdc_abi, ostium_trading_abi, ostium_trading_storage_abi
from .utils import convert_to_scaled_integer, fromErrorCodeToMessage, get_tp_sl_prices, to_base_units
from eth_account.account import Account


class OpenOrderType(Enum):
    MARKET = 0
    LIMIT = 1
    STOP = 2


class Ostium:
    def __init__(self, w3: Web3, usdc_address: str, ostium_trading_storage_address: str, ostium_trading_address: str, private_key: str) -> None:
        if not private_key:
            raise ValueError(
                "Private key is required for Ostium initialization")

        self.web3 = w3
        self.private_key = private_key
        self.usdc_address = usdc_address
        self.ostium_trading_storage_address = ostium_trading_storage_address
        self.ostium_trading_address = ostium_trading_address

        # Create contract instances
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address, abi=usdc_abi)
        self.ostium_trading_storage_contract = self.web3.eth.contract(
            address=self.ostium_trading_storage_address, abi=ostium_trading_storage_abi)
        self.ostium_trading_contract = self.web3.eth.contract(
            address=self.ostium_trading_address, abi=ostium_trading_abi)

    def _get_account(self) -> Account:
        """Get account from stored private key"""
        return self.web3.eth.account.from_key(self.private_key)

    def get_block_number(self):
        return self.web3.eth.get_block('latest')['number']

    def get_nonce(self, address):
        return self.web3.eth.get_transaction_count(address)

    def perform_trade(self, trade_params, at_price):
        account = self._get_account()
        amount = to_base_units(trade_params['collateral'], decimals=6)
        self.__approve(account, amount)

        try:
            print("Final trade parameters being sent:", trade_params)
            tp_price, sl_price = get_tp_sl_prices(trade_params)

            trade = {
                'collateral': convert_to_scaled_integer(trade_params['collateral'], precision=5, scale=6),
                'openPrice': convert_to_scaled_integer(at_price),
                'tp': convert_to_scaled_integer(tp_price),
                'sl': convert_to_scaled_integer(sl_price),
                'trader': account.address,
                'leverage': to_base_units(trade_params['leverage'], decimals=2),
                'pairIndex': int(trade_params['asset_type']),
                'index': 0,
                'buy': trade_params['direction']
            }

            order_type = OpenOrderType.MARKET.value

            if 'order_type' in trade_params:
                if trade_params['order_type'] == 'LIMIT':
                    order_type = OpenOrderType.LIMIT.value
                elif trade_params['order_type'] == 'STOP':
                    order_type = OpenOrderType.STOP.value
                elif trade_params['order_type'] == 'MARKET':
                    pass
                else:
                    raise Exception('Invalid order type')

            trade_tx = self.ostium_trading_contract.functions.openTrade(
                trade, order_type, 9000).build_transaction({'from': account.address})
            trade_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=self.private_key)
            trade_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            print('Trade Receipt:', trade_receipt)
            return trade_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(e)
            print(
                f"An error ({str(e)}) occurred during the trading process - parsed as {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def cancel_limit_order(self, pairID, index):
        account = self._get_account()

        trade_tx = self.ostium_trading_contract.functions.cancelOpenLimitOrder(
            int(pairID), int(index)).build_transaction({'from': account.address})
        trade_tx['nonce'] = self.get_nonce(account.address)

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.raw_transaction)
        print('Cancel Limit Order TX Hash:', trade_tx_hash.hex())

        trade_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        print('Cancel Limit Order Receipt:', trade_receipt)
        return trade_receipt

    def close_trade(self, pairID, index):
        account = self._get_account()

        trade_tx = self.ostium_trading_contract.functions.closeTradeMarket(
            int(pairID), int(index)).build_transaction({'from': account.address})
        trade_tx['nonce'] = self.get_nonce(account.address)

        signed_tx = self.web3.eth.account.sign_transaction(
            trade_tx, private_key=self.private_key)
        trade_tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.raw_transaction)
        print('Trade TX Hash:', trade_tx_hash.hex())

        trade_receipt = self.web3.eth.wait_for_transaction_receipt(
            trade_tx_hash)
        print('Trade Receipt:', trade_receipt)
        return trade_receipt

    def add_collateral(self, pairID, index, collateral):
        try:
            account = self._get_account()
            amount = to_base_units(collateral, decimals=6)
            self.__approve(account, amount)

            add_collateral_tx = self.ostium_trading_contract.functions.topUpCollateral(
                int(pairID), int(index), amount).build_transaction({'from': account.address})
            add_collateral_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                add_collateral_tx, private_key=self.private_key)
            add_collateral_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Add Collateral TX Hash:', add_collateral_tx_hash.hex())

            add_collateral_receipt = self.web3.eth.wait_for_transaction_receipt(
                add_collateral_tx_hash)
            print('Add Collateral Receipt:', add_collateral_receipt)
            return add_collateral_receipt

        except Exception as e:
            print("An error occurred during the add collateral process:")
            traceback.print_exc()
            raise e

    def update_tp(self, pairID, index, tp):
        try:
            account = self._get_account()
            tp_value = to_base_units(tp, decimals=18)

            update_tp_tx = self.ostium_trading_contract.functions.updateTp(
                int(pairID), int(index), tp_value).build_transaction({'from': account.address})
            update_tp_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                update_tp_tx, private_key=self.private_key)
            update_tp_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Update TP TX Hash:', update_tp_tx_hash.hex())

        except Exception as e:
            print("An error occurred during the update tp process:")
            traceback.print_exc()
            raise e

    def update_sl(self, pairID, index, sl):
        try:
            account = self._get_account()
            sl_value = to_base_units(sl, decimals=18)

            update_sl_tx = self.ostium_trading_contract.functions.updateSl(
                int(pairID), int(index), sl_value).build_transaction({'from': account.address})
            update_sl_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                update_sl_tx, private_key=self.private_key)
            update_sl_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Update SL TX Hash:', update_sl_tx_hash.hex())

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(str(e))
            print(
                f"An error occurred during the update sl process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def __approve(self, account, collateral):
        allowance = self.usdc_contract.functions.allowance(
            account.address, self.ostium_trading_storage_address).call()

        if allowance < collateral:
            approve_tx = self.usdc_contract.functions.approve(
                self.ostium_trading_storage_address,
                self.web3.to_wei(1000000, 'mwei')
            ).build_transaction({'from': account.address})

            approve_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                approve_tx, private_key=self.private_key)
            approve_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Approval TX Hash:', approve_tx_hash.hex())

            approve_receipt = self.web3.eth.wait_for_transaction_receipt(
                approve_tx_hash)
            print('Approval Receipt:', approve_receipt)

    def withdraw(self, amount, receiving_address):
        try:
            account = self._get_account()
            amount_in_base_units = to_base_units(amount, decimals=6)

            if not self.web3.is_address(receiving_address):
                raise ValueError("Invalid Arbitrum address format")

            transfer_tx = self.usdc_contract.functions.transfer(
                receiving_address,
                amount_in_base_units
            ).build_transaction({'from': account.address})

            transfer_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                transfer_tx, private_key=self.private_key)
            transfer_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Transfer TX Hash:', transfer_tx_hash.hex())

            transfer_receipt = self.web3.eth.wait_for_transaction_receipt(
                transfer_tx_hash)
            print('Transfer Receipt:', transfer_receipt)
            return transfer_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(str(e))
            print(
                f"An error occurred during the transfer process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)

    def update_limit_order(self, pair_id, index, pvt_key, price=None, tp=None, sl=None):
        try:
            print('update_limit_order called with pair_id', pair_id, 'index',
                  index, 'pvt_key', pvt_key, 'price', price, 'tp', tp, 'sl', sl)
            account = self.web3.eth.account.from_key(pvt_key)

            # Get existing order details (tbd why read from storage)
            existing_order = self.ostium_trading_storage_contract.functions.getOpenLimitOrder(
                account.address,
                int(pair_id),
                int(index)
            ).call()

            print('existing_order', existing_order)
            # Use existing values if new values are not provided
            price_value = convert_to_scaled_integer(
                price) if price is not None else existing_order[1]  # openPrice
            tp_value = convert_to_scaled_integer(
                tp) if tp is not None else existing_order[2]    # tp
            sl_value = convert_to_scaled_integer(
                sl) if sl is not None else existing_order[3]    # sl

            print('calling updateOpenLimitOrder with price_value',
                  price_value, 'tp_value', tp_value, 'sl_value', sl_value)
            trade_tx = self.ostium_trading_contract.functions.updateOpenLimitOrder(
                int(pair_id),
                int(index),
                price_value,
                tp_value,
                sl_value
            ).build_transaction({'from': account.address})

            trade_tx['nonce'] = self.get_nonce(account.address)

            signed_tx = self.web3.eth.account.sign_transaction(
                trade_tx, private_key=account.key)
            trade_tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.raw_transaction)
            print('Update Limit Order TX Hash:', trade_tx_hash.hex())

            trade_receipt = self.web3.eth.wait_for_transaction_receipt(
                trade_tx_hash)
            print('Update Limit Order Receipt:', trade_receipt)
            return trade_receipt

        except Exception as e:
            reason_string, suggestion = fromErrorCodeToMessage(str(e))
            print(
                f"An error occurred during the update limit order process: {reason_string}")
            raise Exception(
                f'{reason_string}\n\n{suggestion}' if suggestion != None else reason_string)