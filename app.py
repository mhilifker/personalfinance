import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
if 'target_early_draw' not in st.session_state: st.session_state.target_early_draw = 144000
if 'target_bequest' not in st.session_state: st.session_state.target_bequest = 7500000
if 'gift_start_age' not in st.session_state: st.session_state.gift_start_age = 58
if 'gift_end_age' not in st.session_state: st.session_state.gift_end_age = 83

# Tax Assumptions
if 'tax_roth' not in st.session_state: st.session_state.tax_roth = 25.0
if 'tax_pretax_base' not in st.session_state: st.session_state.tax_pretax_base = 16.0
if 'tax_pretax_excess' not in st.session_state: st.session_state.tax_pretax_excess = 25.0
if 'tax_cap_gains' not in st.session_state: st.session_state.tax_cap_gains = 15.0
if 'us_ss_tax_rate' not in st.session_state: st.session_state.us_ss_tax_rate = 12.0

# Real Estate Assumptions 
if 'home_price' not in st.session_state: st.session_state.home_price = 1200000
if 'down_payment' not in st.session_state: st.session_state.down_payment = 150000
if 'mtg_rate' not in st.session_state: st.session_state.mtg_rate = 6.5
if 'tax_rate' not in st.session_state: st.session_state.tax_rate = 2.1 
if 'ann_insurance' not in st.session_state: st.session_state.ann_insurance = 3000
if 'pmi_rate' not in st.session_state: st.session_state.pmi_rate = 0.5 
if 'ann_apprec' not in st.session_state: st.session_state.ann_apprec = 2.0

# Decoupled SS Claim Ages
if 'mike_ss_age' not in st.session_state: st.session_state.mike_ss_age = 70
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
if 'floor_golden' not in st.session_state: st.session_state.floor_golden = 75000
if 'floor_middle' not in st.session_state: st.session_state.floor_middle = 75000
if 'floor_wind' not in st.session_state: st.session_state.floor_wind = 85000
if 'slash_trigger' not in st.session_state: st.session_state.slash_trigger = 6.0
if 'recovery_trigger' not in st.session_state: st.session_state.recovery_trigger = 4.5
if 'raise_pct' not in st.session_state: st.session_state.raise_pct = 10.0
if 'dynamic_gift_pct' not in st.session_state: st.session_state.dynamic_gift_pct = 50.0

# Institutional Stress Test Macros
if 'sorr_enable' not in st.session_state: st.session_state.sorr_enable = False
if 'sorr_start_yr' not in st.session_state: st.session_state.sorr_start_yr = 2044
if 'sorr_duration' not in st.session_state: st.session_state.sorr_duration = 3
if 'sorr_return' not in st.session_state: st.session_state.sorr_return = -15.0
if 'fx_enable' not in st.session_state: st.session_state.fx_enable = False
if 'fx_rate' not in st.session_state: st.session_state.fx_rate = 1.15

# Bifurcated Glide Path
if 'glide_enable' not in st.session_state: st.session_state.glide_enable = False
if 'glide_start_age' not in st.session_state: st.session_state.glide_start_age = 65
if 'glide_end_age' not in st.session_state: st.session_state.glide_end_age = 85
if 'usd_glide_reduction' not in st.session_state: st.session_state.usd_glide_reduction = 0.15
if 'eur_glide_reduction' not in st.session_state: st.session_state.eur_glide_reduction = 0.05

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
        "Annual Savings Escalator (%)": [0.0, 3.0, 3.0, 0.0, 3.0, 3.0, 0.0, 0.0, 3.0, 0.0],
        "Current State": [0, 30000, 20000, 0, 15000, 12000, 0, 0, 8300, 0],
        "Northbrook Grind": [0, 15000, 23500, 0, 0, 12000, 0, 0, 0, 0]
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
    bp_growth_years = max(0, age_62_year - 2026)
    bp_multiplier = (1 + (awi / 100)) ** bp_growth_years
    bp1, bp2 = 1226 * bp_multiplier, 7395 * bp_multiplier
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

