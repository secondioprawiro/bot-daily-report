import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is not set in .env file!")
        return

    print("====================================================")
    print("Telegram Chat ID Finder Helper")
    print("====================================================")
    print(f"Bot Token: {BOT_TOKEN}")
    print("\nHow to use:")
    print("1. Open Telegram.")
    print("2. Search for your bot (make sure it matches your token).")
    print("3. Click 'Start' or send a message like 'hello' to the bot.")
    print("4. This script will check for new messages and show your Chat ID.\n")
    print("Checking for messages... Press Ctrl+C to stop.")
    
    offset = None
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"timeout": 10}
            if offset:
                params["offset"] = offset
                
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if not data.get("ok"):
                print(f"❌ Telegram API Error: {data.get('description')}")
                time.sleep(5)
                continue
                
            results = data.get("result", [])
            for update in results:
                # Update offset to confirm receipt of this update
                offset = update["update_id"] + 1
                
                if "message" in update:
                    msg = update["message"]
                    chat = msg.get("chat", {})
                    chat_id = chat.get("id")
                    first_name = chat.get("first_name", "")
                    last_name = chat.get("last_name", "")
                    username = chat.get("username", "")
                    text = msg.get("text", "")
                    
                    name = f"{first_name} {last_name}".strip()
                    user_str = f"@{username}" if username else "No username"
                    
                    print("\n====================================================")
                    print("🎉 SUCCESS! FOUND INCOMING MESSAGE:")
                    print(f"👤 Sender Name : {name} ({user_str})")
                    print(f"🆔 Telegram Chat ID: {chat_id}")
                    print(f"💬 Message Text: '{text}'")
                    print("====================================================")
                    print(f"\n👉 Please copy the Chat ID '{chat_id}' and set it in your .env file:")
                    print(f"   TELEGRAM_CHAT_ID={chat_id}")
                    print("====================================================")
                    return
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
