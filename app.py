import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors # Import for potential future use or consistency
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
import os # For checking if openpyxl is available

# --- Risk Questionnaire Definitions ---
questions = {
    1: {"question": "How old are you?", "options": ["Over 60", "45-60", "30-44", "Under 30"], "scores": [1, 2, 3, 4]},
    2: {"question": "What is your investment experience?", "options": ["I don’t have any experience", "I have some experience", "I have a strong educational background in a related field", "I’m an experienced investor"], "scores": [1, 2, 3, 4]},
    3: {"question": "What is an ETF?", "options": ["I don’t know", "A diversified investment fund that only trades commodities", "A diversified, index-tracking investment fund that does not trade on exchanges", "A diversified, index-tracking investment fund that trades on exchanges"], "scores": [1, 2, 3, 4]},
    4: {"question": "Main goal of your investment", "options": ["Capital preservation", "Conservative investment", "General investment", "Capital growth"], "scores": [1, 2, 3, 4]},
    5: {"question": "What is your investment horizon?", "options": ["<5 years", "5-10 years", "10-15 years", ">15 years"], "scores": [1, 2, 3, 4]},
    6: {"question": "Do you prefer guaranteed small gains or potential big gains with risk?", "options": ["Guarantees only", "Smaller gains and contained risk", "Moderate gain and moderate risk", "Big gains with high risk"], "scores": [1, 2, 3, 4]},
    7: {"question": "What is your tolerance of market swings?", "options": ["Low", "Medium-low", "Medium-high", "High"], "scores": [1, 2, 3, 4]},
    8: {"question": "Do you prefer a strategy that:", "options": ["It is able to provide reassurance during high volatile market periods", "It is aligned with Stock market Performance", "It is aligned with Bond market Performance", "Tries to beat the market"], "scores": [1, 2, 3, 4]},
    9: {"question": "What’s the worst-case decline you’re comfortable seeing in 1 year?", "options": ["Less than 10%", "10-20%", "20-30%", "More than 30%"], "scores": [1, 2, 3, 4]},
    10: {"question": "What would you do if you hear the market is down 20%?", "options": ["I sell a majority of my financial assets", "I sell a minority of my financial assets", "I maintain my position", "I buy more"], "scores": [1, 2, 3, 4]},
    11: {"question": "Do you have any preference for ESG (environmental, social, governance) investments?", "options": ["Yes, I want a portfolio with sustainable investments", "No, I don’t take the sustainable factor into consideration"], "scores": [4, 1]},
    12: {"question": "Do you have any preference for the investment strategy of your Roboadvisor?", "options": ["Yes, I want an active strategy", "No, I want a passive strategy"], "scores": [4, 1]}
}

# --- Risk Level Recommendations ---
risk_level_recommendations = {
    "Ultra Conservative": {
        "title": "Your Ultra-Conservative Portfolio",
        "text": "This portfolio prioritizes capital preservation above all else. It's designed for investors who are highly risk-averse and seek minimal exposure to market volatility. Expect modest returns, but with strong protection against significant downturns. Consider this if capital security is your top priority."
    },
    "Conservative": {
        "title": "Your Conservative Portfolio",
        "text": "This portfolio focuses on capital protection while aiming for stable, consistent returns. It's suitable if you have a low tolerance for market fluctuations and prefer slow, steady growth over aggressive gains. Ideal for those who value stability and predictable income."
    },
    "Cautiously Moderate": {
        "title": "Your Cautiously Moderate Portfolio",
        "text": "This portfolio seeks a balance between capital preservation and moderate growth. You're willing to take on a small amount of risk to potentially outperform traditional fixed-income investments, but significant market swings are still a concern. It's a prudent choice for measured growth."
    },
    "Moderate": {
        "title": "Your Moderate Portfolio",
        "text": "This portfolio is built for balanced growth with an acceptable level of risk. You are comfortable with some market fluctuations, understanding they are part of achieving long-term capital appreciation. This strategy aims to provide a healthy mix of stability and growth potential."
    },
    "Moderate Growth": {
        "title": "Your Moderate Growth Portfolio",
        "text": "This portfolio is designed for investors seeking substantial long-term capital growth and are prepared to accept a moderate to higher level of risk. Short-term market volatility is acceptable, as your focus remains on maximizing growth opportunities over time."
    },
    "Growth": {
        "title": "Your Growth Portfolio",
        "text": "This portfolio is focused on maximizing capital appreciation over the long term. You possess a higher risk tolerance and are comfortable with notable market fluctuations as a means to pursue strong returns. This strategy is for those prioritizing aggressive wealth accumulation."
    },
    "Opportunistic": {
        "title": "Your Opportunistic Portfolio",
        "text": "This portfolio actively seeks out investment opportunities with high return potential. You have a significant appetite for risk and are prepared for substantial market volatility and potential drawdowns. This strategy suits investors with a long-term horizon and a strong belief in market recovery."
    },
    "Aggressive Growth": {
        "title": "Your Aggressive Growth Portfolio",
        "text": "This represents the highest level of risk tolerance. Your primary goal is maximum capital growth, and you are comfortable with the highest possible level of market volatility and potential for large swings. This strategy is best for investors with an extremely high risk tolerance and a very long investment horizon."
    }
}