def run_core_simulation(override_m_age=None, override_s_age=None, override_early_draw=None):
    MIKE_SS, STEPH_SS = get_ss_timelines(override_m_age, override_s_age)
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    move_yr = 2026 + (st.session_state.move_age - st.session_state.current_age)
    
    policy = st.session_state.policy_df.set_index("Asset Category")
    current_balances = st.session_state.asset_balances.copy()
    current_basis = st.session_state.asset_balances.copy() 
    
    rmd_divisors = {75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4}
    
    r_discount = st.session_state.usd_market_return / 100.0 
    n_years_giving = st.session_state.gift_end_age - st.session_state.gift_start_age + 1
    years_to_100 = 100 - st.session_state.gift_start_age
    
    if r_discount > 0 and n_years_giving > 0:
        pv_at_start = st.session_state.target_bequest / ((1 + r_discount) ** years_to_100)
        annual_gift = (pv_at_start * r_discount) / (1 - (1 + r_discount) ** -n_years_giving)
    else: annual_gift = 0
    
    bal_matrix, draw_matrix, tax_matrix = {}, {}, {}
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
        
        if st.session_state.glide_enable and age >= st.session_state.glide_start_age:
            years_in_glide = min(age, st.session_state.glide_end_age) - st.session_state.glide_start_age + 1
            usd_yr_return -= (years_in_glide * (st.session_state.usd_glide_reduction / 100.0))
            eur_yr_return -= (years_in_glide * (st.session_state.eur_glide_reduction / 100.0))
            
        if st.session_state.sorr_enable and (st.session_state.sorr_start_yr <= yr < (st.session_state.sorr_start_yr + st.session_state.sorr_duration)):
            usd_yr_return = st.session_state.sorr_return / 100.0
            eur_yr_return = st.session_state.sorr_return / 100.0

        if yr < start_yr:
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
                
                current_balances[asset] = current_balances[asset] * (1 + asset_ret) + cont
                current_basis[asset] += cont 
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
        taxable_ss_usd = gross_ss_usd * 0.85 if gross_ss_usd > 0 else 0.0
        irs_shadow_tax_usd = taxable_ss_usd * (st.session_state.us_ss_tax_rate / 100.0)
        net_ss_usd = gross_ss_usd - irs_shadow_tax_usd
        
        # 2. Dynamic Gifting Math (Smoothed Recalibrating Annuity)
        base_gift_usd = 0
        if st.session_state.gift_start_age <= age <= st.session_state.gift_end_age:
            n_total = 100 - age
            approx_annual_draw = max(0, target_lifestyle_usd - net_ss_usd)
            
            if usd_yr_return == i_rate:
                fv_draws = approx_annual_draw * n_total * (1+usd_yr_return)**(n_total - 1)
            else:
                fv_draws = approx_annual_draw * (((1+usd_yr_return)**n_total - (1+i_rate)**n_total) / (usd_yr_return - i_rate))
                
            # Add back the FV of past gifts to find the TRUE "No-Gift" Terminal Pie
            fv_past_gifts = cumulative_gifts_tracker * (1 + usd_yr_return)**n_total
            total_fv_nogift = max(0, (current_portfolio * (1+usd_yr_return)**n_total) - fv_draws + fv_past_gifts)
            
            target_total_gift_fv = (st.session_state.dynamic_gift_pct / 100.0) * total_fv_nogift
            remaining_gift_fv_needed = max(0, target_total_gift_fv - fv_past_gifts)
            
            n_rem_gifts = st.session_state.gift_end_age - age + 1
            if n_rem_gifts > 0 and usd_yr_return > 0:
                fvifa = (((1+usd_yr_return)**n_rem_gifts) - 1) / usd_yr_return
                growth_after_gifts = (1+usd_yr_return)**(100 - st.session_state.gift_end_age)
                base_gift_usd = remaining_gift_fv_needed / (fvifa * growth_after_gifts)
                
        # 3. Guardrails Logic
        if st.session_state.guardrails_enable and current_portfolio > 0:
            eval_draw = (target_lifestyle_usd + base_gift_usd) * spend_level - net_ss_usd
            eval_wr = max(0, eval_draw) / current_portfolio
            
            if eval_wr > (st.session_state.slash_trigger / 100.0):
                floor_level = floor_usd_inflated / target_lifestyle_usd
                spend_level = floor_level
            elif eval_wr < (st.session_state.recovery_trigger / 100.0) and spend_level < 1.0:
                spend_level = min(1.0, spend_level * (1 + (st.session_state.raise_pct / 100.0)))
        else:
            spend_level = 1.0

        # 4. Finalize Actual Targets
        actual_lifestyle_usd = target_lifestyle_usd * spend_level
        actual_gift_usd = base_gift_usd * spend_level
        
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
                    
            for brok in ["Cash (Slush Fund)", "HSA Pool", "E*TRADE (Legacy)", "Crypto (Coinbase)"]:
                remaining_eur_need -= pull_net_need(brok, remaining_eur_need, 0.0, False, draws, taxes, is_slovenia)
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
        d_col["Actual Lifestyle Spend"] = actual_lifestyle_usd if is_slovenia else target_lifestyle_eur 
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

    return pd.DataFrame(bal_matrix), pd.DataFrame(draw_matrix), pd.DataFrame(tax_matrix)

