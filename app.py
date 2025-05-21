import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

# --- 1. Define Portfolio Data ---
portfolio_data = {
    2: {'category_allocation': {'Bond': 1.0, 'Equity': 0.0}, 'specific_etf_allocation': {'SUSB': 0.5, 'EAGG': 0.5}},
    3: {'category_allocation': {'Bond': 0.8, 'Equity': 0.2}, 'specific_etf_allocation': {'SUSB': 0.4, 'EAGG': 0.4, 'ESGV': 0.2}},
    4: {'category_allocation': {'Bond': 0.6, 'Equity': 0.4}, 'specific_etf_allocation': {'SUSB': 0.3, 'EAGG': 0.3, 'ESGV': 0.4}},
    5: {'category_allocation': {'Bond': 0.4, 'Equity': 0.6}, 'specific_etf_allocation': {'SUSB': 0.13, 'EAGG': 0.13, 'VCEB': 0.13, 'ESGV': 0.3, 'USSG': 0.3}},
    6: {'category_allocation': {'Bond': 0.2, 'Equity': 0.6, 'Real Estate': 0.2}, 'specific_etf_allocation': {'EAGG': 0.1, 'VCEB': 0.1, 'ESGV': 0.2, 'USSG': 0.2, 'ESGU': 0.2, 'XLRE': 0.1, 'SCHH': 0.1}},
    7: {'category_allocation': {'Equity': 0.7, 'Real Estate': 0.3}, 'specific_etf_allocation': {'ESGV': 0.23, 'USSG': 0.23, 'ESGU': 0.23, 'XLRE': 0.15, 'SCHH': 0.15}},
    8: {'category_allocation': {'Equity': 0.8, 'Real Estate': 0.2}, 'specific_etf_allocation': {'ESGV': 0.26, 'USSG': 0.27, 'ESGU': 0.27, 'XLRE': 0.1, 'SCHH': 0.1}},
    9: {'category_allocation': {'Equity': 0.9, 'Real Estate': 0.1}, 'specific_etf_allocation': {'ESGV': 0.3, 'USSG': 0.3, 'ESGU': 0.3, 'XLRE': 0.05, 'SCHH': 0.05}},
}

# --- 2. Define the questions for the questionnaire ---
questions = {
    1: {"question": "How old are you?", "options": ["Over 60", "45-60", "30-44", "Under 30"], "scores": [1, 2, 3, 4]},
    2: {"question": "What is your investment experience?", "options": ["No experience", "Some experience", "Strong background", "Experienced investor"], "scores": [1, 2, 3, 4]},
    3: {"question": "What is an ETF?", "options": ["I don’t know", "Only trades commodities", "Not traded on exchanges", "Traded on exchanges"], "scores": [1, 2, 3, 4]},
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

# --- 3. Show Questionnaire Function ---
def show_questionnaire():
    st.title("Investor Risk Tolerance Questionnaire")

    total_score = 0
    for qid, qdata in questions.items():
        answer = st.radio(qdata["question"], qdata["options"], key=qid)
        selected_index = qdata["options"].index(answer)
        total_score += qdata["scores"][selected_index]

    if st.button("Submit"):
        st.session_state.total_score = total_score
        st.session_state.risk_level = calculate_risk_level(total_score)
        st.session_state.page = "portfolio"  # Page transfer to portfolio
        st.experimental_rerun()  # Re-run the app to show the portfolio page

# --- 4. Calculate Risk Level Function ---
def calculate_risk_level(total_score):
    if 10 <= total_score <= 11:
        return 2  # Ultra Conservative
    elif 12 <= total_score <= 14:
        return 3  # Conservative
    elif 15 <= total_score <= 19:
        return 4  # Cautiously Moderate
    elif 20 <= total_score <= 24:
        return 5  # Moderate
    elif 25 <= total_score <= 29:
        return 6  # Moderate Growth
    elif 30 <= total_score <= 34:
        return 7  # Growth
    elif 35 <= total_score <= 38:
        return 8  # Opportunistic
    elif 39 <= total_score <= 40:
        return 9  # Aggressive Growth
    return None

# --- 5. Show Portfolio Function ---
def show_portfolio():
    st.title("Your Suggested Portfolio")

    if "total_score" in st.session_state:
        total_score = st.session_state.total_score  # امتیاز کاربر
        risk_level = st.session_state.risk_level  # سطح ریسک

        st.write(f"Based on your score of {total_score}, your risk level is {risk_level}.")

        # دریافت تخصیص پرتفوی بر اساس سطح ریسک
        portfolio_data = get_portfolio_data(risk_level)

        # نمایش تخصیص‌ها (نمودار پی)
        plot_pie_chart_with_details(portfolio_data['category_allocation'], f'Portfolio Allocation (Risk Level {risk_level})')

        # نمایش اطلاعات بازدهی و نسبت شارپ
        total_return, annualized_return, sharpe_ratio, _ = calculate_portfolio_returns_and_sharpe(
            prices_for_portfolios, portfolio_data['specific_etf_allocation'], risk_free_rate_annual
        )

        # نمایش نتایج
        st.write(f"Total Cumulative Return: {total_return:.2f}%")
        st.write(f"Annualized Return: {annualized_return:.2f}%")
        st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}" if sharpe_ratio is not None else "Sharpe Ratio could not be calculated.")

    else:
        st.warning("Please complete the questionnaire first.")

# --- 6. Get Portfolio Data Function ---
def get_portfolio_data(risk_level):
    return portfolio_data.get(risk_level, {'category_allocation': {}, 'specific_etf_allocation': {}})

# --- 7. Plot Pie Chart Function ---
def plot_pie_chart_with_details(data_dict, title, figsize=(9, 9), autopct='%1.1f%%', startangle=140):
    labels = []
    sizes = []
    for label, size in data_dict.items():
        if size > 0.001:
            labels.append(label)
            sizes.append(size)

    if not sizes:
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

    ax.legend(wedges, labels, title="Assets", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(title)
    ax.axis('equal')

    st.pyplot(fig)  # Display chart in Streamlit

# --- Main Execution Logic ---
if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "questionnaire"  # Default to questionnaire page
    
    if st.session_state.page == "questionnaire":
        show_questionnaire()  # Show questionnaire
    elif st.session_state.page == "portfolio":
        show_portfolio()  # Show portfolio
