import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mortgage & Savings Simulator", layout="wide")

def currency_input(label, value, key):
    raw = st.sidebar.text_input(label, f"${value:,}", key=key)
    try:
        return int(raw.replace("$", "").replace(",", "").strip())
    except:
        return value

# --- Defaults
D_HOME = 650000
D_APR = 6.251
D_EXTRA = 30000
D_DP1 = 0
D_RENT_YEARS = 2
D_RENT_MONTH = 2200
D_RETURN = 6.0
DEFAULT_SAVINGS = [4000]*5 + [10000]*3 + [4000]*4

# --- Sidebar: Mortgage params
#st.sidebar.markdown("### 🏠 Mortgage Parameters")

# --- Sidebar: Mortgate parms
st.sidebar.markdown(
    '<br><span style="color:#e67300; font-weight:bold;">Mortgage Parameters</span><br>',
    unsafe_allow_html=True
)

home_price = currency_input("Home price ($)", D_HOME, "home_price")

col1, col2 = st.sidebar.columns(2)
apr_percent = col1.number_input("APR (%)", value=D_APR, format="%.3f")
loan_term_years = col2.selectbox("Loan term (years)", [10,15,20,25,30], index=2)
apr = apr_percent / 100

extra_payment = currency_input("Extra lump payment at the end of each year ($)", D_EXTRA, "extra_payment")


# --- Sidebar: Down payment part 1
st.sidebar.markdown(
    '<br><span style="color:#e67300; font-weight:bold;">Down payment [Contribution 1/2]</span><br>'
    '<em>(Any sources)</em>',
    unsafe_allow_html=True
)

down_pay_part1 = currency_input("Amount ($)", D_DP1, "down_part1")

# --- Sidebar: Down payment part 2 & renting
st.sidebar.markdown(
    '<br><span style="color:#e67300; font-weight:bold;">Down payment [Contribution 2/2]</span><br>'
    '<em>(Investments while renting)</em>',
    unsafe_allow_html=True
)
col1, col2 = st.sidebar.columns(2)
rent_years = col1.number_input("Years renting", value=D_RENT_YEARS, min_value=0, step=1)
rent_per_month = col2.text_input("Monthly rent ($)", f"${D_RENT_MONTH:,}", key="monthly_rent")
try:
    rent_per_month = int(rent_per_month.replace("$","").replace(",",""))
except:
    rent_per_month = D_RENT_MONTH

# --- Sidebar: Savings plan
#st.sidebar.markdown("### 🗓️ Savings plan while renting")
investment_return_percent = st.sidebar.number_input("Investment return (%)", value=D_RETURN, format="%.3f")
annual_return = investment_return_percent / 100

#st.sidebar.markdown(
#    '<span style="color:#e67300;"><hr></span>',
#    unsafe_allow_html=True
#)

st.sidebar.markdown('<div style="border-top: 1px solid #ccc; margin: 12px 0;"></div>', unsafe_allow_html=True)


monthly_savings = []
months = pd.date_range("2020-01-01", periods=12, freq="M").strftime("%B")
for i in range(0,12,2):
    c1, c2 = st.sidebar.columns(2)
    val1 = c1.text_input(f"{months[i]} savings ($)", f"${DEFAULT_SAVINGS[i]:,}", key=f"sav_{i}")
    val2 = c2.text_input(f"{months[i+1]} savings ($)", f"${DEFAULT_SAVINGS[i+1]:,}", key=f"sav_{i+1}")
    try:
        val1 = int(val1.replace("$","").replace(",",""))
    except:
        val1 = DEFAULT_SAVINGS[i]
    try:
        val2 = int(val2.replace("$","").replace(",",""))
    except:
        val2 = DEFAULT_SAVINGS[i+1]
    monthly_savings.extend([val1, val2])

# --- Calculations (same as before)
def future_value_ms(ms, r, years):
    r_m, fv, total = r/12, 0.0, 0.0
    for _ in range(years):
        for m in ms:
            total += m
            fv = fv*(1+r_m)+m
    return fv, total

def monthly_payment(P, r, yrs):
    r_m = r/12
    return P*r_m/(1-(1+r_m)**-(yrs*12))

