# IT Buddy - Smart IT Assistant

เว็บแอปต้นแบบสำหรับช่วยผู้ใช้ตรวจสอบปัญหา IT เบื้องต้น โดยใช้ Python + Streamlit พร้อมฐานความรู้, ระบบวิเคราะห์แบบ rule-based, Dashboard และประวัติที่แก้ไขสถานะได้

> **ขอบเขตที่ควรระบุในการนำเสนอ:** IT Buddy ใช้เงื่อนไข Python จับคู่อาการกับฐานความรู้ที่เตรียมไว้ ไม่ได้เชื่อมต่อ Generative AI API และไม่ได้ตรวจคอมพิวเตอร์จากระยะไกล โดย Generative AI ถูกใช้เป็นผู้ช่วยในการออกแบบ/เขียน/ตรวจสอบโค้ดและจัดทำเอกสารประกอบ

## ไฟล์ในโปรเจกต์

- `app.py` - หน้าเว็บแอป Streamlit
- `it_buddy_core.py` - ฐานความรู้และ logic หลัก เช่น diagnose, search, save/load, update status, summary
- `IT_Buddy_Guide.ipynb` - คู่มือประกอบโครงงาน พร้อม Flowchart, ตัวอย่างโค้ด และผลทดสอบ 2 กรณี
- `requirements.txt` - libraries ที่จำเป็น
- `tests/test_core.py` - automated tests สำหรับฟังก์ชันหลัก
- `AI_Usage_Evidence.pdf` - บันทึกสรุปการใช้ AI ประกอบการพัฒนา (อ่านข้อแนะนำด้านหลักฐานด้านล่าง)
- `AI_Usage_Evidence.docx` - ต้นฉบับแก้ไขได้สำหรับกรอกชื่อผู้จัดทำ/รหัสนิสิต
- `VIDEO_PRESENTATION_SCRIPT.md` - บทพูดวิดีโอ 3-5 นาทีและ checklist ก่อนอัด
- `assets/flowchart.png` - ภาพ Flowchart ประกอบคู่มือ
- `run_app.bat` - เปิดแอปบน Windows หลังติดตั้ง dependencies แล้ว

## วิธีเปิดใช้งานบน Windows

1. ติดตั้ง Python 3.10 หรือใหม่กว่า จากเว็บไซต์ทางการของ Python และเลือกตัวเลือก Add Python to PATH ระหว่างติดตั้ง
2. แตกไฟล์ ZIP และเปิด Command Prompt/PowerShell ในโฟลเดอร์ `IT_Buddy_Project` (หรือดับเบิลคลิก `run_app.bat` เพื่อให้สคริปต์ตรวจสอบ/ติดตั้ง libraries แล้วเปิดแอป)
3. สร้าง virtual environment (แนะนำ):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. ติดตั้ง libraries:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. เปิดเว็บแอป:

   ```powershell
   python -m streamlit run app.py
   ```

6. Browser จะเปิดหน้าเว็บโดยอัตโนมัติ โดยปกติใช้ `http://localhost:8501`

ถ้า PowerShell บล็อกการ Activate ให้เปิด Command Prompt แล้วใช้ `.venv\Scripts\activate.bat` หรือรัน `python -m streamlit run app.py` ด้วย environment ที่ติดตั้ง dependencies แล้ว

## วิธีทดสอบ

```powershell
python -m unittest discover -s tests -v
```

ชุดทดสอบครอบคลุมการวิเคราะห์อาการ, การค้นหาฐานความรู้, การอัปเดตสถานะ และการบันทึก/โหลด JSON

## วิธี Deploy ด้วย Streamlit Community Cloud

1. สร้าง repository บน GitHub แล้วอัปโหลดไฟล์โปรเจกต์ทั้งหมด โดยให้ `app.py`, `it_buddy_core.py` และ `requirements.txt` อยู่ในตำแหน่งที่เข้าถึงได้ง่าย
2. เปิด [Streamlit Community Cloud](https://share.streamlit.io/) และเชื่อมต่อบัญชี GitHub
3. กด **Create app** เลือก repository, branch และ entrypoint เป็น `app.py`
4. กด **Deploy** แล้วรอให้ระบบติดตั้ง dependencies และเปิดแอป
5. คัดลอก URL ของแอปสำหรับส่งงานหรือใส่ในวิดีโอนำเสนอ

คู่มือทางการ: [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

### ข้อควรทราบเรื่องประวัติ

เวอร์ชันนี้บันทึกประวัติไว้ใน `it_buddy_data.json` บน filesystem ของแอป เหมาะสำหรับต้นแบบและสาธิตในชั้นเรียน แต่ไม่ได้ออกแบบสำหรับเก็บข้อมูลถาวรบนระบบ Cloud หรือรองรับผู้ใช้หลายคนพร้อมกัน การรีสตาร์ต/นำแอปขึ้นใหม่อาจทำให้ข้อมูลที่บันทึกบนพื้นที่ชั่วคราวหายได้ หากจะใช้งานจริงควรเปลี่ยนไปใช้ฐานข้อมูลที่เหมาะสม เช่น PostgreSQL/Supabase/SQLite ที่อยู่บน persistent storage พร้อมระบบยืนยันตัวตนและสิทธิ์

## วิธีทดสอบผลงานเพื่อสาธิต

**กรณีที่ 1: Network**
1. เปิดเมนู Smart Diagnosis
2. เลือก Network > เชื่อมต่อ Wi-Fi ไม่ได้
3. กดวิเคราะห์ปัญหาและบันทึกประวัติ
4. ตรวจสอบสาเหตุ ขั้นตอนแนะนำ ระดับความสำคัญ และรหัสรายการ

**กรณีที่ 2: Hardware**
1. เปิด Smart Diagnosis อีกครั้ง
2. เลือก Hardware > คอมพิวเตอร์เปิดไม่ติด
3. กดวิเคราะห์ปัญหาและบันทึกประวัติ
4. เปรียบเทียบวิธีแก้ไขและระดับความสำคัญกับกรณีที่ 1

จากนั้นไปที่ History เพื่อเปลี่ยนสถานะรายการเป็น “กำลังดำเนินการ” หรือ “แก้ไขแล้ว” และกลับไป Dashboard เพื่อดูสถิติที่เปลี่ยนตามข้อมูลจริง

## ความเป็นส่วนตัวและความปลอดภัย

- ใช้ข้อมูลสมมติในการสาธิต ห้ามกรอกรหัสผ่าน, MFA code, ข้อมูลลูกค้า หรือข้อมูลลับขององค์กร
- อย่าทำขั้นตอนที่ต้องใช้สิทธิ์ Administrator หรือเปลี่ยนค่าระบบองค์กร หากไม่ได้รับอนุญาต
- คำแนะนำนี้เป็นแนวทางเบื้องต้น ให้ส่งต่อเจ้าหน้าที่ IT เมื่อมีความเสี่ยงหรือกระทบระบบสำคัญ

## หมายเหตุเกี่ยวกับหลักฐานการใช้ AI

ไฟล์ `AI_Usage_Evidence.pdf` เป็น **บันทึกสรุปการใช้ AI สำหรับจัดระเบียบงาน** ไม่ใช่ภาพหน้าจอจริงหรือ Share Link ที่ระบบแชตสร้างขึ้น กรุณาเพิ่มภาพหน้าจอ Prompt/คำตอบจริงจากบทสนทนาที่ใช้พัฒนางาน หรือสร้าง Share Link จากหน้าระบบแชต และส่งตามรูปแบบที่ผู้สอนกำหนด
