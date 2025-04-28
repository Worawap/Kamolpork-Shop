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

with st.form("cash_input_form"):
    st.markdown("<h3 style='color: #4CAF50;'>📝 กรอกจำนวนแบงค์และเหรียญ</h3>", unsafe_allow_html=True)

    counts = {}
    for label, value in cash_types:
        with st.container():
            cols = st.columns([2, 1, 1])
            with cols[0]:
                st.markdown(f"<div style='padding-top: 8px; font-size:18px; color: #333;'>{label}</div>", unsafe_allow_html=True)
            with cols[1]:
                count = st.number_input("", min_value=0, step=1, key=f"count_{value}")
                counts[value] = count

    submitted = st.form_submit_button("✅ คำนวณยอดเงิน")

if submitted:
    total_amount = sum([value * count for value, count in counts.items()])

    st.success(f"✅ ยอดเงินสดรวม: {total_amount:,.0f} บาท")

    def calculate_change(target, counts_available):
        change_counts = {}
        remaining = target
        available = counts_available.copy()

        for value in sorted(available.keys()):
            while available[value] > 0 and remaining >= value:
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

        st.markdown("<h3 style='color: #2196F3;'>📋 สรุปเงินสดที่ต้องส่งกลับบริษัท</h3>", unsafe_allow_html=True)
        st.dataframe(send_back_df, use_container_width=True)

        st.markdown("<h3 style='color: #9C27B0;'>📋 กรอกยอดเงินโอน และยอดเงินสดที่ได้รับจากระบบ POS</h3>", unsafe_allow_html=True)

        col_input1, col_input2 = st.columns(2)
        with col_input1:
            pos_cash = st.number_input("ยอดเงินสดที่ระบบ POS แจ้งมา", min_value=0, step=1)
        with col_input2:
            pos_transfer = st.number_input("ยอดเงินโอนที่ระบบ POS แจ้งมา", min_value=0, step=1)

        if st.button("📊 คำนวณสรุปยอด"):
            money_left_in_drawer = total_amount
            total_sale = money_left_in_drawer + sum([v * c for v, c in send_back.items()])
            cash_received = sum([v * send_back[v] for v in send_back]) - 4000
            cash_transfer = pos_transfer
            difference = (cash_received + cash_transfer) - total_sale

            summary = pd.DataFrame({
                "หัวข้อ": [
                    "ยอดส่งเงิน", "เงินเหลือในลิ้นชัก", "ยอดขายรวม", "เงินสดที่ได้รับ", "เงินโอน", "เงินทอน", "เงินขาด/เงินเกิน"
                ],
                "จำนวนเงิน": [
                    cash_received, money_left_in_drawer, total_sale, pos_cash, cash_transfer, 4000, difference
                ],
                "หน่วย": ["บาท"]*7
            })

            st.markdown("<h3 style='color: #795548;'>📑 สรุปผลการคำนวณ</h3>", unsafe_allow_html=True)
            st.dataframe(summary, use_container_width=True)

    if st.button("📂 บันทึกข้อมูลเป็นไฟล์ CSV"):
        today = datetime.date.today().strftime("%Y-%m-%d")
        filename = f"cash_report_{today}.csv"

        final_df = pd.concat([
            pd.DataFrame([{"ประเภท": "รวมเงินสดทั้งหมด", "จำนวน": total_amount}]),
            pd.DataFrame([{"ประเภท": "เงินทอน 4000 บาท", "จำนวน": 4000}]),
            pd.DataFrame([{"ประเภท": "ต้องส่งกลับ", "จำนวน": total_amount - 4000}]),
            pd.DataFrame([{"ประเภท": "-", "จำนวน": "-"}]),
            send_back_df
        ])

        final_df.to_csv(filename, index=False, encoding='utf-8-sig')
        st.success(f"📂 บันทึกไฟล์เรียบร้อย: {filename}")

    else:
        st.error("❌ ไม่สามารถจัดเงินทอนให้ครบ 4,000 บาทได้ กรุณาตรวจสอบจำนวนแบงค์/เหรียญอีกครั้ง!")
        st.stop()
