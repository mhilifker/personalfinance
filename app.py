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

# Match Streamlit's top header bar to the app's dark theme (it defaults to white/transparent
# and looks out of place). This colors the header and its toolbar to the dark background.
st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background-color: #0e1117;
    }
    [data-testid="stToolbar"] {
        background-color: #0e1117;
    }
    [data-testid="stDecoration"] {
        background: #0e1117;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Master Inputs
if 'ret_age' not in st.session_state: st.session_state.ret_age = 55 
if 'move_age' not in st.session_state: st.session_state.move_age = 56
if 'current_age' not in st.session_state: st.session_state.current_age = 37
if 'nb_start_yr' not in st.session_state: st.session_state.nb_start_yr = 2027
if 'inflation_rate' not in st.session_state: st.session_state.inflation_rate = 2.9

# Bifurcated Returns
if 'usd_market_return' not in st.session_state: st.session_state.usd_market_return = 7.0
if 'eur_market_return' not in st.session_state: st.session_state.eur_market_return = 6.0
if 'execute_great_reset' not in st.session_state: st.session_state.execute_great_reset = True

# Lifetime Tax Smoothing & Giving While Living
if 'enable_smoothing' not in st.session_state: st.session_state.enable_smoothing = True
if 'target_early_draw' not in st.session_state: st.session_state.target_early_draw = 210000
if 'gift_start_age' not in st.session_state: st.session_state.gift_start_age = 58
if 'gift_end_age' not in st.session_state: st.session_state.gift_end_age = 78
# Master on/off for the dynamic generational gifting drip. When False, the model does NOT
# gift surplus away (it lets the portfolio accumulate), regardless of the age window.
if 'gifting_enable' not in st.session_state: st.session_state.gifting_enable = True

# Tax Assumptions
if 'tax_roth' not in st.session_state: st.session_state.tax_roth = 25.0
# Roth conversion ladder: annual pre-tax -> Roth conversion amount (today's USD) and the
# age window over which to convert. Conversions are US-taxable ordinary income always;
# post-move they are ALSO taxed by Slovenia (the double-hit the user chose to model).
if 'roth_conv_annual' not in st.session_state: st.session_state.roth_conv_annual = 0
if 'roth_conv_start_age' not in st.session_state: st.session_state.roth_conv_start_age = 55
if 'roth_conv_end_age' not in st.session_state: st.session_state.roth_conv_end_age = 56
# US ordinary-income rate applied to the conversion amount (the bracket you fill in the valley).
if 'roth_conv_us_rate' not in st.session_state: st.session_state.roth_conv_us_rate = 18.0
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
if 'home_price' not in st.session_state: st.session_state.home_price = 1050000
if 'down_payment' not in st.session_state: st.session_state.down_payment = 150000
if 'mtg_rate' not in st.session_state: st.session_state.mtg_rate = 6.5
if 'tax_rate' not in st.session_state: st.session_state.tax_rate = 1.9
if 'ann_insurance' not in st.session_state: st.session_state.ann_insurance = 4000
if 'pmi_rate' not in st.session_state: st.session_state.pmi_rate = 0.0 
if 'ann_apprec' not in st.session_state: st.session_state.ann_apprec = 2.0

# Decoupled SS Claim Ages
if 'mike_ss_age' not in st.session_state: st.session_state.mike_ss_age = 63
if 'steph_ss_age' not in st.session_state: st.session_state.steph_ss_age = 68
# Tracks whether the claim ages were set by the dynamic optimizer (vs manual input).
if 'ss_ages_optimized' not in st.session_state: st.session_state.ss_ages_optimized = False

# SS Macros
if 'mike_future_pct' not in st.session_state: st.session_state.mike_future_pct = 80 
if 'steph_future_pct' not in st.session_state: st.session_state.steph_future_pct = 80 
if 'trust_fund_haircut' not in st.session_state: st.session_state.trust_fund_haircut = 20 
if 'cola_rate' not in st.session_state: st.session_state.cola_rate = 2.6
# COLA assumption mode. The Social Security COLA can be run as the empirically-defensible
# BASELINE (a modest ~0.3pt structural lag vs inflation, the CPI-W/CPI-U basket difference),
# or as a STRESS case that models SS COLAs persistently lagging inflation by a large margin
# (a ~0.8-0.9pt gap), which erodes real SS benefits substantially over a long retirement and
# hits the survivor hardest. cola_rate above is the baseline; cola_stress_rate is the stress
# value; cola_mode selects which one the engine actually uses, so the choice is never invisible.
if 'cola_mode' not in st.session_state: st.session_state.cola_mode = "Baseline (modest structural lag)"
if 'cola_stress_rate' not in st.session_state: st.session_state.cola_stress_rate = 2.1
if 'awi_rate' not in st.session_state: st.session_state.awi_rate = 3.5

# Spending Targets (2026 Dollars)
if 'spend_golden' not in st.session_state: st.session_state.spend_golden = 127000
if 'spend_middle' not in st.session_state: st.session_state.spend_middle = 98000
if 'spend_wind' not in st.session_state: st.session_state.spend_wind = 85000

# Guardrails & Dynamic Gifting
if 'guardrails_enable' not in st.session_state: st.session_state.guardrails_enable = True
if 'floor_golden' not in st.session_state: st.session_state.floor_golden = 72000
if 'floor_middle' not in st.session_state: st.session_state.floor_middle = 72000
if 'floor_wind' not in st.session_state: st.session_state.floor_wind = 72000
if 'slash_trigger' not in st.session_state: st.session_state.slash_trigger = 5.25
if 'recovery_trigger' not in st.session_state: st.session_state.recovery_trigger = 4.25
if 'raise_pct' not in st.session_state: st.session_state.raise_pct = 33.0
if 'dynamic_gift_pct' not in st.session_state: st.session_state.dynamic_gift_pct = 33.0

# Institutional Stress Test Macros
if 'sorr_enable' not in st.session_state: st.session_state.sorr_enable = False
if 'sorr_start_yr' not in st.session_state: st.session_state.sorr_start_yr = 2044
if 'sorr_duration' not in st.session_state: st.session_state.sorr_duration = 2
if 'sorr_return' not in st.session_state: st.session_state.sorr_return = -15.0
if 'fx_enable' not in st.session_state: st.session_state.fx_enable = True
# fx_rate is the EUR/USD SPOT rate (USD per EUR). Spending is denominated in euros via
# the cost-of-living ratio below; the spot rate only prices currency crossings, so a
# STRONGER euro (higher rate) is now correctly adverse for the USD-heavy portfolio.
if 'fx_rate' not in st.session_state: st.session_state.fx_rate = 1.15
# Slovenia cost-of-living ratio: euros needed per $1 of US-equivalent lifestyle (the
# explicit PPP discount, separated from the exchange rate it used to be conflated with).
if 'sl_col_ratio' not in st.session_state: st.session_state.sl_col_ratio = 0.77
# Tax engine and Tier-1/Tier-2 fix toggles
if 'use_progressive_tax' not in st.session_state: st.session_state.use_progressive_tax = True
if 'roth_first' not in st.session_state: st.session_state.roth_first = True
if 'ibkr_lot_aging' not in st.session_state: st.session_state.ibkr_lot_aging = True
if 'model_div_tax' not in st.session_state: st.session_state.model_div_tax = True
if 'div_yield' not in st.session_state: st.session_state.div_yield = 1.7
# --- Plan B (EU move 2027) machinery ---
# Drag on the EUR equity sleeve from the PFIC/PRIIPs squeeze on a US citizen investing in
# the EU (blocked from US ETFs by PRIIPs, punished on UCITS by PFIC rules). Plan B default 0.4.
if 'eur_return_drag' not in st.session_state: st.session_state.eur_return_drag = 0.0
# Slovenian state (ZPIZ) pension: accrues over contribution years between the move and
# retirement. Basis defaults to ~the average Slovenian NET wage (CPI-indexed); statutory
# accrual ~26.5% at 15 years + ~1.36%/yr beyond. Survivor keeps the larger benefit.
# One-time USD transfer into IBKR at the move year (buys euros at spot).
if 'move_lump_ibkr_usd' not in st.session_state: st.session_state.move_lump_ibkr_usd = 0
if 'si_pension_enable' not in st.session_state: st.session_state.si_pension_enable = False
if 'si_pension_basis_eur' not in st.session_state: st.session_state.si_pension_basis_eur = 19000
if 'si_pension_claim_age' not in st.session_state: st.session_state.si_pension_claim_age = 65
if 'si_pension_tax_pct' not in st.session_state: st.session_state.si_pension_tax_pct = 10.0
if 'great_reset_mode' not in st.session_state: st.session_state.great_reset_mode = "Sweep at retirement (earnings taxed + 10% penalty if under 59½)"

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
# Explicit lifetime gifting goal (real 2026 $) to measure "gift success" against in MC.
if 'mc_gift_goal' not in st.session_state: st.session_state.mc_gift_goal = 500000
# Multi-factor stress toggles and parameters for the Monte Carlo.
if 'mc_stoch_inflation' not in st.session_state: st.session_state.mc_stoch_inflation = True
if 'mc_infl_vol' not in st.session_state: st.session_state.mc_infl_vol = 1.5
if 'mc_infl_equity_corr' not in st.session_state: st.session_state.mc_infl_equity_corr = -0.35
if 'mc_stoch_fx' not in st.session_state: st.session_state.mc_stoch_fx = True
if 'mc_fx_vol' not in st.session_state: st.session_state.mc_fx_vol = 9.0
# FX mean-reversion speed toward PPP (the base rate). 0 = pure random walk (unrealistic over
# decades; lets FX drift to absurd multiples); ~0.15 pulls the log-level ~15% back to parity
# each year, matching the empirical long-horizon mean reversion of real exchange rates.
if 'mc_fx_reversion' not in st.session_state: st.session_state.mc_fx_reversion = 0.15
if 'mc_stoch_longevity' not in st.session_state: st.session_state.mc_stoch_longevity = True
# Mike and Stephanie are the SAME age (corrected from the earlier 2-year offset).
if 'mc_wife_age_offset' not in st.session_state: st.session_state.mc_wife_age_offset = 0
if 'mc_ltc_enable' not in st.session_state: st.session_state.mc_ltc_enable = True
if 'mc_ltc_prob' not in st.session_state: st.session_state.mc_ltc_prob = 0.20
if 'mc_ltc_cost' not in st.session_state: st.session_state.mc_ltc_cost = 75000
if 'mc_ltc_years' not in st.session_state: st.session_state.mc_ltc_years = 3
if 'mc_tax_regime' not in st.session_state: st.session_state.mc_tax_regime = True
if 'mc_tax_vol' not in st.session_state: st.session_state.mc_tax_vol = 0.15
if 'mc_ss_haircut_prob' not in st.session_state: st.session_state.mc_ss_haircut_prob = 0.50
if 'mc_ss_haircut_size' not in st.session_state: st.session_state.mc_ss_haircut_size = 0.15

# Valuation conditioning (CAPE -> forward return) and the crisis-regime overlay. These must
# be initialized at module scope: the Monte Carlo UI widgets read them directly, and the
# shared helpers (build_valuation_shift / apply_crisis_overlay) reference them on every page
if 'mc_valuation_enable' not in st.session_state: st.session_state.mc_valuation_enable = True
if 'mc_cape_implied_usd' not in st.session_state: st.session_state.mc_cape_implied_usd = 3.0
if 'mc_cape_implied_eur' not in st.session_state: st.session_state.mc_cape_implied_eur = 5.0
if 'mc_reversion_years' not in st.session_state: st.session_state.mc_reversion_years = 12
if 'mc_valuation_strength' not in st.session_state: st.session_state.mc_valuation_strength = 1.0
if 'mc_crisis_enable' not in st.session_state: st.session_state.mc_crisis_enable = True
if 'mc_crisis_freq' not in st.session_state: st.session_state.mc_crisis_freq = 0.05
if 'mc_crisis_persist' not in st.session_state: st.session_state.mc_crisis_persist = 0.20
if 'mc_crisis_usd_mean' not in st.session_state: st.session_state.mc_crisis_usd_mean = -22.0
if 'mc_crisis_vol' not in st.session_state: st.session_state.mc_crisis_vol = 22.0
if 'mc_crisis_eur_drag' not in st.session_state: st.session_state.mc_crisis_eur_drag = 0.90
if 'mc_crisis_bond_mean' not in st.session_state: st.session_state.mc_crisis_bond_mean = -6.0

# Survivor scenario: between the first and second death, model the survivor's economics.
# The survivor keeps the LARGER SS benefit (smaller is lost); spending drops to the
# survivor expense ratio (not half); and the survivor files single (widow's penalty
# surcharge on US tax). Applies in any run that carries a first-death year.
if 'survivor_enable' not in st.session_state: st.session_state.survivor_enable = True
if 'survivor_expense_ratio' not in st.session_state: st.session_state.survivor_expense_ratio = 0.75
if 'survivor_tax_surcharge' not in st.session_state: st.session_state.survivor_tax_surcharge = 1.18

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

# US CPI-U annual inflation (%), Dec-to-Dec, BLS, 1928-2025. Used by the historical-cohort
# backtest (Page 15) to feed each cohort the REAL inflation it actually faced -- essential
# because the 1966 and 1973 cohorts were destroyed as much by 1970s inflation as by weak
# equity returns. Without real inflation, a cohort backtest flatters the plan badly.
US_CPI_BY_YEAR = {
    1928:-1.7,1929:0.0,1930:-2.3,1931:-9.0,1932:-9.9,1933:0.8,1934:1.5,1935:3.0,1936:1.4,1937:2.9,
    1938:-2.8,1939:0.0,1940:0.7,1941:9.9,1942:9.0,1943:3.0,1944:2.3,1945:2.2,1946:18.1,1947:8.8,
    1948:3.0,1949:-2.1,1950:5.9,1951:6.0,1952:0.8,1953:0.7,1954:-0.7,1955:0.4,1956:3.0,1957:2.9,
    1958:1.8,1959:1.7,1960:1.4,1961:0.7,1962:1.3,1963:1.6,1964:1.0,1965:1.9,1966:3.5,1967:3.0,
    1968:4.7,1969:6.2,1970:5.6,1971:3.3,1972:3.4,1973:8.7,1974:12.3,1975:6.9,1976:4.9,1977:6.7,
    1978:9.0,1979:13.3,1980:12.5,1981:8.9,1982:3.8,1983:3.8,1984:3.9,1985:3.8,1986:1.1,1987:4.4,
    1988:4.4,1989:4.6,1990:6.1,1991:3.1,1992:2.9,1993:2.7,1994:2.7,1995:2.5,1996:3.3,1997:1.7,
    1998:1.6,1999:2.7,2000:3.4,2001:1.6,2002:2.4,2003:1.9,2004:3.3,2005:3.4,2006:2.5,2007:4.1,
    2008:0.1,2009:2.7,2010:1.5,2011:3.0,2012:1.7,2013:1.5,2014:0.8,2015:0.7,2016:2.1,2017:2.1,
    2018:1.9,2019:2.3,2020:1.4,2021:7.0,2022:6.5,2023:3.4,2024:2.9,2025:2.9
}

# SSA 2025 period life-table life expectancy e(x) by exact age, male & female (55-114),
# used to simulate stochastic death ages via the exact curtate relation
# p(x) = (e(x)-0.5)/(1+(e(x+1)-0.5)), which reproduces the SSA table exactly.
SSA_EX_MALE = {55:24.94,56:24.15,57:23.37,58:22.59,59:21.83,60:21.08,61:20.34,62:19.61,63:18.89,64:18.18,65:17.48,66:16.79,67:16.11,68:15.43,69:14.76,70:14.09,71:13.44,72:12.80,73:12.16,74:11.53,75:10.92,76:10.32,77:9.74,78:9.18,79:8.64,80:8.11,81:7.60,82:7.11,83:6.64,84:6.18,85:5.74,86:5.32,87:4.92,88:4.54,89:4.21,90:3.91,91:3.60,92:3.32,93:3.06,94:2.83,95:2.63,96:2.44,97:2.28,98:2.13,99:2.00,100:1.88,101:1.76,102:1.66,103:1.56,104:1.47,105:1.39,106:1.31,107:1.23,108:1.15,109:1.08,110:1.01,111:0.94,112:0.87,113:0.81,114:0.75}
SSA_EX_FEMALE = {55:28.34,56:27.48,57:26.63,58:25.78,59:24.95,60:24.12,61:23.31,62:22.50,63:21.70,64:20.90,65:20.12,66:19.34,67:18.56,68:17.79,69:17.03,70:16.27,71:15.53,72:14.80,73:14.08,74:13.37,75:12.68,76:12.00,77:11.35,78:10.71,79:10.09,80:9.49,81:8.90,82:8.34,83:7.79,84:7.26,85:6.75,86:6.27,87:5.81,88:5.38,89:4.99,90:4.62,91:4.27,92:3.94,93:3.64,94:3.36,95:3.10,96:2.87,97:2.66,98:2.47,99:2.30,100:2.14,101:2.00,102:1.87,103:1.75,104:1.63,105:1.52,106:1.42,107:1.32,108:1.23,109:1.14,110:1.05,111:0.97,112:0.89,113:0.82,114:0.75}

def _survival_probs(ex_table):
    ages = sorted(ex_table); E = {x: ex_table[x] - 0.5 for x in ages}; p = {}
    for x in ages:
        p[x] = min(0.9999, max(0.0, E[x] / (1 + E[x+1]))) if (x+1) in E else 0.0
    return p

SURV_MALE = _survival_probs(SSA_EX_MALE)
SURV_FEMALE = _survival_probs(SSA_EX_FEMALE)
_MIN_LIFE_AGE = min(SURV_MALE)

def sample_death_age(current_age, sex_table, rng):
    """Draw a death age from SSA survival probabilities. Pre-55 ages assumed to survive."""
    max_age = max(sex_table); age = current_age
    while age < max_age:
        pr = sex_table.get(age, 1.0 if age < _MIN_LIFE_AGE else 0.0)
        if rng.random() > pr:
            break
        age += 1
    return age


def _norm_ppf(p):
    """Inverse standard-normal CDF via Acklam's rational approximation (~1e-7 accurate).
    Replaces scipy.stats.norm.ppf so the app has no scipy dependency (scipy is not
    installed in the deployment environment). Uses only numpy (np.log)."""
    p = min(max(p, 1e-9), 1 - 1e-9)
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = (-2 * np.log(p)) ** 0.5
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= phigh:
        q = p - 0.5; r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = (-2 * np.log(1-p)) ** 0.5
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


def build_valuation_shift(n_years, usd_mean, eur_mean):
    """Per-year additive shift to the equity mean from CAPE conditioning: starts at
    (CAPE_implied - long_run) * strength and reverts linearly to 0 over the window.
    Shared by the Monte Carlo, tornado, interaction matrix, and Roth optimizer so all
    tools evaluate against the same valuation-conditioned world."""
    import numpy as _np
    vsu = _np.zeros(n_years); vse = _np.zeros(n_years)
    if st.session_state.get('mc_valuation_enable', False):
        strength = st.session_state.get('mc_valuation_strength', 1.0)
        rev = max(1, int(st.session_state.get('mc_reversion_years', 12)))
        gap_u = (st.session_state.get('mc_cape_implied_usd', 3.0)/100.0 - usd_mean) * strength
        gap_e = (st.session_state.get('mc_cape_implied_eur', 5.0)/100.0 - eur_mean) * strength
        for t in range(n_years):
            w = max(0.0, 1.0 - t/rev)
            vsu[t] = gap_u * w; vse[t] = gap_e * w
    return vsu, vse


def apply_crisis_overlay(usd, eur, bond, rng):
    """Two-state Markov crisis overlay. In crisis years it overrides the drawn returns with
    a sharp drawdown and drags the EUR sleeve and bonds down too (correlations -> high).
    Shared across all Monte-Carlo-based tools. Returns possibly-modified copies."""
    import numpy as _np
    if not st.session_state.get('mc_crisis_enable', False):
        return usd, eur, bond
    cr_freq = st.session_state.get('mc_crisis_freq', 0.05)
    cr_persist = st.session_state.get('mc_crisis_persist', 0.20)
    cr_entry = ((1 - cr_persist) * cr_freq / (1 - cr_freq)) if cr_freq < 1 else 1.0
    cr_usd_m = st.session_state.get('mc_crisis_usd_mean', -22.0)/100.0
    cr_vol = st.session_state.get('mc_crisis_vol', 22.0)/100.0
    cr_eur_drag = st.session_state.get('mc_crisis_eur_drag', 0.90)
    cr_bond_m = st.session_state.get('mc_crisis_bond_mean', -6.0)/100.0
    u = _np.array(usd, dtype=float).copy(); e = _np.array(eur, dtype=float).copy(); b = _np.array(bond, dtype=float).copy()
    in_crisis = False
    for t in range(len(u)):
        in_crisis = (rng.random() < cr_persist) if in_crisis else (rng.random() < cr_entry)
        if in_crisis:
            shock = rng.normal(cr_usd_m, cr_vol)
            u[t] = shock
            e[t] = cr_eur_drag * shock + (1 - cr_eur_drag) * e[t]
            b[t] = cr_bond_m + 0.3 * (shock - cr_usd_m)
    return u, e, b


# -----------------------------------------------------------------------------
# SHARED MONTE CARLO MACHINERY (single source of truth)
# Every Monte-Carlo-based tool (dashboard gauges, Pages 7/8 bands, Page 12, the
# tornado, the interaction matrix, the SS claim-age optimizer, and the Roth
# ladder optimizer) builds market paths, stress scenarios, discounting, and
# joint-success scoring through THESE helpers. Previously each tool carried its
# own near-copy of this code and they had already diverged (e.g. only the
# dashboard survivor-adjusted the lifestyle target). One implementation means
# one set of semantics everywhere.
# -----------------------------------------------------------------------------
MC_YEARS = list(range(2026, 2090))


def _paired_history():
    """Paired calendar years present in BOTH the US and EUR return series."""
    common = sorted(set(SP500_BY_YEAR) & set(MSCI_EUR_TOTAL_RETURNS))
    uh = np.array([SP500_BY_YEAR[y] for y in common]) / 100.0
    eh = np.array([MSCI_EUR_TOTAL_RETURNS[y] for y in common]) / 100.0
    return common, uh, eh


def draw_bond_path(u, rng):
    """EUR bond returns correlated with the equity path; correlation jumps to the
    crisis value in sharp-drawdown years (the 2022 lesson: bonds fall with stocks
    on rate/inflation shocks, so de-risking is not a free hedge in the bad years)."""
    u = np.asarray(u, dtype=float)
    bm = st.session_state.bond_mean / 100.0
    bv = st.session_state.bond_vol / 100.0
    cn = st.session_state.bond_eq_corr
    cc = st.session_state.bond_eq_corr_crisis
    mu = u.mean()
    sd = u.std() or 1e-9
    zb = rng.standard_normal(len(u))
    b = np.empty(len(u))
    for i, r in enumerate(u):
        z = (r - mu) / sd
        c = cc if (z < -1.0 and r < 0) else cn
        b[i] = bm + bv * (c * z + np.sqrt(max(0.0, 1 - c ** 2)) * zb[i])
    return b


def make_bootstrap_paths(rng, n_years=None):
    """One paired block-bootstrap path (USD equity, EUR equity, EUR bond), with
    valuation conditioning and the crisis overlay applied.

    Recentering uses the FULL-HISTORY mean (`uh.mean()`), not each draw's own
    sample mean. Recentering per-draw pinned every simulated 64-year history to
    realize EXACTLY the assumed average return, deleting long-run-mean
    uncertainty -- one of the largest sources of terminal-wealth dispersion --
    and biasing success rates optimistic. With full-history recentering, paths
    retain natural variation in their realized 64-year averages.
    Honors mc_mean_type: under a Compound (CAGR) target, volatility drag is
    added back to the arithmetic center."""
    n_years = n_years or len(MC_YEARS)
    common, uh, eh = _paired_history()
    block = int(st.session_state.get('mc_block_len', 5))
    nb = len(common) - block + 1
    compound = str(st.session_state.get('mc_mean_type', "Compound (CAGR) target")).startswith("Compound")
    um = st.session_state.usd_market_return / 100.0 + (np.var(uh) / 2.0 if compound else 0.0)
    em = st.session_state.eur_market_return / 100.0 + (np.var(eh) / 2.0 if compound else 0.0)
    vsu, vse = build_valuation_shift(n_years, st.session_state.usd_market_return / 100.0,
                                     st.session_state.eur_market_return / 100.0)
    idx = []
    while len(idx) < n_years:
        s = rng.integers(0, nb)
        idx.extend(range(s, s + block))
    idx = np.array(idx[:n_years])
    u = uh[idx] - uh.mean() + um + vsu
    e = eh[idx] - eh.mean() + em + vse
    b = draw_bond_path(u, rng)
    return apply_crisis_overlay(u, e, b, rng)


def build_stress_scenario(rng, usd_path, flags=None, years=None):
    """Build the per-path stress-factor scenario dict.

    flags=None honors the Stress Factors checkboxes (the main MC behavior);
    otherwise apply ONLY the named factors out of
    {'inflation','fx','longevity','ltc','tax','ss'} (tornado / interaction
    matrix behavior). Longevity always carries '_first_death_yr' so the
    survivor scenario engages consistently in every consumer."""
    years = years or MC_YEARS
    S = st.session_state

    def on(name, enabled_default):
        return enabled_default if flags is None else (name in flags)

    sc = {}
    u = np.asarray(usd_path, dtype=float)
    if on('inflation', S.mc_stoch_inflation):
        base_infl = S.inflation_rate / 100.0
        iv = S.mc_infl_vol / 100.0
        ic = S.mc_infl_equity_corr
        em_ = u.mean()
        es_ = u.std() or 1e-9
        infl = {}
        for i, y in enumerate(years):
            z = (u[i] - em_) / es_
            infl[y] = max(-0.02, base_infl + ic * z * iv + np.sqrt(max(0.0, 1 - ic ** 2)) * rng.normal(0, iv))
        sc['inflation'] = infl
    if on('fx', S.mc_stoch_fx):
        fxv = S.mc_fx_vol / 100.0
        fxb = S.fx_rate if S.fx_enable else 1.0
        kappa = S.get('mc_fx_reversion', 0.15)
        log_lvl = 0.0
        fx = {}
        for y in years:
            log_lvl = (1 - kappa) * log_lvl + rng.normal(0, fxv)
            fx[y] = fxb * np.exp(log_lvl)
        sc['fx'] = fx
    if on('longevity', S.mc_stoch_longevity):
        start = S.current_age
        woff = S.mc_wife_age_offset
        d_self = sample_death_age(start, SURV_MALE, rng)
        d_sp = sample_death_age(start - woff, SURV_FEMALE, rng)
        sy = 2026 + (d_self - start)
        py = 2026 + (d_sp - (start - woff))
        sc['death_year'] = min(2089, max(sy, py))
        sc['_first_death_yr'] = min(sy, py)
    if on('ltc', S.mc_ltc_enable):
        ltc = {}
        for _p in range(2):
            if rng.random() < S.mc_ltc_prob:
                onset = 2026 + (int(rng.integers(78, 90)) - S.current_age)
                for kk in range(int(S.mc_ltc_years)):
                    if onset + kk <= 2089:
                        ltc[onset + kk] = ltc.get(onset + kk, 0) + S.mc_ltc_cost
        if ltc:
            sc['ltc_cost'] = ltc
    if on('tax', S.mc_tax_regime):
        sc['tax_mult'] = max(0.2, rng.normal(1.0, S.mc_tax_vol))
    if on('ss', S.mc_ss_haircut_prob > 0):
        if rng.random() < S.mc_ss_haircut_prob:
            sc['ss_haircut'] = S.mc_ss_haircut_size
    return sc


def discount_map_from(sc, years=None):
    """Per-path real (2026 $) discount factors: realized inflation when the path
    is stochastic, the deterministic assumption otherwise."""
    years = years or MC_YEARS
    if 'inflation' in sc:
        dm = {}
        cpi = 1.0
        for y in years:
            if y > 2026:
                cpi *= (1 + sc['inflation'][y])
            dm[y] = cpi
        return dm
    inf = st.session_state.inflation_rate / 100.0
    return {y: (1 + inf) ** (y - 2026) for y in years}


def retirement_target_map():
    """(retirement years, {year: real 2026-$ lifestyle target}) under the
    golden/middle/wind-down phases."""
    start = st.session_state.current_age
    ret_start = 2026 + (st.session_state.ret_age - start)
    ret_years = [y for y in MC_YEARS if y >= ret_start]

    def _tgt(a):
        return st.session_state.spend_golden if a < 70 else (
            st.session_state.spend_middle if a < 85 else st.session_state.spend_wind)

    return ret_years, {y: _tgt(start + (y - 2026)) for y in ret_years}


def score_path_joint(db, dd, sc, ret_years, target_map, gift_goal):
    """Survivor-aware joint-success scoring shared by EVERY MC consumer.

    - Solvency is judged through the household's actual death year (depletion
      after both have died is irrelevant).
    - Lifestyle is scored over living years only, against a target that is
      scaled DOWN by the survivor expense ratio after the first death --
      otherwise the intentional survivor spending reduction would wrongly count
      as a shortfall (the divergence that previously existed between the
      dashboard and Page 12).
    - Gifting is real (2026 $) over living retirement years."""
    dm = discount_map_from(sc)
    tot = db.loc['Total Portfolio Balance']
    death_yr = sc.get('death_year', 2089)
    zeros = tot[tot <= 0]
    first_zero = zeros.index.min() if len(zeros) > 0 else None
    nd = (first_zero is None) or (first_zero > death_yr)
    scored = [y for y in ret_years if y <= death_yr]
    fd = sc.get('_first_death_yr')
    surv_on = st.session_state.survivor_enable and (fd is not None)
    sr = st.session_state.survivor_expense_ratio if surv_on else 1.0

    def adj_target(y):
        t = target_map[y]
        return t * sr if (surv_on and y > fd) else t

    stgt = sum(adj_target(y) for y in scored) or 1.0
    life = dd.loc["Actual Lifestyle Spend"]
    gift = dd.loc["Actual Generational Drip"]
    ar = sum(life.get(y, 0.0) / dm[y] for y in scored)
    ratio = ar / stgt
    gift_real = sum(gift.get(y, 0.0) / dm[y] for y in scored)
    return {'nd': nd, 'ratio': ratio, 'full': ratio >= 0.95, 'gift_real': gift_real,
            'joint': nd and (ratio >= 0.95) and (gift_real >= gift_goal),
            'death_yr': death_yr, 'first_zero': first_zero, 'dm': dm,
            'scored_years': scored, 'adj_target': adj_target}


def score_joint_success_for_ss(n_runs, seed, m_age, s_age):
    """Monte Carlo joint-success rate for a pair of SS claim ages, with common
    random numbers so claim-age pairs are compared on identical markets.

    Now includes STOCHASTIC LONGEVITY, the SURVIVOR scenario, and the SS-haircut
    lottery -- the factors that actually drive claim timing. (Previously the
    optimizer ran on a fixed age-100 horizon with no mortality, so longevity
    insurance and survivor protection -- the primary economic reasons to delay
    claiming -- were absent from its objective.) The remaining stress factors
    (inflation, FX, LTC, tax drift) are left off here for speed and CRN
    cleanliness; the main MC carries them."""
    ret_years, tmap = retirement_target_map()
    gift_goal = float(st.session_state.get('mc_gift_goal', 500000))
    nN = len(MC_YEARS)
    rng = np.random.default_rng(seed)
    ok = 0
    for _ in range(n_runs):
        u, e, b = make_bootstrap_paths(rng)
        sc = build_stress_scenario(rng, u, flags={'longevity', 'ss'})
        sc['returns'] = {MC_YEARS[i]: (float(u[i]), float(e[i])) for i in range(nN)}
        sc['bond'] = {MC_YEARS[i]: float(b[i]) for i in range(nN)}
        db, dd, _, _, _ = run_core_simulation(override_m_age=m_age, override_s_age=s_age, scenario=sc)
        if score_path_joint(db, dd, sc, ret_years, tmap, gift_goal)['joint']:
            ok += 1
    return 100.0 * ok / n_runs


def dashboard_full_stress_metrics(n_runs, seed):
    """Runs the SAME full-stress engine as Page 12 (valuation conditioning +
    crisis overlay + EUR bond sleeve + every enabled stress factor) and returns
    the dashboard metrics dict. Built entirely on the shared helpers so the
    headline number and Page 12 cannot diverge again."""
    ret_years, tmap = retirement_target_map()
    start = st.session_state.current_age
    nN = len(MC_YEARS)
    rng = np.random.default_rng(seed)

    depl_living_ages, death_ages = [], []
    path_success, full_life, funded_ratios, lifetime_gift_real = [], [], [], []
    spend_matrix = np.full((n_runs, len(ret_years)), np.nan)

    for _run in range(n_runs):
        u, e, b = make_bootstrap_paths(rng)
        sc = build_stress_scenario(rng, u)  # honors the Stress Factors checkboxes
        sc['returns'] = {MC_YEARS[i]: (float(u[i]), float(e[i])) for i in range(nN)}
        sc['bond'] = {MC_YEARS[i]: float(b[i]) for i in range(nN)}
        db, dd, _, _, _ = run_core_simulation(scenario=sc)
        R = score_path_joint(db, dd, sc, ret_years, tmap, 0.0)
        path_success.append(R['nd'])
        funded_ratios.append(R['ratio'])
        lifetime_gift_real.append(R['gift_real'])
        full_life.append(R['nd'] and R['ratio'] >= 0.95)
        fz = R['first_zero']
        depl_living_ages.append((fz - 2026 + start) if fz is not None else 101)
        death_ages.append((R['death_yr'] - 2026 + start) if st.session_state.mc_stoch_longevity else 100)
        dm = R['dm']
        life = dd.loc["Actual Lifestyle Spend"]
        for ci, y in enumerate(ret_years):
            if y <= R['death_yr']:
                spend_matrix[_run, ci] = life.get(y, 0.0) / dm[y]

    path_success = np.array(path_success)
    full_life = np.array(full_life)
    depl = np.array(depl_living_ages)
    fr = np.array(funded_ratios)
    never_deplete = 100.0 * path_success.mean()
    full_lifestyle = 100.0 * full_life.mean()
    band_full = 100.0 * np.mean(fr >= 0.95)
    band_mid = 100.0 * np.mean((fr >= 0.85) & (fr < 0.95))
    band_low = 100.0 * np.mean(fr < 0.85)
    median_funded = 100.0 * float(np.median(fr))
    ages = list(range(70, 101))
    by_age = [100.0 * np.mean(depl >= a) for a in ages]
    import warnings as _w
    with np.errstate(all='ignore'), _w.catch_warnings():
        _w.simplefilter('ignore', RuntimeWarning)  # all-NaN years (every path deceased) -> None
        spend_median = np.nanmedian(spend_matrix, axis=0)
        spend_p25 = np.nanpercentile(spend_matrix, 25, axis=0)
        spend_p75 = np.nanpercentile(spend_matrix, 75, axis=0)
    gift_arr = np.array(lifetime_gift_real)
    return {
        'never_deplete': never_deplete, 'full_lifestyle': full_lifestyle,
        'band_full': band_full, 'band_mid': band_mid, 'band_low': band_low,
        'median_funded': median_funded, 'ages': ages, 'by_age': by_age,
        'funded_ratios': (fr * 100.0).tolist(),
        'gift_median': float(np.median(gift_arr)) if len(gift_arr) else 0.0,
        'gift_p10': float(np.percentile(gift_arr, 10)) if len(gift_arr) else 0.0,
        'gift_p90': float(np.percentile(gift_arr, 90)) if len(gift_arr) else 0.0,
        'gift_values': gift_arr.tolist(),
        'spend_years': ret_years,
        'spend_median': [None if np.isnan(v) else float(v) for v in spend_median],
        'spend_p25': [None if np.isnan(v) else float(v) for v in spend_p25],
        'spend_p75': [None if np.isnan(v) else float(v) for v in spend_p75],
        'spend_target': [tmap[y] for y in ret_years],
        'start_age': start,
    }


def mc_bands_for_pages(n_runs, seed):
    """Lightweight Monte Carlo for Pages 7 and 8: per-year percentile bands for
    the total REAL (2026 $, USD-equivalent) portfolio balance and the
    weighted-average effective tax rate. Same shared engine as everything else."""
    nN = len(MC_YEARS)
    rng = np.random.default_rng(seed)
    real_bal = np.full((n_runs, nN), np.nan)
    tax_rate = np.full((n_runs, nN), np.nan)
    for _run in range(n_runs):
        u, e, b = make_bootstrap_paths(rng)
        sc = build_stress_scenario(rng, u)
        sc['returns'] = {MC_YEARS[i]: (float(u[i]), float(e[i])) for i in range(nN)}
        sc['bond'] = {MC_YEARS[i]: float(b[i]) for i in range(nN)}
        db, _, dtax, _, _ = run_core_simulation(scenario=sc)
        tot = db.loc['Total Portfolio Balance']
        dm = discount_map_from(sc)
        for i, y in enumerate(MC_YEARS):
            bal = tot.get(y, np.nan)
            real_bal[_run, i] = (bal / dm[y]) if (bal == bal and bal > 0) else (0.0 if bal == bal else np.nan)
            if 'Weighted Average' in dtax.index and y in dtax.columns:
                tr = dtax.loc['Weighted Average', y]
                tax_rate[_run, i] = tr if tr == tr else np.nan

    def _pcts(mat):
        import warnings as _w
        with np.errstate(all='ignore'), _w.catch_warnings():
            _w.simplefilter('ignore', RuntimeWarning)
            return {p: np.nanpercentile(mat, p, axis=0) for p in [10, 25, 50, 75, 90]}

    bal_p = _pcts(real_bal)
    tax_p = _pcts(tax_rate)
    return {
        'years': MC_YEARS,
        'bal_p10': bal_p[10].tolist(), 'bal_p25': bal_p[25].tolist(), 'bal_p50': bal_p[50].tolist(),
        'bal_p75': bal_p[75].tolist(), 'bal_p90': bal_p[90].tolist(),
        'tax_p10': tax_p[10].tolist(), 'tax_p25': tax_p[25].tolist(), 'tax_p50': tax_p[50].tolist(),
        'tax_p75': tax_p[75].tolist(), 'tax_p90': tax_p[90].tolist(),
    }


# Bifurcated Glide Path
if 'glide_enable' not in st.session_state: st.session_state.glide_enable = True
if 'glide_start_age' not in st.session_state: st.session_state.glide_start_age = 65
if 'glide_end_age' not in st.session_state: st.session_state.glide_end_age = 85
if 'usd_glide_reduction' not in st.session_state: st.session_state.usd_glide_reduction = 0.1
if 'eur_glide_reduction' not in st.session_state: st.session_state.eur_glide_reduction = 0.055

# Allocation-based glide (preferred): glide the EQUITY WEIGHT, with bonds filling the rest.
# Both the mean AND the volatility of each sleeve's return then depend on the equity weight,
# so de-risking actually compresses outcome dispersion (its real purpose) rather than just
# shaving return. When enabled, this supersedes the return-haircut glide above.
if 'glide_alloc_mode' not in st.session_state: st.session_state.glide_alloc_mode = True
if 'glide_eq_start' not in st.session_state: st.session_state.glide_eq_start = 0.90  # equity weight before de-risking
if 'glide_eq_end' not in st.session_state: st.session_state.glide_eq_end = 0.45    # equity weight at the floor
# Bond sleeve (EUR-denominated from the start, per the EUR-world plan).
if 'bond_mean' not in st.session_state: st.session_state.bond_mean = 3.0           # EUR bond expected return %
if 'bond_vol' not in st.session_state: st.session_state.bond_vol = 5.5             # EUR bond annual vol %
if 'bond_eq_corr' not in st.session_state: st.session_state.bond_eq_corr = 0.15    # normal-year bond/equity corr
if 'bond_eq_corr_crisis' not in st.session_state: st.session_state.bond_eq_corr_crisis = 0.65  # crisis-year corr
# Inflation-linked bond sleeve (a STATIC fraction of the bond allocation, NOT dynamically
# triggered by high inflation -- the protection only works if held continuously, since by
# the time inflation is visibly high, linkers have already repriced). The linker portion's
# return is modeled as a real yield PLUS the year's realized inflation, so it mechanically
# tracks whatever inflation path the simulation generates: it preserves real value in
# high-inflation years (when nominal bonds erode) and earns its modest real yield as a mild
# drag in calm years. linker_frac is the share of the bond sleeve held in linkers.
if 'linker_enable' not in st.session_state: st.session_state.linker_enable = True
if 'linker_frac' not in st.session_state: st.session_state.linker_frac = 0.50      # share of bond sleeve in linkers
if 'linker_real_yield' not in st.session_state: st.session_state.linker_real_yield = 1.0  # real yield % (e.g. euro linker ~1%)

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
        "Annual Savings Escalator (%)": [0.0, 0.0, 2.5, 0.0, -20.0, 2.5, 0.0, 0.0, 0.0, 0.0],
        "Current State": [0, 20000, 30000, 0, 15000, 30000, 0, 0, 8300, 0],
        "Northbrook Grind": [0, 20000, 30000, 0, 15000, 30000, 0, 0, 0, 0]
    })

