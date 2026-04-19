from decimal import Decimal, ROUND_HALF_UP

def normalize_decimal(value: Decimal, precision: int = 8) -> Decimal:
    if value == 0:
        return '0'

    return value.quantize(Decimal(f"1e-{precision}"), rounding=ROUND_HALF_UP)


def normalize_money(value: Decimal) -> Decimal:
    return normalize_decimal(value, precision=2)

def normalize_ex_rate(value: Decimal) -> Decimal:
    return normalize_decimal(value, precision=4)