from decimal import Decimal
from .constants import MAX_PROFIT_P, MAX_STOP_LOSS_P, PRECISION_16, PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, LIQ_THRESHOLD_P
from typing import Dict

#
# This is a copy-cat of formulae repo originally written in TypeScript
#

#
# GetStopLossPrice and GetTakeProfitPrice are consolidated into one function.
# bool is_tp is True if we want to calculate the take profit price, False if we want to calculate the stop loss price
#


def GetTakeProfitPrice(is_tp: bool, open_price: Decimal, leverage: Decimal, long: bool, profit_p: Decimal) -> Decimal:
    """
    Calculate the take profit / stop loss price based on desired profit percentage (aka: MAX_PROFIT_P=900 or MAX_STOP_LOSS_P=85).

    Args:
        open_price (Decimal): The opening price of the trade
        profit_p (Decimal): The desired profit percentage
        leverage (Decimal): The leverage amount
        long (bool): Whether this is a long position
        profit_p (Decimal): The desired profit percentage - 900% for Tp or 85% for SL

    Returns:
        str: The Tp / SL price as a string
    """

    open_price = Decimal(open_price)
    profit_p = Decimal(profit_p)
    leverage = Decimal(leverage)

    price_diff = (open_price * profit_p) / (leverage * Decimal('100'))

    if (is_tp):
        price = open_price + price_diff if long else open_price - price_diff
    else:
        price = open_price - price_diff if long else open_price + price_diff

    return Decimal(price if price > 0 else '0')


def CurrentTradeProfitP(open_price: str, current_price: str, long: bool, leverage: str) -> str:
    """
    Calculate the current trade profit percentage.

    Args:
        open_price (str): The opening price of the trade
        current_price (str): The current price
        long (bool): Whether this is a long position
        leverage (str): The leverage amount

    Returns:
        str: The profit percentage as a string
    """
    try:

        open_price_d = Decimal(open_price)
        current_price_d = Decimal(current_price)
        leverage_d = Decimal(leverage)

        if long:
            price_diff = current_price_d - open_price_d
        else:
            price_diff = open_price_d - current_price_d

        profit_p = (price_diff / open_price_d) * (leverage_d)

        if profit_p > MAX_PROFIT_P:
            return (MAX_PROFIT_P)
        else:
            return (profit_p)
    except Exception as e:
        return str(e)

# tbd - used by SDK


def GetTradeLiquidationPrice(
    open_price: str,
    long: bool,
    collateral: str,
    leverage: str,
    rollover_fee: str,
    funding_fee: str
) -> Decimal:
    try:
        open_price = Decimal(open_price)
        collateral = Decimal(collateral)
        rollover_fee = Decimal(rollover_fee)
        funding_fee = Decimal(funding_fee)
        leverage = Decimal(leverage)

        liq_price_distance = (
            open_price *
            (collateral * Decimal(LIQ_THRESHOLD_P) / Decimal(100) - rollover_fee - funding_fee) /
            collateral /
            leverage
        )

        liq_price = open_price - liq_price_distance if long else open_price + liq_price_distance
        liq_price = liq_price if liq_price > 0 else 0
        return liq_price

    except Exception as error:
        raise Exception(f"Unable to compute Liquidation Price: {error}")


def GetCurrentRolloverFee(
    acc_rollover: str,
    last_rollover_block: str,
    rollover_fee_per_block: str,
    latest_block: str
) -> Decimal:
    try:
        acc_rollover = Decimal(acc_rollover)
        last_rollover_block = Decimal(last_rollover_block)
        rollover_fee_per_block = Decimal(rollover_fee_per_block)
        latest_block = Decimal(latest_block)
        current_fee = acc_rollover + \
            (latest_block - last_rollover_block) * rollover_fee_per_block
        return current_fee

    except Exception as error:
        raise Exception(f"Unable to compute Current Rollover Fee: {error}")


