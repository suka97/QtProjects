from io import BytesIO
import pycurl, json, sys, time


def null():
    pass


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


def publicar(access_token, carpeta, articulo, foto, tituloPrepend, desc, precio, unidades, categoria, altura, ancho, profundidad):
    nombre = tituloPrepend + ' ' + carpeta + ' ' + articulo
    
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
        "title" : nombre,
        "category_id" : categoria,
        "price" : precio,
        "currency_id" : "ARS",
        "available_quantity" : unidades,
        "buying_mode" : "buy_it_now",
        "condition" : "new",
        "listing_type_id" : "gold_special",
        "description" : {
            "plain_text" : desc
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
        "pictures" : [
            {
                "source" : foto
            }
        ],
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
                "value_name" :  carpeta,
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  null(),
                    "name" :  carpeta,
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
                "value_name" :  profundidad+" cm",
                "value_struct" :  {
                "number" :  float(profundidad),
                "unit" :  "cm"
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  profundidad+" cm",
                    "struct" :  {
                        "number" :  float(profundidad),
                        "unit" :  "cm"
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
                "value_name" :  altura+" cm",
                "value_struct" :  {
                "number" :  float(altura),
                "unit" :  "cm"
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  altura+" cm",
                    "struct" :  {
                        "number" :  float(altura),
                        "unit" :  "cm"
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
                "value_name" :  articulo,
                "value_struct" :  null(),
                "values": [
                    {
                    "id" :  null(),
                    "name" :  carpeta,
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
                "value_name" :  ancho+" cm",
                "value_struct" :  {
                "number" :  float(ancho),
                "unit" :  "cm"
                },
                "values": [
                    {
                    "id" :  null(),
                    "name" :  ancho+" cm",
                    "struct" :  {
                        "number" :  float(ancho),
                        "unit" :  "cm"
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