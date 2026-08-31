import os
import random
import datetime
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USERNAME = os.getenv("KEMNAKER_USERNAME")
PASSWORD = os.getenv("KEMNAKER_PASSWORD")

# Perfectly matched pairs so activities align with lessons!
LOGBOOK_PAIRS = [
    {
        "activity": "Melakukan troubleshooting jaringan lokal (LAN) dan memastikan koneksi internet stabil. Kegiatan meliputi pengecekan koneksi, identifikasi gangguan jaringan, serta memastikan perangkat dapat terhubung dengan baik.",
        "lesson": "Memperoleh pembelajaran mengenai langkah-langkah troubleshooting dan manajemen jaringan komputer sederhana. Selain itu, memahami pentingnya melakukan pengecekan koneksi secara sistematis agar gangguan jaringan dapat diketahui dan ditangani dengan tepat.",
        "obstacle": "Belum ada kendala yang dialami sampai saat ini dan seluruh kegiatan dapat dilakukan dengan baik. Setiap pekerjaan dapat diselesaikan sesuai dengan kebutuhan dan tidak terdapat masalah yang menghambat proses pekerjaan."
    },
    {
        "activity": "Melakukan pemeliharaan rutin pada perangkat komputer dan pengecekan sistem. Kegiatan meliputi pemeriksaan kondisi perangkat, pengecekan sistem operasi, serta memastikan komputer dapat digunakan dengan baik.",
        "lesson": "Memperoleh pemahaman mengenai pentingnya pemeliharaan rutin software dan hardware untuk menjaga performa komputer. Selain itu, belajar melakukan pengecekan kondisi sistem agar perangkat tetap dapat digunakan secara optimal.",
        "obstacle": "Tidak menemui kendala berarti selama menjalankan kegiatan hari ini. Seluruh tugas dapat dilakukan dengan lancar dan apabila terdapat masalah kecil, masih dapat ditangani dengan baik sehingga tidak mengganggu pekerjaan."
    },
    {
        "activity": "Membantu instalasi dan konfigurasi software pendukung kerja pada divisi. Kegiatan meliputi proses instalasi aplikasi, konfigurasi software sesuai kebutuhan pengguna, serta memastikan aplikasi dapat berjalan dengan baik.",
        "lesson": "Memperoleh pembelajaran mengenai proses instalasi dan konfigurasi software sesuai kebutuhan pengguna. Selain itu, memahami bahwa setiap aplikasi perlu dikonfigurasi dengan tepat agar dapat berjalan dengan baik dan mendukung pekerjaan.",
        "obstacle": "Belum ada kendala yang dialami sampai saat ini dan seluruh kegiatan dapat dilakukan dengan baik. Setiap proses instalasi dan konfigurasi dapat diselesaikan sesuai kebutuhan tanpa adanya kendala yang berarti."
    },
    {
        "activity": "Melakukan backup data harian pada sistem lokal dan memastikan penyimpanan aman. Kegiatan meliputi pengecekan data, proses pencadangan, serta memastikan hasil backup tersimpan dengan baik untuk mengurangi risiko kehilangan data.",
        "lesson": "Memahami pentingnya melakukan backup data secara rutin untuk mengurangi risiko kehilangan atau kerusakan data. Selain itu, mempelajari bahwa hasil backup perlu diperiksa dan disimpan pada media yang aman agar dapat digunakan kembali.",
        "obstacle": "Tidak menemui kendala berarti dalam proses backup data yang dilakukan hari ini. Seluruh proses pencadangan dapat berjalan dengan lancar dan data berhasil disimpan dengan baik tanpa adanya masalah yang menghambat pekerjaan."
    },
    {
        "activity": "Mengecek status dan performa perangkat keras seperti PC dan laptop rekan kerja. Kegiatan meliputi pemeriksaan kondisi perangkat, penggunaan resource sistem, serta mengidentifikasi masalah yang dapat menghambat pekerjaan.",
        "lesson": "Memperoleh pembelajaran mengenai cara melakukan pengecekan performa perangkat keras dan sistem komputer. Selain itu, memahami indikator dasar seperti penggunaan CPU, RAM, penyimpanan, dan kondisi perangkat untuk mengidentifikasi masalah.",
        "obstacle": "Belum ada kendala yang dialami selama melakukan pengecekan perangkat komputer. Seluruh pemeriksaan dapat dilakukan dengan lancar dan tidak ditemukan masalah yang cukup serius untuk menghambat pekerjaan pengguna."
    }
]

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram token or chat ID is missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print("Telegram notification sent:", response.json())
    except Exception as e:
        print("Failed to send Telegram notification:", e)

def is_holiday_or_sunday():
    today = datetime.datetime.now()
    # Check if Sunday (Weekday 6 is Sunday)
    if today.weekday() == 6:
        return True
    return False

def submit_logbook():
    if is_holiday_or_sunday():
        print("Today is Sunday or a rest day. Skipping logbook submission.")
        return

    # Pick a random matching pair
    pair = random.choice(LOGBOOK_PAIRS)
    activity = pair["activity"]
    lesson = pair["lesson"]
    obstacle = pair["obstacle"]

    print(f"Selected Activity: {activity}")
    print(f"Selected Lesson: {lesson}")
    print(f"Selected Obstacle: {obstacle}")

    with sync_playwright() as p:
        # Launch browser (headless=False so you can watch it happen)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Opening Kemnaker Monev portal...")
            page.goto("https://monev.maganghub.kemnaker.go.id", timeout=60000)

            print("Page title:", page.title())

            # TODO: We will map the exact login and form fields next once we test it!

            # Send success notification to Telegram
            msg = f"✅ *Logbook Submitted Successfully!*\n\n*Aktivitas:* {activity}\n*Pembelajaran:* {lesson}\n*Kendala:* {obstacle}"
            send_telegram_message(msg)

        except Exception as e:
            error_msg = f"❌ *Logbook Submission Failed!*\nError: `{str(e)}`"
            print(error_msg)
            send_telegram_message(error_msg)
        finally:
            browser.close()

if __name__ == "__main__":
    submit_logbook()