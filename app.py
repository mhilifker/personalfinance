import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------------------------------------------------------
# PAGE & SESSION STATE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Slovenian Arbitrage Dashboard", layout="wide")

# Initialize Master Inputs
if 'ret_age' not in st.session_state: st.session_state.ret_age = 55 
if 'move_age' not in st.session_state: st.session_state.move_age = 56
if 'current_age' not in st.session_state: st.session_state.current_age = 37
if 'nb_start_yr' not in st.session_state: st.session_state.nb_start_yr = 2027
if 'inflation_rate' not in st.session_state: st.session_state.inflation_rate = 3.0

# Bifurcated Returns
if 'usd_market_return' not in st.session_state: st.session_state.usd_market_return = 7.0
if 'eur_market_return' not in st.session_state: st.session_state.eur_market_return = 6.0
if 'execute_great_reset' not in st.session_state: st.session_state.execute_great_reset = True

# Lifetime Tax Smoothing & Giving While Living
if 'enable_smoothing' not in st.session_state: st.session_state.enable_smoothing = True
if 'target_early_draw' not in st.session_state: st.session_state.target_early_draw = 210000
if 'gift_start_age' not in st.session_state: st.session_state.gift_start_age = 58
if 'gift_end_age' not in st.session_state: st.session_state.gift_end_age = 83

# Tax Assumptions
if 'tax_roth' not in st.session_state: st.session_state.tax_roth = 25.0
if 'tax_pretax_base' not in st.session_state: st.session_state.tax_pretax_base = 16.0
if 'tax_pretax_excess' not in st.session_state: st.session_state.tax_pretax_excess = 25.0
if 'tax_cap_gains' not in st.session_state: st.session_state.tax_cap_gains = 15.0
if 'us_ss_tax_rate' not in st.session_state: st.session_state.us_ss_tax_rate = 12.0
# US long-term capital-gains rate that continues to apply to US citizens abroad under
# the treaty savings clause. Slovenia's tax is credited (FTC); the effective rate on a
# post-move gain is max(US LTCG, Slovenia graduated rate). Set retain_us_citizenship
# to False to model renouncing (then only Slovenia's rate applies).
if 'us_ltcg_rate' not in st.session_state: st.session_state.us_ltcg_rate = 15.0
if 'retain_us_citizenship' not in st.session_state: st.session_state.retain_us_citizenship = True
# Share of gross SS that is subject to US income tax (US rule allows up to 85%).
if 'ss_taxable_pct' not in st.session_state: st.session_state.ss_taxable_pct = 85.0
# Under the US-Slovenia treaty SAVINGS CLAUSE, the US continues taxing its citizens'
# SS under normal US rules even while resident in Slovenia. Slovenia (residence
# country) may also tax it, with foreign tax credits mitigating double taxation.
# This input models any NET additional Slovenian tax on gross SS after FTC offset.
# Default 0% assumes the US tax fully credits against Slovenian tax (common outcome).
if 'sl_ss_net_rate' not in st.session_state: st.session_state.sl_ss_net_rate = 0.0


# Real Estate Assumptions 
if 'home_price' not in st.session_state: st.session_state.home_price = 1200000
if 'down_payment' not in st.session_state: st.session_state.down_payment = 150000
if 'mtg_rate' not in st.session_state: st.session_state.mtg_rate = 6.5
if 'tax_rate' not in st.session_state: st.session_state.tax_rate = 2.1 
if 'ann_insurance' not in st.session_state: st.session_state.ann_insurance = 3000
if 'pmi_rate' not in st.session_state: st.session_state.pmi_rate = 0.5 
if 'ann_apprec' not in st.session_state: st.session_state.ann_apprec = 2.0

# Decoupled SS Claim Ages
if 'mike_ss_age' not in st.session_state: st.session_state.mike_ss_age = 67
if 'steph_ss_age' not in st.session_state: st.session_state.steph_ss_age = 70

# SS Macros
if 'mike_future_pct' not in st.session_state: st.session_state.mike_future_pct = 80 
if 'steph_future_pct' not in st.session_state: st.session_state.steph_future_pct = 80 
if 'trust_fund_haircut' not in st.session_state: st.session_state.trust_fund_haircut = 20 
if 'cola_rate' not in st.session_state: st.session_state.cola_rate = 2.1
if 'awi_rate' not in st.session_state: st.session_state.awi_rate = 3.5

# Spending Targets (2026 Dollars)
if 'spend_golden' not in st.session_state: st.session_state.spend_golden = 144000
if 'spend_middle' not in st.session_state: st.session_state.spend_middle = 110000
if 'spend_wind' not in st.session_state: st.session_state.spend_wind = 100000

# Guardrails & Dynamic Gifting
if 'guardrails_enable' not in st.session_state: st.session_state.guardrails_enable = True
if 'floor_golden' not in st.session_state: st.session_state.floor_golden = 85000
if 'floor_middle' not in st.session_state: st.session_state.floor_middle = 85000
if 'floor_wind' not in st.session_state: st.session_state.floor_wind = 100000
if 'slash_trigger' not in st.session_state: st.session_state.slash_trigger = 5.25
if 'recovery_trigger' not in st.session_state: st.session_state.recovery_trigger = 4.25
if 'raise_pct' not in st.session_state: st.session_state.raise_pct = 33.0
if 'dynamic_gift_pct' not in st.session_state: st.session_state.dynamic_gift_pct = 65.0

# Institutional Stress Test Macros
if 'sorr_enable' not in st.session_state: st.session_state.sorr_enable = False
if 'sorr_start_yr' not in st.session_state: st.session_state.sorr_start_yr = 2044
if 'sorr_duration' not in st.session_state: st.session_state.sorr_duration = 2
if 'sorr_return' not in st.session_state: st.session_state.sorr_return = -15.0
if 'fx_enable' not in st.session_state: st.session_state.fx_enable = True
if 'fx_rate' not in st.session_state: st.session_state.fx_rate = 1.30

# Monte Carlo parameters
if 'mc_runs' not in st.session_state: st.session_state.mc_runs = 1000
if 'mc_usd_vol' not in st.session_state: st.session_state.mc_usd_vol = 16.0
if 'mc_eur_vol' not in st.session_state: st.session_state.mc_eur_vol = 14.0
if 'mc_corr' not in st.session_state: st.session_state.mc_corr = 0.80
if 'mc_seed' not in st.session_state: st.session_state.mc_seed = 42
if 'mc_method' not in st.session_state: st.session_state.mc_method = "Historical Block Bootstrap"
if 'mc_block_len' not in st.session_state: st.session_state.mc_block_len = 5
# How to interpret the base-case return input under volatility: as the COMPOUND (CAGR)
# target the portfolio should realize on average (intuitive; engine adds back vol drag),
# or as the raw ARITHMETIC mean of annual returns (realized compounding is then lower).
if 'mc_mean_type' not in st.session_state: st.session_state.mc_mean_type = "Compound (CAGR) target"

# S&P 500 annual total returns (%) 1928-2025 (dividends reinvested; Damodaran/NYU
# Stern series, recent years per Macrotrends). Used by the block-bootstrap engine to
# preserve real-world volatility, fat tails, and crash clustering / sequence risk.
SP500_TOTAL_RETURNS = [
    43.81,-8.30,-25.12,-43.84,-8.64,49.98,-1.19,46.74,31.94,-35.34,29.28,-1.10,-10.67,-12.77,
    19.17,25.06,19.03,35.82,-8.43,5.20,5.70,18.30,30.81,23.68,18.15,-1.21,52.56,32.60,7.44,-10.46,
    43.72,12.06,0.34,26.64,-8.81,22.61,16.42,12.40,-9.97,23.80,10.81,-8.24,3.56,14.22,18.76,-14.31,
    -25.90,37.00,23.83,-6.98,6.51,18.52,31.74,-4.70,20.42,22.34,6.15,31.24,18.49,5.81,16.54,31.48,
    -3.06,30.23,7.49,9.97,1.33,37.20,22.68,33.10,28.34,20.89,-9.03,-11.85,-21.97,28.36,10.74,4.83,
    15.61,5.48,-36.55,25.94,14.82,2.10,15.89,32.15,13.52,1.36,11.96,21.83,-4.38,31.49,18.40,28.71,
    -18.11,26.29,25.02,17.70
]

# MSCI Europe / World annual NET total returns in EUR (%), 2000-2025. 2012-2025 are
# verbatim from MSCI factsheets; 2000-2011 use widely-documented MSCI Europe/World EUR
# annual returns including the 2002 and 2008 crashes. This is independent European-
# denominated data (not a recentered copy of US history). The block-bootstrap pairs the
# same CALENDAR years across the US and EUR series so both sleeves share global crises.
MSCI_EUR_TOTAL_RETURNS = {
    2000:-3.86, 2001:-12.50, 2002:-32.00, 2003:10.74, 2004:6.45, 2005:26.10, 2006:7.95,
    2007:1.66, 2008:-46.00, 2009:25.94, 2010:19.53, 2011:-2.38, 2012:14.05, 2013:21.20,
    2014:19.50, 2015:10.42, 2016:10.73, 2017:7.51, 2018:-4.11, 2019:30.02, 2020:6.33,
    2021:31.07, 2022:-12.78, 2023:19.60, 2024:26.60, 2025:6.77
}
# S&P 500 returns keyed by year (for paired calendar-year sampling with the EUR series).
SP500_BY_YEAR = {1928 + i: SP500_TOTAL_RETURNS[i] for i in range(len(SP500_TOTAL_RETURNS))}

# Bifurcated Glide Path
if 'glide_enable' not in st.session_state: st.session_state.glide_enable = True
if 'glide_start_age' not in st.session_state: st.session_state.glide_start_age = 65
if 'glide_end_age' not in st.session_state: st.session_state.glide_end_age = 85
if 'usd_glide_reduction' not in st.session_state: st.session_state.usd_glide_reduction = 0.1
if 'eur_glide_reduction' not in st.session_state: st.session_state.eur_glide_reduction = 0.055

# Centralized Asset Balances 
if 'asset_balances' not in st.session_state:
    st.session_state.asset_balances = {
        "E*TRADE (Legacy)": 90000,
        "IBKR (Active)": 0,
        "Cornerstone: Trad 401(k)": 300000,
        "Cornerstone: Roth 401(k)": 100000,
        "Cornerstone: Profit Sharing": 50000,
        "OCC: Trad 401(k)": 175000,
        "OCC: Roth 401(k)": 75000,
        "Crypto (Coinbase)": 20000,
        "HSA Pool": 8000,
        "Cash (Slush Fund)": 0 
    }

