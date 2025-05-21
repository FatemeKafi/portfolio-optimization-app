 import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
import streamlit as st
# Define a dictionary to store question data and scores
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
    # Collect user information
    name = input("Please enter your full name: ")
    email = input("Please enter your email address: ")
    phone = input("Please enter your phone number: ")
    country = input("Please enter your country of residence: ")

    # Display welcome message
    print(f"\nWelcome, {name}! Let's start the questionnaire.\n")
    
    # Return the user information for confirmation
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
            answer = int(input("Select your answer (1-4): ")) - 1
            if 0 <= answer < len(question["scores"]):
                break
            else:
                print(f"Invalid choice. Please select a number between 1 and {len(question['scores'])}.")
        except ValueError:
            print("Please enter a valid number between 1 and 4.")
    
    return question["scores"][answer]  # Accessing the score list by the selected answer

def main():
    # Collect user information
    user_info = get_user_info()

    # Display collected information
    print("\nYour information has been successfully recorded!")
    print(f"Name: {user_info['name']}")
    print(f"Email: {user_info['email']}")
    print(f"Phone: {user_info['phone']}")
    print(f"Country: {user_info['country']}\n")

    # Calculate the total score based on answers
    total_score = 0
    for i in range(1, 13):  # Iterate through questions 1 to 12
        total_score += ask_question(i)

    # Display total score
    print(f"\nYour total score is: {total_score}\n")

    print("\n--- Risk Profile Assessment ---")

    if 10 <= total_score <= 11:
        risk_label = "Ultra Conservative"
    elif 12 <= total_score <= 14:
        risk_label = "Conservative"
    elif 15 <= total_score <= 19:
        risk_label = "Cautiously Moderate"
    elif 20 <= total_score <= 24:
        risk_label = "Moderate"
    elif 25 <= total_score <= 29:
        risk_label = "Moderate Growth"
    elif 30 <= total_score <= 34:
        risk_label = "Growth"
    elif 35 <= total_score <= 38:
        risk_label = "Opportunistic"
    elif 39 <= total_score <= 40:
        risk_label = "Aggressive Growth"
    else:
        risk_label = "Undefined Profile"

    print(f"Based on your score, your risk profile is: {risk_label}")

    # Special handling for questions 11 and 12
    print("For question 11:")
    esg_answer = int(input('Did you select "Yes"? (1 for Yes, 2 for No): ')) - 1
    esg_message = ""
    if esg_answer == 0:
        esg_message = "You prefer investing in a sustainable portfolio."
    
    print("For question 12:")
    strategy_answer = int(input('Did you select "Yes"? (1 for Yes, 2 for No): ')) - 1
    strategy_message = ""
    if strategy_answer == 0:
        strategy_message = "You prefer an active investment strategy."
    
    # Print the final result
    print(f"Your total score is: {total_score} and {esg_message} {strategy_message}")

if __name__ == "__main__":
    main()


if st.button("Submit"):
    st.session_state.total_score = total_score  # ذخیره امتیاز کلی در session_state
    st.session_state.risk_level = calculate_risk_level(total_score)  # محاسبه سطح ریسک
    st.success(f"Your total score: {total_score}")
    st.session_state.page = "portfolio"  # تنظیم صفحه بعدی برای نمایش
    st.experimental_rerun() 


import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import numpy as np

# --- 1. Define Portfolio Structures ---
# IMPORTANT: You MUST replace these placeholder values with your actual data
# from the 'po.PNG' image or your Excel file.
# The sums of weights for each risk level in 'specific_etf_allocation' should be 1.0 (or 100%).
# The sums of weights for each risk level in 'category_allocation' should also be 1.0 (or 100%).