if 'mike_history' not in st.session_state:
    st.session_state.mike_history = {2025: 176100, 2024: 168600, 2023: 160200, 2022: 147000, 2021: 142800, 2020: 137700, 2019: 132900, 2018: 38614, 2017: 51671, 2016: 80887, 2015: 77417, 2014: 71400, 2013: 16536, 2012: 15239, 2011: 9611, 2010: 13001, 2009: 13067, 2008: 9556, 2007: 7731, 2006: 11676, 2005: 6485}
if 'steph_history' not in st.session_state:
    st.session_state.steph_history = {2025: 170000, 2024: 140000, 2023: 100000, 2022: 120000, 2021: 105000, 2020: 100000, 2019: 100000, 2018: 55000, 2017: 35000, 2016: 35000, 2015: 35000, 2014: 35000, 2013: 35000, 2012: 35000, 2011: 5000, 2010: 5000, 2009: 5000, 2008: 5000, 2007: 5000, 2006: 2500, 2005: 2500}

# -----------------------------------------------------------------------------
# CORE SIMULATION ENGINE (RUNS GLOBALLY)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# PROGRESSIVE TAX TABLES (US + SLOVENIA)
# Used by the core engine when 'use_progressive_tax' is on (the default). All
# ordinary income in a year (pre-tax draws, RMDs, Roth conversions, taxable SS,
# non-qualified Roth-sweep earnings) stacks through these brackets instead of
# the legacy flat base/excess rates. Post-move, the combined liability is
# max(US, Slovenia) -- the savings-clause + foreign-tax-credit outcome -- and a
# survivor files SINGLE (half-width brackets, half deduction), which replaces
# the flat widow's-penalty surcharge. Bracket thresholds are 2026 levels and
# are indexed by the path's realized CPI.
# -----------------------------------------------------------------------------
US_BRACKETS_MFJ = [(0, 0.10), (24800, 0.12), (100800, 0.22), (211400, 0.24),
                   (403550, 0.32), (512450, 0.35), (768700, 0.37)]
US_BRACKETS_SINGLE = [(0, 0.10), (12400, 0.12), (50400, 0.22), (105700, 0.24),
                      (201775, 0.32), (256225, 0.35), (640600, 0.37)]
US_STD_DED_MFJ = 32200       # 2026 MFJ standard deduction (approx., post-OBBBA)
US_STD_DED_SINGLE = 16100
# Slovenia ordinary-income brackets (EUR, ~2026) and the general allowance.
SI_BRACKETS_EUR = [(0, 0.16), (9210, 0.26), (27089, 0.33), (54178, 0.39), (80185, 0.50)]
SI_GENERAL_ALLOWANCE_EUR = 5260
# IRC 877A covered-expatriate exit-tax gain exclusion (2026 approx., CPI-indexed).
EXIT_TAX_EXCLUSION_USD = 890000


def _piecewise_tax(taxable, brackets, scale=1.0):
    """Tax on `taxable` under bracket thresholds multiplied by `scale` (CPI index)."""
    if taxable <= 0:
        return 0.0
    tax = 0.0
    for i, (lo, rate) in enumerate(brackets):
        lo_s = lo * scale
        hi_s = brackets[i + 1][0] * scale if i + 1 < len(brackets) else None
        if taxable <= lo_s:
            break
        top = taxable if hi_s is None else min(taxable, hi_s)
        tax += (top - lo_s) * rate
    return tax


def us_ordinary_tax(gross_usd, cpi, single=False):
    """Total US ordinary-income tax on `gross_usd`, net of the standard
    deduction, with brackets and deduction indexed by the CPI path."""
    std = (US_STD_DED_SINGLE if single else US_STD_DED_MFJ) * cpi
    taxable = max(0.0, gross_usd - std)
    return _piecewise_tax(taxable, US_BRACKETS_SINGLE if single else US_BRACKETS_MFJ, cpi)


def si_ordinary_tax(gross_eur, cpi):
    """Total Slovenian ordinary-income tax on `gross_eur` (general allowance and
    brackets indexed by the CPI path -- a proxy for Slovenian indexation)."""
    taxable = max(0.0, gross_eur - SI_GENERAL_ALLOWANCE_EUR * cpi)
    return _piecewise_tax(taxable, SI_BRACKETS_EUR, cpi)


# -----------------------------------------------------------------------------
# SOCIAL SECURITY ACTUARIAL MODULE
# -----------------------------------------------------------------------------
def effective_cola():
    """Resolve the central COLA assumption from the selected mode. Baseline uses
    cola_rate (modest structural lag); Stress uses cola_stress_rate. With the
    COLA now indexed to the path's realized inflation (see build_cola_path),
    this defines the structural LAG vs the deterministic inflation assumption."""
    mode = st.session_state.get('cola_mode', "Baseline (modest structural lag)")
    if str(mode).startswith("Stress"):
        return st.session_state.get('cola_stress_rate', 2.1)
    return st.session_state.get('cola_rate', 2.6)


def build_cola_path(inflation_path=None):
    """Per-year SS COLA (%) tied to the path's REALIZED inflation.

    SS benefits are CPI-indexed in reality, so a high-inflation path raises
    COLAs (floored at 0, as the statute does). Previously the COLA was a fixed
    nominal rate regardless of the simulated inflation, which made real SS
    collapse in exactly the high-inflation paths the model emphasizes -- and
    made the 1966/1973 historical cohorts (whose real-world benefits WERE
    indexed) look far worse than they were. The structural lag
    (inflation assumption minus the selected COLA) is preserved as the explicit
    pessimism wedge: COLA_y = max(0, realized_inflation_y - lag)."""
    lag = st.session_state.inflation_rate - effective_cola()
    base = effective_cola()
    cola = {}
    for yr in range(2026, 2090):
        if inflation_path is not None and yr in inflation_path:
            cola[yr] = max(0.0, inflation_path[yr] * 100.0 - lag)
        else:
            cola[yr] = max(0.0, base)
    return cola


def calculate_person_benefit(history_dict, person_age, working_years, claim_age,
                             future_pct, cola_path, haircut, awi):
    """SS benefit timeline for ONE person, computed off that person's OWN age
    (claim year, age-60 AWI indexing year, and age-62 bend-point year all key
    off person_age -- previously the spouse's benefit was computed on the
    primary's age, shifting her stream ~2 calendar years).

    Early-claim reduction follows the statute: 5/9 of 1% per month for the
    first 36 months before FRA (6.67%/yr) and 5/12 of 1% per month beyond
    (5%/yr) -- so claiming at 62 with FRA 67 yields 70% of PIA, not 66.65%.
    Delayed credits remain 8%/yr. COLAs compound along cola_path (per-year %)
    from the year after first eligibility (age 62)."""
    current_year = 2026
    age_60_year = current_year + (60 - person_age)
    age_62_year = current_year + (62 - person_age)
    current_max = 176100
    indexed_earnings = []
    for yr, val in history_dict.items():
        if yr < age_60_year:
            idx_factor = (1 + (awi / 100)) ** max(0, age_60_year - yr)
            indexed_earnings.append(val * idx_factor)
        else:
            indexed_earnings.append(val)
    for i in range(working_years):
        yr = current_year + i
        projected_max = current_max * ((1 + (awi / 100)) ** (i + 1))
        val = projected_max * (future_pct / 100.0)
        if yr < age_60_year:
            idx_factor = (1 + (awi / 100)) ** (age_60_year - yr)
            indexed_earnings.append(val * idx_factor)
        else:
            indexed_earnings.append(val)
    indexed_earnings.sort(reverse=True)
    top_35 = (indexed_earnings[:35] + [0] * 35)[:35]
    aime = sum(top_35) / (35 * 12)
    # Bend points are set in the year of first eligibility (age 62) and grow with AWI.
    bp_growth_years = max(0, age_62_year - 2026)
    bp_multiplier = (1 + (awi / 100)) ** bp_growth_years
    bp1, bp2 = 1286 * bp_multiplier, 7749 * bp_multiplier
    if aime <= bp1:
        pia = 0.9 * aime
    elif aime <= bp2:
        pia = (0.9 * bp1) + 0.32 * (aime - bp1)
    else:
        pia = (0.9 * bp1) + 0.32 * (bp2 - bp1) + 0.15 * (aime - bp2)
    # Claim-age adjustment (FRA 67), statutory schedule.
    if claim_age >= 67:
        mult = 1.0 + (claim_age - 67) * 0.08
    else:
        months_early = (67 - claim_age) * 12
        mult = 1.0 - min(months_early, 36) * (5.0 / 900.0) - max(0, months_early - 36) * (5.0 / 1200.0)
    base_annual = pia * 12 * mult * (1 - (haircut / 100))
    claim_year = current_year + (claim_age - person_age)
    timeline = {}
    cola_idx = 1.0
    for yr in range(2026, 2090):
        if yr > max(2026, age_62_year):
            cola_idx *= (1 + cola_path.get(yr, 0.0) / 100.0)
        timeline[yr] = base_annual * cola_idx if yr >= claim_year else 0.0
    return timeline


def get_ss_timelines(override_m_age=None, override_s_age=None, inflation_path=None):
    """Household SS timelines. Each spouse's benefit is computed on their own
    age (spouse = current_age - mc_wife_age_offset, matching the longevity
    module). Pass the scenario's inflation path so COLAs follow realized
    inflation; deterministic runs reproduce the selected baseline/stress COLA."""
    m_claim = override_m_age if override_m_age is not None else st.session_state.mike_ss_age
    s_claim = override_s_age if override_s_age is not None else st.session_state.steph_ss_age
    cola_path = build_cola_path(inflation_path)
    ret_cal_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    move_cal_yr = 2026 + (st.session_state.move_age - st.session_state.current_age)
    # US covered earnings stop at the EARLIER of retirement or the move abroad. In Plan A
    # (move after retirement) this is unchanged; in Plan B (move 2027, retire later) only
    # 2026 is credited -- Slovenian work accrues the ZPIZ pension instead (totalization
    # protects vesting, not benefit size).
    working_years = max(0, min(ret_cal_yr, move_cal_yr) - 2026)
    mike_age = st.session_state.current_age
    steph_age = st.session_state.current_age - st.session_state.get('mc_wife_age_offset', 2)
    mike_ss = calculate_person_benefit(st.session_state.mike_history, mike_age, working_years,
                                       m_claim, st.session_state.mike_future_pct, cola_path,
                                       st.session_state.trust_fund_haircut, st.session_state.awi_rate)
    steph_ss = calculate_person_benefit(st.session_state.steph_history, steph_age, working_years,
                                        s_claim, st.session_state.steph_future_pct, cola_path,
                                        st.session_state.trust_fund_haircut, st.session_state.awi_rate)
    return mike_ss, steph_ss


