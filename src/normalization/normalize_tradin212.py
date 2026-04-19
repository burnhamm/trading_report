from model.action import *
from decimal import Decimal, ROUND_HALF_UP


def normalize(raw_actions: list[dict], base_currency: str) -> list[Action]:
    actions = []
    merging_actions = {}

    for row in raw_actions:
        new = _map_row(row, base_currency, merging_actions)
        if new:
            actions.extend(new)

    return actions


def _map_row(row: dict, base_currency: str, merging_actions: dict) -> list[Action]:
    type = row["Action"]

    match type:
        case "Deposit":
            return _map_deposit(row)
        case "Withdrawal":
            return _map_withdrawal(row)
        case "Market buy" | "Limit buy":
            return _map_buy(row, base_currency)
        case "Market sell":
            return _map_sell(row, base_currency)
        case "Dividend (Ordinary)" | "Dividend (Dividend)" | "Dividend (Tax exempted)":
            return _map_dividend(row, False)
        case "Dividend (Dividend manufactured payment)":
            # it seems to be supplementary dividend for the missing part of the previous dividend.
            # To spread the dividend amount positions correctly it is assigned to positions starting from the last backwards
            return _map_dividend(row, True)
        case "Lending interest":
            return _map_lending_interest(row)
        case "Interest on cash":
            return _map_interest_on_cash(row)
        case "Currency conversion":
            return _map_currency_conversion(row, base_currency)
        case "Card debit":
            return _map_spending(row)
        case "Spending cashback":
            return _map_cashbak(row)
            
        case "Stock split open":
            split_close = merging_actions.get(("Stock split close", row["Ticker"]))
            if not split_close:
                raise ValueError(f"Stock split open without matching close for ticker {row['Ticker']}")
            actions = _map_split(row, split_close)
            del merging_actions[("Stock split close", row["Ticker"])]
            return actions
        case "Stock split close": # split close goes before split open
            if ("Stock split close", row["Ticker"]) in merging_actions:
                raise ValueError(f"Duplicate stock split close for ticker {row['Ticker']}")
            merging_actions[("Stock split close", row["Ticker"])] = row
            return []
        
    raise ValueError(f"Unknown action type: {type}")    


def _map_deposit(row: dict) -> list[Action]:
    return [DepositAction(
        date=row["Time"],
        amount=row["Total"],
        fee=-row.get("Deposit fee", Decimal("0")), # should be in base currency
    )]


def _map_withdrawal(row: dict) -> list[Action]:
    return [WithdrawalAction(
        date=row["Time"],
        amount=-row["Total"],
    )]


def _map_buy(row: dict, base_currency: str) -> list[Action]:    
    actions = []

    currency: str = row['Currency (Price / share)']
    price: Decimal = row['Price / share']
    ex_rate: Decimal = row['Exchange rate']
    if currency == 'GBX':
        currency = 'GBP'
        price /= 100
        ex_rate /= 100
    if currency == row["Currency (Total)"]:
        ex_rate = None

    if row.get("Stamp duty reserve tax", Decimal("0")) != Decimal("0") and row.get("French transaction tax", Decimal("0")) != Decimal("0"):
        raise ValueError(f"Both stamp duty reserve tax and french transaction tax are present for the same buy action on {row['Time']} for ticker {row['Ticker']}. This case is not supported.")
    
    tax = Decimal("0")
    tax_currency = base_currency
    if row.get("Stamp duty reserve tax", Decimal("0")) > Decimal("0"):
        tax = row["Stamp duty reserve tax"]
        tax_currency = row["Currency (Stamp duty reserve tax)"]
    elif row.get("French transaction tax", Decimal("0")) > Decimal("0"):
        tax = row["French transaction tax"]
        tax_currency = row["Currency (French transaction tax)"]
    if tax_currency == 'GBX':
        tax_currency = 'GBP'
        tax /= 100

    actions.append(BuyAction(
        date=row["Time"],
        symbol=row["Ticker"],
        currency=currency,
        quantity=row["No. of shares"],
        price=price,
        ex_rate=1 / ex_rate if ex_rate else None,
        exchange_fee=row.get("Currency conversion fee", Decimal("0")),
        tax=tax,
        tax_currency=tax_currency,
        result=row["Total"],
        result_currency=row["Currency (Total)"],
    ))
    return actions


