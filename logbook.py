import os
import random
import datetime
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()
USERNAME = os.getenv("KEMNAKER_USERNAME")
PASSWORD = os.getenv("KEMNAKER_PASSWORD")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LOGBOOK PAIRS – dipilih acak setiap harinya (1 pasangan per hari)
# ---------------------------------------------------------------------------
LOGBOOK_PAIRS = [
    {
        "activity": (
            "Melakukan troubleshooting jaringan lokal (LAN) dan memastikan koneksi internet stabil. "
            "Kegiatan meliputi pengecekan koneksi, identifikasi gangguan jaringan, serta memastikan "
            "perangkat dapat terhubung dengan baik di lingkungan Rumah Sakit Elim Rantepao."
        ),
        "lesson": (
            "Memperoleh pembelajaran mengenai langkah-langkah troubleshooting dan manajemen jaringan "
            "komputer sederhana. Selain itu, memahami pentingnya melakukan pengecekan koneksi secara "
            "sistematis agar gangguan jaringan dapat diketahui dan ditangani dengan tepat."
        ),
        "obstacle": (
            "Belum ada kendala yang dialami sampai saat ini dan seluruh kegiatan dapat dilakukan dengan "
            "baik. Setiap pekerjaan dapat diselesaikan sesuai dengan kebutuhan dan tidak terdapat masalah "
            "yang menghambat proses pekerjaan di lingkungan rumah sakit."
        ),
    },
    {
        "activity": (
            "Melakukan pemeliharaan rutin pada perangkat komputer dan pengecekan sistem operasi. "
            "Kegiatan meliputi pemeriksaan kondisi hardware, update software, serta memastikan komputer "
            "dapat digunakan dengan baik oleh tenaga medis dan staf administrasi."
        ),
        "lesson": (
            "Memperoleh pemahaman mengenai pentingnya pemeliharaan rutin software dan hardware untuk "
            "menjaga performa komputer. Selain itu, belajar melakukan pengecekan kondisi sistem agar "
            "perangkat tetap dapat digunakan secara optimal di lingkungan rumah sakit."
        ),
        "obstacle": (
            "Tidak menemui kendala berarti selama menjalankan kegiatan hari ini. Seluruh tugas dapat "
            "dilakukan dengan lancar dan apabila terdapat masalah kecil, masih dapat ditangani dengan "
            "baik sehingga tidak mengganggu jalannya pekerjaan."
        ),
    },
    {
        "activity": (
            "Membantu instalasi dan konfigurasi software pendukung kerja pada divisi IT rumah sakit. "
            "Kegiatan meliputi proses instalasi aplikasi, konfigurasi software sesuai kebutuhan pengguna, "
            "serta memastikan aplikasi dapat berjalan dengan baik dan mendukung operasional rumah sakit."
        ),
        "lesson": (
            "Memperoleh pembelajaran mengenai proses instalasi dan konfigurasi software sesuai kebutuhan "
            "pengguna. Selain itu, memahami bahwa setiap aplikasi perlu dikonfigurasi dengan tepat agar "
            "dapat berjalan dengan baik dan mendukung pekerjaan sehari-hari."
        ),
        "obstacle": (
            "Belum ada kendala yang dialami sampai saat ini dan seluruh kegiatan dapat dilakukan dengan "
            "baik. Setiap proses instalasi dan konfigurasi dapat diselesaikan sesuai kebutuhan tanpa "
            "adanya kendala yang berarti selama kegiatan berlangsung."
        ),
    },
    {
        "activity": (
            "Melakukan backup data harian pada sistem lokal dan memastikan penyimpanan data aman. "
            "Kegiatan meliputi pengecekan data penting, proses pencadangan, serta memastikan hasil "
            "backup tersimpan dengan baik untuk mengurangi risiko kehilangan data di rumah sakit."
        ),
        "lesson": (
            "Memahami pentingnya melakukan backup data secara rutin untuk mengurangi risiko kehilangan "
            "atau kerusakan data. Selain itu, mempelajari bahwa hasil backup perlu diperiksa dan disimpan "
            "pada media yang aman agar dapat digunakan kembali jika diperlukan."
        ),
        "obstacle": (
            "Tidak menemui kendala berarti dalam proses backup data yang dilakukan hari ini. Seluruh "
            "proses pencadangan dapat berjalan dengan lancar dan data berhasil disimpan dengan baik "
            "tanpa adanya masalah yang menghambat pekerjaan."
        ),
    },
    {
        "activity": (
            "Mengecek status dan performa perangkat keras seperti PC dan laptop yang digunakan oleh "
            "staf administrasi dan tenaga medis. Kegiatan meliputi pemeriksaan kondisi perangkat, "
            "penggunaan resource sistem, serta mengidentifikasi masalah yang dapat menghambat pekerjaan."
        ),
        "lesson": (
            "Memperoleh pembelajaran mengenai cara melakukan pengecekan performa perangkat keras dan "
            "sistem komputer. Selain itu, memahami indikator dasar seperti penggunaan CPU, RAM, "
            "penyimpanan, dan kondisi perangkat untuk mengidentifikasi masalah lebih awal."
        ),
        "obstacle": (
            "Belum ada kendala yang dialami selama melakukan pengecekan perangkat komputer. Seluruh "
            "pemeriksaan dapat dilakukan dengan lancar dan tidak ditemukan masalah yang cukup serius "
            "untuk menghambat pekerjaan pengguna di lingkungan rumah sakit."
        ),
    },
    {
        "activity": (
            "Melakukan perawatan dan pembersihan fisik pada perangkat keras seperti printer, scanner, "
            "serta CPU di unit layanan medis. Kegiatan meliputi pembersihan debu, pengecekan kabel "
            "konektor, dan refilling tinta printer agar siap digunakan untuk cetak dokumen medis."
        ),
        "lesson": (
            "Memahami pentingnya perawatan fisik perangkat periferal rumah sakit guna mencegah kerusakan "
            "akibat penumpukan debu dan masalah teknis sederhana, serta memastikan ketersediaan perangkat "
            "pendukung administrasi pasien tetap optimal."
        ),
        "obstacle": (
            "Tidak mengalami kendala dalam proses pembersihan dan perawatan fisik perangkat. Semua unit "
            "dapat dibersihkan dan dicek fungsinya dengan baik tanpa mengganggu aktivitas pelayanan rumah sakit."
        ),
    },
    {
        "activity": (
            "Membantu penanganan dan penataan manajemen kabel (cable management) pada ruang server dan "
            "stasiun kerja staf. Kegiatan meliputi kerapian pengkabelan LAN dan listrik agar terlihat rapi, "
            "aman, serta mempermudah identifikasi port saat pengecekan."
        ),
        "lesson": (
            "Belajar pentingnya kerapian penataan kabel untuk keamanan operasional dan kemudahan kendali "
            "jalur koneksi. Manajemen kabel yang terstruktur sangat membantu mempercepat penanganan saat "
            "terjadi masalah pada port tertentu."
        ),
        "obstacle": (
            "Proses penataan berjalan lancar tanpa kendala teknis. Pengorganisasian kabel dapat diselesaikan "
            "sesuai dengan standar kerapian ruangan tanpa memutuskan jaringan aktif."
        ),
    },
    {
        "activity": (
            "Melakukan pengecekan serta pemutakhiran (update) antivirus dan pemindaian keamanan sistem pada "
            "komputer staf. Kegiatan dilakukan untuk mencegah potensi ancaman malware, virus, atau "
            "program berbahaya yang dapat merusak data rumah sakit."
        ),
        "lesson": (
            "Memperoleh pemahaman mendasar mengenai keamanan sistem informasi dan perlindungan endpoint. "
            "Mengetahui bahwa pemutakhiran basis data antivirus secara berkala sangat krusial untuk "
            "menjaga privasi dan integritas data medis."
        ),
        "obstacle": (
            "Tidak ada kendala berarti selama proses pemindaian dan update antivirus berlangsung. Seluruh "
            "perangkat komputer dapat diperbarui dengan lancar tanpa ada infeksi virus yang berdampak fatal."
        ),
    },
    {
        "activity": (
            "Melakukan pengecekan fungsi dan performa perangkat Uninterruptible Power Supply (UPS) serta "
            "stabilizer pada unit perangkat vital. Kegiatan meliputi pengujian indikator baterai dan "
            "memastikan cadangan listrik berfungsi baik saat terjadi pemadaman mendadak."
        ),
        "lesson": (
            "Memahami pentingnya keandalan sistem daya cadangan bagi kelangsungan operasional IT rumah "
            "sakit. Mengetahui cara memeriksa indikator kelayakan baterai UPS guna mengantisipasi kerusakan "
            "perangkat akibat lonjakan voltase atau mati listrik."
        ),
        "obstacle": (
            "Pemeriksaan UPS dan sistem daya berjalan dengan lancar. Seluruh unit penyuplai daya cadangan "
            "dalam kondisi siap pakai tanpa ada gangguan teknis."
        ),
    },
    {
        "activity": (
            "Melakukan inventarisasi dan pendataan aset perangkat IT di lingkungan rumah sakit. "
            "Kegiatan meliputi pencatatan nomor seri, kondisi kelayakan perangkat, spesifikasi singkat, "
            "serta lokasi penempatan unit PC maupun printer."
        ),
        "lesson": (
            "Memahami proses dokumentasi dan manajemen aset IT secara sistematis. Pendataan yang akurat "
            "sangat membantu tim IT dalam memetakan kebutuhan peremajaan atau perbaikan perangkat di "
            "masa mendatang."
        ),
        "obstacle": (
            "Seluruh proses pendataan dan pendokumentasian aset berjalan tertib dan lancar tanpa ada "
            "kendala fisik maupun ketidaksesuaian data yang signifikan."
        ),
    },
]

