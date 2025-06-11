
from fastapi import FastAPI, Request
import payplug
import requests
import datetime

payplug.api_key = "sk_live_wcnT6WgvAxvYFpgxUSVUPB"

app = FastAPI()

def create_payment_ENERGYZ(amount, email, first_name, last_name, acompte_num, item_id):
    payment_data = {
        'amount': int(float(amount) * 100),
        'currency': 'EUR',
        'billing': {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        },
        'hosted_payment': {
            'return_url': 'https://energyz.fr'
        },
        'notification_url': 'https://energyz-server-li4d.onrender.com/energyz_notif',
        'metadata': {
            'acompte_num': acompte_num,
            'item_id': item_id,
        }
    }
    payment = payplug.Payment.create(**payment_data)
    return payment.hosted_payment.payment_url

def send_url_energyz(url, item_id, column_id):
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE1MzA2Mjg0LCJ1aWQiOjExMTE1MjM1LCJpYXQiOjE3MTUwMjA2MzB9.7UraAUXVi7x1NgyIAhsVvV4Cy9RoGQfvBSJfj2-Qh5o",
        "Content-Type": "application/json"
    }
    query = f'''
    mutation {{
      change_column_value(item_id: {item_id}, board_id: 1884832755, column_id: "{column_id}", value: "{{\"url\": \"{url}\", \"text\": \"Payer\"}}" ) {{
        id
      }}
    }}
    '''
    requests.post("https://api.monday.com/v2", json={'query': query}, headers=headers)

@app.post("/to_pay_energyz")
async def generate_all_payments(request: Request):
    payload = await request.json()
    event = payload.get("event", {})
    id_ = event.get("pulseId")
    column_values = event.get("column_values", [])

    def extract(col_id):
        for c in column_values:
            if c["id"] == col_id:
                return c.get("text")
        return None

    first_name = extract("prenom8")
    last_name = extract("nom")
    email = extract("email")
    acompte_info = [
        ("formula_mkpwgwad", "lien_internet__1", "Payé", 1),
        ("formula_mkrt4fpf", "link_mkrspe1k", "Paiement acompte 2", 2),
        ("formula_mkrtqv0z", "link_mkrteth2", "Paiement acompte 3", 3),
        ("formula_mkrt5v2h", "link_mkrtvjt2", "Paiement acompte 4", 4),
    ]

    for formula_col, link_col, _, acompte_num in acompte_info:
        amount = extract(formula_col)
        if amount:
            url = create_payment_ENERGYZ(amount, email, first_name, last_name, acompte_num, id_)
            send_url_energyz(url, id_, link_col)

    return {"status": "All links generated"}

@app.post("/energyz_notif")
async def handle_notification(request: Request):
    data = await request.json()
    metadata = data.get("metadata", {})
    item_id = metadata.get("item_id")
    acompte_num = metadata.get("acompte_num")

    status_mapping = {
        1: "Payé",
        2: "Paiement acompte 2",
        3: "Paiement acompte 3",
        4: "Paiement acompte 4"
    }

    status_label = status_mapping.get(acompte_num)
    if item_id and status_label:
        headers = {
            "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE1MzA2Mjg0LCJ1aWQiOjExMTE1MjM1LCJpYXQiOjE3MTUwMjA2MzB9.7UraAUXVi7x1NgyIAhsVvV4Cy9RoGQfvBSJfj2-Qh5o",
            "Content-Type": "application/json"
        }
        query = f'''
        mutation {{
          change_column_value(item_id: {item_id}, board_id: 1884832755, column_id: "statut0__1", value: "{{\"label\": \"{status_label}\"}}" ) {{
            id
          }}
        }}
        '''
        requests.post("https://api.monday.com/v2", json={'query': query}, headers=headers)

    return {"status": "ok"}
