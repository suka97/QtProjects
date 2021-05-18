from array import array
from io import BytesIO
import pycurl, json


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


def ml_itemsScroll(access_token, scroll_id):
    header = BytesIO()
    response = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.WRITEFUNCTION, response.write)
    crl.setopt(crl.HEADERFUNCTION, header.write)

    url = 'https://api.mercadolibre.com/users/518143830/items/search?search_type=scan'
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