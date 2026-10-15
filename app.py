import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# ─── PAGE CONFIGURATION ───
st.set_page_config(page_title="My Dukan App Pro", page_icon="🛍️", layout="wide")

# ─── ONLINE CLOUD SQL CONNECTION ───
DB_HOST = "db.enzhtmepoqfyvxenamsx.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1234"  # <── Apna password agar alag ho toh theek kar lena
DB_PORT = "5432"

def init_db():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                            customer_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            product_id SERIAL PRIMARY KEY,
                            barcode TEXT UNIQUE,
                            name TEXT NOT NULL, 
                            supplier TEXT,
                            unit_type TEXT,
                            weight_kg REAL,
                            price REAL NOT NULL, 
                            stock INTEGER NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
                            bill_no SERIAL PRIMARY KEY,
                            customer_name TEXT, 
                            customer_phone TEXT,
                            total_amount REAL, 
                            payment_mode TEXT,
                            bill_date TEXT)''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        pass

init_db()

def run_query(query, params=(), fetch=False):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = None
        if fetch:
            data = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        return None

# ─── MASTER PASSWORD ───
MASTER_PASSWORD = "1234"

# ─── LANGUAGE SELECTION ───
lang_choice = st.sidebar.selectbox("🌐 Choose Language / भाषा चुनें", ["English", "Hindi"])
standard_menu = ["dashboard", "billing", "inventory", "customers"]

if lang_choice == "Hindi":
    display_menu = ["📊 डैशबोर्ड", "🛒 बिलिंग काउंटर", "📦 STOCK गोदाम", "👥 ग्राहक खाता"]
    _title = "🏬 मेरी दुकान PRO - डिजिटल स्टोर Management"
else:
    display_menu = ["📊 Dashboard", "🛒 Billing Form", "📦 Inventory (Stock)", "👥 Customers Management"]
    _title = "🏬 My Dukan PRO - Digital Store Management"

st.title(_title)
st.markdown("---")

# ─── SECURITY GLOBAL LOCK CHECK ───
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔒 Owner Lock Security / सुरक्षा लॉक")
    entered_pass = st.text_input("🔑 Enter Dukan Password / पासवर्ड दर्ज करें", type="password")
    if st.button("Unlock / खोलें"):
        if entered_pass == MASTER_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Wrong Password! / गलत पासवर्ड!")
