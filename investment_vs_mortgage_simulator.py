import math
from tabulate import tabulate

# ----------------------------
# CONFIGURATION SECTION
# ----------------------------
home_price = 650000
apr = 0.06251
loan_term_years = 20
lump_sum_per_year = 0
rent_years = 0
rent_per_month = 2200
annual_return = 0.06

# Monthly savings while renting (index 0 = January)
monthly_savings_by_month = [
    4000,  # January
    4000,  # February
    4000,  # March
    4000,  # April
    4000,  # May
    10000, # June
    10000, # July
    10000, # August
    4000,  # September
    4000,  # October
    4000,  # November
    4000   # December
]
# ----------------------------

def future_value_monthly_savings(monthly_savings_by_month, annual_return, years):
    r = annual_return / 12
    fv = 0
    total_contributed = 0
    for year in range(years):
        for month_index in range(12):
            monthly_saving = monthly_savings_by_month[month_index]
            total_contributed += monthly_saving
            fv = fv * (1 + r) + monthly_saving
    return fv, total_contributed

def calculate_monthly_payment(loan_amount, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return loan_amount * r / (1 - (1 + r) ** -n)

def calculate_remaining_term(principal, payment, annual_rate):
    r = annual_rate / 12
    try:
        n = math.log(payment / (payment - r * principal)) / math.log(1 + r)
    except:
        return 0
    return round(n / 12, 1)

def simulate_amortization_yearly(principal, monthly_payment, annual_rate, annual_lump_sum):
    r = annual_rate / 12
    year = 0
    schedule = []

    total_mortgage_paid = 0
    total_interest_paid = 0
    total_principal_paid = 0

    while principal > 0:
        year += 1
        starting_balance = principal
        interest_paid = 0
        principal_paid = 0

        for month in range(12):
            interest = principal * r
            payment_toward_principal = monthly_payment - interest
            if payment_toward_principal > principal:
                payment_toward_principal = principal
                monthly_payment = interest + principal
            principal -= payment_toward_principal
            interest_paid += interest
            principal_paid += payment_toward_principal
            if round(principal, 2) <= 0:
                break

        total_paid_mortgage = interest_paid + principal_paid
        total_mortgage_paid += total_paid_mortgage
        total_interest_paid += interest_paid
        total_principal_paid += principal_paid

        balance_before_lump = principal
        lump = min(annual_lump_sum, principal)
        principal -= lump
        years_remaining = calculate_remaining_term(principal, monthly_payment, annual_rate)

        schedule.append([
            year,
            f"${starting_balance:,.2f}",
            f"${total_paid_mortgage:,.2f}",
            f"${interest_paid:,.2f}",
            f"${principal_paid:,.2f}",
            f"${balance_before_lump:,.2f}",
            f"${principal:,.2f}",
            f"{years_remaining}"
        ])

        if round(principal, 2) <= 0:
            break

    schedule.append([
        "TOTAL",
        "",
        f"${total_mortgage_paid:,.2f}",
        f"${total_interest_paid:,.2f}",
        f"${total_principal_paid:,.2f}",
        "",
        "",
        ""
    ])

    return schedule, year

def main():
    down_payment, total_contributed = future_value_monthly_savings(
        monthly_savings_by_month, annual_return, rent_years)
    if rent_years == 0:
        down_payment = 0
    loan_amount = home_price - down_payment
    monthly_payment = calculate_monthly_payment(loan_amount, apr, loan_term_years)
    total_rent_paid = rent_per_month * 12 * rent_years

    print("\n--- Home Purchase & Financing Plan ---\n")
    print(f"Home price: ${home_price:,.2f}")
    print(f"\tAPR (mortgage interest rate): {apr * 100:.3f}%")

    print()
    print(f"Years renting: {rent_years}")
    print(f"Monthly rent while renting: ${rent_per_month:,.2f}")
    print(f"\tTotal rent paid during that time: ${total_rent_paid:,.2f}")

    print()
    print("Yearly savings/investments (while renting)")
    print(f"\tInvestment return (while renting): {annual_return * 100:.1f}%")
    print(f"\tTotal contributed to savings while renting: ${total_contributed:,.2f}")
    print(f"\tEstimated future value of savings after {rent_years} years: ${down_payment:,.2f}")

    print()
    print(f"Down payment used: ${down_payment:,.2f}")
    print(f"Loan amount: ${loan_amount:,.2f}")
    print(f"\tMonthly mortgage payment (P+I): ${monthly_payment:,.2f}\n")

    schedule, total_years = simulate_amortization_yearly(
        loan_amount, monthly_payment, apr, lump_sum_per_year
    )

    headers = [
        "Year",
        "Starting\nBalance",
        "Total mortgage\npaid this year",
        "Interest paid\nthis year",
        "Principal paid\nthis year",
        "Balance before\nlump sum",
        "Balance after\n$30.0k lump sum",
        "Remaining\nyears"
    ]

    print("--- Year-by-Year Mortgage Summary ---")
    print(tabulate(schedule, headers=headers, tablefmt="grid"))
    print(f"\nLoan paid off in {total_years} years")

if __name__ == "__main__":
    main()