def run_core_simulation(override_m_age=None, override_s_age=None, override_early_draw=None, return_overrides=None, scenario=None):
    # return_overrides: optional dict {year: (usd_return_frac, eur_return_frac)} for the
    # original returns-only Monte Carlo. When None, deterministic base-case returns apply.
    #
    # scenario: optional dict for the multi-factor Monte Carlo, with any of these keys:
    #   'returns'   : {year: (usd_frac, eur_frac)}      stochastic equity returns
    #   'inflation' : {year: inflation_frac}            stochastic per-year inflation
    #   'fx'        : {year: usd_per_eur_spot}          stochastic EUR/USD spot rate
    #   'bond'      : {year: bond_frac}                 stochastic EUR bond returns
    #   'roth_conv' : (annual, start_age, end_age)      conversion override for optimizer
    #   'death_year': int                               year after which no household spending
    #   '_first_death_yr': int                          first spouse's death -> survivor phase
    #   'tax_mult'  : float                             multiplier on all tax rates (regime risk)
    #   'ss_haircut': float (0-1)                       fractional SS benefit cut
    #   'ltc_cost'  : {year: real_usd}                  extra real long-term-care spend by year
    # Missing keys fall back to deterministic session-state values.
    #
    # DENOMINATION MODEL (the Tier-1 FX fix). The household's true liability after the
    # move is a EURO consumption basket. Lifestyle targets are entered in today's USD
    # purchasing power and translated ONCE to euros via the explicit cost-of-living
    # ratio (sl_col_ratio, e.g. 0.77 EUR per $1 of US-equivalent lifestyle). The
    # EUR/USD spot rate (fx) then prices every currency CROSSING: USD assets funding
    # euro spending pay fx dollars per euro (a stronger euro drains them faster --
    # the correct direction of risk), while EUR-denominated assets (IBKR, Cash) fund
    # euro spending 1:1 and are genuine hedges. USD income (SS, gifts to US family)
    # converts to euros at spot. All aggregates -- Total Portfolio Balance, the
    # withdrawal-rate guardrail, terminal wealth -- are reported in USD-equivalents
    # with EUR balances translated at the year's spot rate, and every USD->EUR
    # conversion event (the Roth sweep, home-sale proceeds, surplus redeposits) is
    # charged the spot rate instead of converting at par.
    sc = scenario or {}
    sc_returns = sc.get('returns')
    sc_inflation = sc.get('inflation')
    sc_fx = sc.get('fx')
    sc_bond = sc.get('bond')
    sc_roth_conv = sc.get('roth_conv')
    sc_death_year = sc.get('death_year')
    sc_first_death_year = sc.get('_first_death_yr')
    sc_tax_mult = sc.get('tax_mult', 1.0)
    sc_ltc = sc.get('ltc_cost', {})
    # SS COLAs follow the path's realized inflation (Tier-1 fix #6).
    MIKE_SS, STEPH_SS = get_ss_timelines(override_m_age, override_s_age, inflation_path=sc_inflation)
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    move_yr = 2026 + (st.session_state.move_age - st.session_state.current_age)

    policy = st.session_state.policy_df.set_index("Asset Category")
    current_balances = st.session_state.asset_balances.copy()
    current_basis = st.session_state.asset_balances.copy()

    EUR_ASSETS = ("IBKR (Active)", "Cash (Slush Fund)")
    PRETAX_ACCOUNTS = ["Cornerstone: Trad 401(k)", "OCC: Trad 401(k)", "Cornerstone: Profit Sharing"]
    ROTH_ACCOUNTS = ["Cornerstone: Roth 401(k)", "OCC: Roth 401(k)"]
    DIV_ASSETS = ("E*TRADE (Legacy)", "IBKR (Active)")
    TAXABLE_ACCOUNTS = ["E*TRADE (Legacy)", "Crypto (Coinbase)", "IBKR (Active)"]

    rmd_divisors = {75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4}

    bal_matrix, draw_matrix, tax_matrix, cont_matrix, wr_matrix = {}, {}, {}, {}, {}
    asset_rows = list(current_balances.keys())

    fx_base = st.session_state.fx_rate if st.session_state.fx_enable else 1.0
    col_in = st.session_state.get('sl_col_ratio', 0.77)
    progressive = st.session_state.get('use_progressive_tax', True)
    div_on = st.session_state.get('model_div_tax', True)
    div_y = st.session_state.get('div_yield', 1.7) / 100.0
    citizen = st.session_state.retain_us_citizenship
    us_ltcg = st.session_state.us_ltcg_rate / 100.0
    roth_first = st.session_state.get('roth_first', True)
    ibkr_aging = st.session_state.get('ibkr_lot_aging', True)
    reset_defer = str(st.session_state.get('great_reset_mode', '')).startswith("Defer")

    def slovenia_graduated_rate(years_held):
        # Slovenian schedular capital-gains rates by holding period (capital gains are
        # taxed at flat schedular rates in Slovenia, NOT through the progressive brackets).
        if years_held > 15:
            return 0.0
        elif years_held > 10:
            return 0.15
        elif years_held > 5:
            return 0.20
        else:
            return 0.25

    def legacy_cg_rate(years_held, slovenia_flag):
        # Residual US layer (treaty savings clause): effective rate = max(SI, US LTCG)
        # while a citizen; SI-only after renouncing (the exit tax below charges the toll).
        if not slovenia_flag:
            return us_ltcg
        sl_rate = slovenia_graduated_rate(years_held)
        if citizen:
            return max(sl_rate, us_ltcg)
        return sl_rate

    # State trackers
    spend_level = 1.0
    cumulative_gifts_tracker = 0.0
    cpi_index = 1.0
    # IBKR lot ledger: [weighted-average acquisition year, weight]. Additions update the
    # weighted year; pro-rata draws scale the weight and leave the average unchanged. This
    # lets IBKR lots AGE into the Slovenian holding-period schedule like the legacy lots,
    # instead of paying a flat rate forever. (Tier-2 fix #13.)
    ibkr_lot = [2026.0, 0.0]
    reset_done = False
    exit_tax_done = False

    for yr in range(2026, 2090):
        age = st.session_state.current_age + (yr - 2026)

        usd_yr_return = st.session_state.usd_market_return / 100.0
        eur_yr_return = st.session_state.eur_market_return / 100.0
        i_rate = st.session_state.inflation_rate / 100.0

        if return_overrides is not None and yr in return_overrides:
            usd_yr_return, eur_yr_return = return_overrides[yr]
        if sc_returns is not None and yr in sc_returns:
            usd_yr_return, eur_yr_return = sc_returns[yr][0], sc_returns[yr][1]
        if sc_inflation is not None and yr in sc_inflation:
            i_rate = sc_inflation[yr]
        # PFIC/PRIIPs vehicle drag on the EUR equity sleeve (Plan B: a US citizen investing
        # from the EU faces costlier vehicles; applies to deterministic AND stochastic paths).
        eur_yr_return -= st.session_state.get('eur_return_drag', 0.0) / 100.0
        # EUR/USD spot for the year (USD per EUR). Defined in BOTH phases: it prices any
        # conversion event pre-move and all cross-currency funding post-move.
        fx_spot = sc_fx[yr] if (sc_fx is not None and yr in sc_fx) else fx_base

        if yr > 2026:
            cpi_index *= (1 + i_rate)

        bond_return = st.session_state.bond_mean / 100.0
        if sc_bond is not None and yr in sc_bond:
            bond_return = sc_bond[yr]

        # Inflation-linked sleeve inside the bond bucket (real yield + realized inflation)
        if st.session_state.get('linker_enable', False) and st.session_state.get('linker_frac', 0.0) > 0:
            lf = st.session_state.linker_frac
            linker_return = (st.session_state.get('linker_real_yield', 1.0) / 100.0) + i_rate
            bond_return = (1 - lf) * bond_return + lf * linker_return

        # Bifurcated glide path
        if st.session_state.glide_enable and st.session_state.get('glide_alloc_mode', True):
            if age <= st.session_state.glide_start_age:
                w_eq = st.session_state.glide_eq_start
            elif age >= st.session_state.glide_end_age:
                w_eq = st.session_state.glide_eq_end
            else:
                frac = (age - st.session_state.glide_start_age) / max(1, (st.session_state.glide_end_age - st.session_state.glide_start_age))
                w_eq = st.session_state.glide_eq_start + frac * (st.session_state.glide_eq_end - st.session_state.glide_eq_start)
            usd_yr_return = w_eq * usd_yr_return + (1 - w_eq) * bond_return
            eur_yr_return = w_eq * eur_yr_return + (1 - w_eq) * bond_return
        elif st.session_state.glide_enable and age >= st.session_state.glide_start_age:
            years_in_glide = min(age, st.session_state.glide_end_age) - st.session_state.glide_start_age + 1
            usd_yr_return -= (years_in_glide * (st.session_state.usd_glide_reduction / 100.0))
            eur_yr_return -= (years_in_glide * (st.session_state.eur_glide_reduction / 100.0))

        if st.session_state.sorr_enable and (st.session_state.sorr_start_yr <= yr < (st.session_state.sorr_start_yr + st.session_state.sorr_duration)):
            usd_yr_return = st.session_state.sorr_return / 100.0
            eur_yr_return = st.session_state.sorr_return / 100.0

        is_slovenia = (yr >= move_yr)
        col_ratio = col_in if is_slovenia else 1.0           # euros per $1 of US-equivalent lifestyle
        usd_to_sc = (1.0 / fx_spot) if is_slovenia else 1.0  # spending-ccy units per USD
        sc_to_usd = fx_spot if is_slovenia else 1.0          # USD per spending-ccy unit

        def _ibkr_add(amount_eur):
            if amount_eur <= 0:
                return
            w = ibkr_lot[1]
            ibkr_lot[0] = (ibkr_lot[0] * w + yr * amount_eur) / (w + amount_eur)
            ibkr_lot[1] = w + amount_eur

        div_tax_usd_yr = [0.0]

        def _apply_return_with_divs(asset):
            # Apply the year's return; for taxable dividend-paying sleeves, tax the
            # dividend annually (US qualified rate pre-move; Slovenia's flat 25% -- with
            # the residual US layer for citizens -- post-move). Net dividends are
            # reinvested, so basis rises by the net amount. (Tier-2 fix #15.)
            if asset == "Cash (Slush Fund)":
                ret = 0.0
            elif asset == "IBKR (Active)":
                ret = eur_yr_return
            else:
                ret = usd_yr_return
            bal = current_balances[asset]
            if div_on and asset in DIV_ASSETS and bal > 0:
                div_native = bal * div_y
                if is_slovenia:
                    drate = max(0.25, us_ltcg) if citizen else 0.25
                else:
                    drate = us_ltcg
                dtax = div_native * drate * sc_tax_mult
                current_balances[asset] = bal * (1 + ret) - dtax
                current_basis[asset] += max(0.0, div_native - dtax)
                div_tax_usd_yr[0] += dtax * (fx_spot if asset in EUR_ASSETS else 1.0)
            else:
                current_balances[asset] = bal * (1 + ret)

        def _usd_equiv_total():
            # Tier-1 fix #2: aggregates translate EUR sleeves at the year's spot rate
            # instead of summing euros and dollars 1:1.
            return sum(b * (fx_spot if a in EUR_ASSETS else 1.0) for a, b in current_balances.items())

        # One-time transfer into IBKR at the move year (e.g. Plan B's $100k relocation
        # capital): USD buys euros at the year's spot rate, starts the SI holding clock.
        if yr == move_yr and st.session_state.get('move_lump_ibkr_usd', 0) > 0:
            _lump_eur = st.session_state.move_lump_ibkr_usd / fx_spot
            current_balances["IBKR (Active)"] += _lump_eur
            current_basis["IBKR (Active)"] += _lump_eur
            _ibkr_add(_lump_eur)

        # ---------------------------------------------------------------------
        # ACCUMULATION PHASE
        # ---------------------------------------------------------------------
        if yr < start_yr:
            yr_conts = {}
            for asset in current_balances.keys():
                if asset in policy.index:
                    esc = policy.loc[asset, "Annual Savings Escalator (%)"] / 100.0
                    curr_cont = policy.loc[asset, "Current State"] * ((1 + esc) ** (yr - 2026))
                    nb_cont = policy.loc[asset, "Northbrook Grind"] * ((1 + esc) ** (yr - 2026))
                    cont = curr_cont if yr < st.session_state.nb_start_yr else nb_cont
                else:
                    cont = 0
                _apply_return_with_divs(asset)
                yr_conts[asset] = cont
                if asset in EUR_ASSETS:
                    cont_native = cont / fx_spot  # USD savings buy euros at spot
                    if asset == "IBKR (Active)":
                        _ibkr_add(cont_native)
                else:
                    cont_native = cont
                current_balances[asset] += cont_native
                current_basis[asset] += cont_native

            cont_matrix[yr] = yr_conts
            bal_col = {a: b * (fx_spot if a in EUR_ASSETS else 1.0) for a, b in current_balances.items()}
            bal_col["Total Portfolio Balance"] = sum(bal_col.values())
            bal_matrix[yr] = bal_col
            continue

        # ---------------------------------------------------------------------
        # ONE-TIME EVENTS (balance moves happen pre-returns, as before; their
        # TAXES are computed below once the year's tax machinery exists)
        # ---------------------------------------------------------------------
        pending_sweep_ordinary_usd = 0.0
        pending_event_flat_tax_usd = 0.0
        if yr == start_yr:
            holding_years = max(0, start_yr - st.session_state.nb_start_yr)
            if holding_years > 0:
                principal = st.session_state.home_price - st.session_state.down_payment
                r_mtg = (st.session_state.mtg_rate / 100) / 12
                n_mtg = 30 * 12
                end_prop_val = st.session_state.home_price * ((1 + (st.session_state.ann_apprec / 100)) ** holding_years)
                pmts_made = holding_years * 12
                if r_mtg > 0:
                    end_mtg_bal = principal * (((1 + r_mtg) ** n_mtg - (1 + r_mtg) ** pmts_made) / ((1 + r_mtg) ** n_mtg - 1))
                else:
                    end_mtg_bal = principal - ((principal / n_mtg) * pmts_made)
                net_proceeds = max(0, end_prop_val - end_mtg_bal - (end_prop_val * 0.06))
            else:
                net_proceeds = 0
            # USD proceeds buy euros at the year's spot rate (no more par conversion).
            half_eur = (net_proceeds / 2.0) / fx_spot
            current_balances["IBKR (Active)"] += half_eur
            current_basis["IBKR (Active)"] += half_eur
            _ibkr_add(half_eur)
            current_balances["Cash (Slush Fund)"] += half_eur
            current_basis["Cash (Slush Fund)"] += half_eur

        if st.session_state.execute_great_reset and not reset_done and yr >= start_yr:
            do_sweep = (age >= 60) if reset_defer else (yr == start_yr)
            if do_sweep:
                sweep_val = sum(current_balances[r] for r in ROTH_ACCOUNTS)
                sweep_basis = sum(current_basis[r] for r in ROTH_ACCOUNTS)
                sweep_earnings = max(0.0, sweep_val - sweep_basis)
                if sweep_val > 0:
                    if age < 60:
                        # NON-QUALIFIED Roth 401(k) distribution (59.5 rule): the earnings
                        # slice is US ordinary income PLUS a 10% early-withdrawal penalty.
                        # The old model treated this sweep as tax-free, which is only true
                        # at 59.5+. (Tier-1 fix #4.)
                        pending_sweep_ordinary_usd = sweep_earnings
                        pending_event_flat_tax_usd += 0.10 * sweep_earnings * sc_tax_mult
                    if is_slovenia:
                        # Post-move sweep: under the model's own Roth-Trap assumption,
                        # Slovenia taxes the distribution.
                        pending_event_flat_tax_usd += sweep_val * (st.session_state.tax_roth / 100.0) * sc_tax_mult
                    sweep_eur = sweep_val / fx_spot
                    current_balances["IBKR (Active)"] += sweep_eur
                    current_basis["IBKR (Active)"] += sweep_eur
                    _ibkr_add(sweep_eur)
                    for r in ROTH_ACCOUNTS:
                        current_balances[r] = 0
                        current_basis[r] = 0
                reset_done = True

        # Apply returns (with annual dividend taxation on taxable sleeves)
        for asset in current_balances.keys():
            _apply_return_with_divs(asset)

        current_portfolio = _usd_equiv_total()

        # 1. Baseline Target Determination (today's USD purchasing power, CPI-inflated)
        if age < 70:
            base_spend_usd = st.session_state.spend_golden
            floor_base_usd = st.session_state.floor_golden
        elif age < 85:
            base_spend_usd = st.session_state.spend_middle
            floor_base_usd = st.session_state.floor_middle
        else:
            base_spend_usd = st.session_state.spend_wind
            floor_base_usd = st.session_state.floor_wind

        target_lifestyle_usd = base_spend_usd * cpi_index
        floor_usd_inflated = floor_base_usd * cpi_index
        # USD-equivalent COST of that lifestyle: translate the basket to euros via the
        # cost-of-living ratio, then back to dollars at the year's spot rate. A stronger
        # euro RAISES the dollar cost of the Slovenian life -- the correct risk direction.
        target_cost_usd_equiv = target_lifestyle_usd * col_ratio * sc_to_usd

        ss_m, ss_s = MIKE_SS.get(yr, 0), STEPH_SS.get(yr, 0)
        # Survivor scenario: after the FIRST death, the survivor keeps the LARGER of the two
        # benefits and the smaller one is lost entirely. (If both haven't yet claimed when
        # the first death occurs, the larger eventual stream is what carries forward.)
        in_survivor_phase = (sc_first_death_year is not None and yr > sc_first_death_year)
        filing_single = in_survivor_phase and st.session_state.survivor_enable
        if in_survivor_phase:
            gross_ss_usd = max(ss_m, ss_s) * (1 - sc.get('ss_haircut', 0.0))
        else:
            gross_ss_usd = (ss_m + ss_s) * (1 - sc.get('ss_haircut', 0.0))
        # US tax on SS persists even after the move under the treaty's savings clause
        # (US taxes its citizens under normal US rules regardless of residence).
        taxable_ss_usd = gross_ss_usd * (st.session_state.ss_taxable_pct / 100.0) if gross_ss_usd > 0 else 0.0
        if progressive:
            # Taxable SS runs through the real US brackets; a survivor files SINGLE
            # (half-width brackets, half the deduction), which IS the widow's penalty --
            # no flat surcharge needed in this mode.
            us_ss_tax_usd = us_ordinary_tax(taxable_ss_usd, cpi_index, filing_single) * sc_tax_mult
        else:
            widow_mult = st.session_state.survivor_tax_surcharge if filing_single else 1.0
            us_ss_tax_usd = taxable_ss_usd * (st.session_state.us_ss_tax_rate / 100.0) * sc_tax_mult * widow_mult
        # Slovenia (residence country) may levy additional tax once resident; model the
        # NET incremental amount after US foreign-tax-credit offset (default 0).
        sl_ss_tax_usd = (gross_ss_usd * (st.session_state.sl_ss_net_rate / 100.0)) if (gross_ss_usd > 0 and is_slovenia) else 0.0
        irs_shadow_tax_usd = us_ss_tax_usd + sl_ss_tax_usd
        net_ss_usd = gross_ss_usd - irs_shadow_tax_usd

        # --- Slovenian state (ZPIZ) pension (Plan B) ---
        # EUR-denominated income: funds euro spending 1:1 (no FX crossing). Accrual uses
        # the statutory schedule (~26.5% of the basis at 15 contribution years + ~1.36%/yr
        # beyond) over the years worked in Slovenia (move -> retirement); basis is CPI-
        # indexed (wage growth = inflation per the Plan B assumption). The flat net-tax
        # input approximates the SI pension credit + the residual US layer (a foreign
        # pension is US-taxable, but at this size it sits mostly under the deduction).
        # Survivor keeps the LARGER single benefit, mirroring the SS treatment.
        si_pension_net_sc = 0.0
        if st.session_state.get('si_pension_enable', False) and is_slovenia:
            _yrs_c = max(0, st.session_state.ret_age - st.session_state.move_age)
            if _yrs_c >= 15:
                _acc = min(1.0, (26.5 + 1.36 * (_yrs_c - 15)) / 100.0)
                _p_each = st.session_state.si_pension_basis_eur * _acc * cpi_index
                _claim = st.session_state.si_pension_claim_age
                _s_age = age - st.session_state.mc_wife_age_offset
                _pm = _p_each if age >= _claim else 0.0
                _ps = _p_each if _s_age >= _claim else 0.0
                _gross_p = max(_pm, _ps) if in_survivor_phase else (_pm + _ps)
                si_pension_net_sc = _gross_p * (1 - st.session_state.si_pension_tax_pct / 100.0)
        si_pension_usd_equiv = si_pension_net_sc * sc_to_usd

        # ---------------------------------------------------------------------
        # ORDINARY-INCOME TAX MACHINERY for the year (Tier-1 fix #3).
        # Progressive mode (default): every dollar of ordinary income (pre-tax
        # draws, RMDs, conversions, sweep earnings) stacks on top of taxable SS
        # through the US brackets, and through Slovenia's brackets once resident;
        # the combined liability is max(US, SI) -- the savings-clause + FTC
        # outcome. Previously the entire tax-smoothing draw was charged a flat
        # 16% base rate. Legacy mode keeps the flat base/excess rates but now
        # applies the standard-deduction split to EVERY ordinary draw (the
        # smoothing draw included).
        # ---------------------------------------------------------------------
        if progressive:
            _tallies = {'us': taxable_ss_usd, 'si': 0.0}

            def _ord_total(us_t, si_t):
                us = us_ordinary_tax(us_t, cpi_index, filing_single)
                if is_slovenia:
                    return max(us, si_ordinary_tax(si_t, cpi_index) * fx_spot)
                return us

            def ordinary_tax_for(gross_usd):
                if gross_usd <= 0:
                    return 0.0
                before = _ord_total(_tallies['us'], _tallies['si'])
                after = _ord_total(_tallies['us'] + gross_usd,
                                   _tallies['si'] + (gross_usd / fx_spot if is_slovenia else 0.0))
                return max(0.0, after - before) * sc_tax_mult

            def commit_ordinary(gross_usd):
                t = ordinary_tax_for(gross_usd)
                _tallies['us'] += gross_usd
                if is_slovenia:
                    _tallies['si'] += gross_usd / fx_spot
                return t
        else:
            _legacy_drip_r = ((st.session_state.tax_pretax_base / 100.0) if is_slovenia else 0.12) * sc_tax_mult
            _legacy_high_r = ((st.session_state.tax_pretax_excess / 100.0) if is_slovenia else 0.22) * sc_tax_mult
            _std_left = [30000 * cpi_index]

            def ordinary_tax_for(gross_usd):
                if gross_usd <= 0:
                    return 0.0
                b = min(gross_usd, _std_left[0])
                return b * _legacy_drip_r + (gross_usd - b) * _legacy_high_r

            def commit_ordinary(gross_usd):
                t = ordinary_tax_for(gross_usd)
                _std_left[0] = max(0.0, _std_left[0] - gross_usd)
                return t

        def _gross_for_net_usd(net_usd):
            # Invert net = gross - tax(gross) by fixed-point iteration (marginal < 1).
            if net_usd <= 0:
                return 0.0
            g = net_usd / 0.7
            for _ in range(12):
                g = net_usd + ordinary_tax_for(g)
            return g

        roth_tax_rate = ((st.session_state.tax_roth / 100.0) if is_slovenia else 0.0) * sc_tax_mult
        legacy_lot_rate = legacy_cg_rate(yr - 2026, is_slovenia) * sc_tax_mult
        if ibkr_aging:
            ibkr_rate = legacy_cg_rate(max(0.0, yr - ibkr_lot[0]), is_slovenia) * sc_tax_mult
        else:
            ibkr_rate = ((st.session_state.tax_cap_gains / 100.0) if is_slovenia else 0.15) * sc_tax_mult

        # 2. Dynamic Gifting Math (Smoothed Recalibrating Annuity)
        # The forward "terminal pie" projection uses the assumed long-run return
        # (plan_return), NOT the realized/stochastic return for the year. Draws and the
        # portfolio are USD-equivalents so the projection is in one consistent unit.
        base_gift_usd = 0
        if st.session_state.gifting_enable and st.session_state.gift_start_age <= age <= st.session_state.gift_end_age:
            plan_return = st.session_state.usd_market_return / 100.0
            n_total = 100 - age
            approx_annual_draw = max(0, target_cost_usd_equiv - net_ss_usd - si_pension_usd_equiv)

            if plan_return == i_rate:
                fv_draws = approx_annual_draw * n_total * (1 + plan_return) ** (n_total - 1)
            else:
                fv_draws = approx_annual_draw * (((1 + plan_return) ** n_total - (1 + i_rate) ** n_total) / (plan_return - i_rate))

            fv_past_gifts = cumulative_gifts_tracker * (1 + plan_return) ** n_total
            total_fv_nogift = max(0, (current_portfolio * (1 + plan_return) ** n_total) - fv_draws + fv_past_gifts)

            target_total_gift_fv = (st.session_state.dynamic_gift_pct / 100.0) * total_fv_nogift
            remaining_gift_fv_needed = max(0, target_total_gift_fv - fv_past_gifts)

            n_rem_gifts = st.session_state.gift_end_age - age + 1
            if n_rem_gifts > 0 and plan_return > 0:
                fvifa = (((1 + plan_return) ** n_rem_gifts) - 1) / plan_return
                growth_after_gifts = (1 + plan_return) ** (100 - st.session_state.gift_end_age)
                base_gift_usd = remaining_gift_fv_needed / (fvifa * growth_after_gifts)

        # 3. Guardrails Logic -- withdrawal rate tested in consistent USD-equivalents
        # (EUR sleeves translated at spot in current_portfolio; the lifestyle draw is the
        # USD-equivalent COST of the euro basket).
        current_wr = 0.0
        if current_portfolio > 0:
            eval_lifestyle_draw = max(0, (target_cost_usd_equiv * spend_level) - net_ss_usd - si_pension_usd_equiv)
            current_wr = eval_lifestyle_draw / current_portfolio

            if st.session_state.guardrails_enable:
                if current_wr > (st.session_state.slash_trigger / 100.0):
                    floor_level = floor_usd_inflated / target_lifestyle_usd
                    spend_level = floor_level
                elif current_wr < (st.session_state.recovery_trigger / 100.0) and spend_level < 1.0:
                    # Restoration rate combines the chosen raise with inflation so the
                    # spend_level ratio recovers in real terms.
                    recovery_rate = (st.session_state.raise_pct + st.session_state.inflation_rate) / 100.0
                    spend_level = min(1.0, spend_level * (1 + recovery_rate))
        else:
            spend_level = 1.0

        # 4. Finalize Actual Targets
        actual_lifestyle_usd = target_lifestyle_usd * spend_level
        actual_gift_usd = base_gift_usd * spend_level

        # Survivor scenario: between the first and second death, a surviving single person
        # spends less than the couple did, but NOT half. Gifting continues at the couple's
        # intended pace (it's a bequest goal, not consumption).
        if (st.session_state.survivor_enable and in_survivor_phase
                and not (sc_death_year is not None and yr > sc_death_year)):
            actual_lifestyle_usd *= st.session_state.survivor_expense_ratio

        # Longevity: after both spouses have died, the household no longer spends or gifts.
        if sc_death_year is not None and yr > sc_death_year:
            actual_lifestyle_usd = 0.0
            actual_gift_usd = 0.0

        # Long-term-care shock: extra real (2026 $) cost, inflated to nominal. It is part
        # of the consumption basket, so it shares the cost-of-living translation below.
        ltc_extra_usd = sc_ltc.get(yr, 0.0) * cpi_index if sc_ltc else 0.0
        actual_lifestyle_usd += ltc_extra_usd

        # Capture actual WR for tracking (USD-equivalent cost of the actual basket)
        actual_cost_usd_equiv = actual_lifestyle_usd * col_ratio * sc_to_usd
        final_eval_draw = max(0, actual_cost_usd_equiv - net_ss_usd - si_pension_usd_equiv)
        final_wr = final_eval_draw / current_portfolio if current_portfolio > 0 else 0.0
        wr_matrix[yr] = final_wr

        # Update phantom ledger for next year's smoothed gift calculation
        cumulative_gifts_tracker = cumulative_gifts_tracker * (1 + usd_yr_return) + actual_gift_usd

        # ---------------------------------------------------------------------
        # SPENDING NEEDS in the SPENDING CURRENCY (euros post-move, dollars before).
        # Lifestyle is a CONSUMPTION BASKET: translated by the cost-of-living ratio
        # (price level), NOT by the exchange rate. SS and gifts are USD cash flows:
        # converted at the year's spot rate. The FX rate therefore only prices
        # currency crossings -- the economically correct transmission.
        # ---------------------------------------------------------------------
        lifestyle_sc = actual_lifestyle_usd * col_ratio
        gift_sc = actual_gift_usd * usd_to_sc
        ss_sc = net_ss_usd * usd_to_sc
        remaining_need_sc = max(0, (lifestyle_sc + gift_sc) - ss_sc - si_pension_net_sc)

        # ---------------------------------------------------------------------
        # ONE-TIME EVENT TAXES, funded through the waterfall.
        # ---------------------------------------------------------------------
        event_tax_usd = 0.0
        if pending_sweep_ordinary_usd > 0:
            event_tax_usd += commit_ordinary(pending_sweep_ordinary_usd)
        event_tax_usd += pending_event_flat_tax_usd
        if (not citizen) and (not exit_tax_done) and yr >= move_yr:
            # IRC 877A covered-expatriate EXIT TAX (Tier-2 fix #16): renouncing
            # citizenship triggers a deemed sale of taxable lots; gains above the
            # exclusion are taxed at US LTCG and basis steps up to market. Renouncing
            # is no longer free.
            unrealized_usd = 0.0
            for a in TAXABLE_ACCOUNTS:
                fxm = fx_spot if a in EUR_ASSETS else 1.0
                unrealized_usd += max(0.0, current_balances[a] - current_basis[a]) * fxm
            exclusion = EXIT_TAX_EXCLUSION_USD * cpi_index
            exit_tax = max(0.0, unrealized_usd - exclusion) * us_ltcg * sc_tax_mult
            event_tax_usd += exit_tax
            for a in TAXABLE_ACCOUNTS:
                current_basis[a] = max(current_basis[a], current_balances[a])
            exit_tax_done = True
        remaining_need_sc += event_tax_usd * usd_to_sc

        # --- Roth Conversion Ladder ---
        # Conversion is US-taxable ordinary income ALWAYS; post-move it is ALSO inside the
        # Slovenian base (the double-hit). In progressive mode it stacks through the real
        # brackets on top of SS and the smoothing draw; the tax is funded from other assets.
        if sc_roth_conv is not None:
            rc_annual, rc_start, rc_end = sc_roth_conv
        else:
            rc_annual, rc_start, rc_end = (st.session_state.roth_conv_annual,
                                           st.session_state.roth_conv_start_age,
                                           st.session_state.roth_conv_end_age)
        conversion_tax_usd = 0.0
        if rc_annual > 0 and rc_start <= age <= rc_end:
            conv_nominal = rc_annual * cpi_index
            pretax_avail = sum(current_balances[p] for p in PRETAX_ACCOUNTS if current_balances[p] > 0)
            conv_amt = min(conv_nominal, pretax_avail)
            if conv_amt > 0:
                roth_target = "Cornerstone: Roth 401(k)"
                for p in PRETAX_ACCOUNTS:
                    if current_balances[p] > 0:
                        share = conv_amt * (current_balances[p] / pretax_avail)
                        current_balances[p] -= share
                current_balances[roth_target] += conv_amt
                current_basis[roth_target] += conv_amt
                if progressive:
                    conversion_tax_usd = commit_ordinary(conv_amt)
                else:
                    us_conv_rate = (st.session_state.roth_conv_us_rate / 100.0)
                    sl_conv_rate = (st.session_state.tax_pretax_base / 100.0) if is_slovenia else 0.0
                    conversion_tax_usd = conv_amt * (us_conv_rate + sl_conv_rate) * sc_tax_mult
                remaining_need_sc += conversion_tax_usd * usd_to_sc

        # ---------------------------------------------------------------------
        # DRAWDOWN WATERFALL
        # ---------------------------------------------------------------------
        draws, taxes = {a: 0.0 for a in asset_rows}, {a: 0.0 for a in asset_rows}

        def draw_pretax_gross(asset, gross_usd):
            # Mandatory/targeted GROSS ordinary draw (RMDs, smoothing); returns net USD.
            if gross_usd <= 0 or current_balances[asset] <= 0:
                return 0.0
            g = min(gross_usd, current_balances[asset])
            t = commit_ordinary(g)
            draws[asset] += g
            taxes[asset] += t
            current_balances[asset] -= g
            return g - t

        def pull_net_pretax(asset, need_sc):
            # Draw enough GROSS ordinary income to net `need_sc` in spending currency.
            if need_sc <= 0 or current_balances[asset] <= 0:
                return 0.0
            need_usd = need_sc * sc_to_usd
            g = min(_gross_for_net_usd(need_usd), current_balances[asset])
            t = commit_ordinary(g)
            draws[asset] += g
            taxes[asset] += t
            current_balances[asset] -= g
            return (g - t) * usd_to_sc

        def pull_net_flat(asset, need_sc, statutory_rate, is_brokerage):
            # Flat/schedular-rate draw (Roth trap rate, capital-gains schedules, cash).
            # Native units per 1 unit of spending currency price the currency crossing.
            if need_sc <= 0 or current_balances[asset] <= 0:
                return 0.0
            is_eur = asset in EUR_ASSETS
            if is_slovenia:
                native_per_sc = 1.0 if is_eur else fx_spot
            else:
                native_per_sc = (1.0 / fx_spot) if is_eur else 1.0
            req_net_native = need_sc * native_per_sc
            if is_brokerage:
                gain_ratio = max(0.0, (current_balances[asset] - current_basis[asset]) / current_balances[asset])
                eff = statutory_rate * gain_ratio
            else:
                eff = statutory_rate
            req_gross = req_net_native / (1 - eff) if eff < 1 else req_net_native
            g = min(req_gross, current_balances[asset])
            t = g * eff
            n = g - t
            draws[asset] += g
            taxes[asset] += t
            portion = g / current_balances[asset]
            current_basis[asset] -= current_basis[asset] * portion
            if asset == "IBKR (Active)":
                ibkr_lot[1] *= (1 - portion)
            current_balances[asset] -= g
            return n / native_per_sc

        pre_req_sc_generated = 0.0

        if age >= 75:
            # RMDs: mandatory gross draws through the ordinary-income machinery (the
            # brackets, not a hand-allocated deduction split, decide the tax).
            divisor = rmd_divisors.get(min(age, 100), 6.4)
            for pretax in PRETAX_ACCOUNTS:
                if current_balances[pretax] > 0:
                    rmd_gross = current_balances[pretax] / divisor
                    net_usd = draw_pretax_gross(pretax, rmd_gross)
                    pre_req_sc_generated += net_usd * usd_to_sc

        elif st.session_state.enable_smoothing and age >= 60:
            # Lifetime-tax-smoothing early draw. The WHOLE draw now stacks through the
            # progressive brackets (or the legacy deduction split) -- previously it was
            # all charged the flat base rate, dramatically understating the cost.
            draw_val = override_early_draw if override_early_draw is not None else st.session_state.target_early_draw
            target_early_gross = draw_val * cpi_index
            total_pretax = sum(current_balances[p] for p in PRETAX_ACCOUNTS if current_balances[p] > 0)
            if total_pretax > 0 and target_early_gross > 0:
                actual_total_draw = min(target_early_gross, total_pretax)
                allocations = {p: current_balances[p] / total_pretax for p in PRETAX_ACCOUNTS if current_balances[p] > 0}
                for pretax, prop in allocations.items():
                    net_usd = draw_pretax_gross(pretax, actual_total_draw * prop)
                    pre_req_sc_generated += net_usd * usd_to_sc

        if pre_req_sc_generated >= remaining_need_sc:
            # Surplus net income is redeposited into IBKR -- BUYING EUROS AT SPOT.
            excess_sc = pre_req_sc_generated - remaining_need_sc
            excess_eur = excess_sc if is_slovenia else excess_sc / fx_spot
            current_balances["IBKR (Active)"] += excess_eur
            current_basis["IBKR (Active)"] += excess_eur
            _ibkr_add(excess_eur)
            remaining_need_sc = 0
        else:
            remaining_need_sc -= pre_req_sc_generated

            # Waterfall order: draining the SI-taxed Roth before tax-free cash is the
            # "Roth Trap" thesis (every year of Roth growth exits at the trap rate).
            # It is now a TOGGLE so the joint-success engine can adjudicate it.
            if age >= 60 and roth_first:
                for roth in ROTH_ACCOUNTS:
                    remaining_need_sc -= pull_net_flat(roth, remaining_need_sc, roth_tax_rate, False)

            if age >= 60 and (age >= 75 or not st.session_state.enable_smoothing) and remaining_need_sc > 0:
                # Bracket-fill drip: draw ordinary income up to the unused US standard
                # deduction (progressive mode tracks the real remaining room; legacy
                # mode uses its deduction tracker).
                if progressive:
                    std_total = (US_STD_DED_SINGLE if filing_single else US_STD_DED_MFJ) * cpi_index
                    room_gross = max(0.0, std_total - _tallies['us'])
                else:
                    room_gross = _std_left[0]
                total_pretax = sum(current_balances[p] for p in PRETAX_ACCOUNTS if current_balances[p] > 0)
                if total_pretax > 0 and room_gross > 0:
                    need_gross = min(room_gross, _gross_for_net_usd(remaining_need_sc * sc_to_usd), total_pretax)
                    allocations = {p: current_balances[p] / total_pretax for p in PRETAX_ACCOUNTS if current_balances[p] > 0}
                    for pretax, prop in allocations.items():
                        net_usd = draw_pretax_gross(pretax, need_gross * prop)
                        remaining_need_sc = max(0.0, remaining_need_sc - net_usd * usd_to_sc)

            # Cash and HSA (qualified) draw tax-free. E*TRADE and Crypto are taxed on
            # the embedded gain: US cap-gains rate before the move, Slovenia's
            # holding-period schedule (with the residual US layer) after.
            for brok in ["Cash (Slush Fund)", "HSA Pool"]:
                remaining_need_sc -= pull_net_flat(brok, remaining_need_sc, 0.0, False)
            for brok in ["E*TRADE (Legacy)", "Crypto (Coinbase)"]:
                remaining_need_sc -= pull_net_flat(brok, remaining_need_sc, legacy_lot_rate, True)
            remaining_need_sc -= pull_net_flat("IBKR (Active)", remaining_need_sc, ibkr_rate, True)

            if age >= 60 and not roth_first:
                for roth in ROTH_ACCOUNTS:
                    remaining_need_sc -= pull_net_flat(roth, remaining_need_sc, roth_tax_rate, False)

            if age >= 60:
                total_pretax = sum(current_balances[p] for p in PRETAX_ACCOUNTS if current_balances[p] > 0)
                if total_pretax > 0 and remaining_need_sc > 0:
                    allocations = {p: current_balances[p] / total_pretax for p in PRETAX_ACCOUNTS if current_balances[p] > 0}
                    target_net_snapshot = remaining_need_sc
                    for pretax, prop in allocations.items():
                        achieved_sc = pull_net_pretax(pretax, target_net_snapshot * prop)
                        remaining_need_sc -= achieved_sc

        # ---------------------------------------------------------------------
        # REPORTING (everything in USD-equivalents; EUR flows translated at spot)
        # ---------------------------------------------------------------------
        def _usd_eq_map(d):
            return {a: v * (fx_spot if a in EUR_ASSETS else 1.0) for a, v in d.items()}

        draws_usd = _usd_eq_map(draws)
        taxes_usd = _usd_eq_map(taxes)
        total_furs_tax = sum(taxes_usd.values())
        other_tax_usd = event_tax_usd + div_tax_usd_yr[0]
        total_taxes_paid_usd = total_furs_tax + irs_shadow_tax_usd + conversion_tax_usd + other_tax_usd
        total_gross_portfolio = sum(draws_usd.values())

        d_col = draws_usd.copy()
        d_col["Michael's SS"] = ss_m
        d_col["Stephanie's SS"] = ss_s
        d_col["Slovenian Pension (Net)"] = si_pension_net_sc * sc_to_usd
        d_col["-------------------"] = 0
        d_col["Actual Lifestyle Spend"] = actual_lifestyle_usd
        d_col["Actual Generational Drip"] = actual_gift_usd
        d_col["Total Gross Drawn"] = total_gross_portfolio + gross_ss_usd
        d_col["IRS Tax on SS (US)"] = -irs_shadow_tax_usd
        d_col["Portfolio Tax (FURS)"] = -total_furs_tax
        d_col["Other Taxes (Div/Events)"] = -other_tax_usd
        d_col["Less: Taxes Paid"] = -total_taxes_paid_usd
        d_col["Net Funded (Lifestyle + Gift)"] = (total_gross_portfolio + gross_ss_usd) - total_taxes_paid_usd
        draw_matrix[yr] = d_col

        t_col = {a: (taxes[a] / draws[a] if draws[a] > 0 else 0.0) for a in asset_rows}
        # SS tax is computed centrally as a household "shadow tax" rather than per-asset.
        # Survivor-aware attribution: only the larger benefit is received and taxed.
        if in_survivor_phase:
            if ss_m >= ss_s:
                t_col["Michael's SS"] = (irs_shadow_tax_usd / ss_m) if ss_m > 0 else 0.0
                t_col["Stephanie's SS"] = 0.0
            else:
                t_col["Stephanie's SS"] = (irs_shadow_tax_usd / ss_s) if ss_s > 0 else 0.0
                t_col["Michael's SS"] = 0.0
        else:
            gross_ss_total = ss_m + ss_s
            if gross_ss_total > 0:
                t_col["Michael's SS"] = (irs_shadow_tax_usd * (ss_m / gross_ss_total)) / ss_m if ss_m > 0 else 0.0
                t_col["Stephanie's SS"] = (irs_shadow_tax_usd * (ss_s / gross_ss_total)) / ss_s if ss_s > 0 else 0.0
            else:
                t_col["Michael's SS"], t_col["Stephanie's SS"] = 0.0, 0.0
        t_col["Weighted Average"] = total_taxes_paid_usd / (total_gross_portfolio + gross_ss_usd) if (total_gross_portfolio + gross_ss_usd) > 0 else 0
        tax_matrix[yr] = t_col

        b_col = {a: current_balances[a] * (fx_spot if a in EUR_ASSETS else 1.0) for a in asset_rows}
        b_col["Total Portfolio Balance"] = sum(b_col.values())
        bal_matrix[yr] = b_col

    return pd.DataFrame(bal_matrix), pd.DataFrame(draw_matrix), pd.DataFrame(tax_matrix), pd.DataFrame(cont_matrix), pd.Series(wr_matrix)


