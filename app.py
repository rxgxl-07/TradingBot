from flask import Flask, request, jsonify
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

GMAIL_ADDRESS = "raguleceskct@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("qnul ipvs qlqu vvvw", "")
SEND_TO_EMAIL = "raguleceskct@gmail.com"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = SEND_TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SEND_TO_EMAIL, msg.as_string())

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            raw = request.data.decode("utf-8")
            data = {"raw_alert": raw}

        print(f"Received alert: {data}")

        ticker = data.get("ticker", "Unknown")
        action = data.get("action", "Alert")
        price = data.get("price", "N/A")

        subject = f"📈 TradingView Signal: {ticker} — {action}"
        body = f"""
TradingView Alert Received
==========================
Ticker : {ticker}
Action : {action}
Price  : {price}

Raw Data:
{json.dumps(data, indent=2)}

--
This is an automated signal. Always do your own research before trading.
"""
        send_email(subject, body)
        return jsonify({"status": "success", "message": "Email sent"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Trading Signal Server is running! ✅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)