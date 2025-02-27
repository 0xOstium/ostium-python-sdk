from decimal import Decimal
from .formulae import (PRECISION_18, PRECISION_2, PRECISION_6, GetCurrentRolloverFee,
                       GetTradeFundingFee, GetTradeLiquidationPrice, GetTradeRolloverFee,
                       GetFundingRate, GetPriceImpact, CurrentTradeProfitRaw,
                       CurrentTotalProfitRaw, CurrentTotalProfitP)
from typing import Dict, Union

# TBD - Not used by SDK


def get_liq_price(trade_details, pair_info, block_number):
    current_funding_fee = GetTradeFundingFee(trade_details['funding'], pair_info['accFundingLong'] if trade_details['isBuy']
                                             else pair_info['accFundingShort'], trade_details['collateral'], trade_details['leverage'])

    current_rollover_fee = GetCurrentRolloverFee(
        pair_info['accRollover'], pair_info['lastRolloverBlock'], pair_info['rolloverFeePerBlock'], block_number)

    trade_rollover_fee = GetTradeRolloverFee(
        trade_details['rollover'], current_rollover_fee, trade_details['collateral'], trade_details['leverage'])

    liq_price = GetTradeLiquidationPrice(trade_details['openPrice'], trade_details['isBuy'], Decimal(trade_details['collateral']) / PRECISION_6, Decimal(
        trade_details['leverage']) / PRECISION_2, Decimal(trade_rollover_fee)/PRECISION_6, Decimal(current_funding_fee) / PRECISION_6)

    return liq_price / PRECISION_18

# TBD - used by SDK


def get_funding_fee_long_short(pair_info, block_number):
    funding_rate_raw = GetFundingRate(
        pair_info['accFundingLong'],
        pair_info['accFundingShort'],
        pair_info['lastFundingRate'],
        pair_info['lastFundingVelocity'],
        pair_info['maxFundingFeePerBlock'],
        pair_info['lastFundingBlock'],
        str(block_number),
        pair_info['longOI'],
        pair_info['shortOI']
    )

    # Convert latest funding rate to decimal
    latest_rate = Decimal(
        funding_rate_raw['latestFundingRate']) / PRECISION_18  # Fixed key name

    # Convert OI values to decimal
    long_oi = Decimal(pair_info['longOI']) / PRECISION_18
    short_oi = Decimal(pair_info['shortOI']) / PRECISION_18

    if funding_rate_raw['longsPay']:
        # If longs pay, they get negative rate
        long_rate = -latest_rate
        # Shorts receive proportional to OI ratio
        short_rate = latest_rate * long_oi / \
            short_oi if short_oi > 0 else Decimal('0')
    else:
        # If shorts pay, they get negative rate
        short_rate = -latest_rate
        # Longs receive proportional to OI ratio
        long_rate = latest_rate * short_oi / \
            long_oi if long_oi > 0 else Decimal('0')

    return float(long_rate), float(short_rate)

# TBD - used by SDK
# Gets an open trade metrics: such as the open pnl, rollover, funding, liquidation price, price impact, etc.