# -----------------------------------------------------------------------------
# PAGE ROUTING
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SCENARIO SELECTOR (Plan A vs Plan B)
# A defaults PROFILE, applied only when the selector CHANGES (apply-on-change),
# so user edits are never clobbered on Streamlit's reruns. Plan B repurposes the
# policy table's "Northbrook Grind" column as POST-MOVE savings (the switch year
# nb_start_yr doubles as the move year, 2027).
# -----------------------------------------------------------------------------
PLAN_A = "Plan A \u2014 save in US, retire 2044 at 55, move 2045"
PLAN_B = "Plan B \u2014 move to EU in 2027, retire at 63"

def _apply_scenario_profile(name):
    S = st.session_state
    pdf = S.policy_df.copy()
    if name == PLAN_B:
        S.move_age = 38; S.ret_age = 63
        S.nb_start_yr = 2027                  # = the move year: US contributions stop here
        S.execute_great_reset = False         # 401(k)s untouchable at 38; sweep strategy dies
        S.roth_conv_annual = 0                # conversions double-taxed from 2027
        S.spend_golden, S.spend_middle, S.spend_wind = 90000, 85000, 85000
        S.home_price = 0; S.down_payment = 0  # renting in Slovenia; no Northbrook sale
        S.eur_return_drag = 0.4               # PFIC/PRIIPs vehicle squeeze
        S.si_pension_enable = True            # ZPIZ accrues 38 -> 63 (24 years)
        S.move_lump_ibkr_usd = 100000         # one-time relocation capital into IBKR (2027)
        S.enable_smoothing = False            # no strategic pre-tax depletion (ages 60-74)
        # Post-move savings: $5,000/yr HOUSEHOLD TOTAL into IBKR, flat nominal. Everything
        # else freezes (US accounts keep compounding but receive nothing).
        pdf["Northbrook Grind"] = [5000.0 if a == "IBKR (Active)" else 0.0
                                   for a in pdf["Asset Category"]]
    else:
        S.move_age = 56; S.ret_age = 55
        S.nb_start_yr = 2027
        S.execute_great_reset = True
        S.spend_golden, S.spend_middle, S.spend_wind = 127000, 98000, 85000
        S.home_price = 1050000; S.down_payment = 150000
        S.eur_return_drag = 0.0
        S.si_pension_enable = False
        S.move_lump_ibkr_usd = 0
        S.enable_smoothing = True
        pdf["Northbrook Grind"] = [0.0, 20000.0, 30000.0, 0.0, 15000.0,
                                   30000.0, 0.0, 0.0, 0.0, 0.0]
    S.policy_df = pdf
    # Engine semantics changed: invalidate cached MC results so stale numbers never display.
    for k in ("dash_success_v3", "p7_bands_v2", "p8_bands_v2"):
        S.pop(k, None)

st.sidebar.title("Scenario")
_scen = st.sidebar.selectbox("Life plan", [PLAN_A, PLAN_B],
                             index=1 if st.session_state.get("_last_scenario") == PLAN_B else 0,
                             help="Switching applies that plan's default profile ONCE (timeline, "
                                  "savings ledger, spending phases, housing, Great Reset, EUR "
                                  "vehicle drag, Slovenian pension). Your subsequent edits on any "
                                  "page are preserved until you switch again.")
if st.session_state.get("_last_scenario") != _scen:
    _apply_scenario_profile(_scen)
    st.session_state._last_scenario = _scen
if _scen == PLAN_B:
    st.sidebar.caption("Plan B: \"Northbrook Grind\" column = post-move savings ($5k/yr "
                       "household into IBKR). US SS credits stop after 2026; the ZPIZ pension "
                       "accrues over the 24 Slovenian working years and claims at 65.")

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Navigate", ["1. Executive Dashboard", "2. Pre-Set Asset Ledger & Tax Lots", "3. Investment Policy Editor", "4. Real Estate & Relocation", "5. The Great Reset Simulator", "6. Social Security & Pensions", "7. Cash Flow & Slovenian Drip", "8. Yearly Balances (2026-2089)", "9. Tax Torpedo Optimizer", "10. Institutional Stress Testing", "11. Longevity Optimizer (Guardrails)", "12. Monte Carlo Simulation", "13. Roth Conversion Ladder Optimizer", "14. Variance Decomposition (Sobol)", "15. Historical Cohort Backtest"])

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

    # ---- Plan Success Probability (FULL-STRESS Monte Carlo, mirrors Page 12) ----
    # This uses the SAME conditioned, crisis-prone, multi-factor engine as the Monte Carlo
    # page (valuation conditioning + crisis overlay + EUR bond sleeve + stochastic inflation,
    # FX, longevity, LTC, tax-regime drift, SS haircut, survivor scenario). It is intentionally
    # the honest number, not a blue-sky one. Two gauges: "never run out" and the stricter
    # "fully fund the lifestyle you planned." Cached so it doesn't recompute every interaction.
    st.subheader("Plan Success Probability")
    dash_runs = 400

    if st.button("Refresh Success Probability") or 'dash_success_v3' not in st.session_state:
        with st.spinner(f"Running {dash_runs} full-stress simulations (valuation + crisis + all factors)..."):
            st.session_state.dash_success_v3 = dashboard_full_stress_metrics(dash_runs, seed=2026)
    R = st.session_state.dash_success_v3
    never_succ = R['never_deplete']; succ_ages = R['ages']; succ_by_age = R['by_age']
    median_funded = R['median_funded']
    band_full, band_mid, band_low = R['band_full'], R['band_mid'], R['band_low']

    def _band(v): return "#2ca02c" if v >= 85 else ("#ff9800" if v >= 70 else "#d62728")

    g1, g2 = st.columns(2)
    with g1:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=never_succ, number={'suffix': "%", 'font': {'size': 80}},
            title={'text': "Money Never Runs Out<br><span style='font-size:0.9em;color:gray'>(solvent through your lifetime)</span>"},
            gauge={'axis': {'range': [0, 100], 'ticksuffix': "%"},
                   'bar': {'color': _band(never_succ), 'thickness': 0.3},
                   'steps': [{'range': [0, 70], 'color': "rgba(214,39,40,0.18)"},
                             {'range': [70, 85], 'color': "rgba(255,152,0,0.18)"},
                             {'range': [85, 100], 'color': "rgba(44,160,44,0.18)"}],
                   'threshold': {'line': {'color': "black", 'width': 3}, 'thickness': 0.75, 'value': never_succ}}
        ))
        fig_g.update_layout(height=260, margin=dict(l=20, r=20, t=70, b=10))
        st.plotly_chart(fig_g, use_container_width=True)
    with g2:
        # Lifestyle-funding distribution: how fully you fund your TARGET spending. Most paths
        # that aren't at 95%+ are still in the comfortable 85-95% band, not deprivation.
        fig_d = go.Figure()
        fig_d.add_trace(go.Bar(x=[band_full], y=["Lifestyle"], orientation='h',
                               name="Full (95%+)", marker_color='#2ca02c',
                               text=f"{band_full:.0f}%", textposition='inside'))
        fig_d.add_trace(go.Bar(x=[band_mid], y=["Lifestyle"], orientation='h',
                               name="Comfortable (85-95%)", marker_color='#9ecae1',
                               text=f"{band_mid:.0f}%", textposition='inside'))
        fig_d.add_trace(go.Bar(x=[band_low], y=["Lifestyle"], orientation='h',
                               name="Tightened (<85%)", marker_color='#fdae6b',
                               text=f"{band_low:.0f}%", textposition='inside'))
        
        st.markdown("**How fully is your lifestyle funded?**  \n"
                    f"<span style='color:gray;font-size:1.2em'>Typical path funds {median_funded:.0f}% of target</span>",
                    unsafe_allow_html=True)
        fig_d.update_layout(
            barmode='stack', height=230,
            title="",
            xaxis=dict(range=[0, 100], ticksuffix="%",
                       title=dict(text="Share of simulated futures", standoff=25)),
            yaxis=dict(showticklabels=False),
            legend=dict(orientation='h', y=-0.9, x=0.5, xanchor='center',
                        font=dict(size=12)),
            margin=dict(l=10, r=10, t=20, b=90)
        )
        fig_d.update_yaxes(automargin=True)
        st.plotly_chart(fig_d, use_container_width=True,
                        config={'displayModeBar': False})


    # Full histogram of funded ratios so the coarse bands don't hide the shape \u2014 e.g. how
    # much of the "below 85%" mass is a near-miss 80% vs a genuine 40% shortfall.
    fr_list = R.get('funded_ratios', [])
    if fr_list:
        fr_arr = np.clip(np.array(fr_list), 0, 100)
        below85 = fr_arr[fr_arr < 85]
        fig_h = go.Figure(go.Histogram(
            x=fr_arr, xbins=dict(start=0, end=100, size=5),
            marker_color='#6baed6', marker_line=dict(color='white', width=1),
            hovertemplate="%{x} funded: %{y} of futures<extra></extra>"
        ))
        fig_h.add_vline(x=85, line_dash="dot", line_color="#2ca02c", opacity=0.7,
                        annotation_text="85% (comfortable)", annotation_position="top left")
        fig_h.add_vline(x=median_funded, line_dash="dash", line_color="#d62728", opacity=0.8,
                        annotation_text=f"median {median_funded:.0f}%", annotation_position="top right")
        fig_h.update_layout(
            title="Distribution of lifestyle funding across all simulated futures",
            xaxis=dict(title="% of target lifestyle funded", ticksuffix="%", range=[0, 100]),
            yaxis_title="Number of futures", height=340, bargap=0.02,
            margin=dict(l=10, r=10, t=80, b=10)
        )
        st.plotly_chart(fig_h, use_container_width=True)
        if len(below85) > 0:
            st.caption(
                f"Of the futures funding **below 85%**, the spread is what matters: median **{np.median(below85):.0f}%**, "
                f"25th percentile **{np.percentile(below85,25):.0f}%**, and worst 5% near **{np.percentile(below85,5):.0f}%**. "
                f"A bar at 80% is a mild trim; one at 50% is a serious shortfall \u2014 the histogram shows how much of the "
                f"'tightened' bucket is near-miss versus genuinely painful."
            )

    fig_age = go.Figure(go.Scatter(
        x=succ_ages, y=succ_by_age, mode='lines',
        line=dict(color='#08519c', width=4), fill='tozeroy', fillcolor='rgba(8,81,156,0.12)',
        hovertemplate="Age %{x}: %{y:.0f}% chance the money is still there<extra></extra>"
    ))
    fig_age.add_hline(y=85, line_dash="dot", line_color="#2ca02c", opacity=0.6,
                      annotation_text="comfortable (85%)", annotation_position="bottom right")
    fig_age.update_layout(
        title="Chance the money is still there at each age",
        xaxis_title="Age", yaxis=dict(title="Chance money still lasts", range=[0, 101], ticksuffix="%"),
        height=300, margin=dict(l=10, r=10, t=80, b=10)
    )
    st.plotly_chart(fig_age, use_container_width=True)

    # ---- Lifestyle spend: median achieved vs target, by year (real 2026 $) ----
    sp_years = R.get('spend_years', [])
    sp_med = R.get('spend_median', [])
    sp_tgt = R.get('spend_target', [])
    sp_lo = R.get('spend_p25', []); sp_hi = R.get('spend_p75', [])
    sa = R.get('start_age', st.session_state.current_age)
    if sp_years:
        # Trim trailing years where everyone has died (median is None).
        valid = [i for i, v in enumerate(sp_med) if v is not None]
        if valid:
            lo_i, hi_i = valid[0], valid[-1] + 1
            yy = sp_years[lo_i:hi_i]
            med = sp_med[lo_i:hi_i]; tgt = sp_tgt[lo_i:hi_i]
            p25 = sp_lo[lo_i:hi_i]; p75 = sp_hi[lo_i:hi_i]
            fig_sp = go.Figure()
            # 25-75 band (only where defined).
            band_x = [y for y, a, b in zip(yy, p25, p75) if a is not None and b is not None]
            band_lo = [a for a in p25 if a is not None]; band_hi = [b for b in p75 if b is not None]
            if band_x:
                fig_sp.add_trace(go.Scatter(x=band_x + band_x[::-1], y=band_hi + band_lo[::-1],
                                            fill='toself', fillcolor='rgba(8,81,156,0.10)',
                                            line=dict(color='rgba(0,0,0,0)'), hoverinfo='skip',
                                            name='25th-75th percentile', showlegend=True))
            fig_sp.add_trace(go.Scatter(x=yy, y=tgt, mode='lines', name='Target lifestyle',
                                        line=dict(color='#d62728', width=2, dash='dash'),
                                        hovertemplate="%{x}: target $%{y:,.0f}<extra></extra>"))
            fig_sp.add_trace(go.Scatter(x=yy, y=med, mode='lines', name='Typical (median) achieved',
                                        line=dict(color='#08519c', width=4),
                                        hovertemplate="%{x}: median $%{y:,.0f}<extra></extra>"))
            fig_sp.update_layout(
                title=dict(text="Lifestyle spend: typical achieved vs target (real 2026 $)",
                           y=0.97, yanchor='top'),
                xaxis_title="Year", yaxis=dict(title="Annual spend (2026 $)", tickprefix="$"),
                height=360, legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center'),
                margin=dict(l=10, r=10, t=95, b=10)
            )
            st.plotly_chart(fig_sp, use_container_width=True)
            # Plain-language gap summary.
            med_arr = np.array([m for m in med if m is not None])
            tgt_arr = np.array([t for t, m in zip(tgt, med) if m is not None])
            avg_gap = 100.0 * (1 - np.mean(med_arr) / np.mean(tgt_arr)) if np.mean(tgt_arr) > 0 else 0
            st.caption(
                f"The blue line is what you'd *typically* get to spend each year (median across {dash_runs} "
                f"stress-tested futures), in today's dollars; the dashed red line is your target. The shaded "
                f"band is the 25th-75th percentile range. On average the typical path runs about "
                f"**{avg_gap:.0f}% below target** \u2014 the gap reflects guardrail trims in weaker-market years. "
                "Both are post-tax, real (inflation-adjusted) figures, scored only while the household is living."
            )

    verdict = ("on very solid ground" if never_succ >= 85 else
               "in reasonable shape, with real risk to watch" if never_succ >= 70 else
               "facing meaningful shortfall risk")
    st.markdown(
        f"**In plain terms:** across {dash_runs} simulated futures \u2014 stress-tested for today's high "
        f"valuations, market crashes, inflation, currency swings, long life, care costs, and tax/benefit "
        f"changes \u2014 your money lasts your lifetime about **{never_succ:.0f}%** of the time, so you're "
        f"{verdict}. On lifestyle: the *typical* future funds about **{median_funded:.0f}%** of your target "
        f"spending, with **{band_full:.0f}%** of futures funding it fully (95%+), **{band_mid:.0f}%** "
        f"funding a still-comfortable 85-95%, and **{band_low:.0f}%** requiring a real tightening below 85%. "
        f"The reason full funding isn't higher is that the plan's guardrails *deliberately* trim spending in "
        f"weak markets to keep you solvent \u2014 that trade-off is exactly why the money lasts."
    )
    st.caption(
        "This is the **honest, fully stress-tested** view \u2014 it mirrors the Monte Carlo page's conditioned, "
        "crisis-prone engine, not a best-case projection. 'Full lifestyle' is a deliberately strict bar (95%+ "
        "of target every year); a path funding 90% is comfortable, not a failure, which is why the distribution "
        "is more informative than a single pass/fail. Adjust stress assumptions on Page 12."
    )

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
        chart_draws['Roth Draw'] = chart_draws['Cornerstone: Roth 401(k)'] + chart_draws['OCC: Roth 401(k)']
        # ZPIZ pension is its OWN series, not lumped into Social Security: different payer,
        # different currency (EUR -- no FX risk against the euro liability), different
        # political risk. Shown in USD-equivalents at spot like everything else.
        chart_draws['Slovenian Pension'] = chart_draws['Slovenian Pension (Net)']

        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Brokerage & Cash Draw'], name='Brokerage & Cash Draw'), secondary_y=False)
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Pre-Tax Draw'], name='Pre-Tax Draw'), secondary_y=False)
        if chart_draws['Roth Draw'].sum() > 0:
            fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Roth Draw'], name='Roth Draw'), secondary_y=False)
        fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Social Security'], name='Social Security'), secondary_y=False)
        if chart_draws['Slovenian Pension'].sum() > 0:
            fig2.add_trace(go.Bar(x=chart_draws.index, y=chart_draws['Slovenian Pension'], name='Slovenian Pension (ZPIZ)'), secondary_y=False)
        
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
            # Primary figures come from the 400-run stress-tested distribution (same engine as the
            # gauges above), NOT the single deterministic path -- gifting is the most variable
            # output across futures, so median + 10th-percentile downside are far more honest.
            g_med = R.get('gift_median'); g_p10 = R.get('gift_p10'); g_p90 = R.get('gift_p90')
            if g_med is not None:
                gm1, gm2, gm3 = st.columns(3)
                gm1.metric("Typical Lifetime Gift (median, real 2026 $)", f"${g_med:,.0f}")
                gm2.metric("Downside (10th pctile, real)", f"${g_p10:,.0f}",
                           help="In a bad 1-in-10 future, lifetime gifting is only this much. Gifting is the residual after lifestyle and guardrails, so it varies far more than spending across futures.")
                gm3.metric("Upside (90th pctile, real)", f"${g_p90:,.0f}")
                st.caption(
                    f"Median lifetime gift across {dash_runs} stress-tested futures is **${g_med:,.0f}** (real 2026 $), "
                    f"but the spread is wide: a bad path gifts as little as **${g_p10:,.0f}** while a good one reaches "
                    f"**${g_p90:,.0f}**. Gifting is the first thing the guardrails sacrifice in weak markets. The "
                    "base-case figure below is a single deterministic projection and sits toward the optimistic end."
                )
            g1, g2 = st.columns(2)
            g1.metric("Base-Case Lifetime Gift (deterministic, nominal)", f"${df_gift_summary['Cumulative Nominal Gift'].iloc[-1]:,.0f}",
                      help="A single base-case path with all assumptions at central values -- not stress-tested. The median/downside above are the representative figures.")
            g2.metric("Base-Case Lifetime Gift (deterministic, real 2026 $)", f"${df_gift_summary['Cumulative Real Gift'].iloc[-1]:,.0f}")
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
    st.session_state.retain_us_citizenship = cg2.toggle("Retain US Citizenship", value=st.session_state.retain_us_citizenship, help="If off, models renouncing US citizenship: only Slovenia's graduated rate applies (so >15y holdings become truly 0%). Renouncing is NOT free — the engine charges the IRC 877A covered-expatriate EXIT TAX at the move year: a deemed sale of all taxable lots, with gains above the (CPI-indexed) ~$890k exclusion taxed at the US LTCG rate, then a basis step-up.")

    st.markdown("---")
    st.subheader("Tax Engine")
    te1, te2 = st.columns(2)
    st.session_state.use_progressive_tax = te1.toggle(
        "Progressive bracket engine (US + Slovenia)", value=st.session_state.use_progressive_tax,
        help="ON (recommended): all ordinary income each year — taxable SS, the smoothing draw, "
             "RMDs, conversions, Roth-sweep earnings — stacks through the real US brackets "
             "(MFJ/single, CPI-indexed) and Slovenia's 16/26/33/39/50% schedule once resident; "
             "the combined liability is max(US, SI), the savings-clause + foreign-tax-credit "
             "outcome, and a survivor files SINGLE (this IS the widow's penalty). "
             "OFF: legacy flat base/excess rates below (now with the standard-deduction split "
             "applied to every ordinary draw, including the smoothing draw).")
    st.session_state.roth_first = te2.toggle(
        "Drain Roth before taxable (\"Roth Trap\" order)", value=st.session_state.roth_first,
        help="ON: the waterfall empties the Slovenia-taxed Roth sleeve before tax-free cash and "
             "the brokerage lots (every year of Roth growth exits at the trap rate, so exit "
             "early). OFF: conventional order — Roth is drawn last. Test both against the "
             "Monte Carlo joint-success rate; the better order depends on the Roth Trap Rate "
             "vs the aged capital-gains rates.")
    te3, te4, te5 = st.columns(3)
    st.session_state.ibkr_lot_aging = te3.toggle(
        "IBKR lots age into SI schedule", value=st.session_state.ibkr_lot_aging,
        help="ON: IBKR gains use Slovenia's holding-period schedule (25/20/15/0%) keyed to the "
             "sleeve's weighted-average acquisition year (sweep + redeposits tracked), with the "
             "residual US LTCG layer while a citizen. OFF: legacy flat Capital Gains Rate above.")
    st.session_state.model_div_tax = te4.toggle(
        "Tax dividends annually", value=st.session_state.model_div_tax,
        help="Annual drag on taxable sleeves (E*TRADE, IBKR): qualified-dividend rate pre-move; "
             "Slovenia's flat 25% (max'd with the US rate for citizens) post-move. Net dividends "
             "reinvest into basis.")
    st.session_state.div_yield = te5.number_input(
        "Dividend Yield (%)", value=st.session_state.div_yield, step=0.1,
        help="Cash yield on the taxable equity sleeves used for the annual dividend tax drag.")
    st.session_state.eur_return_drag = st.number_input(
        "EUR Sleeve Vehicle Drag (%/yr)", value=st.session_state.eur_return_drag, step=0.1,
        help="Return penalty on the EUR equity sleeve from the PFIC/PRIIPs squeeze on a US "
             "citizen investing from the EU (blocked from US ETFs by PRIIPs; punished on UCITS "
             "by PFIC rules; workarounds cost basis points). Plan B defaults to 0.4; Plan A 0.")
    
    st.markdown("---")
    st.subheader("Phase Contribution Policies")
    edited_policy = st.data_editor(st.session_state.policy_df, use_container_width=True, hide_index=True)
    st.session_state.policy_df = edited_policy

    st.markdown("---")
    st.subheader("Retirement Phase Lifestyle Targets (Today's USD Purchasing Power)")
    st.caption(
        "Enter what you'd spend in **today's US dollars**. After the move, the model translates "
        "this consumption basket to euros via the explicit **cost-of-living ratio** "
        f"(~{st.session_state.sl_col_ratio:.2f} € per $1, set on Page 10) — Slovenia's lower price "
        "level shows up as lifestyle headroom. The EUR/USD spot rate is a separate input that "
        "prices currency crossings (so a strong euro now correctly raises the dollar cost of the "
        "Slovenian life). For reference, a comfortable family-of-four budget in Slovenia is "
        "~€50k/yr, so amounts above that fund travel and discretionary spending."
    )
    r1, r2, r3 = st.columns(3)
    st.session_state.spend_golden = r1.number_input("Golden Years (< 70)", value=st.session_state.spend_golden, step=5000)
    st.session_state.spend_middle = r2.number_input("Middle Phase (70-85)", value=st.session_state.spend_middle, step=5000)
    st.session_state.spend_wind = r3.number_input("Wind Down Years (85-100)", value=st.session_state.spend_wind, step=5000)
    _col = st.session_state.sl_col_ratio
    st.caption(
        f"≈ Slovenia euro equivalents (cost-of-living basis):  Golden €{st.session_state.spend_golden*_col:,.0f}  |  "
        f"Middle €{st.session_state.spend_middle*_col:,.0f}  |  Wind-down €{st.session_state.spend_wind*_col:,.0f}  "
        f"(of which ~€50k is a comfortable base, the rest travel/discretionary)."
    )

