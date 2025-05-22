import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import numpy as np
from scipy.optimize import minimize # Kept for consistency, but not used in this specific fixed allocation logic
import os

# --- Risk Questionnaire Definitions ---
questions = {
    1: {"question": "How old are you?", "options": ["Over 60", "45-60", "30-44", "Under 30"], "scores": [1, 2, 3, 4]},
    2: {"question": "What is your investment experience?", "options": ["I don’t have any experience", "I have some experience", "I have a strong educational background in a related field", "I’m an experienced investor"], "scores": [1, 2, 3, 4]},
    3: {"question": "What is an ETF?", "options": ["I don’t know", "A diversified investment fund that only trades commodities", "A diversified, index-tracking investment fund that does not trade on exchanges", "A diversified, index-tracking investment fund that trades on exchanges"], "scores": [1, 2, 3, 4]},
    4: {"question": "Main goal of your investment", "options": ["Capital preservation", "Conservative investment", "General investment", "Capital growth"], "scores": [1, 2, 3, 4]},
    5: {"question": "What is your investment horizon?", "options": ["<5 years", "5-10 years", "10-15 years", ">15 years"], "scores": [1, 2, 3, 4]},
    6: {"question": "Do you prefer guaranteed small gains or potential big gains with risk?", "options": ["Guarantees only", "Smaller gains and contained risk", "Moderate gain and moderate risk", "Big gains with high risk"], "scores": [1, 2, 3, 4]},
    7: {"question": "What is your tolerance of market swings?", "options": ["Low", "Medium-low", "Medium-high", "High"], "scores": [1, 2, 3, 4]},
    8: {"question": "Do you prefer a strategy that:", "options": ["Try to Beat the market", "It is aligned with Stock market Performance", "It is aligned with Bond market Performance", "It is able to provide reassurance during high volatile market periods"], "scores": [1, 2, 3, 4]},
    9: {"question": "What’s the worst-case decline you’re comfortable seeing in 1 year?", "options": ["Less than 10%", "10-20%", "20-30%", "More than 30%"], "scores": [1, 2, 3, 4]},
    10: {"question": "What would you do if you hear the market is down 20%?", "options": ["I sell a majority of my financial assets", "I sell a minority of my financial assets", "I maintain my position", "I buy more"], "scores": [1, 2, 3, 4]},
    11: {"question": "Do you have any preference for ESG (environmental, social, governance) investments?", "options": ["Yes, I want a portfolio with sustainable investments", "No, I don’t take the sustainable factor into consideration"], "scores": [4, 1]},
    12: {"question": "Do you have any preference for the investment strategy of your Roboadvisor?", "options": ["Yes, I want an active strategy", "No, I want a passive strategy"], "scores": [4, 1]}
}