def GetTradeRolloverFee(
    trade_rollover: str,
    current_rollover: str,
    collateral: str,
    leverage: str
) -> Decimal:
    try:
        current_rollover = Decimal(current_rollover)
        trade_rollover = Decimal(trade_rollover)
        collateral = Decimal(collateral)
        leverage = Decimal(leverage)

        rollover_fee = (
            (current_rollover - trade_rollover) *
            collateral *
            leverage /
            PRECISION_18 /
            PRECISION_2
        )
        return rollover_fee

    except Exception as error:
        raise Exception(f"Unable to compute Trade Rollover Fee: {error}")

# Gets the funding fee (abs) for an open trade (up to this block, aka based on current_funding up till this block)


def GetTradeFundingFee(
    trade_funding: str,
    current_funding: str,
    collateral: str,
    leverage: str
) -> Decimal:
    try:
        current_funding = Decimal(current_funding)
        trade_funding = Decimal(trade_funding)
        collateral = Decimal(collateral)
        leverage = Decimal(leverage)

        funding_fee = (
            (current_funding - trade_funding) *
            collateral *
            leverage /
            PRECISION_18 /
            PRECISION_2
        )
        return funding_fee

    except Exception as error:
        raise Exception(f"Unable to compute Trade Funding Fee: {error}")


def GetFundingRate(
    acc_funding_long: str,
    acc_funding_short: str,
    last_funding_rate: str,
    last_funding_velocity: str,
    max_funding_fee_per_block: str,
    last_funding_block: str,
    latest_block: str,
    long_oi: str,
    short_oi: str
) -> dict:
    try:
        acc_funding_long = Decimal(acc_funding_long)
        acc_funding_short = Decimal(acc_funding_short)
        last_funding_rate = Decimal(last_funding_rate)
        last_funding_velocity = Decimal(last_funding_velocity)
        max_funding_fee_per_block = Decimal(max_funding_fee_per_block)
        last_funding_block = Decimal(last_funding_block)
        latest_block = Decimal(latest_block)
        long_oi = Decimal(long_oi)
        short_oi = Decimal(short_oi)

        block_diff = latest_block - last_funding_block

        # Calculate skew
        total_oi = long_oi + short_oi
        skew = Decimal('0')
        if total_oi > 0:
            skew = (long_oi - short_oi) / total_oi

        # Calculate funding rate
        funding_rate = last_funding_rate + last_funding_velocity * block_diff

        # Cap funding rate
        if funding_rate > max_funding_fee_per_block:
            funding_rate = max_funding_fee_per_block
        elif funding_rate < -max_funding_fee_per_block:
            funding_rate = -max_funding_fee_per_block

        # Calculate accumulated funding
        funding_long = acc_funding_long + funding_rate * block_diff
        funding_short = acc_funding_short - funding_rate * block_diff

        return {
            'accFundingLong': str(funding_long),
            'accFundingShort': str(funding_short),
            'skew': str(skew)
        }

    except Exception as error:
        raise Exception(f"Unable to compute Funding Rate: {error}")


def GetPriceImpact(
    mid_price: str,
    bid_price: str,
    ask_price: str,
    is_open: bool,
    is_long: bool,  # aka is_long
) -> dict:
    try:
        mid_price = Decimal(mid_price)
        bid_price = Decimal(bid_price)
        ask_price = Decimal(ask_price)

        if (mid_price == 0):
            return {
                'priceImpactP': str(0),
                'priceAfterImpact': str(0)
            }

        above_spot = is_open == is_long
        used_price = ask_price if above_spot else bid_price
        priceImpactP = 100 * (abs(mid_price - used_price) / mid_price)

        return {
            'priceImpactP': str(priceImpactP),
            'priceAfterImpact': str(used_price)
        }

    except Exception as error:
        raise Exception(f"Unable to compute Price Impact: {error}")


# calculates the gross (without fees) profit (abs) of an open trade
def CurrentTradeProfitRaw(
    open_price: str,
    current_price: str,
    is_buy: bool,
    leverage: str,
    collateral: str
) -> str:
    try:
        open_price = Decimal(open_price)
        current_price = Decimal(current_price)
        leverage = Decimal(leverage)
        collateral = Decimal(collateral)

        # Calculate price difference based on position direction
        if is_buy:
            price_diff = current_price - open_price
        else:
            price_diff = open_price - current_price

        # Calculate profit
        profit = (price_diff * collateral * leverage) / \
            (open_price * PRECISION_2)

        return str(profit)

    except Exception as error:
        raise Exception(f"Unable to compute Current Trade Profit Raw: {error}")

