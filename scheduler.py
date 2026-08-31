import time
import schedule
import subprocess
import datetime

def run_bot():
    # Jangan jalan jika hari Minggu (weekday == 6)
    if datetime.datetime.now().weekday() == 6:
        print("Hari ini hari Minggu. Scheduler melewati eksekusi.")
        return

    print("--- Menjalankan bot logbook otomatis ---")
    # Memanggil script bot.py menggunakan python di dalam virtual environment
    subprocess.run(["python", "telegram_bot.py"])

# Menjadwalkan setiap hari pada pukul 12:00 siang (atau ganti jam 13:00 sesuai zona waktu Anda)
schedule.every().day.at("12:00").do(run_bot)

print("Scheduler aktif! Menunggu waktu yang ditentukan (Pukul 12:00 setiap hari kecuali Minggu)...")
print("Biarkan terminal ini tetap terbuka agar scheduler berjalan.")

while True:
    schedule.run_pending()
    time.sleep(1)