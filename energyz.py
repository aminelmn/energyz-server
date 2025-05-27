
#---------------------------------- Paiment energyz -----------------------------

def send_url_energyz(url,id_,id_insta):
    apiKey = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ'
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : apiKey}

    query5 = "mutation {change_multiple_column_values(item_id:"+str(id_)+", board_id:"+str(id_insta)+", column_values: \"{\\\"lien_internet__1\\\" : {\\\"url\\\" : \\\""+url+"\\\", \\\"text\\\":\\\"Payer\\\"}}\") {id}}"
    #print(query5)
    data = {'query' : query5}
    r = requests.post(url=apiUrl,json=data, headers=headers) # make request
    results=json.loads(r.text)
    print(results)
def create_payment_ENERGYZ(installateur,id_,Email,Adresse,Prix):
    payplug.set_secret_key('sk_live_41JDNiBjQYV5rL3lqXnTKS')
    #payplug.set_secret_key('sk_test_6aOfTUHBKVOihUBBv9OvrM')
    
    payment_data = {
    'amount': int(Prix)*100,
    'currency': 'EUR',
    'save_card': False,
    'customer': {
    'email': Email,
    'address1': Adresse,
    
    'first_name': installateur,
    'last_name':installateur


    },
    'hosted_payment': {
    'sent_by':'OTHER',
    'return_url': 'https://energyz-company.monday.com/',
    'cancel_url': 'https://energyz-company.monday.com/',
    },
    'notification_url': 'https://www.energy-consult-center.dev/energyz_notif',
    'metadata': {

    'customer_id': id_,
    'customer_insta': installateur
    },
    }
    print(payment_data)
    try:
        payment = payplug.Payment.create(**payment_data)
        print (f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return (f"An error occurred: {e}")



def get_info_energyz(item_id, column_ids=1676598283):
    # API endpoint
    url = "https://api.monday.com/v2"

    # Headers
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ",
        "Content-Type": "application/json"
    }

    # GraphQL query to get item data
    query = """
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
    """

    # Variables for the query
    variables = {
        "itemId": [item_id]
    }

    # Make the request
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    # Check if the request was successful
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
def get_customer_id(payment_data):
    # Check if 'metadata' key exists and contains 'customer_id'
    if 'metadata' in payment_data and 'customer_id' in payment_data['metadata']:
        return payment_data['metadata']['customer_id']
    else:
        return None
    
def set_payer_energyz(IDM) :
    apiKey = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ'
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : apiKey}
    query2 = "mutation {change_multiple_column_values(item_id:"+str(IDM)+",board_id :1631185124, column_values: \"{\\\"statut0__1\\\" : {\\\"label\\\" : \\\"Payé\\\"}}\") {id}}" 
    data = {'query' : query2}
    print("audit_payé")
    
    r = requests.post(url=apiUrl, json=data, headers=headers)
import requests
import json

def get_formula_column_value(item_id, formula_column_id):
    """
    Get the display value of a specific formula column for an item in monday.com
    
    Parameters:
    api_key (str): Your monday.com API key
    item_id (int): The ID of the item containing the formula column
    formula_column_id (str): The ID of the formula column
    
    Returns:
    str: The display value of the formula column
    """
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
    
    data = {
        "query": query,
        "variables": variables
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        # Extract the display_value from the response
        try:
            display_value = result["data"]["items"][0]["column_values"][0]["display_value"]
            return display_value
        except (KeyError, IndexError):
            return "Formula value not found"
    else:
        return f"Request failed with status code {response.status_code}"

# Example usage
# api_key = "your_api_key_here"
# item_id = 1234567890
# formula_column_id = "formula_column"
# formula_value = get_formula_column_value(api_key, item_id, formula_column_id)
# print(formula_value)

@app.post("/to_pay_energyz")
async def projets(request: Dict[Any, Any]):
    try :
        print(request)
        id_=request['event']['pulseId']
        _insta=request['event']['pulseName']
        print(id_, _insta)
        column_ids = ['e_mail__1', 'lieu__1','formula_mkpwgwad']  # Remplacez par les ID des colonnes (email et adresse)
#
        columns_data = get_info_energyz(id_, column_ids)
        print(columns_data)
        data=[columns_data["lieu__1"]["address"],columns_data["e_mail__1"]["email"]]
        print(data)
        prix=get_formula_column_value(id_, 'formula_mkpwgwad')
#
        url=create_payment_ENERGYZ(_insta,id_,data[1],data[0],int(prix))
        #
        print('url______________',url)
        ##send_url_energyz
        send_url_energyz(url,id_,'1631185124')

        
  
    except :
        pass
    return request


@app.post("/energyz_notif")
async def projets(request: Dict[Any, Any]):
    
    data=request
    print(data)
    if data['is_paid']==True and data['is_live']==True :
        
        try :
            print(request)
            idm=get_customer_id(request)
            set_payer_energyz(idm)

        except :
            pass
    return request