from datetime import datetime
from decimal import Decimal
from web3 import Web3
from ast import literal_eval

from .constants import MAX_PROFIT_P, MAX_STOP_LOSS_P


def format_with_precision(number, precision):
    """
    Formats a number to a specified decimal precision, removing trailing zeros.

    Args:
        number: The number to be formatted (can be int, float, or numeric string)
        precision (int): Maximum number of decimal places to round to

    Returns:
        str: Formatted number with up to specified decimal precision, trailing zeros removed
    """
    try:
        if callable(number):
            raise TypeError("Input cannot be a function")

        float_number = float(number)
        precision = int(precision)

        # Format with specified precision first
        formatted = "{:.{}f}".format(round(float_number, precision), precision)
        # Remove trailing zeros after decimal point, but keep at least one digit before decimal
        formatted = formatted.rstrip('0').rstrip(
            '.') if '.' in formatted else formatted

        return float(formatted)

    except (TypeError, ValueError) as e:
        raise TypeError(f"Invalid input: {e}")


def calculate_fee_per_hours(cur_funding_rate, hours=24, round_to_precision=5):
    period = hours * (10 / 3) * 60 * 60 * 100
    rate = Decimal(cur_funding_rate) * Decimal(period)
    return round(rate, round_to_precision)


def get_tp_sl_prices(trade_params):
    tp_price = 0
    sl_price = 0

    if 'tp' in trade_params and str(trade_params['tp']) != '0':
        tp_price = float(trade_params['tp'])

    if 'sl' in trade_params and str(trade_params['sl']) != '0':
        sl_price = float(trade_params['sl'])

    return tp_price, sl_price


def get_order_details(order_details):
    open_price = Web3.from_wei(int(order_details['openPrice']), 'ether')

    limit_order_created_time = datetime.fromtimestamp(
        int(order_details['initiatedAt']))

    leverage = Web3.from_wei(int(order_details['leverage']), 'kwei')*10
    collateral = Web3.from_wei(int(order_details['collateral']), 'mwei')
    is_long = order_details['isBuy']
    limit_type = order_details['limitType']
    pairIndex, index = parse_limit_order_id(order_details['id'])

    sl_price = Web3.from_wei(int(order_details['stopLossPrice']), 'ether')
    tp_price = Web3.from_wei(int(order_details['takeProfitPrice']), 'ether')

    atLeastTradeNotional = 0
    if open_price:
        atLeastTradeNotional = collateral*leverage/open_price

    return limit_type, sl_price, tp_price, open_price, leverage, limit_order_created_time, collateral, pairIndex, index, is_long, atLeastTradeNotional


def get_trade_details(trade_details):
    open_price = Web3.from_wei(int(trade_details['openPrice']), 'ether')
    sl_price = Web3.from_wei(int(trade_details['stopLossPrice']), 'ether')
    tp_price = Web3.from_wei(int(trade_details['takeProfitPrice']), 'ether')
    tradeNotional = Web3.from_wei(int(trade_details['tradeNotional']), 'ether')
    trans_time = datetime.fromtimestamp(int(trade_details['timestamp']))
    leverage = Web3.from_wei(int(trade_details['leverage']), 'kwei')*10
    collateral = Web3.from_wei(int(trade_details['collateral']), 'mwei')
    is_long = trade_details['isBuy']
    pairIndex = trade_details['pair']['id']
    index = trade_details['index']

    return open_price, round(tradeNotional, 18), trans_time, leverage, collateral, pairIndex, index, is_long, sl_price, tp_price