# --- Portfolio Data (for fixed allocation scenario) ---
# This data will be used if Q11 and Q12 are both "yes"
portfolio_data_fixed = {
    2: {
        'category_allocation': {'Bond': 1.00, 'Equity': 0.00, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.5 ,'AGG': 0.4 ,'BOND': 0.1} # Changed BOND to BND
    },
    3: {
        'category_allocation': {'Bond': 1.0, 'Equity': 0.0, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.5 ,'AGG': 0.25 ,'BOND': 0.25} # Changed BOND to BND
    },
    4: {
        'category_allocation': {'Bond': 0.85, 'Equity': 0.15, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.4306 ,'AGG': 0.085 ,'BOND': 0.3419, 'VTI':0.015 , 'SPLG': 0.0525, 'VOO': 0.075} # Changed BOND to BND
    },
    5: {
        'category_allocation': {'Bond': 0.75, 'Equity': 0.25, 'Real Estate': 0.00,'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.3081 ,'AGG': 0.0705 ,'BOND': 0.3719, 'VTI':0.0375 , 'SPLG':0.145, 'VOO': 0.0625} # Changed BOND to BND
    },
    6: {
        'category_allocation': {'Bond': 0.60, 'Equity': 0.40, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'AGG': 0.3085 ,'BOND': 0.3085, 'VTI':0.1415 , 'SPLG':0.1415 , 'VOO':0.2415} # Changed BOND to BND, removed SHY (as it was 0 anyway)
    },
    7: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.90, 'Real Estate': 0.10,'Crypto': 0.00},
        'specific_etf_allocation': {'VTI':0.21 , 'SPLG':0.2422 , 'VOO':0.4522, 'XLRE':0.0478 ,'SCHH':0.0478 }
    },
    8: {
        'category_allocation': {'Bond': 0.0, 'Equity': 0.7, 'Real Estate': 0.30,'Crypto': 0.00},
        'specific_etf_allocation': {'VTI': 0.2822, 'SPLG': 0.1422 , 'VOO': 0.2822, 'XLRE':0.1467 ,'SCHH':0.1467}
    },
    9: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.65, 'Real Estate': 0.3, 'Crypto': 0.05},
        'specific_etf_allocation': {'VTI': 0.195, 'SPLG':0.13 , 'VOO': 0.325, 'XLRE':0.195 ,'SCHH':0.105, 'GBTC': 0.05}
    },
}

# --- Portfolio Data (for optimization scenario, from mean_var_esg.py) ---
# This data defines the universe of assets available for optimization for each risk level
risk_level_assets_optimized = {
    2: ['SHY','AGG','BOND',],
    3: ['SHY','AGG','BOND',],
    4: ['SHY','AGG','BOND','SPLG','VOO'],
    5: ['SHY','AGG','BOND','VTI','SPLG','VOO'],
    6: ['AGG','BOND','VTI','SPLG','VOO'],
    7: ['VTI','SPLG','VOO','XLRE','SCHH'],
    8: ['VTI','SPLG','VOO','XLRE','SCHH'],
    9: ['VTI','SPLG','VOO','XLRE','SCHH','GBTC']
}

# Mapping ETFs to their categories (used in both scenarios for plotting)

etf_to_category = {
    'SHY': 'Bond', 'AGG': 'Bond', 'BOND': 'Bond',
    'VTI': 'Equity', 'VTI': 'Equity', 'VTI': 'Equity', 'VTI': 'Equity', 'VTI': 'Equity',
    'XLRE': 'Real Estate', 'SCHH': 'Real Estate', 'GBTC':'Crypto'
}


# Define all unique tickers across both fixed and optimized portfolios, plus risk-free rate
all_unique_tickers_for_download = sorted(list(set(
    [etf for data in portfolio_data_fixed.values() for etf in data['specific_etf_allocation'].keys()] +
    [etf for tickers_list in risk_level_assets_optimized.values() for etf in tickers_list] +
    ['^IRX'] # Add ^IRX for risk-free rate
)))