else:
    if st.sidebar.button("🔒 Logout Owner"):
        st.session_state.authenticated = False
        st.rerun()

    choice_display = st.sidebar.selectbox("Menu Navigation / मेनू चुनें", display_menu)
    choice_idx = display_menu.index(choice_display)
    current_form = standard_menu[choice_idx]

    # ─── 1. DASHBOARD SCREEN ───
    if current_form == "dashboard":
        st.subheader("Dukan Live Summary & Reports" if lang_choice == "English" else "दुकान की लाइव कमाई और रिपोर्ट्स")
        total_sales_raw = run_query("SELECT SUM(total_amount) FROM bills", fetch=True)
        total_sales = total_sales_raw[0][0] if total_sales_raw and total_sales_raw[0][0] is not None else 0.0
        
        cash_sales_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode = 'Cash'", fetch=True)
        cash_sales = cash_sales_raw[0][0] if cash_sales_raw and cash_sales_raw[0][0] is not None else 0.0
        
        udhaar_sales_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE payment_mode = 'Udhaar (Balance)'", fetch=True)
        udhaar_sales = udhaar_sales_raw[0][0] if udhaar_sales_raw and udhaar_sales_raw[0][0] is not None else 0.0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Sales", f"₹{total_sales:,.2f}")
        col2.metric("💵 Cash Received", f"₹{cash_sales:,.2f}")
        col3.metric("📉 Market Udhaar", f"₹{udhaar_sales:,.2f}")

    # ─── 2. BILLING SCREEN ───
    elif current_form == "billing":
        st.subheader("Fast Billing Counter")
        cust_list = run_query("SELECT name, phone FROM customers", fetch=True)
        cust_options = [f"{c[0]} ({c[1]})" for c in cust_list] if cust_list else []
        cust_options.insert(0, "Walk-in Customer")
        selected_cust_info = st.selectbox("Customer / ग्राहक चुनें", cust_options)
        
        if " (" in selected_cust_info:
            parts = selected_cust_info.split(" (")
            c_name = parts[0]
            c_phone = parts[1].replace(")", "")
        else:
            c_name = "Walk-in"
            c_phone = "0000000000"

        col_input, col_btn = st.columns(2)
        with col_input:
            barcode_input = st.text_input("🔍 SCAN BARCODE HERE", key="bill_barcode").strip()
        with col_btn:
            st.write(""); st.write("")
            enter_pressed = st.button("↩️ Enter")

        if "active_prod" not in st.session_state:
            st.session_state.active_prod = None

        if barcode_input and (enter_pressed or barcode_input != ""):
            res = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE barcode = %s", (barcode_input,), fetch=True)
            if res and len(res) > 0:
                st.session_state.active_prod = res[0]
            else:
                st.session_state.active_prod = None
                st.error("Barcode Not Found!")

        prod_list = run_query("SELECT product_id, name, price, stock, unit_type, weight_kg FROM products WHERE stock > 0", fetch=True)
        
        if not prod_list:
            st.warning("Inventory empty! / स्टॉक खाली है।")
        else:
            if not st.session_state.active_prod:
                prod_dict = {f"{p[1]} (Price: {p[2]})": p for p in prod_list}
                search_prod = st.selectbox("Search/Select Product Name", list(prod_dict.keys()))
                st.session_state.active_prod = prod_dict[search_prod]
                
            p_id, p_name, current_price, available_stock, u_type, w_kg = st.session_state.active_prod
            st.info(f"🎯 Item: **{p_name}** | Price: ₹{current_price} | Stock: {available_stock} {u_type}")
            
            qty = st.number_input("Quantity", min_value=1, max_value=int(available_stock), value=1)
            total_price = current_price * qty
            st.markdown(f"### **Grand Total: ₹{total_price}**")
            
            pay_mode = st.radio("Payment Mode", ["Cash", "Udhaar (Balance)"], horizontal=True)
            disabled_btn = True if pay_mode == "Udhaar (Balance)" and c_name == "Walk-in" else False
            
            if disabled_btn:
                st.warning("⚠️ Registered Customer needed for Balance option.")
                
            if st.button("🖨️ Generate Bill", disabled=disabled_btn):
                run_query("UPDATE products SET stock = %s WHERE product_id = %s", (available_stock - qty, p_id))
                run_query("INSERT INTO bills (customer_name, customer_phone, total_amount, payment_mode, bill_date) VALUES (%s, %s, %s, %s, %s)", 
                          (c_name, c_phone, total_price, pay_mode, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                st.success("Bill Generated Successfully!")
                st.session_state.active_prod = None
                st.rerun()

    # ─── 3. INVENTORY SCREEN ───
    elif current_form == "inventory":
        st.subheader("Inventory Stock Room")
        tab1, tab2 = st.tabs(["➕ Add Item", "📋 Stock Book"])
        with tab1:
            with st.form("inventory_form", clear_on_submit=True):
                p_barcode = st.text_input("Barcode Number")
                p_name = st.text_input("Product Name")
                p_supplier = st.text_input("Supplier Name")
                p_unit = st.selectbox("Unit Type", ["Pcs", "Packet", "Box", "Kg"])
                p_weight = st.number_input("Weight (KG)", min_value=0.0, step=0.01)
                p_price = st.number_input("Price", min_value=0.0)
                p_stock = st.number_input("Stock Qty", min_value=1, step=1)
                if st.form_submit_button("Save Item"):
                    if p_name and p_price > 0:
                        run_query("INSERT INTO products (barcode, name, supplier, unit_type, weight_kg, price, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                  (p_barcode if p_barcode else None, p_name, p_supplier, p_unit, p_weight, p_price, p_stock))
                        st.success("Product successfully added!")
        with tab2:
            data = run_query("SELECT barcode, name, supplier, unit_type, weight_kg, price, stock FROM products", fetch=True)
            if data:
                st.dataframe(pd.DataFrame(data, columns=["Barcode", "Item Name", "Supplier", "Unit", "Weight (KG)", "Price (₹)", "Stock Qty"]), use_container_width=True)

    # ─── 4. CUSTOMER SCREEN (100% FIXED NO NESTING BLOCKS) ───
    elif current_form == "customers":
        st.subheader("Customer Database")
        st.write("##### ➕ Register New Customer / नया ग्राहक जोड़ें")
        c_name = st.text_input("Customer Name / ग्राहक का नाम")
        c_phone = st.text_input("Mobile Number / मोबाइल नंबर")
        if st.form_submit_button("Register Customer")
          
        
