import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Menggunakan model gemini-1.5-flash (cepat & efisien)
    model = genai.GenerativeModel('gemini-3-flash-preview')
else:
    model = None

async def generate_reply(user_text: str) -> str:
    """Menggunakan Gemini API untuk membuat balasan pintar."""
    if not model:
        return "⚠️ Kunci GEMINI_API_KEY belum diisi di file .env Anda. Bot belum bisa merespons."
    
    try:
        # Memberikan instruksi singkat agar Gemini tahu perannya
        prompt = (
            "Anda adalah asisten bot Telegram (bernama Logbook Bot MONEV) yang bertugas "
            "membantu pengguna terkait pertanyaan umum, jadwal logbook (secara default diset jam 9 pagi), "
            "atau obrolan santai lainnya. Jawablah dengan bahasa Indonesia yang ramah, "
            "singkat, santai namun profesional.\n\n"
            f"Pertanyaan/Pernyataan Pengguna: {user_text}"
        )
        
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Maaf, terjadi kesalahan saat menghubungi AI: {str(e)}"
