from fastapi import FastAPI, Request
import payplug
import requests
import json

app = FastAPI()

# --------------- Helper Functions ---------------

def get_info_energyz(item_id, column_ids):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ",  # REPLACE with your Monday.com API key!
        "Content-Type": "application/json"
    }
    query = """
    query ($itemId: [ID!]) {
      items (ids: $itemId) {
        column_values {
          id
          value
        }
      }
    }
    """
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
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ",
        "Content-Type": "application/json"
    }
    query = """
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
    """
    variables = {
        "itemId": [item_id],
        "columnId": [formula_column_id]
    }
    data = {"query": query, "variables": variables}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        try:
            display_value = result["data"]["items"][0]["column_values"][0]["display_value"]
            return display_value
        except (KeyError, IndexError):
            return None
    else:
        return None

def get_customer_id(payment_data):
    if 'metadata' in payment_data and 'customer_id' in payment_data['metadata']:
        return payment_data['metadata']['customer_id']
    else:
        return None

# --------------- Accompte 1 ---------------
def send_url_energyz(url, id_, id_insta):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{id_}, board_id:{id_insta}, column_values: \"{{\\\"lien_internet__1\\\" : {{\\\"url\\\" : \\\"{url}\\\", \\\"text\\\":\\\"Payer\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print(json.loads(r.text))

def create_payment_ENERGYZ(installateur, id_, Email, Adresse, Prix):
    #payplug.set_secret_key('sk_live_41JDNiBjQYV5rL3lqXnTKS') # Uncomment for production
    payplug.set_secret_key('sk_test_6aOfTUHBKVOihUBBv9OvrM')  # Uncomment for testing
    payment_data = {
        'amount': int(float(Prix)) * 100,
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
            'customer_insta': installateur
        },
    }
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return None

def set_payer_energyz(IDM):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{IDM}, board_id:1631185124, column_values: \"{{\\\"statut0__1\\\" : {{\\\"label\\\" : \\\"Payé\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)

# --------------- Accompte 2 ---------------
def send_url_energyz2(url, id_, id_insta):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{id_}, board_id:{id_insta}, column_values: \"{{\\\"link_mkrspe1k\\\" : {{\\\"url\\\" : \\\"{url}\\\", \\\"text\\\":\\\"Payer\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print(json.loads(r.text))

