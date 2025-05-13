from decimal import Decimal, getcontext, ROUND_DOWN
from .constants import MAX_PROFIT_P, MIN_LOSS_P, MAX_STOP_LOSS_P, PRECISION_16, PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, LIQ_THRESHOLD_P
from typing import Dict
from .scscript.funding import getPendingAccFundingFees, getTargetFundingRate

quantization_6 = Decimal('0.000001')
quantization_18 = Decimal('0.000000000000000001')

# v2 (formulae v1.3.3)


def GetTakeProfitPrice(open_price: Decimal, profit_p: Decimal, leverage: Decimal, is_long: bool) -> Decimal:
    open_price = Decimal(open_price)
    profit_p = Decimal(profit_p)
    leverage = Decimal(leverage)

    price_diff = (open_price * profit_p) / (leverage * Decimal('100'))

    if (is_long):
        tp_price = open_price + price_diff
    else:
        tp_price = open_price - price_diff

    return Decimal(tp_price if tp_price > 0 else '0')

# v2 (formulae v1.3.3)


def GetStopLossPrice(open_price: Decimal, loss_p: Decimal, leverage: Decimal, is_long: bool) -> Decimal:
    open_price = Decimal(open_price)
    loss_p = Decimal(loss_p)
    leverage = Decimal(leverage)

    # price_diff matches your existing TP logic style, except using 'loss_p'
    price_diff = (open_price * loss_p) / (leverage * Decimal('100'))

    sl_price = open_price - price_diff if is_long else open_price + price_diff
    return sl_price if sl_price > 0 else Decimal('0')

# v2 (formulae v1.3.3)


def CurrentTradeProfitP(
    open_price: Decimal,
    current_price: Decimal,
    long: bool,
    leverage: Decimal,
    highest_leverage: Decimal
) -> Decimal:
    leverage_to_use = leverage if leverage > highest_leverage else highest_leverage
    if long:
        price_diff = current_price - open_price
    else:
        price_diff = open_price - current_price

    profit_p = (price_diff / open_price) * leverage_to_use * Decimal("100")

    if profit_p >= MAX_PROFIT_P:
        profit_p = MAX_PROFIT_P

    profit_p *= (leverage / leverage_to_use)

    return profit_p

# v2 (formulae v1.3.3)


def TopUpWithCollateral(
    leverage: Decimal,
    collateral: Decimal,
    added_collateral: Decimal
) -> Decimal:
    new_leverage = (collateral * leverage) / (collateral + added_collateral)
    return new_leverage

# v2 (formulae v1.3.3)


def TopUpWithLeverage(
    leverage: Decimal,
    desired_leverage: Decimal,
    collateral: Decimal
) -> Decimal:
    added_c = (collateral * leverage) / desired_leverage - collateral
    return added_c

# v2 (formulae v1.3.3)


def RemoveCollateralWithCollateral(
    leverage: Decimal,
    collateral: Decimal,
    removed_collateral: Decimal
) -> Decimal:
    new_leverage = (collateral * leverage) / (collateral - removed_collateral)
    return new_leverage

# v2 (formulae v1.3.3)


def RemoveCollateralFromLeverage(
    leverage: Decimal,
    desired_leverage: Decimal,
    collateral: Decimal
) -> Decimal:
    added_c = collateral - (collateral * leverage / desired_leverage)
    return added_c

# tbd - used by SDK
# v2 (formulae v1.3.3)


def getTradeLiquidationPrice(
    liqMarginThresholdP: Decimal,
    openPrice: Decimal,
    long: bool,
    collateral: Decimal,
    leverage: Decimal,
    rolloverFee: Decimal,
    fundingFee: Decimal,
    maxLeverage: Decimal
) -> Decimal:
    print(
        f"***** GetTradeLiquidationPrice: open_price: {openPrice}, long: {long}, collateral: {collateral}, leverage: {leverage}, rollover_fee: {rolloverFee}, funding_fee: {fundingFee}")

    rawAdjustedThreshold = (liqMarginThresholdP * leverage /
                            maxLeverage).quantize(quantization_6, rounding=ROUND_DOWN)
    liqMarginValue = (
        collateral * rawAdjustedThreshold).quantize(quantization_6, rounding=ROUND_DOWN)
    targetCollateralAfterFees = (
        collateral - liqMarginValue - rolloverFee - fundingFee)
    liqPriceDistance = (openPrice * targetCollateralAfterFees / collateral /
                        leverage).quantize(quantization_6, rounding=ROUND_DOWN)
    liqPrice = (
        openPrice - liqPriceDistance if long else openPrice + liqPriceDistance)
    return max(Decimal('0'), liqPrice)


def getTradeValue(
    collateral: Decimal,
    percentProfit: Decimal,
    rolloverFee: Decimal,
    fundingFee: Decimal
) -> Decimal:
    profitPart = (collateral * percentProfit / Decimal('100')
                  ).quantize(quantization_6, rounding=ROUND_DOWN)
    value = (collateral + profitPart - rolloverFee - fundingFee)

    return value


