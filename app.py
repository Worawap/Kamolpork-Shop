
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="💵 กรอกเงินสดหน้าร้าน", layout="centered")

st.title("💵 ระบบกรอกเงินสดหน้าร้าน - ขายหมูหน้าร้าน")
st.markdown("---")

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
    st.subheader("🗓️ กรอกจำนวนแบงค์และเหรียญ")
    col1, col2, col3 = st.columns([2,1,1])

    counts = {}
    for label, value in cash_types:
        with col1:
            st.write(f"**{label}**")
        with col2:
            count = st.number_input(f"จำนวนนับได้ - {label}", min_value=0, step=1, key=f"count_{value}")
            counts[value] = count

    submitted = st.form_submit_button("🚀 คำนวณยอดเงิน")

if submitted:
    total_amount = sum([value * count for value, count in counts.items()])
    
    st.success(f"📈 ยอดเงินสดรวม: {total_amount:,.0f} บาท")

    def calculate_change(target, counts_available):
        change_counts = {}
        remaining = target

        for value in sorted(counts_available.keys()):
            max_use = min(counts_available[value], remaining // value)
            if max_use > 0:
                change_counts[value] = max_use
                remaining -= value * max_use

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

        st.subheader("📎 สรุปเงินสดที่ต้องส่งกลับบริษัท")
        st.dataframe(send_back_df, use_container_width=True)

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
            st.success(f"📎 บันทึกไฟล์เรียบร้อย: {filename}")

    else:
        st.error("❌ ไม่สามารถจัดเงินทอนให้ครบ 4,000 บาทได้ \nกรุณาตรวจสอบจำนวนแบงค์/เหรียญอีกครั้ง!")
        st.stop()
