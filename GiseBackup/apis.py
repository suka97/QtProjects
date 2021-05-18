from array import array
from io import BytesIO
import pycurl, json


def null():
    pass


def upload_ninja(file_non_ascii):
    file = file_non_ascii.encode("utf-8")
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)
    
    crl.setopt(crl.URL, 'https://tmp.ninja/upload.php')
    crl.setopt(crl.POST, 1)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPPOST, [('files[]', (crl.FORM_FILE, file))])
    crl.perform()
    crl.close()

    data = {
            'header' : header.getvalue().decode('UTF-8'),
            'body' : response.getvalue().decode('UTF-8')
            }
    return json.loads(data['body'])['files'][0]['url']


def ml_getAccessToken(refreshToken):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    crl.setopt(crl.URL, 'https://api.mercadolibre.com/oauth/token')
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.POST, 1)
    crl.setopt(crl.POSTFIELDS,
        'grant_type=authorization_code&' +
        'client_id=5949631012072735&' +
        'client_secret=ZICgoJbTmwKspWK22qWfv5M0wLEFNk3h&' +
        'code='+refreshToken+'&' +
        'redirect_uri=https%3A%2F%2Fingia.com.ar%2FtestAPI%2FgiseAPI%2F'
        )
    crl.setopt(crl.HTTPHEADER, [
        'accept: application/json',
        'content-type: application/x-www-form-urlencoded',
        'Cookie: _d2id=697f3ef3-abde-45a8-99f0-0854a8a9babd-n'
        ])

    try:
        crl.perform()
        crl.close()
        data = {
            'header' : header.getvalue().decode('UTF-8'),
            'body' : response.getvalue().decode('UTF-8')
            }
        return str(json.loads(data['body'])['access_token'])
    except:
        return 'ERROR'


def ml_itemsScroll(access_token, scroll_id):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    url = 'https://api.mercadolibre.com/users/'+ml_getUserId(access_token)+'/items/search?search_type=scan'
    if scroll_id != '' : url += '&scroll_id=' + scroll_id
    crl.setopt(crl.URL, url)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPHEADER, [
        'Authorization: Bearer '+access_token,
        'content-type: application/x-www-form-urlencoded',
        ])

    crl.perform()
    crl.close()
    data = {
        'header' : header.getvalue().decode('UTF-8'),
        'body' : response.getvalue().decode('UTF-8')
        }
    return json.loads(data['body'])


def ml_getProducts(access_token):
    products = []
    rta = ml_itemsScroll(access_token, '')
    while len(rta['results']) > 0:
        products += rta['results']
        rta = ml_itemsScroll(access_token, rta['scroll_id'])
    return products


def ml_getProductDetail(access_token, product_id):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    url = 'https://api.mercadolibre.com/items/' + product_id
    crl.setopt(crl.URL, url)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPHEADER, [
        'Authorization: Bearer '+access_token,
        ])

    crl.perform()
    crl.close()
    data = {
        'header' : header.getvalue().decode('UTF-8'),
        'body' : response.getvalue().decode('UTF-8')
        }
    rta = json.loads(data['body'])
    imagenes = []
    for i in rta['pictures']: imagenes.append(i['url'])
    return {
        'id' : rta['id'],
        'title' : rta['title'].strip().replace('/','-'),
        'category_id' : rta['category_id'],
        'price' : rta['price'],
        'base_price' : rta['base_price'],
        'imagenes' : imagenes,
        'attributes' : ml_getProductAttributes(rta['attributes']),
        'description' : ml_getProductDesc(access_token, product_id)
    }


def ml_getProductDesc(access_token, product_id):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    url = 'https://api.mercadolibre.com/items/' + product_id + '/description'
    crl.setopt(crl.URL, url)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPHEADER, [
        'Authorization: Bearer '+access_token,
        ])

    crl.perform()
    crl.close()
    data = {
        'header' : header.getvalue().decode('UTF-8'),
        'body' : response.getvalue().decode('UTF-8')
        }
    return json.loads(data['body'])['plain_text']


def ml_getProductAttributes(att_array):
    salida = {}
    for att in att_array:
        if att['id'] == 'DEPTH': salida['prof'] = att['value_name']
        if att['id'] == 'HEIGHT': salida['altura'] = att['value_name']
        if att['id'] == 'WIDTH': salida['ancho'] = att['value_name']
        if att['id'] == 'MODEL': salida['modelo'] = att['value_name']
        if att['id'] == 'COOKIE_CUTTER_SHAPE': salida['forma'] = att['value_name']
    return salida


def ml_getUserId(access_token):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    url = 'https://api.mercadolibre.com/users/me'
    crl.setopt(crl.URL, url)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPHEADER, [
        'Authorization: Bearer '+access_token,
        ])

    crl.perform()
    crl.close()
    data = {
        'header' : header.getvalue().decode('UTF-8'),
        'body' : response.getvalue().decode('UTF-8')
        }
    return str(json.loads(data['body'])['id'])