def create_payment_ENERGYZ2(installateur, id_, Email, Adresse, Prix):
    #payplug.set_secret_key('sk_live_41JDNiBjQYV5rL3lqXnTKS') # Uncomment for production
    payplug.set_secret_key('sk_test_6aOfTUHBKVOihUBBv9OvrM')  # Uncomment for testing
    payment_data = {
        'amount': int(float(Prix)) * 100,
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
        'notification_url': 'https://energyz-server-li4d.onrender.com/energyz_notif_2',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return None

def set_payer_energyz2(IDM):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{IDM}, board_id:1631185124, column_values: \"{{\\\"statut0__1\\\" : {{\\\"label\\\" : \\\"Payé acompte 2\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)

# --------------- Accompte 3 ---------------
def send_url_energyz3(url, id_, id_insta):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{id_}, board_id:{id_insta}, column_values: \"{{\\\"link_mkrteth2\\\" : {{\\\"url\\\" : \\\"{url}\\\", \\\"text\\\":\\\"Payer\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print(json.loads(r.text))

def create_payment_ENERGYZ3(installateur, id_, Email, Adresse, Prix):
    #payplug.set_secret_key('sk_live_41JDNiBjQYV5rL3lqXnTKS') # Uncomment for production
    payplug.set_secret_key('sk_test_6aOfTUHBKVOihUBBv9OvrM')  # Uncomment for testing
    payment_data = {
        'amount': int(float(Prix)) * 100,
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
        'notification_url': 'https://energyz-server-li4d.onrender.com/energyz_notif_3',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return None

def set_payer_energyz3(IDM):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{IDM}, board_id:1631185124, column_values: \"{{\\\"statut0__1\\\" : {{\\\"label\\\" : \\\"Payé acompte 3\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)

# --------------- Accompte 4 ---------------
def send_url_energyz4(url, id_, id_insta):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{id_}, board_id:{id_insta}, column_values: \"{{\\\"link_mkrtvjt2\\\" : {{\\\"url\\\" : \\\"{url}\\\", \\\"text\\\":\\\"Payer\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print(json.loads(r.text))

def create_payment_ENERGYZ4(installateur, id_, Email, Adresse, Prix):
    #payplug.set_secret_key('sk_live_41JDNiBjQYV5rL3lqXnTKS') # Uncomment for production
    payplug.set_secret_key('sk_test_6aOfTUHBKVOihUBBv9OvrM')  # Uncomment for testing
    payment_data = {
        'amount': int(float(Prix)) * 100,
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
        'notification_url': 'https://energyz-server-li4d.onrender.com/energyz_notif_4',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return None

def set_payer_energyz4(IDM):
    apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = f"mutation {{change_multiple_column_values(item_id:{IDM}, board_id:1631185124, column_values: \"{{\\\"statut0__1\\\" : {{\\\"label\\\" : \\\"Payé acompte 4\\\"}}}}\") {{id}}}}"
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)

# -------------------- ENDPOINTS ----------------------

@app.post("/to_pay_energyz")
async def to_pay_energyz(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        columns_data = get_info_energyz(id_, ['e_mail__1', 'lieu__1'])
        address = columns_data["lieu__1"]["address"]
        email = columns_data["e_mail__1"]["email"]
        prix = get_formula_column_value(id_, 'formula_mkpwgwad')
        if not prix:
            print("No prix found")
            return {"status": "error", "message": "Prix not found"}
        url = create_payment_ENERGYZ(_insta, id_, email, address, prix)
        if url:
            send_url_energyz(url, id_, '1631185124')
    except Exception as e:
        print("Error:", e)
    return {"status": "processed"}

@app.post("/energyz_notif")
async def energyz_notif(request: Request):
    body = await request.json()
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            set_payer_energyz(idm)
        except Exception as e:
            print("Error in notif:", e)
    return {"status": "processed"}

@app.post("/to_pay_energyz_2")
async def to_pay_energyz_2(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        columns_data = get_info_energyz(id_, ['e_mail__1', 'lieu__1'])
        address = columns_data["lieu__1"]["address"]
        email = columns_data["e_mail__1"]["email"]
        prix = get_formula_column_value(id_, 'formula_mkrt4fpf')
        if not prix:
            print("No prix found")
            return {"status": "error", "message": "Prix not found"}
        url = create_payment_ENERGYZ2(_insta, id_, email, address, prix)
        if url:
            send_url_energyz2(url, id_, '1631185124')
    except Exception as e:
        print("Error:", e)
    return {"status": "processed"}

@app.post("/energyz_notif_2")
async def energyz_notif_2(request: Request):
    body = await request.json()
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            set_payer_energyz2(idm)
        except Exception as e:
            print("Error in notif_2:", e)
    return {"status": "processed"}

@app.post("/to_pay_energyz_3")
async def to_pay_energyz_3(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        columns_data = get_info_energyz(id_, ['e_mail__1', 'lieu__1'])
        address = columns_data["lieu__1"]["address"]
        email = columns_data["e_mail__1"]["email"]
        prix = get_formula_column_value(id_, 'formula_mkrtqv0z')
        if not prix:
            print("No prix found")
            return {"status": "error", "message": "Prix not found"}
        url = create_payment_ENERGYZ3(_insta, id_, email, address, prix)
        if url:
            send_url_energyz3(url, id_, '1631185124')
    except Exception as e:
        print("Error:", e)
    return {"status": "processed"}

@app.post("/energyz_notif_3")
async def energyz_notif_3(request: Request):
    body = await request.json()
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            set_payer_energyz3(idm)
        except Exception as e:
            print("Error in notif_3:", e)
    return {"status": "processed"}

@app.post("/to_pay_energyz_4")
async def to_pay_energyz_4(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        columns_data = get_info_energyz(id_, ['e_mail__1', 'lieu__1'])
        address = columns_data["lieu__1"]["address"]
        email = columns_data["e_mail__1"]["email"]
        prix = get_formula_column_value(id_, 'formula_mkrt5v2h')
        if not prix:
            print("No prix found")
            return {"status": "error", "message": "Prix not found"}
        url = create_payment_ENERGYZ4(_insta, id_, email, address, prix)
        if url:
            send_url_energyz4(url, id_, '1631185124')
    except Exception as e:
        print("Error:", e)
    return {"status": "processed"}

@app.post("/energyz_notif_4")
async def energyz_notif_4(request: Request):
    body = await request.json()
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            set_payer_energyz4(idm)
        except Exception as e:
            print("Error in notif_4:", e)
    return {"status": "processed"}
