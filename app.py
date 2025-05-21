import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import numpy as np
from scipy.optimize import minimize

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

def get_user_info():
    name = input("Please enter your full name: ")
    email = input("Please enter your email address: ")
    phone = input("Please enter your phone number: ")
    country = input("Please enter your country of residence: ")
    print(f"\nWelcome, {name}! Let's start the questionnaire.\n")
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "country": country
    }

def ask_question(qid):
    question = questions[qid]
    print(f"Question {qid}: {question['question']}")
    for i, option in enumerate(question["options"]):
        print(f"{i + 1}. {option}")
    
    while True:
        try:
            answer = int(input(f"Select your answer (1-{len(question['scores'])}): ")) - 1
            if 0 <= answer < len(question["scores"]):
                break
            else:
                print(f"Invalid choice. Please select a number between 1 and {len(question['scores'])}.")
        except ValueError:
            print(f"Please enter a valid number between 1 and {len(question['scores'])}.")
    
    return question["scores"][answer], answer # Return score and the chosen option index

def run_risk_questionnaire():
    user_info = get_user_info()
    print("\nYour information has been successfully recorded!")
    print(f"Name: {user_info['name']}")
    print(f"Email: {user_info['email']}")
    print(f"Phone: {user_info['phone']}")
    print(f"Country: {user_info['country']}\n")

    total_score = 0
    answer_q11_idx = None
    answer_q12_idx = None

    for i in range(1, 13):
        score, answer_idx = ask_question(i)
        total_score += score
        if i == 11:
            answer_q11_idx = answer_idx
        elif i == 12:
            answer_q12_idx = answer_idx

    print(f"\nYour total score is: {total_score}\n")
    print("\n--- Risk Profile Assessment ---")

    risk_label = "Undefined Profile"
    risk_level_for_portfolio = None

    # Mapping total_score to risk levels 2-9
    if 10 <= total_score <= 11:
        risk_label = "Ultra Conservative"
        risk_level_for_portfolio = 2
    elif 12 <= total_score <= 14:
        risk_label = "Conservative"
        risk_level_for_portfolio = 3
    elif 15 <= total_score <= 19:
        risk_label = "Cautiously Moderate"
        risk_level_for_portfolio = 4
    elif 20 <= total_score <= 24:
        risk_label = "Moderate"
        risk_level_for_portfolio = 5
    elif 25 <= total_score <= 29:
        risk_label = "Moderate Growth"
        risk_level_for_portfolio = 6
    elif 30 <= total_score <= 34:
        risk_label = "Growth"
        risk_level_for_portfolio = 7
    elif 35 <= total_score <= 38:
        risk_label = "Opportunistic"
        risk_level_for_portfolio = 8
    elif 39 <= total_score <= 40:
        risk_label = "Aggressive Growth"
        risk_level_for_portfolio = 9
    else:
        print("Warning: Your total score falls outside the defined risk profile ranges.")

    print(f"Based on your score, your risk profile is: {risk_label}")

    answer_q11_is_yes = (answer_q11_idx == 0 and questions[11]["options"][answer_q11_idx] == "Yes, I want a portfolio with sustainable investments")
    answer_q12_is_yes = (answer_q12_idx == 0 and questions[12]["options"][answer_q12_idx] == "Yes, I want an active strategy")

    esg_message = "You prefer investing in a sustainable portfolio." if answer_q11_is_yes else ""
    strategy_message = "You prefer an active investment strategy." if answer_q12_is_yes else ""
    
    final_summary_parts = [f"Your total score is: {total_score}."]
    if esg_message:
        final_summary_parts.append(esg_message)
    if strategy_message:
        final_summary_parts.append(strategy_message)
    print(" ".join(final_summary_parts))

    return risk_level_for_portfolio, answer_q11_is_yes, answer_q12_is_yes

