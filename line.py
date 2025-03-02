from flask import Flask, request
import joblib
import numpy as np
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

# ตั้งค่าคีย์จาก LINE Developers
LINE_ACCESS_TOKEN = "rTcz/mgVZ2A20wEdlUYFK7kb8dnpZQ3nvBtB28bfQ9n2sUJeUqM2rXcM77LoiUDHqR1AM8/X69a/S3JJsYlnjIhcJmbVk7AMscHtBApXSvJKrGg51tiEMWSOaL64QeGmDRFROEowTwqIqeH/VzcxfQdB04t89/1O/w1cDnyilFU="
LINE_SECRET = "35bbc1005fd1a9c673fd5770dd30a1d3"

# โหลดโมเดล Naïve Bayes
model = joblib.load("naive_bayes_model.pkl")

# ตั้งค่า Flask
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # แปลงข้อความให้เป็นตัวเลข
        values = list(map(float, user_message.split(",")))  
        if len(values) != 7:
            reply_text = "กรุณากรอกค่าทั้ง 7 ตัว เช่น: 80,40,40,20,50,6.5,200"
        else:
            features = np.array(values).reshape(1, -1)
            prediction = model.predict(features)
            reply_text = f"ผลลัพธ์ที่คาดการณ์: {prediction[0]}"
    
    except Exception as e:
        reply_text = f"เกิดข้อผิดพลาด: {str(e)}"

    # ส่งข้อความกลับไปยัง LINE
    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=5000, debug=True)
