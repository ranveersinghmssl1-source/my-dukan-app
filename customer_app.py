import streamlit as st
import pandas as pd
import sqlite3

# ─── PAGE CONFIGURATION ───
st.set_page_config(page_title="Grahak Khata Portal", page_icon="🔐", layout="wide")

def run_query(query, params=(), fetch=False):
    # Same database use karega jo dukan ka main software use kar raha hai
    conn = sqlite3.connect('dukan_final_perfect_v7.db')
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

# ─── CUSTOMER INTERFACE (NO SIDEBAR MENU, NO PASSWORD) ───
st.title("👤 Customer Self-Service Portal / ग्राहक पोर्टल")
st.write("Apna registered mobile number daalkar apna udhaar balance aur shopping history dekhein.")
st.markdown("---")

login_phone = st.text_input("📲 Enter Registered Mobile Number / नंबर लिखें", key="customer_portal_input").strip()
login_btn = st.button("🔐 Login / लॉगिन करें")

if login_btn and login_phone:
    st.session_state.cust_logged_phone = login_phone

if "cust_logged_phone" in st.session_state and st.session_state.cust_logged_phone != "":
    current_phone = st.session_state.cust_logged_phone
    cust_check = run_query("SELECT name FROM customers WHERE phone = ?", (current_phone,), fetch=True)
    
    if cust_check and len(cust_check) > 0:
        actual_name = cust_check[0][0]
        st.success(f"Welcome / स्वागत है, **{actual_name}**!")
        
        # Fetch history and udhaar
        history = run_query("SELECT bill_no, total_amount, payment_mode, bill_date FROM bills WHERE customer_phone = ? ORDER BY bill_no DESC", (current_phone,), fetch=True)
        total_udhaar_raw = run_query("SELECT SUM(total_amount) FROM bills WHERE customer_phone = ? AND payment_mode = 'Udhaar (Balance)'", (current_phone,), fetch=True)
        total_udhaar = total_udhaar_raw[0][0] if total_udhaar_raw and total_udhaar_raw[0][0] is not None else 0.0
        
        if total_udhaar > 0:
            st.error(f"⚠️ Pending Balance / कुल बकाया उधार: ₹{total_udhaar:,.2f}")
        else:
            st.success("🎉 Balance Account Clear: ₹0.00 / आपका कोई पैसा बाकी नहीं है।")
            
        if history:
            st.markdown("### 🛍️ Purchase History / पुरानी रसीदें")
            st.dataframe(pd.DataFrame(history, columns=["Bill No", "Amount (₹)", "Mode", "Date"]), use_container_width=True)
    else:
        st.error("Number not registered / यह नंबर पंजीकृत नहीं है!")