# --- Portfolio Data (for fixed allocation scenario) ---
# This data will be used if Q11 and Q12 are both "No"
portfolio_data_fixed = {
    2: {
        'category_allocation': {'Bond': 1.00, 'Equity': 0.00, 'Real Estate': 0.00, 'Cash': 0.00},
        'specific_etf_allocation': {'SUSB': 0.333, 'EAGG': 0.333, 'VCEB': 0.334}
    },
    3: {
        'category_allocation': {'Bond': 0.80, 'Equity': 0.20, 'Real Estate': 0.00, 'Cash': 0.00},
        'specific_etf_allocation': {'SUSB': 0.266, 'EAGG': 0.267, 'VCEB': 0.267, 'ESGV': 0.10, 'USSG': 0.10}
    },
    4: {
        'category_allocation': {'Bond': 0.60, 'Equity': 0.40, 'Real Estate': 0.00, 'Cash': 0.00},
        'specific_etf_allocation': {'SUSB': 0.20, 'EAGG': 0.20, 'VCEB': 0.20, 'ESGV': 0.20, 'USSG': 0.20}
    },
    5: {
        'category_allocation': {'Bond': 0.40, 'Equity': 0.60, 'Real Estate': 0.00, 'Cash': 0.00},
        'specific_etf_allocation': {'SUSB': 0.133, 'EAGG': 0.133, 'VCEB': 0.134, 'ESGV': 0.30, 'USSG': 0.30}
    },
    6: {
        'category_allocation': {'Bond': 0.20, 'Equity': 0.60, 'Real Estate': 0.20, 'Cash': 0.00},
        'specific_etf_allocation': {'EAGG': 0.10, 'VCEB': 0.10, 'ESGV': 0.20, 'USSG': 0.20, 'ESGU': 0.20, 'XLRE': 0.10, 'SCHH': 0.10}
    },
    7: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.70, 'Real Estate': 0.30, 'Cash': 0.00},
        'specific_etf_allocation': {'ESGV': 0.233, 'USSG': 0.233, 'ESGU': 0.234, 'XLRE': 0.15, 'SCHH': 0.15}
    },
    8: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.80, 'Real Estate': 0.20, 'Cash': 0.00},
        'specific_etf_allocation': {'ESGV': 0.266, 'USSG': 0.267, 'ESGU': 0.267, 'XLRE': 0.10, 'SCHH': 0.10}
    },
    9: {
        'category_allocation': {'Bond': 0.00, 'Equity': 0.90, 'Real Estate': 0.10, 'Cash': 0.00},
        'specific_etf_allocation': {'ESGV': 0.30, 'USSG': 0.30, 'ESGU': 0.30, 'XLRE': 0.05, 'SCHH': 0.05}
    },
}

# --- Portfolio Data (for optimization scenario, from mean_var_esg.py) ---
# This data defines the universe of assets available for optimization for each risk level
risk_level_assets_optimized = {
    2: ['SUSB','EAGG','VCEB',],
    3: ['SUSB','EAGG','VCEB',],
    4: ['SUSB','EAGG','VCEB','ESGV','USSG','VOO'],
    5: ['SUSB','EAGG','VCEB','ESGV','USSG','VOO'],
    6: ['EAGG','VCEB','ESGV','USSG','VOO','XLRE','SCHH'],
    7: ['ESGV','USSG','ESGU','XLRE','SCHH'],
    8: ['ESGV','USSG','ESGU','XLRE','SCHH','IBIT'],
    9: ['ESGV','USSG','ESGU','XLRE','SCHH','IBIT']
}