# Example portfolio data - PLEASE REPLACE WITH YOUR ACTUAL DATA FROM po.PNG
portfolio_data = {
    # Risk Level 2 (Low Risk - e.g., high Bond content)
    2: {
        'category_allocation': {
            'Bond': 1.00,
            'Equity': 0.00,
            'Real Estate': 0.00,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'SUSB': 0.333,
            'EAGG': 0.333,
            'VCEB': 0.334,
        }
    },
    # Risk Level 3
    3: {
        'category_allocation': {
            'Bond': 0.80,
            'Equity': 0.20,
            'Real Estate': 0.00,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'SUSB': 0.266,
            'EAGG': 0.267,
            'VCEB': 0.267,
            'ESGV': 0.10,
            'USSG': 0.10,
        }
    },
    # Risk Level 4
    4: {
        'category_allocation': {
            'Bond': 0.60,
            'Equity': 0.40,
            'Real Estate': 0.00,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'SUSB': 0.20,
            'EAGG': 0.20,
            'VCEB': 0.20,
            'ESGV': 0.20,
            'USSG': 0.20,
        }
    },
    # Risk Level 5
    5: {
        'category_allocation': {
            'Bond': 0.40,
            'Equity': 0.60,
            'Real Estate': 0.00,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'SUSB': 0.133,
            'EAGG': 0.133,
            'VCEB': 0.134,
            'ESGV': 0.30,
            'USSG': 0.30,
        }
    },
    # Risk Level 6
    6: {
        'category_allocation': {
            'Bond': 0.20,
            'Equity': 0.60,
            'Real Estate': 0.20,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'EAGG': 0.10,
            'VCEB': 0.10,
            'ESGV': 0.20,
            'USSG': 0.20,
            'ESGU': 0.20,
            'XLRE': 0.10,
            'SCHH': 0.10,
        }
    },
    # Risk Level 7
    7: {
        'category_allocation': {
            'Bond': 0.00,
            'Equity': 0.70,
            'Real Estate': 0.30,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'ESGV': 0.233,
            'USSG': 0.233,
            'ESGU': 0.234,
            'XLRE': 0.15,
            'SCHH': 0.15,
        }
    },
    # Risk Level 8
    8: {
        'category_allocation': {
            'Bond': 0.00,
            'Equity': 0.80,
            'Real Estate': 0.20,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'ESGV': 0.266,
            'USSG': 0.267,
            'ESGU': 0.267,
            'XLRE': 0.10,
            'SCHH': 0.10,
        }
    },
    # Risk Level 9 (High Risk - e.g., high Equity content)
    9: {
        'category_allocation': {
            'Bond': 0.00,
            'Equity': 0.90,
            'Real Estate': 0.10,
            'Cash': 0.00,
        },
        'specific_etf_allocation': {
            'ESGV': 0.30,
            'USSG': 0.30,
            'ESGU': 0.30,
            'XLRE': 0.05,
            'SCHH': 0.05,
        }
    },
}

# Mapping ETFs to their categories (Ensure this aligns with your portfolio data and actual ETFs)
etf_to_category = {
    'SUSB': 'Bond', 'EAGG': 'Bond', 'VCEB': 'Bond',
    'ESGV': 'Equity', 'USSG': 'Equity', 'ESGU': 'Equity',
    'XLRE': 'Real Estate', 'SCHH': 'Real Estate',
}

# Define all tickers to download, including the risk-free rate
all_unique_tickers = sorted(list(set(
    [etf for data in portfolio_data.values() for etf in data['specific_etf_allocation'].keys()] + ['^IRX'] # Add ^IRX for risk-free rate
)))


# --- 2. Plotting Functions (with console output) ---