def get_trade_metrics(trade_details, price_data, block_number, verbose=False):
    """
    Calculate PNL and related metrics for a trade.
    """
    if not trade_details or not price_data or not block_number:
        return {
            'pnl': 0,
            # 'pnl_raw': '0',
            'pnl_percent': 0,
            'rollover': 0,
            'funding': 0,
            'total_profit': 0,
            'net_pnl': 0,
            'net_value': 0,
            'liquidation_price': 0
        }

    pair_info = trade_details['pair']
    # Calculate current rollover fee
    current_rollover_raw = GetCurrentRolloverFee(
        pair_info['accRollover'],
        pair_info['lastRolloverBlock'],
        pair_info['rolloverFeePerBlock'],
        str(block_number)
    )

    if verbose:
        print(f"Current rollover fee: {current_rollover_raw}")

    # Calculate rollover for this trade
    rollover_raw = GetTradeRolloverFee(
        trade_details['rollover'],
        current_rollover_raw,
        trade_details['collateral'],
        trade_details['leverage']
    )

    if verbose:
        print(f"Rollover fee: {rollover_raw}")

    # Get funding rate
    funding_rate_raw = GetFundingRate(
        pair_info['accFundingLong'],
        pair_info['accFundingShort'],
        pair_info['lastFundingRate'],
        pair_info['lastFundingVelocity'],
        pair_info['maxFundingFeePerBlock'],
        pair_info['lastFundingBlock'],
        str(block_number),
        pair_info['longOI'],
        pair_info['shortOI']
    )

    if verbose:
        print(f"Funding rate: {funding_rate_raw}")

    # Calculate funding fee
    funding_raw = GetTradeFundingFee(
        trade_details['funding'],
        funding_rate_raw['accFundingLong'] if trade_details['isBuy'] else funding_rate_raw['accFundingShort'],
        trade_details['collateral'],
        trade_details['leverage']
    )

    if verbose:
        print(f"Funding fee: {funding_raw}")

    # Calculate liquidation price
    liquidation_price = GetTradeLiquidationPrice(
        trade_details['openPrice'],
        trade_details['isBuy'],
        trade_details['collateral'],
        trade_details['leverage'],
        str(rollover_raw),
        str(funding_raw)
    )
    liquidation_price = Decimal(liquidation_price) / PRECISION_18

    if verbose:
        print(
            f"Liquidation price: {liquidation_price} with rollover {rollover_raw} and funding {funding_raw}")

    # Calculate price impact
    is_open = False  # Get the price assuming a close

    price_impact_raw = GetPriceImpact(
        str(int(Decimal(str(price_data['mid'])) * PRECISION_18)),
        str(int(Decimal(str(price_data['bid'])) * PRECISION_18)),
        str(int(Decimal(str(price_data['ask'])) * PRECISION_18)),
        is_open,
        trade_details['isBuy']
    )
    price_after_impact = price_impact_raw['priceAfterImpact']

    # Calculate PNL (abs)
    pnl_raw = CurrentTradeProfitRaw(
        trade_details['openPrice'],
        price_after_impact,
        trade_details['isBuy'],
        trade_details['leverage'],
        trade_details['collateral']
    )

    # Calculate total profit (abs)
    total_profit_raw = CurrentTotalProfitRaw(
        trade_details['openPrice'],
        price_after_impact,
        trade_details['isBuy'],
        trade_details['leverage'],
        trade_details['collateral'],
        str(rollover_raw),
        str(funding_raw)
    )

    # Calculate PNL percentage
    pnl_percent_raw = CurrentTotalProfitP(
        str(total_profit_raw), trade_details['collateral'])

    # Convert values to proper decimals
    pnl = Decimal(pnl_raw) / PRECISION_6
    pnl_percent = Decimal(pnl_percent_raw) / PRECISION_6
    net_pnl = Decimal(total_profit_raw) / PRECISION_6
    total_profit = Decimal(total_profit_raw) / PRECISION_6
    funding = Decimal(funding_raw) / PRECISION_6
    rollover = Decimal(rollover_raw) / PRECISION_6
    net_value = net_pnl + (Decimal(trade_details['collateral']) / PRECISION_6)
    price_impact = Decimal(price_after_impact) / PRECISION_18

    return {
        'pnl': float(pnl),
        # 'pnl_raw': str(pnl_raw),
        'pnl_percent': float(pnl_percent),
        'rollover': float(rollover),
        'funding': float(funding),
        # 'funding_raw': str(funding_raw),
        # 'rollover_raw': str(rollover_raw),
        'total_profit': float(total_profit),
        # 'total_profit_percent': float(total_profit_percent),
        'net_pnl': float(net_pnl),
        'net_value': float(net_value),
        'liquidation_price': float(liquidation_price),
        'price_impact': float(price_impact)
    }


