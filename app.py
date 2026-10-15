import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ─── PAGE CONFIGURATION ───
st.set_page_config(page_title="My Dukan App Pro", page_icon="🛍️", layout="wide")

# ─── DATABASE INITIALIZATION (UPDATED WITH SUPPLIER & UNITS) ───
def init_db():
    conn = sqlite3.connect('dukan_ultimate_v1.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL)''')
    # Added supplier, unit_type, weight_kg to products
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
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('dukan_ultimate_v1.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        data = None
        if fetch:
            data = cursor.fetchall()
        conn.commit()
        return data
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None
    finally:
        conn.close()

# ─── LANGUAGE SELECTION ───
lang_choice = st.sidebar.selectbox("🌐 Choose Language / भाषा चुनें", ["English", "Hindi"])

# Fixed Menu Strings to avoid routing failures
standard_menu = ["dashboard", "billing", "inventory", "customers", "portal"]

if lang_choice == "Hindi":
    display_menu = ["📊 डैशबोर्ड", "🛒 बिलिंग काउंटर", "📦 स्टॉक गोदाम (Inventory)", "👥 ग्राहक खाता (Customers)", "🔐 ग्राहक लॉगिन पोर्टल"]
    _title = "🏬 मेरी दुकान PRO - डिजिटल स्टोर मैनेजमेंट"
else:
    display_menu = ["📊 Dashboard", "🛒 Billing Form", "📦 Inventory (Stock)", "👥 Customers Management", "🔐 Customer Login Portal"]
    _title = "🏬 My Dukan PRO - Digital Store Management"

# ─── SIDEBAR NAVIGATION FIXED ───
choice_display = st.sidebar.selectbox("Menu Navigation / मेनू चुनें", display_menu, key="main_navigation_bar")
choice_idx = display_menu.index(choice_display)
current_form = standard_menu[choice_idx]

st.title(_title)
st.markdown("---")

# ─── 1. DASHBOARD SCREEN ───
if current_form == "dashboard":
    if lang_choice == "Hindi":
        st.subheader("दुकान की लाइव कमाई और रिपोर्ट्स")
        l_sales, l_cash, l_udhaar = "💰 कुल बिक्री (नकद + उधार)", "💵 कुल प्राप्त नकद", "📉 कुल मार्केट उधार"
    else:
        st.subheader("Dukan Live Summary & Reports")
        l_sales, l_cash, l_udhaar = "💰 Total Sales (Cash + Balance)", "💵 Total Cash Received", "📉 Total Market Udhaar (Balance)"

    total_sales_raw = run_query("SELECT SUM(total_amount) FROM bills", fetch=True)
    total_sales = total_sales_raw[0][0] if total_sales_raw and total_sales_raw[0][0] is not None else 0.0
    
    cash_sales_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode = 'Cash'", fetch=True)
    cash_sales = cash_sales_raw[0][0] if cash_sales_raw and cash_sales_raw[0][0] is not None else 0.0
    
    udhaar_sales_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode = 'Udhaar (Balance)'", fetch=True)
    udhaar_sales = udhaar_sales_raw[0][0] if udhaar_sales_raw and udhaar_sales_raw[0][0] is not None else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(l_sales, f"₹{total_sales:,.2f}")
    col2.metric(l_cash, f"₹{cash_sales:,.2f}")
    col3.metric(l_udhaar, f"₹{udhaar_sales:,.2f}")

# ─── 2. BILLING SCREEN ───
elif current_form == "billing":
    st.subheader("Fast Billing Counter" if lang_choice == "English" else "फ़ास्ट बिलिंग काउंटर")
    
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

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        barcode_input = st.text_input("🔍 SCAN BARCODE HERE", key="bill_barcode").strip()
    with col_btn:
        st.write(""); st.write("")
        enter_pressed = st.button("↩️ Enter / आइटम जोड़ें")

    if "active_prod" not in st.session_state:
        st.session_state.active_prod = None

    if barcode_input and (enter_pressed or barcode_input != ""):
        res = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE barcode = ?", (barcode_input,), fetch=True)
        if res:
            st.session_state.active_prod = res[0]
        else:
            st.session_state.active_prod = None
            st.error("Barcode Not Found!")

    prod_list = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE stock > 0", fetch=True)
    
    if not prod_list:
        st.warning("Inventory empty!")
    else:
        if not st.session_state.active_prod:
            prod_dict = {p[1]: p for p in prod_list}
            search_prod = st.selectbox("Search/Select Product Name", list(prod_dict.keys()))
            st.session_state.active_prod = prod_dict[search_prod]
            
        p_id, p_name, current_price, available_stock, u_type, w_kg = st.session_state.active_prod
        st.info(f"🎯 Item: **{p_name}** | Price: ₹{current_price} | Stock: {available_stock} {u_type} ({w_kg} KG)")
        
        qty = st.number_input("Quantity", min_value=1, max_value=int(available_stock), value=1)
        total_price = current_price * qty
        st.markdown(f"### **Grand Total: ₹{total_price}**")
        
        pay_mode = st.radio("Payment Mode", ["Cash", "Udhaar (Balance)"], horizontal=True)
        
        disabled_btn = True if pay_mode == "Udhaar (Balance)" and c_name == "Walk-in" else False
        if st.button("🖨️ Generate Bill", disabled=disabled_btn):
            run_query("UPDATE products SET stock = ? WHERE product_id = ?", (available_stock - qty, p_id))
            run_query("INSERT INTO bills (customer_name, customer_phone, total_amount, payment_mode, bill_date) VALUES (?, ?, ?, ?, ?)", 
                      (c_name, c_phone, total_price, pay_mode, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            st.success("Bill Generated Successfully!")
            st.session_state.active_prod = None
            st.balloons()

# ─── 3. INVENTORY SCREEN (WITH SUPPLIER, UNIT & KG) ───
elif current_form == "inventory":
    st.subheader("Inventory Stock Room" if lang_choice == "English" else "इन्वेंट्री स्टॉक गोदाम")
    tab1, tab2 = st.tabs(["➕ Add Item / नया सामान", "📋 Stock Book / रजिस्टर"])
    
    with tab1:
        with st.form("inventory_form", clear_on_submit=True):
            p_barcode = st.text_input("Barcode Number")
            p_name = st.text_input("Product Name / सामान का नाम")
            p_supplier = st.text_input("Supplier Name / सप्लायर का नाम")
            
            col_u, col_k = st.columns(2)
            with col_u:
                p_unit = st.selectbox("Unit Type / यूनिट प्रकार", ["Pcs", "Packet", "Box", "Kg", "Litre"])
            with col_k:
                p_weight = st.number_input("Weight per unit (KG) / वजन (किग्रा)", min_value=0.0, step=0.01)
                
            p_price = st.number_input("Price per unit / कीमत", min_value=0.0)
            p_stock = st.number_input("Stock Qty / कुल मात्रा", min_value=1, step=1)
            
            if st.form_submit_button("Save Item / सुरक्षित करें"):
                if p_name and p_price > 0:
                    b_val = p_barcode if p_barcode else None
                    run_query("INSERT INTO products (barcode, name, supplier, unit_type, weight_kg, price, stock) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (b_val, p_name, p_supplier, p_unit, p_weight, p_price, p_stock))
                    st.success("Product successfully added!")
                    
    with tab2:
        data = run_query("SELECT barcode, name, supplier, unit_type, weight_kg, price, stock FROM products", fetch=True)
        if data:
            df_stock = pd.DataFrame(data, columns=["Barcode", "Item Name", "Supplier", "Unit", "Weight (KG)", "Price (₹)", "Stock Qty"])
            st.dataframe(df_stock, use_container_width=True)

# ─── 4. CUSTOMER SCREEN ───
elif current_form == "customers":
    st.subheader("Customer Database" if lang_choice == "English" else "ग्राहक बहीखाता रजिस्टर")
    with st.form("add_cust_form", clear_on_submit=True):
        c_name = st.text_input("Customer Name / ग्राहक का नाम")
        c_phone = st.text_input("Mobile Number / मोबाइल नंबर")
        if st.form_submit_button("Register Customer"):
            run_query("INSERT INTO customers (name, phone) VALUES (?, ?)", (c_name, c_phone))
            st.success("Registered successfully!")
    
    c_data = run_query("SELECT name, phone FROM customers", fetch=True)
    if c_data:
        st.dataframe(pd.DataFrame(c_data, columns=["Naam", "Mobile Number"]), use_container_width=True)

# ─── 5. CUSTOMER PORTAL (100% FIXED & TESTED) ───
elif current_form == "portal":
    st.subheader("Customer Login Portal" if lang_choice == "English" else "ग्राहक लॉगिन पोर्टल")
    c_phone = st.text_input("Enter your registered mobile number / अपना पंजीकृत मोबाइल नंबर दर्ज करें")
    
    if st.button("Login / लॉगिन करें"):
        cust_info = run_query("SELECT name FROM customers WHERE phone = ?", (c_phone,), fetch=True)
        if cust_info:
            c_name = cust_info[0][0]
            st.success(f"Welcome {c_name}!")
            bills = run_query("SELECT bill_no, total_amount, payment_mode, bill_date FROM bills WHERE customer_phone = ?", (c_phone,), fetch=True)
            if bills:
                df_bills = pd.DataFrame(bills, columns=["Bill No", "Amount (₹)", "Payment Mode", "Date"])
                st.dataframe(df_bills, use_container_width=True)
            else:
                st.info("No bills found for this customer.")
        else:
            st.error("Customer not found. Please register first.")
