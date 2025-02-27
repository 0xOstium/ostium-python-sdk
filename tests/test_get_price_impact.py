from ostium_python_sdk.formulae import GetPriceImpact
from decimal import Decimal
import pytest


@pytest.fixture
def test_cases():
    return [
        {
            'midPrice': Decimal('0'),
            'bidPrice': Decimal('98'),
            'askPrice': Decimal('0'),
            'is_open': True,
            'is_long': True,
            'expected_price_impact_p': '0',
            'expected_price_after_impact': '0'
        },
        {
            'midPrice': Decimal('100'),
            'bidPrice': Decimal('99'),
            'askPrice': Decimal('101'),
            'is_open': True,
            'is_long': True,
            'expected_price_impact_p': '1.00',
            'expected_price_after_impact': '101'
        },
        {
            'midPrice': Decimal('100'),
            'bidPrice': Decimal('99'),
            'askPrice': Decimal('101'),
            'is_open': False,
            'is_long': True,
            'expected_price_impact_p': '1.00',
            'expected_price_after_impact': '99'
        },
        {
            'midPrice': Decimal('100'),
            'bidPrice': Decimal('99'),
            'askPrice': Decimal('101'),
            'is_open': False,
            'is_long': False,
            'expected_price_impact_p': '1.00',
            'expected_price_after_impact': '101'
        },
    ]


def test_get_price_impact(test_cases):
    for case in test_cases:
        response = GetPriceImpact(
            case['midPrice'],
            case['bidPrice'],
            case['askPrice'],
            case['is_open'],
            case['is_long']
        )
        assert pytest.approx(response['priceAfterImpact'], rel=Decimal(1e-7)
                             ) == case['expected_price_after_impact']
        assert pytest.approx(response['priceImpactP'], rel=Decimal(1e-7)
                             ) == case['expected_price_impact_p']
