
import csv
from enum import Enum
from decimal import Decimal
from datetime import datetime as Datetime
from pathlib import Path


class FieldRule(Enum):
    REQUIRED = "required"
    FORBIDDEN = "forbidden"
    OPTIONAL = "optional" # one word synonims: 
    IGNORED = "ignored"    


class FieldType(Enum):
    TEXT = "text"
    DATE = "date"
    DECIMAL = "decimal"


def parse_date(value: str):
    if "." in value:
        base, frac = value.split(".")
        frac = (frac + "000000")[:6]  # pad to microseconds
        value = f"{base}.{frac}"

    return Datetime.fromisoformat(value)


CONVERTERS = {
    FieldType.DATE: lambda v: parse_date(v),
    FieldType.DECIMAL: Decimal,
    FieldType.TEXT: lambda v: v,
}


SCHEMA = {
    "Time" : {                                       "Deposit": FieldRule.REQUIRED,  "Withdrawal": FieldRule.REQUIRED,  "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Interest on cash": FieldRule.REQUIRED,  "Card debit": FieldRule.REQUIRED,  "Spending cashback": FieldRule.REQUIRED,  "Stock split open": FieldRule.REQUIRED,  "Stock split close": FieldRule.REQUIRED,  "Currency conversion": FieldRule.REQUIRED },
    "ISIN" : {                                       "Deposit": FieldRule.IGNORED,   "Withdrawal": FieldRule.IGNORED,   "Market buy": FieldRule.IGNORED,   "Market sell": FieldRule.IGNORED,   "Limit buy": FieldRule.IGNORED,   "Dividend (Ordinary)": FieldRule.IGNORED,   "Dividend (Dividend)": FieldRule.IGNORED,   "Dividend (Tax exempted)": FieldRule.IGNORED,   "Dividend (Dividend manufactured payment)": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.FORBIDDEN },
    "Ticker" : {                                     "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.REQUIRED,  "Stock split close": FieldRule.REQUIRED,  "Currency conversion": FieldRule.FORBIDDEN },
    "Name" : {                                       "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.IGNORED,   "Market sell": FieldRule.IGNORED,   "Limit buy": FieldRule.IGNORED,   "Dividend (Ordinary)": FieldRule.IGNORED,   "Dividend (Dividend)": FieldRule.IGNORED,   "Dividend (Tax exempted)": FieldRule.IGNORED,   "Dividend (Dividend manufactured payment)": FieldRule.IGNORED,   "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.FORBIDDEN },
    "Notes" : {                                      "Deposit": FieldRule.IGNORED,   "Withdrawal": FieldRule.IGNORED,   "Market buy": FieldRule.IGNORED,   "Market sell": FieldRule.IGNORED,   "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.IGNORED,   "Dividend (Dividend)": FieldRule.IGNORED,   "Dividend (Tax exempted)": FieldRule.IGNORED,   "Dividend (Dividend manufactured payment)": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Interest on cash": FieldRule.IGNORED,   "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.IGNORED },
    "ID" : {                                         "Deposit": FieldRule.IGNORED,   "Withdrawal": FieldRule.IGNORED,   "Market buy": FieldRule.IGNORED,   "Market sell": FieldRule.IGNORED,   "Limit buy": FieldRule.IGNORED,   "Dividend (Ordinary)": FieldRule.IGNORED,   "Dividend (Dividend)": FieldRule.IGNORED,   "Dividend (Tax exempted)": FieldRule.IGNORED,   "Dividend (Dividend manufactured payment)": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Lending interest": FieldRule.IGNORED,   "Interest on cash": FieldRule.IGNORED,   "Card debit": FieldRule.IGNORED,   "Spending cashback": FieldRule.IGNORED,   "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.IGNORED },
    "No. of shares" : {                              "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.REQUIRED,  "Stock split close": FieldRule.REQUIRED,  "Currency conversion": FieldRule.FORBIDDEN },
    "Price / share" : {                              "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.REQUIRED,  "Stock split close": FieldRule.REQUIRED,  "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (Price / share)" : {                   "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.REQUIRED,  "Stock split close": FieldRule.REQUIRED,  "Currency conversion": FieldRule.FORBIDDEN },
    "Exchange rate" : {                              "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.IGNORED,   "Dividend (Dividend)": FieldRule.IGNORED,   "Dividend (Tax exempted)": FieldRule.IGNORED,   "Dividend (Dividend manufactured payment)": FieldRule.IGNORED,   "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.FORBIDDEN },
    "Result" : {                                     "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (Result)" : {                          "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.OPTIONAL,  "Dividend (Dividend)": FieldRule.OPTIONAL,  "Dividend (Tax exempted)": FieldRule.OPTIONAL,  "Dividend (Dividend manufactured payment)": FieldRule.OPTIONAL,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.FORBIDDEN },
    "Total" : {                                      "Deposit": FieldRule.REQUIRED,  "Withdrawal": FieldRule.REQUIRED,  "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Interest on cash": FieldRule.REQUIRED,  "Card debit": FieldRule.REQUIRED,  "Spending cashback": FieldRule.REQUIRED,  "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.IGNORED },
    "Currency (Total)" : {                           "Deposit": FieldRule.REQUIRED,  "Withdrawal": FieldRule.REQUIRED,  "Market buy": FieldRule.REQUIRED,  "Market sell": FieldRule.REQUIRED,  "Limit buy": FieldRule.REQUIRED,  "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Lending interest": FieldRule.REQUIRED,  "Interest on cash": FieldRule.REQUIRED,  "Card debit": FieldRule.REQUIRED,  "Spending cashback": FieldRule.REQUIRED,  "Stock split open": FieldRule.IGNORED,   "Stock split close": FieldRule.IGNORED,   "Currency conversion": FieldRule.IGNORED },
    "Withholding tax" : {                            "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN }, # withholding tax is provided for dividends, but it the result is given already including it, so it's ignored. TODO: include it as fee or new field `tax`
    "Currency (Withholding tax)" : {                 "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.REQUIRED,  "Dividend (Dividend)": FieldRule.REQUIRED,  "Dividend (Tax exempted)": FieldRule.REQUIRED,  "Dividend (Dividend manufactured payment)": FieldRule.REQUIRED,  "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Charge amount" : {                              "Deposit": FieldRule.OPTIONAL,  "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (Charge amount)" : {                   "Deposit": FieldRule.OPTIONAL,  "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Deposit fee" : {                                "Deposit": FieldRule.OPTIONAL,  "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (Deposit fee)" : {                     "Deposit": FieldRule.OPTIONAL,  "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Stamp duty reserve tax" : {                     "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (Stamp duty reserve tax)" : {          "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Currency conversion from amount" : {            "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.REQUIRED },
    "Currency (Currency conversion from amount)" : { "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.REQUIRED },
    "Currency conversion to amount" : {              "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.REQUIRED },
    "Currency (Currency conversion to amount)" : {   "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.REQUIRED },
    "Currency conversion fee" : {                    "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.OPTIONAL,  "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.OPTIONAL },
    "Currency (Currency conversion fee)" : {         "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.OPTIONAL,  "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.OPTIONAL },    
    "Merchant name" : {                              "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.IGNORED,   "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Merchant category" : {                          "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.FORBIDDEN, "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.FORBIDDEN, "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.IGNORED,   "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "French transaction tax" : {                     "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
    "Currency (French transaction tax)" : {          "Deposit": FieldRule.FORBIDDEN, "Withdrawal": FieldRule.FORBIDDEN, "Market buy": FieldRule.OPTIONAL,  "Market sell": FieldRule.FORBIDDEN, "Limit buy": FieldRule.OPTIONAL,  "Dividend (Ordinary)": FieldRule.FORBIDDEN, "Dividend (Dividend)": FieldRule.FORBIDDEN, "Dividend (Tax exempted)": FieldRule.FORBIDDEN, "Dividend (Dividend manufactured payment)": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Lending interest": FieldRule.FORBIDDEN, "Interest on cash": FieldRule.FORBIDDEN, "Card debit": FieldRule.FORBIDDEN, "Spending cashback": FieldRule.FORBIDDEN, "Stock split open": FieldRule.FORBIDDEN, "Stock split close": FieldRule.FORBIDDEN, "Currency conversion": FieldRule.FORBIDDEN },
}


FIELD_TYPES = {
    "Time": FieldType.DATE,
    "Ticker": FieldType.TEXT,
    "No. of shares": FieldType.DECIMAL,
    "Price / share": FieldType.DECIMAL,
    "Currency (Price / share)": FieldType.TEXT,
    "Exchange rate": FieldType.DECIMAL,
    "Result": FieldType.DECIMAL,
    "Currency (Result)": FieldType.TEXT,
    "Total": FieldType.DECIMAL,
    "Currency (Total)": FieldType.TEXT,
    "Withholding tax": FieldType.DECIMAL,
    "Currency (Withholding tax)": FieldType.TEXT,
    "Charge amount": FieldType.DECIMAL,
    "Currency (Charge amount)": FieldType.TEXT,
    "Deposit fee": FieldType.DECIMAL,
    "Currency (Deposit fee)": FieldType.TEXT,
    "Stamp duty reserve tax": FieldType.DECIMAL,
    "Currency (Stamp duty reserve tax)": FieldType.TEXT,
    "Currency conversion from amount": FieldType.DECIMAL,
    "Currency (Currency conversion from amount)": FieldType.TEXT,
    "Currency conversion to amount": FieldType.DECIMAL,
    "Currency (Currency conversion to amount)": FieldType.TEXT,
    "Currency conversion fee": FieldType.DECIMAL,
    "Currency (Currency conversion fee)": FieldType.TEXT,
    "French transaction tax": FieldType.DECIMAL,
    "Currency (French transaction tax)": FieldType.TEXT,
}


def load_csv(path: str, base_currency: str) -> list[dict]:
    path_obj = Path(path)

    files = (
        [path_obj]
        if path_obj.is_file()
        else list(path_obj.glob("*.csv"))
    )

    files.sort(key=lambda f: f.name)

    events = []

    for file in files:
        events.extend(_load_single_file(file, base_currency))

    return events


def _load_single_file(file_path: Path, base_currency: str) -> list[dict]:
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = []
        for row in reader:
            parsed = _parse_row(row, base_currency)
            rows.append(parsed)

        return rows
    

def _parse_row(row: dict, base_currency: str) -> dict:
    type = row["Action"]

    parsed = {}

    if base_currency != row.get('Currency (Total)', base_currency) and len(row.get('Currency (Total)', base_currency)) != 0 and type not in ["Market buy", "Limit buy", "Market sell", "Interest on cash", "Currency conversion"]:
        raise ValueError(f"Unsupported currency '{row.get('Currency (Total)', base_currency)}' in 'Currency (Total)' for row {row}")
    if base_currency != row.get('Currency (Result)', base_currency) and len(row.get('Currency (Result)', base_currency)) != 0 and type != "Market sell":
        raise ValueError(f"Unsupported currency '{row.get('Currency (Result)', base_currency)}' in 'Currency(Result)' field (only {base_currency} is supported)")            
    if row.get("Currency (Currency conversion fee)", base_currency) != base_currency and len(row.get('Currency (Currency conversion fee)', base_currency)) != 0 and type != "Currency conversion":
        raise ValueError(f"Unsupported currency '{row.get('Currency (Currency conversion fee)', base_currency)}' in 'Currency (Currency conversion fee)' field (only {base_currency} is supported)")    
    if row.get("Currency (Charge amount)", base_currency) != base_currency and len(row.get('Currency (Charge amount)', base_currency)) != 0:
        raise ValueError(f"Unsupported currency '{row.get('Currency (Charge amount)', base_currency)}' in 'Currency (Charge amount)' field (only {base_currency} is supported)")
    if row.get("Currency (Deposit fee)", base_currency) != base_currency and len(row.get('Currency (Deposit fee)', base_currency)) != 0:
        raise ValueError(f"Unsupported currency '{row.get('Currency (Deposit fee)', base_currency)}' in 'Currency (Deposit fee)' field (only {base_currency} is supported)")
    if row.get("Currency (Stamp duty reserve tax)", base_currency) != base_currency and len(row.get('Currency (Stamp duty reserve tax)', base_currency)) != 0 and type not in ["Market buy"]:
        raise ValueError(f"Unsupported currency '{row.get('Currency (Stamp duty reserve tax)', base_currency)}' in 'Currency (Stamp duty reserve tax)' for row {row}")
    if row.get("Currency (French transaction tax)", base_currency) != base_currency and len(row.get('Currency (French transaction tax)', base_currency)) != 0 and type not in ["Market buy"]:
        raise ValueError(f"Unsupported currency '{row.get('Currency (French transaction tax)', base_currency)}' in 'Currency (French transaction tax)' field (only {base_currency} is supported)")
    if row.get("Currency (Currency conversion from amount)", base_currency) != base_currency and len(row.get('Currency (Currency conversion from amount)', base_currency)) != 0 and \
            row.get('Currency (Currency conversion to amount)', base_currency) != base_currency and len(row.get('Currency (Currency conversion to amount)', base_currency)) != 0:
        raise ValueError(f"Unsupported currency '{row.get('Currency (Currency conversion from amount)', base_currency)}' or '{row.get('Currency (Currency conversion to amount)', base_currency)}' in 'Currency (Currency conversion from/to amount)' fields (only {base_currency} is supported)")

    for field, value in row.items():
        if field == "Action":
            parsed[field] = value
            continue

        if field not in SCHEMA:
            raise ValueError(f"Unexpected field '{field}'")

        field_schema = SCHEMA[field]
        if type not in field_schema:
            raise ValueError(f"Schema of type '{type}' is not specified for field '{field}'")
        
        rule = field_schema[type]

        match rule:
            case FieldRule.REQUIRED:
                if len(value) == 0:
                    raise ValueError(f"Missing required field '{field}' for {type} in row {row}")
                parsed[field] = _convert_value(field, value)

            case FieldRule.FORBIDDEN:
                if len(value) != 0:
                    raise ValueError(f"Field '{field}' must be empty for {type} in row {row}")
                continue

            case FieldRule.OPTIONAL:
                if len(value) != 0:
                    parsed[field] = _convert_value(field, value)

            case FieldRule.IGNORED:
                continue

    return parsed


def _convert_value(field: str, value: str):
    field_type = FIELD_TYPES.get(field)

    if field_type is None:
        raise ValueError(f"missing type definition for field '{field}'")

    converter = CONVERTERS.get(field_type)

    if converter is None:
        raise ValueError(f"No converter for field type '{field_type}' (field '{field}')")

    return converter(value)