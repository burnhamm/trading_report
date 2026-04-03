import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze broker CSVs and generate financial reports."
    )

    parser.add_argument(
        "--input",
        default="data",
        help="Path to input CSV file or directory containing CSVs (default: data/)."
    )
    parser.add_argument(
        "--output-path",
        default="out",
        help="Directory where reports will be saved (default: out/)."
    )
    parser.add_argument(
        "--broker",
        choices=["trading212"],
        default="trading212",
        help="Broker name (currently only 'trading212' is supported)."
    )
    parser.add_argument(
        "--base-currency",
        default="PLN",
        help="Base currency for FX and reporting (default: PLN)."
    )
    parser.add_argument(
        "--to-date",
        help="End date for filtering events (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--include-open",
        action="store_true",
        help="Include open positions in reports."
    )
    parser.add_argument(
        "--fx-mode",
        choices=["realized", "full"],
        default="realized",
        help="FX handling mode: realized (default) or full."
    )

    # Debug / development
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress messages."
    )
    parser.add_argument(
        "--dump-events",
        action="store_true",
        help="Save normalized events to file for inspection."
    )

    return parser.parse_args()