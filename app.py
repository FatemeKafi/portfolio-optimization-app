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
    details_for_print = []

    for label, size in data_dict.items():
        if size > 0.001: # Only include if weight is more than 0.1%
            labels.append(label)
            sizes.append(size)
            details_for_print.append(f"  - {label}: {size*100:.2f}%")

    if not sizes:
        print(f"No significant data to plot for: {title}")
        return

    print(f"\n--- {title} Details ---")
    if details_for_print:
        print("\n".join(details_for_print))
    else:
        print("No significant allocations to display.")

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

        # Handle both multi-index and single-column DataFrames for 'Adj Close'/'Close'
        if 'Adj Close' in data.columns:
            price_data = data['Adj Close']
        elif 'Close' in data.columns:
            price_data = data['Close']
        else:
            if isinstance(data, pd.DataFrame) and len(data.columns) == 1:
                price_data = data.iloc[:, 0] # Assume the single column is the price
            elif isinstance(data, pd.Series): # Single ticker returns a Series
                price_data = data
            else:
                print(f"Could not find 'Adj Close' or 'Close' prices for {tickers}.")
                return pd.DataFrame()

        if isinstance(price_data, pd.Series): # Convert Series to DataFrame for consistent operations
            price_data = price_data.to_frame()

        price_data = price_data.dropna(axis=1, how='all') # Drop empty ticker columns
        price_data = price_data.dropna(axis=0, how='all') # Drop empty date rows

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
    # Filter prices_df to only include the ETFs in the current portfolio allocation
    # and drop any rows (dates) where any of these specific tickers have NaN prices
    available_prices = prices_df[portfolio_tickers].dropna(axis=0, how='any')

    if available_prices.empty or len(available_prices) < 2:
        print(f"Not enough valid historical price data for portfolio {portfolio_tickers}.")
        return None, None, None

    # Calculate daily returns for individual assets
    daily_returns_assets = available_prices.pct_change().dropna()

    if daily_returns_assets.empty:
        print("Could not calculate daily returns for assets in the portfolio.")
        return None, None, None

    # Ensure weights are aligned with daily_returns_assets columns
    # and normalize to 1 in case some tickers were dropped due to no data
    weights_series = pd.Series(specific_etf_allocation).reindex(daily_returns_assets.columns).fillna(0)
    if weights_series.sum() == 0:
        print("All weights are zero after reindexing. Cannot calculate portfolio returns.")
        return None, None, None
    weights_series = weights_series / weights_series.sum()

    # Calculate portfolio daily returns
    portfolio_daily_returns = (daily_returns_assets * weights_series).sum(axis=1)

    # Total Cumulative Return
    portfolio_cumulative_growth = (1 + portfolio_daily_returns).cumprod()
    total_cumulative_return = (portfolio_cumulative_growth.iloc[-1] - 1) * 100

    # Annualized Cumulative Return
    first_date_data = portfolio_cumulative_growth.index[0]
    last_date_data = portfolio_cumulative_growth.index[-1]
    time_delta_days = (last_date_data - first_date_data).days

    if time_delta_days > 0:
        num_years = time_delta_days / 365.25
        annualized_cumulative_return = ((1 + (total_cumulative_return / 100))**(1/num_years) - 1) * 100
    else:
        annualized_cumulative_return = total_cumulative_return # If only one day, annualization is not meaningful

    # Calculate Annualized Sharpe Ratio
    # Annualize portfolio daily returns (mean)
    mean_daily_portfolio_return = portfolio_daily_returns.mean()
    annualized_portfolio_return = (1 + mean_daily_portfolio_return)**252 - 1 # Assuming 252 trading days

    # Annualize portfolio daily standard deviation
    annualized_portfolio_std = portfolio_daily_returns.std() * np.sqrt(252)

    sharpe_ratio = None
    if annualized_portfolio_std > 1e-6: # Avoid division by zero or near-zero
        sharpe_ratio = (annualized_portfolio_return - risk_free_rate_annual) / annualized_portfolio_std
    else:
        print("Warning: Annualized portfolio standard deviation is zero or near zero. Sharpe Ratio not meaningful.")


    return total_cumulative_return, annualized_cumulative_return, sharpe_ratio


