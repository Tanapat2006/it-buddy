"""Core logic for IT Buddy: rule-based IT troubleshooting assistant.

This module is intentionally independent from Streamlit so the logic can be
studied, tested, and reused in a notebook.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import uuid

STATUSES = ["รอดำเนินการ", "กำลังดำเนินการ", "แก้ไขแล้ว", "ส่งต่อ IT"]
PRIORITIES = ["สูง", "ปานกลาง", "ต่ำ"]

# A small curated knowledge base for a classroom demonstration.
# Advice is intentionally conservative: users should not bypass company controls.
ISSUES: list[dict[str, Any]] = [
    {
        "id": "wifi_not_connect", "category": "Network", "title": "เชื่อมต่อ Wi-Fi ไม่ได้",
        "symptom": "เชื่อมต่อ Wi-Fi ไม่ได้", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากปิด Wi-Fi / Airplane mode, โปรไฟล์เครือข่ายเดิม, รหัสผ่านหมดอายุ หรือสัญญาณอ่อน",
        "steps": [
            "ตรวจสอบว่าเปิด Wi-Fi และปิด Airplane mode แล้ว",
            "ลองย้ายเข้าใกล้ Access Point และตรวจดูว่าอุปกรณ์อื่นพบชื่อเครือข่ายหรือไม่",
            "เลือกเครือข่ายบริษัทแล้วเชื่อมต่อใหม่ โดยใช้ข้อมูลรับรองที่ได้รับอนุญาต",
            "หากยังไม่ได้ ให้จดชื่อเครือข่ายและข้อความผิดพลาดเพื่อแจ้ง IT",
        ],
        "escalate_when": "อุปกรณ์หลายเครื่องเชื่อมต่อไม่ได้ หรือระบบขอข้อมูลรับรองที่ไม่รู้จัก",
        "safety_note": "อย่าเชื่อมต่อ Wi-Fi สาธารณะที่ไม่รู้จักเพื่อเลี่ยงระบบบริษัท และอย่าเปิดเผยรหัสผ่าน",
    },
    {
        "id": "no_internet", "category": "Network", "title": "เชื่อมต่อเครือข่ายได้แต่เข้าอินเทอร์เน็ตไม่ได้",
        "symptom": "ต่อเครือข่ายได้ แต่เข้าอินเทอร์เน็ตไม่ได้", "priority": "สูง",
        "likely_cause": "อาจเกิดจากปัญหา Gateway, DNS, Proxy/VPN หรือบริการเครือข่ายส่วนกลาง",
        "steps": [
            "ตรวจสอบว่าเว็บไซต์หลายแห่งเข้าไม่ได้จริง ไม่ใช่เฉพาะเว็บไซต์เดียว",
            "ตรวจสอบสถานะ VPN และ Proxy ตามการตั้งค่าที่องค์กรกำหนด",
            "ปิด/เปิดการเชื่อมต่อเครือข่ายหนึ่งครั้ง แล้วทดลองใหม่",
            "หากยังใช้งานไม่ได้ ให้แจ้ง IT พร้อมเวลาที่เริ่มเกิดปัญหาและสถานะ VPN",
        ],
        "escalate_when": "ผู้ใช้หลายคนได้รับผลกระทบ หรือระบบงานสำคัญหยุดทำงาน",
        "safety_note": "อย่าเปลี่ยน DNS, Proxy หรือการตั้งค่า VPN ของบริษัทโดยไม่ได้รับอนุญาต",
    },
    {
        "id": "slow_network", "category": "Network", "title": "เครือข่ายช้าหรือหลุดบ่อย",
        "symptom": "อินเทอร์เน็ตช้าหรือหลุดบ่อย", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากสัญญาณอ่อน ความหนาแน่นของเครือข่าย VPN หรือปัญหาที่จุดเชื่อมต่อ",
        "steps": [
            "ตรวจสอบว่าปัญหาเกิดกับเว็บไซต์/แอปเดียวหรือทุกระบบ",
            "หากใช้ Wi-Fi ให้ทดลองในตำแหน่งที่สัญญาณดีขึ้น",
            "จดช่วงเวลาที่เกิดปัญหาและตรวจสอบว่ามีผู้ใช้อื่นได้รับผลกระทบหรือไม่",
            "หากเกิดซ้ำ ให้ส่งข้อมูลเวลา สถานที่ และระบบที่ได้รับผลกระทบให้ IT",
        ],
        "escalate_when": "ปัญหาเกิดซ้ำหรือกระทบหลายคน/งานเร่งด่วน",
        "safety_note": "อย่าถอดสาย uplink หรือรีสตาร์ตอุปกรณ์เครือข่ายส่วนกลางเอง",
    },
    {
        "id": "slow_pc", "category": "Windows", "title": "คอมพิวเตอร์ทำงานช้า",
        "symptom": "คอมพิวเตอร์ทำงานช้า", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากโปรแกรมเปิดพร้อมเครื่องมาก พื้นที่ดิสก์เหลือน้อย งานเบื้องหลัง หรือหน่วยความจำไม่เพียงพอ",
        "steps": [
            "บันทึกงานที่เปิดอยู่ก่อนปิดโปรแกรมที่ไม่จำเป็น",
            "เปิด Task Manager เพื่อตรวจสอบ CPU, Memory และ Disk ที่ใช้งานสูง",
            "ตรวจสอบพื้นที่ว่างในไดรฟ์ระบบ และลบเฉพาะไฟล์ที่ทราบว่าไม่จำเป็น",
            "รีสตาร์ตเครื่องเมื่อสะดวกและไม่มีงานที่ยังไม่ได้บันทึก",
        ],
        "escalate_when": "เครื่องค้างซ้ำ มีเสียง/ความร้อนผิดปกติ หรือดิสก์/หน่วยความจำใช้งานสูงต่อเนื่อง",
        "safety_note": "อย่าลบไฟล์ระบบหรือปิดโปรแกรมความปลอดภัยเพื่อเพิ่มความเร็ว",
    },
    {
        "id": "windows_update_failed", "category": "Windows", "title": "Windows Update ติดตั้งไม่สำเร็จ",
        "symptom": "Windows Update ติดตั้งไม่สำเร็จ", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากพื้นที่ว่างไม่พอ การรีสตาร์ตที่รออยู่ เครือข่าย หรือข้อกำหนดของอุปกรณ์",
        "steps": [
            "จดรหัสข้อผิดพลาดและชื่ออัปเดตที่ติดตั้งไม่สำเร็จ",
            "ตรวจสอบพื้นที่ว่างในไดรฟ์ระบบและเสียบอะแดปเตอร์ไฟหากเป็นโน้ตบุ๊ก",
            "รีสตาร์ตเครื่องหากมีการร้องขอ และลองตรวจสอบอัปเดตอีกครั้งตามนโยบายองค์กร",
            "ส่งรหัสข้อผิดพลาดให้ IT หากเกิดซ้ำ",
        ],
        "escalate_when": "อัปเดตล้มเหลวซ้ำ เครื่องบูตไม่ขึ้น หรือมีข้อความ BitLocker/Recovery",
        "safety_note": "อย่าปิดการเข้ารหัสหรือข้ามนโยบายอัปเดตขององค์กร หากมีข้อความ BitLocker ให้ติดต่อ IT",
    },
    {
        "id": "login_problem", "category": "Windows", "title": "เข้าสู่ระบบ Windows ไม่ได้",
        "symptom": "เข้าสู่ระบบ Windows ไม่ได้", "priority": "สูง",
        "likely_cause": "อาจเกิดจากรหัสผ่านหมดอายุ บัญชีถูกล็อก การเชื่อมต่อ Domain/VPN หรือปัญหาโปรไฟล์ผู้ใช้",
        "steps": [
            "ตรวจสอบภาษาแป้นพิมพ์ Caps Lock และชื่อบัญชีที่เลือก",
            "อ่านข้อความผิดพลาดและจดเวลาเกิดปัญหา โดยไม่ส่งรหัสผ่านให้ผู้อื่น",
            "หากองค์กรกำหนดขั้นตอนรีเซ็ตรหัสผ่าน ให้ใช้ช่องทางทางการเท่านั้น",
            "ติดต่อ IT เพื่อยืนยันสถานะบัญชีและการเชื่อมต่อ Domain",
        ],
        "escalate_when": "บัญชีถูกล็อก มีข้อความสงสัยด้านความปลอดภัย หรือเข้าเครื่องที่ต้องใช้ทำงานไม่ได้",
        "safety_note": "ห้ามแชร์รหัสผ่านหรือรหัส MFA และอย่าพยายามข้ามระบบยืนยันตัวตน",
    },
    {
        "id": "app_crash", "category": "Software", "title": "โปรแกรมเปิดแล้วปิดเอง/ค้าง",
        "symptom": "โปรแกรมค้างหรือปิดเอง", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากโปรแกรมเวอร์ชันไม่เข้ากัน ไฟล์ตั้งค่าผิดพลาด ทรัพยากรเครื่องไม่พอ หรือส่วนเสริมมีปัญหา",
        "steps": [
            "บันทึกงานและจดชื่อโปรแกรมพร้อมข้อความผิดพลาด",
            "ปิดโปรแกรมแล้วเปิดใหม่หนึ่งครั้ง หากงานได้รับการบันทึกแล้ว",
            "ตรวจสอบว่ามีการอัปเดตที่ได้รับอนุมัติหรือประกาศปัญหาจาก IT หรือไม่",
            "หากเกิดซ้ำ ให้ส่งภาพข้อความผิดพลาดและขั้นตอนที่ทำก่อนโปรแกรมปิด",
        ],
        "escalate_when": "โปรแกรมเกี่ยวข้องกับงานสำคัญ ข้อมูลเสียหาย หรือเกิดกับผู้ใช้หลายคน",
        "safety_note": "อย่าติดตั้งโปรแกรมจากเว็บไซต์ที่ไม่รู้จักหรือปิดระบบป้องกันไวรัส",
    },
    {
        "id": "install_failed", "category": "Software", "title": "ติดตั้งโปรแกรมไม่ได้",
        "symptom": "ติดตั้งโปรแกรมไม่ได้", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากไม่มีสิทธิ์ติดตั้ง แพ็กเกจไม่ถูกต้อง ระบบไม่รองรับ หรือโปรแกรมถูกจำกัดด้วยนโยบายองค์กร",
        "steps": [
            "จดชื่อโปรแกรม เวอร์ชัน และข้อความผิดพลาด",
            "ตรวจสอบว่าใช้ไฟล์ติดตั้งจากแหล่งที่องค์กรอนุมัติ",
            "ตรวจสอบความต้องการระบบและพื้นที่ว่างตามเอกสารของโปรแกรม",
            "ส่งคำขอติดตั้งผ่านขั้นตอนของ IT หากต้องใช้สิทธิ์ผู้ดูแลระบบ",
        ],
        "escalate_when": "ต้องใช้สิทธิ์ Administrator หรือโปรแกรมไม่อยู่ในรายการที่อนุมัติ",
        "safety_note": "อย่าข้าม UAC, นโยบายสิทธิ์ หรือใช้บัญชีผู้ดูแลระบบของบุคคลอื่น",
    },
    {
        "id": "license_issue", "category": "Software", "title": "โปรแกรมแจ้งปัญหา License/Activation",
        "symptom": "โปรแกรมแจ้ง License หรือ Activation ผิดพลาด", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากบัญชีที่ลงชื่อเข้าใช้ สิทธิ์ใช้งาน การเชื่อมต่อ หรือการเปิดใช้งานที่ยังไม่สมบูรณ์",
        "steps": [
            "จดข้อความผิดพลาดและชื่อบัญชีที่แสดง โดยไม่เปิดเผยรหัสผ่าน",
            "ตรวจสอบว่าเชื่อมต่ออินเทอร์เน็ตและลงชื่อเข้าใช้บัญชีองค์กรที่ถูกต้อง",
            "ตรวจสอบสิทธิ์ใช้งานผ่านหน้า/ช่องทางทางการของผู้ให้บริการ",
            "ติดต่อ IT หรือผู้ดูแล License หากยังไม่เปิดใช้งาน",
        ],
        "escalate_when": "กระทบซอฟต์แวร์งานหลักหรือจำเป็นต้องจัดสรร License เพิ่ม",
        "safety_note": "อย่าใช้ Key Generator, Crack หรือบัญชีที่ไม่ได้รับอนุญาต",
    },
    {
        "id": "cannot_print", "category": "Printer", "title": "สั่งพิมพ์แล้วไม่ออก",
        "symptom": "สั่งพิมพ์แล้วไม่ออก", "priority": "ปานกลาง",
        "likely_cause": "อาจเกิดจากเลือกเครื่องพิมพ์ผิด สถานะ Offline กระดาษ/หมึกหมด หรือคิวพิมพ์ค้าง",
        "steps": [
            "ตรวจสอบชื่อเครื่องพิมพ์ที่เลือกและลองพิมพ์หน้า Test Page หากได้รับอนุญาต",
            "ตรวจสอบกระดาษ หมึก/โทนเนอร์ ฝาครอบ และข้อความบนหน้าจอเครื่องพิมพ์",
            "ตรวจสอบว่าเครื่องพิมพ์แสดงสถานะ Ready/Online",
            "หากคิวพิมพ์ค้าง ให้แจ้ง IT พร้อมชื่อเครื่องพิมพ์และเวลาเกิดปัญหา",
        ],
        "escalate_when": "เครื่องพิมพ์มีไฟ/รหัสผิดพลาด หรือผู้ใช้หลายคนพิมพ์ไม่ได้",
        "safety_note": "อย่าดึงกระดาษติดอย่างรุนแรงหรือแกะชิ้นส่วนภายในเครื่องขณะมีไฟ",
    },
    {
        "id": "printer_queue", "category": "Printer", "title": "เอกสารค้างในคิวพิมพ์",
        "symptom": "เอกสารค้างในคิวพิมพ์", "priority": "ต่ำ",
        "likely_cause": "อาจเกิดจากงานพิมพ์ก่อนหน้าค้าง การเชื่อมต่อขาดหาย หรือไดรเวอร์/บริการพิมพ์มีปัญหา",
        "steps": [
            "ตรวจสอบว่าเลือกเครื่องพิมพ์ถูกตัวและเครื่องพร้อมใช้งาน",
            "รอสักครู่แล้วตรวจสอบว่ามีงานพิมพ์ซ้ำหรือไม่ เพื่อป้องกันพิมพ์ซ้ำหลายชุด",
            "ยกเลิกเฉพาะงานของตนเองหากทำได้และเป็นไปตามนโยบายองค์กร",
            "แจ้ง IT หากคิวพิมพ์ยังค้างหรือมีงานของผู้ใช้อื่นติดอยู่",
        ],
        "escalate_when": "คิวพิมพ์ของหลายคนค้างหรือบริการพิมพ์หยุดทำงาน",
        "safety_note": "อย่าลบคิวพิมพ์ส่วนกลางหรือรีสตาร์ต Print Server เอง",
    },
    {
        "id": "no_power", "category": "Hardware", "title": "คอมพิวเตอร์เปิดไม่ติด",
        "symptom": "คอมพิวเตอร์เปิดไม่ติด", "priority": "สูง",
        "likely_cause": "อาจเกิดจากไฟไม่เข้า อะแดปเตอร์/สายไฟผิดปกติ แบตเตอรี่หมด หรืออุปกรณ์ภายในขัดข้อง",
        "steps": [
            "ตรวจสอบเต้ารับและการเสียบสายไฟ/อะแดปเตอร์ โดยไม่เปิดฝาเครื่อง",
            "ถอดอุปกรณ์ USB ที่ไม่จำเป็น แล้วทดลองเปิดเครื่องอีกครั้ง",
            "สังเกตไฟสถานะ เสียงพัดลม หรือไฟกระพริบ และจดรูปแบบที่พบ",
            "หากยังไม่ติด ให้หยุดทดลองซ้ำและติดต่อ IT/ผู้ให้บริการซ่อม",
        ],
        "escalate_when": "มีกลิ่นไหม้ เครื่องร้อนผิดปกติ ของเหลวหก หรือไม่มีไฟสถานะเลย",
        "safety_note": "ห้ามแกะอะแดปเตอร์/Power Supply หรือเปิดเครื่องหากยังมีไฟเลี้ยง",
    },
    {
        "id": "overheating", "category": "Hardware", "title": "เครื่องร้อนหรือพัดลมดังผิดปกติ",
        "symptom": "เครื่องร้อนหรือพัดลมดังผิดปกติ", "priority": "สูง",
        "likely_cause": "อาจเกิดจากช่องระบายอากาศอุดตัน ภาระงานสูง พัดลมผิดปกติ หรือระบบระบายความร้อนมีปัญหา",
        "steps": [
            "บันทึกงานและปิดโปรแกรมที่ไม่จำเป็นหากเครื่องยังตอบสนอง",
            "วางเครื่องบนพื้นผิวแข็ง ไม่ปิดกั้นช่องระบายอากาศ",
            "หากเครื่องร้อนมาก ให้ปิดเครื่องและปล่อยให้เย็นในพื้นที่ปลอดภัย",
            "ติดต่อ IT หากอาการเกิดซ้ำหรือมีเสียงเสียดสี/กลิ่นผิดปกติ",
        ],
        "escalate_when": "เครื่องร้อนจนสัมผัสไม่ได้ มีกลิ่นไหม้ ดับเอง หรือพัดลมไม่หมุน",
        "safety_note": "อย่าใช้ของแหลมแหย่ช่องระบายอากาศหรือเปิดฝาเพื่อซ่อมเอง",
    },
    {
        "id": "audio_problem", "category": "Hardware", "title": "ไมโครโฟนหรือลำโพงไม่ทำงาน",
        "symptom": "ไมโครโฟนหรือลำโพงไม่ทำงาน", "priority": "ต่ำ",
        "likely_cause": "อาจเกิดจากเลือกอุปกรณ์เสียงผิด ระดับเสียงถูกปิด สิทธิ์แอป หรือไดรเวอร์",
        "steps": [
            "ตรวจสอบปุ่ม Mute และระดับเสียงทั้งบนอุปกรณ์และใน Windows",
            "เลือก Output/Input device ให้ตรงกับอุปกรณ์ที่ต้องการใช้",
            "ตรวจสอบสิทธิ์ไมโครโฟนของแอปที่ได้รับอนุญาต",
            "ทดสอบกับแอปที่ได้รับอนุมัติอีกหนึ่งแอป และแจ้ง IT หากยังไม่ทำงาน",
        ],
        "escalate_when": "อุปกรณ์ไม่ปรากฏใน Windows หรือมีผลต่อการประชุม/งานสำคัญ",
        "safety_note": "อย่าดาวน์โหลดไดรเวอร์จากเว็บไม่เป็นทางการ",
    },
]

CATEGORIES = list(dict.fromkeys(issue["category"] for issue in ISSUES))


def get_issue_by_id(issue_id: str) -> dict[str, Any] | None:
    """Return the knowledge-base entry that matches an ID."""
    for issue in ISSUES:
        if issue["id"] == issue_id:
            return issue.copy()
    return None


def get_issues_by_category(category: str) -> list[dict[str, Any]]:
    """Return all issues in a category; category='ทั้งหมด' returns all entries."""
    if category == "ทั้งหมด":
        return [issue.copy() for issue in ISSUES]
    return [issue.copy() for issue in ISSUES if issue["category"] == category]


def search_knowledge_base(query: str = "", category: str = "ทั้งหมด") -> list[dict[str, Any]]:
    """Search issue title, symptom, likely causes, and troubleshooting steps."""
    query = query.strip().casefold()
    results: list[dict[str, Any]] = []
    for issue in get_issues_by_category(category):
        searchable = " ".join([
            issue["title"], issue["symptom"], issue["category"],
            issue["likely_cause"], " ".join(issue["steps"]),
        ]).casefold()
        if not query or query in searchable:
            results.append(issue)
    return results


def diagnose_issue(issue_id: str) -> dict[str, Any]:
    """Apply rule-based diagnosis and return safe troubleshooting guidance.

    This is not a machine-learning model and does not call an external AI API.
    It matches a selected symptom to a reviewed knowledge-base rule.
    """
    issue = get_issue_by_id(issue_id)
    if issue is None:
        raise ValueError(f"ไม่พบรหัสปัญหา: {issue_id}")
    return {
        "issue_id": issue["id"],
        "category": issue["category"],
        "title": issue["title"],
        "symptom": issue["symptom"],
        "priority": issue["priority"],
        "likely_cause": issue["likely_cause"],
        "steps": list(issue["steps"]),
        "escalate_when": issue["escalate_when"],
        "safety_note": issue["safety_note"],
    }


def make_record(issue_id: str, user_notes: str = "", attempted_steps: str = "") -> dict[str, Any]:
    """Create one history record using the chosen rule and the supplied context."""
    result = diagnose_issue(issue_id)
    return {
        "id": uuid.uuid4().hex[:8].upper(),
        "created_at": datetime.now().astimezone().isoformat(timespec="minutes"),
        "category": result["category"],
        "issue_id": result["issue_id"],
        "symptom": result["symptom"],
        "priority": result["priority"],
        "status": "รอดำเนินการ",
        "likely_cause": result["likely_cause"],
        "steps": result["steps"],
        "escalate_when": result["escalate_when"],
        "safety_note": result["safety_note"],
        "user_notes": user_notes.strip(),
        "attempted_steps": attempted_steps.strip(),
        "resolution_notes": "",
    }


def load_records(path: str | Path) -> list[dict[str, Any]]:
    """Load local JSON history; return an empty list if no valid file exists."""
    file_path = Path(path)
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_records(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Save records atomically to a local JSON file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
    temp_path.replace(file_path)


def update_record_status(
    records: list[dict[str, Any]], record_id: str, status: str, resolution_notes: str = ""
) -> list[dict[str, Any]]:
    """Return records with one matching record updated; leave other records intact."""
    if status not in STATUSES:
        raise ValueError(f"สถานะไม่ถูกต้อง: {status}")
    found = False
    updated = []
    for record in records:
        copied = dict(record)
        if copied.get("id") == record_id:
            copied["status"] = status
            copied["resolution_notes"] = resolution_notes.strip()
            found = True
        updated.append(copied)
    if not found:
        raise ValueError(f"ไม่พบรายการประวัติ: {record_id}")
    return updated


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return simple dashboard metrics from a list of history records."""
    total = len(records)
    resolved = sum(1 for row in records if row.get("status") == "แก้ไขแล้ว")
    forwarded = sum(1 for row in records if row.get("status") == "ส่งต่อ IT")
    open_cases = total - resolved - forwarded
    resolution_rate = round((resolved / total) * 100, 1) if total else 0.0
    category_counts: dict[str, int] = {}
    for row in records:
        category = str(row.get("category", "ไม่ระบุ"))
        category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "total": total,
        "resolved": resolved,
        "forwarded": forwarded,
        "open": open_cases,
        "resolution_rate": resolution_rate,
        "category_counts": category_counts,
    }