# Koordinat Rumah Sakit Elim Rantepao (bypass geolocation popup browser)
LOCATION = {"latitude": -2.9726, "longitude": 119.8979, "accuracy": 10}

BASE_URL = "https://monev.maganghub.kemnaker.go.id"


async def _type_vue_field(page, locator, text: str) -> None:
    """
    Isi field Vue/Vuetify dengan cara yang men-trigger reactive events:
    1. Klik untuk fokus
    2. Select all & hapus isi lama
    3. Type karakter per karakter (dispatch keyboard events)
    4. Dispatch 'input' event secara eksplisit
    """
    await locator.click()
    await locator.select_text()
    await page.keyboard.press("Control+a")
    await page.keyboard.press("Delete")
    await locator.type(text, delay=10)   # type() → trigger key events per karakter
    # Dispatch 'input' event eksplisit agar Vue reactive watcher bereaksi
    await locator.dispatch_event("input")
    await locator.dispatch_event("change")


async def run_logbook() -> str:
    """
    Jalankan alur pengisian logbook secara async menggunakan Playwright.
    Mengembalikan string pesan hasil (sukses/gagal) untuk dikirim ke Telegram.
    """
    # Lewati hari Minggu (weekday 6)
    if datetime.datetime.now().weekday() == 6:
        return "📅 Hari Minggu – logbook tidak dijalankan."

    if not USERNAME or not PASSWORD:
        return "⚠️ KEMNAKER_USERNAME atau KEMNAKER_PASSWORD belum diisi di .env"

    pair     = random.choice(LOGBOOK_PAIRS)
    activity = pair["activity"]
    lesson   = pair["lesson"]
    obstacle = pair["obstacle"]

    today    = datetime.date.today().isoformat()
    edit_url = f"{BASE_URL}/dashboard/riwayat?date={today}&view=edit"
    # Setelah submit berhasil, URL berubah ke view=detail
    detail_url_pattern = f"date={today}&view=detail"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                geolocation=LOCATION,
                permissions=["geolocation"],
            )
            page = await context.new_page()

            # ------------------------------------------------------------------
            # 1. Buka halaman utama (redirect ke SSO login jika belum login)
            # ------------------------------------------------------------------
            logger.info("Membuka portal MONEV…")
            await page.goto(BASE_URL, timeout=60_000)
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                logger.warning("Timeout waiting for networkidle after opening portal, proceeding...")
            logger.info("URL awal: %s", page.url)

            # ------------------------------------------------------------------
            # 2. Login via SSO
            # ------------------------------------------------------------------
            if "login" in page.url:
                logger.info("Halaman login SSO ditemukan, melakukan login…")

                # input[name='username'] id='username'
                email_field = page.locator(
                    "input[name='username'], input[id='username']"
                ).first
                await email_field.wait_for(state="visible", timeout=20000)
                await email_field.fill(USERNAME)
                logger.info("Username diisi")

                # input[id='password']
                pwd_field = page.locator("input[id='password']").first
                await pwd_field.wait_for(state="visible", timeout=10000)
                await pwd_field.fill(PASSWORD)
                logger.info("Password diisi")

                # button[type='submit'] → "Masuk"
                login_btn = page.locator("button[type='submit']").first
                await login_btn.wait_for(state="visible", timeout=10000)
                await login_btn.click()
                logger.info("Tombol 'Masuk' diklik – menunggu redirect ke MONEV…")

                await page.wait_for_url(
                    lambda url: "maganghub.kemnaker.go.id" in url and "login" not in url,
                    timeout=30000,
                )
                await page.wait_for_load_state("networkidle")
                logger.info("Login berhasil, URL: %s", page.url)

            # ------------------------------------------------------------------
            # 3. Navigasi ke halaman edit laporan hari ini
            # ------------------------------------------------------------------
            logger.info("Navigasi ke halaman edit: %s", edit_url)
            await page.goto(edit_url, timeout=30_000)
            await page.wait_for_load_state("networkidle")

            # Tunggu form Vuetify selesai render
            try:
                await page.wait_for_selector("textarea.v-field__input", timeout=15000)
                logger.info("Form Vuetify berhasil dimuat")
            except Exception:
                logger.warning("Textarea Vuetify belum terdeteksi setelah 15s, lanjutkan…")

            # ------------------------------------------------------------------
            # 4. Isi form – gunakan type() agar Vue reactive events ter-trigger
            # ------------------------------------------------------------------
            logger.info("Mengisi form logbook…")

            # Textarea 1: Uraian aktivitas (placeholder & id dari HTML)
            ta_activity = page.locator(
                "textarea[placeholder*='uraian aktivitas'], textarea[id='input-v-7']"
            ).first
            await ta_activity.wait_for(state="visible", timeout=10000)
            await _type_vue_field(page, ta_activity, activity)
            logger.info("Uraian aktivitas diisi (%d karakter)", len(activity))

            # Textarea 2: Pembelajaran
            ta_lesson = page.locator(
                "textarea[placeholder*='pembelajaran'], textarea[id='input-v-10']"
            ).first
            await ta_lesson.wait_for(state="visible", timeout=10000)
            await _type_vue_field(page, ta_lesson, lesson)
            logger.info("Pembelajaran diisi (%d karakter)", len(lesson))

            # Textarea 3: Kendala
            ta_obstacle = page.locator(
                "textarea[placeholder*='kendala'], textarea[id='input-v-13']"
            ).first
            await ta_obstacle.wait_for(state="visible", timeout=10000)
            await _type_vue_field(page, ta_obstacle, obstacle)
            logger.info("Kendala diisi (%d karakter)", len(obstacle))

            # ------------------------------------------------------------------
            # 5. Centang checkbox pernyataan (id=checkbox-v-15)
            # ------------------------------------------------------------------
            logger.info("Mencentang checkbox pernyataan…")
            checkbox = page.locator(
                "input[id='checkbox-v-15'], "
                "input[type='checkbox'][aria-label*='menyatakan']"
            ).first
            await checkbox.wait_for(state="attached", timeout=10000)
            if not await checkbox.is_checked():
                await checkbox.click(force=True)
                logger.info("Checkbox berhasil dicentang")
            else:
                logger.info("Checkbox sudah tercentang")

            # Screenshot sebelum submit untuk verifikasi isian – simpan ke folder terstruktur
            import os
            os.makedirs("debug_picture", exist_ok=True)
            pre_submit_path = f"debug_picture/debug_pre_submit_{today}.png"
            await page.screenshot(path=pre_submit_path, full_page=True)
            logger.info("Screenshot pre-submit disimpan: %s", pre_submit_path)

            # ------------------------------------------------------------------
            # 6. Klik tombol Simpan / Submit
            # ------------------------------------------------------------------
            logger.info("Menekan tombol submit…")
            submit_selectors = [
                "button[type='submit']",
                "button:has-text('Simpan')",
                "button:has-text('Kirim')",
                "button:has-text('Submit')",
            ]
            submitted = False
            for sel in submit_selectors:
                try:
                    btn = page.locator(sel).first
                    await btn.scroll_into_view_if_needed()
                    if await btn.is_visible(timeout=3000):
                        await btn.click(force=True)
                        submitted = True
                        logger.info("Submit diklik: %s", sel)
                        break
                except Exception as e:
                    logger.debug("Gagal klik %s: %s", sel, e)
                    continue

            if not submitted:
                logger.warning("Tombol submit tidak terdeteksi dengan selector biasa.")

            # Tangani modal konfirmasi jika muncul
            try:
                confirm_btn = page.locator(
                    "button:has-text('Ya'), button:has-text('Confirm'), button:has-text('OK')"
                ).first
                if await confirm_btn.is_visible(timeout=4000):
                    await confirm_btn.click()
                    logger.info("Modal konfirmasi diklik")
            except Exception:
                pass

            # ------------------------------------------------------------------
            # 7. Tunggu URL berubah dari view=edit → view=detail (indikasi sukses)
            # ------------------------------------------------------------------
            logger.info("Menunggu redirect ke view=detail…")
            try:
                await page.wait_for_url(
                    lambda url: detail_url_pattern in url,
                    timeout=15000,
                )
                logger.info("✅ Redirect ke view=detail berhasil: %s", page.url)
                status_ok = True
            except Exception:
                logger.warning("Tidak ada redirect ke view=detail dalam 15 detik")
                status_ok = False

            # Screenshot setelah submit – simpan ke folder terstruktur
            import os
            os.makedirs("debug_picture", exist_ok=True)
            post_submit_path = f"debug_picture/debug_post_submit_{today}.png"
            await page.screenshot(path=post_submit_path, full_page=True)
            logger.info("Screenshot post-submit disimpan: %s", post_submit_path)

            final_url = page.url
            logger.info("URL akhir: %s", final_url)

            await browser.close()

        # ------------------------------------------------------------------
        # 8. Tentukan status akhir
        # ------------------------------------------------------------------
        if status_ok or detail_url_pattern in final_url:
            status = "✅ *Logbook Berhasil Disubmit!*"
        elif not submitted:
            status = "⚠️ Tombol submit tidak ditemukan – silakan cek dashboard manual."
        else:
            status = (
                "⚠️ *Logbook mungkin gagal disimpan.*\n"
                f"URL setelah submit: `{final_url}`\n"
                f"Silakan cek dashboard."
            )

        msg = (
            f"{status}\n\n"
            f"📅 *Tanggal:* {datetime.date.today().strftime('%d %B %Y')}\n\n"
            f"📝 *Uraian Aktivitas:*\n{activity}\n\n"
            f"📚 *Pembelajaran:*\n{lesson}\n\n"
            f"🚧 *Kendala:*\n{obstacle}"
        )
        return msg

    except Exception as exc:
        logger.exception("Logbook submission error")
        return f"❌ *Logbook Gagal!*\nError: `{exc}`"
