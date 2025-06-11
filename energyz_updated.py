
#---------------------------------- Paiment energyz -----------------------------
from fastapi import FastAPI, Request
import payplug
import requests 
import json
from fastapi.responses import JSONResponse  

app = FastAPI()

def send_url_energyz(url, id_, id_insta, link_column):
    apiKey = 'your_api_key_here'
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f'''mutation {{
        change_multiple_column_values(item_id: {id_}, board_id: {id_insta}, column_values: "{{\\\"{link_column}\\\": {{\\\"url\\\": \\\"{url}\\\", \\\"text\\\": \\\"Payer\\\"}}}}") {{
            id
        }}
    }}'''
    r = requests.post(url=apiUrl, json={"query": query}, headers=headers)
    print(json.loads(r.text))

def create_payment_ENERGYZ(installateur, id_, Email, Adresse, Prix, acompte_number="1"):
    payplug.set_secret_key('your_payplug_secret_key')
    payment_data = {
        'amount': int(Prix)*100,
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
        print(f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return f"An error occurred: {e}"

def get_info_energyz(item_id, column_ids):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": "your_api_key_here",
        "Content-Type": "application/json"
    }
    query = '''
    query ($itemId: [ID!]) {
      items (ids: $itemId) {
        id
        name
        column_values {
          id
          value
        }
      }
    }
    '''
    variables = {"itemId": [item_id]}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        item_data = response.json()
        result = {}
        items = item_data.get('data', {}).get('items', [])
        for item in items:
            for column in item['column_values']:
                if column['id'] in column_ids:
                    column_value = column['value']
                    if column_value:
                        try:
                            decoded_value = json.loads(column_value)
                            result[column['id']] = decoded_value
                        except json.JSONDecodeError:
                            result[column['id']] = column_value
                    else:
                        result[column['id']] = None
        return result
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

def get_formula_column_value(item_id, formula_column_id):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": "your_api_key_here",
        "Content-Type": "application/json"
    }
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
        try:
            return response.json()["data"]["items"][0]["column_values"][0]["display_value"]
        except:
            return None
    return None

@app.post("/to_pay_energyz")
async def projets(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = ['e_mail__1', 'lieu__1']
        columns_data = get_info_energyz(id_, column_ids)
        data = [columns_data["lieu__1"]["address"], columns_data["e_mail__1"]["email"]]

        acompte_map = {
            "1": ("formula_mkpwgwad", "lien_internet__1"),
            "2": ("formula_mkrt4fpf", "link_mkrspe1k"),
            "3": ("formula_mkrtqv0z", "link_mkrteth2"),
            "4": ("formula_mkrt5v2h", "link_mkrtvjt2")
        }

        for num, (formula_id, link_col) in acompte_map.items():
            prix = get_formula_column_value(id_, formula_id)
            if prix:
                url = create_payment_ENERGYZ(_insta, id_, data[1], data[0], int(prix), acompte_number=num)
                send_url_energyz(url, id_, '1631185124', link_col)
    except Exception as e:
        print("Error:", e)
    return {"status": "processed"}

@app.post("/energyz_notif")
async def projets(request: Request):
    body = await request.json()
    print(body)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = body.get('metadata', {}).get('customer_id')
            acompte = body.get('metadata', {}).get('acompte_number', '1')
            label_map = {
                '1': "Payé",
                '2': "Paiement acompte 2",
                '3': "Paiement acompte 3",
                '4': "Paiement acompte 4"
            }
            label = label_map.get(acompte, "Payé")
            apiKey = 'your_api_key_here'
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            mutation = f'''mutation {{
                change_multiple_column_values(item_id: {idm}, board_id: 1631185124,
                column_values: "{{\\\"statut0__1\\\": {{\\\"label\\\": \\\"{label}\\\"}}}}") {{ id }}
            }}'''
            requests.post(apiUrl, json={"query": mutation}, headers=headers)
        except Exception as e:
            print("Error in notif:", e)
    return {"status": "processed"}
