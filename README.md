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

## แก้คำแปลและสร้างตัวติดตั้ง

```sh
git clone https://github.com/kaoitp/bloodborne-thai.git
cd bloodborne-thai
```

แก้ไฟล์ JSON ใน [`th/`](th/) ด้วย UTF-8 โดยคง ID ของข้อความ ตัวแปร และแท็กจัดรูปแบบไว้ ชื่อไฟล์บอกตารางของเกม เช่น `item.24.json` สำหรับคำอธิบายไอเทม เริ่มจาก [คู่มือศัพท์](docs/terminology.md) และ [ตารางวิจัยศัพท์](docs/terminology-research.md) ได้

ใช้ Python 3.13 แล้วรันคำสั่งจากโฟลเดอร์ที่ clone มา

**Windows (PowerShell)**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller==6.22.3
.\build.ps1
```

**Linux x86-64 (Bash)**

```bash
python3.13 -m venv .venv-linux
.venv-linux/bin/python -m pip install -r requirements.txt pyinstaller==6.22.3
bash build.sh
```

ชุดติดตั้งจะอยู่ใน `out/` ขั้นตอน build ใช้ไฟล์ใน repo ส่วนขั้นติดตั้งและทดสอบใช้สำเนาเกมของคุณเอง บน Linux ต้องมี `ldd`, `objdump` และ `objcopy` [ข้อกำหนด PyInstaller](https://pyinstaller.org/en/stable/requirements.html#gnu-linux)

ระหว่างแก้คำแปล ใช้ Python จาก venv รัน `python tools/install.py install GAME_FOLDER` เพื่อทดสอบ และ `python tools/install.py restore GAME_FOLDER` เพื่อคืนไฟล์เดิม หากต้องการข้อความอ้างอิงภาษาอังกฤษ ให้รัน `python tools/build.py export GAME_FOLDER` กับสำเนาเกมอังกฤษที่ยังไม่ได้ติดตั้งม็อด ไฟล์ที่สกัดไว้ใน `source/en/` ถูกตั้งให้ Git ข้าม

ดูสคริปต์ประกอบงานแปลจากรอบก่อนใน [`tools/editorial-history/`](tools/editorial-history/)

## เครดิตและสิทธิ์

Bloodborne เป็นเกมของ FromSoftware และ Sony Interactive Entertainment โครงการนี้เป็นม็อดแฟนเมดแบบไม่เป็นทางการ

คำแปลภาษาไทยและเครื่องมือติดตั้งจัดทำโดยทีม Bloodborne Thai

โค้ด เครื่องมือ และ workflow ที่ทีมเขียนเผยแพร่ภายใต้ [MIT License](LICENSE) สามารถใช้ แก้ไข และแจกต่อได้ตามเงื่อนไขในไฟล์นั้น ทีมเปิดให้ใช้และปรับปรุงตารางคำแปลสำหรับม็อดนี้ สิทธิ์ MIT ครอบคลุมโค้ดของทีม ส่วนเนื้อหาเกมและคำแปลที่อิงเนื้อหาเกมอยู่นอกขอบเขตของไลเซนส์นี้

ฟอนต์ Anuphan เผยแพร่ภายใต้ SIL Open Font License 1.1 โดยมีไฟล์ `OFL.txt` ในชุดติดตั้ง [ต้นทางฟอนต์](https://github.com/google/fonts/tree/95f4904fc8bcf26d3420fe315560c96417c6dec7/ofl/anuphan)

ชุดติดตั้งแนบประกาศสิทธิ์ของ Python และ fontTools ในโฟลเดอร์ `licenses/` ส่วนชุด Linux แนบประกาศสิทธิ์ของ zlib ด้วย [ต้นฉบับสิทธิ์ Python](https://github.com/python/cpython/blob/v3.13.18/LICENSE) · [ต้นฉบับสิทธิ์ zlib](https://github.com/madler/zlib/blob/v1.2.11/zlib.h)
