from web3 import Web3

from ostium_python_sdk.ostium import Ostium

DELEGATE_KEY = '0x' + '01' * 32
TRADER = Web3.to_checksum_address('0x' + 'ab' * 20)


class _Captured(Exception):
    """Raised once the trade struct has been captured, to stop before any RPC."""


def _build_sdk(use_delegation):
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:1'))
    return Ostium(
        w3,
        '0x' + '11' * 20,
        '0x' + '22' * 20,
        '0x' + '33' * 20,
        private_key=DELEGATE_KEY,
        use_delegation=use_delegation,
    )


def _capture_trade(sdk, trade_params):
    captured = {}

    def fake_encode(fn_name, args):
        captured['trade'] = args[0]
        raise _Captured

    sdk.get_nonce = lambda _address: 0
    sdk._check_allowance = lambda _owner, _amount: 0
    sdk._Ostium__approve = lambda *a, **k: 0
    sdk._encode_trading_call = fake_encode
    sdk.ostium_trading_contract = None  # any RPC use would fail loudly

    try:
        sdk.perform_trade(trade_params, at_price=100)
    except Exception:
        # perform_trade wraps failures, so _Captured surfaces as a generic error; the
        # captured struct is the assertion target either way.
        pass
    return captured.get('trade')


def test_delegated_trade_names_the_trader_not_the_delegate():
    # The outer delegatedAction() names the trader, so the inner trade struct has to name
    # the same address; otherwise the contract reverts with DelegatedActionFailed().
    sdk = _build_sdk(use_delegation=True)
    trade = _capture_trade(sdk, {
        'collateral': 100,
        'leverage': 10,
        'asset_type': 0,
        'direction': True,
        'order_type': 'MARKET',
        'trader_address': TRADER,
    })

    assert trade is not None, 'trade struct was never built'
    assert trade['trader'] == TRADER
