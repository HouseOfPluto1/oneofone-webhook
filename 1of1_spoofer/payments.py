# payments.py

import requests

NOWPAYMENTS_API_KEY = "XAB0FQG-XD04GYT-QBGP8XQ-NCJ10MF"

headers = {
    "x-api-key": NOWPAYMENTS_API_KEY,
    "Content-Type": "application/json"
}

def create_invoice(order_id, amount, desc):
    payload = {
        "price_amount": float(amount),
        "price_currency": "usd",
        # ❌ REMOVE pay_currency so NowPayments handles crypto selection
        "ipn_callback_url": "https://example.com/ipn",
        "order_id": str(order_id),
        "order_description": desc,
        "is_fee_paid_by_user": True  # ✅ Optional: let user cover fees
    }

    try:
        res = requests.post("https://api.nowpayments.io/v1/invoice", json=payload, headers=headers)
        print("NOWPAYMENTS STATUS:", res.status_code)
        print("NOWPAYMENTS RAW TEXT:", res.text)

        json_data = res.json()
        print("NOWPAYMENTS JSON:", json_data)

        return json_data.get("invoice_url")

    except Exception as e:
        print("‼️ Exception occurred while requesting invoice:", str(e))
        return None