def _map_sell(row: dict, base_currency: str) -> list[Action]:    
    actions = []

    currency: str = row['Currency (Price / share)']
    price: Decimal = row['Price / share']
    ex_rate: Decimal = row['Exchange rate']
    if currency == 'GBX':
        currency = 'GBP'
        price /= 100
        ex_rate /= 100
    if currency == row["Currency (Total)"]:
        ex_rate = None        

    actions.append(SellAction(
        date=row["Time"],
        symbol=row["Ticker"],
        currency=currency,
        quantity=row["No. of shares"],
        price=price,
        ex_rate=1 / ex_rate if ex_rate else None,
        exchange_fee=row.get("Currency conversion fee", Decimal("0")),
        result=row["Total"],
        result_currency=row["Currency (Total)"],
    ))

    return actions


def _map_dividend(row: dict, reversed: bool) -> list[Action]:
    tax = row["Withholding tax"] #TODO: this tax is present, but does not seem to be actually withheld. Not sure what to do with it
    tax_currency = row["Currency (Withholding tax)"]
    if tax_currency == 'GBX':
        tax_currency = 'GBP'
        tax /= 100

    return [DividendAction(
        date=row["Time"],
        symbol=row["Ticker"],
        currency=row["Currency (Total)"],
        no_of_shares=row["No. of shares"],
        amount_per_share=row["Price / share"],
        reversed_assignment=reversed,
        tax=tax,
        tax_currency=tax_currency,
        result=row["Total"],
    )]


def _map_lending_interest(row: dict) -> list[Action]:
    return [LendingInterestAction(
        date=row["Time"],
        result=row["Total"],
    )]


def _map_interest_on_cash(row: dict) -> list[Action]:
    return [InterestOnCashAction(
        date=row["Time"],
        currency=row["Currency (Total)"],
        amount=row["Total"],
    )]


def _map_currency_conversion(row: dict, base_currency: str) -> list[Action]:
    # TODO: unlike other actions, for this one the fee is not accounted for in the Total, and should be subtracted explicitly
    #+I think fee as closed position should be implemented for all actions. For now I will not create it though
    if row["Currency (Currency conversion from amount)"] != base_currency and \
       row["Currency (Currency conversion to amount)"] != base_currency:
        raise ValueError(f"Currency conversion between non-base currencies is not supported: {row['Currency (Currency conversion from amount)']} to {row['Currency (Currency conversion to amount)']}")

    if row["Currency (Currency conversion from amount)"] == base_currency:
        ex_rate = row["Currency conversion from amount"] / row["Currency conversion to amount"]
        fee = Decimal(-row.get("Currency conversion fee", Decimal("0")))
        return [ExchangeBuyAction(
            date=row["Time"],
            currency=row["Currency (Currency conversion to amount)"],
            quantity=row["Currency conversion to amount"] - fee,
            exchange_rate=(ex_rate).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),
            fee=fee,
            fee_currency=row.get("Currency (Currency conversion fee)", base_currency),
            result=row["Currency conversion from amount"],
        )]
    else:
        ex_rate = row["Currency conversion to amount"] / row["Currency conversion from amount"]
        # TODO: I haven't done exhange sell yet, so I don't know if I should subtract fee as in exhange buy. Perform this experiment
        return [ExchangeSellAction(
            date=row["Time"],
            currency=row["Currency (Currency conversion from amount)"],
            quantity=row["Currency conversion from amount"],
            exchange_rate=(ex_rate).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),            
            fee=-row.get("Currency conversion fee", Decimal("0")),
            fee_currency=row.get("Currency (Currency conversion fee)", base_currency),
            result=row["Currency conversion to amount"],
        )]


def _map_spending(row: dict) -> list[Action]:
    return [SpendingAction(
        date=row["Time"],
        result=-row["Total"],
    )]


def _map_cashbak(row: dict) -> list[Action]:
    return [CashbackAction(
        date=row["Time"],
        result=row["Total"],
    )]


def _map_split(open: dict, close: dict) -> list[Action]:
    return [SplitAction(
        date=open["Time"],
        symbol=open["Ticker"],
        ratio=open["No. of shares"] / close["No. of shares"],
    )]