# --- Portfolio Data for FIXED ALLOCATION (when Q11 and Q12 are NO) ---
portfolio_data_fixed = {
    2: {
        'category_allocation': {'Bond': 1.00, 'Equity': 0.00, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.5 ,'AGG': 0.4 ,'BOND': 0.1}
    },
    3: {
        'category_allocation': {'Bond': 1.0, 'Equity': 0.0, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.5 ,'AGG': 0.25 ,'BOND': 0.25}
    },
    4: {
        'category_allocation': {'Bond': 0.85, 'Equity': 0.15, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.4306 ,'AGG': 0.085 ,'BOND': 0.3419, 'VTI':0.015 , 'SPLG': 0.0525, 'VOO': 0.075}
    },
    5: {
        'category_allocation': {'Bond': 0.75, 'Equity': 0.25, 'Real Estate': 0.00,'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.3081 ,'AGG': 0.0705 ,'BOND': 0.3719, 'VTI':0.0375 , 'SPLG':0.145, 'VOO': 0.0625}
    },
    6: {
        'category_allocation': {'Bond': 0.60, 'Equity': 0.40, 'Real Estate': 0.00, 'Crypto': 0.00},
        'specific_etf_allocation': {'SHY': 0.0 ,'AGG': 0.3085 ,'BOND': 0.3085, 'VTI':0.1415 , 'SPLG':0.1415 , 'VOO':0.2415}
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

# --- Portfolio Data for ESG/ACTIVE FIXED ALLOCATION (when Q11 or Q12 are YES) ---
portfolio_data_esg_active = {
    2: {
        'category_allocation': {'Bond': 1.00, 'Equity': 0.00, 'Real Estate': 0.00},
        'specific_etf_allocation': {'SUSB': 0.45, 'EAGG': 0.41, 'VCEB': 0.14}
    },
    3: {
        'category_allocation': {'Bond': 1.0, 'Equity': 0.0, 'Real Estate': 0.00},
        'specific_etf_allocation': {'SUSB': 0.5, 'EAGG': 0.36, 'VCEB': 0.14}
    },
    4: {
        'category_allocation': {'Bond': 0.89, 'Equity': 0.11, 'Real Estate': 0.00},
        'specific_etf_allocation': {'SUSB': 0.4493, 'EAGG': 0.1902, 'VCEB': 0.2591, 'ESGV': 0.0507, 'USSG': 0.0507}
    },
    5: {
        'category_allocation': {'Bond': 0.75, 'Equity': 0.25, 'Real Estate': 0.00},
        'specific_etf_allocation': {'SUSB': 0.133, 'EAGG': 0.133, 'VCEB': 0.134, 'ESGV': 0.30, 'USSG': 0.30}
    },
    6: {
        'category_allocation': {'Bond': 0.63, 'Equity': 0.37, 'Real Estate': 0.00},
        'specific_etf_allocation': {'SUSB': 0.061 ,'EAGG': 0.3764, 'VCEB': 0.19, 'USSG': 0.1863, 'ESGU': 0.1863}
    },
    7: {
        'category_allocation': {'Bond': 0.00, 'Equity': 1.0, 'Real Estate': 0.0},
        'specific_etf_allocation': {'ESGV': 0.1, 'USSG': 0.55, 'ESGU': 0.35}
    },
    8: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.61, 'Real Estate': 0.39},
        'specific_etf_allocation': {'ESGV': 0.2535, 'USSG': 0.2265, 'ESGU': 0.2335, 'GRES':0.1365, 'NURE':0.15}
    },
    9: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.90, 'Real Estate': 0.10}, # Corrected category to Real Estate
        'specific_etf_allocation': {'ESGV': 0.3353, 'USSG': 0.3353, 'ESGU': 0.30, 'GRES':0.1647, 'NURE':0.1647}
    },
}

# Mapping ETFs to their categories (used in both scenarios for plotting)
etf_to_category = {
    # Fixed Portfolio ETFs
    'SHY': 'Bond', 'AGG': 'Bond', 'BOND': 'Bond',
    'VTI': 'Equity', 'SPLG': 'Equity', 'VOO': 'Equity',
    'XLRE': 'Real Estate', 'SCHH': 'Real Estate',
    'GBTC': 'Crypto',
    # ESG/Active Fixed Portfolio ETFs
    'SUSB': 'Bond', 'EAGG': 'Bond', 'VCEB': 'Bond',
    'ESGV': 'Equity', 'USSG': 'Equity', 'ESGU': 'Equity',
    'GRES': 'Real Estate', 'NURE': 'Real Estate',
    'IBIT': 'Crypto', # Assuming IBIT is Crypto/Equity - adjusted to Crypto for consistency with GBTC
}

# Define all unique tickers across both fixed portfolio sets, plus risk-free rate
all_unique_tickers_for_download = sorted(list(set(
    [etf for data in portfolio_data_fixed.values() for etf in data['specific_etf_allocation'].keys()] +
    [etf for data in portfolio_data_esg_active.values() for etf in data['specific_etf_allocation'].keys()] +
    ['^IRX'] # Add ^IRX for risk-free rate
)))

# --- Plotting Functions (shared) ---
def plot_pie_chart_with_details(data_dict, title, figsize=(9, 9), autopct='%1.1f%%', startangle=140):
    labels = []
    sizes = []
    # Filter out very small allocations, as they clutter the pie chart
    filtered_data = {k: v for k, v in data_dict.items() if v > 0.001}
    
    # Check if there are any remaining items after filtering
    if not filtered_data:
        st.warning(f"No significant data to plot for: {title}. All values were too small or zero.")
        return None

    # Recalculate labels and sizes from filtered data
    labels = list(filtered_data.keys())
    sizes = list(filtered_data.values())

    # Re-normalize if filtering changed the sum significantly, so percentages are accurate relative to filtered data
    total_size = sum(sizes)
    if total_size > 0: # Avoid division by zero
        sizes = [s / total_size for s in sizes]

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