# -----------------------------------------------------------------------------
# PAGE ROUTING
# -----------------------------------------------------------------------------
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Navigate", ["1. Executive Dashboard", "2. Pre-Set Asset Ledger & Tax Lots", "3. Investment Policy Editor", "4. Real Estate & Relocation", "5. The Great Reset Simulator", "6. Social Security & Pensions", "7. Cash Flow & Slovenian Drip", "8. Yearly Balances (2026-2089)", "9. Tax Torpedo Optimizer", "10. Institutional Stress Testing", "11. Longevity Optimizer (Guardrails)"])

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

    df_bal, df_draw, _ = run_core_simulation()
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    
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
    
    fig_gauge.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader(f"Asset & Tax Lot Balances ({start_yr}-2089)")
    
    milestone_years = [yr for yr in range(start_yr, 2090, 5)]
    if 2089 not in milestone_years: milestone_years.append(2089)
    
    milestone_data = {}
    inf_rate = st.session_state.inflation_rate / 100.0
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
    
    real_bals = df_bal.loc['Total Portfolio Balance'].copy()
    for yr in real_bals.index:
        real_bals[yr] = real_bals[yr] / ((1 + inf_rate) ** (yr - 2026))

    chart_bals = df_bal.drop("Total Portfolio Balance").T
    if start_yr in chart_bals.index:
        chart_bals = chart_bals.loc[start_yr:]
        real_bals = real_bals.loc[start_yr:]
        
    fig1 = go.Figure()
    for col in chart_bals.columns:
        real_asset_bals = chart_bals[col].copy()
        for yr in real_asset_bals.index:
            real_asset_bals[yr] = real_asset_bals[yr] / ((1 + inf_rate) ** (yr - 2026))
            
        fig1.add_trace(go.Bar(
            x=chart_bals.index, 
            y=chart_bals[col], 
            name=col, 
            yaxis='y1',
            customdata=real_asset_bals.values,
            hovertemplate="<b>%{x}</b><br>Nominal: $%{y:,.0f}<br>Real (2026 $): $%{customdata:,.0f}<extra></extra>"
        ))
        
    fig1.add_trace(go.Scatter(
        x=real_bals.index, y=real_bals.values, name="Real Portfolio Value (2026 $)",
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
    st.subheader("Yearly Income Sources (Nominal $)")
    if start_yr in df_draw.columns:
        chart_draws = df_draw.loc[:, start_yr:].T
        chart_draws['Brokerage & Cash Draw'] = chart_draws['E*TRADE (Legacy)'] + chart_draws['IBKR (Active)'] + chart_draws['Crypto (Coinbase)'] + chart_draws['Cash (Slush Fund)'] + chart_draws['HSA Pool']
        chart_draws['Pre-Tax Draw'] = chart_draws['Cornerstone: Trad 401(k)'] + chart_draws['Cornerstone: Profit Sharing'] + chart_draws['OCC: Trad 401(k)']
        chart_draws['Social Security'] = chart_draws["Michael's SS"] + chart_draws["Stephanie's SS"]
        
        fig2 = px.bar(chart_draws[['Brokerage & Cash Draw', 'Pre-Tax Draw', 'Social Security']], barmode='stack')
        fig2.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""), xaxis_title="", yaxis_title="Income / Draw ($)")
        st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. PRE-SET ASSET LEDGER & TAX LOTS
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
    c1, c2 = st.columns(2)
    c1.success(f"**Michael**\n\n${MIKE_SS[m_claim_yr]:,.0f} / yr (Starts {m_claim_yr})")
    c2.success(f"**Stephanie**\n\n${STEPH_SS[s_claim_yr]:,.0f} / yr (Starts {s_claim_yr})")