if 'policy_df' not in st.session_state:
    st.session_state.policy_df = pd.DataFrame({
        "Asset Category": list(st.session_state.asset_balances.keys()),
        "Annual Savings Escalator (%)": [0.0, 0.0, 0.0, 0.0, -20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Current State": [0, 30000, 30000, 0, 15000, 18000, 0, 0, 8300, 0],
        "Northbrook Grind": [0, 15000, 30000, 0, 15000, 18000, 0, 0, 0, 0]
    })

if 'mike_history' not in st.session_state:
    st.session_state.mike_history = {2025: 176100, 2024: 168600, 2023: 160200, 2022: 147000, 2021: 142800, 2020: 137700, 2019: 132900, 2018: 38614, 2017: 51671, 2016: 80887, 2015: 77417, 2014: 71400, 2013: 16536, 2012: 15239, 2011: 9611, 2010: 13001, 2009: 13067, 2008: 9556, 2007: 7731, 2006: 11676, 2005: 6485}
if 'steph_history' not in st.session_state:
    st.session_state.steph_history = {2025: 170000, 2024: 140000, 2023: 100000, 2022: 120000, 2021: 105000, 2020: 100000, 2019: 100000, 2018: 55000, 2017: 35000, 2016: 35000, 2015: 35000, 2014: 35000, 2013: 35000, 2012: 35000, 2011: 5000, 2010: 5000, 2009: 5000, 2008: 5000, 2007: 5000, 2006: 2500, 2005: 2500}

# -----------------------------------------------------------------------------
# CORE SIMULATION ENGINE (RUNS GLOBALLY)
# -----------------------------------------------------------------------------
def calculate_person_benefit(history_dict, current_age, ret_age, claim_age, future_pct, cola, haircut, awi):
    current_year = 2026
    working_yrs = max(0, ret_age - current_age)
    age_60_year = current_year + (60 - current_age)
    age_62_year = current_year + (62 - current_age)
    current_max = 176100 
    indexed_earnings = []
    for yr, val in history_dict.items():
        if yr < age_60_year:
            idx_factor = (1 + (awi / 100)) ** max(0, age_60_year - yr)
            indexed_earnings.append(val * idx_factor)
        else: indexed_earnings.append(val)
    for i in range(working_yrs):
        yr = current_year + i
        projected_max = current_max * ((1 + (awi / 100)) ** (i + 1))
        val = projected_max * (future_pct / 100.0)
        if yr < age_60_year:
            idx_factor = (1 + (awi / 100)) ** (age_60_year - yr)
            indexed_earnings.append(val * idx_factor)
        else: indexed_earnings.append(val)
    indexed_earnings.sort(reverse=True)
    top_35 = (indexed_earnings[:35] + [0]*35)[:35]
    aime = sum(top_35) / (35 * 12)
    # Bend points are set in the year of first eligibility (age 62) and grow with AWI.
    # 2026 bend points are $1,286 and $7,749 (SSA). We grow the 2026 values by AWI
    # to the year this person turns 62.
    bp_growth_years = max(0, age_62_year - 2026)
    bp_multiplier = (1 + (awi / 100)) ** bp_growth_years
    bp1, bp2 = 1286 * bp_multiplier, 7749 * bp_multiplier
    if aime <= bp1: pia = 0.9 * aime
    elif aime <= bp2: pia = (0.9 * bp1) + 0.32 * (aime - bp1)
    else: pia = (0.9 * bp1) + 0.32 * (bp2 - bp1) + 0.15 * (aime - bp2)
    mult = 1.0
    if claim_age > 67: mult += (claim_age - 67) * 0.08
    elif claim_age < 67: mult -= (67 - claim_age) * 0.0667
    cola_years_before_claim = max(0, claim_age - max(62, current_age))
    cola_multiplier = (1 + (cola / 100)) ** cola_years_before_claim
    annual_at_claim = pia * 12 * mult * cola_multiplier * (1 - (haircut / 100))
    timeline = {}
    claim_year = current_year + (claim_age - current_age)
    for yr in range(2026, 2090):
        if yr < claim_year: timeline[yr] = 0
        else: timeline[yr] = annual_at_claim * ((1 + (cola / 100)) ** (yr - claim_year))
    return timeline

def get_ss_timelines(override_m_age=None, override_s_age=None):
    m_age = override_m_age if override_m_age is not None else st.session_state.mike_ss_age
    s_age = override_s_age if override_s_age is not None else st.session_state.steph_ss_age
    mike_ss = calculate_person_benefit(st.session_state.mike_history, st.session_state.current_age, st.session_state.ret_age, m_age, st.session_state.mike_future_pct, st.session_state.cola_rate, st.session_state.trust_fund_haircut, st.session_state.awi_rate)
    steph_ss = calculate_person_benefit(st.session_state.steph_history, st.session_state.current_age, st.session_state.ret_age, s_age, st.session_state.steph_future_pct, st.session_state.cola_rate, st.session_state.trust_fund_haircut, st.session_state.awi_rate)
    return mike_ss, steph_ss

def run_core_simulation(override_m_age=None, override_s_age=None, override_early_draw=None, return_overrides=None):
    # return_overrides: optional dict {year: (usd_return_frac, eur_return_frac)} used by
    # the Monte Carlo engine to inject stochastic annual returns. When None, the model
    # uses the deterministic base-case returns from session state (with glide/SORR).
    MIKE_SS, STEPH_SS = get_ss_timelines(override_m_age, override_s_age)
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    move_yr = 2026 + (st.session_state.move_age - st.session_state.current_age)
    
    policy = st.session_state.policy_df.set_index("Asset Category")
    current_balances = st.session_state.asset_balances.copy()
    current_basis = st.session_state.asset_balances.copy() 
    
    rmd_divisors = {75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4}
    
    bal_matrix, draw_matrix, tax_matrix, cont_matrix, wr_matrix = {}, {}, {}, {}, {}
    asset_rows = list(current_balances.keys())
    
    fx_mult_global = st.session_state.fx_rate if st.session_state.fx_enable else 1.0
    
    # State Tracker for Guardrails & Past Gifts
    spend_level = 1.0 
    cumulative_gifts_tracker = 0.0
    
    def execute_draw(asset, gross_amount_native, statutory_tax_rate, is_brokerage, draws_dict, taxes_dict):
        if gross_amount_native <= 0 or current_balances[asset] <= 0: return 0.0
        actual_gross = min(gross_amount_native, current_balances[asset])
        if is_brokerage:
            gain_ratio = max(0, (current_balances[asset] - current_basis[asset]) / current_balances[asset])
            effective_tax_rate = statutory_tax_rate * gain_ratio 
        else: effective_tax_rate = statutory_tax_rate
        
        actual_tax = actual_gross * effective_tax_rate
        actual_net = actual_gross - actual_tax
        draws_dict[asset] += actual_gross
        taxes_dict[asset] += actual_tax
        
        portion_drawn = actual_gross / current_balances[asset]
        current_basis[asset] -= (current_basis[asset] * portion_drawn)
        current_balances[asset] -= actual_gross
        return actual_net
        
    def pull_net_need(asset, target_eur_need, statutory_tax_rate, is_brokerage, draws_dict, taxes_dict, is_slovenia):
        if target_eur_need <= 0 or current_balances[asset] <= 0: return 0.0
        
        is_eur_asset = asset in ["IBKR (Active)", "Cash (Slush Fund)"]
        asset_fx_mult = 1.0 if is_eur_asset else (fx_mult_global if is_slovenia else 1.0)
        req_net_native = target_eur_need * asset_fx_mult
        
        if is_brokerage and current_balances[asset] > 0:
            gain_ratio = max(0, (current_balances[asset] - current_basis[asset]) / current_balances[asset])
            effective_tax_rate = statutory_tax_rate * gain_ratio 
        else: effective_tax_rate = statutory_tax_rate
            
        req_gross_native = req_net_native / (1 - effective_tax_rate) if effective_tax_rate < 1 else req_net_native
        actual_gross_native = min(req_gross_native, current_balances[asset])
        actual_tax_native = actual_gross_native * effective_tax_rate
        actual_net_native = actual_gross_native - actual_tax_native
        
        draws_dict[asset] += actual_gross_native
        taxes_dict[asset] += actual_tax_native
        
        portion_drawn = actual_gross_native / current_balances[asset]
        current_basis[asset] -= (current_basis[asset] * portion_drawn)
        current_balances[asset] -= actual_gross_native
        
        achieved_eur = actual_net_native / asset_fx_mult
        return achieved_eur

    for yr in range(2026, 2090):
        age = st.session_state.current_age + (yr - 2026)
        
        usd_yr_return = st.session_state.usd_market_return / 100.0
        eur_yr_return = st.session_state.eur_market_return / 100.0
        i_rate = st.session_state.inflation_rate / 100.0

        # Monte Carlo: replace the deterministic base return with this path's stochastic
        # draw for the year. Glide-path de-risking below still applies on top.
        if return_overrides is not None and yr in return_overrides:
            usd_yr_return, eur_yr_return = return_overrides[yr]
        
        if st.session_state.glide_enable and age >= st.session_state.glide_start_age:
            years_in_glide = min(age, st.session_state.glide_end_age) - st.session_state.glide_start_age + 1
            usd_yr_return -= (years_in_glide * (st.session_state.usd_glide_reduction / 100.0))
            eur_yr_return -= (years_in_glide * (st.session_state.eur_glide_reduction / 100.0))
            
        if st.session_state.sorr_enable and (st.session_state.sorr_start_yr <= yr < (st.session_state.sorr_start_yr + st.session_state.sorr_duration)):
            usd_yr_return = st.session_state.sorr_return / 100.0
            eur_yr_return = st.session_state.sorr_return / 100.0

        if yr < start_yr:
            yr_conts = {}
            for asset in current_balances.keys():
                if asset in policy.index:
                    esc = policy.loc[asset, "Annual Savings Escalator (%)"] / 100.0
                    curr_cont = policy.loc[asset, "Current State"] * ((1 + esc)**(yr - 2026))
                    nb_cont = policy.loc[asset, "Northbrook Grind"] * ((1 + esc)**(yr - 2026))
                    cont = curr_cont if yr < st.session_state.nb_start_yr else nb_cont
                else: cont = 0
                
                if asset == "Cash (Slush Fund)": asset_ret = 0.0
                elif asset == "IBKR (Active)": asset_ret = eur_yr_return
                else: asset_ret = usd_yr_return
                
                yr_conts[asset] = cont
                current_balances[asset] = current_balances[asset] * (1 + asset_ret) + cont
                current_basis[asset] += cont 
                
            cont_matrix[yr] = yr_conts
            bal_col = current_balances.copy()
            bal_col["Total Portfolio Balance"] = sum(current_balances.values())
            bal_matrix[yr] = bal_col
            continue
            
        if yr == start_yr:
            if st.session_state.execute_great_reset:
                sweep_val = current_balances["Cornerstone: Roth 401(k)"] + current_balances["OCC: Roth 401(k)"]
                current_balances["IBKR (Active)"] += sweep_val
                current_basis["IBKR (Active)"] += sweep_val 
                current_balances["Cornerstone: Roth 401(k)"] = 0
                current_balances["OCC: Roth 401(k)"] = 0
                current_basis["Cornerstone: Roth 401(k)"] = 0
                current_basis["OCC: Roth 401(k)"] = 0
            
            holding_years = max(0, start_yr - st.session_state.nb_start_yr)
            if holding_years > 0:
                principal = st.session_state.home_price - st.session_state.down_payment
                r_mtg = (st.session_state.mtg_rate / 100) / 12
                n_mtg = 30 * 12
                end_prop_val = st.session_state.home_price * ((1 + (st.session_state.ann_apprec / 100)) ** holding_years)
                pmts_made = holding_years * 12
                if r_mtg > 0: end_mtg_bal = principal * (((1 + r_mtg)**n_mtg - (1 + r_mtg)**pmts_made) / ((1 + r_mtg)**n_mtg - 1))
                else: end_mtg_bal = principal - ((principal / n_mtg) * pmts_made)
                net_proceeds = max(0, end_prop_val - end_mtg_bal - (end_prop_val * 0.06))
            else: net_proceeds = 0
                
            half_proceeds = net_proceeds / 2
            current_balances["IBKR (Active)"] += half_proceeds 
            current_basis["IBKR (Active)"] += half_proceeds 
            current_balances["Cash (Slush Fund)"] += half_proceeds 
            current_basis["Cash (Slush Fund)"] += half_proceeds 

        is_slovenia = (yr >= move_yr)
        current_fx = fx_mult_global if is_slovenia else 1.0
        
        # Apply Returns for the year
        for asset in current_balances.keys():
            if asset == "Cash (Slush Fund)": pass 
            elif asset == "IBKR (Active)": current_balances[asset] *= (1 + eur_yr_return)
            else: current_balances[asset] *= (1 + usd_yr_return)
            
        current_portfolio = sum(current_balances.values())
        
        # 1. Baseline Target Determination
        if age < 70: 
            base_spend_usd = st.session_state.spend_golden
            floor_base_usd = st.session_state.floor_golden
        elif age < 85: 
            base_spend_usd = st.session_state.spend_middle
            floor_base_usd = st.session_state.floor_middle
        else: 
            base_spend_usd = st.session_state.spend_wind
            floor_base_usd = st.session_state.floor_wind
            
        target_lifestyle_usd = base_spend_usd * ((1 + i_rate) ** (yr - 2026))
        floor_usd_inflated = floor_base_usd * ((1 + i_rate) ** (yr - 2026))
        
        ss_m, ss_s = MIKE_SS.get(yr, 0), STEPH_SS.get(yr, 0)
        gross_ss_usd = ss_m + ss_s
        # US tax on SS persists even after the move under the treaty's savings clause
        # (US taxes its citizens under normal US rules regardless of residence).
        taxable_ss_usd = gross_ss_usd * (st.session_state.ss_taxable_pct / 100.0) if gross_ss_usd > 0 else 0.0
        us_ss_tax_usd = taxable_ss_usd * (st.session_state.us_ss_tax_rate / 100.0)
        # Slovenia (residence country) may levy additional tax once resident; model the
        # NET incremental amount after US foreign-tax-credit offset (default 0).
        sl_ss_tax_usd = (gross_ss_usd * (st.session_state.sl_ss_net_rate / 100.0)) if (gross_ss_usd > 0 and is_slovenia) else 0.0
        irs_shadow_tax_usd = us_ss_tax_usd + sl_ss_tax_usd
        net_ss_usd = gross_ss_usd - irs_shadow_tax_usd
        
        # 2. Dynamic Gifting Math (Smoothed Recalibrating Annuity)
        # The forward "terminal pie" projection uses the assumed long-run return
        # (plan_return), NOT the realized/stochastic return for the year. This mirrors how
        # a real planner extrapolates: they don't assume one lucky (or terrible) year will
        # repeat to age 100. The actual portfolio balance still compounds at the realized
        # return (usd_yr_return) elsewhere; only this forward-looking gift sizing is
        # decoupled, which removes the single-year gift jumpiness in Monte Carlo paths.
        base_gift_usd = 0
        if st.session_state.gift_start_age <= age <= st.session_state.gift_end_age:
            plan_return = st.session_state.usd_market_return / 100.0
            n_total = 100 - age
            approx_annual_draw = max(0, target_lifestyle_usd - net_ss_usd)
            
            if plan_return == i_rate:
                fv_draws = approx_annual_draw * n_total * (1+plan_return)**(n_total - 1)
            else:
                fv_draws = approx_annual_draw * (((1+plan_return)**n_total - (1+i_rate)**n_total) / (plan_return - i_rate))
                
            # Add back the FV of past gifts to find the TRUE "No-Gift" Terminal Pie
            fv_past_gifts = cumulative_gifts_tracker * (1 + plan_return)**n_total
            total_fv_nogift = max(0, (current_portfolio * (1+plan_return)**n_total) - fv_draws + fv_past_gifts)
            
            target_total_gift_fv = (st.session_state.dynamic_gift_pct / 100.0) * total_fv_nogift
            remaining_gift_fv_needed = max(0, target_total_gift_fv - fv_past_gifts)
            
            n_rem_gifts = st.session_state.gift_end_age - age + 1
            if n_rem_gifts > 0 and plan_return > 0:
                fvifa = (((1+plan_return)**n_rem_gifts) - 1) / plan_return
                growth_after_gifts = (1+plan_return)**(100 - st.session_state.gift_end_age)
                base_gift_usd = remaining_gift_fv_needed / (fvifa * growth_after_gifts)
                
        # 3. Guardrails Logic
        # Calculate Withdrawal Rate based on Lifestyle Draw only to test against Guardrails
        current_wr = 0.0
        if current_portfolio > 0:
            eval_lifestyle_draw = max(0, (target_lifestyle_usd * spend_level) - net_ss_usd)
            current_wr = eval_lifestyle_draw / current_portfolio
            
            if st.session_state.guardrails_enable:
                if current_wr > (st.session_state.slash_trigger / 100.0):
                    floor_level = floor_usd_inflated / target_lifestyle_usd
                    spend_level = floor_level
                elif current_wr < (st.session_state.recovery_trigger / 100.0) and spend_level < 1.0:
                    # Restoration rate combines the chosen raise with inflation so the
                    # spend_level ratio recovers in real terms (target_lifestyle is
                    # already inflating, so a pure raise_pct would lag by inflation).
                    recovery_rate = (st.session_state.raise_pct + st.session_state.inflation_rate) / 100.0
                    spend_level = min(1.0, spend_level * (1 + recovery_rate))
        else:
            spend_level = 1.0

        # 4. Finalize Actual Targets
        actual_lifestyle_usd = target_lifestyle_usd * spend_level
        actual_gift_usd = base_gift_usd * spend_level
        
        # Capture actual WR for tracking (incorporating newly slashed level if applicable)
        final_eval_draw = max(0, actual_lifestyle_usd - net_ss_usd)
        final_wr = final_eval_draw / current_portfolio if current_portfolio > 0 else 0.0
        wr_matrix[yr] = final_wr
        
        # Update phantom ledger for next year's smoothed calculation
        cumulative_gifts_tracker = cumulative_gifts_tracker * (1 + usd_yr_return) + actual_gift_usd
        
        target_lifestyle_eur = actual_lifestyle_usd / current_fx if not is_slovenia else actual_lifestyle_usd
        gift_need_eur = actual_gift_usd / current_fx
        ss_eur_equivalent = net_ss_usd / current_fx
        
        remaining_eur_need = max(0, (target_lifestyle_eur + gift_need_eur) - ss_eur_equivalent)
        
        draws, taxes = {a: 0.0 for a in asset_rows}, {a: 0.0 for a in asset_rows}
        
        roth_tax_rate = (st.session_state.tax_roth / 100.0) if is_slovenia else 0.0
        pretax_drip_rate = (st.session_state.tax_pretax_base / 100.0) if is_slovenia else 0.12
        pretax_high_rate = (st.session_state.tax_pretax_excess / 100.0) if is_slovenia else 0.22
        ibkr_rate = (st.session_state.tax_cap_gains / 100.0) if is_slovenia else 0.15 

        # Slovenian graduated capital-gains schedule by holding period (years held).
        # 0-5y: 25%, 5-10y: 20%, 10-15y: 15%, >15y: 0%. Applies once resident in
        # Slovenia; before the move, US capital-gains rules apply (taxed on the gain).
        # E*TRADE/Crypto seed lots are treated as acquired in 2026 (per user choice),
        # so holding period = yr - 2026.
        #
        # Residual US tax layer (treaty savings clause): as US citizens, the US still
        # taxes these gains. Slovenia's tax is credited dollar-for-dollar (FTC), so the
        # effective combined rate is max(Slovenia rate, US LTCG rate). When Slovenia is
        # 0% (>15y holding), the FULL US LTCG rate still applies — the sale is NOT
        # tax-free. Set retain_us_citizenship=False to model renouncing (Slovenia only).
        def slovenia_graduated_rate(years_held):
            if years_held > 15: return 0.0
            elif years_held > 10: return 0.15
            elif years_held > 5:  return 0.20
            else:                 return 0.25
        def legacy_cg_rate(years_held):
            if not is_slovenia:
                return st.session_state.us_ltcg_rate / 100.0  # US LTCG pre-move (gain-based)
            sl_rate = slovenia_graduated_rate(years_held)
            if st.session_state.retain_us_citizenship:
                # FTC: owe the higher of the two; Slovenian tax credits against US tax.
                return max(sl_rate, st.session_state.us_ltcg_rate / 100.0)
            return sl_rate
        legacy_lot_rate = legacy_cg_rate(yr - 2026)

        pretax_accounts = ["Cornerstone: Trad 401(k)", "OCC: Trad 401(k)", "Cornerstone: Profit Sharing"]
        pre_req_eur_generated = 0.0
        
        if age >= 75:
            divisor = rmd_divisors.get(min(age, 100), 6.4)
            total_pretax_rmd = sum([current_balances[p] / divisor for p in pretax_accounts if current_balances[p] > 0])
            
            if total_pretax_rmd > 0:
                std_ded_infl = 30000 * ((1 + i_rate) ** (yr - 2026))
                for pretax in pretax_accounts:
                    if current_balances[pretax] > 0:
                        rmd_gross = current_balances[pretax] / divisor
                        prop = rmd_gross / total_pretax_rmd
                        allocated_base = std_ded_infl * prop
                        
                        base_gross = min(rmd_gross, allocated_base)
                        excess_gross = max(0, rmd_gross - base_gross)
                        
                        net1_usd = execute_draw(pretax, base_gross, pretax_drip_rate, False, draws, taxes)
                        net2_usd = execute_draw(pretax, excess_gross, pretax_high_rate, False, draws, taxes)
                        pre_req_eur_generated += (net1_usd + net2_usd) / current_fx
                    
        elif st.session_state.enable_smoothing and age >= 60:
            draw_val = override_early_draw if override_early_draw is not None else st.session_state.target_early_draw
            target_early_gross = draw_val * ((1 + i_rate) ** (yr - 2026))
            
            total_pretax = sum(current_balances[p] for p in pretax_accounts if current_balances[p] > 0)
            if total_pretax > 0 and target_early_gross > 0:
                actual_total_draw = min(target_early_gross, total_pretax)
                allocations = {p: current_balances[p] / total_pretax for p in pretax_accounts if current_balances[p] > 0}
                for pretax, prop in allocations.items():
                    draw_amt = actual_total_draw * prop
                    net_usd = execute_draw(pretax, draw_amt, pretax_drip_rate, False, draws, taxes)
                    pre_req_eur_generated += (net_usd / current_fx)

        if pre_req_eur_generated >= remaining_eur_need:
            excess_eur = pre_req_eur_generated - remaining_eur_need
            current_balances["IBKR (Active)"] += excess_eur
            current_basis["IBKR (Active)"] += excess_eur
            remaining_eur_need = 0 
        else:
            remaining_eur_need -= pre_req_eur_generated
            
            if age >= 60:
                for roth in ["Cornerstone: Roth 401(k)", "OCC: Roth 401(k)"]:
                    remaining_eur_need -= pull_net_need(roth, remaining_eur_need, roth_tax_rate, False, draws, taxes, is_slovenia)
                    
            if age >= 60 and (age >= 75 or not st.session_state.enable_smoothing):
                std_ded_net_equivalent = (30000 * ((1 + i_rate) ** (yr - 2026))) * (1 - pretax_drip_rate)
                drip_target_eur = min(remaining_eur_need, std_ded_net_equivalent / current_fx)
                
                total_pretax = sum(current_balances[p] for p in pretax_accounts if current_balances[p] > 0)
                if total_pretax > 0 and drip_target_eur > 0:
                    allocations = {p: current_balances[p] / total_pretax for p in pretax_accounts if current_balances[p] > 0}
                    for pretax, prop in allocations.items():
                        achieved_eur = pull_net_need(pretax, drip_target_eur * prop, pretax_drip_rate, False, draws, taxes, is_slovenia)
                        remaining_eur_need -= achieved_eur
                    
            # Cash and HSA (qualified) draw tax-free. E*TRADE and Crypto are taxed on
            # the embedded gain: US cap-gains rate before the move, and Slovenia's
            # holding-period schedule after (reaching 0% once held >15 years).
            for brok in ["Cash (Slush Fund)", "HSA Pool"]:
                remaining_eur_need -= pull_net_need(brok, remaining_eur_need, 0.0, False, draws, taxes, is_slovenia)
            for brok in ["E*TRADE (Legacy)", "Crypto (Coinbase)"]:
                remaining_eur_need -= pull_net_need(brok, remaining_eur_need, legacy_lot_rate, True, draws, taxes, is_slovenia)
            remaining_eur_need -= pull_net_need("IBKR (Active)", remaining_eur_need, ibkr_rate, True, draws, taxes, is_slovenia)
            
            if age >= 60:
                total_pretax = sum(current_balances[p] for p in pretax_accounts if current_balances[p] > 0)
                if total_pretax > 0 and remaining_eur_need > 0:
                    allocations = {p: current_balances[p] / total_pretax for p in pretax_accounts if current_balances[p] > 0}
                    target_net_snapshot = remaining_eur_need 
                    for pretax, prop in allocations.items():
                        achieved_eur = pull_net_need(pretax, target_net_snapshot * prop, pretax_high_rate, False, draws, taxes, is_slovenia)
                        remaining_eur_need -= achieved_eur
                
        total_furs_tax = sum(taxes.values())
        total_taxes_paid_usd = total_furs_tax + irs_shadow_tax_usd
        total_gross_portfolio = sum(draws.values())
        
        d_col = draws.copy()
        d_col["Michael's SS"] = ss_m
        d_col["Stephanie's SS"] = ss_s
        d_col["-------------------"] = 0 
        d_col["Actual Lifestyle Spend"] = actual_lifestyle_usd
        d_col["Actual Generational Drip"] = actual_gift_usd
        d_col["Total Gross Drawn"] = total_gross_portfolio + gross_ss_usd
        d_col["IRS Tax on SS (US)"] = -irs_shadow_tax_usd
        d_col["Portfolio Tax (FURS)"] = -total_furs_tax
        d_col["Less: Taxes Paid"] = -total_taxes_paid_usd
        d_col["Net Funded (Lifestyle + Gift)"] = (total_gross_portfolio + gross_ss_usd) - total_taxes_paid_usd
        draw_matrix[yr] = d_col
        
        t_col = {a: (taxes[a] / draws[a] if draws[a] > 0 else 0.0) for a in asset_rows}
        t_col["Michael's SS"], t_col["Stephanie's SS"] = 0.0, 0.0
        t_col["Weighted Average"] = total_taxes_paid_usd / (total_gross_portfolio + gross_ss_usd) if (total_gross_portfolio + gross_ss_usd) > 0 else 0
        tax_matrix[yr] = t_col
        
        b_col = current_balances.copy()
        b_col["Total Portfolio Balance"] = sum(current_balances.values())
        bal_matrix[yr] = b_col

    return pd.DataFrame(bal_matrix), pd.DataFrame(draw_matrix), pd.DataFrame(tax_matrix), pd.DataFrame(cont_matrix), pd.Series(wr_matrix)

# -----------------------------------------------------------------------------
# PAGE ROUTING
# -----------------------------------------------------------------------------
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Navigate", ["1. Executive Dashboard", "2. Pre-Set Asset Ledger & Tax Lots", "3. Investment Policy Editor", "4. Real Estate & Relocation", "5. The Great Reset Simulator", "6. Social Security & Pensions", "7. Cash Flow & Slovenian Drip", "8. Yearly Balances (2026-2089)", "9. Tax Torpedo Optimizer", "10. Institutional Stress Testing", "11. Longevity Optimizer (Guardrails)", "12. Monte Carlo Simulation"])

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Stress Scenarios")
if st.sidebar.button("🌿 Baseline (Reset)"):
    st.session_state.sorr_enable = False
    st.session_state.fx_enable = False
    st.session_state.glide_enable = False
if st.sidebar.button("📉 Bear Market"):
    st.session_state.sorr_enable = True
    st.session_state.sorr_start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    st.session_state.sorr_duration = 3
    st.session_state.sorr_return = -15.0
if st.sidebar.button("💶 Strong Euro"):
    st.session_state.fx_enable = True
    st.session_state.fx_rate = 1.30

# -----------------------------------------------------------------------------
# 1. EXECUTIVE DASHBOARD
# -----------------------------------------------------------------------------
if selection == "1. Executive Dashboard":
    st.header("1. Executive Dashboard")
    c1, c2 = st.columns(2)
    st.session_state.ret_age = c1.number_input("Retirement Age", value=st.session_state.ret_age)
    st.session_state.move_age = c2.number_input("Move to Slovenia Age", value=st.session_state.move_age)

    df_bal, df_draw, _, df_conts, wr_series = run_core_simulation()
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    inf_rate = st.session_state.inflation_rate / 100.0
    
    st.markdown("---")
    
    zero_years = df_bal.columns[df_bal.loc['Total Portfolio Balance'] <= 0]
    if len(zero_years) > 0:
        zero_yr = zero_years.min()
        longevity_age = zero_yr - 2026 + st.session_state.current_age
    else:
        longevity_age = 100
        
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = longevity_age,
        title = {'text': "Projected Portfolio Longevity (Age)"},
        gauge = {
            'axis': {'range': [st.session_state.ret_age, 100]},
            'bar': {'color': "black", 'thickness': 0.25},
            'steps': [
                {'range': [st.session_state.ret_age, 75], 'color': "rgba(255, 99, 71, 0.8)"},   
                {'range': [75, 85], 'color': "rgba(255, 165, 0, 0.8)"},      
                {'range': [85, 95], 'color': "rgba(255, 235, 59, 0.8)"},     
                {'range': [95, 100], 'color': "rgba(144, 238, 144, 0.8)"}    
            ],
        }
    ))
    
    fig_gauge.update_layout(height=150, margin=dict(l=50, r=50, t=50, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader(f"Asset & Tax Lot Balances ({start_yr}-2089)")
    
    milestone_years = [yr for yr in range(start_yr, 2090, 5)]
    if 2089 not in milestone_years: milestone_years.append(2089)
    
    milestone_data = {}
    for yr in milestone_years:
        if yr in df_bal.columns:
            nom_val = df_bal.loc['Total Portfolio Balance', yr]
            real_val = nom_val / ((1 + inf_rate) ** (yr - 2026))
            milestone_data[yr] = {
                "Nominal Balance": f"${nom_val / 1000:,.0f}k",
                "Real Balance (2026 $)": f"${real_val / 1000:,.0f}k"
            }
            
    df_milestones = pd.DataFrame(milestone_data)
    st.dataframe(df_milestones, use_container_width=True)
    
    discount_factors_bal = np.array([(1 + inf_rate) ** (yr - 2026) for yr in df_bal.columns])
    df_bal_real = df_bal.div(discount_factors_bal, axis=1)

    chart_bals = df_bal.drop("Total Portfolio Balance").T
    if start_yr in chart_bals.index:
        chart_bals = chart_bals.loc[start_yr:]
        
    fig1 = go.Figure()
    for col in chart_bals.columns:
        real_asset_bals = df_bal_real.loc[col, start_yr:]
        
        fig1.add_trace(go.Bar(
            x=chart_bals.index, 
            y=chart_bals[col], 
            name=col, 
            yaxis='y1',
            customdata=real_asset_bals.values,
            hovertemplate="<b>%{x}</b><br>Nominal: $%{y:,.0f}<br>Real (2026 $): $%{customdata:,.0f}<extra></extra>"
        ))
        
    real_total_bals = df_bal_real.loc['Total Portfolio Balance', start_yr:]
    fig1.add_trace(go.Scatter(
        x=real_total_bals.index, y=real_total_bals.values, name="Real Portfolio Value (2026 $)",
        mode='lines', line=dict(color='red', width=3), yaxis='y1',
        hovertemplate="<b>%{x}</b><br>Total Real Balance: $%{y:,.0f}<extra></extra>"
    ))

    fig1.update_layout(
        barmode='stack', legend=dict(orientation="h", yanchor="top", y=-0.30, xanchor="center", x=0.5, title=""),
        margin=dict(b=100),
        xaxis=dict(title="Year", tickformat="d"), yaxis=dict(title="Balance ($)"), hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Yearly Income Sources (Real 2026 $)")
    
    if start_yr in df_draw.columns:
        discount_factors_draw = np.array([(1 + inf_rate) ** (yr - 2026) for yr in df_draw.columns])
        df_draw_real = df_draw.div(discount_factors_draw, axis=1)
        
        chart_draws = df_draw_real.loc[:, start_yr:].T
                
        chart_draws['Brokerage & Cash Draw'] = chart_draws['E*TRADE (Legacy)'] + chart_draws['IBKR (Active)'] + chart_draws['Crypto (Coinbase)'] + chart_draws['Cash (Slush Fund)'] + chart_draws['HSA Pool']
        chart_draws['Pre-Tax Draw'] = chart_draws['Cornerstone: Trad 401(k)'] + chart_draws['Cornerstone: Profit Sharing'] + chart_draws['OCC: Trad 401(k)']
        chart_draws['Social Security'] = chart_draws["Michael's SS"] + chart_draws["Stephanie's SS"]
        
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Brokerage & Cash Draw'], name='Brokerage & Cash Draw'), secondary_y=False)
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Pre-Tax Draw'], name='Pre-Tax Draw'), secondary_y=False)
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Social Security'], name='Social Security'), secondary_y=False)
        
        fig2.add_trace(go.Scatter(
            x=chart_draws.index, 
            y=chart_draws['Actual Generational Drip'], 
            name="Amount Given (Generational Drip)", 
            mode='lines+markers', 
            line=dict(color='gold', width=3, dash='dot')
        ), secondary_y=False)
        
        fig2.add_trace(go.Scatter(
            x=chart_draws.index, 
            y=chart_draws['Actual Lifestyle Spend'], 
            name="Post-Tax Lifestyle Spend", 
            mode='lines+markers', 
            line=dict(color='red', width=3)
        ), secondary_y=False)

        # Plot the WR series on the secondary axis
        wr_plot_data = wr_series.loc[start_yr:] * 100
        fig2.add_trace(go.Scatter(
            x=wr_plot_data.index,
            y=wr_plot_data.values,
            name="Gross Withdrawal Rate %",
            mode='lines',
            line=dict(color='#00FF00', width=2)
        ), secondary_y=True)
        
        fig2.update_layout(
            barmode='stack',
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""), 
            hovermode="x unified"
        )
        fig2.update_xaxes(title_text="Year")
        fig2.update_yaxes(title_text="Real Income / Draw (2026 $)", secondary_y=False)
        fig2.update_yaxes(title_text="Withdrawal Rate (%)", secondary_y=True, tickformat='.1f')
        
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("Yearly Savings (Accumulation Phase)")
    
    if start_yr in df_draw.columns:
        gift_nominal = df_draw.loc["Actual Generational Drip", start_yr:]
        gift_real = df_draw_real.loc["Actual Generational Drip", start_yr:]
        
        df_gift_summary = pd.DataFrame({
            "Nominal Annual Gift": gift_nominal,
            "Real Annual Gift (2026 $)": gift_real,
            "Cumulative Nominal Gift": gift_nominal.cumsum(),
            "Cumulative Real Gift": gift_real.cumsum()
        })
        
        df_gift_active = df_gift_summary[df_gift_summary["Nominal Annual Gift"] > 0]
        
        if not df_gift_active.empty:
            st.markdown("**Generational Wealth Transfer Summary**")
            g1, g2 = st.columns(2)
            g1.metric("Total Lifetime Gift (Nominal)", f"${df_gift_summary['Cumulative Nominal Gift'].iloc[-1]:,.0f}")
            g2.metric("Total Lifetime Gift (Real 2026 $)", f"${df_gift_summary['Cumulative Real Gift'].iloc[-1]:,.0f}")
            st.markdown("<br>", unsafe_allow_html=True)
            
    if not df_conts.empty:
        df_conts_t = df_conts.T
        
        df_conts_t['Total Nominal Savings'] = df_conts_t.sum(axis=1)
        df_conts_t['Total Real Savings (2026 $)'] = df_conts_t['Total Nominal Savings'] / ((1 + inf_rate) ** (df_conts_t.index - 2026))
        
        tot_nom = df_conts_t['Total Nominal Savings'].sum()
        tot_real = df_conts_t['Total Real Savings (2026 $)'].sum()
        
        st.markdown("**Pre-Retirement Contribution Summary**")
        c1, c2 = st.columns(2)
        c1.metric("Total Lifetime Savings (Nominal)", f"${tot_nom:,.0f}")
        c2.metric("Total Lifetime Savings (Real 2026 $)", f"${tot_real:,.0f}")
        
        plot_cols = [c for c in df_conts_t.columns if c not in ['Total Nominal Savings', 'Total Real Savings (2026 $)'] and df_conts_t[c].sum() > 0]
        
        fig3 = px.bar(df_conts_t, x=df_conts_t.index, y=plot_cols, barmode='stack')
        
        fig3.add_trace(go.Scatter(
            x=df_conts_t.index, 
            y=df_conts_t['Total Real Savings (2026 $)'], 
            name="Total Real Savings (2026 $)", 
            mode='lines+markers', 
            line=dict(color='gold', width=4)
        ))
        
        fig3.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""), xaxis_title="Year", yaxis_title="Savings / Contributions ($)", hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("You are already in or past the retirement phase. No pre-retirement savings projected.")

# -----------------------------------------------------------------------------
# 2. PRE-SET ASSET Ledger & Tax Lots
# -----------------------------------------------------------------------------
elif selection == "2. Pre-Set Asset Ledger & Tax Lots":
    st.header("2. Pre-Set Asset Ledger & Tax Lots")
    st.session_state.current_age = st.selectbox("Current Age", options=list(range(35, 70)), index=list(range(35, 70)).index(st.session_state.current_age))
    df_assets = pd.DataFrame(list(st.session_state.asset_balances.items()), columns=["Asset Ledger / Tax Lot", "Current Balance (USD)"])
    edited_df = st.data_editor(df_assets, use_container_width=True, hide_index=True)
    st.session_state.asset_balances = dict(zip(edited_df["Asset Ledger / Tax Lot"], edited_df["Current Balance (USD)"]))

# -----------------------------------------------------------------------------
# 3. INVESTMENT POLICY EDITOR
# -----------------------------------------------------------------------------
elif selection == "3. Investment Policy Editor":
    st.header("3. Investment Policy Editor")
    c1, c2, c3, c4 = st.columns(4)
    st.session_state.inflation_rate = c1.number_input("Annual Inflation (%)", value=st.session_state.inflation_rate, step=0.1)
    st.session_state.usd_market_return = c2.number_input("USD Asset Base Return (%)", value=st.session_state.usd_market_return, step=0.1)
    st.session_state.eur_market_return = c3.number_input("EUR Asset Base Return (%)", value=st.session_state.eur_market_return, step=0.1)
    st.session_state.nb_start_yr = c4.number_input("Transition to Northbrook (Year)", value=st.session_state.nb_start_yr)
    
    st.markdown("---")
    st.subheader("Lifetime Tax Smoothing Optimizer")
    s1, s2 = st.columns(2)
    st.session_state.enable_smoothing = s1.toggle("Enable Strategic Pre-Tax Depletion (Ages 60-74)", value=st.session_state.enable_smoothing)
    if st.session_state.enable_smoothing:
        st.session_state.target_early_draw = s2.number_input("Target Annual Pre-Tax Draw (Nominal $)", value=st.session_state.target_early_draw, step=5000)
        
    st.markdown("---")
    st.subheader("Tax Assumptions (%)")
    t1, t2, t3, t4, t5 = st.columns(5)
    st.session_state.tax_roth = t1.number_input("Roth Trap Rate", value=st.session_state.tax_roth, step=1.0)
    st.session_state.tax_pretax_base = t2.number_input("Base Pre-Tax Rate", value=st.session_state.tax_pretax_base, step=1.0)
    st.session_state.tax_pretax_excess = t3.number_input("Excess Pre-Tax Rate", value=st.session_state.tax_pretax_excess, step=1.0)
    st.session_state.tax_cap_gains = t4.number_input("Capital Gains Rate", value=st.session_state.tax_cap_gains, step=1.0)
    st.session_state.us_ss_tax_rate = t5.number_input("US SS Tax Rate", value=st.session_state.us_ss_tax_rate, step=1.0)

    s1, s2 = st.columns(2)
    st.session_state.ss_taxable_pct = s1.number_input("US Taxable Share of SS (%)", value=st.session_state.ss_taxable_pct, step=5.0, help="Max 85% under US rules. US taxes this share even after moving (treaty savings clause).")
    st.session_state.sl_ss_net_rate = s2.number_input("Slovenia Net SS Tax Rate (%)", value=st.session_state.sl_ss_net_rate, step=1.0, help="Net additional Slovenian tax on gross SS after US foreign-tax-credit offset, applied only after the move. Default 0 assumes US tax fully credits.")

    st.markdown("**Cross-Border Capital Gains (E\\*TRADE / Crypto legacy lots)**")
    cg1, cg2 = st.columns(2)
    st.session_state.us_ltcg_rate = cg1.number_input("US Long-Term Cap-Gains Rate (%)", value=st.session_state.us_ltcg_rate, step=1.0, help="Applies to US citizens even abroad (savings clause). Effective post-move rate = max(this, Slovenia's holding-period rate). When Slovenia is 0% (>15y), the full US rate still applies via residual US tax.")
    st.session_state.retain_us_citizenship = cg2.toggle("Retain US Citizenship", value=st.session_state.retain_us_citizenship, help="If off, models renouncing US citizenship: only Slovenia's graduated rate applies (so >15y holdings become truly 0%).")
    
    st.markdown("---")
    st.subheader("Phase Contribution Policies")
    edited_policy = st.data_editor(st.session_state.policy_df, use_container_width=True, hide_index=True)
    st.session_state.policy_df = edited_policy

    st.markdown("---")
    st.subheader("Retirement Phase Lifestyle Targets (Today's 2026 Dollars)")
    r1, r2, r3 = st.columns(3)
    st.session_state.spend_golden = r1.number_input("Golden Years (< 70)", value=st.session_state.spend_golden, step=5000)
    st.session_state.spend_middle = r2.number_input("Middle Phase (70-85)", value=st.session_state.spend_middle, step=5000)
    st.session_state.spend_wind = r3.number_input("Wind Down Years (85-100)", value=st.session_state.spend_wind, step=5000)

# -----------------------------------------------------------------------------
# 4. REAL ESTATE & RELOCATION
# -----------------------------------------------------------------------------
elif selection == "4. Real Estate & Relocation":
    st.header("4. Real Estate & Relocation")
    c1, c2 = st.columns(2)
    st.session_state.home_price = c1.number_input("Home Purchase Price ($)", value=st.session_state.home_price, step=25000)
    st.session_state.down_payment = c2.number_input("Down Payment ($)", value=st.session_state.down_payment, step=10000)
    
    c3, c4, c5, c6 = st.columns(4)
    st.session_state.mtg_rate = c3.number_input("Mortgage Rate (%)", value=st.session_state.mtg_rate, step=0.1)
    st.session_state.tax_rate = c4.number_input("Property Tax Rate (%)", value=st.session_state.tax_rate, step=0.1)
    st.session_state.ann_insurance = c5.number_input("Annual Home Insurance ($)", value=st.session_state.ann_insurance, step=100)
    st.session_state.pmi_rate = c6.number_input("PMI Rate (%)", value=st.session_state.pmi_rate, step=0.1)
    
    principal = st.session_state.home_price - st.session_state.down_payment
    r = (st.session_state.mtg_rate / 100) / 12
    n = 30 * 12 
    if r > 0: monthly_pi = principal * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else: monthly_pi = principal / n
    monthly_tax = (st.session_state.home_price * (st.session_state.tax_rate / 100)) / 12
    monthly_ins = st.session_state.ann_insurance / 12
    ltv = principal / st.session_state.home_price
    monthly_pmi = (principal * (st.session_state.pmi_rate / 100)) / 12 if ltv > 0.80 else 0.0
    total_piti = monthly_pi + monthly_tax + monthly_ins + monthly_pmi
    
    st.markdown("### Estimated Monthly Payment (PITIA)")
    piti_col1, piti_col2, piti_col3, piti_col4, piti_col5 = st.columns(5)
    piti_col1.metric("Principal & Interest", f"${monthly_pi:,.0f}")
    piti_col2.metric("Property Taxes", f"${monthly_tax:,.0f}")
    piti_col3.metric("Insurance", f"${monthly_ins:,.0f}")
    piti_col4.metric("PMI", f"${monthly_pmi:,.0f}")
    piti_col5.metric("Total Monthly", f"${total_piti:,.0f}")
    
    st.markdown("---")
    ret_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    st.subheader(f"Northbrook Liquidation (Year: {ret_yr})")
    st.session_state.ann_apprec = st.number_input("Annual Property Appreciation (%)", value=st.session_state.ann_apprec, step=0.1)
    
    holding_years = max(0, ret_yr - st.session_state.nb_start_yr)
    if holding_years > 0:
        end_prop_val = st.session_state.home_price * ((1 + (st.session_state.ann_apprec / 100)) ** holding_years)
        pmts_made = holding_years * 12
        if r > 0: end_mtg_bal = principal * (((1 + r)**n - (1 + r)**pmts_made) / ((1 + r)**n - 1))
        else: end_mtg_bal = principal - (monthly_pi * pmts_made)
        net_proceeds = max(0, end_prop_val - end_mtg_bal - (end_prop_val * 0.06))
    else:
        end_prop_val, end_mtg_bal, net_proceeds = st.session_state.home_price, principal, 0
        
    st.write(f"**Holding Period:** {holding_years} Years")
    st.write(f"**Projected Sale Price:** ${end_prop_val:,.0f}")
    st.write(f"**Ending Mortgage Balance:** ${end_mtg_bal:,.0f}")
    st.metric("Net Property Sale Proceeds", f"${net_proceeds:,.0f}")
    st.success(f"**Allocation A:** ${net_proceeds/2:,.0f} to Cash (Slush Fund) Ledger.")
    st.success(f"**Allocation B:** ${net_proceeds/2:,.0f} immediately invested into IBKR (Active) Ledger.")

# -----------------------------------------------------------------------------
# 5. THE GREAT RESET SIMULATOR
# -----------------------------------------------------------------------------
elif selection == "5. The Great Reset Simulator":
    st.header("5. The Great Reset Simulator")
    st.session_state.execute_great_reset = st.toggle("Enable Great Reset in Cash Flow Model", value=st.session_state.execute_great_reset)
    st.caption("Note: The pre-move Roth 401(k) sweep generates **no US tax** because qualified Roth distributions are US-tax-exempt — not because of any capital-gains rate. Any pre-move sales of taxable lots (E\\*TRADE/Crypto) in the drawdown engine are taxed at the US long-term cap-gains rate on the gain, never 0%.")
    reset_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    
    if st.session_state.execute_great_reset:
        reset_assets = ["Crypto (Coinbase)", "IBKR (Active)", "Cornerstone: Roth 401(k)", "OCC: Roth 401(k)"]
        market_ret = st.session_state.usd_market_return / 100.0 
        policy = st.session_state.policy_df.set_index("Asset Category")
        projected_data = []
        for asset in reset_assets:
            bal = st.session_state.asset_balances.get(asset, 0)
            basis = bal 
            if asset in policy.index:
                esc = policy.loc[asset, "Annual Savings Escalator (%)"] / 100.0
                curr_cont = policy.loc[asset, "Current State"]
                nb_cont = policy.loc[asset, "Northbrook Grind"]
            else:
                esc, curr_cont, nb_cont = 0, 0, 0
            for y in range(2026, reset_yr):
                cont = curr_cont if y < st.session_state.nb_start_yr else nb_cont
                bal = bal * (1 + market_ret) + cont
                basis += cont
                curr_cont *= (1 + esc)
                nb_cont *= (1 + esc)
            projected_data.append([asset, basis, bal])
        df_reset = pd.DataFrame(projected_data, columns=["Asset Bucket", "Projected Cost Basis", "Projected Market Value at Reset"])
        df_reset['Realized US Gain'] = np.where(df_reset['Asset Bucket'].str.contains("Roth"), 0, df_reset['Projected Market Value at Reset'] - df_reset['Projected Cost Basis'])
        df_reset['New Stepped-Up Basis / Protected Cash'] = df_reset['Projected Market Value at Reset']
        st.dataframe(df_reset.style.format({"Projected Cost Basis": "${:,.0f}", "Projected Market Value at Reset": "${:,.0f}", "Realized US Gain": "${:,.0f}", "New Stepped-Up Basis / Protected Cash": "${:,.0f}"}), use_container_width=True)

# -----------------------------------------------------------------------------
# 6. SOCIAL SECURITY & PENSIONS
# -----------------------------------------------------------------------------
elif selection == "6. Social Security & Pensions":
    st.header("6. Actuarial Social Security Engine")
    st.sidebar.header("Earnings Assumptions")
    st.session_state.mike_future_pct = st.sidebar.slider("Michael: Future % of Max Wage", 0, 100, st.session_state.mike_future_pct, 10)
    st.session_state.steph_future_pct = st.sidebar.slider("Stephanie: Future % of Max Wage", 0, 100, st.session_state.steph_future_pct, 10)

    st.sidebar.header("Retirement Timing")
    st.session_state.mike_ss_age = st.sidebar.slider("Michael Claim Age", 62, 70, st.session_state.mike_ss_age)
    st.session_state.steph_ss_age = st.sidebar.slider("Stephanie Claim Age", 62, 70, st.session_state.steph_ss_age)
    
    st.sidebar.header("Actuarial Macros")
    st.session_state.awi_rate = st.sidebar.number_input("Average Wage Index (AWI) %", value=st.session_state.awi_rate, step=0.1)
    st.session_state.cola_rate = st.sidebar.number_input("Annual COLA (%)", value=st.session_state.cola_rate, step=0.1)
    st.session_state.trust_fund_haircut = st.sidebar.slider("Trust Fund Haircut (%)", 0, 50, st.session_state.trust_fund_haircut, 5)

    MIKE_SS, STEPH_SS = get_ss_timelines()
    m_claim_yr = 2026 + (st.session_state.mike_ss_age - st.session_state.current_age)
    s_claim_yr = 2026 + (st.session_state.steph_ss_age - st.session_state.current_age)
    
    # Calculate Real 2026 Dollars based on claim year and inflation rate
    inf_rate = st.session_state.inflation_rate / 100.0
    m_real_ss = MIKE_SS[m_claim_yr] / ((1 + inf_rate) ** (m_claim_yr - 2026))
    s_real_ss = STEPH_SS[s_claim_yr] / ((1 + inf_rate) ** (s_claim_yr - 2026))
    
    c1, c2 = st.columns(2)
    c1.success(f"**Michael (Starts {m_claim_yr})**\n\nNominal: **${MIKE_SS[m_claim_yr]:,.0f}** / yr\n\nReal (2026 $): **${m_real_ss:,.0f}** / yr")
    c2.success(f"**Stephanie (Starts {s_claim_yr})**\n\nNominal: **${STEPH_SS[s_claim_yr]:,.0f}** / yr\n\nReal (2026 $): **${s_real_ss:,.0f}** / yr")

# -----------------------------------------------------------------------------
# 7. CASH FLOW & SLOVENIAN DRIP
# -----------------------------------------------------------------------------
elif selection == "7. Cash Flow & Slovenian Drip":
    st.header("7. Cash Flow & Multi-Period Optimization Engine")
    _, df_draw, df_tax, _, _ = run_core_simulation()
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    
    st.markdown("---")
    st.subheader("1a. Yearly Future Projected Draw by Asset Ledger (Nominal $)")
    st.dataframe(df_draw.style.format("${:,.0f}"), use_container_width=True, height=765)
    
    st.markdown("---")
    st.subheader("1b. Yearly Future Projected Draw by Asset Ledger (Real 2026 $)")
    
    inf_rate = st.session_state.inflation_rate / 100.0
    discount_factors = np.array([(1 + inf_rate) ** (yr - 2026) for yr in df_draw.columns])
    df_draw_real = df_draw.div(discount_factors, axis=1)
    
    st.dataframe(df_draw_real.style.format("${:,.0f}"), use_container_width=True, height=765)
    
    st.markdown("---")
    st.subheader("2. Yearly Effective Tax Rate")
    
    df_tax_t = df_tax.T
    if start_yr in df_tax_t.index:
        tax_chart_data = df_tax_t.loc[start_yr:].copy()
        fig_tax = px.line(tax_chart_data, y='Weighted Average', markers=True)
        fig_tax.layout.yaxis.tickformat = ',.1%'
        fig_tax.update_layout(xaxis_title="Year", yaxis_title="Effective Tax Rate (%)", showlegend=False)
        st.plotly_chart(fig_tax, use_container_width=True)
        
    st.dataframe(df_tax.style.format("{:.1%}"), use_container_width=True, height=500)

    st.markdown("---")
    st.subheader("3. Generational Wealth Transfer (Giving While Living) Summary")
    
    if start_yr in df_draw.columns:
        gift_nominal = df_draw.loc["Actual Generational Drip", start_yr:]
        gift_real = df_draw_real.loc["Actual Generational Drip", start_yr:]
        
        df_gift_summary = pd.DataFrame({
            "Nominal Annual Gift": gift_nominal,
            "Real Annual Gift (2026 $)": gift_real,
            "Cumulative Nominal Gift": gift_nominal.cumsum(),
            "Cumulative Real Gift": gift_real.cumsum()
        })
        
        df_gift_active = df_gift_summary[df_gift_summary["Nominal Annual Gift"] > 0]
        
        if not df_gift_active.empty:
            c1, c2 = st.columns(2)
            c1.metric("Total Lifetime Gift (Nominal)", f"${df_gift_summary['Cumulative Nominal Gift'].iloc[-1]:,.0f}")
            c2.metric("Total Lifetime Gift (Real 2026 $)", f"${df_gift_summary['Cumulative Real Gift'].iloc[-1]:,.0f}")
            
            fig_gift = px.bar(df_gift_summary, y=["Nominal Annual Gift", "Real Annual Gift (2026 $)"], barmode='group')
            fig_gift.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""), xaxis_title="Year", yaxis_title="Gift Amount ($)")
            st.plotly_chart(fig_gift, use_container_width=True)
            
            st.dataframe(df_gift_active.style.format("${:,.0f}"), use_container_width=True)
        else:
            st.info("No generational gifting is projected under the current guardrail and timing parameters.")

