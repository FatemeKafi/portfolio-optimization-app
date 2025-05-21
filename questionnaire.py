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
