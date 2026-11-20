import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="My Dukan PRO",
    page_icon="🏬",
    layout="wide"
)

# -------------------------------------------------
# CSS
# -------------------------------------------------

st.markdown("""
<style>

.main-card{
    background:#f8f9fa;
    padding:20px;
    border-radius:12px;
    border-left:5px solid #28a745;
}

div[data-testid="metric-container"]{
    background:white;
    border:1px solid #eaeaea;
    padding:15px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

DB_NAME = "dukan_pos.db"


def run_query(query, params=(), fetch=False):

    with sqlite3.connect(DB_NAME) as conn:

        cursor = conn.cursor()
        cursor.execute(query, params)

        if fetch:
            return cursor.fetchall()

        conn.commit()


def init_db():

    run_query("""
    CREATE TABLE IF NOT EXISTS customers(
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT UNIQUE
    )
    """)

    run_query("""
    CREATE TABLE IF NOT EXISTS products(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE,
        name TEXT,
        supplier TEXT,
        unit_type TEXT,
        weight_kg REAL,
        price REAL,
        stock REAL
    )
    """)

    run_query("""
    CREATE TABLE IF NOT EXISTS bills(
        bill_no INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_phone TEXT,
        total_amount REAL,
        payment_mode TEXT,
        bill_date TEXT
    )
    """)


init_db()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Billing",
        "Inventory",
        "Customers"
    ]
)

st.title("🏬 My Dukan PRO - Digital Store Management")

st.markdown("---")

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

if menu == "Dashboard":

    sales = run_query(
        "SELECT COALESCE(SUM(total_amount),0) FROM bills",
        fetch=True
    )[0][0]

    customers = run_query(
        "SELECT COUNT(*) FROM customers",
        fetch=True
    )[0][0]

    products = run_query(
        "SELECT COUNT(*) FROM products",
        fetch=True
    )[0][0]

    low_stock = run_query(
        "SELECT COUNT(*) FROM products WHERE stock < 10",
        fetch=True
    )[0][0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💰 Total Sales", f"₹{sales:,.2f}")
    c2.metric("👥 Customers", customers)
    c3.metric("📦 Products", products)
    c4.metric("⚠️ Low Stock", low_stock)

    st.markdown("---")

    st.subheader("Recent Bills")

    bills = run_query(
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

    if bills:

        df = pd.DataFrame(
            bills,
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

# -------------------------------------------------
# INVENTORY
# -------------------------------------------------

elif menu == "Inventory":

    st.subheader("📦 Inventory Management")

    with st.form("product_form"):

        col1, col2 = st.columns(2)

        with col1:

            barcode = st.text_input("Barcode")

            product_name = st.text_input(
                "Product Name"
            )

            supplier = st.text_input(
                "Supplier"
            )

        with col2:

            unit_type = st.selectbox(
                "Unit",
                ["PCS", "BOX", "KG"]
            )

            weight = st.number_input(
                "Weight KG",
                min_value=0.0,
                value=0.0
            )

            price = st.number_input(
                "Price ₹",
                min_value=0.0
            )

            stock = st.number_input(
                "Stock",
                min_value=0.0
            )

        submit = st.form_submit_button(
            "✅ Save Product"
        )

        if submit:

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
                VALUES
                (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    barcode,
                    product_name,
                    supplier,
                    unit_type,
                    weight,
                    price,
                    stock
                )
            )

            st.success("Product Saved")

    st.markdown("---")

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
                "Name",
                "Supplier",
                "Unit",
                "Weight",
                "Price",
                "Stock"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True
        )

# -------------------------------------------------
# CUSTOMERS
# -------------------------------------------------

elif menu == "Customers":

    st.subheader("👥 Customers Management")

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input(
            "Customer Name"
        )

    with col2:

        phone = st.text_input(
            "Mobile Number"
        )

    if st.button(
        "✅ Save Customer"
    ):

        run_query(
            """
            INSERT INTO customers
            (name, phone)
            VALUES (?, ?)
            """,
            (name, phone)
        )

        st.success("Customer Saved")

    st.markdown("---")

    data = run_query(
        """
        SELECT
        customer_id,
        name,
        phone
        FROM customers
        ORDER BY customer_id DESC
        """,
        fetch=True
    )

    if data:

        df = pd.DataFrame(
            data,
            columns=[
                "ID",
                "Name",
                "Phone"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True
        )

# -------------------------------------------------
# BILLING
# -------------------------------------------------

elif menu == "Billing":

    st.subheader("🛒 Billing Counter")

    customer_data = run_query(
        """
        SELECT name, phone
        FROM customers
        """,
        fetch=True
    )

    customers = ["Walk-in Customer"]

    for c in customer_data:
        customers.append(
            f"{c[0]} ({c[1]})"
        )

    selected_customer = st.selectbox(
        "Customer",
        customers
    )

    products = run_query(
        """
        SELECT
        product_id,
        name,
        price,
        stock,
        unit_type
        FROM products
        WHERE stock > 0
        """,
        fetch=True
    )

    if products:

        prod_dict = {
            p[1]: p for p in products
        }

        selected_product = st.selectbox(
            "Select Product",
            list(prod_dict.keys())
        )

        product = prod_dict[selected_product]

        pid = product[0]
        price = product[2]
        stock = product[3]
        unit = product[4]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Price",
            f"₹{price}"
        )

        col2.metric(
            "Available",
            f"{stock} {unit}"
        )

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=int(stock),
            value=1
        )

        total = qty * price

        st.markdown(
            f"""
            <div class='main-card'>
            <h2>Grand Total : ₹{total:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        payment = st.radio(
            "Payment Mode",
            ["Cash", "Udhaar"],
            horizontal=True
        )

        if st.button(
            "🖨️ Generate Bill"
        ):

            run_query(
                """
                UPDATE products
                SET stock = ?
                WHERE product_id = ?
                """,
                (
                    stock - qty,
                    pid
                )
            )

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
                    selected_customer,
                    "",
                    total                 payment,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            st.success(
                "✅ Bill Generated Successfully"
            )

            st.balloons()

    else:

        st.warning(
            "No Products Available"
        )