def parse_limit_order_id(limit_order_id):
    # 0x3750a14869d419f1069cbf7cbe47a89b2dc1d4c4_0_0
    trader, pairIndex, index = limit_order_id.split('_')

    return pairIndex, index


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def fromErrorCodeToMessage(error_code, verbose=False):
    if verbose:
        print('----->fromErrorCodeToMessage(error_code) called with', str(error_code))

    # Create reverse mapping of hash -> error name
    error_map = {
        "80a71fc5": "AboveMaxAllowedCollateral()",
        "f77a8069": "AlreadyMarketClosed(address,uint16,uint8)",
        "eca695e1": "BelowMinLevPos()",
        "5be5878a": "DelegatedActionFailed()",
        "46c4ede2": "ExposureLimits()",
        "4f285592": "IsContract(address)",
        "084986e7": "IsDone()",
        "1309a563": "IsPaused()",
        "5c12ea62": "MaxPendingMarketOrdersReached(address)",
        "e6f47fab": "MaxTradesPerPairReached(address,uint16)",
        "2a917859": "NoDelegate(address)",
        "a35ee470": "NoLimitFound(address,uint16,uint8)",
        "17e08e97": "NoTradeFound(address,uint16,uint8)",
        "efa9e5be": "NoTradeToTimeoutFound(uint256)",
        "c7fe4d00": "NotCloseMarketTimeoutOrder(uint256)",
        "502b946d": "NotDelegate(address,address)",
        "093650d5": "NotGov(address)",
        "1add0915": "NotOpenMarketTimeoutOrder(uint256)",
        "432b6c83": "NotTradesUpKeep(address)",
        "df17e316": "NotWhitelisted(address)",
        "5ac89f62": "NotYourOrder(uint256,address)",
        "f3d0b126": "NullAddr()",
        "cb87b762": "PairNotListed(uint16)",
        "dd9397bb": "TriggerPending(address,uint16,uint8)",
        "3e0b1869": "WaitTimeout(uint256)",
        "35fe85c5": "WrongLeverage(uint32)",
        "5863f789": "WrongParams()",
        "083fbd78": "WrongSL()",
        "a41bb918": "WrongTP()"
    }

    # Search for any of the known error hashes within the error_code string
    for hash_code, error_message in error_map.items():
        if hash_code in str(error_code):
            ret = error_message
            if verbose:
                print('----->fromErrorCodeToMessage(error_code) returns', ret)
            return str(ret), None

    # If we couldn't find the error in error_map, try to parse the error
    try:
        # Convert string representation to dictionary if needed
        error_dict = error_code if isinstance(
            error_code, dict) else literal_eval(str(error_code))
        if isinstance(error_dict, dict) and 'message' in error_dict:
            if 'insufficient funds for gas * price + value' in error_dict['message']:
                suggestion = 'Please top up your account with more ETH'
                return error_dict["message"], suggestion
            else:
                return error_dict['message'], None
    except (ValueError, SyntaxError):
        pass

    if 'execution reverted: ERC20: transfer amount exceeds balance' in str(error_code):
        suggestion = 'Please top up your account with more USDC'
        return 'execution reverted: ERC20: transfer amount exceeds balance', suggestion

    ret = 'Unknown error (missing in error_map?)'
    if verbose:
        print('----->Did\'t find the error, so returning - fromErrorCodeToMessage(error_code) returns', ret)
    return str(ret), None


def to_base_units(amount: float, decimals: int = 6) -> int:
    """
    Converts a decimal number to base units by multiplying by 10^decimals

    Args:
        amount (float): The amount to convert (e.g., 1.23)
        decimals (int, optional): Number of decimal places. Defaults to 6 for USDC.

    Returns:
        int: The amount in base units (e.g., 1.23 -> 1230000 for decimals=6)
    """
    return int(float(amount) * 10**decimals)


def convert_to_scaled_integer(value, precision=5, scale=18):
    # First scale to the precision we want to preserve (e.g., 5 decimal places)
    precise_value = round(Decimal(value) * (10 ** precision))
    # Then pad with zeros to reach 18 decimals
    scaled_value = precise_value * (10 ** (scale - precision))
    return scaled_value


def is_valid_decimal(s, must_be_positive=True):
    try:
        float(s)
    except ValueError:
        return False
    else:
        if must_be_positive and float(s) < 0:
            return False
        return True


def convert_decimals(obj):
    if isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, Decimal):
        return str(obj)  # or float(obj) if you prefer
    return obj

# timestamp is a string in seconds as returned from graph
