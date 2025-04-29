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

if "cash_editor" not in st.session_state:
    st.session_state["cash_editor"] = pd.DataFrame({
        "ประเภท": [label for label, _ in cash_types],
        "จำนวน": [0 for _ in cash_types]
    })

if "pork_table" not in st.session_state:
    st.session_state["pork_table"] = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})

if "package_table" not in st.session_state:
    st.session_state["package_table"] = pd.DataFrame({"No": [1], "เลขที่บิล": [""], "จำนวนเงิน": [0]})

if "drink_table" not in st.session_state:
    st.session_state["drink_table"] = pd.DataFrame({"No": [1], "รายการ": [""], "จำนวนเงิน": [0]})

if "waste_bills" not in st.session_state:
    st.session_state["waste_bills"] = [0 for _ in range(5)]

if "cancel_bills" not in st.session_state:
    st.session_state["cancel_bills"] = [0 for _ in range(5)]

if "next_page" not in st.session_state:
    st.session_state["next_page"] = False

if not st.session_state["next_page"]:
    st.markdown("<h3 style='color: #4CAF50;'>📝 กรอกจำนวนแบงค์และเหรียญ</h3>", unsafe_allow_html=True)

    edited_cash_df = st.data_editor(
        st.session_state["cash_editor"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="cash_editor_editor"
    )

    st.session_state["cash_editor"] = edited_cash_df

    col1, col2 = st.columns(2)
    with col1:
        pos_cash_input = st.number_input("💵 เงินสดที่ได้รับ (จาก POS)", min_value=0, step=1)
    with col2:
        pos_transfer_input = st.number_input("🏦 เงินโอน (จาก POS)", min_value=0, step=1)

    st.markdown("<h4 style='color: #4CAF50;'>🍖 รายการหมูหมัก</h4>", unsafe_allow_html=True)
    st.session_state["pork_table"] = st.data_editor(
        st.session_state["pork_table"],
        use_container_width=True,
        key="pork_table_editor"
    )

    pork_total = st.session_state["pork_table"]["จำนวนเงิน"].sum() if not st.session_state["pork_table"].empty else 0
    st.markdown(f"รวมยอดหมูหมัก: {pork_total} บาท")

    st.markdown("<h4 style='color: #4CAF50;'>📦 รายการถุง/สติ๊กเกอร์/ของแปรรูป/แหนม</h4>", unsafe_allow_html=True)
    st.session_state["package_table"] = st.data_editor(
        st.session_state["package_table"],
        use_container_width=True,
        key="package_table_editor"
    )

    package_total = st.session_state["package_table"]["จำนวนเงิน"].sum() if not st.session_state["package_table"].empty else 0
    st.markdown(f"รวมยอดถุง/ของแปรรูป/แหนม: {package_total} บาท")

    st.markdown("<h4 style='color: #4CAF50;'>🥤 รายการเครื่องดื่ม/เครื่องปรุง</h4>", unsafe_allow_html=True)
    st.session_state["drink_table"] = st.data_editor(
        st.session_state["drink_table"],
        use_container_width=True,
        key="drink_table_editor"
    )

    drink_total = st.session_state["drink_table"]["จำนวนเงิน"].sum() if not st.session_state["drink_table"].empty else 0
    st.markdown(f"รวมยอดเครื่องดื่ม/เครื่องปรุง: {drink_total} บาท")

    st.markdown("<h4 style='color: #4CAF50;'>📦 บิลของเสีย</h4>", unsafe_allow_html=True)
    waste_bills = [st.number_input(f"ของเสีย {i+1}", min_value=0, step=1, key=f"waste_{i}") for i in range(5)]

    st.markdown("<h4 style='color: #4CAF50;'>🧾 บิลยกเลิก</h4>", unsafe_allow_html=True)
    cancel_bills = [st.number_input(f"บิลยกเลิก {i+1}", min_value=0, step=1, key=f"cancel_{i}") for i in range(5)]

    counts = dict(zip([value for _, value in cash_types], st.session_state["cash_editor"]["จำนวน"]))
    total_amount = sum([value * count for value, count in counts.items()])
    pos_total = pos_cash_input + pos_transfer_input

    st.markdown(f"""
    <div style='padding:10px; background-color:#E0F7FA; color:#006064; border-radius:8px; text-align:center;'>
        <h4>💰 ยอดรวมแบงค์เหรียญ: {total_amount:,} บาท</h4>
        <h4>💳 ยอดขายรวม (เงินสด + โอน): {pos_total:,} บาท</h4>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ ไปหน้าเงินทอน"):
        st.session_state.update({
            "counts": counts,
            "total_amount": total_amount,
            "pos_cash": pos_cash_input,
            "pos_transfer": pos_transfer_input,
            "cash_in_drawer": total_amount,
            "pork_marinated": pork_total,
            "processed_goods": package_total,
            "drinks_seasoning": drink_total,
            "waste_bills": waste_bills,
            "cancel_bills": cancel_bills,
            "next_page": True
        })
