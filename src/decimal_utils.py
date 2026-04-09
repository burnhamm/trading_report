from decimal import Decimal, ROUND_HALF_UP

def normalize_decimal(value: Decimal, precision: int = 8) -> str:
    if value == 0:
        return '0'

    return str(value.quantize(Decimal(f"1e-{precision}"), rounding=ROUND_HALF_UP))


def normalize_money(value: Decimal) -> str:
    return normalize_decimal(value, precision=2)
