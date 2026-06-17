import streamlit as st
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier

# Download necessary text parsing resources inside the cloud instance
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# 1. Operational Database Matrix
AGAPE_DATABASE = {
    "mombasa": {"standard": 1500, "vip": 3000, "times": ["08:00 AM", "10:00 PM"]},
    "kisumu":  {"standard": 1200, "vip": 2500, "times": ["07:00 AM", "09:00 PM"]},
    "nakuru":  {"standard": 600,   "vip": 1200, "times": ["06:00 AM", "02:00 PM"]}
}

# 2. Intent Classification Corpus Setup
training_corpus = [
    ("how much is a ticket to mombasa", "pricing_inquiry"),
    ("what are the prices for nakuru", "pricing_inquiry"),
    ("ticket rates to kisumu", "pricing_inquiry"),
    ("fare breakdown for luxury vip", "pricing_inquiry"),
    ("how much for 3 passengers", "pricing_inquiry"),
    ("hello", "greeting"), ("hi", "greeting")
]

STOP_WORDS = set(stopwords.words('english'))

def extract_features(text):
    tokens = word_tokenize(text.lower())
    cleaned = [w for w in tokens if w.isalnum() and w not in STOP_WORDS]
    return {word: True for word in cleaned}

vectorized_corpus = [(extract_features(text), intent) for text, intent in training_corpus]
intent_classifier = NaiveBayesClassifier.train(vectorized_corpus)

def parse_passenger_count(text):
    numbers = re.findall(r'\b\d+\b', text)
    if numbers:
        return max(1, int(numbers[0]))
    return 1

# 3. Streamlit UI Rendering Engine Canvas Layout
st.set_page_config(page_title="Agape Enterprise Portal", page_icon="🚌")
st.title("🚌 Agape Enterprise Customer Portal")
st.caption("Inquire about active routes, bus schedules, and direct pricing metrics instantly.")

# Create chat history state holder
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation blocks
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Act on live user string message input
if user_message := st.chat_input("Ask about ticket prices (e.g., '3 tickets to Mombasa VIP')"):
    with st.chat_message("user"):
        st.markdown(user_message)
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    clean_input = user_message.strip().lower()
    features = extract_features(clean_input)
    predicted_intent = intent_classifier.classify(features)
    
    # Process responses dynamically
    if predicted_intent == "greeting":
        bot_reply = "Hello! Welcome to Agape Enterprise. Which route's pricing or schedule can I assist you with today?"
    else:
        target_destination = None
        for city in AGAPE_DATABASE.keys():
            if city in clean_input:
                target_destination = city
                break
                
        if not target_destination:
            bot_reply = ("I am sorry, that route does not exist in our system at the moment. "
                         "Our active routes are Nairobi to Mombasa, Kisumu, and Nakuru.")
        else:
            travel_class = "vip" if ("vip" in clean_input or "luxury" in clean_input) else "standard"
            passenger_count = parse_passenger_count(clean_input)
            
            base_fare = AGAPE_DATABASE[target_destination][travel_class]
            total_fare = base_fare * passenger_count
            schedules = AGAPE_DATABASE[target_destination]["times"]
            class_label = "Luxury VIP Class" if travel_class == "vip" else "Standard Class"
            
            bot_reply = (
                f"### 🚌 Fare Breakdown\n\n"
                f"* **Route:** Nairobi to {target_destination.title()}\n"
                f"* **Class:** {class_label}\n"
                f"* **Price per Passenger:** KES {base_fare:,}\n"
                f"* **Passengers:** {passenger_count}\n\n"
                f"### **TOTAL AMOUNT PAYABLE: KES {total_fare:,}**\n\n"
                f"🕒 **Departure Times:** {', '.join(schedules)}."
            )
            
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
