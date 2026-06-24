from flask import Flask, request, jsonify
import smtplib
import requests
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ===================== YOUR SETTINGS =====================
GROQ_API_KEY = os.environ.get("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", "")
GMAIL_ADDRESS = "raguleceskct@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("iana gkix xspo bywn", "")
SEND_TO_EMAIL = "raguleceskct@gmail.com"
# =========================================================

def analyze_with_groq(alert_data):
    """Send alert data to Groq and get analysis."""
    
    prompt = f"""You are a trading signal analyst. A TradingView alert just triggered with the following data:

{json.dumps(alert_data, indent=2)}

Based on this alert, provide:
1. Signal Summary (BUY / SELL / NEUTRAL)
2. What this signal means in simple terms
3. Suggested action (entry, stop loss, target if possible)
4. Risk warning

Keep it concise and clear. No fluff."""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
    )

    result = response.json()
    print(f"Groq response: {result}")  # This will show us exactly what Groq returns
    if "choices" not in result:
        error_msg = result.get("error", {}).get("message", str(result))
        return f"Groq API Error: {error_msg}"
    return result["choices"][0]["message"]["content"]


def send_email(subject, body):
    """Send email via Gmail SMTP."""
    
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
    """TradingView sends alerts here."""
    
    try:
        # Get data from TradingView
        data = request.get_json(force=True)
        
        if not data:
            # Try plain text
            raw = request.data.decode("utf-8")
            data = {"raw_alert": raw}

        print(f"Received alert: {data}")

        # Analyze with Groq
        analysis = analyze_with_groq(data)

        # Build email
        ticker = data.get("ticker", "Unknown")
        action = data.get("action", "Alert")
        subject = f"📈 TradingView Signal: {ticker} — {action}"
        
        body = f"""
TradingView Alert Received
==========================
{json.dumps(data, indent=2)}

AI Analysis (Groq)
==================
{analysis}

--
This is an automated signal. Always do your own research before trading.
"""

        send_email(subject, body)

        return jsonify({"status": "success", "message": "Signal processed and email sent"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "Trading Signal Server is running! ✅", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)