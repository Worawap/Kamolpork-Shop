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

    st.markdown("""
    <div style='text-align:center; padding-top:20px;'>
        <form action="" method="post">
            <input type="submit" value="✅ ไปหน้าเงินทอน" style='background-color:#4CAF50; color:white; padding:12px 36px; font-size:18px; border:none; border-radius:10px; cursor:pointer;'>
        </form>
    </div>
    """, unsafe_allow_html=True)

    if st.button("ไปหน้าเงินทอน", key="next_button", use_container_width=True):
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
    st.markdown("<h2 style='color: #4CAF50;'>💵 หน้ากรอกเงินทอน</h2>", unsafe_allow_html=True)

    change_df = pd.DataFrame({
        "ประเภท": [label for label, _ in cash_types],
        "เงินที่ออกหน้าแรก": [st.session_state["counts"].get(value, 0) for _, value in cash_types],
        "จำนวนที่ต้องเหลือ": [0 for _ in cash_types]
    })

    edited_change_df = st.data_editor(
        change_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="change_editor"
    )

    change_counts = dict(zip([value for _, value in cash_types], edited_change_df["จำนวนที่ต้องเหลือ"]))
    total_change = sum([value * count for value, count in change_counts.items()])

    st.markdown(f"<h4 style='color: #4CAF50;'>ยอดเงินทอนรวม: {total_change:,} / 4,000 บาท</h4>", unsafe_allow_html=True)

    if st.button("📋 สรุปผลเงินทอนและส่งเงิน"):
        if total_change != 4000:
            st.error("❌ เงินทอนไม่ครบ 4,000 บาท กรุณาตรวจสอบและปรับยอดให้พอดี!")
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
        total_amount = st.session_state.get("total_amount", 0)
        total_waste = st.session_state.get("waste_bills", 0)
        total_cancel = st.session_state.get("cancel_bills", 0)

        difference = ((cash_in_drawer - 4000) + total_waste + total_cancel) - pos_cash

        diff_color = "#4CAF50" if difference > 0 else ("#FF9800" if difference == 0 else "#F44336")
        diff_message = "ยอดเงินตรงเป๊ะ เยี่ยมมาก! 🎉" if difference == 0 else ("เงินเกินนิดหน่อยครับ" if difference > 0 else "เงินขาด กรุณาตรวจสอบ!")

        styled_summary = f"""
        <div style='padding:10px; background-color:{diff_color}; color:white; border-radius:8px; text-align:center;'>
            <h2>{diff_message}</h2>
            <p>ขาด/เกิน {difference:.2f} บาท</p>
        </div>
        """
        st.markdown("<h3 style='color: #E91E63;'>📢 สรุปยอดตรวจสอบ</h3>", unsafe_allow_html=True)
        st.markdown(styled_summary, unsafe_allow_html=True)