# -----------------------------------------------------------------------------
# 8. YEARLY BALANCES (2026-2089)
# -----------------------------------------------------------------------------
elif selection == "8. Yearly Balances (2026-2089)":
    st.header("8. Yearly Balances (2026-2089)")
    df_bal, _, _, _, _ = run_core_simulation()
    chart_bals = df_bal.drop("Total Portfolio Balance").T
    fig3 = px.bar(chart_bals, barmode='stack')
    fig3.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""), xaxis_title="", yaxis_title="Balance ($)")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("---")
    st.subheader("Detailed Ledger")
    st.dataframe(df_bal.style.format("${:,.0f}"), use_container_width=True, height=450)

# -----------------------------------------------------------------------------
# 9. TAX TORPEDO OPTIMIZER (GRID SEARCH)
# -----------------------------------------------------------------------------
elif selection == "9. Tax Torpedo Optimizer":
    st.header("9. Tax Torpedo Optimizer")
    st.markdown("Run a grid search to find the mathematically optimal combination of **Social Security Claim Age** and **Strategic Pre-Tax Depletion**.")
    
    if st.button("Run Optimization Matrix"):
        with st.spinner("Running thousands of actuarial permutations..."):
            results = []
            ss_ages = [62, 63, 64, 65, 66, 67, 68, 69, 70]
            draw_amounts = [0, 50000, 100000, 125000, 150000, 175000, 200000]
            
            for ss in ss_ages:
                for draw in draw_amounts:
                    _, df_draw, _, _, _ = run_core_simulation(override_m_age=ss, override_s_age=ss, override_early_draw=draw)
                    df_draw_t = df_draw.T
                    
                    if 'Less: Taxes Paid' in df_draw_t.columns:
                        valid_years = [y for y in df_draw_t.index if y <= 2079]
                        total_tax = df_draw_t.loc[valid_years, 'Less: Taxes Paid'].sum() * -1
                    else:
                        total_tax = 0
                    
                    results.append({
                        "Joint SS Claim Age": ss, 
                        "Early Pre-Tax Draw ($)": draw, 
                        "Lifetime Taxes ($)": total_tax
                    })
            
            df_results = pd.DataFrame(results)
            grid = df_results.pivot(index="Joint SS Claim Age", columns="Early Pre-Tax Draw ($)", values="Lifetime Taxes ($)")
            
            fig4 = px.imshow(
                grid, 
                text_auto='.3s', 
                color_continuous_scale="RdYlGn_r", 
                aspect="auto", 
                labels=dict(x="Annual Early Pre-Tax Draw ($)", y="Joint SS Claim Age", color="Lifetime Taxes ($)")
            )
            fig4.update_layout(title="Total Lifetime Taxes Paid up to Age 90 (Dark Green = Lowest Tax Burden)")
            st.plotly_chart(fig4, use_container_width=True)
            
            min_row = df_results.loc[df_results['Lifetime Taxes ($)'].idxmin()]
            st.success(f"**Optimal Strategy Found!**\n\nTo minimize lifetime taxes to **${min_row['Lifetime Taxes ($)']:,.0f}**, claim Social Security at **Age {int(min_row['Joint SS Claim Age'])}** and set your strategic early pre-tax drawdown to **${min_row['Early Pre-Tax Draw ($)']:,.0f} / year**.")

