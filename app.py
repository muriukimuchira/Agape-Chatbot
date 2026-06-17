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

# 2. Expanded Agape Enterprise Core Operational Database Matrix
AGAPE_DATABASE = {
    "nairobi to mombasa": {"standard": 1500, "vip": 3000, "times": ["08:00 AM", "10:00 PM"]},
    "nairobi to kisumu":  {"standard": 1200, "vip": 2500, "times": ["07:00 AM", "09:00 PM"]},
    "nairobi to eldoret": {"standard": 1000, "vip": 2000, "times": ["06:00 AM", "04:00 PM"]},
    "nairobi to nakuru":  {"standard": 600,   "vip": 1200, "times": ["06:00 AM", "02:00 PM"]},
    "nakuru to kisumu":   {"standard": 500,   "vip": 1000, "times": ["09:00 AM", "03:00 PM"]},
    "mombasa to kisumu":  {"standard": 2500, "vip": 4000, "times": ["05:00 PM"]},
    "nakuru to mombasa":  {"standard": 1800, "vip": 3200, "times": ["07:00 PM"]},
    "eldoret to mombasa": {"standard": 2200, "vip": 3800, "times": ["04:00 PM"]}
}

# 3. Initialize Conversation State Parameters (The Bot Memory)
if "messages" not in st.session_state:
    route_menu = (
        "👋 Welcome to **Agape Enterprise Automated Ticketing **!\n\n"
        "Please choose or type your preferred travel route from our active network below:\n\n"
        "• **Nairobi** ➔ Mombasa\n"
        "• **Nairobi** ➔ Kisumu\n"
        "• **Nairobi** ➔ Eldoret\n"
        "• **Nairobi** ➔ Nakuru\n"
        "• **Nakuru** ➔ Kisumu\n"
        "• **Mombasa** ➔ Kisumu\n"
        "• **Nakuru** ➔ Mombasa\n"
        "• **Eldoret** ➔ Mombasa\n\n"
        "👉 *Example format: 'Nairobi to Mombasa' or 'Nakuru to Kisumu'*"
    )
    st.session_state.messages = [{"role": "assistant", "content": route_menu}]

if "step" not in st.session_state:
    st.session_state.step = "COLLECT_ROUTE"  # Core tracking state machine

if "booking_data" not in st.session_state:
    st.session_state.booking_data = {
        "primary_name": None, "primary_id": None, "primary_phone": None,
        "route": None, "class": None, "time": None, "date": None,
        "passenger_count": 1, "extra_passengers_details": []
    }

# 4. Configure Basic Streamlit Page Framing
st.set_page_config(page_title="Agape Enterprise Portal", page_icon="🚌")
st.title("🚌 Agape Enterprise Customer Portal")
st.caption("Inquire about active routes, bus schedules, and direct pricing metrics instantly.")

