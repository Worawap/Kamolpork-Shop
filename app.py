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

# สร้าง DataFrame สำหรับ data_editor
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

if st.button("✅ คำนวณยอดเงินและสรุปผล"):
    counts = dict(zip([value for _, value in cash_types], edited_cash_df["จำนวน"]))
    total_amount = sum([value * count for value, count in counts.items()])

    st.success(f"✅ ยอดเงินสดรวม: {total_amount:,.0f} บาท")

    def calculate_change(target, counts_available):
        change_counts = {}
        remaining = target
        available = counts_available.copy()
        denominations = sorted(available.keys())

        for value in denominations:
            qty = min(available[value], remaining // value)
            if qty > 0:
                change_counts[value] = qty
                remaining -= qty * value
                available[value] -= qty

        if remaining > 0:
            for value in reversed(denominations):
                while available[value] > 0 and remaining > 0:
                    available[value] -= 1
                    change_counts[value] = change_counts.get(value, 0) + 1
                    remaining -= value

        if remaining == 0:
            return change_counts
        else:
            return None

    change_result = calculate_change(4000, counts)

    if change_result:
        st.success("💰 เงินทอนที่ต้องเหลือไว้ 4,000 บาท เรียบร้อยแล้ว")

        change_df = pd.DataFrame([
            {"ประเภท": f"{value} บาท", "จำนวนที่เหลือ": count}
            for value, count in change_result.items()
        ])
        st.dataframe(change_df, use_container_width=True)

        send_back = {}
        for value in counts:
            qty_after_change = counts[value] - change_result.get(value, 0)
            if qty_after_change > 0:
                send_back[value] = qty_after_change

        send_back_df = pd.DataFrame([
            {"ประเภท": f"{value} บาท", "จำนวนที่ต้องส่งกลับ": count}
            for value, count in send_back.items()
        ])

        st.markdown("<h3 style='color: #795548;'>📋 สรุปเงินสดที่ต้องส่งกลับบริษัท</h3>", unsafe_allow_html=True)
        st.dataframe(send_back_df, use_container_width=True)

        total_sale = pos_cash + pos_transfer
        total_real = total_amount
        difference = total_real - total_sale

        st.markdown("<h3 style='color: #E91E63;'>📢 สรุปยอดตรวจสอบ</h3>", unsafe_allow_html=True)
        summary_df = pd.DataFrame({
            "รายการ": ["ยอดขายจากระบบ POS", "ยอดเงินสดนับจริง", "เงินขาด/เกิน"],
            "จำนวนเงิน (บาท)": [total_sale, total_real, difference]
        })
        st.dataframe(summary_df, use_container_width=True)

    else:
        st.error("❌ ไม่สามารถจัดเงินทอนให้ครบ 4,000 บาทได้ กรุณาตรวจสอบจำนวนแบงค์/เหรียญอีกครั้ง!")
        st.stop()