# --- Main Execution Logic ---
if __name__ == "__main__":
    # Check for openpyxl library explicitly needed for Excel export
    try:
        import openpyxl
    except ImportError:
        print("The 'openpyxl' library is required to save data to Excel.")
        print("Please install it by running: pip install openpyxl")
        exit() # Exit if openpyxl is not found

    print("--- Portfolio Analysis and Returns Calculation ---")

    # Define the fixed historical analysis period for returns and Sharpe Ratio
    analysis_start_date = datetime(2023, 1, 1).date()
    analysis_end_date = datetime(2024, 12, 31).date()

    # Download all necessary historical data once for the full period, including risk-free rate
    # This avoids re-downloading for every risk level
    all_historical_data = download_historical_prices(all_unique_tickers, analysis_start_date, analysis_end_date)

    if all_historical_data.empty:
        print("\nFailed to download essential historical data. Please check your internet connection, ticker symbols, and date range.")
        print("Exiting application.")
    else:
        # Extract risk-free rate
        risk_free_rate_annual = 0.0 # Default to 0 if ^IRX not found or has no data
        if '^IRX' in all_historical_data.columns:
            # ^IRX provides annual yield in percentage, convert to decimal for calculation
            rf_series = all_historical_data['^IRX'].dropna()
            if not rf_series.empty:
                # Average annual yield (e.g., 4.5% -> 0.045)
                risk_free_rate_annual = rf_series.mean() / 100.0
                print(f"\nAverage Annual Risk-Free Rate ({analysis_start_date} to {analysis_end_date}): {risk_free_rate_annual*100:.2f}%")
            else:
                print("Warning: No valid risk-free rate data (^IRX) for the specified period. Using 0 as risk-free rate for Sharpe calculation.")
        else:
            print("Warning: '^IRX' ticker not found in downloaded data. Using 0 as risk-free rate for Sharpe calculation.")

        # Remove '^IRX' column from the main data used for portfolio calculations
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

                # --- Plot Category Allocation with details ---
                print(f"\n--- Analyzing Portfolio for Risk Level {risk_level} ---")
                plot_pie_chart_with_details(category_allocation, f'Portfolio Allocation by Category (Risk Level {risk_level})')

                # --- Plot Specific ETF Allocation for each category (with details) ---
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
                        elif len(allocation_dict) == 1:
                            etf, weight = list(allocation_dict.items())[0]
                            print(f"\n--- Detailed Allocation within {category} (Risk Level {risk_level}) Details ---")
                            print(f"  - {etf}: {weight*100:.2f}% (This ETF forms {weight/category_total_weight_in_portfolio*100:.2f}% of {category} category)")
                            print(f"Category '{category}' for Risk Level {risk_level} contains only {etf}. No detailed pie chart for single asset.")
                    else:
                        print(f"Category '{category}' has negligible allocation in this portfolio. Skipping detailed plot.")

                # --- Get and Display Current Prices ---
                etfs_to_get_price = list(specific_etf_allocation.keys())
                if etfs_to_get_price:
                    # Filter for tickers that are actually in `prices_for_portfolios`
                    valid_etfs_for_price = [t for t in etfs_to_get_price if t in prices_for_portfolios.columns]
                    if valid_etfs_for_price:
                        # For current price, we use the last available price in `prices_for_portfolios`
                        # or could use yf.Ticker().info for truly live prices.
                        # For simplicity, we'll use the last available historical price from our downloaded data.
                        current_prices = prices_for_portfolios[valid_etfs_for_price].iloc[-1]
                        print("\n--- Last Available Prices of Allocated ETFs (from downloaded historical data) ---")
                        for etf, price in current_prices.items():
                            print(f"  {etf}: ${price:.2f}")
                    else:
                        print("\nNo valid ETF prices found in downloaded data for current price display.")
                else:
                    print("\nNo ETFs allocated in this portfolio to fetch current prices.")


                # --- Calculate and Display Portfolio Returns and Sharpe Ratio ---
                print(f"\n--- Portfolio Returns & Sharpe Ratio ({analysis_start_date} to {analysis_end_date}) for Risk Level {risk_level} ---")
                
                total_ret, annualized_ret, sharpe_ratio = calculate_portfolio_returns_and_sharpe(
                    prices_for_portfolios, specific_etf_allocation, risk_free_rate_annual
                )

                if total_ret is not None and annualized_ret is not None and sharpe_ratio is not None:
                    print(f"Total Cumulative Return: {total_ret:.2f}%")
                    print(f"Annualized Cumulative Return: {annualized_ret:.2f}%")
                    print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
                elif total_ret is not None and annualized_ret is not None: # Sharpe could be None if std_dev is 0
                     print(f"Total Cumulative Return: {total_ret:.2f}%")
                     print(f"Annualized Cumulative Return: {annualized_ret:.2f}%")
                     print("Sharpe Ratio could not be calculated (e.g., zero volatility or data issues).")
                else:
                    print("Could not calculate portfolio returns or Sharpe Ratio for this period.")

                # --- Save Cumulative Return Data to Excel (daily indexed values of this portfolio) ---
                # To save the daily indexed growth of the portfolio itself:
                portfolio_tickers_for_growth = list(specific_etf_allocation.keys())
                if portfolio_tickers_for_growth:
                    # Filter for actual available data
                    growth_prices = prices_for_portfolios[portfolio_tickers_for_growth].dropna(axis=0, how='any')

                    if not growth_prices.empty and len(growth_prices) >= 2:
                        growth_daily_returns_assets = growth_prices.pct_change().dropna()
                        if not growth_daily_returns_assets.empty:
                            growth_weights_series = pd.Series(specific_etf_allocation).reindex(growth_daily_returns_assets.columns).fillna(0)
                            if growth_weights_series.sum() > 0:
                                growth_weights_series = growth_weights_series / growth_weights_series.sum()
                                portfolio_daily_returns_for_growth = (growth_daily_returns_assets * growth_weights_series).sum(axis=1)
                                portfolio_cumulative_growth_indexed = (1 + portfolio_daily_returns_for_growth).cumprod().fillna(1) * 100

                                excel_filename = f"portfolio_{risk_level}_cumulative_growth_{analysis_start_date}_to_{analysis_end_date}.xlsx"
                                try:
                                    portfolio_cumulative_growth_indexed.name = 'Portfolio Value (Indexed to 100)'
                                    portfolio_cumulative_growth_indexed.to_excel(excel_filename, index=True)
                                    print(f"Daily indexed portfolio growth saved to '{excel_filename}' successfully.")
                                except Exception as e:
                                    print(f"Error saving portfolio growth to Excel: {e}")
                            else:
                                print("No valid weights for portfolio growth calculation.")
                        else:
                            print("Not enough daily returns data for portfolio growth calculation.")
                    else:
                        print("Not enough valid price data for portfolio growth calculation.")
                else:
                    print("No ETFs in this portfolio for growth calculation.")


            except ValueError:
                print("Invalid input. Please enter an integer for the risk level.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print("Please check your internet connection, the data definitions, and the availability of historical data.")