# 5. Render Conversation History Bubbles
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Live State Workflow Engine Logic
if user_input := st.chat_input("Type your reply here..."):
    # Append user chat bubble
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    clean_input = user_input.strip().lower()
    bot_reply = ""

    # STATE 1: SMART ROUTE EXTRACTION
    if st.session_state.step == "COLLECT_ROUTE":
        matched_route = None
        for route in AGAPE_DATABASE.keys():
            # Check for the complete route phrase or individual component match pairs
            if route in clean_input or (route.split(" to ")[0] in clean_input and route.split(" to ")[1] in clean_input):
                matched_route = route
                break
        
        if matched_route:
            st.session_state.booking_data["route"] = matched_route
            st.session_state.step = "COLLECT_CLASS"
            bot_reply = f"Great! You chose the **{matched_route.title()}** route. Which class would you prefer?\n1. Standard Class\n2. Luxury VIP Class"
        else:
            bot_reply = "Sorry, we couldn't match that route. Please type an active path from our menu (e.g., *Nairobi to Eldoret*):"

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

    # STATE 3: TIME SELECTION -> NOW PROMPTS FOR PRIMARY BOOKER DETAILS NEXT
    elif st.session_state.step == "COLLECT_TIME":
        st.session_state.booking_data["time"] = user_input
        st.session_state.step = "COLLECT_PRIMARY_DETAILS"
        bot_reply = "Excellent. As the primary passenger and payer, please enter your details first in this exact format:\n**Full Name, National ID/Passport Number, Phone Number, Travel Date**\n\n*(e.g., John Mwangi, ID 12345678, 0712345678, 20 June 2026)*"

    # STATE 4: MAIN BOOKER DETAILS COLLECTION
    elif st.session_state.step == "COLLECT_PRIMARY_DETAILS":
        parts = [p.strip() for p in user_input.split(",")]
        if len(parts) >= 4:
            st.session_state.booking_data["primary_name"] = parts[0]
            st.session_state.booking_data["primary_id"] = parts[1]
            st.session_state.booking_data["primary_phone"] = parts[2]
            st.session_state.booking_data["date"] = parts[3]
            
            st.session_state.step = "COLLECT_COUNT"
            bot_reply = f"Thank you, {parts[0]}. How many passengers would you like to book for in total (including yourself)?"
        else:
            bot_reply = "Missing Information: Please ensure you provide all 4 fields separated by commas:\n**Full Name, ID, Phone, Travel Date**"

    # STATE 5: PASSENGER COUNT VALIDATION
    elif st.session_state.step == "COLLECT_COUNT":
        numbers = re.findall(r'\b\d+\b', clean_input)
        if numbers and int(numbers[0]) > 0:
            count = int(numbers[0])
            st.session_state.booking_data["passenger_count"] = count
            
            if count == 1:
                st.session_state.step = "CONFIRMATION"
                bot_reply = "Perfect. Generating your booking documentation now..."
                st.rerun()
            else:
                st.session_state.step = "ASK_EXTRA_DETAILS_CONSENT"
                bot_reply = f"You are booking for **{count} passengers** in total. Would you like to provide details for each additional passenger? (Yes/No)"
        else:
            bot_reply = "Data Validation Warning: Passenger count must be a positive whole number. Please enter a valid number (e.g., 2):"

    # STATE 6: EXTRA PASSENGER CONSENT CHECK
    elif st.session_state.step == "ASK_EXTRA_DETAILS_CONSENT":
        if "yes" in clean_input or "y" == clean_input:
            st.session_state.step = "COLLECT_EXTRA_DETAILS"
            st.session_state.current_extra_index = 2
            bot_reply = f"Please enter details for **Passenger 2** in this format:\n**Full Name, ID/Passport Number, Phone Number (Optional)**"
        else:
            st.session_state.step = "CONFIRMATION"
            bot_reply = "Understood. Compiling your configuration parameters..."
            st.rerun()

    # STATE 7: LOOP THROUGH EXTRA PASSENGERS
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
                st.session_state.step = "CONFIRMATION"
                bot_reply = "All additional passenger details logged! Compiling summary metrics..."
                st.rerun()
        else:
            bot_reply = "Missing Information: Please ensure you provide at least **Full Name, ID/Passport Number** separated by a comma."

    # STATE 8: GENERATE PRICING MATRIX SUMMARY AND VERIFY
    if st.session_state.step == "CONFIRMATION" and bot_reply in ["All additional passenger details logged! Compiling summary metrics...", "Understood. Compiling your configuration parameters...", "Perfect. Generating your booking documentation now..."]:
        route = st.session_state.booking_data["route"]
        travel_class = st.session_state.booking_data["class"]
        count = st.session_state.booking_data["passenger_count"]
        
        price_per_head = AGAPE_DATABASE[route][travel_class]
        total_fare = price_per_head * count
        class_title = "Luxury VIP Class" if travel_class == "vip" else "Standard Class"
        
        summary = (
            f"### 📋 Booking Summary\n\n"
            f"* **Name:** {st.session_state.booking_data['primary_name']}\n"
            f"* **Phone Number:** {st.session_state.booking_data['primary_phone']}\n"
            f"* **Route:** {route.title()}\n"
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
        bot_reply = summary

    elif st.session_state.step == "CONFIRMATION":
        if "yes" in clean_input or "correct" in clean_input or "y" == clean_input:
            bot_reply = "🎉 **Thank you. Your booking request has been recorded and will be processed by Agape Enterprise.**"
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}
        else:
            bot_reply = "Booking cancelled. System reset. Which route would you like to book? (e.g., Nairobi to Mombasa)"
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}

    # Render Bot Bubble response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})


