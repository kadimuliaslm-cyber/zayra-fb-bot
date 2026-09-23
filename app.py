import os
from flask import Flask, request, jsonify
import requests
import google.generativeai as genai

app = Flask(__name__)

# গুগল এআই চাবি সেটআপ করা (উদ্ধৃতি চিহ্নের ভেতর আপনার আসল চাবিটি বসাবেন)
GOOGLE_API_KEY ="AQ.Ab8RN6LNzbP0t2KMH1OE9rys0BJq-6IZfVybofaOhZoZrWENcw"
genai.configure(api_key=GOOGLE_API_KEY)

# ফেসবুক টোকেন সেটআপ
FB_PAGE_ACCESS_TOKEN = "EAAYmkkxXWP4BSu6vn5CVUMZAMBqXXtDQVLfUkv8PQH2rGDxCrirqvwqtAGPam8VhVMl89X0RAMZCS8s9A6vku8Yv6xNnNt7ZB1A1ytZAZCRzP1fl9DEp6ZCjrcyDAhwO4OkNtsisgei7qymAye1UIR041GYXNSx1QyAMY2klUNMl4ejjPcSStWo1ZC6PWoiNBZAjC8sO8QZDZD"
VERIFY_TOKEN = "my_secret_webhook_token"

# এআই-এর জন্য প্রম্পট (আপনার জাইরা ফ্যাশন পেজের নিয়মাবলী)
SYSTEM_INSTRUCTION = """
তুমি বাংলাদেশের মেয়েদের পোশাকের পেজ 'Zayra - Women's Fashion' এর একটি স্মার্ট এআই অ্যাসিস্ট্যান্ট।
তোমার কাজ হচ্ছে ক্রেতাদের সাথে খুব নম্রভাবে বাংলায় কথা বলা।
নিয়মাবলী:
- কুশল বিনিময় করো (যেমন: আপু কেমন আছেন? আসসালামু আলাইকুম)।
- পণ্যের দাম, সাইজ ও স্টক সম্পর্কে তথ্য দাও।
- কোনো অর্ডার কনফার্ম করতে চাইলে নাম, মোবাইল নম্বর এবং সম্পূর্ণ ঠিকানা সুন্দরভাবে চেয়ে নাও।
"""

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("WEBHOOK_VERIFIED")
                return challenge, 200
            else:
                return "Verification token mismatch", 403
                
    elif request.method == "POST":
        data = request.json
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        user_text = messaging_event["message"].get("text", "👍")
                        
                        # জেমিনি এআই দিয়ে রিপ্লাই তৈরি করা
                        try:
                            model = genai.GenerativeModel(
                                model_name='gemini-1.5-flash',
                                system_instruction=SYSTEM_INSTRUCTION
                            )
                            ai_response = model.generate_content(user_text)
                            reply_text = ai_response.text
                        except Exception as e:
                            print(f"AI Error: {e}")
                            reply_text = "দুঃখিত আপু, আমার সিস্টেমে একটু সমস্যা হচ্ছে। আমাদের প্রতিনিধি দ্রুত আপনার সাথে যোগাযোগ করবেন।"

                        # ফেসবুকে রিপ্লাই পাঠানো
                        send_fb_message(sender_id, reply_text)
                        
            return "EVENT_RECEIVED", 200
    return "Not Found", 404

def send_fb_message(recipient_id, text_message):
    url = f"https://facebook.com{FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text_message}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
                  
