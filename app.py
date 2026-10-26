from __future__ import annotations

from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

from it_buddy_core import (
    CATEGORIES,
    ISSUES,
    STATUSES,
    diagnose_issue,
    get_issues_by_category,
    load_records,
    make_record,
    save_records,
    search_knowledge_base,
    summarize_records,
    update_record_status,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "it_buddy_data.json"

st.set_page_config(
    page_title="IT Buddy | Smart IT Assistant",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A compact visual system: deep navy, blue, teal, and generous spacing.
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&display=swap');
      html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'IBM Plex Sans Thai', sans-serif;
      }
      .stApp { background: #f4f7fb; color: #15243b; }
      [data-testid="stHeader"] { background: rgba(244,247,251,0.92); }
      [data-testid="stSidebar"] { background: linear-gradient(180deg, #10233f 0%, #18365b 100%); }
      [data-testid="stSidebar"] * { color: #edf5ff !important; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #c6d8ed !important; }
      [data-testid="stSidebar"] label { color: #edf5ff !important; }
      .brand-chip { display:inline-block; padding: 6px 11px; border-radius: 999px; background:#dff7f3; color:#087e79; font-weight:700; font-size:0.78rem; letter-spacing:.04em; }
      .hero { padding: 27px 30px; border-radius: 22px; color: white; background: linear-gradient(115deg, #10233f 0%, #145f78 63%, #149b9b 100%); box-shadow: 0 12px 28px rgba(21, 55, 91, .14); margin-bottom: 22px; }
      .hero h1 { color:white; font-size: 2.15rem; font-weight:700; margin: 9px 0 6px 0; line-height:1.2; }
      .hero p { color:#d8edf7; margin:0; font-size:1rem; }
      .section-kicker { color:#128b91; font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:2px; }
      .soft-card { background:white; border:1px solid #e2eaf2; border-radius:16px; padding:18px 20px; box-shadow:0 5px 18px rgba(20,50,80,.04); }
      .metric-label { color:#728198; font-size:.88rem; margin-bottom:5px; }
      .metric-value { color:#15243b; font-size:1.85rem; font-weight:700; line-height:1.2; }
      .metric-note { color:#8593a7; font-size:.78rem; margin-top:5px; }
      .small-muted { color:#76859a; font-size:.86rem; }
      .result-title { color:#15243b; font-size:1.3rem; font-weight:700; margin-bottom:4px; }
      .priority-high { display:inline-block; background:#fff0ed; color:#b93826; padding:4px 10px; border-radius:99px; font-size:.82rem; font-weight:700; }
      .priority-medium { display:inline-block; background:#fff6df; color:#97630b; padding:4px 10px; border-radius:99px; font-size:.82rem; font-weight:700; }
      .priority-low { display:inline-block; background:#e6f7ef; color:#15734d; padding:4px 10px; border-radius:99px; font-size:.82rem; font-weight:700; }
      div[data-testid="stMetric"] { background:white; border:1px solid #e2eaf2; padding:16px 18px; border-radius:16px; box-shadow:0 5px 18px rgba(20,50,80,.035); }
      div[data-testid="stMetricLabel"] p { color:#728198; }
      .stButton button, .stFormSubmitButton button { border-radius:11px; font-weight:600; }
      div[data-testid="stForm"] { background:white; padding:18px; border-radius:16px; border:1px solid #e2eaf2; }
      .kb-bullet { margin: 6px 0; }
      .footer { color:#8190a4; font-size:.78rem; border-top:1px solid #dfe7f0; padding-top:14px; margin-top:30px; }
      .callout { border-left:4px solid #149b9b; background:#eaf8f7; border-radius:0 12px 12px 0; padding:12px 15px; color:#244957; }
      .danger-callout { border-left:4px solid #e16b55; background:#fff2ef; border-radius:0 12px 12px 0; padding:12px 15px; color:#78382e; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "it_buddy_page" not in st.session_state:
    st.session_state.it_buddy_page = "Dashboard"
if "latest_diagnosis" not in st.session_state:
    st.session_state.latest_diagnosis = None

records = load_records(DATA_FILE)

with st.sidebar:
    st.markdown("<div style='font-size:2rem;font-weight:700;line-height:1.1'>🛠️ IT Buddy</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:5px;color:#b5d3ec;font-size:.86rem'>SMART IT ASSISTANT · PYTHON PROJECT</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#355171;margin:20px 0 16px 0'>", unsafe_allow_html=True)
    nav_items = [
        ("Dashboard", "▦", "ภาพรวมระบบ"),
        ("Smart Diagnosis", "⌕", "วิเคราะห์ปัญหา"),
        ("Knowledge Base", "▤", "คลังวิธีแก้ปัญหา"),
        ("History", "◷", "ประวัติการวิเคราะห์"),
        ("About Project", "ⓘ", "เกี่ยวกับโครงงาน"),
    ]
    for page_key, icon, label in nav_items:
        if st.button(f"{icon}   {label}", key=f"nav_{page_key}", use_container_width=True,
                     type="primary" if st.session_state.it_buddy_page == page_key else "secondary"):
            st.session_state.it_buddy_page = page_key
            st.rerun()
    st.markdown("<hr style='border-color:#355171;margin:18px 0'>", unsafe_allow_html=True)
    summary = summarize_records(records)
    st.caption("WORKSPACE STATUS")
    st.markdown(f"**{summary['total']}** รายการในประวัติ")
    st.progress(summary["resolution_rate"] / 100 if summary["total"] else 0)
    st.markdown(f"<div style='font-size:.8rem;color:#b5d3ec'>อัตราปิดงาน {summary['resolution_rate']:.1f}%</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:22px;color:#b5d3ec;font-size:.75rem'>DEMO MODE · บันทึกในไฟล์ JSON</div>", unsafe_allow_html=True)

page = st.session_state.it_buddy_page


def render_hero(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='hero'><span class='brand-chip'>{kicker}</span><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def priority_badge(priority: str) -> str:
    css = {"สูง": "priority-high", "ปานกลาง": "priority-medium", "ต่ำ": "priority-low"}.get(priority, "priority-medium")
    return f"<span class='{css}'>ความสำคัญ: {priority}</span>"


def render_diagnosis(result: dict, record_id: str | None = None) -> None:
    st.markdown("<div class='section-kicker'>DIAGNOSIS RESULT</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-title'>{result['title']}</div>", unsafe_allow_html=True)
    cols = st.columns([1, 2, 2])
    cols[0].markdown(priority_badge(result["priority"]), unsafe_allow_html=True)
    cols[1].markdown(f"<div class='small-muted'>หมวดหมู่</div><b>{result['category']}</b>", unsafe_allow_html=True)
    if record_id:
        cols[2].markdown(f"<div class='small-muted'>รหัสอ้างอิง</div><b>#{record_id}</b>", unsafe_allow_html=True)
    st.markdown("#### สาเหตุที่เป็นไปได้")
    st.write(result["likely_cause"])
    st.markdown("#### ขั้นตอนแนะนำ")
    for index, step in enumerate(result["steps"], start=1):
        st.markdown(f"**{index}.** {step}")
    st.markdown(f"<div class='callout'><b>ควรส่งต่อ IT เมื่อ:</b> {result['escalate_when']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='danger-callout' style='margin-top:10px'><b>ข้อควรระวัง:</b> {result['safety_note']}</div>", unsafe_allow_html=True)


if page == "Dashboard":
    render_hero("OVERVIEW · IT OPERATIONS", "IT Buddy Dashboard", "มองเห็นภาพรวมปัญหา IT และติดตามสถานะการแก้ไขได้ในที่เดียว")
    metrics = summarize_records(records)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ปัญหาที่บันทึกทั้งหมด", metrics["total"], help="จำนวนรายการที่เคยวิเคราะห์และบันทึกไว้")
    c2.metric("แก้ไขแล้ว", metrics["resolved"], help="รายการที่มีสถานะเป็นแก้ไขแล้ว")
    c3.metric("รอดำเนินการ / กำลังทำ", metrics["open"], help="รายการที่ยังไม่ปิดงานและยังไม่ส่งต่อ IT")
    c4.metric("อัตราปิดงาน", f"{metrics['resolution_rate']:.1f}%", help="คำนวณจากจำนวนแก้ไขแล้ว ÷ รายการทั้งหมด")

    st.markdown("### ภาพรวมการทำงาน")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("<div class='soft-card'><b>รายการตามหมวดหมู่</b><div class='small-muted'>จำนวนปัญหาในแต่ละหมวดจากประวัติที่บันทึก</div></div>", unsafe_allow_html=True)
        if records:
            cat_df = pd.DataFrame(list(metrics["category_counts"].items()), columns=["หมวดหมู่", "จำนวนรายการ"]).set_index("หมวดหมู่")
            st.bar_chart(cat_df, height=260)
        else:
            st.info("ยังไม่มีข้อมูลให้แสดงกราฟ เริ่มจากเมนู Smart Diagnosis เพื่อทดลองบันทึกปัญหา")
    with right:
        st.markdown("<div class='soft-card'><b>สถานะของรายการ</b><div class='small-muted'>ใช้ติดตามงานที่เปิดอยู่และงานที่ปิดแล้ว</div></div>", unsafe_allow_html=True)
        status_counts = {status: sum(1 for row in records if row.get("status") == status) for status in STATUSES}
        if records:
            status_df = pd.DataFrame(list(status_counts.items()), columns=["สถานะ", "จำนวนรายการ"]).set_index("สถานะ")
            st.bar_chart(status_df, height=260)
        else:
            st.info("กราฟสถานะจะแสดงเมื่อมีประวัติอย่างน้อย 1 รายการ")

    st.markdown("### รายการล่าสุด")
    if records:
        recent = sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)[:5]
        recent_df = pd.DataFrame([
            {"รหัส": row.get("id", "-"), "วันที่": row.get("created_at", "-").replace("T", " "),
             "หมวดหมู่": row.get("category", "-"), "อาการ": row.get("symptom", "-"),
             "ความสำคัญ": row.get("priority", "-"), "สถานะ": row.get("status", "-")}
            for row in recent
        ])
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.markdown("<div class='soft-card'><b>ยินดีต้อนรับสู่ IT Buddy</b><p>เริ่มต้นด้วยการวิเคราะห์ปัญหาตัวอย่าง แล้วระบบจะบันทึกประวัติและนำมาแสดงใน Dashboard โดยอัตโนมัติ</p></div>", unsafe_allow_html=True)

elif page == "Smart Diagnosis":
    render_hero("RULE-BASED TROUBLESHOOTING", "Smart Diagnosis", "เลือกอาการเพื่อรับแนวทางตรวจสอบเบื้องต้น พร้อมบันทึกประวัติสำหรับติดตามผล")
    st.markdown("<div class='callout'>ระบบนี้จับคู่กับฐานความรู้ที่เตรียมไว้ด้วยเงื่อนไข Python จึงเป็นคำแนะนำเบื้องต้น ไม่ใช่การวินิจฉัยจาก AI Model หรือการตรวจเครื่องระยะไกล</div>", unsafe_allow_html=True)
    st.write("")
    cat_col, issue_col = st.columns(2)
    with cat_col:
        selected_category = st.selectbox("1. เลือกหมวดหมู่ปัญหา", CATEGORIES, key="diagnosis_category")
    category_issues = get_issues_by_category(selected_category)
    with issue_col:
        issue_labels = {f"{item['symptom']} · {item['priority']}": item["id"] for item in category_issues}
        selected_label = st.selectbox("2. เลือกอาการที่พบ", list(issue_labels.keys()), key=f"symptom_{selected_category}")
        selected_issue_id = issue_labels[selected_label]

    with st.form("diagnosis_form", clear_on_submit=False):
        user_notes = st.text_area("รายละเอียดเพิ่มเติม (ไม่บังคับ)", placeholder="เช่น เกิดกับโปรแกรมใด เริ่มมีปัญหาเมื่อไหร่ หรือมีข้อความผิดพลาดอะไร", height=90)
        attempted_steps = st.text_area("ลองแก้ไขอะไรไปแล้วบ้าง? (ไม่บังคับ)", placeholder="เช่น รีสตาร์ตเครื่องแล้ว แต่ยังเกิดปัญหา", height=80)
        submitted = st.form_submit_button("วิเคราะห์ปัญหาและบันทึกประวัติ", type="primary", use_container_width=True)
    if submitted:
        result = diagnose_issue(selected_issue_id)
        record = make_record(selected_issue_id, user_notes=user_notes, attempted_steps=attempted_steps)
        records.append(record)
        save_records(DATA_FILE, records)
        st.session_state.latest_diagnosis = {**result, "record_id": record["id"], "user_notes": user_notes, "attempted_steps": attempted_steps}
        st.success(f"วิเคราะห์และบันทึกเรียบร้อยแล้ว รหัสรายการ #{record['id']}")
    if st.session_state.latest_diagnosis:
        st.divider()
        render_diagnosis(st.session_state.latest_diagnosis, st.session_state.latest_diagnosis.get("record_id"))

elif page == "Knowledge Base":
    render_hero("SELF-SERVICE KNOWLEDGE", "Knowledge Base", "ค้นหาวิธีตรวจสอบเบื้องต้นตามหมวดหมู่ปัญหา IT")
    search_col, category_col = st.columns([2, 1])
    query = search_col.text_input("ค้นหาคำหรืออาการ", placeholder="เช่น Wi-Fi, Printer, Windows Update...")
    category_filter = category_col.selectbox("หมวดหมู่", ["ทั้งหมด"] + CATEGORIES)
    results = search_knowledge_base(query=query, category=category_filter)
    st.markdown(f"**พบ {len(results)} รายการ**")
    if not results:
        st.warning("ไม่พบข้อมูลที่ตรงกัน ลองใช้คำค้นที่สั้นลงหรือเลือกหมวดหมู่ทั้งหมด")
    for item in results:
        with st.expander(f"{item['category']} · {item['title']} · ความสำคัญ {item['priority']}"):
            st.markdown(f"**อาการ:** {item['symptom']}")
            st.markdown(f"**สาเหตุที่เป็นไปได้:** {item['likely_cause']}")
            st.markdown("**แนวทางตรวจสอบ:**")
            for step in item["steps"]:
                st.markdown(f"- {step}")
            st.markdown(f"**ควรส่งต่อ IT เมื่อ:** {item['escalate_when']}")
            st.caption(f"ข้อควรระวัง: {item['safety_note']}")

elif page == "History":
    render_hero("CASE TRACKING", "Diagnosis History", "ตรวจสอบประวัติ แก้ไขสถานะการดำเนินงาน และบันทึกผลการแก้ไข")
    if not records:
        st.info("ยังไม่มีประวัติ ไปที่ Smart Diagnosis เพื่อสร้างรายการแรก")
    else:
        f1, f2 = st.columns([1, 1])
        status_filter = f1.selectbox("กรองตามสถานะ", ["ทั้งหมด"] + STATUSES)
        category_filter = f2.selectbox("กรองตามหมวดหมู่", ["ทั้งหมด"] + CATEGORIES)
        filtered = [row for row in records if (status_filter == "ทั้งหมด" or row.get("status") == status_filter)
                    and (category_filter == "ทั้งหมด" or row.get("category") == category_filter)]
        display_df = pd.DataFrame([
            {"รหัส": row.get("id", "-"), "วันเวลา": row.get("created_at", "-").replace("T", " "),
             "หมวดหมู่": row.get("category", "-"), "อาการ": row.get("symptom", "-"),
             "ความสำคัญ": row.get("priority", "-"), "สถานะ": row.get("status", "-")}
            for row in sorted(filtered, key=lambda item: item.get("created_at", ""), reverse=True)
        ])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown("### อัปเดตสถานะรายการ")
        record_options = {
            f"#{row.get('id')} · {row.get('symptom')} · {row.get('status')}": row.get("id")
            for row in sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)
        }
        with st.form("update_history_form"):
            chosen_record_label = st.selectbox("เลือกรายการที่ต้องการแก้ไข", list(record_options.keys()))
            chosen_id = record_options[chosen_record_label]
            chosen_record = next((row for row in records if row.get("id") == chosen_id), {})
            current_status = chosen_record.get("status", STATUSES[0])
            new_status = st.selectbox("สถานะใหม่", STATUSES, index=STATUSES.index(current_status) if current_status in STATUSES else 0)
            resolution_notes = st.text_area("บันทึกผลการดำเนินการ (ไม่บังคับ)", value=chosen_record.get("resolution_notes", ""), placeholder="เช่น แก้ไขโดยติดตั้งไดรเวอร์ที่ได้รับอนุมัติแล้ว")
            update_submitted = st.form_submit_button("บันทึกการเปลี่ยนแปลง", type="primary", use_container_width=True)
        if update_submitted:
            records = update_record_status(records, chosen_id, new_status, resolution_notes)
            save_records(DATA_FILE, records)
            st.success(f"อัปเดตสถานะรายการ #{chosen_id} แล้ว")
            st.rerun()
        st.markdown("### รายละเอียดรายการ")
        chosen_detail_label = st.selectbox("เลือกรายการเพื่อดูรายละเอียด", list(record_options.keys()), key="history_detail_choice")
        detail_id = record_options[chosen_detail_label]
        detail = next(row for row in records if row.get("id") == detail_id)
        with st.expander(f"รายละเอียด #{detail_id}", expanded=True):
            st.write(f"**อาการ:** {detail.get('symptom', '-')}")
            st.write(f"**รายละเอียดผู้ใช้:** {detail.get('user_notes') or 'ไม่ได้ระบุ'}")
            st.write(f"**สิ่งที่ลองทำแล้ว:** {detail.get('attempted_steps') or 'ไม่ได้ระบุ'}")
            st.write(f"**ผลการดำเนินการ:** {detail.get('resolution_notes') or 'ยังไม่มีบันทึก'}")
            st.write(f"**สาเหตุที่เป็นไปได้:** {detail.get('likely_cause', '-')}")

elif page == "About Project":
    render_hero("PYTHON CREATIVE CHALLENGE", "About IT Buddy", "โปรเจกต์ดิจิทัลที่ประยุกต์ใช้ Python เพื่อช่วยตรวจสอบปัญหา IT เบื้องต้น")
    st.markdown("### แนวคิดและวัตถุประสงค์")
    st.write("IT Buddy เป็นเว็บแอปสำหรับช่วยผู้ใช้ค้นหาแนวทางแก้ไขปัญหาคอมพิวเตอร์เบื้องต้นจากฐานความรู้ที่เตรียมไว้ ช่วยให้ผู้ใช้ทำตามขั้นตอนที่ปลอดภัย เก็บประวัติการวิเคราะห์ และติดตามสถานะงานได้")
    st.markdown("### ความรู้ Python ที่นำมาใช้")
    skill_rows = [
        {"หัวข้อ": "Conditions (if/else)", "การประยุกต์": "เลือกกฎวิเคราะห์ตามรหัสอาการ และตรวจสอบสถานะของรายการ"},
        {"หัวข้อ": "Loops (for)", "การประยุกต์": "ค้นหาฐานความรู้ วนรายการขั้นตอน และสรุปจำนวนรายการตามหมวดหมู่"},
        {"หัวข้อ": "Functions (def)", "การประยุกต์": "แยกงานเป็นฟังก์ชันวิเคราะห์ ค้นหา บันทึก โหลด และอัปเดตประวัติ"},
        {"หัวข้อ": "Lists / Dictionaries", "การประยุกต์": "เก็บฐานความรู้ ขั้นตอนแนะนำ และประวัติของแต่ละรายการ"},
        {"หัวข้อ": "JSON File I/O", "การประยุกต์": "บันทึกและโหลดประวัติจากไฟล์ภายในโฟลเดอร์โปรเจกต์"},
    ]
    st.dataframe(pd.DataFrame(skill_rows), use_container_width=True, hide_index=True)
    st.markdown("### ขอบเขตและข้อจำกัด")
    st.markdown("- การวิเคราะห์เป็นแบบ **Rule-based** จากฐานความรู้ ไม่ได้เชื่อมต่อ Generative AI API และไม่ตรวจสอบเครื่องจากระยะไกล\n- คำแนะนำเป็นแนวทางเบื้องต้น ควรส่งต่อ IT เมื่อมีความเสี่ยงด้านความปลอดภัย อุปกรณ์เสียหาย หรือกระทบระบบงานสำคัญ\n- ข้อมูลประวัติถูกบันทึกไว้ในไฟล์ `it_buddy_data.json` ในโฟลเดอร์โปรเจกต์ เหมาะสำหรับต้นแบบ/สาธิต ไม่ใช่ระบบ Production ที่มีผู้ใช้พร้อมกันจำนวนมาก\n- อย่าบันทึกรหัสผ่าน ข้อมูลส่วนบุคคลที่ละเอียดอ่อน หรือข้อมูลลับขององค์กรในช่องรายละเอียด")
    st.markdown("### โครงสร้างไฟล์")
    st.code("IT_Buddy_Project/\n├── app.py                 # Streamlit web app\n├── it_buddy_core.py       # Python logic and knowledge base\n├── IT_Buddy_Guide.ipynb   # Notebook / development guide\n├── requirements.txt       # Dependencies\n├── README.md              # Run and deployment instructions\n└── it_buddy_data.json     # Created automatically when a case is saved", language="text")

st.markdown("<div class='footer'>IT Buddy · Python Creative Challenge · Prototype for educational use · ตรวจสอบคำแนะนำกับนโยบาย IT ขององค์กรก่อนใช้งานจริง</div>", unsafe_allow_html=True)