# --- Plotting Functions (shared) ---
def plot_pie_chart_with_details(data_dict, title, figsize=(9, 9), autopct='%1.1f%%', startangle=140):
    labels = []
    sizes = []
    for label, size in data_dict.items():
        if size > 0.001:
            labels.append(label)
            sizes.append(size)

    if not sizes:
        st.warning(f"No significant data to plot for: {title}")
        return None # Return None if no plot is generated

    fig, ax = plt.subplots(figsize=figsize)
    colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))
    wedges, texts, autotexts = ax.pie(sizes, autopct=autopct, startangle=startangle, colors=colors,
                                      wedgeprops=dict(width=0.4, edgecolor='w'))
    for autotext in autotexts:
        autotext.set_color('black')
    ax.legend(wedges, labels, title="Assets", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(title)
    ax.axis('equal')
    return fig # Return the figure object for Streamlit

# --- Functions for Portfolio Optimization ---
@st.cache_data # Cache this function to avoid re-downloading data
def download_historical_prices(tickers, start_date, end_date):
    """Downloads historical 'Adj Close' or 'Close' price data from Yahoo Finance for a given period."""
    if not tickers:
        st.error("No tickers provided for download.")
        return pd.DataFrame(), pd.DataFrame(), 0.0

    st.info(f"Downloading historical data for {len(tickers)} assets from {start_date} to {end_date}...")
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        if data.empty:
            st.error("No data downloaded. Check ticker symbols or date range.")
            return pd.DataFrame(), pd.DataFrame(), 0.0

        price_data = pd.DataFrame() # Initialize an empty DataFrame
        
        # Priority 1: Adj Close (for multiple tickers)
        if isinstance(data.columns, pd.MultiIndex) and 'Adj Close' in data.columns.levels[0]:
            price_data = data['Adj Close']
        # Priority 2: Adj Close (for single ticker as a DataFrame)
        elif 'Adj Close' in data.columns: 
            price_data = data[['Adj Close']]
        # Priority 3: Close (for multiple tickers)
        elif isinstance(data.columns, pd.MultiIndex) and 'Close' in data.columns.levels[0]: # Added this for multiple tickers
            price_data = data['Close']
        # Priority 4: Close (for single ticker as a DataFrame)
        elif 'Close' in data.columns: 
            price_data = data[['Close']]
        else:
            # Fallback for single ticker as a Series (less common, but good to handle)
            if len(tickers) == 1 and isinstance(data, pd.DataFrame) and not data.empty:
                if 'Adj Close' in data.columns:
                    price_data = data[['Adj Close']]
                elif 'Close' in data.columns:
                    price_data = data[['Close']]
                else:
                    st.error(f"Could not find 'Adj Close' or 'Close' prices for single ticker {tickers[0]}.")
                    return pd.DataFrame(), pd.DataFrame(), 0.0
            else:
                st.error(f"Could not find 'Adj Close' or 'Close' prices for selected tickers. Data columns: {data.columns}")
                return pd.DataFrame(), pd.DataFrame(), 0.0

        price_data = price_data.dropna(axis=1, how='all') # Drop columns that are all NaN
        price_data = price_data.dropna(axis=0, how='all') # Drop rows that are all NaN
        
        if price_data.empty:
            st.error("After cleaning, no valid price data remains.")
        
            return pd.DataFrame(), pd.DataFrame(), 0.0 # Changed to return three values

        # --- risk_free_rate_annual ---
        risk_free_rate_annual = 0.0
        if '^IRX' in price_data.columns: # Check if '^IRX' is in the final price_data
            rf_series = price_data['^IRX'].dropna()
            if not rf_series.empty:
                daily_risk_free_rate = rf_series.mean() / 100.0 / 252 # Convert to daily rate if ^IRX is annual in data
                risk_free_rate_annual = (1 + daily_risk_free_rate)**252 - 1
                st.info(f"Calculated Annual Risk-Free Rate: {risk_free_rate_annual*100:.2f}%")
            else:
                st.warning("No valid risk-free rate data (^IRX) for the specified period. Using 0 as risk-free rate for Sharpe calculation.")
        else:
            st.warning("'^IRX' ticker not found in downloaded data. Using 0 as risk-free rate for Sharpe calculation.")
        
        prices_for_portfolios = price_data.drop(columns=['^IRX'], errors='ignore')
        returns_data = prices_for_portfolios.pct_change().dropna(axis=0, how='all').dropna(axis=1, how='all')
        
        return prices_for_portfolios, returns_data, risk_free_rate_annual
    except Exception as e:
        st.error(f"Error downloading or processing data: {e}")

        return pd.DataFrame(), pd.DataFrame(), 0.0 # Changed to return three values


def portfolio_variance(weights, covariance):
    return weights.T @ covariance @ weights

def portfolio_return(weights, returns):
    return weights.T @ returns

def negative_sharpe_ratio(weights, mean_returns, covariance, risk_free_rate_annual):
    port_ret_daily = portfolio_return(weights, mean_returns)
    port_std_daily = np.sqrt(portfolio_variance(weights, covariance))

    annual_port_ret = (1 + port_ret_daily)**252 - 1
    annual_port_std = port_std_daily * np.sqrt(252)
    
    if annual_port_std == 0:
        return -np.inf if annual_port_ret - risk_free_rate_annual > 0 else np.inf
    
    sharpe = (annual_port_ret - risk_free_rate_annual) / annual_port_std
    return -sharpe

def optimize_portfolio(returns_df, tickers, risk_free_rate_annual):
    asset_returns = returns_df[tickers].dropna(axis=0, how='any')

    if asset_returns.empty or asset_returns.shape[0] < 2:
        st.warning(f"Warning: Not enough valid return data available for optimization with tickers: {tickers}.")
        return None

    mean_returns = asset_returns.mean()
    covariance_matrix = asset_returns.cov()
    num_assets = len(tickers)

    if num_assets == 0:
        return None

    initial_weights = np.array([1/num_assets] * num_assets)
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1, 'jac': lambda weights: np.ones_like(weights)})

    optimized_results = minimize(negative_sharpe_ratio,
                                 initial_weights,
                                 args=(mean_returns, covariance_matrix, risk_free_rate_annual),
                                 method='SLSQP',
                                 bounds=bounds,
                                 constraints=constraints,
                                 options={'disp': False})

    if optimized_results.success:
        optimized_weights = optimized_results.x
        optimized_weights /= np.sum(optimized_weights) # Re-normalize
        portfolio_allocation_raw = {tickers[i]: weight for i, weight in enumerate(optimized_weights) if weight > 1e-4}

        if portfolio_allocation_raw:
            total_weight = sum(portfolio_allocation_raw.values())
            if total_weight > 0 :
                 portfolio_allocation_final = {ticker: weight / total_weight for ticker, weight in portfolio_allocation_raw.items()}
                 return portfolio_allocation_final
            else:
                st.warning("Warning: All optimized weights are near zero after filtering. Optimization might not be meaningful.")
                return None
        else:
            return None
    else:
        st.error(f"Optimization failed: {optimized_results.message}")
        return None

