import streamlit as st
import pandas as pd
import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="กรอกเงินสดหน้าร้าน", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B;'>ระบบกรอกเงินสดหน้าร้าน - ขายหมูหน้าร้าน</h1>
    <hr style='border:1px solid #FF4B4B;'>
""", unsafe_allow_html=True)

cash_types = [
    ("1,000 บาท", 1000),
    ("500 บาท", 500),
    ("100 บาท", 100),
    ("50 บาท", 50),
    ("20 บาท", 20),
    ("10 บาท (เหรียญ)", 10),
    ("5 บาท (เหรียญ)", 5),
    ("2 บาท (เหรียญ)", 2),
    ("1 บาท (เหรียญ)", 1)
]

initial_pork = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})
initial_package = pd.DataFrame({"No": [1], "เลขที่บิล": [""], "จำนวนเงิน": [0]})
initial_drink = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})
initial_waste = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})
initial_cancel = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})

if "pork_table" not in st.session_state:
    st.session_state["pork_table"] = initial_pork

if "package_table" not in st.session_state:
    st.session_state["package_table"] = initial_package

if "drink_table" not in st.session_state:
    st.session_state["drink_table"] = initial_drink

if "waste_table" not in st.session_state:
    st.session_state["waste_table"] = initial_waste

if "cancel_table" not in st.session_state:
    st.session_state["cancel_table"] = initial_cancel

if "next_page" not in st.session_state:
    st.session_state["next_page"] = False

if not st.session_state["next_page"]:
    st.markdown("<h3 style='color: #4CAF50;'>📝 กรอกจำนวนแบงค์และเหรียญ</h3>", unsafe_allow_html=True)

    with st.container():
        counts = {}
        for label, value in cash_types:
            counts[value] = st.number_input(f"{label}", min_value=0, step=1, key=f"cash_{value}")

    col1, col2 = st.columns(2)
    with col1:
        pos_cash_input = st.number_input("💵 เงินสดที่ได้รับ (จาก POS)", min_value=0, step=1)
    with col2:
        pos_transfer_input = st.number_input("🏦 เงินโอน (จาก POS)", min_value=0, step=1)

    def section(title, table_key):
        st.markdown(f"<h4 style='color: #4CAF50;'>{title}</h4>", unsafe_allow_html=True)
        st.session_state[table_key] = st.data_editor(
            st.session_state[table_key],
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key=f"{table_key}_editor",
            disabled=False
        )
        if not st.session_state[table_key].empty:
            total = st.session_state[table_key]["จำนวนเงิน"].sum()
        else:
            total = 0
        st.markdown(f"รวมยอด {title}: {total:,} บาท")
        return total

    pork_total = section("🥩 รายการหมูหมัก", "pork_table")
    package_total = section("📦 รายการถุง/สติ๊กเกอร์/ของแปรรูป/แหนม", "package_table")
    drink_total = section("🥤 รายการเครื่องดื่ม/เครื่องปรุง", "drink_table")
    waste_total = section("📦 บิลของเสีย", "waste_table")
    cancel_total = section("🧾 บิลยกเลิก", "cancel_table")

    total_amount = sum([value * count for value, count in counts.items()])
    pos_total = pos_cash_input + pos_transfer_input

    st.markdown(f"""
    <div style='padding:10px; background-color:#E0F7FA; color:#006064; border-radius:8px; text-align:center;'>
        <h4>💰 ยอดรวมแบงค์เหรียญ: {total_amount:,} บาท</h4>
        <h4>💳 ยอดขายรวม (เงินสด + โอน): {pos_total:,} บาท</h4>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; padding-top:10px;'>
        <button style='background-color:#4CAF50; color:white; padding:12px 32px; font-size:18px; border:none; border-radius:8px; cursor:pointer;'>✅ ไปหน้าเงินทอน</button>
    </div>
    """, unsafe_allow_html=True)

    if st.button("ไปหน้าเงินทอน", key="next_button"):
        st.session_state.update({
            "counts": counts,
            "total_amount": total_amount,
            "pos_cash": pos_cash_input,
            "pos_transfer": pos_transfer_input,
            "cash_in_drawer": total_amount,
            "pork_marinated": pork_total,
            "processed_goods": package_total,
            "drinks_seasoning": drink_total,
            "waste_bills": waste_total,
            "cancel_bills": cancel_total,
            "next_page": True
        })
else:
    st.markdown("""
        <h2 style='color: #4CAF50;'>💵 หน้ากรอกเงินทอน</h2>
        <p>กำลังเตรียมระบบเงินทอนให้พร้อมใช้งาน...</p>
    """, unsafe_allow_html=True)