# --- Functions for Portfolio Analysis ---
@st.cache_data # Cache this function to avoid re-downloading data
def download_historical_prices(tickers, start_date, end_date):
    """Downloads historical 'Adj Close' price data from Yahoo Finance for a given period."""
    if not tickers:
        st.error("No tickers provided for download.")
        return pd.DataFrame(), pd.DataFrame(), 0.0

    st.info(f"Downloading historical data for {len(tickers)} assets from {start_date} to {end_date}...")
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        if data.empty:
            st.error("No data downloaded. Check ticker symbols or date range.")
            return pd.DataFrame(), pd.DataFrame(), 0.0

        # Handle data structure: for multiple tickers, 'Adj Close' is multi-column; for single, it's a Series or one column.
        if isinstance(data.columns, pd.MultiIndex) and 'Adj Close' in data.columns.levels[0]:
            price_data = data['Adj Close']
        elif 'Adj Close' in data.columns: # Single ticker, but data is a DataFrame
            price_data = data[['Adj Close']]
        elif 'Close' in data.columns: # Fallback to 'Close' if 'Adj Close' not found
            price_data = data[['Close']]
        else:
            # Handle cases where data might be a single Series for a single ticker download
            if len(tickers) == 1 and isinstance(data, pd.DataFrame) and not data.empty:
                 # Check if the single ticker's data has a 'Close' or 'Adj Close' column, or if it's already the series
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
            return pd.DataFrame(), pd.DataFrame(), 0.0

        # --- risk_free_rate_annual ---
        risk_free_rate_annual = 0.0
        if '^IRX' in price_data.columns: # Check if '^IRX' is in the final price_data
            rf_series = price_data['^IRX'].dropna()
            if not rf_series.empty:
                # ^IRX is typically annualized percentage yield (e.g., 4.5 for 4.5%). Convert to decimal.
                risk_free_rate_annual = rf_series.mean() / 100.0
                st.info(f"Calculated Average Annual Risk-Free Rate: {risk_free_rate_annual*100:.2f}%")
            else:
                st.warning("No valid risk-free rate data (^IRX) for the specified period. Using 0 as risk-free rate for Sharpe calculation.")
        else:
            st.warning("'^IRX' ticker not found in downloaded data. Using 0 as risk-free rate for Sharpe calculation.")
        
        # Remove '^IRX' from the main prices DataFrame that will be used for portfolio asset calculations
        prices_for_portfolios = price_data.drop(columns=['^IRX'], errors='ignore')
        
        # Calculate returns, dropping rows/cols with all NaNs
        returns_data = prices_for_portfolios.pct_change().dropna(axis=0, how='all').dropna(axis=1, how='all')
        
        return prices_for_portfolios, returns_data, risk_free_rate_annual
    except Exception as e:
        st.error(f"Error downloading or processing data: {e}")
        st.info("Common issues: incorrect ticker symbols, invalid date range, or internet connectivity problems.")
        return pd.DataFrame(), pd.DataFrame(), 0.0