def calculate_portfolio_returns_and_sharpe(prices_df, specific_allocation, risk_free_rate_annual):
    portfolio_tickers = list(specific_allocation.keys())
    available_prices = prices_df[portfolio_tickers].dropna(axis=0, how='any')

    if available_prices.empty or len(available_prices) < 2:
        st.warning(f"Not enough valid historical price data for portfolio {portfolio_tickers}.")
        return None, None, None, None

    daily_returns_assets = available_prices.pct_change().dropna()

    if daily_returns_assets.empty:
        st.warning("Could not calculate daily returns for assets in the portfolio.")
        return None, None, None, None

    weights_series = pd.Series(specific_allocation).reindex(daily_returns_assets.columns).fillna(0)
    if weights_series.sum() == 0:
        st.warning("All weights are zero after reindexing. Cannot calculate portfolio returns.")
        return None, None, None, None
    weights_series = weights_series / weights_series.sum() # Ensure weights sum to 1 after reindexing

    portfolio_daily_returns = (daily_returns_assets * weights_series).sum(axis=1)

    portfolio_cumulative_growth = (1 + portfolio_daily_returns).cumprod()
    total_cumulative_return = (portfolio_cumulative_growth.iloc[-1] - 1) * 100

    first_date_data = portfolio_cumulative_growth.index[0]
    last_date_data = portfolio_cumulative_growth.index[-1]
    time_delta_days = (last_date_data - first_date_data).days

    if time_delta_days > 0:
        num_years = time_delta_days / 365.25
        annualized_cumulative_return = ((1 + (total_cumulative_return / 100))**(1/num_years) - 1) * 100
    else:
        annualized_cumulative_return = total_cumulative_return

    mean_daily_portfolio_return = portfolio_daily_returns.mean()
    annualized_portfolio_return = (1 + mean_daily_portfolio_return)**252 - 1

    annualized_portfolio_std = portfolio_daily_returns.std() * np.sqrt(252)

    sharpe_ratio = None
    if annualized_portfolio_std > 1e-6:
        sharpe_ratio = (annualized_portfolio_return - risk_free_rate_annual) / annualized_portfolio_std
    else:
        st.warning("Warning: Annualized portfolio standard deviation is zero or near zero. Sharpe Ratio not meaningful.")

    portfolio_cumulative_growth_indexed = portfolio_cumulative_growth * 100

    return total_cumulative_return, annualized_cumulative_return, sharpe_ratio, portfolio_cumulative_growth_indexed

