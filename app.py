import streamlit as st
import re
import nltk
import random
from datetime import date

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
        "👋 Welcome to **Agape Enterprise Automated Ticketing Portal**!\n\n"
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
    st.session_state.step = "COLLECT_ROUTE"

if "booking_data" not in st.session_state:
    st.session_state.booking_data = {
        "primary_name": None, "primary_id": None, "primary_phone": None,
        "route": None, "class": None, "time": None, "date": None,
        "passenger_count": 1, "extra_passengers_details": []
    }

# Helper function to generate standardized booking reference IDs
def generate_booking_id():
    serial = random.randint(100, 999)
    return f"AGP2026{serial}"

# 4. Configure Basic Streamlit Page Framing
st.set_page_config(page_title="Agape Enterprise Portal", page_icon="🚌")
st.title("🚌 Agape Enterprise Customer Portal")
st.caption("Inquire about active routes, bus schedules, and direct pricing metrics instantly.")

# 5. DYNAMIC SIDEBAR DATA COLLECTION PANEL
# Moving the state tracking logic outside the form handler ensures Streamlit processes clicks correctly
with st.sidebar:
    st.header("📋 Passenger Portal")
    
    if st.session_state.step == "COLLECT_PRIMARY_DETAILS":
        st.subheader("Main Booker Profile Form")
        st.info("Please fill out your details here on the left side menu to continue.")
        
        with st.form("primary_passenger_form", clear_on_submit=True):
            form_name = st.text_input("Full Names:")
            form_id = st.text_input("National ID/ Passport:")
            form_phone = st.text_input("Phone Number:")
            form_date = st.date_input("Travel Date:", min_value=date.today())
            submit_primary = st.form_submit_button("Submit Details")
            
            if submit_primary:
                if form_name.strip() and form_id.strip() and form_phone.strip():
                    st.session_state.booking_data["primary_name"] = form_name
                    st.session_state.booking_data["primary_id"] = form_id
                    st.session_state.booking_data["primary_phone"] = form_phone
                    st.session_state.booking_data["date"] = form_date.strftime("%d %B %Y")
                    
                    # Append user action to visible chat message list
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"📝 Submitted Primary Details:\n* Name: {form_name}\n* ID: {form_id}\n* Phone: {form_phone}\n* Date: {st.session_state.booking_data['date']}"
                    })
                    
                    # Force step advancement immediately
                    st.session_state.step = "COLLECT_COUNT"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"Thank you, {form_name}. Your info has been saved. **How many passengers are booking in total (including yourself)?** Please type the total number in the chat bar below."
                    })
                    st.rerun()
                else:
                    st.error("⚠️ All fields are required.")

    elif st.session_state.step == "COLLECT_EXTRA_DETAILS":
        current_idx = st.session_state.current_extra_index
        total_needed = st.session_state.booking_data["passenger_count"]
        
        st.subheader(f"Manifest: Passenger {current_idx} of {total_needed}")
        
        with st.form("extra_passenger_form", clear_on_submit=True):
            ext_name = st.text_input("Full Names:")
            ext_id = st.text_input("National ID/ Passport:")
            ext_phone = st.text_input("Phone Number (Optional):", value="N/A")
            submit_extra = st.form_submit_button(f"Save Passenger {current_idx}")
            
            if submit_extra:
                if ext_name.strip() and ext_id.strip():
                    st.session_state.booking_data["extra_passengers_details"].append({
                        "name": ext_name, "id": ext_id, "phone": ext_phone
                    })
                    
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"👥 Added Passenger {current_idx}:\n* Name: {ext_name}\n* ID: {ext_id}"
                    })
                    
                    if current_idx < total_needed:
                        st.session_state.current_extra_index += 1
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Logged Passenger {current_idx}. Please enter records for **Passenger {st.session_state.current_extra_index}** in the sidebar panel."
                        })
                    else:
                        st.session_state.step = "PROCESS_SUMMARY_INVOICE"
                    st.rerun()
                else:
                    st.error("⚠️ Name and ID/Passport are required.")
    else:
        st.write("Form panels initialize here dynamically when needed.")

# 6. Render Conversation History Bubbles
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Live State Workflow Engine Chat Logic
input_disabled = st.session_state.step in ["COLLECT_PRIMARY_DETAILS", "COLLECT_EXTRA_DETAILS"]
placeholder_msg = "⬅️ Use the form panel on the left sidebar..." if input_disabled else "Type your reply here..."

