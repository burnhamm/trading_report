import csv

from decimal import Decimal, ROUND_HALF_UP

from model.incomes_n_costs import Incost, IncostType

def generate_income_cost_view(incomes_n_costs: list[Incost], fx_rate_provider, output_path: str):
    data = []
    for incost in incomes_n_costs:
        result = incost.amount * fx_rate_provider.get_rate(incost.currency, incost.date)
        data.append([incost.date.date(), f"{incost.type.value}", incost.amount, incost.currency, incost.symbol, result])

    data.sort(key=lambda r: r[0])
    data.insert(0, ["Date", "Type", "Amount", "Currency", "Symbol", f"Result ({fx_rate_provider.base_currency})"])

    with open(output_path + "/incomes_and_costs.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