# -----------------------------------------------------------------------------
# 10. INSTITUTIONAL STRESS TESTING
# -----------------------------------------------------------------------------
elif selection == "10. Institutional Stress Testing":
    st.header("10. Institutional Stress Testing")
    st.markdown("Stress test your portfolio's survivability against Sequence of Returns Risk, Currency Volatility, and asset allocation Glide Paths.")
    
    st.markdown("---")
    st.subheader("A. Dynamic Asset Allocation (Bifurcated Glide Path)")
    st.markdown("Simulate moving your portfolio from aggressive equities to conservative bonds as you age by dynamically lowering your expected rate of return over time.")
    g1, g2, g3 = st.columns(3)
    st.session_state.glide_enable = g1.toggle("Enable Glide Path", value=st.session_state.glide_enable)
    st.session_state.glide_start_age = g2.number_input("Start De-Risking Age", value=st.session_state.glide_start_age)
    st.session_state.glide_end_age = g3.number_input("End De-Risking Age (Floor)", value=st.session_state.glide_end_age)
    
    g4, g5 = st.columns(2)
    st.session_state.usd_glide_reduction = g4.number_input("Yearly Reduction in USD Return (%)", value=st.session_state.usd_glide_reduction, step=0.001, format="%.3f")
    st.session_state.eur_glide_reduction = g5.number_input("Yearly Reduction in EUR Return (%)", value=st.session_state.eur_glide_reduction, step=0.001, format="%.3f")

    if st.session_state.glide_enable:
        total_usd_drop = (st.session_state.glide_end_age - st.session_state.glide_start_age + 1) * st.session_state.usd_glide_reduction
        total_eur_drop = (st.session_state.glide_end_age - st.session_state.glide_start_age + 1) * st.session_state.eur_glide_reduction
        st.info(f"**Status:** Active. By age {st.session_state.glide_end_age}, your USD return will drop to **{st.session_state.usd_market_return - total_usd_drop:.3f}%** and your EUR return will drop to **{st.session_state.eur_market_return - total_eur_drop:.3f}%**.")

    st.markdown("---")
    st.subheader("B. Sequence of Returns Risk (SORR)")
    st.markdown("Simulate a devastating, multi-year market crash at a specific point in time to see if early portfolio damage bankrupts your long-term plan.")
    s1, s2, s3 = st.columns(3)
    st.session_state.sorr_enable = s1.toggle("Enable Market Crash", value=st.session_state.sorr_enable)
    st.session_state.sorr_start_yr = s2.number_input("Crash Start Year", value=st.session_state.sorr_start_yr)
    st.session_state.sorr_duration = s3.number_input("Crash Duration (Years)", value=st.session_state.sorr_duration)
    st.session_state.sorr_return = st.number_input("Annual Return During Crash (%)", value=st.session_state.sorr_return, step=1.0)
    
    st.markdown("---")
    st.subheader("C. Foreign Exchange Risk (USD/EUR)")
    st.markdown("If your lifestyle targets are effectively priced in Euros, a weakening US Dollar forces your portfolio to bleed faster to afford the same lifestyle. *Note: IBKR and Cash ledgers are exempt from this drag as they represent Synthetic Euro Hedges.*")
    f1, f2 = st.columns(2)
    st.session_state.fx_enable = f1.toggle("Enable Currency Drag", value=st.session_state.fx_enable)
    st.session_state.fx_rate = f2.number_input("Assumed EUR/USD Exchange Rate (e.g. 1.15 = $1.15 USD per €1.00)", value=st.session_state.fx_rate, step=0.05)

    if st.button("Run Stress Test Diagnostics"):
        with st.spinner("Stress testing portfolio parameters..."):
            df_bal, _, _, _, _ = run_core_simulation()
            final_yr = 2089
            if final_yr in df_bal.columns and df_bal.loc['Total Portfolio Balance', final_yr] > 0:
                final_val = df_bal.loc['Total Portfolio Balance', final_yr]
                st.success(f"**Test Passed:** Your portfolio survived the stress tests. Projected nominal terminal wealth at Age 100 is **${final_val / 1000000:,.1f} Million**.")
            else:
                st.error("**Test Failed:** Your portfolio was depleted before age 100 under these stress conditions.")

