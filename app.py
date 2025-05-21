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

# --- 2. Define the questions for the questionnaire ---
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

# --- 3. Show Questionnaire Function ---
def show_questionnaire():
    st.title("Investor Risk Tolerance Questionnaire")

    # جمع‌آوری امتیازات
    total_score = 0
    for qid, qdata in questions.items():
        answer = st.radio(qdata["question"], qdata["options"], key=qid)
        selected_index = qdata["options"].index(answer)
        total_score += qdata["scores"][selected_index]

    # ذخیره نتیجه امتیاز در session state
    if st.button("Submit"):
        st.session_state.total_score = total_score
        st.session_state.risk_level = calculate_risk_level(total_score)
        st.success(f"Your total score: {total_score}")
        st.experimental_rerun()

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
        total_score = st.session_state.total_score
        risk_level = st.session_state.risk_level

        st.write(f"Based on your score of {total_score}, your risk level is {risk_level}.")

        # دریافت تخصیص پرتفوی
        portfolio_data = get_portfolio_data(risk_level)

        # نمایش تخصیص‌ها (نمودار پی)
        plot_pie_chart_with_details(portfolio_data['category_allocation'], f'Portfolio Allocation (Risk Level {risk_level})')

        # نمایش عملکرد پرتفوی
        st.write("Portfolio returns and performance details will be displayed here.")

    else:
        st.warning("Please complete the questionnaire first.")

# --- 6. Get Portfolio Data Function ---
def get_portfolio_data(risk_level):
    portfolio_data = {
        2: {'category_allocation': {'Bond': 1.0, 'Equity': 0.0}, 'specific_etf_allocation': {'SUSB': 0.5, 'EAGG': 0.5}},
        3: {'category_allocation': {'Bond': 0.8, 'Equity': 0.2}, 'specific_etf_allocation': {'SUSB': 0.4, 'EAGG': 0.4, 'ESGV': 0.2}},
        4: {'category_allocation': {'Bond': 0.6, 'Equity': 0.4}, 'specific_etf_allocation': {'SUSB': 0.3, 'EAGG': 0.3, 'ESGV': 0.4}},
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
    return portfolio_data.get(risk_level, {'category_allocation': {}, 'specific_etf_allocation': {}})

# --- 7. Plot Pie Chart Function ---
import matplotlib.pyplot as plt
import numpy as np

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
    plt.show()

# --- Main Execution Logic ---
if __name__ == "__main__":
    if "total_score" not in st.session_state:
        show_questionnaire()
    else:
        show_portfolio()