# --- Main Streamlit App Logic ---
st.set_page_config(layout="wide") # Use a wide layout for better display of charts
st.title("Robo-Advisor Portfolio Recommender")
st.markdown("Welcome to your personalized investment portfolio recommender!")

# Check for openpyxl dependency
try:
    import openpyxl
    openpyxl_available = True
except ImportError:
    openpyxl_available = False
    st.warning("The 'openpyxl' library is not found. Excel download functionality will be disabled. Please install it (`pip install openpyxl`) for full features.")

# State management for multi-step form (optional, but good for complex forms)
if 'page' not in st.session_state:
    st.session_state.page = 'info'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = 0
if 'q11_pref' not in st.session_state:
    st.session_state.q11_pref = False
if 'q12_pref' not in st.session_state:
    st.session_state.q12_pref = False
if 'determined_risk_level' not in st.session_state:
    st.session_state.determined_risk_level = None

# --- Page 1: Personal Information ---
if st.session_state.page == 'info':
    st.header("1. Personal Information")
    with st.form("personal_info_form"):
        user_name = st.text_input("Please enter your full name:", value=st.session_state.user_info.get('name', ''))
        user_email = st.text_input("Please enter your email address:", value=st.session_state.user_info.get('email', ''))
        user_phone = st.text_input("Please enter your phone number:", value=st.session_state.user_info.get('phone', ''))
        user_country = st.text_input("Please enter your country of residence:", value=st.session_state.user_info.get('country', ''))
        
        submitted_info = st.form_submit_button("Proceed to Questionnaire")
        if submitted_info:
            if user_name and user_email and user_phone and user_country:
                st.session_state.user_info = {
                    "name": user_name,
                    "email": user_email,
                    "phone": user_phone,
                    "country": user_country
                }
                st.success(f"Welcome, {user_name}! Let's start the questionnaire.")
                st.session_state.page = 'questionnaire'
                st.rerun() # Rerun to go to the next page
            else:
                st.error("Please fill in all personal information fields.")

# --- Page 2: Risk Questionnaire ---
elif st.session_state.page == 'questionnaire':
    st.header(f"2. Risk Questionnaire for {st.session_state.user_info['name']}")
    total_score = 0
    answer_q11_idx = None
    answer_q12_idx = None

    answers = {}
    
    # Using a form to submit all answers at once
    with st.form("risk_questionnaire_form"):
        for i in range(1, 13):
            question_data = questions[i]
            selected_option = st.radio(f"Question {i}: {question_data['question']}",
                                    question_data['options'],
                                    key=f'q{i}',
                                    index=0) # Default to first option
            
            answer_idx = question_data['options'].index(selected_option)
            score = question_data['scores'][answer_idx]
            total_score += score
            
            if i == 11:
                answer_q11_idx = answer_idx
            elif i == 12:
                answer_q12_idx = answer_idx
            answers[f'q{i}'] = selected_option
        
        submitted_answers = st.form_submit_button("Calculate My Risk Profile")

    if submitted_answers:
        st.session_state.risk_score = total_score
        st.session_state.q11_pref = (answer_q11_idx == 0 and questions[11]["options"][answer_q11_idx] == "Yes, I want a portfolio with sustainable investments")
        st.session_state.q12_pref = (answer_q12_idx == 0 and questions[12]["options"][answer_q12_idx] == "Yes, I want an active strategy")

        st.subheader("Your Risk Profile Assessment")
        st.write(f"Your total score is: {st.session_state.risk_score}")

        determined_risk_level = None
        risk_label = "Undefined Profile"
        if 10 <= st.session_state.risk_score <= 11:
            risk_label = "Ultra Conservative"
            determined_risk_level = 2
        elif 12 <= st.session_state.risk_score <= 14:
            risk_label = "Conservative"
            determined_risk_level = 3
        elif 15 <= st.session_state.risk_score <= 19:
            risk_label = "Cautiously Moderate"
            determined_risk_level = 4
        elif 20 <= st.session_state.risk_score <= 24:
            risk_label = "Moderate"
            determined_risk_level = 5
        elif 25 <= st.session_state.risk_score <= 29:
            risk_label = "Moderate Growth"
            determined_risk_level = 6
        elif 30 <= st.session_state.risk_score <= 34:
            risk_label = "Growth"
            determined_risk_level = 7
        elif 35 <= st.session_state.risk_score <= 38:
            risk_label = "Opportunistic"
            determined_risk_level = 8
        elif 39 <= st.session_state.risk_score <= 40:
            risk_label = "Aggressive Growth"
            determined_risk_level = 9
        else:
            st.warning("Your total score falls outside the defined risk profile ranges.")

        st.session_state.determined_risk_level = determined_risk_level
        st.info(f"Based on your score, your risk profile is: **{risk_label}** (Level {determined_risk_level})")

        esg_message = "You prefer investing in a sustainable portfolio." if st.session_state.q11_pref else ""
        strategy_message = "You prefer an active investment strategy." if st.session_state.q12_pref else ""
        
        final_summary_parts = []
        if esg_message:
            final_summary_parts.append(esg_message)
        if strategy_message:
            final_summary_parts.append(strategy_message)
        
        if final_summary_parts:
            st.write(" ".join(final_summary_parts))

        st.session_state.page = 'results'
        st.rerun()