# -----------------------------------------------------------------------------
# 11. LONGEVITY OPTIMIZER (GUARDRAILS)
# -----------------------------------------------------------------------------
elif selection == "11. Longevity Optimizer (Guardrails)":
    st.header("11. Longevity Optimizer (Guyton-Klinger Guardrails)")
    st.markdown("This engine mathematically protects your portfolio from a death spiral. If your Withdrawal Rate spikes due to a crash, it dynamically slashes discretionary spending down to your absolute minimum floors. When the market recovers, it provides annual 10% 'raises' back to your original baseline. Generational Gifting automatically scales up or down in exact proportion to your lifestyle sacrifices.")
    
    c1, c2 = st.columns(2)
    st.session_state.guardrails_enable = c1.toggle("Enable Dynamic Guardrails", value=st.session_state.guardrails_enable)
    
    st.markdown("---")
    st.subheader("1. The Ironclad Floor (Absolute Minimum Spend in 2026 $)")
    f1, f2, f3 = st.columns(3)
    st.session_state.floor_golden = f1.number_input("Golden Years Floor (< 70)", value=st.session_state.floor_golden, step=5000)
    st.session_state.floor_middle = f2.number_input("Middle Phase Floor (70-85)", value=st.session_state.floor_middle, step=5000)
    st.session_state.floor_wind = f3.number_input("Wind Down Floor (85-100)", value=st.session_state.floor_wind, step=5000)

    st.markdown("---")
    st.subheader("2. Actuarial Triggers")
    t1, t2, t3 = st.columns(3)
    st.session_state.slash_trigger = t1.number_input("Slash Trigger (Withdrawal Rate %)", value=st.session_state.slash_trigger, step=0.1)
    st.session_state.recovery_trigger = t2.number_input("Recovery Trigger (Withdrawal Rate %)", value=st.session_state.recovery_trigger, step=0.1)
    st.session_state.raise_pct = t3.number_input("Annual Recovery Raise (%)", value=st.session_state.raise_pct, step=1.0)
    
    st.markdown("---")
    st.subheader("3. Dynamic Gifting Calibration")
    st.markdown("Every year, the engine projects what your Terminal Portfolio Value at Age 100 *would be* if you stopped gifting today. It targets gifting a total equivalent to your chosen percentage of that terminal value.")
    st.session_state.dynamic_gift_pct = st.number_input("Target Lifetime Gift Value (% of Projected Terminal Portfolio)", value=st.session_state.dynamic_gift_pct, step=5.0)
    st.session_state.gift_start_age = st.number_input("Age to Start Gifting", value=st.session_state.gift_start_age, step=1)
    st.session_state.gift_end_age = st.number_input("Age to End Gifting", value=st.session_state.gift_end_age, step=1)