if user_input := st.chat_input(placeholder_msg, disabled=input_disabled):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    clean_input = user_input.strip().lower()
    bot_reply = ""

    # STATE 1: ROUTE EXTRACTION
    if st.session_state.step == "COLLECT_ROUTE":
        matched_route = None
        for route in AGAPE_DATABASE.keys():
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

    # STATE 3: TIME SELECTION -> TRIGGERS SIDEBAR UNLOCK
    elif st.session_state.step == "COLLECT_TIME":
        st.session_state.booking_data["time"] = user_input
        st.session_state.step = "COLLECT_PRIMARY_DETAILS"
        bot_reply = "Excellent. 📍 **Please look at the form on the left sidebar panel of your screen.** Enter your details there and click submit!"
        st.rerun()

    # STATE 4: PASSENGER COUNT VALIDATION
    elif st.session_state.step == "COLLECT_COUNT":
        numbers = re.findall(r'\b\d+\b', clean_input)
        if numbers and int(numbers[0]) > 0:
            count = int(numbers[0])
            st.session_state.booking_data["passenger_count"] = count
            
            if count == 1:
                st.session_state.step = "PROCESS_SUMMARY_INVOICE"
                st.rerun()
            else:
                st.session_state.step = "ASK_EXTRA_DETAILS_CONSENT"
                bot_reply = f"You are booking for **{count} passengers** in total. Would you like to provide details for each additional passenger? (Yes/No)"
        else:
            bot_reply = "Data Validation Warning: Please enter a valid number of passengers (e.g., 2):"

    # STATE 5: EXTRA PASSENGER CONSENT CHECK
    elif st.session_state.step == "ASK_EXTRA_DETAILS_CONSENT":
        if "yes" in clean_input or "y" == clean_input:
            st.session_state.step = "COLLECT_EXTRA_DETAILS"
            st.session_state.current_extra_index = 2
            bot_reply = "Understood. 📍 **Please check the sidebar form layout on the left** to fill out details for Passenger 2."
            st.rerun()
        else:
            st.session_state.step = "PROCESS_SUMMARY_INVOICE"
            st.rerun()

    # STATE 6: PROCESS FINAL CANCELLATION OR RESET CONFIRMATION
    elif st.session_state.step == "CONFIRMATION":
        if "yes" in clean_input or "correct" in clean_input or "y" == clean_input:
            route = st.session_state.booking_data["route"]
            travel_class = st.session_state.booking_data["class"]
            count = st.session_state.booking_data["passenger_count"]
            price_per_head = AGAPE_DATABASE[route][travel_class]
            total_fare = price_per_head * count
            class_title = "Luxury VIP Class" if travel_class == "vip" else "Standard Class"
            
            bot_reply = (
                f"### 🎉 BOOKING CONFIRMATION\n\n"
                f"**Booking ID:** {generate_booking_id()}\n\n"
                f"**Route:** {route.title()}\n"
                f"**Travel Class:** {class_title}\n"
                f"**Departure Time:** {st.session_state.booking_data['time']}\n"
                f"**Number of Passengers:** {count}\n\n"
                f"**Passenger 1:**\n"
                f"Name: {st.session_state.booking_data['primary_name']}\n"
                f"Phone: {st.session_state.booking_data['primary_phone']}\n"
                f"Preferred Time: {st.session_state.booking_data['time']}\n\n"
            )
            
            if st.session_state.booking_data["extra_passengers_details"]:
                for i, p in enumerate(st.session_state.booking_data["extra_passengers_details"], 2):
                    bot_reply += (
                        f"**Passenger {i}:**\n"
                        f"Name: {p['name']}\n"
                        f"Phone: {p['phone']}\n"
                        f"Preferred Time: {st.session_state.booking_data['time']}\n\n"
                    )
            
            bot_reply += (
                f"**Total Amount Paid:** KES {total_fare:,}\n\n"
                f"**Booking Status:** Confirmed"
            )
            
            # Full Reset
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}
        else:
            bot_reply = "Booking cancelled. System reset. Which route would you like to book? (e.g., Nairobi to Mombasa)"
            st.session_state.step = "COLLECT_ROUTE"
            st.session_state.booking_data = {"primary_name": None, "primary_id": None, "primary_phone": None, "route": None, "class": None, "time": None, "date": None, "passenger_count": 1, "extra_passengers_details": []}

    if bot_reply:
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# 8. ISOLATED SUMMARY COMPILER (Executes automatically when state reaches billing)
if st.session_state.step == "PROCESS_SUMMARY_INVOICE":
    route = st.session_state.booking_data["route"]
    travel_class = st.session_state.booking_data["class"]
    count = st.session_state.booking_data["passenger_count"]
    
    price_per_head = AGAPE_DATABASE[route][travel_class]
    total_fare = price_per_head * count
    class_title = "Luxury VIP Class" if travel_class == "vip" else "Standard Class"
    
    summary = (
        f"### 📋 Booking Summary Verification\n\n"
        f"* **Name:** {st.session_state.booking_data['primary_name']}\n"
        f"* **ID / Passport:** {st.session_state.booking_data['primary_id']}\n"
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
    
    st.session_state.step = "CONFIRMATION"
    with st.chat_message("assistant"):
        st.markdown(summary)
    st.session_state.messages.append({"role": "assistant", "content": summary})
    st.rerun()
