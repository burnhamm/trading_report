import csv

from model.cash_flow import CashFlowEvent

def generate_cash_flow_view(cash_flow: list[CashFlowEvent], output_path: str):
    data = []
    for f in cash_flow:
        data.append([f.date.date(), f"{f.type.value}", f.amount])

    data.sort(key=lambda r: r[0])
    data.insert(0, ["Date", "Type", "Amount"])

    with open(output_path + "/cash_flow.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