# -----------------------------------------------------------------------------
# 12. MONTE CARLO SIMULATION
# -----------------------------------------------------------------------------
elif selection == "12. Monte Carlo Simulation":
    st.header("12. Monte Carlo Simulation")
    st.markdown(
        "Replaces the single fixed-return assumption with thousands of randomized market "
        "paths to estimate the **probability** your plan survives, rather than one "
        "deterministic outcome. Sequence-of-returns risk emerges naturally from the random "
        "ordering of good and bad years."
    )

    st.session_state.mc_method = st.radio(
        "Return-Generation Method",
        ["Historical Block Bootstrap", "Correlated Normal (Parametric)"],
        index=0 if st.session_state.mc_method == "Historical Block Bootstrap" else 1,
        horizontal=True,
        help="Block Bootstrap resamples contiguous runs of real S&P 500 history (1928-2025), "
             "preserving fat tails, volatility clustering, and momentum. Normal draws are "
             "smoother and understate crash risk."
    )

    st.session_state.mc_mean_type = st.radio(
        "Interpret base-case return as",
        ["Compound (CAGR) target", "Arithmetic mean"],
        index=0 if st.session_state.mc_mean_type == "Compound (CAGR) target" else 1,
        horizontal=True,
        help="Compound: the engine adds volatility drag back so your portfolio's realized "
             "average compound growth centers on your input (intuitive). Arithmetic: your "
             "input is the simple average of annual returns, so realized compounding lands "
             "lower because of volatility drag."
    )

    m1, m2, m3 = st.columns(3)
    st.session_state.mc_runs = m1.number_input("Number of Simulations", value=st.session_state.mc_runs, min_value=100, max_value=5000, step=100)
    st.session_state.mc_seed = m2.number_input("Random Seed (reproducibility)", value=st.session_state.mc_seed, step=1)

    if st.session_state.mc_method == "Historical Block Bootstrap":
        st.session_state.mc_block_len = m3.number_input(
            "Block Length (years)", value=st.session_state.mc_block_len, min_value=1, max_value=20, step=1,
            help="Length of each contiguous historical run sampled. Longer blocks preserve more "
                 "serial structure (e.g. multi-year bear markets); 1 = i.i.d. resampling."
        )
        st.info(
            f"Resamples {st.session_state.mc_block_len}-year blocks of paired calendar years "
            f"(2000-2025) from real S&P 500 (USD) and MSCI Europe (EUR) total-return history, "
            f"then **recenters** each sleeve to your base-case returns "
            f"(**USD {st.session_state.usd_market_return:.1f}%**, **EUR {st.session_state.eur_market_return:.1f}%**). "
            "Each sleeve uses its own independent historical data, but the same calendar years "
            "are applied to both so global crises (2002, 2008, 2022) hit both sleeves together "
            "(realized correlation ~0.88)."
        )
    else:
        st.session_state.mc_corr = m3.number_input("USD/EUR Return Correlation", value=st.session_state.mc_corr, min_value=-1.0, max_value=1.0, step=0.05)
        m4, m5 = st.columns(2)
        st.session_state.mc_usd_vol = m4.number_input("USD Annual Volatility (Std Dev %)", value=st.session_state.mc_usd_vol, step=1.0)
        st.session_state.mc_eur_vol = m5.number_input("EUR Annual Volatility (Std Dev %)", value=st.session_state.mc_eur_vol, step=1.0)
        st.info(
            f"Draws correlated normal returns centered on your base case "
            f"(**USD {st.session_state.usd_market_return:.1f}%**, **EUR {st.session_state.eur_market_return:.1f}%**). "
            "Glide-path de-risking still applies on top; deterministic SORR is ignored here."
        )

    if st.button("Run Monte Carlo"):
        inf_rate = st.session_state.inflation_rate / 100.0
        years = list(range(2026, 2090))
        n_years = len(years)
        n_runs = int(st.session_state.mc_runs)
        usd_mean = st.session_state.usd_market_return / 100.0
        eur_mean = st.session_state.eur_market_return / 100.0
        rng = np.random.default_rng(int(st.session_state.mc_seed))

        use_bootstrap = (st.session_state.mc_method == "Historical Block Bootstrap")
        compound_target = (st.session_state.mc_mean_type == "Compound (CAGR) target")

        if use_bootstrap:
            block_len = int(st.session_state.mc_block_len)
            # Pair the same calendar years across the US and EUR series so both sleeves
            # share global crises, using independent European return data for the EUR
            # sleeve. Sampling is restricted to years present in BOTH series.
            common_years = sorted(set(SP500_BY_YEAR) & set(MSCI_EUR_TOTAL_RETURNS))
            usd_hist = np.array([SP500_BY_YEAR[y] for y in common_years]) / 100.0
            eur_hist = np.array([MSCI_EUR_TOTAL_RETURNS[y] for y in common_years]) / 100.0
            n_blocks_src = len(common_years) - block_len + 1
            # Recenter each sleeve to its own historical mean, then to the user's target;
            # add volatility drag back when targeting a compound (CAGR) return.
            usd_var, eur_var = float(np.var(usd_hist)), float(np.var(eur_hist))
            usd_arith = usd_mean + (usd_var / 2.0 if compound_target else 0.0)
            eur_arith = eur_mean + (eur_var / 2.0 if compound_target else 0.0)

            def make_paths():
                # Sample contiguous calendar-year blocks; apply the SAME year indices to
                # both sleeves so a 2008 in the US sleeve is a 2008 in the EUR sleeve.
                idx = []
                while len(idx) < n_years:
                    s = rng.integers(0, n_blocks_src)
                    idx.extend(range(s, s + block_len))
                idx = np.array(idx[:n_years])
                u_seq, e_seq = usd_hist[idx], eur_hist[idx]
                usd = u_seq - u_seq.mean() + usd_arith
                eur = e_seq - e_seq.mean() + eur_arith
                return usd, eur
        else:
            usd_sd = st.session_state.mc_usd_vol / 100.0
            eur_sd = st.session_state.mc_eur_vol / 100.0
            rho = st.session_state.mc_corr
            # Add vol drag back to the arithmetic mean when targeting a compound return.
            usd_arith = usd_mean + (usd_sd**2 / 2.0 if compound_target else 0.0)
            eur_arith = eur_mean + (eur_sd**2 / 2.0 if compound_target else 0.0)
            cov = np.array([[usd_sd**2, rho*usd_sd*eur_sd], [rho*usd_sd*eur_sd, eur_sd**2]])
            try:
                L = np.linalg.cholesky(cov)
            except np.linalg.LinAlgError:
                L = np.linalg.cholesky(cov + np.eye(2)*1e-9)

            def make_paths():
                z = rng.standard_normal((n_years, 2)) @ L.T
                return usd_arith + z[:, 0], eur_arith + z[:, 1]

        terminal_real, depletion_ages = [], []
        real_paths = np.full((n_runs, n_years), np.nan)
        success = 0
        start_age = st.session_state.current_age

        progress = st.progress(0.0, text="Running simulations...")
        for run in range(n_runs):
            usd_draws, eur_draws = make_paths()
            overrides = {years[i]: (float(usd_draws[i]), float(eur_draws[i])) for i in range(n_years)}
            df_bal, _, _, _, _ = run_core_simulation(return_overrides=overrides)
            total = df_bal.loc['Total Portfolio Balance']

            real_series = np.array([total[y] / ((1 + inf_rate) ** (y - 2026)) for y in years])
            real_paths[run, :] = real_series

            depleted = total[total <= 0]
            if len(depleted) > 0:
                depletion_ages.append(depleted.index.min() - 2026 + start_age)
            else:
                success += 1
                depletion_ages.append(100)
            terminal_real.append(real_series[-1])

            if run % max(1, n_runs // 50) == 0:
                progress.progress(run / n_runs, text=f"Running simulations... {run}/{n_runs}")
        progress.progress(1.0, text="Complete.")

        terminal_real = np.array(terminal_real)
        depletion_ages = np.array(depletion_ages)
        success_rate = 100.0 * success / n_runs

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Plan Success Rate (to age 100)", f"{success_rate:.1f}%")
        c2.metric("Median Terminal Wealth (Real)", f"${np.median(terminal_real)/1e6:,.2f}M")
        c3.metric("10th-Pctile Terminal Wealth", f"${np.percentile(terminal_real,10)/1e6:,.2f}M")
        c4.metric("10th-Pctile Depletion Age", f"{np.percentile(depletion_ages, 10):.0f}")

        # Success rate by age: share of paths whose portfolio is still solvent AT each
        # age (i.e. depletion age >= target age). Shown for ages 70-100.
        st.markdown("---")
        st.subheader("Success Rate by Age (Probability Portfolio Survives to Each Age)")
        target_ages = list(range(70, 101))
        survival = [100.0 * np.mean(depletion_ages >= a) for a in target_ages]

        fig_surv = go.Figure()
        fig_surv.add_trace(go.Scatter(
            x=target_ages, y=survival, mode='lines+markers',
            line=dict(color='#1f77b4', width=3), marker=dict(size=5),
            fill='tozeroy', fillcolor='rgba(31,119,180,0.12)',
            hovertemplate="Age %{x}: %{y:.1f}% of paths solvent<extra></extra>", name="Survival %"
        ))
        # Reference lines at common planning thresholds.
        for thr, lbl in [(95, "95%"), (90, "90%"), (80, "80%")]:
            fig_surv.add_hline(y=thr, line_dash="dot", line_color="grey", opacity=0.5,
                               annotation_text=lbl, annotation_position="right")
        fig_surv.update_layout(
            xaxis=dict(title="Age", dtick=5), yaxis=dict(title="Probability Still Solvent (%)", range=[0, 101]),
            hovermode="x unified", showlegend=False, height=400
        )
        st.plotly_chart(fig_surv, use_container_width=True)

        # Compact table at 5-year milestones.
        milestone_ages = [70, 75, 80, 85, 90, 95, 100]
        df_surv = pd.DataFrame({
            "Age": milestone_ages,
            "Success Rate (%)": [f"{100.0 * np.mean(depletion_ages >= a):.1f}%" for a in milestone_ages]
        }).set_index("Age").T
        st.dataframe(df_surv, use_container_width=True)
        st.caption(
            "Reads as a survival curve: the share of simulated paths in which your money "
            "lasts at least to each age. It necessarily declines with age. A plan is commonly "
            "considered robust if it clears ~90% at your planning-horizon age."
        )

        pct = {p: np.nanpercentile(real_paths, p, axis=0) for p in [10, 25, 50, 75, 90]}
        fig_fan = go.Figure()
        fig_fan.add_trace(go.Scatter(x=years, y=pct[90], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig_fan.add_trace(go.Scatter(x=years, y=pct[10], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(31,119,180,0.15)', name='10th-90th pct'))
        fig_fan.add_trace(go.Scatter(x=years, y=pct[75], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig_fan.add_trace(go.Scatter(x=years, y=pct[25], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(31,119,180,0.30)', name='25th-75th pct'))
        fig_fan.add_trace(go.Scatter(x=years, y=pct[50], mode='lines', line=dict(color='red', width=3), name='Median'))
        fig_fan.update_layout(
            title=f"Real Portfolio Value Across {n_runs:,} Paths ({st.session_state.mc_method})",
            xaxis_title="Year", yaxis_title="Real Portfolio Value (2026 $)",
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            hovermode="x unified"
        )
        st.plotly_chart(fig_fan, use_container_width=True)

        fig_hist = px.histogram(x=terminal_real/1e6, nbins=50, labels={'x': 'Terminal Real Wealth (Millions, 2026 $)'})
        fig_hist.update_layout(title="Distribution of Terminal Wealth at Age 100 (Real 2026 $)", yaxis_title="Number of Simulations", showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)

        if use_bootstrap:
            st.caption(
                "Block bootstrap preserves real historical volatility, fat tails, and the clustering "
                "of bad years (sequence risk) that a normal model misses. The USD and EUR sleeves use "
                "independent historical series paired on calendar year, so both fall together in global "
                "crises. Recentering to your assumed mean means the *shape* is historical but the *level* "
                "is your forward view. Caveat: paired sampling is limited to 2000-2025 (26 years), so the "
                "deepest pre-2000 US crashes (1931, 1974) are not in the joint sample."
            )
        else:
            st.caption(
                "The normal model understates fat tails and assumes returns are independent year to "
                "year (no clustering of crashes). Switch to Historical Block Bootstrap for a more "
                "realistic tail and sequence-of-returns risk."
            )
