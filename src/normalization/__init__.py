from normalization.normalize_tradin212 import normalize as normalize_tradin212


def normalize_actions(path: str, base_currency: str,  broker: str) -> list[dict]:
    if broker == "trading212":
        return normalize_tradin212(path, base_currency)

    raise ValueError(f"Unsupported broker: {broker}")