def plot_pie_chart_with_details(data_dict, title, figsize=(9, 9), autopct='%1.1f%%', startangle=140):
    """
    Plots a pie chart from a dictionary of labels and values,
    filters out near-zero entries, and prints details to console.
    """
    labels = []
    sizes = []
    
    # Filter out entries with zero or very small weights to avoid clutter and improve readability
    for label, size in data_dict.items():
        if size > 0.001: # Only include if weight is more than 0.1%
            labels.append(label)
            sizes.append(size)

    if not sizes:
        print(f"No significant data to plot for: {title}")
        return

    total_size = sum(sizes)
    if not np.isclose(total_size, 1.0) and total_size > 0:
        sizes = [s / total_size for s in sizes]

    fig, ax = plt.subplots(figsize=figsize)
    colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))

    wedges, texts, autotexts = ax.pie(sizes, autopct=autopct, startangle=startangle, colors=colors,
                                      wedgeprops=dict(width=0.4, edgecolor='w'))

    for autotext in autotexts:
        autotext.set_color('black')

    ax.legend(wedges, labels,
              title="Assets",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    ax.set_title(title)
    ax.axis('equal')
    plt.show()


# --- 3. Function to Download Historical Data ---

def download_historical_prices(tickers, start_date, end_date):
    """
    Downloads historical 'Adj Close' price data from Yahoo Finance for a given period.
    Returns a DataFrame with dates as index and ticker prices as columns.
    """
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


# --- 4. Function to Calculate Portfolio Returns and Sharpe Ratio ---

def calculate_portfolio_returns_and_sharpe(prices_df, specific_etf_allocation, risk_free_rate_annual):
    """
    Calculates total cumulative return, annualized cumulative return,
    and Annualized Sharpe Ratio for a portfolio.
    """
    portfolio_tickers = list(specific_etf_allocation.keys())
    available_prices = prices_df[portfolio_tickers].dropna(axis=0, how='any')

    if available_prices.empty or len(available_prices) < 2:
        print(f"Not enough valid historical price data for portfolio {portfolio_tickers}.")
        return None, None, None, None # Also return None for portfolio_cumulative_growth_indexed

    daily_returns_assets = available_prices.pct_change().dropna()

    if daily_returns_assets.empty:
        print("Could not calculate daily returns for assets in the portfolio.")
        return None, None, None, None

    weights_series = pd.Series(specific_etf_allocation).reindex(daily_returns_assets.columns).fillna(0)
    if weights_series.sum() == 0:
        print("All weights are zero after reindexing. Cannot calculate portfolio returns.")
        return None, None, None, None
    weights_series = weights_series / weights_series.sum()

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

    # Return the daily indexed growth data for Excel saving
    portfolio_cumulative_growth_indexed = portfolio_cumulative_growth * 100 # Index to 100

    return total_cumulative_return, annualized_cumulative_return, sharpe_ratio, portfolio_cumulative_growth_indexed


# --- Main Execution Logic ---
if __name__ == "__main__":
    try:
        import openpyxl
    except ImportError:
        print("The 'openpyxl' library is required to save data to Excel.")
        print("Please install it by running: pip install openpyxl")
        exit()

    print("--- Portfolio Analysis and Returns Calculation ---")

    # Define the fixed historical analysis period for returns and Sharpe Ratio
    analysis_start_date = datetime(2023, 1, 1).date()
    analysis_end_date = datetime(2024, 12, 31).date()

    # Download all necessary historical data once for the full period, including risk-free rate
    all_historical_data = download_historical_prices(all_unique_tickers, analysis_start_date, analysis_end_date)

    if all_historical_data.empty:
        print("\nFailed to download essential historical data. Please check your internet connection, ticker symbols, and date range.")
        print("Exiting application.")
    else:
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

        while True:
            try:
                risk_level_input = input("\nEnter a risk level (2-9) to view its portfolio structure, returns, and Sharpe Ratio, or type 'exit' to quit: ").strip().lower()

                if risk_level_input == 'exit':
                    print("Exiting application.")
                    break

                risk_level = int(risk_level_input)

                if risk_level not in portfolio_data:
                    print(f"Invalid risk level. Please enter a number between {min(portfolio_data.keys())} and {max(portfolio_data.keys())}.")
                    continue

                selected_portfolio = portfolio_data[risk_level]
                category_allocation = selected_portfolio['category_allocation']
                specific_etf_allocation = selected_portfolio['specific_etf_allocation']

                print(f"\n--- Analyzing Portfolio for Risk Level {risk_level} ---")

                # --- 1. Plot Category Allocation ---
                plot_pie_chart_with_details(category_allocation, f'Portfolio Allocation by Category (Risk Level {risk_level})')

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
                                                        f'Detailed Allocation within {category} (Risk Level {risk_level})')
                        # For single asset categories, we just print the detail, no separate pie chart
                        elif len(allocation_dict) == 1:
                            etf, weight = list(allocation_dict.items())[0]
                            print(f"\n--- Detailed Allocation within {category} (Risk Level {risk_level}) Details ---")
                            print(f"  - {etf}: {weight*100:.2f}% (This ETF forms {weight/category_total_weight_in_portfolio*100:.2f}% of {category} category)")
                            print(f"Category '{category}' for Risk Level {risk_level} contains only {etf}. No detailed pie chart for single asset.")
                    else:
                        print(f"Category '{category}' has negligible allocation in this portfolio. Skipping detailed plot.")

                # --- 3. Display Specific ETF Allocation (Names and Percentages) ---
                print(f"\n--- Specific ETFs and Their Percentages for Risk Level {risk_level} ---")
                if specific_etf_allocation:
                    # Sort for consistent output
                    sorted_etfs = sorted(specific_etf_allocation.items(), key=lambda item: item[1], reverse=True)
                    for etf, weight in sorted_etfs:
                        print(f"  - {etf}: {weight*100:.2f}%")
                else:
                    print("No specific ETFs allocated in this portfolio.")

                # --- 4. Get and Display Last Available Prices ---
                etfs_to_get_price = list(specific_etf_allocation.keys())
                if etfs_to_get_price:
                    valid_etfs_for_price = [t for t in etfs_to_get_price if t in prices_for_portfolios.columns]
                    if valid_etfs_for_price:
                        last_prices = prices_for_portfolios[valid_etfs_for_price].iloc[-1]
                        print(f"\n--- Last Available Prices of Allocated ETFs (as of {last_prices.name.date()}) ---")
                        for etf, price in last_prices.items():
                            print(f"  {etf}: ${price:.2f}")
                    else:
                        print("\nNo valid ETF prices found in downloaded data for current price display.")
                else:
                    print("\nNo ETFs allocated in this portfolio to fetch current prices.")


                # --- 5. Calculate and Display Portfolio Returns & Sharpe Ratio ---
                print(f"\n--- Portfolio Performance ({analysis_start_date} to {analysis_end_date}) for Risk Level {risk_level} ---")
                
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
                    print("Could not calculate portfolio returns or Sharpe Ratio for this period.")

                # --- 6. Save Cumulative Return Data to Excel ---
                if portfolio_cumulative_growth_indexed is not None and not portfolio_cumulative_growth_indexed.empty:
                    excel_filename = f"portfolio_{risk_level}_cumulative_growth_{analysis_start_date}_to_{analysis_end_date}.xlsx"
                    try:
                        portfolio_cumulative_growth_indexed.name = 'Portfolio Value (Indexed to 100)'
                        portfolio_cumulative_growth_indexed.to_excel(excel_filename, index=True)
                        print(f"\nDaily indexed portfolio growth saved to '{excel_filename}' successfully.")
                    except Exception as e:
                        print(f"Error saving portfolio growth to Excel: {e}")
                else:
                    print("\nNo daily portfolio growth data to save to Excel.")


            except ValueError:
                print("Invalid input. Please enter an integer for the risk level.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print("Please check your internet connection, the data definitions, and the availability of historical data.")