# -----------------------------------------------------------------------------
# 4. REAL ESTATE & RELOCATION
# -----------------------------------------------------------------------------
elif selection == "4. Real Estate & Relocation":
    st.header("4. Real Estate & Relocation")
    st.session_state.move_lump_ibkr_usd = st.number_input(
        "One-Time Transfer into IBKR at the Move ($)", value=st.session_state.move_lump_ibkr_usd, step=10000,
        help="Relocation capital moved into the EUR-denominated IBKR sleeve in the move year, "
             "converted at the spot rate (starts the Slovenian holding-period clock). "
             "Plan B defaults to $100k; Plan A to $0.")
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
    st.markdown(
        "Sweeps the Roth 401(k) balances into the EUR-denominated IBKR sleeve around "
        "retirement, converting the dollars to euros **at the spot rate**. The engine now "
        "applies the real tax treatment instead of assuming a free sweep:"
    )
    st.session_state.execute_great_reset = st.toggle("Enable Great Reset in Cash Flow Model", value=st.session_state.execute_great_reset)
    _GR_NOW = "Sweep at retirement (earnings taxed + 10% penalty if under 59½)"
    _GR_DEFER = "Defer sweep to age 59½ (post-move sweep taxed at the Roth Trap Rate)"
    st.session_state.great_reset_mode = st.radio(
        "Sweep timing", [_GR_NOW, _GR_DEFER],
        index=0 if str(st.session_state.great_reset_mode).startswith("Sweep") else 1,
        disabled=not st.session_state.execute_great_reset,
        help="A Roth 401(k) distribution is only QUALIFIED at 59½ (plus the 5-year clock). "
             "Sweeping at retirement age 55 is non-qualified: the EARNINGS slice is US "
             "ordinary income plus a 10% early-withdrawal penalty (the contributions slice "
             "exits tax-free). Deferring to 59½ avoids the US tax and penalty, but by then "
             "you are a Slovenian resident — under the model's own Roth-Trap assumption "
             "Slovenia taxes the distribution. There is no free path; this lets the "
             "Monte Carlo adjudicate the trade-off honestly."
    )
    st.caption(
        "What the engine actually does (Page 5 previously displayed a gain-harvest and basis "
        "step-up for Crypto/E\\*TRADE/IBKR that was never simulated): **only the Roth sleeves are "
        "swept**. Taxable lots keep their original basis and are taxed on the embedded gain when "
        "actually sold in the drawdown waterfall — US LTCG pre-move, Slovenia's holding-period "
        "schedule (with the residual US layer) after."
    )
    reset_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    reset_age = st.session_state.ret_age

    if st.session_state.execute_great_reset:
        # Project ONLY the Roth sleeves to the sweep year and show the honest tax estimate.
        defer = str(st.session_state.great_reset_mode).startswith("Defer")
        sweep_age = max(60, reset_age) if defer else reset_age
        sweep_yr = 2026 + (sweep_age - st.session_state.current_age)
        move_age = st.session_state.move_age
        market_ret = st.session_state.usd_market_return / 100.0
        policy = st.session_state.policy_df.set_index("Asset Category")
        rows = []
        tot_val = tot_basis = 0.0
        for asset in ["Cornerstone: Roth 401(k)", "OCC: Roth 401(k)"]:
            bal = st.session_state.asset_balances.get(asset, 0)
            basis = bal
            if asset in policy.index:
                esc = policy.loc[asset, "Annual Savings Escalator (%)"] / 100.0
                curr_cont = policy.loc[asset, "Current State"]
                nb_cont = policy.loc[asset, "Northbrook Grind"]
            else:
                esc, curr_cont, nb_cont = 0, 0, 0
            for y in range(2026, min(sweep_yr, reset_yr)):
                cont = curr_cont if y < st.session_state.nb_start_yr else nb_cont
                bal = bal * (1 + market_ret) + cont
                basis += cont
                curr_cont *= (1 + esc)
                nb_cont *= (1 + esc)
            for y in range(min(sweep_yr, reset_yr), sweep_yr):
                bal = bal * (1 + market_ret)  # post-retirement growth, no contributions
            rows.append([asset, basis, bal, max(0.0, bal - basis)])
            tot_val += bal
            tot_basis += basis
        df_reset = pd.DataFrame(rows, columns=["Roth Sleeve", "Projected Contributions (Basis)", "Projected Value at Sweep", "Projected Earnings"])
        st.dataframe(df_reset.style.format({"Projected Contributions (Basis)": "${:,.0f}", "Projected Value at Sweep": "${:,.0f}", "Projected Earnings": "${:,.0f}"}), use_container_width=True)

        earnings = max(0.0, tot_val - tot_basis)
        if not defer and sweep_age < 60:
            est_penalty = 0.10 * earnings
            st.warning(
                f"Sweeping at age {sweep_age} is **non-qualified**: roughly ${earnings:,.0f} of "
                f"earnings is US ordinary income (taxed through the brackets, stacked on other "
                f"income that year) **plus a ~${est_penalty:,.0f} early-withdrawal penalty**. "
                "The exact tax is computed inside the engine via the progressive brackets."
            )
        elif defer:
            si_rate = st.session_state.tax_roth / 100.0
            note_si = (f"the move (age {move_age}), so Slovenia taxes the distribution at the "
                       f"Roth Trap Rate (~${tot_val * si_rate:,.0f} at {st.session_state.tax_roth:.0f}%)"
                       if sweep_age >= move_age else "the move, so no Slovenian tax applies")
            st.info(
                f"Sweep deferred to age {sweep_age}: qualified for US purposes (no US tax or "
                f"penalty), but it occurs after {note_si}."
            )
        st.caption(
            f"The swept dollars buy euros at the spot rate in {sweep_yr} (no more 1:1 par "
            "conversion), land in IBKR with stepped-up basis, and begin aging on Slovenia's "
            "holding-period schedule from the sweep year."
        )