def calculate_portfolio_returns_and_sharpe(prices_df, specific_allocation, risk_free_rate_annual):
    portfolio_tickers = list(specific_allocation.keys())
    
    # Filter prices_df to only include tickers that are actually in the prices_df columns and have non-NaN values
    available_portfolio_tickers = [t for t in portfolio_tickers if t in prices_df.columns and not prices_df[t].isnull().all()]

    if not available_portfolio_tickers:
        st.warning(f"No valid historical price data available for any of the specified ETFs in the allocation. Cannot calculate performance.")
        return None, None, None, None, None

    # Recreate specific_allocation with only available tickers and re-normalize weights
    filtered_specific_allocation = {ticker: specific_allocation[ticker] for ticker in available_portfolio_tickers}
    total_filtered_weight = sum(filtered_specific_allocation.values())
    
    if total_filtered_weight == 0:
        st.warning("All allocated weights sum to zero after filtering for available tickers. Cannot calculate portfolio returns.")
        return None, None, None, None, None
    
    # Normalize weights to sum to 1 only for available tickers
    normalized_specific_allocation = {ticker: weight / total_filtered_weight for ticker, weight in filtered_specific_allocation.items()}

    available_prices = prices_df[available_portfolio_tickers].dropna(axis=0, how='any')

    if available_prices.empty or len(available_prices) < 2:
        st.warning(f"Not enough common valid historical price data for portfolio {available_portfolio_tickers} after filtering missing data points. Need at least 2 data points.")
        return None, None, None, None, None

    daily_returns_assets = available_prices.pct_change().dropna()

    if daily_returns_assets.empty:
        st.warning("Could not calculate daily returns for assets in the portfolio after differencing and dropping NaNs.")
        return None, None, None, None, None

    # Ensure weights are aligned with daily_returns_assets columns and are ordered correctly
    weights_array = np.array([normalized_specific_allocation.get(col, 0) for col in daily_returns_assets.columns])
    
    portfolio_daily_returns = (daily_returns_assets * weights_array).sum(axis=1)

    portfolio_cumulative_growth = (1 + portfolio_daily_returns).cumprod()
    if portfolio_cumulative_growth.empty:
        st.warning("Cumulative growth could not be calculated (empty series after cumprod).")
        return None, None, None, None, None
    
    # Index the cumulative growth to 100 for plotting
    portfolio_cumulative_growth_indexed = portfolio_cumulative_growth / portfolio_cumulative_growth.iloc[0] * 100

    total_cumulative_return = (portfolio_cumulative_growth.iloc[-1] - 1) * 100

    first_date_data = portfolio_cumulative_growth.index[0]
    last_date_data = portfolio_cumulative_growth.index[-1]
    time_delta_days = (last_date_data - first_date_data).days

    annualized_cumulative_return = total_cumulative_return # Default if cannot annualize
    if time_delta_days > 0:
        num_years = time_delta_days / 365.25
        if num_years > 0:
            # Formula for annualized return: (1 + total_return_decimal)^(1/num_years) - 1
            base_return_decimal = (total_cumulative_return / 100)
            # Ensure base_return_decimal is not too low for numerical stability if very negative
            if (1 + base_return_decimal) >= 0: # Check for non-negative base for exponentiation
                annualized_cumulative_return = ((1 + base_return_decimal)**(1/num_years) - 1) * 100
            else:
                st.warning("Cannot annualize return: (1 + total_return_decimal) is negative. Results may be misleading.")
                annualized_cumulative_return = None # Indicate it's not well-defined
        else:
            st.warning("Time delta is zero, cannot annualize return over zero period.")
            annualized_cumulative_return = None

    mean_daily_portfolio_return = portfolio_daily_returns.mean()
    annualized_portfolio_return = (1 + mean_daily_portfolio_return)**252 - 1 # Assuming 252 trading days

    annualized_portfolio_std = portfolio_daily_returns.std() * np.sqrt(252) # Assuming 252 trading days

    sharpe_ratio = None
    if annualized_portfolio_std > 1e-9: # Avoid division by zero or very small numbers
        # Use annualized returns and risk-free rate for Sharpe Ratio
        sharpe_ratio = (annualized_portfolio_return - risk_free_rate_annual) / annualized_portfolio_std
    else:
        st.warning("Warning: Annualized portfolio standard deviation is zero or near zero. Sharpe Ratio not meaningful.")

    return total_cumulative_return, annualized_cumulative_return, annualized_portfolio_std, sharpe_ratio, portfolio_cumulative_growth_indexed

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

# State management for multi-step form
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
                st.rerun()
            else:
                st.error("Please fill in all personal information fields.")

