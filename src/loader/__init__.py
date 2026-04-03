from loader.csv_loader_tradin212 import load_csv as load_csv_tradin212


def load_csv(path: str, base_currency: str, broker: str) -> list[dict]:
    if broker == "trading212":
        return load_csv_tradin212(path, base_currency)

    raise ValueError(f"Unsupported broker: {broker}")
