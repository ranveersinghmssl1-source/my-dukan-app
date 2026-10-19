import streamlit as st
import pandas as pd
import sqlite3

# ─── PAGE CONFIGURATION ───
st.set_page_config(page_title="Grahak Khata Portal", page_icon="🔐", layout="wide")

# ─── CUSTOM CSS FOR PROFESSIONAL CARD LOOK ───
st.markdown("""
    <style>
    .khata-card {
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 25px;
    }
    .khata-title { font-size: 18px; font-weight: bold; color: #555; }
    .khata-value { font-size: 36px; font-weight: bold; margin-top: 8px; }
    </style>
""", unsafe_allow_html=True)

# ─── DATABASE HANDLING WITH CONTEXT MANAGER ───
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

# initialize session state for login
if "cust_logged_phone" not in st.session_state:
    st.session_state.cust_logged_phone = ""

# ─── CUSTOMER INTERFACE ───
st.title("👤 Customer Self-Service Portal / ग्राहक पोर्टल")
st.write("अपना रजिस्टर्ड मोबाइल नंबर डालकर अपना उधार बैलेंस और शॉपिंग हिस्ट्री देखें।")
st.markdown("---")

# ─── LOGIN SCREEN (If not logged in) ───
if st.session_state.cust_logged_phone == "":
    col1, _ = st.columns([2, 2])
    with col1:
        login_phone = st.text_input("📲 Enter Registered Mobile Number / नंबर लिखें", key="customer_portal_input", placeholder="e.g. 9876543210").strip()
        login_btn = st.button("🔐 Login / लॉगिन करें", use_container_width=True, type="primary")

    if (login_btn or login_phone) and login_phone:
        cust_check = run_query("SELECT name FROM customers WHERE phone = ?", (login_phone,), fetch=True)
        if cust_check:
            st.session_state.cust_logged_phone = login_phone
            st.rerun()
        else:
            st.error("❌ Number not registered / यह नंबर पंजीकृत नहीं है!")

# ─── PORTAL DASHBOARD (If logged in) ───
else:
    current_phone = st.session_state.cust_logged_phone
    cust_check = run_query("SELECT name FROM customers WHERE phone = ?", (current_phone,), fetch=True)
    actual_name = cust_check[0][0] if cust_check else "Customer"

    # Top Header Welcome & Logout
    col_name, col_logout = st.columns([4, 1])
    with col_name:
        st.subheader(f"👋 Welcome / स्वागत है, {actual_name}!")
    with col_logout:
        if st.button("🚪 Logout / लॉगआउट", type="secondary", use_container_width=True):
            st.session_state.cust_logged_phone = ""
            st.rerun()

    st.markdown("##")

    # Fetch history and udhaar
    history = run_query("SELECT bill_no, total_amount, payment_mode, bill_date FROM bills WHERE customer_phone = ? ORDER BY bill_no DESC", (current_phone,), fetch=True)
    total_udhaar_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE customer_phone = ? AND payment_mode LIKE '%Udhaar%'", (current_phone,), fetch=True)
    total_udhaar = total_udhaar_raw[0][0] if total_udhaar_raw and total_udhaar_raw[0][0] is not None else 0.0

    # Professional Udhaar Status Card
    if total_udhaar > 0:
        st.markdown(
            f'<div class="khata-card" style="background-color: #FFF5F5; border: 1px solid #FEB2B2; border-left: 6px solid #E53E3E;">'
            f'<div class="khata-title" style="color: #9B2C2C;">⚠️ Total Pending Balance / कुल बकाया उधार</div>'
            f'<div class="khata-value" style="color: #C53030;">₹{total_udhaar:,.2f}</div>'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="khata-card" style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 6px solid #16A34A;">'
            f'<div class="khata-title" style="color: #14532D;">🎉 Balance Account Clear / खाता साफ़ है</div>'
            f'<div class="khata-value" style="color: #166534;">₹0.00</div>'
            f'</div>', 
            unsafe_allow_html=True
        )

    # Purchase History Table
    st.markdown("### 🛍️ Purchase History / पुरानी रसीदें")
    if history:
        df_history = pd.DataFrame(history, columns=["Bill No", "Amount (₹)", "Payment Mode", "Date & Time"])
        # Professional formatting for Table
        df_history["Amount (₹)"] = df_history["Amount (₹)"].map("₹{:,.2f}".format)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
    else:
        st.info("No purchase history found / कोई पुरानी रसीद उपलब्ध नहीं है।")