def getTradeLiquidationMargin(
    liqMarginThresholdP: Decimal,
    collateral: Decimal,
    leverage: Decimal,
    maxLeverage: Decimal
) -> Decimal:
    rawAdjustedThreshold = (liqMarginThresholdP * leverage /
                            maxLeverage).quantize(quantization_6, rounding=ROUND_DOWN)
    return (collateral * rawAdjustedThreshold / Decimal('100')).quantize(quantization_6, rounding=ROUND_DOWN)


# ???
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


# v2 (formulae v1.3.3)
def GetTradeRolloverFee(
    trade_rollover: Decimal,
    current_rollover: Decimal,
    collateral: Decimal,
    leverage: Decimal
) -> Decimal:
    rollover_fee = (current_rollover - trade_rollover) * collateral * leverage
    return rollover_fee


# Gets the funding fee (abs) for an open trade (up to this block, aka based on current_funding up till this block)
# v2 (formulae v1.3.3)
def GetTradeFundingFee(
    trade_funding: Decimal,
    current_funding: Decimal,
    collateral: Decimal,
    leverage: Decimal
) -> Decimal:
    print(
        f"======> GetTradeFundingFee: trade_funding: {trade_funding}, current_funding: {current_funding}, collateral: {collateral}, leverage: {leverage}")
    funding_fee = (current_funding - trade_funding) * collateral * leverage
    return funding_fee


def GetPriceImpact(
    mid_price: str,
    bid_price: str,
    ask_price: str,
    is_open: bool,
    is_long: bool,
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

# calculates the net profit (after fees) of an open trade (abs)
# v2 (formulae v1.3.3)
def CurrentTradeProfitRaw(
    open_price: Decimal,
    current_price: Decimal,
    long: bool,
    leverage: Decimal,
    highest_leverage: Decimal,
    collateral: Decimal
) -> Decimal:
    profit_p = CurrentTradeProfitP(
        open_price,
        current_price,
        long,
        leverage,
        highest_leverage
    )
    profit = (collateral * profit_p) / Decimal("100")
    return profit

# v2 (formulae v1.3.3)


def CurrentTotalProfitRaw(
    open_price: Decimal,
    current_price: Decimal,
    long: bool,
    leverage: Decimal,
    highest_leverage: Decimal,
    collateral: Decimal,
    rollover_fee: Decimal,
    funding_fee: Decimal
) -> Decimal:
    # Get trade profit
    trade_profit = CurrentTradeProfitRaw(
        open_price,
        current_price,
        long,
        leverage,
        highest_leverage,
        collateral
    )

    # Subtract fees
    total_profit = trade_profit - \
        rollover_fee - funding_fee

    return total_profit


# v2 (formulae v1.3.3)
def CurrentTotalProfitP(total_profit: Decimal, collateral: Decimal) -> Decimal:
    profit_p = (total_profit * Decimal("100")) / collateral
    if profit_p <= MIN_LOSS_P:
        profit_p = MIN_LOSS_P
    return profit_p


def GetFundingRate(
    accPerOiLong: str,
    accPerOiShort: str,
    lastFundingRate: str,
    maxFundingFeePerBlock: str,
    lastUpdateBlock: str,
    latestBlock: str,
    oiLong: str,
    oiShort: str,
    oiCap: str,
    hillInflectionPoint: str,
    hillPosScale: str,
    hillNegScale: str,
    springFactor: str,
    sFactorUpScaleP: str,
    sFactorDownScaleP: str,
    verbose: bool = False
):
    acc_funding_long, acc_funding_short, latest_funding_rate, target_fr = getPendingAccFundingFees(
        blockNumber=Decimal(latestBlock),
        lastUpdateBlock=Decimal(lastUpdateBlock),
        valueLong=Decimal(accPerOiLong) / PRECISION_18,
        valueShort=Decimal(accPerOiShort) / PRECISION_18,
        openInterestUsdcLong=Decimal(oiLong) / PRECISION_6,
        openInterestUsdcShort=Decimal(oiShort) / PRECISION_6,
        OiCap=Decimal(oiCap) / PRECISION_6,
        maxFundingFeePerBlock=Decimal(maxFundingFeePerBlock) / PRECISION_18,
        lastFundingRate=Decimal(lastFundingRate) / PRECISION_18,
        hillInflectionPoint=Decimal(hillInflectionPoint) / PRECISION_18,
        hillPosScale=Decimal(hillPosScale) / PRECISION_2,
        hillNegScale=Decimal(hillNegScale) / PRECISION_2,
        springFactor=Decimal(springFactor) / PRECISION_18,
        sFactorUpScale=Decimal(sFactorUpScaleP) / PRECISION_2,
        sFactorDownScaleP=Decimal(sFactorDownScaleP) / PRECISION_2
    )

    return {
        'accFundingLong': acc_funding_long,
        'accFundingShort': acc_funding_short,
        'latestFundingRate': latest_funding_rate,
        'targetFundingRate': target_fr
    }