# --- Page 3: Results and Portfolio Analysis ---
elif st.session_state.page == 'results':
    st.header("3. Your Personalized Portfolio Recommendation")
    
    determined_risk_level = st.session_state.determined_risk_level
    prefers_esg = st.session_state.q11_pref
    prefers_active_strategy = st.session_state.q12_pref

    if determined_risk_level is None:
        st.error("Could not determine a valid risk level. Please go back to the questionnaire.")
        if st.button("Go Back to Questionnaire"):
            st.session_state.page = 'questionnaire'
            st.experimental_rerun()
        st.stop()

    # Define the fixed historical analysis period for returns and Sharpe Ratio
    analysis_start_date = datetime(2023, 1, 1).date()
    analysis_end_date = datetime(2024, 12, 31).date()

    # Load and process data (cached)
    prices_for_portfolios, returns_data, risk_free_rate_annual = download_historical_prices(
        all_unique_tickers_for_download, analysis_start_date, analysis_end_date
    )

    if prices_for_portfolios.empty or returns_data.empty:
        st.error("Cannot proceed with portfolio analysis due to data issues.")
        st.stop()
    
    if prefers_esg or prefers_active_strategy:
        st.subheader(f"Sharpe Ratio Optimized Portfolio for Risk Level {determined_risk_level}")
        
        selected_tickers_for_optimization = risk_level_assets_optimized.get(determined_risk_level, [])
        available_tickers_for_optimization = [t for t in selected_tickers_for_optimization if t in returns_data.columns and not returns_data[t].isnull().all()]

        if not available_tickers_for_optimization:
            st.warning(f"No usable historical data for any of the tickers ({selected_tickers_for_optimization}) in risk level {determined_risk_level} for optimization. Displaying default fixed portfolio if available.")
            
            # Fallback to fixed portfolio if optimization is not possible due to data
            if determined_risk_level in portfolio_data_fixed:
                st.warning("Falling back to fixed portfolio due to insufficient data for optimization.")
                prefers_esg = False # Force fixed path
                prefers_active_strategy = False # Force fixed path
            else:
                st.error("No valid portfolio can be generated with available data and preferences.")
                st.stop() # Stop if no fallback is possible

        elif len(available_tickers_for_optimization) < 1:
            st.warning(f"Not enough unique assets for optimization in risk level {determined_risk_level}. Displaying default fixed portfolio if available.")
            if determined_risk_level in portfolio_data_fixed:
                st.warning("Falling back to fixed portfolio due to insufficient assets for optimization.")
                prefers_esg = False # Force fixed path
                prefers_active_strategy = False # Force fixed path
            else:
                st.error("No valid portfolio can be generated with available data and preferences.")
                st.stop()
        else:
            optimal_allocation = None
            if len(available_tickers_for_optimization) == 1:
                optimal_allocation = {available_tickers_for_optimization[0]: 1.0}
                st.info(f"Only one asset ({available_tickers_for_optimization[0]}) available for optimization. Allocating 100% to it.")
            else:
                optimal_allocation = optimize_portfolio(returns_data, available_tickers_for_optimization, risk_free_rate_annual)

            if optimal_allocation and sum(optimal_allocation.values()) > 0:
                st.write("### Optimal Portfolio Allocation (ETFs):")
                allocation_df = pd.DataFrame(optimal_allocation.items(), columns=['ETF', 'Weight'])
                allocation_df['Weight (%)'] = allocation_df['Weight'] * 100
                st.dataframe(allocation_df[['ETF', 'Weight (%)']].set_index('ETF'))

                category_allocation_optimized = {cat: 0.0 for cat in set(etf_to_category.values())}
                for etf, weight in optimal_allocation.items():
                    category = etf_to_category.get(etf)
                    if category:
                        category_allocation_optimized[category] += weight
                category_allocation_optimized = {cat: weight for cat, weight in category_allocation_optimized.items() if weight > 0.001}
                
                # Plotting category allocation
                fig_cat = plot_pie_chart_with_details(category_allocation_optimized, f'Optimized Portfolio Allocation by Category (Risk Level {determined_risk_level})')
                if fig_cat:
                    st.pyplot(fig_cat)
                    plt.close(fig_cat) # Close the figure to free up memory

                # Detailed allocation within categories
                st.write("### Detailed Allocation within Categories:")
                allocations_by_category_opt = {cat: {} for cat in set(etf_to_category.values())}
                for etf, weight in optimal_allocation.items():
                    category = etf_to_category.get(etf)
                    if category:
                        allocations_by_category_opt[category][etf] = weight

                for category, allocation_dict in allocations_by_category_opt.items():
                    category_total_weight_in_portfolio = category_allocation_optimized.get(category, 0)
                    if category_total_weight_in_portfolio > 0.001:
                        if len(allocation_dict) > 1:
                            normalized_allocation_dict = {etf: weight / category_total_weight_in_portfolio for etf, weight in allocation_dict.items()}
                            fig_detail = plot_pie_chart_with_details(normalized_allocation_dict,
                                                                    f'Optimized Detailed Allocation within {category}')
                            if fig_detail:
                                st.pyplot(fig_detail)
                                plt.close(fig_detail)
                            else:
                                st.write(f"No detailed plot for {category} due to insufficient data.")
                        elif len(allocation_dict) == 1:
                            etf, weight = list(allocation_dict.items())[0]
                            st.write(f"**{category}**: Contains only **{etf}** with **{weight*100:.2f}%** of the portfolio's {category} allocation.")
                    else:
                        st.write(f"Category '{category}' has negligible allocation in this optimized portfolio.")

                total_ret, annualized_ret, sharpe_ratio, portfolio_cumulative_growth_indexed = calculate_portfolio_returns_and_sharpe(
                    prices_for_portfolios, optimal_allocation, risk_free_rate_annual
                )

                if total_ret is not None and annualized_ret is not None:
                    st.write("### Portfolio Performance Metrics:")
                    st.write(f"Total Cumulative Return ({analysis_start_date} to {analysis_end_date}): **{total_ret:.2f}%**")
                    st.write(f"Annualized Cumulative Return: **{annualized_ret:.2f}%**")
                    if sharpe_ratio is not None:
                        st.write(f"Annualized Sharpe Ratio: **{sharpe_ratio:.2f}**")
                    else:
                        st.warning("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")

                    # Plot portfolio growth over time
                    if portfolio_cumulative_growth_indexed is not None and not portfolio_cumulative_growth_indexed.empty:
                        fig_growth, ax_growth = plt.subplots(figsize=(12, 6))
                        ax_growth.plot(portfolio_cumulative_growth_indexed.index, portfolio_cumulative_growth_indexed.values)
                        ax_growth.set_title('Portfolio Performance Over Time (Indexed to 100)')
                        ax_growth.set_xlabel('Date')
                        ax_growth.set_ylabel('Portfolio Value (Indexed)')
                        ax_growth.grid(True)
                        st.pyplot(fig_growth)
                        plt.close(fig_growth)
                        
                        # Save to Excel button only if openpyxl is available
                        if openpyxl_available:
                            # Create a BytesIO object to save the Excel file in memory
                            import io
                            output = io.BytesIO()
                            portfolio_cumulative_growth_indexed.to_excel(output, header=True, index=True)
                            output.seek(0) # Go to the beginning of the BytesIO object
                            st.download_button(
                                label=f"Download Optimized Portfolio Growth Data ({determined_risk_level}) as Excel",
                                data=output,
                                file_name=f"optimized_portfolio_growth_risk_{determined_risk_level}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.info("Install 'openpyxl' (`pip install openpyxl`) to enable Excel download.")
                    else:
                        st.warning("Could not calculate or plot portfolio value history.")
            else:
                st.error("Portfolio optimization failed to produce a valid allocation.")

    else: # Fixed allocation scenario (no ESG/Active preference)
        st.subheader(f"Fixed Portfolio for Risk Level {determined_risk_level}")

        if determined_risk_level not in portfolio_data_fixed:
            st.error(f"Determined risk level {determined_risk_level} does not have a defined fixed portfolio.")
            st.stop()

        selected_portfolio = portfolio_data_fixed[determined_risk_level]
        category_allocation = selected_portfolio['category_allocation']
        specific_etf_allocation = selected_portfolio['specific_etf_allocation']

        st.write("### Fixed Portfolio Allocation (ETFs):")
        allocation_df = pd.DataFrame(specific_etf_allocation.items(), columns=['ETF', 'Weight'])
        allocation_df['Weight (%)'] = allocation_df['Weight'] * 100
        st.dataframe(allocation_df[['ETF', 'Weight (%)']].set_index('ETF'))

        # Plotting category allocation
        fig_cat = plot_pie_chart_with_details(category_allocation, f'Fixed Portfolio Allocation by Category (Risk Level {determined_risk_level})')
        if fig_cat:
            st.pyplot(fig_cat)
            plt.close(fig_cat)

        # Detailed allocation within categories
        st.write("### Detailed Allocation within Categories:")
        allocations_by_category = {cat: {} for cat in set(etf_to_category.values())}
        for etf, weight in specific_etf_allocation.items():
            category = etf_to_category.get(etf)
            if category:
                allocations_by_category[category][etf] = weight
        
        active_categories_for_plotting = {
            cat: alloc_dict for cat, alloc_dict in allocations_by_category.items()
            if sum(alloc_dict.values()) > 0.001
        }

        for category, allocation_dict in active_categories_for_plotting.items():
            category_total_weight_in_portfolio = category_allocation.get(category, 0)
            if category_total_weight_in_portfolio > 0.001:
                if len(allocation_dict) > 1:
                    normalized_allocation_dict = {
                        etf: weight / category_total_weight_in_portfolio
                        for etf, weight in allocation_dict.items()
                    }
                    fig_detail = plot_pie_chart_with_details(normalized_allocation_dict,
                                                                f'Fixed Detailed Allocation within {category}')
                    if fig_detail:
                        st.pyplot(fig_detail)
                        plt.close(fig_detail)
                    else:
                        st.write(f"No detailed plot for {category} due to insufficient data.")
                elif len(allocation_dict) == 1:
                    etf, weight = list(allocation_dict.items())[0]
                    st.write(f"**{category}**: Contains only **{etf}** with **{weight*100:.2f}%** of the portfolio's {category} allocation.")
            else:
                st.write(f"Category '{category}' has negligible allocation in this fixed portfolio.")

        total_ret, annualized_ret, sharpe_ratio, portfolio_cumulative_growth_indexed = calculate_portfolio_returns_and_sharpe(
            prices_for_portfolios, specific_etf_allocation, risk_free_rate_annual
        )

        if total_ret is not None and annualized_ret is not None:
            st.write("### Portfolio Performance Metrics:")
            st.write(f"Total Cumulative Return ({analysis_start_date} to {analysis_end_date}): **{total_ret:.2f}%**")
            st.write(f"Annualized Cumulative Return: **{annualized_ret:.2f}%**")
            if sharpe_ratio is not None:
                st.write(f"Annualized Sharpe Ratio: **{sharpe_ratio:.2f}**")
            else:
                st.warning("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")

            # Plot portfolio growth over time
            if portfolio_cumulative_growth_indexed is not None and not portfolio_cumulative_growth_indexed.empty:
                fig_growth, ax_growth = plt.subplots(figsize=(12, 6))
                ax_growth.plot(portfolio_cumulative_growth_indexed.index, portfolio_cumulative_growth_indexed.values)
                ax_growth.set_title('Portfolio Performance Over Time (Indexed to 100)')
                ax_growth.set_xlabel('Date')
                ax_growth.set_ylabel('Portfolio Value (Indexed)')
                ax_growth.grid(True)
                st.pyplot(fig_growth)
                plt.close(fig_growth)

                # Save to Excel button only if openpyxl is available
                if openpyxl_available:
                    import io
                    output = io.BytesIO()
                    portfolio_cumulative_growth_indexed.to_excel(output, header=True, index=True)
                    output.seek(0) # Go to the beginning of the BytesIO object
                    st.download_button(
                        label=f"Download Fixed Portfolio Growth Data ({determined_risk_level}) as Excel",
                        data=output,
                        file_name=f"fixed_portfolio_growth_risk_{determined_risk_level}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("Install 'openpyxl' (`pip install openpyxl`) to enable Excel download.")
            else:
                st.warning("Could not calculate or plot portfolio value history.")
    
    st.markdown("---")
    if st.button("Start Over"):
        st.session_state.clear() # Clear all session state variables
        st.experimental_rerun() # Rerun the app from scratch
