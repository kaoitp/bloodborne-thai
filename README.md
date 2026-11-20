# Bloodborne Thai

ม็อดภาษาไทยสำหรับ Bloodborne บน PC ผ่าน bbport แปลบทสนทนา เมนู ชื่อไอเทม อาวุธ สถานที่ และฉายาตัวละคร โดยถอดเสียงชื่อเฉพาะเป็นภาษาไทย [bbport](https://github.com/deadinside28/bloodborne_pc)

## ดาวน์โหลด

| ระบบ | ดาวน์โหลดรุ่นล่าสุด |
| --- | --- |
| Windows x64 | [ดาวน์โหลด Windows (.zip)](https://github.com/kaoitp/bloodborne-thai/releases/latest/download/bloodborne-thai-windows-x64.zip) |
| Linux x86-64 | [ดาวน์โหลด Linux (.tar.gz)](https://github.com/kaoitp/bloodborne-thai/releases/latest/download/bloodborne-thai-linux-x64.tar.gz) |

[ประวัติการออกรุ่น](https://github.com/kaoitp/bloodborne-thai/releases) · [ดาวน์โหลด SHA256SUMS.txt](https://github.com/kaoitp/bloodborne-thai/releases/latest/download/SHA256SUMS.txt)

ใช้ `SHA256SUMS.txt` ตรวจสอบไฟล์ที่ดาวน์โหลด ใน PowerShell ใช้ `Get-FileHash .\bloodborne-thai-windows-x64.zip -Algorithm SHA256` ใน Linux ให้วางไฟล์ checksum ไว้ข้างไฟล์ที่ดาวน์โหลด แล้วใช้ `sha256sum --ignore-missing --check SHA256SUMS.txt`

ดูเลขเวอร์ชันของชุดติดตั้งได้ในไฟล์ `VERSION` ที่อยู่ในไฟล์ดาวน์โหลด

## ติดตั้ง

ต้องมีสำเนาเกม **CUSA03173 v1.09** ที่มีไฟล์ภาษา **English (UK)** (`enggb`) เดิม และสิทธิ์เขียนโฟลเดอร์เกม ตัวติดตั้งบรรจุคำแปล ฟอนต์ และ Python runtime แล้ว ให้นำไฟล์เกมจากสำเนาของคุณเองมาใช้

ปิดเกมก่อนติดตั้งหรืออัปเดตม็อดภาษาไทย ตัวติดตั้งใช้ขั้นตอนเดียวกันทั้งสองกรณี

### Windows x64

1. แตกไฟล์ ZIP แล้วเปิด `Install Thai.bat`
2. เลือก `1` แล้วลากโฟลเดอร์ `CUSA03173` หรือ `dvdroot_ps4` ลงในหน้าต่างตัวติดตั้งแล้วกด Enter
3. เปิดเกมและเลือกภาษา **English (UK)**

### Linux x86-64

แตกไฟล์ `.tar.gz` แล้วเปิด Terminal ในโฟลเดอร์ที่แตกไฟล์ ระบุพาธไปยังโฟลเดอร์ `CUSA03173` หรือ `dvdroot_ps4`

```bash
./bloodborne-thai install "/path/to/CUSA03173"
```

ใช้ `./bloodborne-thai` เพื่อเปิดเมนูแบบโต้ตอบบน Linux ได้ จากนั้นเปิดเกมและเลือกภาษา **English (UK)** ชุดติดตั้ง Linux จาก GitHub Actions สร้างและทดสอบบน Ubuntu 22.04 การติดตั้งบน Steam Deck ยังไม่ได้ทดสอบ

### อัปเดตม็อดหรือคืนไฟล์เดิม

หากจะอัปเดตม็อด ให้เปิดตัวติดตั้งรุ่นใหม่แล้วเลือก `1` หรือใช้คำสั่ง `install` บน Linux โดยเลือกโฟลเดอร์เกมเดิม ตัวติดตั้งจะตรวจหา `bloodborne-thai-backup` และใช้ไฟล์ต้นฉบับในนั้นสร้างไฟล์ม็อดรุ่นใหม่ เก็บโฟลเดอร์นี้ไว้สำหรับอัปเดตและคืนไฟล์เดิม

หากจะถอนม็อดหรืออัปเดตตัวเกม ให้คืนไฟล์เดิมก่อนด้วยเมนู `2` หรือรัน `./bloodborne-thai restore "/path/to/CUSA03173"` บน Linux

## แจ้งปัญหาหรือเสนอคำแปล

ระบุรุ่นของม็อด ระบบปฏิบัติการ รุ่นเกม และข้อความที่พบ ถ้าเป็นปัญหาคำแปล ให้แนบภาพหน้าจอ ชื่อไอเทมหรือตัวละคร และฉากที่พบเท่าที่จำได้ [GitHub Issues](https://github.com/kaoitp/bloodborne-thai/issues)


## เครดิตและสิทธิ์

Bloodborne เป็นเกมของ FromSoftware และ Sony Interactive Entertainment โครงการนี้เป็นม็อดแฟนเมดแบบไม่เป็นทางการ

คำแปลภาษาไทยและเครื่องมือติดตั้งจัดทำโดยทีม Bloodborne Thai

ฟอนต์ Anuphan เผยแพร่ภายใต้ SIL Open Font License 1.1 โดยมีไฟล์ `OFL.txt` ในชุดติดตั้ง [ต้นทางฟอนต์](https://github.com/google/fonts/tree/95f4904fc8bcf26d3420fe315560c96417c6dec7/ofl/anuphan)

ชุดติดตั้งแนบประกาศสิทธิ์ของ Python และ fontTools ในโฟลเดอร์ `licenses/` ส่วนชุด Linux แนบประกาศสิทธิ์ของ zlib ด้วย [ต้นฉบับสิทธิ์ Python](https://github.com/python/cpython/blob/v3.13.18/LICENSE) · [ต้นฉบับสิทธิ์ zlib](https://github.com/madler/zlib/blob/v1.2.11/zlib.h)
