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

# ─── DASHBOARD SCREEN ───

if current_form == "dashboard":

    st.subheader("📊 Business Dashboard")

    # SALES DATA

    t_sales = run_query(
        "SELECT COALESCE(SUM(total_amount),0) FROM bills",
        fetch=True
    )[0][0]

    c_sales = run_query(
        "SELECT COALESCE(SUM(total_amount),0) FROM bills WHERE payment_mode='Cash'",
        fetch=True
    )[0][0]

    u_sales = run_query(
        "SELECT COALESCE(SUM(total_amount),0) FROM bills WHERE payment_mode LIKE '%Udhaar%'",
        fetch=True
    )[0][0]

    total_products = run_query(
        "SELECT COUNT(*) FROM products",
        fetch=True
    )[0][0]

    total_customers = run_query(
        "SELECT COUNT(*) FROM customers",
        fetch=True
    )[0][0]

    low_stock = run_query(
        "SELECT COUNT(*) FROM products WHERE stock < 10",
        fetch=True
    )[0][0]

    # TOP METRICS

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "💰 Total Sales",
            f"₹{t_sales:,.2f}"
        )

    with c2:
        st.metric(
            "💵 Cash Sale",
            f"₹{c_sales:,.2f}"
        )

    with c3:
        st.metric(
            "📉 Udhaar",
            f"₹{u_sales:,.2f}"
        )

    with c4:
        st.metric(
            "📦 Products",
            total_products
        )

    with c5:
        st.metric(
            "👥 Customers",
            total_customers
        )

    st.markdown("---")

    # LOW STOCK ALERT

    if low_stock > 0:

        st.error(
            f"⚠️ {low_stock} Products Have Low Stock (Less Than 10)"
        )

    # RECENT SALES

    st.subheader("🧾 Recent Transactions")

    recent_data = run_query(
        """
        SELECT
        bill_no,
        customer_name,
        total_amount,
        payment_mode,
        bill_date
        FROM bills
        ORDER BY bill_no DESC
        LIMIT 10
        """,
        fetch=True
    )

    if recent_data:

        df = pd.DataFrame(
            recent_data,
            columns=[
                "Bill No",
                "Customer",
                "Amount",
                "Payment",
                "Date"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "No Transactions Found"
        )

    st.markdown("---")

    # LOW STOCK PRODUCTS

    st.subheader("📦 Low Stock Products")

    low_stock_items = run_query(
        """
        SELECT
        name,
        stock,
        unit_type
        FROM products
        WHERE stock < 10
        ORDER BY stock ASC
        """,
        fetch=True
    )

    if low_stock_items:

        low_df = pd.DataFrame(
            low_stock_items,
            columns=[
                "Product",
                "Stock",
                "Unit"
            ]
        )

        st.dataframe(
            low_df,
            use_container_width=True
        )

    else:

        st.success(
            "✅ All Products Have Sufficient Stock"
        )

# ─── 2. BILLING SCREEN (PROFESSIONAL VERSION) ───
elif current_form == "billing":

    st.subheader(
        "🛒 Fast Billing Counter"
        if lang_choice == "English"
        else "🛒 फ़ास्ट बिलिंग काउंटर"
    )

    # CUSTOMER SELECTION

    cust_list = run_query(
        "SELECT name, phone FROM customers",
        fetch=True
    )

    cust_options = (
        [f"{c[0]} ({c[1]})" for c in cust_list]
        if cust_list
        else []
    )

    cust_options.insert(
        0,
        "Walk-in Customer"
        if lang_choice == "English"
        else "नया ग्राहक"
    )

    selected_cust_info = st.selectbox(
        "Customer / ग्राहक चुनें",
        cust_options
    )

    if "(" in selected_cust_info:

        parts = selected_cust_info.split(" (")

        c_name = parts[0]
        c_phone = parts[1].replace(")", "")

    else:

        c_name = "Walk-in"
        c_phone = "0000000000"

    st.markdown("---")

    # BARCODE SCANNER

    barcode_input = st.text_input(
        "🔍 Scan Barcode",
        key="bill_barcode"
    ).strip()

    if barcode_input:

        res = run_query(
            """
            SELECT
            product_id,
            name,
            price,
            stock,
            unit_type,
            weight_kg
            FROM products
            WHERE barcode = ?
            """,
            (barcode_input,),
            fetch=True
        )

        if res:

            st.session_state.active_prod = res[0]

        else:

            st.session_state.active_prod = None

            st.error(
                "❌ Barcode Not Found"
            )

    # PRODUCT LIST

    prod_list = run_query(
        """
        SELECT
        product_id,
        name,
        price,
        stock,
        unit_type,
        weight_kg
        FROM products
        WHERE stock > 0
        """,
        fetch=True
    )

    if not prod_list:

        st.warning(
            "⚠️ Inventory empty. Please add products first."
        )

    else:

        if (
            "active_prod" not in st.session_state
            or st.session_state.active_prod is None
        ):

            prod_dict = {
                p[1]: p
                for p in prod_list
            }

            search_prod = st.selectbox(
                "Search Product",
                list(prod_dict.keys())
            )

            st.session_state.active_prod = (
                prod_dict[search_prod]
            )

        if st.session_state.active_prod:

            (
                p_id,
                p_name,
                current_price,
                available_stock,
                u_type,
                w_kg
            ) = st.session_state.active_prod

            # PRODUCT CARDS

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "📦 Product",
                    p_name
                )

            with c2:
                st.metric(
                    "💰 Price",
                    f"₹{current_price}"
                )

            with c3:
                st.metric(
                    "📊 Stock",
                    f"{available_stock} {u_type}"
                )

            qty = st.number_input(
                "Quantity",
                min_value=1,
                max_value=max(
                    1,
                    int(available_stock)
                ),
                value=1
            )

            total_price = qty * current_price

            # GRAND TOTAL CARD

            st.markdown(
                f"""
                <div style="
                background:#16a34a;
                padding:20px;
                border-radius:12px;
                text-align:center;
                color:white;
                margin-top:10px;">
                <h3>Grand Total</h3>
                <h1>₹{total_price:,.2f}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            pay_mode = st.radio(
                "Payment Mode",
                [
                    "Cash",
                    "Udhaar (Balance)"
                ],
                horizontal=True
            )

            disabled_btn = (
                pay_mode == "Udhaarance)"
                and c_name == "Walk-in"
            )

            if disabled_btn:

                st.warning(
                    "⚠️ Walk-in customer cannot use Udhaar"
                )

            if st.button(
                "🖨️ Generate Bill",
                disabled=disabled_btn,
                type="primary"
            ):

                # UPDATE STOCK

                run_query(
                    """
                    UPDATE products
                    SET stock = ?
                    WHERE product_id = ?
                    """,
                    (
                        available_stock - qty,
                        p_id
                    )
                )

                # SAVE BILL

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
                        total_price,
                        pay_mode,
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                )

                st.success(
                    "🎉 Bill Generated Successfully!"
                )

                st.session_state.active_prod = None

                st.balloons()

                st.rerun()
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
            else:
                st.warning("Please enter Name and Mobile Number")

    with tab2:
        customers = run_query(
            "SELECT customer_id, name, phone FROM customers",
            fetch=True
        )

        if customers:
            df = pd.DataFrame(
                customers,
                columns=["ID", "Name", "Phone"]
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

    products = run_query(
        """
        SELECT
            product_id,
            barcode,
            name,
            supplier,
            unit_type,
            weight_kg,
            price,
            stock
        FROM products
        ORDER BY product_id DESC
        """,
        fetch=True
    )

    if products:

        df = pd.DataFrame(
            products,
            columns=[
                "ID",
                "Barcode",
                "Product Name",
                "Supplier",
                "Unit",
                "Weight(KG)",
                "Price",
                "Stock"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:
        st.warning("No products available")