# -----------------------------------------------------------------------------
# 6. SOCIAL SECURITY & PENSIONS
# -----------------------------------------------------------------------------
elif selection == "6. Social Security & Pensions":
    st.header("6. Actuarial Social Security Engine")
    st.markdown(
        "Claim ages are **dynamically optimized** to maximize Monte Carlo joint-success (shown "
        "below). Adjust the assumptions here, then hit **Re-Optimize** to re-solve the claim ages "
        "against the new inputs. All figures show both nominal (future) and real 2026 dollars."
    )

    st.subheader("Earnings, COLA & Funding Assumptions")
    e1, e2, e3 = st.columns(3)
    st.session_state.mike_future_pct = e1.slider("Michael: Future % of Max Taxable Earnings", 0, 100, st.session_state.mike_future_pct, 5,
                                                 help="Share of the SS maximum taxable wage base you earn in the years until retirement. 100% = always at the cap.")
    st.session_state.steph_future_pct = e2.slider("Stephanie: Future % of Max Taxable Earnings", 0, 100, st.session_state.steph_future_pct, 5)
    st.session_state.awi_rate = e3.number_input("Average Wage Index growth (%)", value=st.session_state.awi_rate, step=0.1,
                                                help="National wage growth that indexes the bend points and your earnings history.")
    f1, f2, f3 = st.columns(3)
    st.session_state.cola_rate = f1.number_input("Baseline COLA (%)", value=st.session_state.cola_rate, step=0.1,
                                                 help="The empirically-defensible central COLA: a modest ~0.3pt structural lag vs inflation (the CPI-W basket SS uses runs slightly below CPI-U). This is used when COLA mode is Baseline.")
    st.session_state.trust_fund_haircut = f2.slider("SS Funding Shortfall Haircut (%)", 0, 50, st.session_state.trust_fund_haircut, 5,
                                                    help="Permanent benefit reduction from the trust-fund shortfall. The Trustees project ~20-23% if Congress does nothing by ~2033.")
    st.session_state.inflation_rate = f3.number_input("Inflation for Real $ Conversion (%)", value=st.session_state.inflation_rate, step=0.1,
                                                      help="Used to convert future nominal benefits into today's 2026 purchasing power.")

    # --- COLA assumption: explicit baseline-vs-stress toggle (no longer an invisible default) ---
    st.markdown("**COLA Assumption Mode**")
    cm1, cm2 = st.columns([1.3, 1])
    st.session_state.cola_mode = cm1.radio(
        "How should SS cost-of-living adjustments be modeled?",
        ["Baseline (modest structural lag)", "Stress (COLA persistently lags inflation)"],
        index=0 if str(st.session_state.cola_mode).startswith("Baseline") else 1,
        help="Baseline uses the rate above (~0.3pt structural lag, the defensible central case). "
             "Stress applies a larger persistent gap that erodes real SS substantially over a long "
             "retirement and hits the survivor hardest \u2014 useful for pressure-testing, but more "
             "pessimistic than the historical record, so it shouldn't be your silent default."
    )
    st.session_state.cola_stress_rate = cm2.number_input(
        "Stress COLA (%)", value=st.session_state.cola_stress_rate, step=0.1,
        help="The COLA used in Stress mode. Default 2.1% models a ~0.8pt persistent lag vs a 2.9% "
             "inflation assumption \u2014 the conservative wedge that was previously baked into the default."
    )
    _eff_cola = effective_cola()
    _gap = st.session_state.inflation_rate - _eff_cola
    # Illustrative real-SS erosion over 30 years at the current gap.
    _erosion = (1 - ((1 + _eff_cola/100) / (1 + st.session_state.inflation_rate/100)) ** 30) * 100
    if _gap <= 0.45:
        st.success(
            f"**Active COLA: {_eff_cola:.1f}%** vs inflation {st.session_state.inflation_rate:.1f}% "
            f"\u2014 a {_gap:+.1f}pt gap (modest, defensible). At this gap, real SS purchasing power "
            f"erodes ~{_erosion:.0f}% over 30 years."
        )
    else:
        st.warning(
            f"**Active COLA: {_eff_cola:.1f}%** vs inflation {st.session_state.inflation_rate:.1f}% "
            f"\u2014 a {_gap:+.1f}pt gap (stress). This erodes real SS purchasing power ~{_erosion:.0f}% "
            f"over 30 years and compounds with the {st.session_state.trust_fund_haircut}% trust-fund "
            f"haircut \u2014 a deliberately pessimistic SS scenario, most punishing for the survivor."
        )

    st.markdown("---")
    st.subheader("Slovenian State Pension (ZPIZ) \u2014 Plan B")
    zp0, zp1, zp2, zp3 = st.columns(4)
    st.session_state.si_pension_enable = zp0.toggle(
        "Enable ZPIZ pension", value=st.session_state.si_pension_enable,
        help="Accrues over the Slovenian working years (move age to retirement age) at the "
             "statutory schedule: ~26.5% of the basis at 15 contribution years + ~1.36%/yr "
             "beyond (Plan B's 24 years \u2248 39% each). Below 15 years, no pension. Survivor "
             "keeps the larger single benefit. EUR income \u2014 a natural hedge, no FX crossing.")
    st.session_state.si_pension_basis_eur = zp1.number_input(
        "Pension basis (\u20ac/yr, net)", value=st.session_state.si_pension_basis_eur, step=1000,
        help="Proxy for the ZPIZ pension rating base in today's euros, CPI-indexed (wage growth "
             "= inflation per Plan B). Default \u2248 average Slovenian net wage. Replace with a "
             "real ZPIZ projection when you have one \u2014 this is the module's softest number.")
    st.session_state.si_pension_claim_age = zp2.number_input(
        "Claim age", value=st.session_state.si_pension_claim_age, step=1,
        help="Statutory old-age pension age (65 with 15+ contribution years).")
    st.session_state.si_pension_tax_pct = zp3.number_input(
        "Net tax on pension (%)", value=st.session_state.si_pension_tax_pct, step=1.0,
        help="Flat haircut approximating the Slovenian pension tax credit plus the residual US "
             "layer (a foreign pension is US-taxable income, though at this size it sits mostly "
             "under the standard deduction).")

    # Quantify the stacked pessimism so the assumption pile is a CHOICE, not an accident.
    _hc = st.session_state.trust_fund_haircut / 100.0
    _mc_p = st.session_state.get('mc_ss_haircut_prob', 0.0)
    _mc_s = st.session_state.get('mc_ss_haircut_size', 0.0)
    _exp_share = (1 - _hc) * (1 - _mc_p * _mc_s)
    st.caption(
        f"**Assumption-stacking check:** the {st.session_state.trust_fund_haircut}% baseline haircut, "
        f"the Monte Carlo's {_mc_p:.0%} chance of a further {_mc_s:.0%} cut, the COLA lag, and the "
        f"{st.session_state.mike_future_pct}%/{st.session_state.steph_future_pct}% future-earnings "
        f"assumptions COMPOUND: expected benefit \u2248 **{_exp_share:.0%} of scheduled** before COLA-lag "
        "erosion. Each is defensible; together they are a deliberately severe SS scenario \u2014 re-run "
        "the dashboard at 0% haircut once to see how much of the failure tail is this stack rather "
        "than market risk. COLAs are now indexed to each path's REALIZED inflation (less the "
        "structural lag), so high-inflation paths and the 1966/1973 backtest cohorts no longer "
        "erode SS's real value unrealistically."
    )

    st.markdown("---")
    st.subheader("Optimized Claim Ages")
    oc1, oc2, oc3 = st.columns([1, 1, 1])
    # Manual override sliders (kept available; editing them turns off the 'optimized' flag).
    new_m = oc1.slider("Michael Claim Age", 62, 70, int(st.session_state.mike_ss_age))
    new_s = oc2.slider("Stephanie Claim Age", 62, 70, int(st.session_state.steph_ss_age))
    if new_m != st.session_state.mike_ss_age or new_s != st.session_state.steph_ss_age:
        st.session_state.mike_ss_age = new_m; st.session_state.steph_ss_age = new_s
        st.session_state.ss_ages_optimized = False
    opt_runs_ss = oc3.number_input("Paths per evaluation", value=150, min_value=50, max_value=500, step=50, key="ss_opt_runs")

    reopt = st.button("Re-Optimize Claim Ages", type="primary")
    if reopt:
        ages = list(range(62, 71))
        seed = int(st.session_state.get('mc_seed', 42))
        n_ev = int(opt_runs_ss)
        m_cur = int(st.session_state.mike_ss_age); s_cur = int(st.session_state.steph_ss_age)
        history = []
        prog = st.progress(0.0, text="Re-optimizing claim ages against current assumptions...")
        total_steps = 4 * len(ages); done = 0
        for rnd in range(2):
            best_m, best_score = m_cur, -1.0
            for a in ages:
                sc = score_joint_success_for_ss(n_ev, seed, a, s_cur)
                if sc > best_score: best_score, best_m = sc, a
                done += 1; prog.progress(done/total_steps, text=f"Round {rnd+1}: Michael age {a} \u2192 {sc:.0f}%")
            m_cur = best_m
            best_s, best_score = s_cur, -1.0
            for a in ages:
                sc = score_joint_success_for_ss(n_ev, seed, m_cur, a)
                if sc > best_score: best_score, best_s = sc, a
                done += 1; prog.progress(done/total_steps, text=f"Round {rnd+1}: Stephanie age {a} \u2192 {sc:.0f}%")
            s_cur = best_s
            history.append((rnd+1, m_cur, s_cur, best_score))
        prog.progress(1.0, text="Complete.")
        st.session_state.mike_ss_age = int(m_cur); st.session_state.steph_ss_age = int(s_cur)
        st.session_state.ss_ages_optimized = True
        st.success(f"**Re-optimized:** Michael claims at **{m_cur}**, Stephanie at **{s_cur}** \u2014 joint-success **{history[-1][3]:.1f}%**. Applied across the entire model.")

    if st.session_state.get('ss_ages_optimized', False):
        st.caption(f"Claim ages are optimizer-set (Michael {st.session_state.mike_ss_age}, Stephanie {st.session_state.steph_ss_age}). Editing a slider above switches to manual mode; Re-Optimize restores the solved ages.")
    else:
        st.caption("Claim ages are currently **manual**. Hit Re-Optimize to solve for the joint-success-maximizing ages under the assumptions above.")

    # Recompute timelines with current inputs and ages.
    MIKE_SS, STEPH_SS = get_ss_timelines()
    m_claim_yr = 2026 + (st.session_state.mike_ss_age - st.session_state.current_age)
    # Stephanie's claim year keys off HER OWN age (she is mc_wife_age_offset years younger),
    # matching the rebuilt SS module (Tier-2 fix #7).
    s_claim_yr = 2026 + (st.session_state.steph_ss_age - (st.session_state.current_age - st.session_state.mc_wife_age_offset))
    inf_rate = st.session_state.inflation_rate / 100.0
    m_real_ss = MIKE_SS[m_claim_yr] / ((1 + inf_rate) ** (m_claim_yr - 2026))
    s_real_ss = STEPH_SS[s_claim_yr] / ((1 + inf_rate) ** (s_claim_yr - 2026))

    st.markdown("---")
    st.subheader("Benefit at Claim")
    c1, c2 = st.columns(2)
    c1.success(f"**Michael \u2014 claims {m_claim_yr} (age {st.session_state.mike_ss_age})**\n\nNominal: **${MIKE_SS[m_claim_yr]:,.0f}**/yr\n\nReal (2026 $): **${m_real_ss:,.0f}**/yr")
    c2.success(f"**Stephanie \u2014 claims {s_claim_yr} (age {st.session_state.steph_ss_age})**\n\nNominal: **${STEPH_SS[s_claim_yr]:,.0f}**/yr\n\nReal (2026 $): **${s_real_ss:,.0f}**/yr")

    # Combined household benefit over time, nominal vs real 2026 $.
    all_yrs = sorted(set(MIKE_SS) | set(STEPH_SS))
    rows = []
    for y in all_yrs:
        m_nom = MIKE_SS.get(y, 0); s_nom = STEPH_SS.get(y, 0); tot_nom = m_nom + s_nom
        defl = (1 + inf_rate) ** (y - 2026)
        rows.append({"Year": y, "Age (M)": st.session_state.current_age + (y - 2026),
                     "Michael (nom)": m_nom, "Stephanie (nom)": s_nom,
                     "Household (nom)": tot_nom, "Household (real 2026 $)": tot_nom / defl})
    df_ss = pd.DataFrame(rows)
    df_ss = df_ss[df_ss["Household (nom)"] > 0]

    st.markdown("---")
    st.subheader("Household Benefit Over Time \u2014 Real (2026 $) vs Nominal")
    if not df_ss.empty:
        fig_ss = go.Figure()
        fig_ss.add_trace(go.Scatter(x=df_ss["Year"], y=df_ss["Household (nom)"], mode='lines',
                                    name="Nominal (future $)", line=dict(color='#9ecae1', width=2)))
        fig_ss.add_trace(go.Scatter(x=df_ss["Year"], y=df_ss["Household (real 2026 $)"], mode='lines',
                                    name="Real (2026 $)", line=dict(color='#08519c', width=3)))
        fig_ss.update_layout(height=360, yaxis_title="Household SS ($/yr)", xaxis_title="Year",
                             legend=dict(orientation='h', y=1.12), margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_ss, use_container_width=True)
        st.caption("Nominal benefits grow with COLA; the real line shows constant 2026 purchasing power (COLA net of inflation). If COLA < inflation, the real line drifts down over time.")

        show = df_ss[df_ss["Year"].isin([y for y in df_ss["Year"] if (y - 2026) % 5 == 0 or y in (m_claim_yr, s_claim_yr)])].copy()
        st.dataframe(
            show.style.format({"Michael (nom)": "${:,.0f}", "Stephanie (nom)": "${:,.0f}",
                               "Household (nom)": "${:,.0f}", "Household (real 2026 $)": "${:,.0f}"}),
            use_container_width=True, hide_index=True)
    st.caption(
        "Optimization scores joint-success (never deplete + full lifestyle + hit gift goal) with common "
        "random numbers on the valuation-conditioned, crisis-prone engine. The funding-shortfall haircut "
        "permanently scales benefits down. Not tax/financial advice \u2014 the survivor-benefit interaction "
        "(the higher earner's delay protects the survivor) especially warrants a specialist's review."
    )

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

    show_tax_band = st.checkbox(
        "Overlay Monte Carlo range (10th-90th percentile)", value=False,
        help="Adds the distribution of your weighted-average effective tax rate across stress-tested "
             "futures around the deterministic line. The draw tables above stay deterministic (their "
             "value is the exact mechanics); only this summary rate gets a range, since its uncertainty "
             "is decision-relevant."
    )

    df_tax_t = df_tax.T
    if start_yr in df_tax_t.index:
        tax_chart_data = df_tax_t.loc[start_yr:].copy()
        fig_tax = go.Figure()
        if show_tax_band:
            tb1, tb2 = st.columns(2)
            tax_runs = tb1.number_input("Simulations", value=300, min_value=100, max_value=1500, step=100, key="p7_runs")
            if tb2.button("Run / Refresh Tax Range") or 'p7_bands_v2' not in st.session_state:
                with st.spinner(f"Running {int(tax_runs)} full-stress paths..."):
                    st.session_state.p7_bands_v2 = mc_bands_for_pages(int(tax_runs), seed=int(st.session_state.get('mc_seed', 42)))
            T = st.session_state.p7_bands_v2
            yrs = T['years']
            # Clip to the retirement window shown on the deterministic chart.
            keep = [i for i, y in enumerate(yrs) if y >= start_yr]
            yk = [yrs[i] for i in keep]
            def col(key): return [T[key][i] for i in keep]
            fig_tax.add_trace(go.Scatter(x=yk, y=col('tax_p90'), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig_tax.add_trace(go.Scatter(x=yk, y=col('tax_p10'), mode='lines', line=dict(width=0), fill='tonexty',
                                         fillcolor='rgba(214,39,40,0.12)', name='10th-90th pct'))
            fig_tax.add_trace(go.Scatter(x=yk, y=col('tax_p75'), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig_tax.add_trace(go.Scatter(x=yk, y=col('tax_p25'), mode='lines', line=dict(width=0), fill='tonexty',
                                         fillcolor='rgba(214,39,40,0.25)', name='25th-75th pct'))
            fig_tax.add_trace(go.Scatter(x=yk, y=col('tax_p50'), mode='lines', line=dict(color='#d62728', width=2, dash='dot'), name='MC median'))
        fig_tax.add_trace(go.Scatter(x=tax_chart_data.index, y=tax_chart_data['Weighted Average'],
                                     mode='lines+markers', line=dict(color='#08519c', width=3), name='Base case'))
        fig_tax.update_yaxes(tickformat=',.1%')
        fig_tax.update_layout(xaxis_title="Year", yaxis_title="Effective Tax Rate (%)",
                              legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                              showlegend=show_tax_band, height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_tax, use_container_width=True)
        if show_tax_band:
            st.caption(
                "The blue line is the base-case effective tax rate; the red band is its range across "
                "stress-tested futures (tax-regime drift, varying drawdown sources, and inflation moving "
                "bracket fills all widen it). A wide band means your effective rate is sensitive to "
                "conditions you don't control \u2014 useful context for the Roth-conversion and SS-timing decisions."
            )

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

    view_mode = st.radio(
        "View", ["Deterministic (base-case stack)", "Monte Carlo (percentile fan)"],
        horizontal=True,
        help="Deterministic shows the single base-case projection by asset. Monte Carlo shows "
             "the range of TOTAL real balance across stress-tested futures (10th-90th percentile), "
             "so you see where your balance could plausibly land at each age, not just one line."
    )

    if view_mode.startswith("Monte Carlo"):
        mc1, mc2 = st.columns(2)
        band_runs = mc1.number_input("Simulations", value=400, min_value=100, max_value=2000, step=100, key="p8_runs")
        if mc2.button("Run / Refresh Percentile Fan") or 'p8_bands_v2' not in st.session_state:
            with st.spinner(f"Running {int(band_runs)} full-stress paths..."):
                st.session_state.p8_bands_v2 = mc_bands_for_pages(int(band_runs), seed=int(st.session_state.get('mc_seed', 42)))
        B = st.session_state.p8_bands_v2
        yrs = B['years']
        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(x=yrs, y=B['bal_p90'], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig8.add_trace(go.Scatter(x=yrs, y=B['bal_p10'], mode='lines', line=dict(width=0), fill='tonexty',
                                  fillcolor='rgba(31,119,180,0.15)', name='10th-90th percentile'))
        fig8.add_trace(go.Scatter(x=yrs, y=B['bal_p75'], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig8.add_trace(go.Scatter(x=yrs, y=B['bal_p25'], mode='lines', line=dict(width=0), fill='tonexty',
                                  fillcolor='rgba(31,119,180,0.30)', name='25th-75th percentile'))
        fig8.add_trace(go.Scatter(x=yrs, y=B['bal_p50'], mode='lines', line=dict(color='red', width=3), name='Median'))
        fig8.update_layout(
            title=dict(text="Total Real Portfolio Balance Across Stress-Tested Futures (2026 $)", y=0.97, yanchor='top'),
            xaxis_title="Year", yaxis=dict(title="Real Portfolio Value (2026 $)", tickprefix="$"),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            hovermode="x unified", height=460, margin=dict(l=10, r=10, t=80, b=10)
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.caption(
            "Each band is the range of your TOTAL portfolio balance (real 2026 $) across the simulated "
            "futures at each age \u2014 the red line is the typical (median) path, the dark band the middle "
            "half, the light band the 10th-90th percentile. A band that stays well above zero late in life "
            "means the plan is robust; one that dips toward zero in the lower percentiles flags depletion "
            "risk in bad sequences. This is the honest range; the deterministic view shows only one line "
            "through the middle. Uses the same engine as the dashboard and Page 12."
        )
        st.markdown("---")
        st.subheader("Detailed Ledger (base-case deterministic)")
        st.dataframe(df_bal.style.format("${:,.0f}"), use_container_width=True, height=450)
    else:
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

    st.markdown("**Allocation-Based Glide (recommended)** — de-risk by shifting equity weight into an EUR bond sleeve, so both the *mean and the volatility* of returns fall. This is the financially correct model; the return-haircut fields above are a legacy fallback used only when this is off.")
    ag1, ag2, ag3 = st.columns(3)
    st.session_state.glide_alloc_mode = ag1.toggle("Use Allocation Glide", value=st.session_state.glide_alloc_mode)
    st.session_state.glide_eq_start = ag2.number_input("Equity Weight Before De-Risking", value=st.session_state.glide_eq_start, min_value=0.0, max_value=1.0, step=0.05, format="%.2f")
    st.session_state.glide_eq_end = ag3.number_input("Equity Weight at Floor", value=st.session_state.glide_eq_end, min_value=0.0, max_value=1.0, step=0.05, format="%.2f")
    b1, b2, b3, b4 = st.columns(4)
    st.session_state.bond_mean = b1.number_input("EUR Bond Return (%)", value=st.session_state.bond_mean, step=0.25, format="%.2f")
    st.session_state.bond_vol = b2.number_input("EUR Bond Vol (%)", value=st.session_state.bond_vol, step=0.5, format="%.2f")
    st.session_state.bond_eq_corr = b3.number_input("Bond/Equity Corr (normal)", value=st.session_state.bond_eq_corr, min_value=-1.0, max_value=1.0, step=0.05, format="%.2f")
    st.session_state.bond_eq_corr_crisis = b4.number_input("Bond/Equity Corr (crisis)", value=st.session_state.bond_eq_corr_crisis, min_value=-1.0, max_value=1.0, step=0.05, format="%.2f", help="In equity-crash years bonds tend to fall too (2022); this higher correlation means de-risking is not a free hedge in exactly the bad years.")

    st.markdown("**Inflation-Linked Bond Sleeve (static hedge)** — hold a fixed share of the bond sleeve in inflation-linked bonds (euro linkers / TIPS). Held *continuously*, not switched on when inflation rises — the protection only works if you already own it before the shock, since linkers reprice the moment inflation becomes visible. The linker portion earns a real yield plus realized inflation, so it preserves purchasing power in high-inflation years and costs a small drag in calm ones.")
    il1, il2, il3 = st.columns(3)
    st.session_state.linker_enable = il1.toggle("Hold Inflation-Linked Bonds", value=st.session_state.linker_enable,
                                                help="Static allocation, applied every year. Off = the whole bond sleeve is nominal (most exposed to inflation).")
    st.session_state.linker_frac = il2.number_input("Linker Share of Bond Sleeve", value=st.session_state.linker_frac, min_value=0.0, max_value=1.0, step=0.05, format="%.2f",
                                                    help="Fraction of the bond allocation held in inflation-linked bonds. The rest stays nominal. Sweep this and re-run Page 14 to see how much it shrinks inflation's swing.", disabled=not st.session_state.linker_enable)
    st.session_state.linker_real_yield = il3.number_input("Linker Real Yield (%)", value=st.session_state.linker_real_yield, step=0.25, format="%.2f",
                                                          help="The real (above-inflation) yield linkers earn. Euro-area linkers have recently been ~0.5-1.5% real. Linker nominal return each year = this + that year's realized inflation.", disabled=not st.session_state.linker_enable)
    if st.session_state.linker_enable:
        _bm = st.session_state.bond_mean; _lf = st.session_state.linker_frac
        _ly = st.session_state.linker_real_yield; _inf = st.session_state.inflation_rate
        _blended_calm = (1 - _lf) * _bm + _lf * (_ly + _inf)
        st.caption(
            f"At {_lf:.0%} linkers (real yield {_ly:.1f}%), in a *normal* {_inf:.1f}%-inflation year the blended "
            f"bond sleeve returns ~{_blended_calm:.1f}% vs {_bm:.1f}% all-nominal "
            f"({'a slight drag' if _blended_calm < _bm else 'roughly even'}). In a high-inflation year the linker "
            f"portion rises with inflation while the nominal portion erodes — that asymmetry is the hedge. "
            f"Test it: sweep the inflation factor on Page 14 with this on vs off."
        )
    if st.session_state.glide_enable and st.session_state.glide_alloc_mode:
        st.info(
            f"**Status:** Allocation glide active. Equity weight shifts from "
            f"**{st.session_state.glide_eq_start:.0%}** at age {st.session_state.glide_start_age} to "
            f"**{st.session_state.glide_eq_end:.0%}** at age {st.session_state.glide_end_age}, with the rest "
            f"in EUR bonds ({st.session_state.bond_mean:.1f}% / {st.session_state.bond_vol:.1f}% vol). Bonds are "
            "EUR-denominated throughout, matching your post-move spending currency. In the Monte Carlo this "
            "compresses late-life outcome dispersion (the real purpose of de-risking)."
        )
    elif st.session_state.glide_enable:
        st.info(f"**Status:** Legacy return-haircut glide active. By age {st.session_state.glide_end_age}, USD return drops to **{st.session_state.usd_market_return - total_usd_drop:.3f}%** and EUR to **{st.session_state.eur_market_return - total_eur_drop:.3f}%** (volatility unchanged — turn on Allocation Glide for the realistic version).")

    st.markdown("---")
    st.subheader("B. Sequence of Returns Risk (SORR)")
    st.markdown("Simulate a devastating, multi-year market crash at a specific point in time to see if early portfolio damage bankrupts your long-term plan.")
    s1, s2, s3 = st.columns(3)
    st.session_state.sorr_enable = s1.toggle("Enable Market Crash", value=st.session_state.sorr_enable)
    st.session_state.sorr_start_yr = s2.number_input("Crash Start Year", value=st.session_state.sorr_start_yr)
    st.session_state.sorr_duration = s3.number_input("Crash Duration (Years)", value=st.session_state.sorr_duration)
    st.session_state.sorr_return = st.number_input("Annual Return During Crash (%)", value=st.session_state.sorr_return, step=1.0)
    
    st.markdown("---")
    st.subheader("C. Foreign Exchange & Cost of Living (USD/EUR)")
    st.markdown(
        "Retirement spending is denominated in **euros** (your actual liability in Slovenia). "
        "Lifestyle inputs stay in today's US dollars and are translated to euros ONCE via the "
        "explicit **cost-of-living ratio** below — the Slovenian price-level discount, now "
        "separated from the exchange rate it used to be conflated with. The **spot rate** then "
        "prices every currency crossing: USD accounts pay the spot rate for each euro of "
        "spending, so a **stronger euro (higher rate) drains the USD-heavy portfolio faster** — "
        "the correct direction of risk. EUR-denominated IBKR and Cash fund euro spending 1:1 "
        "and are genuine hedges; all totals report EUR sleeves at the year's spot rate."
    )
    f1, f2, f3 = st.columns(3)
    st.session_state.fx_enable = f1.toggle("Model FX (off = parity 1.00)", value=st.session_state.fx_enable,
                                           help="When off, the spot rate is pinned at 1.00 — currency risk and conversion costs are ignored entirely.")
    st.session_state.fx_rate = f2.number_input("EUR/USD Spot Rate ($ per €1.00)", value=st.session_state.fx_rate, step=0.05,
                                               help="Deterministic spot rate (the Monte Carlo's stochastic FX wanders around this). Raise it to stress a strong euro — which now correctly HURTS the plan.")
    st.session_state.sl_col_ratio = f3.number_input("Slovenia Cost-of-Living Ratio (€ per $1 of lifestyle)", value=st.session_state.sl_col_ratio, step=0.01,
                                                    help="Euros needed in Slovenia to buy $1 of US-equivalent lifestyle (the PPP discount). 0.77 ≈ a ~23% lower price level. Applies to the consumption basket only — SS and gifts are USD cash flows converted at spot.")

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
    st.session_state.gifting_enable = st.toggle("Enable Generational Gifting", value=st.session_state.gifting_enable,
                                                help="Off = the model never gifts surplus away; the portfolio accumulates instead. Turn off to model a pure no-gifting plan.")
    st.session_state.dynamic_gift_pct = st.number_input("Target Lifetime Gift Value (% of Projected Terminal Portfolio)", value=st.session_state.dynamic_gift_pct, step=5.0, disabled=not st.session_state.gifting_enable)
    st.session_state.gift_start_age = st.number_input("Age to Start Gifting", value=st.session_state.gift_start_age, step=1, disabled=not st.session_state.gifting_enable)
    st.session_state.gift_end_age = st.number_input("Age to End Gifting", value=st.session_state.gift_end_age, step=1, disabled=not st.session_state.gifting_enable)

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
        help="Block Bootstrap resamples contiguous runs of PAIRED US/EUR calendar years "
             "(2000-2025, the overlap of the two return series), preserving fat tails, "
             "volatility clustering, and cross-sleeve crisis synchronization. Normal draws "
             "are smoother and understate crash risk."
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

    st.session_state.mc_gift_goal = st.number_input(
        "Lifetime Gifting Goal (Real 2026 $)", value=st.session_state.mc_gift_goal, step=100000,
        help="Total real generational gift you'd consider a success. Used for the gifting "
             "success rate and the joint-success metric below."
    )

    with st.expander("Stress Factors (randomize more than just equity returns)", expanded=True):
        st.caption(
            "By default the simulation randomizes only equity returns. These toggles add the "
            "other big plan risks. Each is independent so you can isolate effects; the tornado "
            "chart below quantifies how much each one moves your success rate."
        )
        f1, f2 = st.columns(2)
        with f1:
            st.session_state.mc_stoch_inflation = st.checkbox("Stochastic inflation", value=st.session_state.mc_stoch_inflation)
            st.session_state.mc_infl_vol = st.number_input("Inflation volatility (std dev %)", value=st.session_state.mc_infl_vol, step=0.25)
            st.session_state.mc_infl_equity_corr = st.number_input("Inflation/equity correlation", value=st.session_state.mc_infl_equity_corr, min_value=-1.0, max_value=1.0, step=0.05, help="Negative = high inflation tends to coincide with bad equity years (stagflation risk).")
            st.session_state.mc_stoch_fx = st.checkbox("Stochastic EUR/USD", value=st.session_state.mc_stoch_fx)
            st.session_state.mc_fx_vol = st.number_input("FX annual volatility (%)", value=st.session_state.mc_fx_vol, step=1.0, help="USD-funding cost of euro spending follows a mean-reverting process with this annual vol.")
            st.session_state.mc_fx_reversion = st.number_input("FX mean-reversion speed", value=st.session_state.mc_fx_reversion, min_value=0.0, max_value=0.9, step=0.05, help="0 = pure random walk (FX can drift to absurd multiples over decades, overstating currency risk). ~0.15 pulls the rate back toward today's parity each year, matching how real exchange rates revert toward purchasing-power parity over long horizons.")
            st.session_state.mc_stoch_longevity = st.checkbox("Stochastic longevity (SSA tables)", value=st.session_state.mc_stoch_longevity)
            st.session_state.mc_wife_age_offset = st.number_input("Spouse age offset (you minus spouse)", value=st.session_state.mc_wife_age_offset, step=1, help="Used to age the second life. Female table applied to spouse, male to you.")
            st.session_state.survivor_enable = st.checkbox("Survivor scenario (model first death)", value=st.session_state.survivor_enable, help="After the first death: SS drops to the larger benefit, spending falls to the survivor ratio, and the survivor files single (widow's penalty). Requires stochastic longevity to generate first-death years.")
            st.session_state.survivor_expense_ratio = st.number_input("Survivor expense ratio", value=st.session_state.survivor_expense_ratio, min_value=0.4, max_value=1.0, step=0.05, help="Surviving single person's spending as a fraction of the couple's (consensus ~70-80%; not 50%).")
            st.session_state.survivor_tax_surcharge = st.number_input("Widow's-penalty tax surcharge", value=st.session_state.survivor_tax_surcharge, min_value=1.0, max_value=1.5, step=0.02, help="Survivor files single: ~half-width US brackets and a smaller standard deduction tax the same income harder. ~1.18 ≈ +$3,700/yr scale.")
        with f2:
            st.session_state.mc_ltc_enable = st.checkbox("Long-term care shock", value=st.session_state.mc_ltc_enable)
            st.session_state.mc_ltc_prob = st.number_input("LTC lifetime probability (per person)", value=st.session_state.mc_ltc_prob, min_value=0.0, max_value=1.0, step=0.05)
            st.session_state.mc_ltc_cost = st.number_input("LTC annual cost (real $)", value=st.session_state.mc_ltc_cost, step=5000)
            st.session_state.mc_ltc_years = st.number_input("LTC duration (years)", value=st.session_state.mc_ltc_years, step=1)
            st.session_state.mc_tax_regime = st.checkbox("Tax-regime uncertainty", value=st.session_state.mc_tax_regime)
            st.session_state.mc_tax_vol = st.number_input("Tax-rate drift (std dev, fraction)", value=st.session_state.mc_tax_vol, step=0.05, help="A path-level multiplier on all tax rates, e.g. 0.15 = +/-15% rate uncertainty.")
            st.session_state.mc_ss_haircut_prob = st.number_input("Incremental SS benefit-cut probability", value=st.session_state.mc_ss_haircut_prob, min_value=0.0, max_value=1.0, step=0.05, help="Chance the SS trust-fund shortfall triggers a benefit cut on your timeline.")
            st.session_state.mc_ss_haircut_size = st.number_input("Incremental SS benefit-cut size", value=st.session_state.mc_ss_haircut_size, min_value=0.0, max_value=1.0, step=0.05)

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

    with st.expander("Valuation Conditioning & Crisis Regime (return realism)", expanded=True):
        st.markdown(
            "Two upgrades that most affect credibility from a high starting valuation. "
            "**Valuation conditioning** lowers the *near-term* equity return because the US "
            "CAPE (~41 in May 2026) is near a record high and historically implies low forward "
            "returns; it reverts to your long-run assumption over the reversion window. "
            "**Crisis regime** overlays occasional clustered crash years on the bootstrap, "
            "dragging equities, the EUR sleeve, and bonds down together (the tail the 2000-2025 "
            "sample alone underweights)."
        )
        v1, v2 = st.columns(2)
        with v1:
            st.session_state.mc_valuation_enable = st.checkbox("Valuation conditioning (CAPE)", value=st.session_state.mc_valuation_enable)
            st.session_state.mc_cape_implied_usd = st.number_input("CAPE-implied near-term USD return (%)", value=st.session_state.mc_cape_implied_usd, step=0.5, help="GuruFocus CAPE-implied was ~2.7% in Apr 2026; 3-4% is a defensible starting point.")
            st.session_state.mc_cape_implied_eur = st.number_input("CAPE-implied near-term EUR return (%)", value=st.session_state.mc_cape_implied_eur, step=0.5, help="European markets are less stretched, so the haircut is milder.")
            st.session_state.mc_reversion_years = st.number_input("Years to revert to long-run", value=st.session_state.mc_reversion_years, min_value=1, max_value=30, step=1)
            st.session_state.mc_valuation_strength = st.slider("Conditioning strength", 0.0, 1.0, value=st.session_state.mc_valuation_strength, step=0.1, help="0 = ignore valuation (full long-run mean); 1 = full CAPE conditioning. Your conviction dial.")
        with v2:
            st.session_state.mc_crisis_enable = st.checkbox("Crisis regime overlay", value=st.session_state.mc_crisis_enable)
            st.session_state.mc_crisis_freq = st.number_input("Crisis year frequency", value=st.session_state.mc_crisis_freq, min_value=0.0, max_value=0.5, step=0.01, help="Long-run share of years in the crisis state. ~0.05 keeps the worst 15-yr window near historical experience; higher values stress-test beyond history (but >0.10 produces decade-long crashes worse than any on record).")
            st.session_state.mc_crisis_persist = st.number_input("Crisis persistence", value=st.session_state.mc_crisis_persist, min_value=0.0, max_value=0.95, step=0.05, help="P(stay in crisis next year | in crisis). Higher = longer, clustered bear markets. Above ~0.3 crises cluster into implausibly long depressions.")
            st.session_state.mc_crisis_usd_mean = st.number_input("Crisis-year USD mean (%)", value=st.session_state.mc_crisis_usd_mean, step=2.0)
            st.session_state.mc_crisis_eur_drag = st.number_input("EUR co-movement in crisis", value=st.session_state.mc_crisis_eur_drag, min_value=0.0, max_value=1.0, step=0.05, help="1.0 = EUR sleeve fully mirrors the USD crisis shock (correlations -> 1).")

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

        # Valuation conditioning is applied inside the shared helpers for the bootstrap;
        # the parametric branch applies it explicitly below so both methods evaluate
        # against the identical conditioned world.
        val_shift_usd, val_shift_eur = build_valuation_shift(n_years, usd_mean, eur_mean)

        if use_bootstrap:
            # Shared paired block-bootstrap (sec: SHARED MONTE CARLO MACHINERY). Recentered
            # by the FULL-HISTORY mean -- per-draw recentering used to pin every path's
            # 64-year average exactly to the target, deleting long-run-mean uncertainty
            # and overstating success. Honors mc_block_len / mc_mean_type, and applies
            # valuation conditioning + the crisis overlay internally.
            def make_paths():
                return make_bootstrap_paths(rng, n_years)
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
                usd = usd_arith + z[:, 0] + val_shift_usd; eur = eur_arith + z[:, 1] + val_shift_eur
                bond = draw_bond_path(usd, rng)
                return apply_crisis_overlay(usd, eur, bond, rng)

        terminal_real, depletion_ages = [], []
        real_paths = np.full((n_runs, n_years), np.nan)
        success = 0
        start_age = st.session_state.current_age
        ret_start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)

        # ---- Stress-factor scenario builder (per path) ----
        # Shared with the dashboard, tornado, interaction matrix, and optimizers
        # (sec: SHARED MONTE CARLO MACHINERY) so factor semantics cannot diverge.
        def build_scenario(usd_draws, eur_draws):
            return build_stress_scenario(rng, usd_draws, flags=None, years=years)

        any_stress = (st.session_state.mc_stoch_inflation or st.session_state.mc_stoch_fx or
                      st.session_state.mc_stoch_longevity or st.session_state.mc_ltc_enable or
                      st.session_state.mc_tax_regime or st.session_state.mc_ss_haircut_prob > 0)

        # Target lifestyle in REAL 2026 $ is constant within each age band (golden/middle/
        # wind-down); recompute per retirement year so we can score actual vs target.
        def target_real_by_age(a):
            if a < 70: return st.session_state.spend_golden
            elif a < 85: return st.session_state.spend_middle
            else: return st.session_state.spend_wind
        ret_years = [y for y in years if y >= ret_start_yr]
        target_real_map = {y: target_real_by_age(start_age + (y - 2026)) for y in ret_years}
        total_target_real = sum(target_real_map.values())
        gift_goal = float(st.session_state.mc_gift_goal)

        # Per-path collectors for the new insight groups.
        lifetime_gift_real = []      # total real generational gift per path
        lifestyle_funded_ratio = []  # achieved real lifestyle / target, over retirement
        years_below_target = []      # count of retirement years with a meaningful cut
        full_lifestyle_path = []     # bool: avg funded ratio >= 95%
        first_cut_age = []           # age of first lifestyle cut (np.nan if none)
        worst_drawdown = []          # largest peak-to-trough real drop per path
        path_success = []            # bool: money outlasted the household (true success)
        fin_depletion_age = []       # age the portfolio actually hit zero (ignoring death)
        death_age_arr = []           # survivor death age for this path (or 100 if not modeled)

        progress = st.progress(0.0, text="Running simulations...")
        for run in range(n_runs):
            usd_draws, eur_draws, bond_draws = make_paths()
            ret_map = {years[i]: (float(usd_draws[i]), float(eur_draws[i])) for i in range(n_years)}
            scen = build_scenario(usd_draws, eur_draws) if any_stress else {}
            scen['returns'] = ret_map
            scen['bond'] = {years[i]: float(bond_draws[i]) for i in range(n_years)}
            df_bal, df_draw, _, _, _ = run_core_simulation(scenario=scen)
            total = df_bal.loc['Total Portfolio Balance']

            # Per-path real discounting: use the path's realized inflation when stochastic,
            # else the deterministic rate. Build a cumulative CPI discount factor by year.
            if 'inflation' in scen:
                disc_map = {}; cpi = 1.0
                for y in years:
                    if y > 2026: cpi *= (1 + scen['inflation'][y])
                    disc_map[y] = cpi
            else:
                disc_map = {y: (1 + inf_rate) ** (y - 2026) for y in years}

            real_series = np.array([total[y] / disc_map[y] for y in years])
            real_paths[run, :] = real_series

            # Success = solvent through the survivor's actual death year (not a fixed 100).
            # With stochastic longevity, dying early is NOT a planning "win": a path only
            # succeeds if the money outlasts the household. Depletion AFTER both have died
            # is irrelevant (you can't run out after you're gone), so it counts as success.
            horizon_yr = scen.get('death_year', 2089)
            depleted = total[total <= 0]
            if len(depleted) > 0:
                first_zero_yr = depleted.index.min()
                if first_zero_yr <= horizon_yr:
                    depletion_ages.append(first_zero_yr - 2026 + start_age)
                    path_success.append(False)
                else:
                    success += 1
                    depletion_ages.append(horizon_yr - 2026 + start_age)
                    path_success.append(True)
            else:
                success += 1
                depletion_ages.append(horizon_yr - 2026 + start_age)
                path_success.append(True)
            terminal_real.append(real_series[-1])

            # Pure financial depletion age (when portfolio hit zero, regardless of death),
            # and the survivor death age, for the conditional-solvency survival curve.
            fin_depletion_age.append((depleted.index.min() - 2026 + start_age) if len(depleted) > 0 else 101)
            death_age_arr.append((horizon_yr - 2026 + start_age) if 'death_year' in scen else 100)

            # --- Lifestyle quality (real 2026 $) ---
            life_nom = df_draw.loc["Actual Lifestyle Spend"]
            gift_nom = df_draw.loc["Actual Generational Drip"]
            achieved_real_total = 0.0
            cut_count = 0
            first_cut = np.nan
            # Score lifestyle only over years the household is alive (longevity stops
            # spending after death_year); otherwise post-death zero-spend years would
            # wrongly count as lifestyle "cuts".
            death_yr = scen.get('death_year', 9999)
            scored_years = [y for y in ret_years if y <= death_yr]
            # Survivor-adjust the target (Tier-2 fix #8): after the first death the engine
            # intentionally spends at survivor_expense_ratio of the couple's target, so the
            # target must scale down too -- otherwise the planned reduction would wrongly
            # count as a lifestyle shortfall (the old divergence vs the dashboard).
            _fd_yr = scen.get('_first_death_yr')
            _surv_on = st.session_state.survivor_enable and (_fd_yr is not None)
            _s_ratio = st.session_state.survivor_expense_ratio if _surv_on else 1.0
            def _adj_tgt(y):
                t = target_real_map[y]
                return t * _s_ratio if (_surv_on and y > _fd_yr) else t
            scored_target = sum(_adj_tgt(y) for y in scored_years) or 1.0
            for y in scored_years:
                disc = disc_map[y]
                achieved_real = life_nom.get(y, 0.0) / disc
                achieved_real_total += achieved_real
                tgt = _adj_tgt(y)
                if tgt > 0 and achieved_real < 0.99 * tgt:  # 1% tolerance = a real cut
                    cut_count += 1
                    if np.isnan(first_cut):
                        first_cut = start_age + (y - 2026)
            ratio = achieved_real_total / scored_target
            lifestyle_funded_ratio.append(ratio)
            years_below_target.append(cut_count)
            full_lifestyle_path.append(ratio >= 0.95)
            first_cut_age.append(first_cut)

            # --- Gifting (real 2026 $) ---
            gift_total_real = sum(gift_nom.get(y, 0.0) / disc_map[y] for y in ret_years)
            lifetime_gift_real.append(gift_total_real)

            # --- Worst market shock experienced in the path ---
            # A deliberate spend-down plan drives the real balance toward ~0 by age 100 by
            # design, so a portfolio peak-to-trough mostly measures intended decumulation,
            # not risk. Instead we capture the worst MARKET shock the path actually drew:
            # the single worst year and the worst 3-year cumulative real-equity return
            # (USD sleeve), which is the sequence risk that endangers the plan.
            usd_real = np.array([usd_draws[i] - inf_rate for i in range(n_years)])
            worst_1yr = float(usd_real.min())
            if n_years >= 3:
                cum3 = [np.prod(1 + usd_real[i:i+3]) - 1 for i in range(n_years - 2)]
                worst_3yr = float(min(cum3))
            else:
                worst_3yr = worst_1yr
            worst_drawdown.append((worst_1yr, worst_3yr))

            if run % max(1, n_runs // 50) == 0:
                progress.progress(run / n_runs, text=f"Running simulations... {run}/{n_runs}")
        progress.progress(1.0, text="Complete.")

        terminal_real = np.array(terminal_real)
        depletion_ages = np.array(depletion_ages)
        lifetime_gift_real = np.array(lifetime_gift_real)
        lifestyle_funded_ratio = np.array(lifestyle_funded_ratio)
        years_below_target = np.array(years_below_target)
        full_lifestyle_path = np.array(full_lifestyle_path)
        first_cut_age = np.array(first_cut_age, dtype=float)
        worst_drawdown = np.array(worst_drawdown)  # shape (n_runs, 2): [worst_1yr, worst_3yr]
        worst_1yr_arr = worst_drawdown[:, 0]
        worst_3yr_arr = worst_drawdown[:, 1]
        path_success = np.array(path_success)
        fin_depletion_age = np.array(fin_depletion_age)
        death_age_arr = np.array(death_age_arr)
        success_rate = 100.0 * success / n_runs

        # Joint success: money outlasted the household AND avg lifestyle >= 95% AND hit gift goal.
        never_deplete = path_success
        hit_gift = lifetime_gift_real >= gift_goal
        joint_success = never_deplete & full_lifestyle_path & hit_gift
        joint_rate = 100.0 * np.mean(joint_success)

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Plan Success Rate", f"{success_rate:.1f}%",
                  help="Money outlasted the household: solvent through the survivor's death "
                       "(or to age 100 if longevity isn't randomized). Dying early is not counted as success.")
        c2.metric("Median Terminal Wealth (Real)", f"${np.median(terminal_real)/1e6:,.2f}M")
        c3.metric("10th-Pctile Terminal Wealth", f"${np.percentile(terminal_real,10)/1e6:,.2f}M")
        c4.metric("Median Survivor Death Age", f"{np.median(death_age_arr):.0f}" if st.session_state.mc_stoch_longevity else "100 (fixed)")

        # Financial survival by age, CONDITIONAL on the household still being alive: among
        # paths where someone is alive at age X, the share still financially solvent. This
        # is the honest "will the money be there if we live that long" curve, and it does
        # not reward early death the way an unconditional curve would.
        st.markdown("---")
        st.subheader("Financial Survival by Age (Solvent, Given You're Still Alive)")
        target_ages = list(range(70, 101))
        survival = []
        for a in target_ages:
            alive = death_age_arr >= a
            n_alive = np.sum(alive)
            if n_alive > 0:
                survival.append(100.0 * np.mean(fin_depletion_age[alive] >= a))
            else:
                survival.append(np.nan)

        fig_surv = go.Figure()
        fig_surv.add_trace(go.Scatter(
            x=target_ages, y=survival, mode='lines+markers',
            line=dict(color='#1f77b4', width=3), marker=dict(size=5),
            fill='tozeroy', fillcolor='rgba(31,119,180,0.12)',
            hovertemplate="Age %{x}: %{y:.1f}% solvent (of those alive)<extra></extra>", name="Solvent %"
        ))
        for thr, lbl in [(95, "95%"), (90, "90%"), (80, "80%")]:
            fig_surv.add_hline(y=thr, line_dash="dot", line_color="grey", opacity=0.5,
                               annotation_text=lbl, annotation_position="right")
        fig_surv.update_layout(
            xaxis=dict(title="Age", dtick=5), yaxis=dict(title="Solvent, of Those Alive (%)", range=[0, 101]),
            hovermode="x unified", showlegend=False, height=400
        )
        st.plotly_chart(fig_surv, use_container_width=True)

        milestone_ages = [70, 75, 80, 85, 90, 95, 100]
        def _solv(a):
            alive = death_age_arr >= a
            return f"{100.0*np.mean(fin_depletion_age[alive] >= a):.1f}%" if np.sum(alive) > 0 else "n/a"
        df_surv = pd.DataFrame({
            "Age": milestone_ages,
            "Solvent if Alive (%)": [_solv(a) for a in milestone_ages]
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

        # ----------------------------------------------------------------------
        # JOINT SUCCESS: the headline "did I get everything" number
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.subheader("Did You Get Everything You Planned For?")
        st.markdown(
            "A plan can avoid running out of money while still slashing your lifestyle for "
            "years or gifting almost nothing. These metrics separate *surviving* from "
            "*thriving*. **Joint success** = never depleted AND average lifestyle \u2265 95% of "
            "target AND lifetime gift \u2265 your goal."
        )
        jc1, jc2, jc3, jc4 = st.columns(4)
        jc1.metric("Never Ran Out of Money", f"{100.0*np.mean(never_deplete):.1f}%")
        jc2.metric("Full Lifestyle (\u226595% of target)", f"{100.0*np.mean(full_lifestyle_path):.1f}%")
        jc3.metric(f"Hit Gift Goal (\u2265${gift_goal/1e6:.1f}M)", f"{100.0*np.mean(hit_gift):.1f}%")
        jc4.metric("JOINT Success (all three)", f"{joint_rate:.1f}%")

        # Funnel showing attrition from survival -> full lifestyle -> + gift goal.
        funnel_labels = ["Never Depleted", "+ Full Lifestyle", "+ Hit Gift Goal (Joint)"]
        funnel_vals = [
            100.0*np.mean(never_deplete),
            100.0*np.mean(never_deplete & full_lifestyle_path),
            joint_rate
        ]
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels, x=funnel_vals, textinfo="value+percent initial",
            marker=dict(color=["#2ca02c", "#1f77b4", "#9467bd"])
        ))
        fig_funnel.update_layout(title="From Surviving to Thriving (% of paths)", height=300, margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig_funnel, use_container_width=True)

        # ----------------------------------------------------------------------
        # LIFESTYLE QUALITY
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.subheader("Lifestyle Quality")
        lc1, lc2, lc3 = st.columns(3)
        lc1.metric("Median Lifestyle Funded", f"{np.median(lifestyle_funded_ratio)*100:.1f}%",
                   help="Total real lifestyle spending achieved vs. target, across retirement.")
        lc2.metric("10th-Pctile Lifestyle Funded", f"{np.percentile(lifestyle_funded_ratio,10)*100:.1f}%",
                   help="In a bad path (bottom 10%), this share of target lifestyle was funded.")
        lc3.metric("Median Years With a Cut", f"{np.median(years_below_target):.0f}",
                   help="Retirement years spent below target (guardrails active).")

        fig_life = px.histogram(x=lifestyle_funded_ratio*100, nbins=40,
                                labels={'x': 'Lifestyle Funded Ratio (% of target, real)'})
        fig_life.add_vline(x=95, line_dash="dot", line_color="green", annotation_text="95% bar")
        fig_life.update_layout(title="Distribution of Lifestyle Funded Ratio Across Paths",
                               yaxis_title="Number of Simulations", showlegend=False, height=350)
        st.plotly_chart(fig_life, use_container_width=True)

        # Years-on-floor distribution.
        fig_floor = px.histogram(x=years_below_target, nbins=int(max(years_below_target)+1) if len(years_below_target) and max(years_below_target)>0 else 10,
                                 labels={'x': 'Number of Retirement Years Below Target Lifestyle'})
        fig_floor.update_layout(title="How Many Years Get Pinched (Lifestyle Below Target)",
                                yaxis_title="Number of Simulations", showlegend=False, height=350)
        st.plotly_chart(fig_floor, use_container_width=True)

        # ----------------------------------------------------------------------
        # GIFTING DISTRIBUTION
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.subheader("Generational Gifting Outcomes")
        gc1, gc2, gc3, gc4 = st.columns(4)
        gc1.metric("Gifting Success Rate", f"{100.0*np.mean(hit_gift):.1f}%",
                   help=f"Share of paths with lifetime real gift \u2265 ${gift_goal/1e6:.1f}M goal.")
        gc2.metric("Any Meaningful Gift (>$0)", f"{100.0*np.mean(lifetime_gift_real>1000):.1f}%")
        gc3.metric("Median Lifetime Gift", f"${np.median(lifetime_gift_real)/1e6:,.2f}M")
        gc4.metric("10th-Pctile Lifetime Gift", f"${np.percentile(lifetime_gift_real,10)/1e6:,.2f}M")

        fig_gift = px.histogram(x=lifetime_gift_real/1e6, nbins=50,
                                labels={'x': 'Total Lifetime Gift (Millions, real 2026 $)'})
        fig_gift.add_vline(x=gift_goal/1e6, line_dash="dot", line_color="gold", annotation_text="Goal")
        fig_gift.update_layout(title="Distribution of Total Lifetime Gifting (Real 2026 $)",
                               yaxis_title="Number of Simulations", showlegend=False, height=350)
        st.plotly_chart(fig_gift, use_container_width=True)
        st.caption(
            f"Median path gifts ${np.median(lifetime_gift_real)/1e6:,.2f}M in real terms, but the "
            f"bottom 10% of paths gift only ${np.percentile(lifetime_gift_real,10)/1e6:,.2f}M or less. "
            "Gifting is the first thing the guardrails sacrifice, so it varies more than lifestyle."
        )

        # ----------------------------------------------------------------------
        # RISK TIMING
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.subheader("Risk Timing")
        valid_cuts = first_cut_age[~np.isnan(first_cut_age)]
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Median Worst 1-Year Real Return", f"{np.median(worst_1yr_arr)*100:.0f}%",
                   help="The worst single-year real equity (USD sleeve) return drawn in the typical path.")
        rc2.metric("Median Worst 3-Year Cumulative", f"{np.median(worst_3yr_arr)*100:.0f}%",
                   help="Worst 3-year cumulative real equity return per path; captures sustained crashes / sequence risk.")
        rc3.metric("Paths With a Lifestyle Cut", f"{100.0*np.mean(~np.isnan(first_cut_age)):.1f}%")

        if len(valid_cuts) > 0:
            fig_cut = px.histogram(x=valid_cuts, nbins=30,
                                   labels={'x': 'Age of First Lifestyle Cut'})
            fig_cut.update_layout(title="When the First Lifestyle Cut Happens (paths that get cut)",
                                  yaxis_title="Number of Simulations", showlegend=False, height=350)
            st.plotly_chart(fig_cut, use_container_width=True)
            st.caption(
                f"Among paths that suffer a cut, the median first cut lands at age {np.median(valid_cuts):.0f}. "
                "Earlier cuts are more damaging because they compound over more remaining years."
            )
        else:
            st.info("No lifestyle cuts occurred in any simulated path under these settings.")

        # ----------------------------------------------------------------------
        # LONGEVITY TAIL: the real longevity risk is living long, not the average
        # ----------------------------------------------------------------------
        if st.session_state.mc_stoch_longevity:
            st.markdown("---")
            st.subheader("Longevity Tail Risk")
            st.markdown(
                "Longevity's danger isn't the average case (most people don't reach 100) but the "
                "**tail** where one of you lives a long time. These show how the plan holds up "
                "specifically in the long-life paths."
            )
            long_paths = death_age_arr >= 90
            very_long = death_age_arr >= 95
            lt1, lt2, lt3 = st.columns(3)
            lt1.metric("Survivor Reaches 90+", f"{100.0*np.mean(long_paths):.0f}%",
                       help="Share of paths where at least one spouse lives to 90 or beyond.")
            if np.sum(long_paths) > 0:
                lt2.metric("Success | Survivor Lives 90+", f"{100.0*np.mean(path_success[long_paths]):.0f}%",
                           help="Plan-success rate conditional on a long life (90+). This is the number that matters.")
            if np.sum(very_long) > 0:
                lt3.metric("Success | Survivor Lives 95+", f"{100.0*np.mean(path_success[very_long]):.0f}%")
            overall_succ = np.mean(path_success)*100
            cond_succ = np.mean(path_success[long_paths])*100 if np.sum(long_paths) > 0 else overall_succ
            st.caption(
                f"Overall success is {overall_succ:.0f}%, but conditional on a survivor reaching 90+ it is "
                f"{cond_succ:.0f}%. The gap is your true longevity exposure: the plan is "
                + ("meaningfully weaker" if overall_succ - cond_succ > 8 else "fairly robust")
                + " in long-life scenarios. This is why longevity is shown here rather than in the tornado "
                "(it shifts the success horizon rather than acting as a market-style shock)."
            )
            if st.session_state.survivor_enable:
                st.caption(
                    f"Survivor scenario is **active**: in every path with a first death, SS drops to the larger "
                    f"benefit, spending falls to {st.session_state.survivor_expense_ratio:.0%} of the couple's, and "
                    f"the survivor files single (widow's-penalty surcharge {st.session_state.survivor_tax_surcharge:.2f}\u00d7 "
                    "on US tax). The higher earner delaying SS to 70 is what most protects the survivor here \u2014 a direct "
                    "link to the claim-age optimizer."
                )
            else:
                st.caption("Survivor scenario is **off** \u2014 the couple's full spending is assumed until the second death, which is conservative (overstates spending in the survivor years).")

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

    # ======================================================================
    # SENSITIVITY TORNADO: isolate each factor's marginal impact on success
    # ======================================================================
    st.markdown("---")
    st.subheader("Sensitivity Tornado (Marginal Impact of Each Assumption)")
    st.markdown(
        "Runs the simulation once with **only equity returns random** (baseline), then turns "
        "on **one stress factor at a time**, holding everything else at base. The bars show "
        "how many percentage points each factor moves your plan-success rate. This tells you "
        "which risk your plan is actually most fragile to."
    )
    tornado_runs = st.number_input("Simulations per factor (lower = faster)", value=400, min_value=100, max_value=2000, step=100, key="tornado_runs")
    st.caption("Uses the same return engine and the **valuation-conditioning + crisis-regime settings from the Monte Carlo page above**, so the tornado is consistent with your main simulation.")

    if st.button("Run Sensitivity Tornado"):
        t_years = list(range(2026, 2090)); t_n = len(t_years)
        t_inf = st.session_state.inflation_rate / 100.0
        t_start = st.session_state.current_age
        t_ret_start = 2026 + (st.session_state.ret_age - st.session_state.current_age)
        t_ret_years = [y for y in t_years if y >= t_ret_start]
        t_gift_goal = float(st.session_state.mc_gift_goal)
        def t_tgt(a):
            return st.session_state.spend_golden if a < 70 else (st.session_state.spend_middle if a < 85 else st.session_state.spend_wind)
        t_tmap = {y: t_tgt(t_start + (y - 2026)) for y in t_ret_years}
        t_total_tgt = sum(t_tmap.values()) or 1.0

        # Return generation, stress factors, and scoring all come from the SHARED
        # MONTE CARLO MACHINERY, so the tornado evaluates against exactly the same
        # conditioned world (full-history recentering, valuation shift, crisis
        # overlay) and the same survivor-aware joint-success definition as the
        # main simulation and the dashboard. The 'longevity' factor now carries
        # the first-death year, so the survivor scenario engages here too.
        def t_make(rng):
            return make_bootstrap_paths(rng, t_n)

        def t_scenario(flags, usd, eur, rng):
            return build_stress_scenario(rng, usd, flags=set(flags) if flags else set(), years=t_years)

        def t_run(flags, n, seed=12345):
            # Common random numbers: equity paths AND factor draws use fixed seeds across all
            # runs, so baseline, singles and pairs see identical markets and factor realizations.
            # This is what makes the interaction signal trustworthy rather than MC noise.
            eq_rng = np.random.default_rng(seed)
            fac_rng = np.random.default_rng(seed + 7777)
            joint_ok = 0
            for _ in range(n):
                usd, eur, bond = t_make(eq_rng)
                sc = t_scenario(flags, usd, eur, fac_rng) if flags else {}
                sc['returns'] = {t_years[i]: (float(usd[i]), float(eur[i])) for i in range(t_n)}
                sc['bond'] = {t_years[i]: float(bond[i]) for i in range(t_n)}
                db, dd, _, _, _ = run_core_simulation(scenario=sc)
                if score_path_joint(db, dd, sc, t_ret_years, t_tmap, t_gift_goal)['joint']:
                    joint_ok += 1
            return 100.0 * joint_ok / n

        tn = int(st.session_state.tornado_runs)
        prog = st.progress(0.0, text="Running tornado...")
        baseline = t_run(None, tn); prog.progress(1/8, text="Baseline done")
        factors = [
            ('inflation', 'Stochastic Inflation', st.session_state.mc_stoch_inflation),
            ('fx', 'EUR/USD Exchange Rate', st.session_state.mc_stoch_fx),
            # Longevity is intentionally excluded from the tornado: it changes the success
            # HORIZON rather than acting as a shock, so its "impact" is an artifact of most
            # people not living to 100. Its real (tail) risk is shown in the longevity panel.
            ('ltc', 'Long-Term Care Shock', st.session_state.mc_ltc_enable),
            ('tax', 'Tax-Regime Drift', st.session_state.mc_tax_regime),
            ('ss', 'Social Security Cut', st.session_state.mc_ss_haircut_prob > 0),
        ]
        results = []
        for i, (flag, label, enabled) in enumerate(factors):
            if not enabled:
                continue
            rate = t_run([flag], tn)
            results.append((label, rate - baseline))
            prog.progress((i+2)/8, text=f"{label} done")
        prog.progress(1.0, text="Complete.")

        st.metric("Baseline Joint-Success (equity returns only)", f"{baseline:.1f}%")
        if results:
            results.sort(key=lambda r: r[1])  # most negative (most damaging) first
            labels = [r[0] for r in results]
            deltas = [r[1] for r in results]
            colors = ['#d62728' if d < 0 else '#2ca02c' for d in deltas]
            fig_t = go.Figure(go.Bar(x=deltas, y=labels, orientation='h', marker_color=colors,
                                     text=[f"{d:+.1f} pts" for d in deltas], textposition='outside'))
            fig_t.update_layout(
                title="Marginal Impact on Joint-Success Rate (percentage points vs baseline)",
                xaxis_title="Change in Joint-Success Rate (pts)", height=350,
                margin=dict(l=10, r=40, t=40, b=10)
            )
            st.plotly_chart(fig_t, use_container_width=True)
            worst = results[0]
            st.caption(
                f"Your plan is most fragile to **{worst[0]}** ({worst[1]:+.1f} pts). Factors are tested "
                "one at a time against an equity-only baseline. Interactions between factors are NOT in "
                "these bars \u2014 the interaction matrix below quantifies how much worse pairs are together "
                "than the sum of their individual bars."
            )
        else:
            st.info("No stress factors are enabled. Turn some on in the Stress Factors panel above.")

    # ======================================================================
    # INTERACTION MATRIX: how much worse are factor PAIRS than the sum of parts
    # ======================================================================
    st.markdown("---")
    st.subheader("Interaction Matrix (Compounding Risk Between Factors)")
    st.markdown(
        "The tornado tests factors one at a time. This matrix asks a deeper question: do two "
        "risks **compound** when they hit together? Each off-diagonal cell shows the "
        "*interaction effect* = (success with both) \u2212 (success with A alone) \u2212 (success with B "
        "alone) + baseline. A strongly **negative** cell means the pair is more dangerous together "
        "than their individual tornado bars predict (e.g. a stock crash *and* high inflation at "
        "once). Near-zero means the two are roughly independent. The diagonal shows each factor's "
        "solo impact for reference."
    )
    matrix_runs = st.number_input("Simulations per cell (lower = faster; 16 cells)", value=300, min_value=100, max_value=1500, step=100, key="matrix_runs")
    st.caption("Inherits the **valuation-conditioning + crisis-regime settings from the Monte Carlo page**, so interaction effects are measured against the same conditioned world.")
    st.caption("Note: a 5-factor matrix runs baseline + 5 singles + 10 pairs = 16 batches. At 300 paths that's ~4,800 full simulations; expect this to take a bit.")

    if st.button("Run Interaction Matrix"):
        im_years = list(range(2026, 2090)); im_n = len(im_years)
        im_inf = st.session_state.inflation_rate / 100.0
        im_start = st.session_state.current_age
        im_ret_start = 2026 + (st.session_state.ret_age - st.session_state.current_age)
        im_ret_years = [y for y in im_years if y >= im_ret_start]
        im_gift_goal = float(st.session_state.mc_gift_goal)
        def im_tgt(a):
            return st.session_state.spend_golden if a < 70 else (st.session_state.spend_middle if a < 85 else st.session_state.spend_wind)
        im_tmap = {y: im_tgt(im_start + (y - 2026)) for y in im_ret_years}

        # Shared machinery: identical conditioned world and survivor-aware joint
        # scoring as the main MC, dashboard, and tornado.
        def im_make(rng):
            return make_bootstrap_paths(rng, im_n)

        def im_scenario(flags, usd, rng):
            return build_stress_scenario(rng, usd, flags=set(flags), years=im_years)

        def im_run(flags, n, seed=2024):
            eq = np.random.default_rng(seed); fac = np.random.default_rng(seed + 7777)
            ok = 0
            for _ in range(n):
                usd, eur, bond = im_make(eq)
                sc = im_scenario(flags, usd, fac) if flags else {}
                sc['returns'] = {im_years[i]: (float(usd[i]), float(eur[i])) for i in range(im_n)}
                sc['bond'] = {im_years[i]: float(bond[i]) for i in range(im_n)}
                db, dd, _, _, _ = run_core_simulation(scenario=sc)
                if score_path_joint(db, dd, sc, im_ret_years, im_tmap, im_gift_goal)['joint']:
                    ok += 1
            return 100.0 * ok / n

        # Only include factors the user has enabled (longevity excluded by design).
        all_factors = [
            ('inflation', 'Inflation', st.session_state.mc_stoch_inflation),
            ('fx', 'FX', st.session_state.mc_stoch_fx),
            ('ltc', 'LTC', st.session_state.mc_ltc_enable),
            ('tax', 'Tax', st.session_state.mc_tax_regime),
            ('ss', 'SS Cut', st.session_state.mc_ss_haircut_prob > 0),
        ]
        active = [(f, lbl) for (f, lbl, en) in all_factors if en]

        if len(active) < 2:
            st.info("Enable at least two stress factors (in the panel above) to compute interactions.")
        else:
            mn = int(st.session_state.matrix_runs)
            keys = [f for f, _ in active]; labels = [lbl for _, lbl in active]
            total_cells = 1 + len(keys) + len(keys)*(len(keys)-1)//2
            prog = st.progress(0.0, text="Computing matrix...")
            done = 0
            base = im_run([], mn); done += 1; prog.progress(done/total_cells, text="Baseline done")
            singles = {}
            for k in keys:
                singles[k] = im_run([k], mn); done += 1
                prog.progress(done/total_cells, text=f"{k} solo done")
            pair_combined = {}
            for a in range(len(keys)):
                for b in range(a+1, len(keys)):
                    ka, kb = keys[a], keys[b]
                    pair_combined[(ka, kb)] = im_run([ka, kb], mn); done += 1
                    prog.progress(min(1.0, done/total_cells), text=f"{ka}+{kb} done")
            prog.progress(1.0, text="Complete.")

            # Build matrices: diagonal = solo impact (single - base); off-diag = interaction.
            nF = len(keys)
            Z = np.full((nF, nF), np.nan)
            text = [["" for _ in range(nF)] for _ in range(nF)]
            for i in range(nF):
                solo_i = singles[keys[i]] - base
                Z[i][i] = solo_i
                text[i][i] = f"solo<br>{solo_i:+.1f}"
                for j in range(nF):
                    if i == j: continue
                    ka, kb = keys[min(i,j)], keys[max(i,j)]
                    both = pair_combined[(ka, kb)]
                    inter = (both - base) - (singles[ka] - base) - (singles[kb] - base)
                    Z[i][j] = inter
                    text[i][j] = f"{inter:+.1f}"

            import plotly.graph_objects as _go
            fig_m = _go.Figure(data=_go.Heatmap(
                z=Z, x=labels, y=labels, text=text, texttemplate="%{text}",
                colorscale=[[0,'#b2182b'],[0.5,'#f7f7f7'],[1,'#2166ac']], zmid=0,
                colorbar=dict(title="Effect (pts)"),
                hovertemplate="%{y} \u00d7 %{x}<br>Effect: %{z:+.1f} pts<extra></extra>"
            ))
            fig_m.update_layout(
                title="Interaction Effects on Joint-Success (off-diagonal) & Solo Impact (diagonal)",
                height=480, yaxis=dict(autorange='reversed'), margin=dict(l=10,r=10,t=50,b=10)
            )
            st.plotly_chart(fig_m, use_container_width=True)

            # Find the strongest compounding pair.
            worst_pair = None; worst_val = 0.0
            for (ka, kb), both in pair_combined.items():
                inter = (both - base) - (singles[ka] - base) - (singles[kb] - base)
                if inter < worst_val:
                    worst_val = inter; worst_pair = (ka, kb)
            st.metric("Baseline Joint-Success (equity only)", f"{base:.1f}%")
            if worst_pair and worst_val < -1.0:
                lbl_map = dict(active)
                st.warning(
                    f"Strongest compounding pair: **{lbl_map[worst_pair[0]]} + {lbl_map[worst_pair[1]]}** "
                    f"({worst_val:.1f} pts beyond the sum of their individual effects). These two risks "
                    "reinforce each other and deserve a dedicated hedge or larger cash buffer."
                )
            else:
                st.success(
                    "No strong compounding pairs detected: the factors behave roughly independently, so "
                    "the tornado bars already capture most of the risk. (Interactions within ~1 pt are "
                    "indistinguishable from Monte Carlo noise at this path count.)"
                )
            st.caption(
                "Blue = the pair is *less* bad together than the sum of parts (mild offsetting); red = "
                "*more* bad together (compounding). Built with common random numbers so the interaction "
                "signal isn't swamped by sampling noise. Longevity is excluded (it shifts the success "
                "horizon rather than acting as a shock). Raise simulations-per-cell to sharpen faint signals."
            )

# -----------------------------------------------------------------------------
# 13. ROTH CONVERSION LADDER OPTIMIZER
# -----------------------------------------------------------------------------
elif selection == "13. Roth Conversion Ladder Optimizer":
    st.header("13. Roth Conversion Ladder Optimizer")
    st.markdown(
        "Finds the pre-tax \u2192 Roth conversion strategy that maximizes your Monte Carlo "
        "**joint-success rate**, optimizing across the US *and* Slovenian tax regimes. "
        "Conversions are US-taxable ordinary income always; **post-move conversions are also "
        "taxed by Slovenia** (the double-hit), and Slovenia is assumed to tax Roth "
        "distributions later at your Roth Trap Rate. Because of that double exposure, the "
        "optimizer will generally favor converting in the **pre-move US window (ages 55-56)** "
        "and avoid post-move conversions \u2014 but it discovers that from the mechanics rather "
        "than being told."
    )
    st.info(
        "Why pre-move is the valley: ages 55-56 you're a US resident with no wages, no Social "
        "Security, and no RMDs \u2014 so conversions fill low US brackets at ordinary rates with no "
        "Slovenian tax. After the move, a conversion is taxed by both countries going in, and the "
        "Roth may be taxed again coming out, which usually destroys the benefit."
    )

    o1, o2, o3 = st.columns(3)
    opt_max_conv = o1.number_input("Max Annual Conversion to Test ($)", value=150000, min_value=0, step=25000)
    opt_grid = o2.number_input("Grid Points (conversion levels)", value=7, min_value=3, max_value=12, step=1)
    opt_runs = o3.number_input("Paths per Strategy", value=200, min_value=50, max_value=600, step=50)

    w1, w2 = st.columns(2)
    opt_start_age = w1.number_input("Conversion Window Start Age", value=55, step=1)
    opt_end_age = w2.number_input("Conversion Window End Age", value=56, step=1, help="Default 55-56 = the pre-move US window. Extend past the move age to let the optimizer test (and likely reject) post-move conversions.")
    opt_us_rate = st.number_input("US Ordinary Rate on Conversions (%)", value=st.session_state.roth_conv_us_rate, step=1.0, help="The marginal US bracket the conversion fills. ~10-24% in the low-income valley years.")
    st.caption("Scored on the same Monte Carlo engine, including the **valuation-conditioning + crisis-regime settings from the Monte Carlo page** \u2014 so the optimal conversion is robust to the conditioned, crisis-prone world rather than an optimistic one.")

    if st.button("Optimize Conversion Ladder"):
        st.session_state.roth_conv_us_rate = opt_us_rate
        o_years = list(range(2026, 2090)); o_n = len(o_years)
        o_inf = st.session_state.inflation_rate / 100.0
        o_start = st.session_state.current_age
        o_ret_start = 2026 + (st.session_state.ret_age - st.session_state.current_age)
        o_ret_years = [y for y in o_years if y >= o_ret_start]
        o_gift_goal = float(st.session_state.mc_gift_goal)
        def o_tgt(a):
            return st.session_state.spend_golden if a < 70 else (st.session_state.spend_middle if a < 85 else st.session_state.spend_wind)
        o_tmap = {y: o_tgt(o_start + (y - 2026)) for y in o_ret_years}

        # Shared machinery: same conditioned bootstrap world and survivor-aware
        # joint scoring as the main MC. Stochastic LONGEVITY (with the survivor
        # scenario) and the SS-haircut lottery are now part of the optimizer's
        # objective -- conversions trade off against RMD-era exposure, and death
        # timing is exactly what determines how long that era lasts. Common
        # random numbers (fixed seeds) keep conversion levels comparable.
        def o_make(rng):
            return make_bootstrap_paths(rng, o_n)

        def o_score(conv_amt, n, seed=4242):
            eq = np.random.default_rng(seed)
            fac = np.random.default_rng(seed + 7777)
            ok = 0
            for _ in range(n):
                usd, eur, bond = o_make(eq)
                sc = build_stress_scenario(fac, usd, flags={'longevity', 'ss'}, years=o_years)
                sc['returns'] = {o_years[i]: (float(usd[i]), float(eur[i])) for i in range(o_n)}
                sc['bond'] = {o_years[i]: float(bond[i]) for i in range(o_n)}
                sc['roth_conv'] = (conv_amt, int(opt_start_age), int(opt_end_age))
                db, dd, _, _, _ = run_core_simulation(scenario=sc)
                if score_path_joint(db, dd, sc, o_ret_years, o_tmap, o_gift_goal)['joint']:
                    ok += 1
            return 100.0 * ok / n

        levels = np.linspace(0, int(opt_max_conv), int(opt_grid))
        prog = st.progress(0.0, text="Sweeping conversion levels...")
        scores = []
        for i, lv in enumerate(levels):
            scores.append(o_score(int(lv), int(opt_runs)))
            prog.progress((i+1)/len(levels), text=f"Tested ${int(lv):,}/yr")
        prog.progress(1.0, text="Complete.")
        scores = np.array(scores)

        best_i = int(np.argmax(scores))
        best_conv = int(levels[best_i]); best_score = scores[best_i]
        zero_score = scores[0]

        fig = go.Figure(go.Scatter(
            x=levels, y=scores, mode='lines+markers',
            line=dict(color='#2166ac', width=3), marker=dict(size=8),
            hovertemplate="$%{x:,.0f}/yr: %{y:.1f}% joint success<extra></extra>"
        ))
        fig.add_vline(x=best_conv, line_dash="dash", line_color="green",
                      annotation_text=f"Optimal ${best_conv:,}", annotation_position="top")
        fig.update_layout(
            title=f"Joint-Success Rate vs Annual Roth Conversion (ages {int(opt_start_age)}-{int(opt_end_age)})",
            xaxis_title="Annual Conversion Amount ($, today's purchasing power)",
            yaxis_title="Monte Carlo Joint-Success (%)", height=420
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Optimal Annual Conversion", f"${best_conv:,}")
        c2.metric("Joint-Success at Optimum", f"{best_score:.1f}%")
        c3.metric("vs No Conversion", f"{best_score - zero_score:+.1f} pts")

        win = int(opt_end_age) - int(opt_start_age) + 1
        if best_conv > 0:
            st.success(
                f"**Optimal strategy:** convert **${best_conv:,}/year** (today's dollars) for "
                f"{win} year(s), ages {int(opt_start_age)}-{int(opt_end_age)} \u2014 about "
                f"**${best_conv*win:,}** total. This lifts joint-success by "
                f"**{best_score - zero_score:+.1f} points** versus doing no conversions. To apply it, "
                f"set Roth Conversion params on the relevant input page (annual ${best_conv:,}, ages "
                f"{int(opt_start_age)}-{int(opt_end_age)})."
            )
        else:
            st.warning(
                "**Optimal strategy: do NOT convert.** Given your tax assumptions (especially the "
                "Slovenian Roth Trap and the post-move double-hit), conversions reduce joint-success. "
                "This typically means your projected retirement tax rates aren't high enough above your "
                "conversion-year rates to justify paying tax early \u2014 or the conversion window is "
                "mostly post-move where the double taxation dominates."
            )
        if int(opt_end_age) >= (o_start + (st.session_state.move_age - st.session_state.current_age)):
            st.caption(
                "Your conversion window extends past the move age, so the optimizer is testing post-move "
                "conversions too. If the optimum lands in the pre-move years, that's the model confirming "
                "the standard expat playbook: convert before you leave the US tax-only world."
            )
        st.caption(
            "Optimization uses common random numbers (identical simulated markets across every conversion "
            "level) so the comparison reflects the strategy, not Monte Carlo noise. Scored on joint-success "
            "(never deplete + full lifestyle + hit gift goal). Not tax advice \u2014 cross-border Roth treatment "
            "is genuinely uncertain and warrants a US-expat tax specialist before acting."
        )

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 14. SENSITIVITY DECOMPOSITION (FACTOR SWING)
# -----------------------------------------------------------------------------
elif selection == "14. Variance Decomposition (Sobol)":
    st.header("14. Sensitivity Decomposition (Factor Swing on Terminal Wealth)")
    st.markdown(
        "How much does each structural assumption move your **terminal real wealth**? For each "
        "factor, the model sweeps it across a plausible range while holding the others at their "
        "median, and reports the resulting swing in age-100 wealth (2026 dollars). This is the "
        "robust, interpretable cousin of a formal variance decomposition: it ranks the factors "
        "by how much they actually move your outcome, without the estimator noise that a Sobol "
        "decomposition suffers when returns compound so multiplicatively over 60+ years that "
        "almost all variance becomes interaction variance."
    )
    st.info(
        "Each point is one deterministic 64-year simulation with the swept factor fixed at a "
        "quantile of its range and all others at median \u2014 so this isolates structural sensitivity, "
        "not Monte Carlo noise. The full Monte Carlo (Page 12) still captures year-by-year sequence "
        "risk and the joint interactions; this view is about *which lever matters most*."
    )

    sweep_pts = st.number_input("Points per factor sweep", value=7, min_value=3, max_value=15, step=2)

    if st.button("Run Sensitivity Decomposition"):
        years = list(range(2026, 2090)); nN = len(years)
        start = st.session_state.current_age
        common = sorted(set(SP500_BY_YEAR) & set(MSCI_EUR_TOTAL_RETURNS))
        uh = np.array([SP500_BY_YEAR[y] for y in common]) / 100.0
        eh = np.array([MSCI_EUR_TOTAL_RETURNS[y] for y in common]) / 100.0
        usd_mu = st.session_state.usd_market_return/100.0; usd_sd = uh.std()
        eur_mu = st.session_state.eur_market_return/100.0; eur_sd = eh.std()
        bond_mu = st.session_state.bond_mean/100.0
        SM, SF = SURV_MALE, SURV_FEMALE; woff = st.session_state.mc_wife_age_offset

        FAC = ["Equity Returns", "Inflation", "FX Rate", "Longevity", "LTC Shock", "Tax Regime"]
        k = len(FAC)

        def death_from_u(u, table, cur):
            cum = 1.0; target = 1 - u
            for a in range(cur, max(table)+1):
                cum *= table.get(a, 1.0 if a < _MIN_LIFE_AGE else 0.0)
                if cum <= target: return a
            return max(table)

        def evaluate(row):
            u_eq, u_inf, u_fx, u_lon, u_ltc, u_tax = row
            z_eq = _norm_ppf(min(max(u_eq, 1e-4), 1 - 1e-4))
            # Sustained 64-year AVERAGE return disperses far less than a single year. Map the
            # quantile to roughly +/-3% around the mean (a wide but plausible realized-average
            # band) so the dollar swing is meaningful, not an absurd single-year extrapolation.
            eq_shift = np.clip(z_eq, -2.5, 2.5) * 0.012
            sc = {'returns': {y: (usd_mu+eq_shift, eur_mu+eq_shift*(eur_sd/usd_sd)) for y in years},
                  'bond': {y: bond_mu for y in years}}
            infl = 0.01 + 0.05 * u_inf
            sc['inflation'] = {y: infl for y in years}
            sc['fx'] = {y: st.session_state.fx_rate * (0.85 + 0.40 * u_fx) for y in years}
            d_self = death_from_u(u_lon, SM, start); d_sp = death_from_u(u_lon, SF, start - woff)
            sy = 2026 + (d_self - start); py = 2026 + (d_sp - (start - woff))
            sc['death_year'] = min(2089, max(sy, py)); sc['_first_death_yr'] = min(sy, py)
            if u_ltc < st.session_state.mc_ltc_prob:
                onset = 2026 + (82 - start); ltc = {}
                for j in range(int(st.session_state.mc_ltc_years)):
                    if onset+j <= 2089: ltc[onset+j] = st.session_state.mc_ltc_cost
                sc['ltc_cost'] = ltc
            sc['tax_mult'] = 0.8 + 0.5 * u_tax
            db, _, _, _, _ = run_core_simulation(scenario=sc)
            tot = db.loc['Total Portfolio Balance']
            return tot[2089] / ((1+infl)**(2089-2026))

        P = int(sweep_pts); qs = np.linspace(0.05, 0.95, P)
        med = [0.5]*k
        base_wealth = evaluate(med)
        prog = st.progress(0.0, text="Sweeping factors...")
        swings = []; curves = {}
        for j in range(k):
            vals = []
            for q in qs:
                row = med.copy(); row[j] = q
                vals.append(evaluate(row))
            vals = np.array(vals)
            curves[FAC[j]] = (qs.copy(), vals.copy())
            swings.append((FAC[j], vals.max() - vals.min(), vals.min(), vals.max()))
            prog.progress((j+1)/k, text=f"{FAC[j]} done")
        prog.progress(1.0, text="Complete.")

        swings.sort(key=lambda r: r[1], reverse=True)
        labels = [s[0] for s in swings]; mags = [s[1]/1e6 for s in swings]
        total = sum(mags) or 1.0
        fig = go.Figure(go.Bar(
            y=labels, x=mags, orientation='h',
            marker_color='#2166ac',
            text=[f"${m:,.1f}M  ({m/total:.0%})" for m in mags], textposition='outside'
        ))
        fig.update_layout(
            title="Terminal Real Wealth Swing by Factor (range sweep, others at median)",
            xaxis_title="Swing in age-100 real wealth ($M, 2026 $)",
            height=400, yaxis=dict(autorange='reversed'), margin=dict(l=10, r=80, t=50, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        df_sw = pd.DataFrame({
            "Factor": [s[0] for s in swings],
            "Low end": [f"${s[2]/1e6:,.1f}M" for s in swings],
            "High end": [f"${s[3]/1e6:,.1f}M" for s in swings],
            "Swing": [f"${s[1]/1e6:,.1f}M" for s in swings],
            "Share of total swing": [f"{(s[1]/1e6)/total:.0%}" for s in swings],
        }).set_index("Factor")
        st.dataframe(df_sw, use_container_width=True)

        top = swings[0]
        st.metric("Median-case terminal real wealth", f"${base_wealth/1e6:,.2f}M")
        st.success(
            f"**{top[0]}** is the dominant lever \u2014 sweeping it across its plausible range moves your "
            f"age-100 real wealth by **${top[1]/1e6:,.1f}M** ({(top[1]/1e6)/total:.0%} of the total factor "
            f"swing), from ${top[2]/1e6:,.1f}M to ${top[3]/1e6:,.1f}M. Concentrate planning attention and "
            f"hedges on the highest-swing factors; the bottom of the list barely moves your outcome and "
            f"isn't worth optimizing."
        )

        # Detail: show the response curve for the top factor.
        tq, tv = curves[swings[0][0]]
        figc = go.Figure(go.Scatter(x=tq, y=tv/1e6, mode='lines+markers', line=dict(color='#b2182b', width=3)))
        figc.update_layout(
            title=f"Response curve: {swings[0][0]} (others at median)",
            xaxis_title="Factor quantile (low \u2192 high)", yaxis_title="Terminal real wealth ($M)",
            height=320, margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(figc, use_container_width=True)
        st.caption(
            "Factor ranges: equity \u00b1~3% on the sustained average annual return; inflation 1-6%; FX 0.85-1.25x base; "
            "tax 0.8-1.3x; longevity via SSA survival tables; LTC at your stated probability/cost. This is a "
            "one-at-a-time structural sensitivity (others held at median), so it ranks lever importance but "
            "does not itself quantify interactions \u2014 the Page 12 interaction matrix covers those. Not advice."
        )
# -----------------------------------------------------------------------------
# 15. HISTORICAL COHORT BACKTEST
# -----------------------------------------------------------------------------
elif selection == "15. Historical Cohort Backtest":
    st.header("15. Historical Cohort Backtest")
    st.markdown(
        "The ultimate validation: would this exact plan have **survived the real past?** "
        "Instead of resampling or simulating, this feeds the model the *actual* sequence of "
        "S&P 500 returns and US inflation a retiree would have faced starting in each year "
        "from 1928 onward, and checks whether the plan held up. The cohorts that retired into "
        "**1966, 1973, and 2000** are the ones that broke many supposedly-safe plans \u2014 not "
        "because of a single crash, but because a weak first decade plus high inflation "
        "drained the portfolio before markets recovered. If your plan survives those, it is "
        "robust in a way no single Monte Carlo number can show."
    )
    st.info(
        "Each cohort uses real history for BOTH equity returns and inflation. Because "
        "independent European return data only exists from 2000, deep-history cohorts apply "
        "the US equity sequence to both sleeves (a documented approximation \u2014 the point is "
        "the sequence-and-inflation stress, which is US-data-rich back to 1928). Your strategy, "
        "guardrails, taxes, SS, and spending are exactly as configured elsewhere; only the "
        "market/inflation path is replaced with history."
    )

    bt_horizon = st.number_input("Planning horizon to test (years from retirement)", value=35, min_value=20, max_value=50, step=1,
                                 help="A cohort 'survives' if the portfolio stays solvent this many years past retirement. 35 years is a common robustness bar for an early retiree.")
    apply_real_eur = st.checkbox("Use real European data for 2000+ cohorts (paired)", value=True,
                                 help="For cohorts starting 2000 or later, use the actual MSCI Europe EUR series for the EUR sleeve instead of mirroring US returns.")
    recenter = st.checkbox("Recenter returns to my assumed mean (isolate sequence risk)", value=True,
                           help="History compounded at ~10-12%/yr nominal, well above your ~7% forward assumption, so a RAW backtest flatters every cohort and lets the 1929 cohort balloon to absurd terminal wealth. Recentering shifts each cohort's average return to YOUR assumption while preserving the historical SEQUENCE, volatility, and crash clustering -- so the test isolates 'would this sequence-and-inflation pattern have worked at my return level' (the question that matters). Uncheck to see raw historical levels.")

    if st.button("Run Historical Backtest"):
        years_model = list(range(2026, 2090))
        n_model = len(years_model)
        start_age = st.session_state.current_age
        ret_age = st.session_state.ret_age
        ret_offset = ret_age - start_age  # model years from 2026 to retirement
        H = int(bt_horizon)

        # Real return + inflation history.
        hist_years = sorted(US_CPI_BY_YEAR.keys() & SP500_BY_YEAR.keys())
        first_hist, last_hist = min(hist_years), max(hist_years)
        # A cohort needs returns for the full model horizon from RETIREMENT onward up to H years,
        # but the model also simulates the pre-retirement accumulation. We map historical year
        # H0 to the RETIREMENT year, and walk forward; pre-retirement years borrow the run-up
        # history before H0 where available, else repeat the earliest available year.
        # Cohort is viable if we have H years of history at/after the retirement-mapped year.
        cohort_starts = [y for y in hist_years if y + H <= last_hist + 1]

        if not cohort_starts:
            st.error("Not enough history for that horizon. Lower the horizon.")
        else:
            usd_assume = st.session_state.usd_market_return / 100.0
            eur_assume = st.session_state.eur_market_return / 100.0
            def hist_path(h0):
                # Build per-model-year returns & inflation. Model year 2026 = (h0 - ret_offset).
                # Retirement model-year (2026+ret_offset) maps to historical year h0.
                ret_model_yr = 2026 + ret_offset
                raw_us = {}; raw_eu = {}; raw_inf = {}
                for my in years_model:
                    hy = h0 + (my - ret_model_yr)  # historical year aligned so retirement=h0
                    hy_clamped = min(max(hy, first_hist), last_hist)
                    raw_us[my] = SP500_BY_YEAR[hy_clamped] / 100.0
                    if apply_real_eur and hy_clamped in MSCI_EUR_TOTAL_RETURNS:
                        raw_eu[my] = MSCI_EUR_TOTAL_RETURNS[hy_clamped] / 100.0
                    else:
                        raw_eu[my] = raw_us[my]  # approximation for deep-history cohorts
                    raw_inf[my] = US_CPI_BY_YEAR[hy_clamped] / 100.0
                # Recenter (optional): shift each sleeve so its mean over the span equals the
                # user's assumed return, preserving every deviation so the SEQUENCE, volatility,
                # and crash clustering stay intact. Inflation is NEVER recentered -- feeding the
                # real historical CPI path is the whole point of the backtest.
                us_shift = (usd_assume - np.mean(list(raw_us.values()))) if recenter else 0.0
                eu_shift = (eur_assume - np.mean(list(raw_eu.values()))) if recenter else 0.0
                returns = {my: (raw_us[my] + us_shift, raw_eu[my] + eu_shift) for my in years_model}
                return returns, raw_inf, ret_model_yr

            results = []
            prog = st.progress(0.0, text="Backtesting cohorts...")
            for k, h0 in enumerate(cohort_starts):
                returns, inflation, ret_model_yr = hist_path(h0)
                sc = {'returns': returns, 'inflation': inflation}
                db, dd, _, _, _ = run_core_simulation(scenario=sc)
                tot = db.loc['Total Portfolio Balance']
                # Survival horizon: H years past retirement.
                horizon_yr = min(2089, ret_model_yr + H)
                window = [y for y in years_model if ret_model_yr <= y <= horizon_yr]
                depleted = tot[(tot.index >= ret_model_yr) & (tot.index <= horizon_yr) & (tot <= 0)]
                survived = len(depleted) == 0
                fail_yr_hist = (h0 + (depleted.index.min() - ret_model_yr)) if not survived else None
                # Lowest real funded ratio across retirement window (achieved/target).
                cpi = 1.0; cum = {}
                for my in years_model:
                    if my > 2026: cpi *= (1 + inflation[my])
                    cum[my] = cpi
                life = dd.loc["Actual Lifestyle Spend"]
                def tgt_real(my):
                    a = start_age + (my - 2026)
                    return st.session_state.spend_golden if a < 70 else (st.session_state.spend_middle if a < 85 else st.session_state.spend_wind)
                ratios = []
                for my in window:
                    t = tgt_real(my)
                    if t > 0:
                        ratios.append((life.get(my, 0)/cum[my]) / t)
                min_funded = min(ratios) if ratios else 1.0
                avg_funded = float(np.mean(ratios)) if ratios else 1.0
                term_real = tot[horizon_yr] / cum[horizon_yr] if horizon_yr in tot.index else np.nan
                results.append({
                    'cohort': h0, 'survived': survived, 'fail_year': fail_yr_hist,
                    'min_funded': min_funded, 'avg_funded': avg_funded, 'terminal_real': term_real
                })
                prog.progress((k+1)/len(cohort_starts), text=f"Cohort {h0} done")
            prog.progress(1.0, text="Complete.")

            df_bt = pd.DataFrame(results)
            surv_rate = 100.0 * df_bt['survived'].mean()
            n_cohorts = len(df_bt)
            n_fail = int((~df_bt['survived']).sum())

            c1, c2, c3 = st.columns(3)
            c1.metric("Historical Survival Rate", f"{surv_rate:.0f}%", help=f"Share of {n_cohorts} starting years (1928-{cohort_starts[-1]}) whose plan stayed solvent for {H} years.")
            c2.metric("Cohorts Tested", f"{n_cohorts}")
            c3.metric("Cohorts That Failed", f"{n_fail}")

            # Survival/terminal-wealth bar by cohort.
            fig_bt = go.Figure()
            colors = ['#2ca02c' if s else '#d62728' for s in df_bt['survived']]
            fig_bt.add_trace(go.Bar(
                x=df_bt['cohort'], y=df_bt['min_funded']*100, marker_color=colors,
                hovertemplate="Cohort %{x}: lowest funded %{y:.0f}% of target<extra></extra>",
                name="Lowest funded ratio"
            ))
            fig_bt.add_hline(y=100, line_dash="dot", line_color="grey", annotation_text="100% of target")
            fig_bt.update_layout(
                title=f"Worst Real-Spending Year by Retirement Cohort (green=survived {H}y, red=depleted)",
                xaxis_title="Retirement Start Year (historical)",
                yaxis_title="Lowest funded ratio in retirement (%)", height=400
            )
            st.plotly_chart(fig_bt, use_container_width=True)

            # Spotlight the famous killer cohorts.
            st.subheader("The Cohorts That Break Plans")
            spotlight = [1966, 1973, 2000, 1929]
            rows = []
            for sy in spotlight:
                r = df_bt[df_bt['cohort'] == sy]
                if not r.empty:
                    r = r.iloc[0]
                    rows.append({
                        "Cohort": sy,
                        "Survived": "✅ Yes" if r['survived'] else "❌ No",
                        "Failed In": "—" if r['survived'] else f"{int(r['fail_year'])}",
                        "Lowest Funded": f"{r['min_funded']*100:.0f}%",
                        "Avg Funded": f"{r['avg_funded']*100:.0f}%",
                        "Terminal Real": f"${r['terminal_real']/1e6:.1f}M" if pd.notna(r['terminal_real']) else "n/a"
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Cohort"), use_container_width=True)

            # Worst 5 cohorts overall.
            worst = df_bt.sort_values('min_funded').head(5)
            st.subheader("5 Worst Cohorts in History")
            wrows = [{
                "Cohort": int(r['cohort']),
                "Survived": "✅" if r['survived'] else "❌",
                "Lowest Funded": f"{r['min_funded']*100:.0f}%",
                "Avg Funded": f"{r['avg_funded']*100:.0f}%",
                "Terminal Real": f"${r['terminal_real']/1e6:.1f}M" if pd.notna(r['terminal_real']) else "n/a"
            } for _, r in worst.iterrows()]
            st.dataframe(pd.DataFrame(wrows).set_index("Cohort"), use_container_width=True)

            # Verdict.
            killer_survived = df_bt[df_bt['cohort'].isin([1966,1973,2000])]['survived']
            if surv_rate >= 95 and killer_survived.all():
                verdict = ("**Robust.** The plan survives essentially all historical cohorts, including "
                           "the notorious 1966/1973/2000 sequences that break naive plans. This is strong, "
                           "real-world validation that your guardrails and spending plan handle sequence-and-"
                           "inflation risk, not just average returns.")
            elif surv_rate >= 85:
                verdict = (f"**Mostly robust.** {surv_rate:.0f}% of cohorts survived. Inspect the failures "
                           "above \u2014 if they cluster in the high-inflation 1960s-70s starts, your plan's "
                           "weak point is inflation eroding real spending, and a more inflation-protected "
                           "allocation or a lower initial withdrawal would close the gap.")
            else:
                verdict = (f"**Fragile to history.** Only {surv_rate:.0f}% of cohorts survived. The plan as "
                           "configured would have failed in a meaningful share of real historical sequences. "
                           "The Monte Carlo success rate is more optimistic than history justifies \u2014 worth "
                           "lowering spending, tightening guardrails, or de-risking the early-retirement years.")
            st.markdown(verdict)
            st.caption(
                "Backtest feeds real S&P 500 returns and real US CPI inflation per cohort; your guardrails, "
                "taxes, SS, gifting, and spending are unchanged. Caveat: only US equity history reaches back "
                "to 1928, so deep-history cohorts approximate the EUR sleeve with US returns; the cross-border "
                "tax and FX specifics of the actual plan are not what 1928-1990 retirees faced. This validates "
                "SEQUENCE and INFLATION robustness, the dimensions history is richest on. Not a guarantee \u2014 "
                "the future can be worse than any realized past, which is why the crisis-overlay Monte Carlo "
                "and this backtest are complements, not substitutes."
            )