# --- Page 2: Risk Questionnaire ---
elif st.session_state.page == 'questionnaire':
    st.header(f"2. Risk Questionnaire for {st.session_state.user_info.get('name', 'User')}") # Use .get for robustness
    total_score = 0
    answer_q11_idx = None
    answer_q12_idx = None

    with st.form("risk_questionnaire_form"):
        for i in range(1, 13):
            question_data = questions[i]
            # Ensure the default index is within bounds of options
            default_index = 0
            # Try to pre-select based on session state if available, otherwise default to first option
            if f'q{i}' in st.session_state and st.session_state[f'q{i}'] in question_data['options']:
                default_index = question_data['options'].index(st.session_state[f'q{i}'])
            
            selected_option = st.radio(f"Question {i}: {question_data['question']}",
                                       question_data['options'],
                                       key=f'q{i}',
                                       index=default_index)
            
            # Store selected option in session state for persistence
            st.session_state[f'q{i}'] = selected_option
            
            answer_idx = question_data['options'].index(selected_option)
            score = question_data['scores'][answer_idx]
            total_score += score
            
            if i == 11:
                answer_q11_idx = answer_idx
            elif i == 12:
                answer_q12_idx = answer_idx
        
        submitted_answers = st.form_submit_button("Calculate My Risk Profile")

    if submitted_answers:
        st.session_state.risk_score = total_score
        # Q11: "Yes, I want a portfolio with sustainable investments" is index 0
        st.session_state.q11_pref = (answer_q11_idx == 0 and questions[11]["options"][answer_q11_idx] == "Yes, I want a portfolio with sustainable investments")
        # Q12: "Yes, I want an active strategy" is index 0
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
            st.rerun()
        st.stop()

    # Define the historical analysis period for returns and Sharpe Ratio
    analysis_start_date = datetime(2023, 1, 1).date() # Example start date
    analysis_end_date = datetime.now().date() # Today's date

    st.write(f"Analyzing historical performance from **{analysis_start_date}** to **{analysis_end_date}**.")

    # Load and process data (cached)
    prices_for_portfolios, returns_data, risk_free_rate_annual = download_historical_prices(
        all_unique_tickers_for_download, analysis_start_date, analysis_end_date
    )

    if prices_for_portfolios.empty or returns_data.empty:
        st.error("Cannot proceed with portfolio analysis due to data issues. Please check ticker symbols and date range for data availability. Ensure data covers the selected period.")
        st.stop()
    
    # Determine which fixed portfolio to use
    if prefers_esg or prefers_active_strategy:
        st.info(f"Based on your preferences, an **ESG/Active fixed portfolio** is recommended for Risk Level {determined_risk_level}.")
        current_portfolio_data = portfolio_data_esg_active
        portfolio_type_display_name = "ESG/Active Fixed"
        file_name_prefix = "esg_active_fixed"
    else:
        st.info(f"Based on your preferences, a **Standard fixed portfolio** is recommended for Risk Level {determined_risk_level}.")
        current_portfolio_data = portfolio_data_fixed
        portfolio_type_display_name = "Standard Fixed"
        file_name_prefix = "standard_fixed"

    if determined_risk_level not in current_portfolio_data:
        st.error(f"Error: Risk level {determined_risk_level} does not have a defined portfolio in the {portfolio_type_display_name} category.")
        st.stop()

    selected_portfolio = current_portfolio_data[determined_risk_level]
    category_allocation = selected_portfolio['category_allocation']
    specific_etf_allocation = selected_portfolio['specific_etf_allocation']

    st.write(f"### Your Recommended {portfolio_type_display_name} Portfolio (Risk Level {determined_risk_level})")
    
    st.write("#### Portfolio Allocation (ETFs):")
    # Convert allocation to a DataFrame for better display
    allocation_df = pd.DataFrame(specific_etf_allocation.items(), columns=['ETF', 'Weight'])
    allocation_df['Weight (%)'] = (allocation_df['Weight'] * 100).round(2)
    st.dataframe(allocation_df[['ETF', 'Weight (%)']].set_index('ETF'))

    # Plotting category allocation
    st.write("#### Allocation by Asset Category:")
    fig_cat = plot_pie_chart_with_details(category_allocation, f'Portfolio Allocation by Category (Risk Level {determined_risk_level})')
    if fig_cat:
        st.pyplot(fig_cat)
        plt.close(fig_cat) # Close the figure to free up memory

    # Detailed allocation within categories
    st.write("#### Detailed Allocation within Each Major Category:")
    allocations_by_category_current = {cat: {} for cat in set(etf_to_category.values())}
    for etf, weight in specific_etf_allocation.items():
        category = etf_to_category.get(etf)
        if category:
            allocations_by_category_current[category][etf] = weight
    
    # Iterate through categories to plot detailed allocations
    for category in sorted(allocations_by_category_current.keys()): # Sort for consistent order
        allocation_dict = allocations_by_category_current[category]
        # Only plot if the category actually has allocation in the current portfolio and more than one ETF
        category_total_weight_in_portfolio = category_allocation.get(category, 0)
        
        if category_total_weight_in_portfolio > 0.001: # Check if category has any significant allocation
            if len(allocation_dict) > 1: # Only plot if there are multiple ETFs in the category
                current_sum_weights = sum(allocation_dict.values())
                if current_sum_weights > 0:
                    # Normalize weights within this specific category for the pie chart
                    normalized_allocation_dict = {etf: weight / current_sum_weights for etf, weight in allocation_dict.items()}
                    fig_detail = plot_pie_chart_with_details(normalized_allocation_dict,
                                                            f'Detailed Allocation within {category}')
                    if fig_detail:
                        st.pyplot(fig_detail)
                        plt.close(fig_detail)
                    else:
                        st.write(f"No detailed plot for {category} due to filtered (very small) ETFs.")
                else:
                    st.write(f"No detailed plot for {category} as allocated weights sum to zero.")
            elif len(allocation_dict) == 1: # If only one ETF in category
                etf_name, etf_weight = list(allocation_dict.items())[0]
                st.write(f"**{category}**: Only invested in **{etf_name}** ({etf_weight*100:.2f}% of portfolio total).")
            else:
                st.write(f"No specific ETFs allocated to '{category}' in this portfolio's detailed breakdown.")
        # else: no significant allocation in this category for the current portfolio

    # Calculate and display performance metrics for the selected fixed portfolio
    total_ret, annualized_ret, annualized_std, sharpe_ratio, portfolio_cumulative_growth_indexed = \
        calculate_portfolio_returns_and_sharpe(prices_for_portfolios, specific_etf_allocation, risk_free_rate_annual)

    if total_ret is not None and annualized_ret is not None and annualized_std is not None:
        st.write("### Portfolio Performance Metrics (Historical):")
        st.markdown(f"- Total Cumulative Return ({analysis_start_date} to {analysis_end_date}): **{total_ret:.2f}%**")
        st.markdown(f"- Annualized Return: **{annualized_ret:.2f}%**")
        st.markdown(f"- Annualized Standard Deviation (Volatility): **{annualized_std*100:.2f}%**") # Display as percentage
        if sharpe_ratio is not None:
            st.markdown(f"- Annualized Sharpe Ratio: **{sharpe_ratio:.2f}**")
        else:
            st.warning("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")

        # Plot portfolio growth over time
        if portfolio_cumulative_growth_indexed is not None and not portfolio_cumulative_growth_indexed.empty:
            st.write("### Portfolio Performance Over Time:")
            fig_growth, ax_growth = plt.subplots(figsize=(12, 6))
            ax_growth.plot(portfolio_cumulative_growth_indexed.index, portfolio_cumulative_growth_indexed.values)
            ax_growth.set_title(f'{portfolio_type_display_name} Portfolio Performance Over Time (Indexed to 100)')
            ax_growth.set_xlabel('Date')
            ax_growth.set_ylabel('Portfolio Value (Indexed)')
            ax_growth.grid(True)
            st.pyplot(fig_growth)
            plt.close(fig_growth)

            # Save to Excel button only if openpyxl is available
            if openpyxl_available:
                import io
                output = io.BytesIO()
                # Create a DataFrame for Excel, ensuring the index (Date) is included
                excel_df = portfolio_cumulative_growth_indexed.rename('Portfolio Value (Indexed to 100)').to_frame()
                excel_df.index.name = 'Date'
                
                excel_df.to_excel(output, header=True, index=True)
                output.seek(0) # Go to the beginning of the BytesIO object
                
                st.download_button(
                    label=f"Download {portfolio_type_display_name} Portfolio Growth Data as Excel",
                    data=output,
                    file_name=f"{file_name_prefix}_portfolio_growth_risk_{determined_risk_level}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Install 'openpyxl' (`pip install openpyxl`) to enable Excel download.")
        else:
            st.warning("Could not calculate or plot portfolio value history due to insufficient data for the selected ETFs and date range.")
    else:
        st.warning("Could not calculate portfolio performance metrics due to data issues or very limited historical data for the selected ETFs.")
    
    st.markdown("---")
    if st.button("Start Over"):
        st.session_state.clear() # Clear all session state variables
        st.rerun()
