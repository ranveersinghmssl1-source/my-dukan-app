import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ─── PAGE CONFIGURATION ───
st.set_page_config(page_title="My Dukan App Pro", page_icon="🛍️", layout="wide")

# ─── CUSTOM CSS FOR PROFESSIONAL LOOK ───
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #4CAF50;
    }
    .metric-title { font-size: 16px; color: #6c757d; font-weight: bold; }
    .metric-value { font-size: 28px; color: #212529; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# ─── DATABASE INITIALIZATION ───
def init_db():
    with sqlite3.connect('dukan_ultimate_v1.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            barcode TEXT UNIQUE,
                            name TEXT NOT NULL, 
                            supplier TEXT,
                            unit_type TEXT,
                            weight_kg REAL,
                            price REAL NOT NULL, 
                            stock INTEGER NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
                            bill_no INTEGER PRIMARY KEY AUTOINCREMENT,
                            customer_name TEXT, 
                            customer_phone TEXT,
                            total_amount REAL, 
                            payment_mode TEXT,
                            bill_date TEXT)''')
        conn.commit()

init_db()

def run_query(query, params=(), fetch=False):
    with sqlite3.connect('dukan_ultimate_v1.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return None
        except Exception as e:
            st.error(f"⚠️ Database Error: {e}")
            return None

# ─── LANGUAGE SELECTION ───
lang_choice = st.sidebar.selectbox("🌐 Choose Language / भाषा चुनें", ["English", "Hindi"])
standard_menu = ["dashboard", "billing", "inventory", "customers", "portal"]

if lang_choice == "Hindi":
    display_menu = ["📊 डैशबोर्ड", "🛒 बिलिंग काउंटर", "📦 स्टॉक गोदाम (Inventory)", "👥 ग्राहक खाता (Customers)", "🔐 ग्राहक लॉगिन पोर्टल"]
    _title = "🏬 मेरी दुकान PRO - डिजिटल स्टोर मैनेजमेंट"
else:
    display_menu = ["📊 Dashboard", "🛒 Billing Form", "📦 Inventory (Stock)", "👥 Customers Management", "🔐 Customer Login Portal"]
    _title = "🏬 My Dukan PRO - Digital Store Management"

# ─── SIDEBAR NAVIGATION ───
choice_display = st.sidebar.selectbox("Menu Navigation / मेनू चुनें", display_menu, key="main_navigation_bar")
choice_idx = display_menu.index(choice_display)
current_form = standard_menu[choice_idx]

st.title(_title)
st.markdown("---")

# ─── 1. DASHBOARD SCREEN ───
if current_form == "dashboard":
    if lang_choice == "Hindi":
        st.subheader("📊 दुकान की लाइव कमाई और रिपोर्ट्स")
        l_sales, l_cash, l_udhaar = "💰 कुल बिक्री (नकद + उधार)", "💵 कुल प्राप्त नकद", "📉 कुल मार्केट उधार"
    else:
        st.subheader("📊 Dukan Live Summary & Reports")
        l_sales, l_cash, l_udhaar = "💰 Total Sales (Cash + Balance)", "💵 Total Cash Received", "📉 Total Market Udhaar (Balance)"

    # Data Fetching
    t_sales = run_query("SELECT SUM(total_amount) FROM bills", fetch=True)[0][0] or 0.0
    c_sales = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode = 'Cash'", fetch=True)[0][0] or 0.0
    u_sales = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode LIKE '%Udhaar%'", fetch=True)[0][0] or 0.0
    
    # Modern UI UI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">{l_sales}</div><div class="metric-value">₹{t_sales:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card" style="border-left-color: #2196F3;"><div class="metric-title">{l_cash}</div><div class="metric-value">₹{c_sales:,.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card" style="border-left-color: #f44336;"><div class="metric-title">{l_udhaar}</div><div class="metric-value">₹{u_sales:,.2f}</div></div>', unsafe_allow_html=True)

    # Recent Transactions Table
    st.markdown("### 📋 Recent Transactions / हालिया बिक्री")
    recent_data = run_query("SELECT bill_no, customer_name, total_amount, payment_mode, bill_date FROM bills ORDER BY bill_no DESC LIMIT 5", fetch=True)
    if recent_data:
        df = pd.DataFrame(recent_data, columns=["Bill No", "Customer", "Amount", "Mode", "Date"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")

# ─── 2. BILLING SCREEN (AUTOMATIC BARCODE SEARCH) ───
elif current_form == "billing":
    st.subheader("🛒 Fast Billing Counter" if lang_choice == "English" else "🛒 फ़ास्ट बिलिंग काउंटर")
    
    # Customer Selection
    cust_list = run_query("SELECT name, phone FROM customers", fetch=True)
    cust_options = [f"{c[0]} ({c[1]})" for c in cust_list] if cust_list else []
    cust_options.insert(0, "Walk-in Customer" if lang_choice == "English" else "नया या अनजान ग्राहक")
    selected_cust_info = st.selectbox("Customer / ग्राहक चुनें", cust_options)
    
    if "(" in selected_cust_info:
        parts = selected_cust_info.split(" (")
        c_name = parts[0]
        c_phone = parts[1].replace(")", "")
    else:
        c_name = "Walk-in"
        c_phone = "0000000000"

    # 🎯 AUTOMATIC BARCODE INPUT BOX (बिना बटन के काम करेगा)
    barcode_input = st.text_input("🔍 SCAN BARCODE HERE / यहाँ बारकोड स्कैन करें", key="bill_barcode", autocomplete="off").strip()

    # बारकोड बॉक्स में कुछ भी लिखते ही या स्कैन होते ही यह कोड अपने आप बैकग्राउंड में एक्टिव हो जाएगा
    if barcode_input:
        res = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE barcode = ?", (barcode_input,), fetch=True)
        if res:
            # अगर डेटाबेस में बारकोड मिल गया, तो उसे session_state में सेव कर लें
            st.session_state.active_prod = res[0]
        else:
            st.session_state.active_prod = None
            st.error("❌ Barcode Not Found! / यह बारकोड इन्वेंट्री में नहीं मिला!")

    # अगर मैन्युअली भी सर्च करना हो तो बैकअप ऑप्शन
    prod_list = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE stock > 0", fetch=True)
    
    if not prod_list:
        st.warning("Inventory empty! Please add products first.")
    else:
        # अगर बारकोड से सामान नहीं मिला है, तभी मैन्युअल ड्रॉपडाउन दिखाएं
        if "active_prod" not in st.session_state or st.session_state.active_prod is None:
            prod_dict = {p[1]: p for p in prod_list}
            search_prod = st.selectbox("Or Search by Name / या नाम से चुनें", list(prod_dict.keys()))
            st.session_state.active_prod = prod_dict[search_prod]
            
        # सामान की जानकारी दिखाना
        if st.session_state.active_prod:
            p_id, p_name, current_price, available_stock, u_type, w_kg = st.session_state.active_prod
            st.info(f"🎯 Item Found: **{p_name}** | Price: ₹{current_price} | Stock: {available_stock} {u_type} ({w_kg} KG)")
            
            qty = st.number_input("Quantity / मात्रा", min_value=1, max_value=int(available_stock), value=1)
            total_price = current_price * qty
            st.markdown(f"### **Grand Total: ₹{total_price:,.2f}**")
            
            pay_mode = st.radio("Payment Mode", ["Cash", "Udhaar (Balance)"], horizontal=True)
            
            disabled_btn = True if pay_mode == "Udhaar (Balance)" and c_name == "Walk-in" else False
            if disabled_btn:
                st.warning("⚠️ Walk-in customers cannot take Udhaar. Please select a registered customer.")
                
            if st.button("🖨️ Generate Bill", disabled=disabled_btn, type="primary"):
                # स्टॉक कम करना और बिल सेव करना
                run_query("UPDATE products SET stock = ? WHERE product_id = ?", (available_stock - qty, p_id))
                run_query("INSERT INTO bills (customer_name, customer_phone, total_amount, payment_mode, bill_date) VALUES (?, ?, ?, ?, ?)", 
                          (c_name, c_phone, total_price, pay_mode, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                st.success("🎉 Bill Generated Successfully!")
                
                # अगले स्कैन के लिए बारकोड इनपुट और एक्टिव प्रोडक्ट को साफ़ करना
                st.session_state.active_prod = None
                st.balloons()