# Mapping ETFs to their categories (used in both scenarios for plotting)
etf_to_category = {
    'SUSB': 'Bond', 'EAGG': 'Bond', 'VCEB': 'Bond',
    'ESGV': 'Equity', 'USSG': 'Equity', 'ESGU': 'Equity', 'VOO': 'Equity', 'IBIT': 'Equity',
    'XLRE': 'Real Estate', 'SCHH': 'Real Estate',
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
        print(f"No significant data to plot for: {title}")
        return

    fig, ax = plt.subplots(figsize=figsize)
    colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))
    wedges, texts, autotexts = ax.pie(sizes, autopct=autopct, startangle=startangle, colors=colors,
                                      wedgeprops=dict(width=0.4, edgecolor='w'))
    for autotext in autotexts:
        autotext.set_color('black')
    ax.legend(wedges, labels, title="Assets", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(title)
    ax.axis('equal')
    plt.show()

# --- Functions for Portfolio Optimization (from mean_var_esg.py) ---
def download_historical_prices(tickers, start_date, end_date):
    """Downloads historical 'Adj Close' price data from Yahoo Finance for a given period."""
    if not tickers:
        print("No tickers provided for download.")
        return pd.DataFrame()
    print(f"\nDownloading historical data for {tickers} from {start_date} to {end_date}...")
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        if data.empty:
            print("No data downloaded. Check ticker symbols or date range.")
            return pd.DataFrame()
        if 'Adj Close' in data.columns:
            price_data = data['Adj Close']
        elif 'Close' in data.columns:
            price_data = data['Close']
        else:
            if isinstance(data, pd.DataFrame) and len(data.columns) == 1:
                price_data = data.iloc[:, 0]
            elif isinstance(data, pd.Series):
                price_data = data
            else:
                print(f"Could not find 'Adj Close' or 'Close' prices for {tickers}.")
                return pd.DataFrame()
        if isinstance(price_data, pd.Series):
            price_data = price_data.to_frame()
        price_data = price_data.dropna(axis=1, how='all')
        price_data = price_data.dropna(axis=0, how='all')
        if price_data.empty:
            print("After cleaning, no valid price data remains.")
        return price_data
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()

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
        print(f"Warning: Not enough valid return data available for optimization with tickers: {tickers}.")
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
                print("Warning: All optimized weights are near zero after filtering. Optimization might not be meaningful.")
                return None
        else:
            return None
    else:
        print(f"Optimization failed: {optimized_results.message}")
        return None

def calculate_portfolio_returns_and_sharpe(prices_df, specific_allocation, risk_free_rate_annual):
    portfolio_tickers = list(specific_allocation.keys())
    available_prices = prices_df[portfolio_tickers].dropna(axis=0, how='any')

    if available_prices.empty or len(available_prices) < 2:
        print(f"Not enough valid historical price data for portfolio {portfolio_tickers}.")
        return None, None, None, None

    daily_returns_assets = available_prices.pct_change().dropna()

    if daily_returns_assets.empty:
        print("Could not calculate daily returns for assets in the portfolio.")
        return None, None, None, None

    weights_series = pd.Series(specific_allocation).reindex(daily_returns_assets.columns).fillna(0)
    if weights_series.sum() == 0:
        print("All weights are zero after reindexing. Cannot calculate portfolio returns.")
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
        print("Warning: Annualized portfolio standard deviation is zero or near zero. Sharpe Ratio not meaningful.")

    portfolio_cumulative_growth_indexed = portfolio_cumulative_growth * 100

    return total_cumulative_return, annualized_cumulative_return, sharpe_ratio, portfolio_cumulative_growth_indexed

def save_portfolio_value_to_excel(portfolio_values, filename="portfolio_performance.xlsx"):
    if portfolio_values is None or portfolio_values.empty:
        print("No portfolio values to save to Excel.")
        return

    try:
        portfolio_values.name = 'Portfolio Value'
        portfolio_values.to_excel(filename, header=True, index=True)
        print(f"Portfolio performance saved to {filename}")
    except Exception as e:
        print(f"Error saving portfolio performance to Excel: {e}")

# --- Main Execution Logic ---
if __name__ == "__main__":
    try:
        import openpyxl
    except ImportError:
        print("The 'openpyxl' library is required to save data to Excel.")
        print("Please install it by running: pip install openpyxl")
        exit()

    print("--- Starting Risk Assessment and Portfolio Analysis ---")

    # Run the risk questionnaire to get the user's risk level and preferences
    determined_risk_level, prefers_esg, prefers_active_strategy = run_risk_questionnaire()

    if determined_risk_level is None:
        print("\nCould not determine a valid risk level from the questionnaire. Exiting.")
        exit()

    # Define the fixed historical analysis period for returns and Sharpe Ratio
    analysis_start_date = datetime(2023, 1, 1).date()
    analysis_end_date = datetime(2024, 12, 31).date()

    # Download all necessary historical data once for the full period, including risk-free rate
    all_historical_data = download_historical_prices(all_unique_tickers_for_download, analysis_start_date, analysis_end_date)

    if all_historical_data.empty:
        print("\nFailed to download essential historical data. Please check your internet connection, ticker symbols, and date range.")
        print("Exiting application.")
        exit()
    
    # Extract risk-free rate
    risk_free_rate_annual = 0.0
    if '^IRX' in all_historical_data.columns:
        rf_series = all_historical_data['^IRX'].dropna()
        if not rf_series.empty:
            risk_free_rate_annual = rf_series.mean() / 100.0
            print(f"\nAverage Annual Risk-Free Rate ({analysis_start_date} to {analysis_end_date}): {risk_free_rate_annual*100:.2f}%")
        else:
            print("Warning: No valid risk-free rate data (^IRX) for the specified period. Using 0 as risk-free rate for Sharpe calculation.")
    else:
        print("Warning: '^IRX' ticker not found in downloaded data. Using 0 as risk-free rate for Sharpe calculation.")

    prices_for_portfolios = all_historical_data.drop(columns=['^IRX'], errors='ignore')
    returns_data = prices_for_portfolios.pct_change().dropna(axis=0, how='all').dropna(axis=1, how='all')

    # --- Conditional Logic for Portfolio Selection ---
    if prefers_esg or prefers_active_strategy:
        print(f"\n--- Running Sharpe Ratio Optimization for User's Risk Level: {determined_risk_level} (due to ESG/Active preference) ---")
        
        # Only optimize for the determined risk level, not all of them
        risk_level_opt = determined_risk_level 

        selected_tickers_for_optimization = risk_level_assets_optimized.get(risk_level_opt, [])
        available_tickers_for_optimization = [t for t in selected_tickers_for_optimization if t in returns_data.columns and not returns_data[t].isnull().all()]

        if not available_tickers_for_optimization:
            print(f"No usable historical data for any of the tickers ({selected_tickers_for_optimization}) in risk level {risk_level_opt} for optimization. Skipping.")
        elif len(available_tickers_for_optimization) < 1:
            print(f"Not enough unique assets for optimization in risk level {risk_level_opt}. Skipping.")
        else: # Proceed with optimization for the single determined risk level
            # Special handling for single asset case (optimization isn't needed, allocate 100% to it)
            if len(available_tickers_for_optimization) == 1:
                optimal_allocation = {available_tickers_for_optimization[0]: 1.0}
                print(f"Only one asset ({available_tickers_for_optimization[0]}) available for optimization in Risk Level {risk_level_opt}. Allocating 100% to it.")
            else:
                optimal_allocation = optimize_portfolio(returns_data, available_tickers_for_optimization, risk_free_rate_annual)

            if optimal_allocation and sum(optimal_allocation.values()) > 0:
                print(f"\n--- Optimal Portfolio Allocation (Sharpe Ratio) for Risk Level {risk_level_opt} ---")
                for ticker, weight in optimal_allocation.items():
                    print(f"  {ticker}: {weight*100:.2f}%")

                # Re-calculate category allocation for plotting
                category_allocation_optimized = {cat: 0.0 for cat in set(etf_to_category.values())}
                for etf, weight in optimal_allocation.items():
                    category = etf_to_category.get(etf)
                    if category:
                        category_allocation_optimized[category] += weight
                
                # Filter out categories with zero total weight for plotting
                category_allocation_optimized = {cat: weight for cat, weight in category_allocation_optimized.items() if weight > 0.001}

                plot_pie_chart_with_details(category_allocation_optimized, f'Optimized Portfolio Allocation by Category (Risk Level {risk_level_opt})')
                
                # Plot specific ETF allocations within categories for optimized portfolio
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
                            plot_pie_chart_with_details(normalized_allocation_dict,
                                                        f'Optimized Detailed Allocation within {category} (Risk Level {risk_level_opt})')
                        elif len(allocation_dict) == 1:
                            etf, weight = list(allocation_dict.items())[0]
                            print(f"\n--- Optimized Detailed Allocation within {category} (Risk Level {risk_level_opt}) Details ---")
                            print(f"  - {etf}: {weight*100:.2f}% (This ETF forms {weight/category_total_weight_in_portfolio*100:.2f}% of {category} category)")
                            print(f"Category '{category}' for Risk Level {risk_level_opt} contains only {etf}. No detailed pie chart for single asset.")
                    else:
                        print(f"Category '{category}' has negligible allocation in this optimized portfolio. Skipping detailed plot.")

                # Get and Display Last Available Prices for Optimized Portfolio
                etfs_to_get_price_opt = list(optimal_allocation.keys())
                if etfs_to_get_price_opt:
                    valid_etfs_for_price_opt = [t for t in etfs_to_get_price_opt if t in prices_for_portfolios.columns]
                    if valid_etfs_for_price_opt:
                        last_prices_opt = prices_for_portfolios[valid_etfs_for_price_opt].iloc[-1]
                        print(f"\n--- Last Available Prices of Optimized ETFs (as of {last_prices_opt.name.date()}) ---")
                        for etf, price in last_prices_opt.items():
                            print(f"  {etf}: ${price:.2f}")
                    else:
                        print("\nNo valid ETF prices found in downloaded data for current price display for optimized portfolio.")
                else:
                    print("\nNo ETFs allocated in this optimized portfolio to fetch current prices.")


                # Calculate and Display Portfolio Returns & Sharpe Ratio for Optimized Portfolio
                print(f"\n--- Optimized Portfolio Performance ({analysis_start_date} to {analysis_end_date}) for Risk Level {risk_level_opt} ---")
                total_ret, annualized_ret, sharpe_ratio, portfolio_cumulative_growth_indexed = calculate_portfolio_returns_and_sharpe(
                    prices_for_portfolios, optimal_allocation, risk_free_rate_annual
                )

                if total_ret is not None and annualized_ret is not None:
                    print(f"Total Cumulative Return: {total_ret:.2f}%")
                    print(f"Annualized Cumulative Return: {annualized_ret:.2f}%")
                    if sharpe_ratio is not None:
                        print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
                    else:
                        print("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")
                else:
                    print("Could not calculate portfolio returns or Sharpe Ratio for this optimized portfolio.")

                save_portfolio_value_to_excel(portfolio_cumulative_growth_indexed,
                                               filename=f"optimized_portfolio_growth_risk_{risk_level_opt}.xlsx")
            else:
                print(f"Optimization for Risk Level {risk_level_opt} failed to produce a valid portfolio.")

    else:
        # Default behavior: use the fixed portfolio data based on the determined risk level
        print(f"\n--- Analyzing Fixed Portfolio for Determined Risk Level: {determined_risk_level} ---")

        if determined_risk_level not in portfolio_data_fixed:
            print(f"Determined risk level {determined_risk_level} does not have a defined fixed portfolio. Exiting.")
            exit()

        selected_portfolio = portfolio_data_fixed[determined_risk_level]
        category_allocation = selected_portfolio['category_allocation']
        specific_etf_allocation = selected_portfolio['specific_etf_allocation']

        print(f"\n--- Analyzing Fixed Portfolio for Risk Level {determined_risk_level} ---")

        # --- 1. Plot Category Allocation ---
        plot_pie_chart_with_details(category_allocation, f'Fixed Portfolio Allocation by Category (Risk Level {determined_risk_level})')

        # --- 2. Plot Specific ETF Allocation for each category ---
        allocations_by_category = {cat: {} for cat in set(etf_to_category.values())}
        for etf, weight in specific_etf_allocation.items():
            category = etf_to_category.get(etf)
            if category:
                allocations_by_category[category][etf] = weight
            else:
                print(f"Warning: ETF {etf} not found in etf_to_category mapping. Skipping from detailed plot.")

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
                    plot_pie_chart_with_details(normalized_allocation_dict,
                                                f'Fixed Detailed Allocation within {category} (Risk Level {determined_risk_level})')
                elif len(allocation_dict) == 1:
                    etf, weight = list(allocation_dict.items())[0]
                    print(f"\n--- Fixed Detailed Allocation within {category} (Risk Level {determined_risk_level}) Details ---")
                    print(f"  - {etf}: {weight*100:.2f}% (This ETF forms {weight/category_total_weight_in_portfolio*100:.2f}% of {category} category)")
                    print(f"Category '{category}' for Risk Level {determined_risk_level} contains only {etf}. No detailed pie chart for single asset.")
            else:
                print(f"Category '{category}' has negligible allocation in this fixed portfolio. Skipping detailed plot.")

        # --- 3. Display Specific ETF Allocation (Names and Percentages) ---
        print(f"\n--- Specific ETFs and Their Percentages for Fixed Risk Level {determined_risk_level} ---")
        if specific_etf_allocation:
            sorted_etfs = sorted(specific_etf_allocation.items(), key=lambda item: item[1], reverse=True)
            for etf, weight in sorted_etfs:
                print(f"  - {etf}: {weight*100:.2f}%")
        else:
            print("No specific ETFs allocated in this fixed portfolio.")

        # --- 4. Get and Display Last Available Prices ---
        etfs_to_get_price = list(specific_etf_allocation.keys())
        if etfs_to_get_price:
            valid_etfs_for_price = [t for t in etfs_to_get_price if t in prices_for_portfolios.columns]
            if valid_etfs_for_price:
                last_prices = prices_for_portfolios[valid_etfs_for_price].iloc[-1]
                print(f"\n--- Last Available Prices of Fixed Allocated ETFs (as of {last_prices.name.date()}) ---")
                for etf, price in last_prices.items():
                    print(f"  {etf}: ${price:.2f}")
            else:
                print("\nNo valid ETF prices found in downloaded data for current price display for fixed portfolio.")
        else:
            print("\nNo ETFs allocated in this fixed portfolio to fetch current prices.")

        # --- 5. Calculate and Display Portfolio Returns & Sharpe Ratio ---
        print(f"\n--- Fixed Portfolio Performance ({analysis_start_date} to {analysis_end_date}) for Risk Level {determined_risk_level} ---")
        
        total_ret, annualized_ret, sharpe_ratio, portfolio_cumulative_growth_indexed = calculate_portfolio_returns_and_sharpe(
            prices_for_portfolios, specific_etf_allocation, risk_free_rate_annual
        )

        if total_ret is not None and annualized_ret is not None:
            print(f"Total Cumulative Return: {total_ret:.2f}%")
            print(f"Annualized Cumulative Return: {annualized_ret:.2f}%")
            if sharpe_ratio is not None:
                print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
            else:
                print("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")
        else:
            print("Could not calculate portfolio returns or Sharpe Ratio for this fixed portfolio.")

        # --- 6. Save Cumulative Return Data to Excel ---
        save_portfolio_value_to_excel(portfolio_cumulative_growth_indexed,
                                       filename=f"fixed_portfolio_growth_risk_{determined_risk_level}.xlsx")

    print("\nApplication finished.")
