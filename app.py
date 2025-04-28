import streamlit as st
import pandas as pd
import datetime

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

st.markdown("<h3 style='color: #4CAF50;'>📝 กรอกจำนวนแบงค์และเหรียญ</h3>", unsafe_allow_html=True)

cash_df = pd.DataFrame({
    "ประเภท": [label for label, _ in cash_types],
    "จำนวน": [0 for _ in cash_types]
})

edited_cash_df = st.data_editor(
    cash_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed"
)

col_input1, col_input2 = st.columns(2)
with col_input1:
    pos_cash = st.number_input("💵 เงินสดที่ได้รับ (จาก POS)", min_value=0, step=1)
with col_input2:
    pos_transfer = st.number_input("🏦 เงินโอน (จาก POS)", min_value=0, step=1)

if st.button("✅ คำนวณยอดเงินและไปหน้าเงินทอน"):
    counts = dict(zip([value for _, value in cash_types], edited_cash_df["จำนวน"]))
    total_amount = sum([value * count for value, count in counts.items()])

    st.session_state["counts"] = counts
    st.session_state["total_amount"] = total_amount
    st.session_state["pos_cash"] = pos_cash
    st.session_state["pos_transfer"] = pos_transfer
    st.switch_page("เงินทอน")

if "counts" in st.session_state:
    st.markdown("<h3 style='color: #4CAF50;'>💰 ใส่ข้อมูลเงินทอนที่ต้องเหลือในลิ้นชัก</h3>", unsafe_allow_html=True)

    change_df = pd.DataFrame({
        "ประเภท": [label for label, _ in cash_types],
        "จำนวนที่ต้องเหลือ": [0 for _ in cash_types]
    })

    edited_change_df = st.data_editor(
        change_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    if st.button("📋 สรุปผลเงินทอนและส่งเงิน"):
        change_counts = dict(zip([value for _, value in cash_types], edited_change_df["จำนวนที่ต้องเหลือ"]))
        total_change = sum([value * count for value, count in change_counts.items()])

        if total_change > 4000:
            st.error("❌ เงินทอนเกิน 4,000 บาท กรุณาปรับยอดใหม่!")
            st.stop()

        send_back = {}
        for value in st.session_state["counts"]:
            qty_after_change = st.session_state["counts"][value] - change_counts.get(value, 0)
            if qty_after_change > 0:
                send_back[value] = qty_after_change

        send_back_df = pd.DataFrame([
            {"ประเภท": f"{value} บาท", "จำนวนที่ต้องส่งกลับ": count}
            for value, count in send_back.items()
        ])

        st.success("✅ สรุปผลเรียบร้อย!")

        st.markdown("<h3 style='color: #795548;'>📋 เงินสดที่ต้องส่งกลับบริษัท</h3>", unsafe_allow_html=True)
        st.dataframe(send_back_df, use_container_width=True)

        total_sale = st.session_state["pos_cash"] + st.session_state["pos_transfer"]
        total_real = st.session_state["total_amount"]
        difference = total_real - total_sale

        st.markdown("<h3 style='color: #E91E63;'>📢 สรุปยอดตรวจสอบ</h3>", unsafe_allow_html=True)
        summary_df = pd.DataFrame({
            "รายการ": ["ยอดขายจากระบบ POS", "ยอดเงินสดนับจริง", "เงินขาด/เกิน"],
            "จำนวนเงิน (บาท)": [total_sale, total_real, difference]
        })
        st.dataframe(summary_df, use_container_width=True)
