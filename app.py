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

    with sqlite3.connect("dukan_ultimate_v1.db") as conn:

        cursor = conn.cursor()

        # Customers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL
        )
        """)
        cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    dashboard_access INTEGER DEFAULT 0,
    billing_access INTEGER DEFAULT 0,
    inventory_access INTEGER DEFAULT 0,
    customers_access INTEGER DEFAULT 0,
    portal_access INTEGER DEFAULT 0,
    users_access INTEGER DEFAULT 0
)
""")

        # Products Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT NOT NULL,
            supplier TEXT,
            unit_type TEXT,
            weight_kg REAL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """)

        # Bills Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_no INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            total_amount REAL,
            payment_mode TEXT,
            bill_date TEXT,
            sold_by TEXT
        )
        """)

        # Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """)

        # Default Admin User
        cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password, role)
        VALUES
        ('admin', 'admin123', 'Admin')
        """)

        conn.commit()


# Initialize Database

init_db()

def run_query(query, params=(), fetch=False):

    with sqlite3.connect("dukan_ultimate_v1.db") as conn:

        cursor = conn.cursor()

        try:

            cursor.execute(query, params)

            if fetch:
                return cursor.fetchall()

            conn.commit()

        except Exception as e:

            st.error(f"Database Error: {e}")

            return None


# LOGIN SYSTEM YAHA SE START HOGA

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 My Dukan PRO Login")

    username = st.text_input("USER ID")

    password = st.text_input(
        "PASSWORD",
        type="password"
    )

    if st.button("Login"):

        user = run_query(
            """
            SELECT username, role
            FROM users
            WHERE username = ?
            AND password = ?
            """,
            (username, password),
            fetch=True
        )

        if user:

            st.session_state.logged_in = True
            st.session_state.username = user[0][0]
            st.session_state.role = user[0][1]

            st.rerun()

        else:

            st.error(
                "Invalid Username / Password"
            )

    st.stop()

# ─── LANGUAGE SELECTION ───
lang_choice = st.sidebar.selectbox("🌐 Choose Language / भाषा चुनें", ["English", "Hindi"])
standard_menu = [
    "dashboard",
    "billing",
    "inventory",
    "customers",
    "portal",
    "users"
]

if lang_choice == "Hindi":

    display_menu = [
        "📊 डैशबोर्ड",
        "🛒 बिलिंग काउंटर",
        "📦 स्टॉक गोदाम (Inventory)",
        "👥 ग्राहक खाता (Customers)",
        "🔐 ग्राहक लॉगिन पोर्टल",
        "👤 यूजर अनुमति"
    ]

    _title = "🏬 मेरी दुकान PRO - डिजिटल स्टोर मैनेजमेंट"

else:

    display_menu = [
        "📊 Dashboard",
        "🛒 Billing Form",
        "📦 Inventory (Stock)",
        "👥 Customers Management",
        "🔐 Customer Login Portal",
        "👤 User Authorization"
    ]

    _title = "🏬 My Dukan PRO - Digital Store Management"
# ─── SIDEBAR NAVIGATION ───
choice_display = st.sidebar.selectbox("Menu Navigation / मेनू चुनें", display_menu, key="main_navigation_bar")
choice_idx = display_menu.index(choice_display)
current_form = standard_menu[choice_idx]
st.sidebar.markdown("---")

st.sidebar.success(
    f"👤 {st.session_state.username}"
)

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    st.session_state.pop(
        "username",
        None
    )

    st.session_state.pop(
        "role",
        None
    )

   

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
    

# ─── BILLING SCREEN MULTIPLE PRODUCTS ───

elif current_form == "billing":

    st.subheader("🛒 Fast Billing Counter")

    # Cart Session
    if "cart" not in st.session_state:
        st.session_state.cart = []

    # Customer Selection

    cust_list = run_query(
        "SELECT name, phone FROM customers",
        fetch=True
    )

    customer_options = ["Walk-in Customer"]

    if cust_list:

        customer_options += [
            f"{c[0]} ({c[1]})"
            for c in cust_list
        ]

    selected_customer = st.selectbox(
        "👤 Select Customer",
        customer_options
    )

    if "(" in selected_customer:

        parts = selected_customer.split(" (")

        c_name = parts[0]
        c_phone = parts[1].replace(")", "")

    else:

        c_name = "Walk-in"
        c_phone = "0000000000"

    st.markdown("---")

    # Product Loading

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

        st.warning("⚠️ No Products Available")

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
            st.metric("💰 Price", f"₹{price:,.2f}")

        with col2:
            st.metric("📊 Stock", f"{stock} {unit_type}")

        with col3:
            st.metric("📦 Product", p_name)

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=int(stock),
            value=1,
            key=f"qty_{p_id}"
        )

        # Add Product

        if st.button("➕ Add To Bill"):

            found = False

            for item in st.session_state.cart:

                if item["product_id"] == p_id:

                    item["qty"] += qty
                    item["total"] = (
                        item["qty"] * item["price"]
                    )

                    found = True
                    break

            if not found:

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
                f"✅ {p_name} Added To Bill"
            )

            st.rerun()

    # Show Cart

    st.markdown("---")
    st.subheader("🧾 Current Bill")

    if st.session_state.cart:

        cart_df = pd.DataFrame(
            st.session_state.cart
        )

        st.dataframe(
            cart_df[
                [
                    "barcode",
                    "name",
                    "price",
                    "qty",
                    "unit",
                    "total"
                ]
            ],
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
            color:white;
            text-align:center;">
            <h2>GRAND TOTAL</h2>
            <h1>₹ {grand_total:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        pay_mode = st.radio(
            "💳 Payment Mode",
            ["Cash", "Udhaar (Balance)"],
            horizontal=True
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "🗑️ Clear",
                use_container_width=True
            ):

                st.session_state.cart = []
                st.rerun()

        with c2:

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
elif current_form == "portal":

    st.subheader("🔐 Customer Portal")

    mobile = st.text_input(
        "Enter Mobile Number"
    )

    if st.button("View Account"):

        customer = run_query(
            """
            SELECT
            name,
            phone
            FROM customers
            WHERE phone = ?
            """,
            (mobile,),
            fetch=True
        )

        if customer:

            st.success(
                f"Customer : {customer[0][0]}"
            )

            bills = run_query(
                """
                SELECT
                bill_no,
                total_amount,
                payment_mode,
                bill_date
                FROM bills
                WHERE customer_phone = ?
                ORDER BY bill_no DESC
                """,
                (mobile,),
                fetch=True
            )

            if bills:

                df = pd.DataFrame(
                    bills,
                    columns=[
                        "Bill No",
                        "Amount",
                        "Payment",
                        "Date"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                total_purchase = df[
                    "Amount"
                ].sum()

                total_udhaar = df[
                    df["Payment"] ==
                    "Udhaar (Balance)"
                ]["Amount"].sum()

                total_cash = df[
                    df["Payment"] ==
                    "Cash"
                ]["Amount"].sum()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Total Purchase",
                        f"₹{total_purchase:,.2f}"
                    )

                with col2:
                    st.metric(
                        "Cash Paid",
                        f"₹{total_cash:,.2f}"
                    )

                with col3:
                    st.metric(
                        "Udhaar",
                        f"₹{total_udhaar:,.2f}"
                    )

            else:

                st.info(
                    "No Purchase History Found"
                )

        else:

            st.error(
                "Customer Not Found"
            )

# ─── USER AUTHORIZATION ───

elif current_form == "users":

    if st.session_state.get("role") != "Admin":

        st.error(
            "⛔ Only Admin Can Access This Page"
        )

    else:

        st.subheader("👤 User Authorization")

        username = st.text_input("User ID")

        password = st.text_input(
            "Password",
            type="password"
        )

        role = st.selectbox(
            "Role",
            [
                "Admin",
                "Operator",
                "Store",
                "Supervisor"
            ]
        )

        st.markdown("### Access Rights")

        dashboard_access = st.checkbox("Dashboard")
        billing_access = st.checkbox("Billing")
        inventory_access = st.checkbox("Inventory")
        customers_access = st.checkbox("Customers")
        portal_access = st.checkbox("Customer Portal")
        users_access = st.checkbox("User Authorization")

        if st.button("✅ Create User"):

    try:

        run_query(
            """
            INSERT INTO users
            (
                username,
                password,
                role,
                dashboard_access,
                billing_access,
                inventory_access,
                customers_access,
                portal_access,
                users_access
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                password,
                role,
                int(dashboard_access),
                int(billing_access),
                int(inventory_access),
                int(customers_access),
                int(portal_access),
                int(users_access)
            )
        )

        st.success("✅ User Created Successfully")

    except Exception as e:

        st.error(str(e))

        st.subheader("📋 Existing Users")

        users_data = run_query(
            """
            SELECT
                user_id,
                username,
                role,
                dashboard_access,
                billing_access,
                inventory_access,
                customers_access,
                portal_access,
                users_access
            FROM users
            ORDER BY user_id DESC
            """,
            fetch=True
        )

        if users_data:

            df = pd.DataFrame(
                users_data,
                columns=[
                    "ID",
                    "User Name",
                    "Role",
                    "Dashboard",
                    "Billing",
                    "Inventory",
                    "Customers",
                    "Portal",
                    "Users"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No Users Found"
            )
            st.markdown("---")
st.subheader("✏️ Edit / Delete User")

users_list = run_query(
    """
    SELECT
        user_id,
        username,
        role
    FROM users
    ORDER BY user_id
    """,
    fetch=True
)

if users_list:

    user_options = {
        f"{u[1]} ({u[2]})": u[0]
        for u in users_list
    }

    selected_user = st.selectbox(
        "Select User",
        list(user_options.keys())
    )

    selected_user_id = user_options[selected_user]

    c1, c2 = st.columns(2)

    with c1:

        if st.button("🗑️ Delete User"):

            run_query(
                """
                DELETE FROM users
                WHERE user_id = ?
                """,
                (selected_user_id,)
            )

            st.success(
                "✅ User Deleted Successfully"
            )

            st.rerun()

    with c2:

        new_role = st.selectbox(
            "Change Role",
            [
                "Admin",
                "Operator",
                "Store",
                "Supervisor"
            ],
            key="edit_role"
        )

        if st.button("✏️ Update Role"):

            run_query(
                """
                UPDATE users
                SET role = ?
                WHERE user_id = ?
                """,
                (
                    new_role,
                    selected_user_id
                )
            )

            st.success(
                "✅ Role Updated Successfully"
            )

            st.rerun()