def ceil_div(a: int, b: int) -> int:
    """Implements ceiling division for integers"""
    return -((-a) // b)


def GetFundingRate(
    acc_per_oi_long: str,
    acc_per_oi_short: str,
    last_funding_rate: str,
    last_velocity: str,
    max_funding_fee_per_block: str,
    last_update_block: str,
    latest_block: str,
    oi_long: str,
    oi_short: str,
) -> Dict[str, Union[str, bool]]:
    # Convert string inputs to integers (similar to BigNumber.from)
    acc_per_oi_long_bn = int(acc_per_oi_long)
    acc_per_oi_short_bn = int(acc_per_oi_short)
    last_funding_rate_bn = int(last_funding_rate)
    last_velocity_bn = int(last_velocity)
    max_funding_fee_per_block_bn = int(max_funding_fee_per_block)
    last_update_block_bn = int(last_update_block)
    latest_block_bn = int(latest_block)
    oi_long_bn = int(oi_long)
    oi_short_bn = int(oi_short)

    value_long = acc_per_oi_long_bn
    value_short = acc_per_oi_short_bn
    fr = 0

    abs_last_funding_rate = abs(last_funding_rate_bn)
    abs_last_velocity = abs(last_velocity_bn)

    num_blocks = latest_block_bn - last_update_block_bn
    new_funding_rate = last_funding_rate_bn + (last_velocity_bn * num_blocks)
    abs_new_funding_rate = abs(new_funding_rate)

    num_blocks_to_charge = num_blocks

    accumulated_funding_rate_change = 0
    longs_pay = False
    funding_rate_to_use = 0

    if abs_new_funding_rate > max_funding_fee_per_block_bn:
        num_blocks_to_limit = (
            max_funding_fee_per_block_bn - abs_last_funding_rate) // abs_last_velocity

        if (new_funding_rate * last_funding_rate_bn) < 0:
            num_blocks_to_charge = num_blocks_to_charge + \
                (2 * last_funding_rate_bn) // last_velocity_bn

        accumulated_funding_rate_change = (
            abs_last_funding_rate +
            (ceil_div(num_blocks_to_limit, 2) * abs_last_velocity)
        ) * num_blocks_to_limit + (
            (num_blocks_to_charge - num_blocks_to_limit) *
            max_funding_fee_per_block_bn
        )

        if new_funding_rate > 0:
            longs_pay = True
            fr = max_funding_fee_per_block_bn
        else:
            longs_pay = False
            fr = -max_funding_fee_per_block_bn
    else:
        funding_rate_to_use = abs_new_funding_rate if abs_new_funding_rate > abs_last_funding_rate else abs_last_funding_rate

        if (last_funding_rate_bn * new_funding_rate) < 0:
            num_blocks_to_charge = num_blocks_to_charge - \
                (2 * funding_rate_to_use) // abs_last_velocity

        longs_pay = (new_funding_rate + last_funding_rate_bn) >= 0

        accumulated_funding_rate_change = (
            funding_rate_to_use +
            (ceil_div(num_blocks_to_charge, 2) * abs_last_velocity)
        ) * num_blocks_to_charge

        fr = new_funding_rate

    if longs_pay:
        value_long = value_long + \
            (accumulated_funding_rate_change if oi_long_bn > 0 else 0)

        if oi_short_bn != 0:
            value_short = value_short - \
                (accumulated_funding_rate_change * oi_long_bn) // oi_short_bn
    else:
        value_short = value_short + \
            (accumulated_funding_rate_change if oi_short_bn > 0 else 0)

        if oi_long_bn != 0:
            value_long = value_long - \
                (accumulated_funding_rate_change * oi_short_bn) // oi_long_bn

    return {
        'accFundingLong': str(value_long),
        'accFundingShort': str(value_short),
        'latestFundingRate': str(fr),
        'longsPay': longs_pay,
    }
