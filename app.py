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

    counts = dict(zip([value for _, value in cash_types], st.session_state["cash_editor"]["จำนวน"]))
    total_amount = sum([value * count for value, count in counts.items()])
    pos_total = pos_cash_input + pos_transfer_input

    st.markdown(f"""
    <div style='padding:10px; background-color:#E0F7FA; color:#006064; border-radius:8px; text-align:center;'>
        <h4>💰 ยอดรวมแบงค์เหรียญ: {total_amount:,} บาท</h4>
        <h4>💳 ยอดขายรวม (เงินสด + โอน): {pos_total:,} บาท</h4>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: #4CAF50;'>📦 บิลของเสีย</h4>", unsafe_allow_html=True)
    waste_bills = [st.number_input(f"ของเสีย {i+1}", min_value=0, step=1, key=f"waste_{i}") for i in range(5)]

    st.markdown("<h4 style='color: #4CAF50;'>🧾 บิลยกเลิก</h4>", unsafe_allow_html=True)
    cancel_bills = [st.number_input(f"บิลยกเลิก {i+1}", min_value=0, step=1, key=f"cancel_{i}") for i in range(5)]

    if st.button("✅ คำนวณยอดเงินและไปหน้าเงินทอน"):
        st.session_state.update({
            "counts": counts,
            "total_amount": total_amount,
            "pos_cash": pos_cash_input,
            "pos_transfer": pos_transfer_input,
            "cash_in_drawer": total_amount,
            "waste_bills": waste_bills,
            "cancel_bills": cancel_bills,
            "next_page": True
        })

else:
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

        pos_cash = st.session_state.get("pos_cash", 0)
        pos_transfer = st.session_state.get("pos_transfer", 0)
        cash_in_drawer = st.session_state.get("cash_in_drawer", 0)
        total_waste = sum(st.session_state.get("waste_bills", []))
        total_cancel = sum(st.session_state.get("cancel_bills", []))

        pos_total = pos_cash + pos_transfer

        difference = (cash_in_drawer - pos_cash) + total_waste + total_cancel

        st.markdown("<h3 style='color: #E91E63;'>📢 สรุปยอดตรวจสอบ</h3>", unsafe_allow_html=True)

        diff_color = "#4CAF50" if difference > 0 else ("#FF9800" if difference == 0 else "#F44336")
        diff_message = "ยอดเงินตรงเป๊ะ เยี่ยมมาก! 🎉" if difference == 0 else ("เงินเกินนิดหน่อยครับ" if difference > 0 else "เงินขาด กรุณาตรวจสอบ!")

        styled_summary = f"""
        <div style='padding:10px; background-color:{diff_color}; color:white; border-radius:8px; text-align:center;'>
            <h2>{diff_message}</h2>
            <p>ขาด/เกิน {difference:.2f} บาท</p>
        </div>
        """
        st.markdown(styled_summary, unsafe_allow_html=True)

        if abs(difference) > 500:
            components.html("""
            <audio autoplay>
              <source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg">
            </audio>
            """, height=0)

        summary_df = pd.DataFrame({
            "รายการ": [
                "ยอดส่งเงิน",
                "เงินเหลือไว้ในลิ้นชัก",
                "ยอดขายรวม",
                "เงินสดที่ได้รับ",
                "เงินโอน",
                "เงินทอน",
                "เงินขาด/เงินเกิน",
                "ของเสีย",
                "บิลยกเลิก",
            ],
            "จำนวนเงิน (บาท)": [
                cash_in_drawer - 4000,
                cash_in_drawer,
                pos_total,
                pos_cash,
                pos_transfer,
                4000,
                difference,
                total_waste,
                total_cancel
            ]
        })

        st.dataframe(summary_df, use_container_width=True)

        # Save to CSV
        today = datetime.date.today().strftime("%Y-%m-%d")
        filename = f"cashflow_{today}.csv"
        summary_df.to_csv(filename, index=False)
        st.success(f"บันทึกข้อมูลลงไฟล์ {filename} เรียบร้อยแล้ว!")
