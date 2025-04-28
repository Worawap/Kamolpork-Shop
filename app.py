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

if "next_page" not in st.session_state:
    st.session_state["next_page"] = False

if not st.session_state["next_page"]:
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

    col1, col2, col3 = st.columns(3)
    with col1:
        pos_cash = st.number_input("💵 เงินสดที่ได้รับ (จาก POS)", min_value=0, step=1)
    with col2:
        pos_transfer = st.number_input("🏦 เงินโอน (จาก POS)", min_value=0, step=1)
    with col3:
        cash_in_drawer = st.number_input("💼 เงินเหลือในลิ้นชักทั้งหมด", min_value=0, step=1)

    st.markdown("<h4 style='color: #4CAF50;'>📦 บิลของเสีย</h4>", unsafe_allow_html=True)
    waste_bills = [st.number_input(f"ของเสีย {i+1}", min_value=0, step=1, key=f"waste_{i}") for i in range(5)]

    st.markdown("<h4 style='color: #4CAF50;'>🧾 บิลยกเลิก</h4>", unsafe_allow_html=True)
    cancel_bills = [st.number_input(f"บิลยกเลิก {i+1}", min_value=0, step=1, key=f"cancel_{i}") for i in range(5)]

    if st.button("✅ คำนวณยอดเงินและไปหน้าเงินทอน"):
        counts = dict(zip([value for _, value in cash_types], edited_cash_df["จำนวน"]))
        total_amount = sum([value * count for value, count in counts.items()])

        st.session_state.update({
            "counts": counts,
            "total_amount": total_amount,
            "pos_cash": pos_cash,
            "pos_transfer": pos_transfer,
            "cash_in_drawer": cash_in_drawer,
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

        total_sale = st.session_state.get("pos_cash", 0) + st.session_state.get("pos_transfer", 0)
        total_real = st.session_state.get("total_amount", 0)
        total_waste = sum(st.session_state.get("waste_bills", []))
        total_cancel = sum(st.session_state.get("cancel_bills", []))

        difference = (st.session_state.get("cash_in_drawer", 0) - st.session_state.get("pos_cash", 0)) + total_waste + total_cancel

        st.markdown("<h3 style='color: #E91E63;'>📢 สรุปยอดตรวจสอบ</h3>", unsafe_allow_html=True)
        summary_df = pd.DataFrame({
            "รายการ": ["ยอดขายจากระบบ POS", "ยอดเงินสดนับจริง", "เงินขาด/เกิน"],
            "จำนวนเงิน (บาท)": [total_sale, total_real, difference]
        })
        st.dataframe(summary_df, use_container_width=True)