# calculates the net profit (after fees) of an open trade (abs)


def CurrentTotalProfitRaw(
    open_price: str,
    current_price: str,
    is_buy: bool,
    leverage: str,
    collateral: str,
    rollover_fee: str,
    funding_fee: str
) -> str:
    try:
        # Get trade profit
        trade_profit = Decimal(CurrentTradeProfitRaw(
            open_price,
            current_price,
            is_buy,
            leverage,
            collateral
        ))

        # Subtract fees
        total_profit = trade_profit - \
            Decimal(rollover_fee) - Decimal(funding_fee)

        return str(total_profit)

    except Exception as error:
        raise Exception(f"Unable to compute Current Total Profit Raw: {error}")


# TBD- used by sdk. calculates the net profit percentage of an open trade
# What's the diff between this and CurrentTradeProfitP?
def CurrentTotalProfitP(total_profit: str, collateral: str) -> str:
    try:
        total_profit = Decimal(total_profit)
        collateral = Decimal(collateral)

        # Calculate profit percentage
        profit_percentage = (total_profit * PRECISION_6) / collateral

        # Cap at MAX_PROFIT_P if needed
        if profit_percentage > MAX_PROFIT_P:
            return str(MAX_PROFIT_P)

        return str(profit_percentage)

    except Exception as error:
        raise Exception(
            f"Unable to compute Current Total Profit Percentage: {error}")

# given desired TP percentage, like 35, 50, 75, 100, 500 and 900 which is max: gives you the TP price


def get_target_funding_rate(
    normalized_oi_delta: Decimal,
    hill_inflection_point: Decimal,
    max_fr: Decimal,
    hill_pos_scale: Decimal,
    hill_neg_scale: Decimal,
) -> Decimal:
    a = Decimal('184')
    k = Decimal('16')

    x = a * normalized_oi_delta / PRECISION_2
    x2 = x * x * PRECISION_6  # convert to PRECISION_18
    hill = x2 * PRECISION_18 / (k * PRECISION_16 + x2)

    if normalized_oi_delta >= 0:
        target_fr = hill_pos_scale * hill / PRECISION_2 + hill_inflection_point
    else:
        target_fr = hill_neg_scale * \
            Decimal('-1') * hill / PRECISION_2 + hill_inflection_point

    if target_fr > PRECISION_18:
        target_fr = PRECISION_18
    elif target_fr < PRECISION_18 * Decimal('-1'):
        target_fr = PRECISION_18 * Decimal('-1')

    return target_fr * max_fr / PRECISION_18


def exponential_approximation(x: Decimal) -> Decimal:
    approx_threshold = Decimal('793231258909201900')

    if abs(x) < approx_threshold:
        three_with_precision = PRECISION_18 * 3
        numerator = x + three_with_precision
        numerator = numerator * numerator / PRECISION_18 + three_with_precision
        denominator = x - three_with_precision
        denominator = denominator * denominator / PRECISION_18 + three_with_precision

        return numerator * PRECISION_18 / denominator
    else:
        k = [1648721, 1284025, 1133148, 1064494, 1031743,
             1015748, 1007843, 1003915, 1001955, 1000977]
        integer_part = abs(x) // PRECISION_18
        decimal_part = abs(x) - (integer_part * PRECISION_18)

        approx = PRECISION_6

        for ki in k:
            decimal_part = decimal_part * 2
            if decimal_part >= PRECISION_18:
                approx = approx * Decimal(str(ki)) / PRECISION_6
                decimal_part = decimal_part - PRECISION_18
            if decimal_part == 0:
                break

        return (PRECISION_18 * PRECISION_18 /
                (Decimal('2') ** integer_part *
                 (approx / Decimal('1000') * Decimal('1e15'))) /
                Decimal('1e15') * Decimal('1e15'))


