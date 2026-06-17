import streamlit as st
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier

# 1. Essential Cloud Dependencies Downloader
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# 2. Official Agape Enterprise Core Operational Data
AGAPE_DATABASE = {
    "mombasa": {"standard": 1500, "vip": 3000, "times": ["08:00 AM", "10:00 PM"]},
    "kisumu":  {"standard": 1200, "vip": 2500, "times": ["07:00 AM", "09:00 PM"]},
    "nakuru":  {"standard": 600,   "vip": 1200, "times": ["06:00 AM", "02:00 PM"]}
}

# 3. Initialize Conversation State Parameters (The Bot Memory)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to Agape Enterprise! Which route would you like to book? (e.g., Mombasa, Kisumu, or Nakuru)"}]

if "step" not in st.session_state:
    st.session_state.step = "COLLECT_ROUTE"  # Core tracking state machine

if "booking_data" not in st.session_state:
    st.session_state.booking_data = {
        "primary_name": None, "primary_id": None, "primary_phone": None,
        "route": None, "class": None, "time": None, "date": None,
        "passenger_count": 1, "extra_passengers_details": []
    }

# 4. Render Conversation History Bubbles
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Live State Workflow Engine Logic
if user_input := st.chat_input("Type your reply here..."):
    # Append user chat bubble
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    clean_input = user_input.strip().lower()
    bot_reply = ""

    # STATE 1: ROUTE EXTRACTION
    if st.session_state.step == "COLLECT_ROUTE":
        matched_city = None
        for city in AGAPE_DATABASE.keys():
            if city in clean_input:
                matched_city = city
                break
        
        if matched_city:
            st.session_state.booking_data["route"] = matched_city
            st.session_state.step = "COLLECT_CLASS"
            bot_reply = f"Great! You chose Nairobi to **{matched_city.title()}**. Which class would you prefer?\n1. Standard Class\n2. Luxury VIP Class"
        else:
            bot_reply = "Sorry, that route does not exist. Our active routes are **Mombasa, Kisumu, and Nakuru**. Please enter a valid route:"

    # STATE 2: TRAVEL CLASS SELECTION
    elif st.session_state.step == "COLLECT_CLASS":
        if "vip" in clean_input or "luxury" in clean_input or "2" in clean_input:
            st.session_state.booking_data["class"] = "vip"
        else:
            st.session_state.booking_data["class"] = "standard"
            
        chosen_route = st.session_state.booking_data["route"]
        available_times = AGAPE_DATABASE[chosen_route]["times"]
        
        st.session_state.step = "COLLECT_TIME"
        bot_reply = f"Understood. For that route, what departure time do you prefer? Available options are:\n" + "\n".join([f"* {t}" for t in available_times])

    # STATE 3: TIME SELECTION
    elif st.session_state.step == "COLLECT_TIME":
        chosen_route = st.session_state.booking_data["route"]
        valid_times = [t.lower() for t in AGAPE_DATABASE[chosen_route]["times"]]
        
        # Simple match check or fall back to text given
        st.session_state.booking_data["time"] = user_input
        st.session_state.step = "COLLECT_COUNT"
        bot_reply = "How many passengers would you like to book for?"

    # STATE 4: PASSENGER COUNT VALIDATION
    elif st.session_state.step == "COLLECT_COUNT":
        numbers = re.findall(r'\b\d+\b', clean_input)
        if numbers and int(numbers[0]) > 0:
            count = int(numbers[0])
            st.session_state.booking_data["passenger_count"] = count
            
            if count == 1:
                st.session_state.step = "COLLECT_PRIMARY_DETAILS"
                bot_reply = "Please enter your personal details in this format:\n**Full Name, National ID/Passport Number, Phone Number, Travel Date**\n\n*(e.g., John Mwangi, ID 12345678, 0712345678, 20 June 2026)*"
            else:
                st.session_state.step = "ASK_EXTRA_DETAILS_CONSENT"
                bot_reply = f"You are booking for **{count} passengers**. Would you like to provide details for each additional passenger? (Yes/No)"
        else:
            bot_reply = "Data Validation Warning: Passenger count must be a positive whole number. Please enter a valid number (e.g., 2):"

    # STATE 5: EXTRA PASSENGER CONSENT CHECK
    elif st.session_state.step == "ASK_EXTRA_DETAILS_CONSENT":
        if "yes" in clean_input or "y" == clean_input:
            st.session_state.step = "COLLECT_EXTRA_DETAILS"
            st.session_state.current_extra_index = 2
            bot_reply = f"Please enter details for **Passenger 2** in this format:\n**Full Name, ID/Passport Number, Phone Number (Optional)**"
        else:
            st.session_state.step = "COLLECT_PRIMARY_DETAILS"
            bot_reply = "No problem. Let's get the main traveler details. Please enter your details in this format:\n**Full Name, National ID/Passport Number, Phone Number, Travel Date**\n\n*(e.g., John Mwangi, ID 12345678, 0712345678, 20 June 2026)*"

    # STATE 6: LOOP THROUGH EXTRA PASSENGERS
    elif st.session_state.step == "COLLECT_EXTRA_DETAILS":
        parts = [p.strip() for p in user_input.split(",")]
        if len(parts) >= 2:
            name = parts[0]
            id_no = parts[1]
            phone = parts[2] if len(parts) > 2 else "N/A"
            st.session_state.booking_data["extra_passengers_details"].append({"name": name, "id": id_no, "phone": phone})
            
            total_needed = st.session_state.booking_data["passenger_count"]
            current_idx = st.session_state.current_extra_index
            
            if current_idx < total_needed:
                st.session_state.current_extra_index += 1
                bot_reply = f"Got it. Please enter details for **Passenger {st.session_state.current_extra_index}**:\n**Full Name, ID/Passport Number, Phone Number (Optional)**"
            else:
                st.session_state.step = "COLLECT_PRIMARY_DETAILS"
                bot_reply = "All additional passenger logs recorded! Finally, please provide the **Main Booker's Details** in this format:\n**Full Name, National ID/Passport Number, Phone Number, Travel Date**"
        else:
            bot_reply = "Missing Information: Please ensure you provide at least **Full Name, ID/Passport Number** separated by a comma."

    # STATE 7: MAIN TRAVELER DETAILS & PRICING CALCULATION SUMMARY
    elif st.session_state.step == "COLLECT_PRIMARY_DETAILS":
        parts = [p.strip() for p in user_input.split(",")]
        if len(parts) >= 4:
            st.session_state.booking_data["primary_name"] = parts[0]
            st.session_state.booking_data["primary_id"] = parts[1]
            st.session_state.booking_data["primary_phone"] = parts[2]
            st.session_state.booking_data["date"] = parts[3]
            
            # Run Mathematical Formula: Total Fare = Ticket Price * Passenger Count
            route = st.session_state.booking_data["route"]
            travel_class = st.session_state.booking_data["class"]
            count = st.session_state.booking_data["passenger_count"]
            
            price_per_head = AGAPE_DATABASE[route][travel_class]
            total_fare = price_per_head * count
            class_title = "Luxury VIP Class" if travel_class == "vip" else "Standard Class"
            
            # Construct Final Summary
            summary = (
                f"### 📋 Booking Summary\n\n"
                f"* **Name:** {st.session_state.booking_data['primary_name']}\n"
                f"* **Phone Number:** {st.session_state.booking_data['primary_phone']}\n"
                f"* **Route:** Nairobi → {route.title()}\n"
                f"* **Travel Date:** {st.session_state.booking_data['date']}\n"
                f"* **Class:** {class_title}\n"
                f"* **Departure Time:** {st.session_state.booking_data['time']}\n"
                f"* **Number of Passengers:** {count}\n\n"
            )
            
            if st.session_state.booking_data["extra_passengers_details"]:
                summary += "👥 **Additional Passenger Manifest:**\n"
                for i, p in enumerate(st.session_state.booking_data["extra_passengers_details"], 2):
                    summary += f"- Pax {i}: {p['name']} (ID: {p['id']})\n"
                summary += "\n"
                
            summary += (
                f"### 💵 Fare Breakdown\n"
                f"* **Price per Passenger:** KES {price_per_head:,}\n"
                f"* **Passengers:** {count}\n"
                f"**TOTAL FARE:** KES {total_fare:,}\n\n"
                f"Please confirm that the above information is correct. (Yes/No)"
            )
            st.session_state.step = "CONFIRMATION"
            bot_reply = summary
        else:
            bot_reply = "Missing Information: Please ensure you provide all 4 fields separated by commas:\n**Full Name, ID, Phone, Travel Date**"

    # STATE 8: PROCESS FINAL CONFIRMATION
    elif st.session_state.step == "CONFIRMATION":
        if "yes" in clean_input or "correct" in clean_input or "y" == clean_input:
            bot_reply = "🎉 **Thank you. Your booking request has been recorded and will be processed by Agape Enterprise.**"
            # Reset session state parameters back to step 1
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}
        else:
            bot_reply = "Booking cancelled or system reset. Which route would you like to book? (Mombasa, Kisumu, or Nakuru)"
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}

    # Render Bot Bubble response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})


   
       