# -----------------------------------------------------------------------------
# 7. CASH FLOW & SLOVENIAN DRIP
# -----------------------------------------------------------------------------
elif selection == "7. Cash Flow & Slovenian Drip":
    st.header("7. Cash Flow & Multi-Period Optimization Engine")
    _, df_draw, df_tax = run_core_simulation()
    start_yr = 2026 + (st.session_state.ret_age - st.session_state.current_age)
    
    st.markdown("---")
    st.subheader("1a. Yearly Future Projected Draw by Asset Ledger (Nominal $)")
    st.dataframe(df_draw.style.format("${:,.0f}"), use_container_width=True, height=600)
    
    st.markdown("---")
    st.subheader("1b. Yearly Future Projected Draw by Asset Ledger (Real 2026 $)")
    df_draw_real = df_draw.copy()
    inf_rate = st.session_state.inflation_rate / 100.0
    for yr in df_draw_real.columns:
        if yr in df_draw_real.columns and not isinstance(df_draw_real[yr], str):
            df_draw_real[yr] = df_draw_real[yr] / ((1 + inf_rate) ** (yr - 2026))
    st.dataframe(df_draw_real.style.format("${:,.0f}"), use_container_width=True, height=600)
    
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
        gift_nominal = df_draw.loc["Actual Generational Drip"]
        gift_real = df_draw_real.loc["Actual Generational Drip"]
        
        df_gift_summary = pd.DataFrame({
            "Nominal Annual Gift": gift_nominal,
            "Real Annual Gift (2026 $)": gift_real,
            "Cumulative Nominal Gift": gift_nominal.cumsum(),
            "Cumulative Real Gift": gift_real.cumsum()
        })
        
        df_gift_active = df_gift_summary[df_gift_summary["Nominal Annual Gift"] > 0]
        
        if not df_gift_active.empty:
            c1, c2 = st.columns(2)
            c1.metric("Total Lifetime Gift (Nominal)", f"${df_gift_active['Cumulative Nominal Gift'].iloc[-1]:,.0f}")
            c2.metric("Total Lifetime Gift (Real 2026 $)", f"${df_gift_active['Cumulative Real Gift'].iloc[-1]:,.0f}")
            
            fig_gift = px.bar(df_gift_active, y=["Nominal Annual Gift", "Real Annual Gift (2026 $)"], barmode='group')
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
    df_bal, _, _ = run_core_simulation()
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
            draw_amounts = [0, 25000, 50000, 75000, 100000, 125000, 150000]
            
            for ss in ss_ages:
                for draw in draw_amounts:
                    _, df_draw, _ = run_core_simulation(override_m_age=ss, override_s_age=ss, override_early_draw=draw)
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
            df_bal, _, _ = run_core_simulation()
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