def remain_years(p, pay, r):
    m = r/12
    if pay <= p*m: return 0
    return round(math.log(pay/(pay-p*m)) / math.log(1+m) /12,1)

def amort_yearly(P, pay, r, lump):
    rows=[]
    tot_int=tot_princ=0.0
    year=0
    while P>1e-6:
        year +=1
        sb=P
        intp=prcp=0.0
        for _ in range(12):
            interest=P*r/12
            principal=max(0.0,pay-interest)
            if principal>P:
                principal, pay=P,interest+P
            P-=principal
            intp+=interest
            prcp+=principal
            if P<1e-6:
                P=0
                break
        tot_int+=intp
        tot_princ+=prcp
        prev=P
        P=max(0.0,P-lump)
        rows.append([year,sb,intp+prcp,intp,prcp,prev,P,remain_years(P,pay,r)])
    rows.append(["TOTAL",None,tot_int+tot_princ,tot_int,tot_princ,None,None,None])
    return rows

# --- Simulation
fv, contrib = future_value_ms(monthly_savings, annual_return, rent_years)
down_payment = down_pay_part1 + fv
loan_amount = home_price - down_payment
monthly_pay = monthly_payment(loan_amount, apr, loan_term_years)
rows = amort_yearly(loan_amount, monthly_pay, apr, extra_payment)

df = pd.DataFrame(rows, columns=[
    "Year","Starting Balance","Mortgage [P+I] (yearly)",
    "Interest Paid","Principal Paid","Balance Before Lump Sum",
    "Balance After Lump Sum","Remaining Years"
])
for c in df.columns[1:7]:
    df[c]=df[c].apply(lambda x: f"${x:,.2f}" if isinstance(x,(int,float)) else x)

# --- Display
#st.title("🏠 Mortgage & Investments Simulator")
st.markdown("### 🏠 Mortgage & Investments Simulator")
st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)


st.markdown(
    f"""<table style="width:100%; border:1px solid #ddd; border-collapse: collapse">
       <tr>
         <td style="padding:8px;"><strong>Amount saved while renting:</strong> ${contrib:,.2f}</td>
         <td style="padding:8px;"><strong>Future value of savings (after {rent_years} years):</strong> ${fv:,.2f}</td>
       </tr></table>""",
    unsafe_allow_html=True
)

st.markdown(f"""<table style="width:100%;background-color:#f0f8ff;border:1px solid #ddd;border-collapse:collapse">
<tr>
<td style="padding:8px;"><strong style="color:#003366">Total down payment [Contributions 1+2]:</strong> <strong style="color:#e67300">${down_payment:,.2f}</strong></td>
<td style="padding:8px;"><strong style="color:#003366">Loan amount:</strong> <strong style="color:#e67300">${loan_amount:,.2f}</strong></td>
<td style="padding:8px;"><strong style="color:#003366">Monthly mortgage (P+I):</strong> <strong style="color:#e67300">${monthly_pay:,.2f}</strong></td>
</tr></table>""",unsafe_allow_html=True)

st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
#st.markdown("##### Year‑by‑Year Amortization Schedule")
st.markdown('<h5 style="color:#3399cc;">Year‑by‑Year Amortization Schedule</h5>', unsafe_allow_html=True)

st.dataframe(df[df.Year!="TOTAL"], hide_index=True)

tot, tot_int, tot_princ = rows[-1][2],rows[-1][3],rows[-1][4]
st.markdown(f"""<table style="width:100%;background-color:#f0f8ff;border:1px solid #ddd;border-collapse:collapse">
<tr>
<td style="padding:8px;"><strong style="color:#003366">Total mortgage paid:</strong> <strong style="color:#e67300">${tot:,.2f}</strong></td>
<td style="padding:8px;"><strong style="color:#003366">Total interest paid:</strong> <strong style="color:#e67300">${tot_int:,.2f}</strong></td>
<td style="padding:8px;"><strong style="color:#003366">Total principal paid:</strong> <strong style="color:#e67300">${tot_princ:,.2f}</strong></td>
</tr></table>""",unsafe_allow_html=True)
