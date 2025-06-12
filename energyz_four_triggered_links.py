from fastapi import FastAPI, Request
import payplug
import requests
import json

app = FastAPI()

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
PAYPLUG_SECRET = "sk_test_6aOfTUHBKVOihUBBv9OvrM" # test key : "sk_test_6aOfTUHBKVOihUBBv9OvrM" / live key : "sk_live_41JDNiBjQYV5rL3lqXnTKS"
BOARD_ID = "1631185124"

status_trigger_map = {
    "Générer 📑": ("formula_mkpwgwad", "lien_internet__1", "1"),
    "Générer 2": ("formula_mkrt4fpf", "link_mkrspe1k", "2"),
    "Générer 3": ("formula_mkrtqv0z", "link_mkrteth2", "3"),
    "Générer 4": ("formula_mkrt5v2h", "link_mkrtvjt2", "4")
}

label_map = {
    '1': "Payé",
    '2': "Paiement acompte 2",
    '3': "Paiement acompte 3",
    '4': "Paiement acompte 4"
}

def get_info_energyz(item_id, column_ids):
    url = "https://api.monday.com/v2"
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    query = '''
    query ($itemId: [ID!]) {
      items (ids: $itemId) {
        column_values {
          id
          value
          text
        }
      }
    }
    '''
    variables = {"itemId": [item_id]}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return {col["id"]: col for col in result["data"]["items"][0]["column_values"] if col["id"] in column_ids}
    return {}

def get_formula_column_value(item_id, formula_column_id):
    url = "https://api.monday.com/v2"
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    query = '''
    query ($itemId: [ID!], $columnId: [String!]) {
      items (ids: $itemId) {
        column_values(ids: $columnId) {
          ... on FormulaValue {
            id
            display_value
          }
        }
      }
    }
    '''
    variables = {"itemId": [item_id], "columnId": [formula_column_id]}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["items"][0]["column_values"][0]["display_value"]
    return None

def create_payment_ENERGYZ(installateur, id_, Email, Adresse, Prix, acompte_number="1"):
    payplug.set_secret_key(PAYPLUG_SECRET)
    payment_data = {
        'amount': int(float(Prix) * 100),
        'currency': 'EUR',
        'save_card': False,
        'customer': {
            'email': Email,
            'address1': Adresse,
            'first_name': installateur,
            'last_name': installateur
        },
        'hosted_payment': {
            'sent_by': 'OTHER',
            'return_url': 'https://energyz-company.monday.com/',
            'cancel_url': 'https://energyz-company.monday.com/',
        },
        'notification_url': 'https://energyz-server-li4d.onrender.com/energyz_notif',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur,
            'acompte_number': acompte_number
        },
    }
    try:
        payment = payplug.Payment.create(**payment_data)
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return None

def send_url_energyz(url, id_, id_insta, link_column):
    headers = {"Authorization": API_KEY}
    apiUrl = "https://api.monday.com/v2"
    mutation = (
        "mutation {"
        f"change_multiple_column_values(item_id: {id_}, board_id: {id_insta}, "
        f'column_values: "{{\"{link_column}\": {{\"url\": \"{url}\", \"text\": \"Payer\"}}}}") {{ id }}'
        "}"
    )
    r = requests.post(url=apiUrl, json={"query": mutation}, headers=headers)
    print(r.json())

@app.post("/to_pay_energyz")
async def projets(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        status_text = body['event']['value']['label']['text']

        if status_text not in status_trigger_map:
            print("No matching trigger status.")
            return {"status": "ignored"}

        formula_id, link_col, acompte_number = status_trigger_map[status_text]
        column_ids = ['e_mail__1', 'lieu__1']
        info = get_info_energyz(id_, column_ids)
        email = info['e_mail__1']['text']
        address = info['lieu__1']['text']
        prix = get_formula_column_value(id_, formula_id)
        url = create_payment_ENERGYZ(_insta, id_, email, address, prix, acompte_number)
        if url:
            send_url_energyz(url, id_, BOARD_ID, link_col)
    except Exception as e:
        print("Error in webhook:", e)
    return {"status": "processed"}

@app.post("/energyz_notif")
async def projets(request: Request):
    body = await request.json()
    print(body)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = body.get('metadata', {}).get('customer_id')
            acompte = body.get('metadata', {}).get('acompte_number', '1')
            label = label_map.get(acompte, "Payé")
            headers = {"Authorization": API_KEY}
            mutation = (
                "mutation {"
                f"change_multiple_column_values(item_id: {idm}, board_id: {BOARD_ID}, "
                f'column_values: "{{\"statut0__1\": {{\"label\": \"{label}\"}}}}") {{ id }}'
                "}"
            )
            requests.post("https://api.monday.com/v2", json={"query": mutation}, headers=headers)
        except Exception as e:
            print("Error in notif:", e)
    return {"status": "processed"}