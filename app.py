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
    

# ─── BILLING SCREEN ───

elif current_form == "billing":

    st.subheader("🛒 Fast Billing Counter")

    # Session Cart
    if "cart" not in st.session_state:
        st.session_state.cart = []

    # Customer Selection

    cust_list = run_query(
        "SELECT name, phone FROM customers",
        fetch=True
    )

    cust_options = ["Walk-in Customer"]

    if cust_list:
        cust_options += [
            f"{c[0]} ({c[1]})"
            for c in cust_list
        ]

    selected_customer = st.selectbox(
        "👤 Customer",
        cust_options
    )

    if "(" in selected_customer:

        parts = selected_customer.split(" (")

        c_name = parts[0]
        c_phone = parts[1].replace(")", "")

    else:

        c_name = "Walk-in"
        c_phone = "0000000000"

    st.markdown("---")

    # Product List

    products = run_query(
        """
        SELECT
            product_id,
            barcode,
            name,
            price,
            stock,
            unit_type
        FROM products
        WHERE stock > 0
        """,
        fetch=True
    )

    if not products:

        st.warning(
            "⚠️ Inventory Empty. Please Add Products."
        )

    else:

        product_dict = {
            p[2]: p
            for p in products
        }

        selected_product = st.selectbox(
            "📦 Select Product",
            list(product_dict.keys())
        )

        (
            p_id,
            barcode,
            p_name,
            price,
            stock,
            unit_type
        ) = product_dict[selected_product]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Price",
                f"₹{price:,.2f}"
            )

        with col2:
            st.metric(
                "Stock",
                f"{stock} {unit_type}"
            )

        with col3:
            st.metric(
                "Unit",
                unit_type
            )

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=int(stock),
            value=1
        )

        if st.button("➕ Add To Bill"):

            item_exists = False

            for item in st.session_state.cart:

                if item["product_id"] == p_id:

                    item["qty"] += qty
                    item["total"] = (
                        item["qty"]
                        * item["price"]
                    )

                    item_exists = True
                    break

            if not item_exists:

                st.session_state.cart.append(
                    {
                        "product_id": p_id,
                        "barcode": barcode,
                        "name": p_name,
                        "price": price,
                        "qty": qty,
                        "unit": unit_type,
                        "total": price * qty
                    }
                )

            st.success(
                f"{p_name} Added To Bill"
            )

            st.rerun()

    # Cart Items

    st.markdown("---")
    st.subheader("🧾 Current Bill")

    if st.session_state.cart:

        cart_df = pd.DataFrame(
            st.session_state.cart
        )

        st.dataframe(
            cart_df,
            use_container_width=True,
            hide_index=True
        )

        grand_total = sum(
            item["total"]
            for item in st.session_state.cart
        )

        st.markdown(
            f"""
            <div style="
            background:#16a34a;
            padding:20px;
            border-radius:15px;
            text-align:center;
            color:white;
            ">
                <h2>Grand Total</h2>
                <h1>₹ {grand_total:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        pay_mode = st.radio(
            "💳 Payment Mode",
            [
                "Cash",
                "Udhaar (Balance)"
            ],
            horizontal=True
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗑️ Clear Bill",
                use_container_width=True
            ):

                st.session_state.cart = []
                st.rerun()

        with col2:

            if st.button(
                "🖨️ Generate Final Bill",
                type="primary",
                use_container_width=True
            ):

                # Save Bill

           run_query(
                    """
                    INSERT INTO bills
                    (
                        customer_name,
                        customer_phone,
                        total_amount,
                        payment_mode,
                        bill_date
                    )
                    VALUES
                    (?, ?, ?, ?, ?)
                    """,
                    (
                        c_name,
                        c_phone,
                        grand_total,
                        pay_mode,
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                )

                # Update Stock

                for item in st.session_state.cart:

                    run_query(
                        """
                        UPDATE products
                        SET stock = stock - ?
                        WHERE product_id = ?
                        """,
                        (
                            item["qty"],
                            item["product_id"]
                        )
                    )

                st.success(
                    f"✅ Bill Generated Successfully | Total ₹{grand_total:,.2f}"
                )

                st.balloons()

                st.session_state.cart = []

                st.rerun()

    else:

        st.info(
            "No Products Added In Bill"
        )

elif current_form == "customers":

    st.subheader("👥 Customers Management")

    tab1, tab2 = st.tabs(["Add Customer", "Customer List"])

    with tab1:

        name = st.text_input("Customer Name")
        phone = st.text_input("Mobile Number")

        if st.button("Save Customer"):

            if name and phone:

                run_query(
                    "INSERT INTO customers (name, phone) VALUES (?, ?)",
                    (name, phone)
                )

                st.success("✅ Customer Added Successfully")

                st.rerun()

            else:

                st.warning(
                    "Please enter Name and Mobile Number"
                )

    with tab2:

        customers = run_query(
            "SELECT customer_id, name, phone FROM customers",
            fetch=True
        )

        if customers:

            df = pd.DataFrame(
                customers,
                columns=[
                    "ID",
                    "Name",
                    "Phone"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No Customers Found"
            )
         
elif current_form == "inventory":

    st.subheader("📦 Inventory Management")

    st.markdown("### ➕ Add New Product")

    with st.form("add_product_form"):

        barcode = st.text_input("Barcode")

        product_name = st.text_input("Product Name")

        unit_type = st.selectbox(
            "Unit Type",
            ["PCS", "BOX", "KG"]
        )

        weight_kg = st.number_input(
            "Weight (KG)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        price = st.number_input(
            "Selling Price (₹)",
            min_value=0.0,
            value=0.0
        )

        stock = st.number_input(
            "Stock Quantity",
            min_value=0,
            value=0,
            step=1
        )

        supplier = st.text_input("Supplier Name")

        submit_product = st.form_submit_button("✅ Add Product")

        if submit_product:

            if barcode and product_name:

                run_query(
                    """
                    INSERT INTO products
                    (
                        barcode,
                        name,
                        supplier,
                        unit_type,
                        weight_kg,
                        price,
                        stock
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        barcode,
                        product_name,
                        supplier,
                        unit_type,
                        weight_kg,
                        price,
                        stock
                    )
                )

                st.success("✅ Product Added Successfully")

            else:
                st.warning("Please Enter Barcode and Product Name")

    st.markdown("---")

    st.markdown("### 📋 Product Inventory")

    
