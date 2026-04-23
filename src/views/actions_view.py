import csv

from model.action import Action, DepositAction, WithdrawalAction, BuyAction, SellAction, DividendAction

def generate_actions_view(actions: list[Action], output_path: str):
    data = []

    for action in actions:
        if isinstance(action, DepositAction):
            data.append(["Deposit", action.date.date(), "", "", action.amount, "", "", action.fee, "", "", action.amount])
        elif isinstance(action, WithdrawalAction):
            data.append(["Withdrawal", action.date.date(), "", "", action.amount, "", "", "", "", "", action.amount])
        elif isinstance(action, BuyAction):
            data.append(["Buy", action.date.date(), action.symbol, action.currency, action.quantity, action.price, action.ex_rate, action.exchange_fee, action.tax, action.tax_currency, action.result])
        elif isinstance(action, SellAction):
            data.append(["Sell", action.date.date(), action.symbol, action.currency, action.quantity, action.price, action.ex_rate, action.exchange_fee, "", "", action.result])
        elif isinstance(action, DividendAction):
            data.append(["Dividend", action.date.date(), action.symbol, action.currency, "", "", "", "", action.tax, action.tax_currency, action.result])

    data.sort(key=lambda r: r[0])
    data.insert(0, ["Type", "Date", "Ticker", "Currency", "Quantity", "Price", "Exchange rate", "Fee", "Tax", "Tax Currency", "Result"])

    with open(output_path + "/actions.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
