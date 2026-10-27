from __future__ import annotations

from pathlib import Path
import html
import altair as alt
import pandas as pd
import streamlit as st

from it_buddy_core import (
    CATEGORIES,
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

# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "it_buddy_data.json"

st.set_page_config(
    page_title="IT Buddy | Smart IT Assistant",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. GLOBAL STYLE
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Thai', sans-serif;
    }

    /* Main page */
    .stApp {
        font-family: 'IBM Plex Sans Thai', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #10233f 0%,
            #18365b 100%
        );
    }

    [data-testid="stSidebar"] * {
        color: #edf5ff !important;
    }

    [data-testid="stSidebar"] button {
        border-radius: 11px;
        font-weight: 600;
        color: #ffffff !important;
    }

    /* Keep navigation readable regardless of Streamlit light/dark theme. */
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #ff4848 !important;
        border: 1px solid #ff4848 !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] button[kind="primary"] *,
    [data-testid="stSidebar"] button[kind="secondary"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #263d5b !important;
        border: 1px solid #355171 !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #345273 !important;
        border-color: #52779c !important;
    }

    /* Hero header */
    .hero {
        padding: 28px 30px;
        border-radius: 22px;
        color: #ffffff !important;
        background: linear-gradient(
            115deg,
            #10233f 0%,
            #145f78 63%,
            #149b9b 100%
        );
        box-shadow: 0 12px 28px rgba(21, 55, 91, .14);
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #ffffff !important;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 12px 0 8px 0;
        line-height: 1.3;
    }

    .hero p {
        color: #edf8ff !important;
        margin: 0;
        font-size: 1rem;
        line-height: 1.8;
    }

    .brand-chip {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        background: #dff7f3;
        color: #087e79 !important;
        font-weight: 700;
        font-size: .78rem;
        letter-spacing: .04em;
    }

    .section-kicker {
        color: #128b91 !important;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .08em;
        margin-bottom: 5px;
    }

    /* Dashboard chart sections */
    .dashboard-info {
        padding: 20px;
        border: 1px solid var(--secondary-background-color, #e2eaf2);
        border-radius: 16px;
        min-height: 180px;
        margin-bottom: 8px;
    }

    .dashboard-info h3 {
        font-size: 1.25rem;
        margin: 0 0 12px 0;
        line-height: 1.5;
    }

    .dashboard-info p {
        line-height: 1.9;
        opacity: .9;
    }

    .dashboard-tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 8px;
        background: #e3f5f5;
        color: #087e79 !important;
        font-size: .8rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        border: 1px solid var(--secondary-background-color, #e2eaf2);
        padding: 17px;
        border-radius: 16px;
        box-shadow: 0 5px 18px rgba(20, 50, 80, .04);
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 500;
    }

    /* General cards */
    .soft-card {
        border: 1px solid var(--secondary-background-color, #e2eaf2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .small-muted {
        font-size: .88rem;
        opacity: .8;
        line-height: 1.8;
    }

    .result-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    /* Priority badges */
    .priority-high {
        display: inline-block;
        background: #fff0ed;
        color: #b93826 !important;
        padding: 5px 11px;
        border-radius: 99px;
        font-size: .82rem;
        font-weight: 700;
    }

    .priority-medium {
        display: inline-block;
        background: #fff6df;
        color: #97630b !important;
        padding: 5px 11px;
        border-radius: 99px;
        font-size: .82rem;
        font-weight: 700;
    }

    .priority-low {
        display: inline-block;
        background: #e6f7ef;
        color: #15734d !important;
        padding: 5px 11px;
        border-radius: 99px;
        font-size: .82rem;
        font-weight: 700;
    }

    /* Buttons */
    .stButton button,
    .stFormSubmitButton button {
        border-radius: 11px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Form: theme-aware readable text */
    [data-testid="stForm"] {
        border-radius: 16px;
        padding: 20px;
    }

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--text-color, inherit) !important;
        opacity: 1 !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--text-color, #15243b) !important;
        caret-color: var(--text-color, #15243b) !important;
        -webkit-text-fill-color: var(--text-color, #15243b) !important;
        background-color: var(
            --secondary-background-color,
            #ffffff
        ) !important;
        border-radius: 9px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: var(--text-color, #526174) !important;
        -webkit-text-fill-color: var(--text-color, #526174) !important;
        opacity: .65 !important;
    }

    [data-baseweb="select"] > div {
        border-radius: 9px;
    }

    [data-baseweb="select"] input {
        color: var(--text-color, inherit) !important;
        -webkit-text-fill-color: var(--text-color, inherit) !important;
    }

    /* Callout boxes */
    .callout {
        border-left: 4px solid #149b9b;
        background: #eaf8f7;
        border-radius: 0 12px 12px 0;
        padding: 14px 16px;
        color: #244957 !important;
        line-height: 1.9;
    }

    .callout *,
    .danger-callout * {
        color: inherit !important;
    }

    .danger-callout {
        border-left: 4px solid #e16b55;
        background: #fff2ef;
        border-radius: 0 12px 12px 0;
        padding: 14px 16px;
        color: #78382e !important;
        line-height: 1.9;
    }

    .footer {
        font-size: .8rem;
        opacity: .75;
        border-top: 1px solid var(--secondary-background-color, #dfe7f0);
        padding-top: 14px;
        margin-top: 30px;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 22px 18px;
        }

        .hero h1 {
            font-size: 1.6rem;
        }

        [data-testid="stForm"] {
            padding: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 3. SESSION STATE
# =========================================================

if "it_buddy_page" not in st.session_state:
    st.session_state.it_buddy_page = "Dashboard"

if "latest_diagnosis" not in st.session_state:
    st.session_state.latest_diagnosis = None

# =========================================================
# 4. LOAD DATA
# =========================================================

records = load_records(DATA_FILE)


# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def safe_text(value) -> str:
    """Escape text before displaying it inside HTML."""
    return html.escape(str(value))


def render_hero(kicker: str, title: str, subtitle: str) -> None:
    """Display the page header."""
    st.markdown(
        f"""
        <div class="hero">
            <span class="brand-chip">{safe_text(kicker)}</span>
            <h1>{safe_text(title)}</h1>
            <p>{safe_text(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(priority: str) -> str:
    """Create a colored priority label."""
    css = {
        "สูง": "priority-high",
        "ปานกลาง": "priority-medium",
        "ต่ำ": "priority-low",
    }.get(priority, "priority-medium")

    return (
        f"<span class='{css}'>"
        f"ความสำคัญ: {safe_text(priority)}"
        f"</span>"
    )


def render_diagnosis(
    result: dict,
    record_id: str | None = None,
) -> None:
    """Display diagnosis results and recommended actions."""
    st.markdown(
        '<div class="section-kicker">DIAGNOSIS RESULT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="result-title">{safe_text(result["title"])}</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 2])

    col1.markdown(
        priority_badge(result["priority"]),
        unsafe_allow_html=True,
    )

    col2.markdown(
        f"""
        <div class="small-muted">หมวดหมู่</div>
        <b>{safe_text(result["category"])}</b>
        """,
        unsafe_allow_html=True,
    )

    if record_id:
        col3.markdown(
            f"""
            <div class="small-muted">รหัสอ้างอิง</div>
            <b>#{safe_text(record_id)}</b>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### สาเหตุที่เป็นไปได้")
    st.write(result["likely_cause"])

    st.markdown("#### ขั้นตอนแนะนำ")

    for index, step in enumerate(result["steps"], start=1):
        st.markdown(f"**{index}.** {step}")

    st.markdown(
        f"""
        <div class="callout">
            <b>ควรส่งต่อ IT เมื่อ:</b>
            {safe_text(result["escalate_when"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="danger-callout" style="margin-top:12px">
            <b>ข้อควรระวัง:</b>
            {safe_text(result["safety_note"])}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_row(
    title: str,
    description: str,
    tag: str,
    chart_data: pd.DataFrame | None,
    chart_height: int = 300,
) -> None:
    """
    Dashboard layout:
    Information on the left, chart on the right.
    Each section occupies its own horizontal row.
    """
    left, right = st.columns([1, 2.2], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="dashboard-info">
                <h3>{safe_text(title)}</h3>
                <p>{safe_text(description)}</p>
                <span class="dashboard-tag">{safe_text(tag)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        if chart_data is not None and not chart_data.empty:
            # Altair lets us keep vertical bars while forcing category labels
            # to remain horizontal in both light and dark themes.
            chart_frame = chart_data.reset_index()
            category_field = chart_frame.columns[0]
            value_field = chart_frame.columns[1]

            chart = (
                alt.Chart(chart_frame)
                .mark_bar()
                .encode(
                    x=alt.X(
                        f"{category_field}:N",
                        title=category_field,
                        axis=alt.Axis(
                            labelAngle=0,
                            labelOverlap=False,
                            labelLimit=260,
                        ),
                    ),
                    y=alt.Y(
                        f"{value_field}:Q",
                        title=value_field,
                        axis=alt.Axis(format="d"),
                    ),
                    tooltip=[
                        alt.Tooltip(f"{category_field}:N", title=category_field),
                        alt.Tooltip(f"{value_field}:Q", title=value_field, format="d"),
                    ],
                )
                .properties(height=chart_height)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลให้แสดงกราฟ")

    st.write("")


# =========================================================
# 6. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:2rem;font-weight:700;line-height:1.2">
            🛠️ IT Buddy
        </div>
        <div style="margin-top:6px;font-size:.86rem">
            SMART IT ASSISTANT · PYTHON PROJECT
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<hr style='border-color:#355171;margin:20px 0 16px 0'>",
        unsafe_allow_html=True,
    )

    nav_items = [
        ("Dashboard", "▦", "ภาพรวมระบบ"),
        ("Smart Diagnosis", "⌕", "วิเคราะห์ปัญหา"),
        ("Knowledge Base", "▤", "คลังวิธีแก้ปัญหา"),
        ("History", "◷", "ประวัติการวิเคราะห์"),
        ("About Project", "ⓘ", "เกี่ยวกับโครงงาน"),
    ]

    for page_key, icon, label in nav_items:
        if st.button(
            f"{icon}   {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.it_buddy_page == page_key
                else "secondary"
            ),
        ):
            st.session_state.it_buddy_page = page_key
            st.rerun()

    st.markdown(
        "<hr style='border-color:#355171;margin:18px 0'>",
        unsafe_allow_html=True,
    )

    sidebar_summary = summarize_records(records)

    st.caption("WORKSPACE STATUS")
    st.markdown(f"**{sidebar_summary['total']}** รายการในประวัติ")

    st.progress(
        sidebar_summary["resolution_rate"] / 100
        if sidebar_summary["total"]
        else 0
    )

    st.markdown(
        f"""
        <div style="font-size:.8rem">
            อัตราปิดงาน {sidebar_summary['resolution_rate']:.1f}%
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="margin-top:22px;font-size:.75rem">
            DEMO MODE · บันทึกในไฟล์ JSON
        </div>
        """,
        unsafe_allow_html=True,
    )

page = st.session_state.it_buddy_page


# =========================================================
# 7. DASHBOARD
# =========================================================

if page == "Dashboard":

    render_hero(
        "OVERVIEW · IT OPERATIONS",
        "IT Buddy Dashboard",
        "มองเห็นภาพรวมปัญหา IT และติดตามสถานะการแก้ไขได้ในที่เดียว",
    )

    metrics = summarize_records(records)

    # Summary metrics
    st.markdown("### ตัวชี้วัดภาพรวม")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "ปัญหาที่บันทึกทั้งหมด",
        metrics["total"],
        help="จำนวนรายการที่เคยวิเคราะห์และบันทึกไว้",
    )

    c2.metric(
        "แก้ไขแล้ว",
        metrics["resolved"],
        help="รายการที่มีสถานะเป็นแก้ไขแล้ว",
    )

    c3.metric(
        "รอดำเนินการ / กำลังทำ",
        metrics["open"],
        help="จำนวนรายการที่ยังไม่ปิดงาน",
    )

    c4.metric(
        "อัตราปิดงาน",
        f"{metrics['resolution_rate']:.1f}%",
        help="คำนวณจากจำนวนแก้ไขแล้วเทียบกับรายการทั้งหมด",
    )

    st.divider()
    st.markdown("## 📊 ภาพรวมการทำงาน")

    # Row 1: Categories
    category_counts = metrics["category_counts"]

    if category_counts:
        category_df = pd.DataFrame(
            list(category_counts.items()),
            columns=["หมวดหมู่", "จำนวนรายการ"],
        ).set_index("หมวดหมู่")
    else:
        category_df = pd.DataFrame()

    render_dashboard_row(
        title="รายการตามหมวดหมู่",
        description=(
            "ดูว่าปัญหาที่บันทึกไว้เกิดขึ้นในหมวดหมู่ใดบ้าง "
            "เพื่อช่วยให้มองเห็นประเภทปัญหาที่พบได้ง่ายขึ้น"
        ),
        tag=f"{len(category_counts)} หมวดหมู่",
        chart_data=category_df,
        chart_height=300,
    )

    st.divider()

    # Row 2: Status
    status_counts = {
        status: sum(
            1
            for row in records
            if row.get("status") == status
        )
        for status in STATUSES
    }

    status_df = pd.DataFrame(
        list(status_counts.items()),
        columns=["สถานะ", "จำนวนรายการ"],
    ).set_index("สถานะ")

    render_dashboard_row(
        title="สถานะของรายการ",
        description=(
            "ติดตามจำนวนงานที่รอดำเนินการ "
            "กำลังดำเนินการ แก้ไขแล้ว หรือส่งต่อ IT"
        ),
        tag=f"{len(records)} รายการทั้งหมด",
        chart_data=status_df if records else pd.DataFrame(),
        chart_height=300,
    )

    st.divider()

    # Recent records
    st.markdown("## 🕒 รายการล่าสุด")

    if records:
        recent = sorted(
            records,
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )[:5]

        recent_df = pd.DataFrame(
            [
                {
                    "รหัส": row.get("id", "-"),
                    "วันที่": row.get("created_at", "-").replace("T", " "),
                    "หมวดหมู่": row.get("category", "-"),
                    "อาการ": row.get("symptom", "-"),
                    "ความสำคัญ": row.get("priority", "-"),
                    "สถานะ": row.get("status", "-"),
                }
                for row in recent
            ]
        )

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.markdown(
            """
            <div class="soft-card">
                <h3>ยินดีต้อนรับสู่ IT Buddy</h3>
                <p>
                    เริ่มต้นด้วยการวิเคราะห์ปัญหาตัวอย่าง
                    ระบบจะบันทึกประวัติและนำมาแสดงใน Dashboard
                    โดยอัตโนมัติ
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 8. SMART DIAGNOSIS
# =========================================================

elif page == "Smart Diagnosis":

    render_hero(
        "RULE-BASED TROUBLESHOOTING",
        "Smart Diagnosis",
        "เลือกอาการเพื่อรับแนวทางตรวจสอบเบื้องต้น พร้อมบันทึกประวัติสำหรับติดตามผล",
    )

    st.markdown(
        """
        <div class="callout">
            ระบบนี้ใช้เงื่อนไข Python จับคู่กับฐานความรู้ที่เตรียมไว้
            เพื่อแนะนำวิธีตรวจสอบเบื้องต้น ไม่ใช่การวินิจฉัยจาก AI Model
            หรือการตรวจเครื่องระยะไกล
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    cat_col, issue_col = st.columns(2)

    with cat_col:
        selected_category = st.selectbox(
            "1. เลือกหมวดหมู่ปัญหา",
            CATEGORIES,
            key="diagnosis_category",
        )

    category_issues = get_issues_by_category(selected_category)

    with issue_col:
        issue_labels = {
            f"{item['symptom']} · {item['priority']}": item["id"]
            for item in category_issues
        }

        selected_label = st.selectbox(
            "2. เลือกอาการที่พบ",
            list(issue_labels.keys()),
            key=f"symptom_{selected_category}",
        )

        selected_issue_id = issue_labels[selected_label]

    with st.form("diagnosis_form", clear_on_submit=False):

        user_notes = st.text_area(
            "รายละเอียดเพิ่มเติม (ไม่บังคับ)",
            placeholder=(
                "เช่น เกิดกับโปรแกรมใด เริ่มมีปัญหาเมื่อไหร่ "
                "หรือมีข้อความผิดพลาดอะไร"
            ),
            height=100,
        )

        attempted_steps = st.text_area(
            "ลองแก้ไขอะไรไปแล้วบ้าง? (ไม่บังคับ)",
            placeholder=(
                "เช่น รีสตาร์ตเครื่องแล้ว "
                "แต่ยังเกิดปัญหา"
            ),
            height=90,
        )

        submitted = st.form_submit_button(
            "วิเคราะห์ปัญหาและบันทึกประวัติ",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        result = diagnose_issue(selected_issue_id)

        record = make_record(
            selected_issue_id,
            user_notes=user_notes,
            attempted_steps=attempted_steps,
        )

        records.append(record)
        save_records(DATA_FILE, records)

        st.session_state.latest_diagnosis = {
            **result,
            "record_id": record["id"],
            "user_notes": user_notes,
            "attempted_steps": attempted_steps,
        }

        st.success(
            f"วิเคราะห์และบันทึกเรียบร้อยแล้ว "
            f"รหัสรายการ #{record['id']}"
        )

    if st.session_state.latest_diagnosis:

        st.divider()

        render_diagnosis(
            st.session_state.latest_diagnosis,
            st.session_state.latest_diagnosis.get("record_id"),
        )


# =========================================================
# 9. KNOWLEDGE BASE
# =========================================================

elif page == "Knowledge Base":

    render_hero(
        "SELF-SERVICE KNOWLEDGE",
        "Knowledge Base",
        "ค้นหาวิธีตรวจสอบเบื้องต้นตามหมวดหมู่ปัญหา IT",
    )

    search_col, category_col = st.columns([2, 1])

    query = search_col.text_input(
        "ค้นหาคำหรืออาการ",
        placeholder="เช่น Wi-Fi, Printer, Windows Update...",
    )

    category_filter = category_col.selectbox(
        "หมวดหมู่",
        ["ทั้งหมด"] + CATEGORIES,
    )

    results = search_knowledge_base(
        query=query,
        category=category_filter,
    )

    st.markdown(f"### พบ {len(results)} รายการ")

    if not results:
        st.warning(
            "ไม่พบข้อมูลที่ตรงกัน "
            "ลองใช้คำค้นที่สั้นลงหรือเลือกหมวดหมู่ทั้งหมด"
        )

    for item in results:

        with st.expander(
            f"{item['category']} · {item['title']} · "
            f"ความสำคัญ {item['priority']}"
        ):

            st.markdown(f"**อาการ:** {item['symptom']}")

            st.markdown(
                f"**สาเหตุที่เป็นไปได้:** {item['likely_cause']}"
            )

            st.markdown("**แนวทางตรวจสอบ:**")

            for step in item["steps"]:
                st.markdown(f"- {step}")

            st.markdown(
                f"**ควรส่งต่อ IT เมื่อ:** {item['escalate_when']}"
            )

            st.caption(
                f"ข้อควรระวัง: {item['safety_note']}"
            )


# =========================================================
# 10. HISTORY
# =========================================================

elif page == "History":

    render_hero(
        "CASE TRACKING",
        "Diagnosis History",
        "ตรวจสอบประวัติ แก้ไขสถานะการดำเนินงาน และบันทึกผลการแก้ไข",
    )

    if not records:

        st.info(
            "ยังไม่มีประวัติ ไปที่ Smart Diagnosis เพื่อสร้างรายการแรก"
        )

    else:

        f1, f2 = st.columns(2)

        status_filter = f1.selectbox(
            "กรองตามสถานะ",
            ["ทั้งหมด"] + STATUSES,
        )

        category_filter = f2.selectbox(
            "กรองตามหมวดหมู่",
            ["ทั้งหมด"] + CATEGORIES,
        )

        filtered = [
            row
            for row in records
            if (
                status_filter == "ทั้งหมด"
                or row.get("status") == status_filter
            )
            and (
                category_filter == "ทั้งหมด"
                or row.get("category") == category_filter
            )
        ]

        display_df = pd.DataFrame(
            [
                {
                    "รหัส": row.get("id", "-"),
                    "วันเวลา": row.get("created_at", "-").replace("T", " "),
                    "หมวดหมู่": row.get("category", "-"),
                    "อาการ": row.get("symptom", "-"),
                    "ความสำคัญ": row.get("priority", "-"),
                    "สถานะ": row.get("status", "-"),
                }
                for row in sorted(
                    filtered,
                    key=lambda item: item.get("created_at", ""),
                    reverse=True,
                )
            ]
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### อัปเดตสถานะรายการ")

        record_options = {
            (
                f"#{row.get('id')} · "
                f"{row.get('symptom')} · "
                f"{row.get('status')}"
            ): row.get("id")
            for row in sorted(
                records,
                key=lambda item: item.get("created_at", ""),
                reverse=True,
            )
        }

        with st.form("update_history_form"):

            chosen_record_label = st.selectbox(
                "เลือกรายการที่ต้องการแก้ไข",
                list(record_options.keys()),
            )

            chosen_id = record_options[chosen_record_label]

            chosen_record = next(
                (
                    row
                    for row in records
                    if row.get("id") == chosen_id
                ),
                {},
            )

            current_status = chosen_record.get(
                "status",
                STATUSES[0],
            )

            new_status = st.selectbox(
                "สถานะใหม่",
                STATUSES,
                index=(
                    STATUSES.index(current_status)
                    if current_status in STATUSES
                    else 0
                ),
            )

            resolution_notes = st.text_area(
                "บันทึกผลการดำเนินการ (ไม่บังคับ)",
                value=chosen_record.get("resolution_notes", ""),
                placeholder=(
                    "เช่น แก้ไขโดยติดตั้งไดรเวอร์ "
                    "ที่ได้รับอนุมัติแล้ว"
                ),
            )

            update_submitted = st.form_submit_button(
                "บันทึกการเปลี่ยนแปลง",
                type="primary",
                use_container_width=True,
            )

        if update_submitted:

            records = update_record_status(
                records,
                chosen_id,
                new_status,
                resolution_notes,
            )

            save_records(DATA_FILE, records)

            st.success(
                f"อัปเดตสถานะรายการ #{chosen_id} แล้ว"
            )

            st.rerun()

        st.markdown("### รายละเอียดรายการ")

        chosen_detail_label = st.selectbox(
            "เลือกรายการเพื่อดูรายละเอียด",
            list(record_options.keys()),
            key="history_detail_choice",
        )

        detail_id = record_options[chosen_detail_label]

        detail = next(
            row for row in records
            if row.get("id") == detail_id
        )

        with st.expander(
            f"รายละเอียด #{detail_id}",
            expanded=True,
        ):

            st.write(f"**อาการ:** {detail.get('symptom', '-')}")

            st.write(
                f"**รายละเอียดผู้ใช้:** "
                f"{detail.get('user_notes') or 'ไม่ได้ระบุ'}"
            )

            st.write(
                f"**สิ่งที่ลองทำแล้ว:** "
                f"{detail.get('attempted_steps') or 'ไม่ได้ระบุ'}"
            )

            st.write(
                f"**ผลการดำเนินการ:** "
                f"{detail.get('resolution_notes') or 'ยังไม่มีบันทึก'}"
            )

            st.write(
                f"**สาเหตุที่เป็นไปได้:** "
                f"{detail.get('likely_cause', '-')}"
            )


# =========================================================
# 11. ABOUT PROJECT
# =========================================================

elif page == "About Project":

    render_hero(
        "PYTHON CREATIVE CHALLENGE",
        "About IT Buddy",
        "โปรเจกต์ดิจิทัลที่ประยุกต์ใช้ Python เพื่อช่วยตรวจสอบปัญหา IT เบื้องต้น",
    )

    st.markdown("### แนวคิดและวัตถุประสงค์")

    st.write(
        "IT Buddy เป็นเว็บแอปสำหรับช่วยผู้ใช้ค้นหาแนวทางแก้ไข "
        "ปัญหาคอมพิวเตอร์เบื้องต้นจากฐานความรู้ที่เตรียมไว้ "
        "ช่วยให้ผู้ใช้ทำตามขั้นตอนที่ปลอดภัย เก็บประวัติการวิเคราะห์ "
        "และติดตามสถานะงานได้"
    )

    st.markdown("### ความรู้ Python ที่นำมาใช้")

    skill_rows = [
        {
            "หัวข้อ": "Conditions (if/else)",
            "การประยุกต์": (
                "เลือกกฎวิเคราะห์ตามรหัสอาการ "
                "และตรวจสอบสถานะของรายการ"
            ),
        },
        {
            "หัวข้อ": "Loops (for)",
            "การประยุกต์": (
                "ค้นหาฐานความรู้ วนรายการขั้นตอน "
                "และสรุปจำนวนรายการตามหมวดหมู่"
            ),
        },
        {
            "หัวข้อ": "Functions (def)",
            "การประยุกต์": (
                "แยกงานเป็นฟังก์ชันวิเคราะห์ ค้นหา "
                "บันทึก โหลด และอัปเดตประวัติ"
            ),
        },
        {
            "หัวข้อ": "Lists / Dictionaries",
            "การประยุกต์": (
                "เก็บฐานความรู้ ขั้นตอนแนะนำ "
                "และประวัติของแต่ละรายการ"
            ),
        },
        {
            "หัวข้อ": "JSON File I/O",
            "การประยุกต์": (
                "บันทึกและโหลดประวัติจากไฟล์ "
                "ภายในโฟลเดอร์โปรเจกต์"
            ),
        },
    ]

    st.dataframe(
        pd.DataFrame(skill_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### ขอบเขตและข้อจำกัด")

    st.markdown(
        """
        - การวิเคราะห์เป็นแบบ Rule-based จากฐานความรู้
          ไม่ได้เชื่อมต่อ Generative AI API
          และไม่ตรวจสอบเครื่องจากระยะไกล
        - คำแนะนำเป็นแนวทางเบื้องต้น
          ควรส่งต่อ IT เมื่อมีความเสี่ยงด้านความปลอดภัย
          อุปกรณ์เสียหาย หรือกระทบระบบงานสำคัญ
        - ข้อมูลประวัติถูกบันทึกไว้ในไฟล์
          `it_buddy_data.json` ในโฟลเดอร์โปรเจกต์
        - การบันทึกไฟล์ภายในเครื่องที่โฮสต์แอป
          ไม่เหมาะกับระบบ Production ที่ต้องเก็บข้อมูลถาวร
          หรือรองรับผู้ใช้พร้อมกันจำนวนมาก
        - อย่าบันทึกรหัสผ่าน ข้อมูลส่วนบุคคลที่ละเอียดอ่อน
          หรือข้อมูลลับขององค์กรในช่องรายละเอียด
        """
    )

    st.markdown("### โครงสร้างไฟล์")

    st.code(
        "IT_Buddy_Project/\n"
        "├── app.py                 # Streamlit web app\n"
        "├── it_buddy_core.py       # Python logic and knowledge base\n"
        "├── IT_Buddy_Guide.ipynb   # Notebook / development guide\n"
        "├── requirements.txt       # Dependencies\n"
        "├── README.md              # Run and deployment instructions\n"
        "└── it_buddy_data.json     # Created when a case is saved",
        language="text",
    )


# =========================================================
# 12. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        IT Buddy · Python Creative Challenge · Prototype for educational use
        · ตรวจสอบคำแนะนำกับนโยบาย IT ขององค์กรก่อนใช้งานจริง
    </div>
    """,
    unsafe_allow_html=True,
)