def get_funding_rate(
    acc_per_oi_long: str,
    acc_per_oi_short: str,
    last_funding_rate: str,
    max_funding_fee_per_block: str,
    last_update_block: str,
    latest_block: str,
    oi_long: str,
    oi_short: str,
    oi_cap: str,
    hill_inflection_point: str,
    hill_pos_scale: str,
    hill_neg_scale: str,
    spring_factor: str,
    s_factor_up_scale_p: str,
    s_factor_down_scale_p: str,
    verbose: bool = False
) -> Dict[str, str]:
    # Convert string inputs to Decimal
    acc_per_oi_long_dec = Decimal(acc_per_oi_long)
    acc_per_oi_short_dec = Decimal(acc_per_oi_short)
    last_funding_rate_dec = Decimal(last_funding_rate)
    max_funding_fee_per_block_dec = Decimal(max_funding_fee_per_block)
    last_update_block_dec = Decimal(last_update_block)
    latest_block_dec = Decimal(latest_block)
    oi_long_dec = Decimal(oi_long)
    oi_short_dec = Decimal(oi_short)
    oi_cap_dec = Decimal(oi_cap)
    spring_factor_dec = Decimal(spring_factor)
    s_factor_up_scale_p_dec = Decimal(s_factor_up_scale_p)
    s_factor_down_scale_p_dec = Decimal(s_factor_down_scale_p)
    hill_inflection_point_dec = Decimal(hill_inflection_point)
    hill_pos_scale_dec = Decimal(hill_pos_scale)
    hill_neg_scale_dec = Decimal(hill_neg_scale)

    # Calculate open interest max
    open_interest_max = max(oi_long_dec, oi_short_dec)
    denominator = max(oi_cap_dec, open_interest_max)
    oi_delta = (oi_long_dec - oi_short_dec) * PRECISION_6 / denominator

    if verbose:
        print(f"open_interest_max: {open_interest_max}")
        print(f"denominator: {denominator}")

        print(
            f"oi_long_dec: {oi_long_dec} (make sure this is in notional aka usd)")
        print(
            f"oi_short_dec: {oi_short_dec} (make sure this is in notional aka usd)")
        print(f"oi_cap_dec: {oi_cap_dec}")
        print(f"oi_delta: {oi_delta}")

    # Get target funding rate
    target_fr = get_target_funding_rate(
        oi_delta,
        hill_inflection_point_dec,
        max_funding_fee_per_block_dec,
        hill_pos_scale_dec,
        hill_neg_scale_dec,
    )

    if verbose:
        print(f"target_fr: {target_fr}")

    # Calculate spring factor
    s_factor = Decimal('0')
    if last_funding_rate_dec * target_fr >= 0:
        if abs(target_fr) > abs(last_funding_rate_dec):
            s_factor = spring_factor_dec
        else:
            s_factor = s_factor_down_scale_p_dec * \
                spring_factor_dec / Decimal('10000')
    else:
        s_factor = s_factor_up_scale_p_dec * \
            spring_factor_dec / Decimal('10000')

    # Calculate blocks to charge and exponential
    num_blocks_to_charge = latest_block_dec - last_update_block_dec
    exp = exponential_approximation(
        s_factor * num_blocks_to_charge * Decimal('-1'))

    # Calculate funding rates
    acc_funding_rate = (target_fr * num_blocks_to_charge +
                        (PRECISION_18 - exp) * (last_funding_rate_dec - target_fr) / s_factor)
    fr = target_fr + (last_funding_rate_dec - target_fr) * exp / PRECISION_18

    # Update accumulations
    if acc_funding_rate > 0:
        if oi_long_dec > 0:
            acc_per_oi_long_dec += acc_funding_rate
            acc_per_oi_short_dec -= (acc_funding_rate * oi_long_dec / oi_short_dec
                                     if oi_short_dec > 0 else Decimal('0'))
    else:
        if oi_short_dec > 0:
            acc_per_oi_short_dec -= acc_funding_rate
            acc_per_oi_long_dec += (acc_funding_rate * oi_short_dec / oi_long_dec
                                    if oi_long_dec > 0 else Decimal('0'))

    return {
        'accFundingLong': str(acc_per_oi_long_dec),
        'accFundingShort': str(acc_per_oi_short_dec),
        'latestFundingRate': str(fr),
        'targetFr': str(target_fr)
    }