def publicar(access_token, data, imagenes):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)
    
    crl.setopt(crl.URL, 'https://api.mercadolibre.com/items?access_token='+access_token)
    crl.setopt(crl.POST, 1)
    crl.setopt(pycurl.SSL_VERIFYPEER, 0)
    crl.setopt(pycurl.SSL_VERIFYHOST, 0)
    crl.setopt(crl.HTTPHEADER, [
        'Content-Type: application/json'
      ])
    crl.setopt(crl.POSTFIELDS, json.dumps({
        "title" : data['title'],
        "category_id" : data['category_id'],
        "price" : data['price'],
        "currency_id" : "ARS",
        "available_quantity" : 100,
        "buying_mode" : "buy_it_now",
        "condition" : "new",
        "listing_type_id" : "gold_pro",
        "description" : {
            "plain_text" : data['description']
        },
        "sale_terms" : [
            {
                "id" :  "WARRANTY_TYPE",
                "name" :  "Tipo de garantía",
                "value_id" :  "6150835",
                "value_name" :  "Sin garantía",
                "value_struct" :  null(),
                "values" :  [
                    {
                        "id" :  "6150835",
                        "name" :  "Sin garantía",
                        "struct" :  null()
                    }
                ]
            }
        ],
        "pictures" : imagenes,
        "attributes" : [
            {
                "id" :  "BRAND",
                "name" :  "Marca",
                "value_id" :  "7234693",
                "value_name" :  "Gisegi3D",
                "value_struct" :  null(),
                "values" :  [
                    {
                    "id" :  "7234693",
                    "name" :  "Gisegi3D",
                    "struct" :  null()
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "COOKIE_CUTTER_SHAPE",
                "name" :  "Forma",
                "value_id" :  null(),
                "value_name" :  data['attributes']['forma'],
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  null(),
                    "name" :  data['attributes']['forma'],
                    "struct" :  null()
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "DEPTH",
                "name" :  "Profundidad",
                "value_id" :  null(),
                "value_name" :  data['attributes']['prof'],
                "value_struct" :  {
                "number" :  float(data['attributes']['prof'].split(' ')[0]),
                "unit" :  data['attributes']['prof'].split(' ')[1]
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  data['attributes']['prof'],
                    "struct" :  {
                        "number" :  float(data['attributes']['prof'].split(' ')[0]),
                        "unit" :  data['attributes']['prof'].split(' ')[1]
                        }
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "HEIGHT",
                "name" :  "Altura",
                "value_id" :  null(),
                "value_name" :  data['attributes']['altura'],
                "value_struct" :  {
                "number" :  float(data['attributes']['altura'].split(' ')[0]),
                "unit" :  data['attributes']['altura'].split(' ')[1]
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  data['attributes']['altura'],
                    "struct" :  {
                        "number" :  float(data['attributes']['altura'].split(' ')[0]),
                        "unit" :  data['attributes']['altura'].split(' ')[1]
                        }
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "ITEM_CONDITION",
                "name" :  "Condición del ítem",
                "value_id" :  "2230284",
                "value_name" :  "Nuevo",
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  "2230284",
                    "name" :  "Nuevo",
                    "struct" :  null()
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "MODEL",
                "name" :  "Modelo",
                "value_id" :  null(),
                "value_name" :  data['attributes']['modelo'],
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  null(),
                    "name" :  data['attributes']['modelo'],
                    "struct" :  null()
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "SALE_FORMAT",
                "name" :  "Formato de venta",
                "value_id" :  "1359391",
                "value_name" :  "Unidad",
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  "1359391",
                    "name" :  "Unidad",
                    "struct" :  null()
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            },
            {
                "id" :  "WIDTH",
                "name" :  "Ancho",
                "value_id" :  null(),
                "value_name" :  data['attributes']['ancho'],
                "value_struct" :  {
                "number" :  float(data['attributes']['ancho'].split(' ')[0]),
                "unit" :  data['attributes']['ancho'].split(' ')[1]
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  data['attributes']['ancho'],
                    "struct" :  {
                        "number" :  float(data['attributes']['ancho'].split(' ')[0]),
                        "unit" :  data['attributes']['ancho'].split(' ')[1]
                        }
                    }
                ],
                "attribute_group_id" :  "OTHERS",
                "attribute_group_name" :  "Otros"
            }
        ]
    }))
    
    crl.perform()
    crl.close()
    data = {
        'header' : header.getvalue().decode('UTF-8'),
        'body' : response.getvalue().decode('UTF-8')
        }
    return json.loads(data['body'])['id']