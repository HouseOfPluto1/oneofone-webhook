# payment_webhook.py

from flask import Flask, request
from db import grant_access
import hmac, hashlib

IPN_SECRET = "AHAHMl7sqX+ZfGD5mlOsn2khmEcUQiIW"
app = Flask(__name__)

@app.route("/ipn", methods=["POST"])
def handle_ipn():
    data = request.get_json()
    received_hmac = request.headers.get("x-nowpayments-sig")
    computed_hmac = hmac.new(IPN_SECRET.encode(), request.data, hashlib.sha512).hexdigest()

    if received_hmac != computed_hmac:
        return "Invalid signature", 403

    if data["payment_status"] == "confirmed":
        user_id = data["order_id"]
        desc = data.get("order_description", "")
        if "Lifetime" in desc:
            grant_access(user_id, "lifetime")
        else:
            grant_access(user_id, "monthly")

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
