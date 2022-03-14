from locale import currency
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as finding
from django.db import connection
from datetime import datetime
from datetime import date
from datetime import timedelta
import json
import csv
import io


@api_view(['GET', 'POST'])
def getCategory(request):
    category_id = request.data['category_id']
    print("dfd", category_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from ebaycategory where level=%s", [category_id])
        row = cursor.fetchall()
        # this will extract row headers
        row_headers = [x[0] for x in cursor.description]

        categorylist = []
        for result in row:
            categorylist.append(dict(zip(row_headers, result)))

    return Response(categorylist)


@api_view(['GET', 'POST'])
def getSubCategory(request):
    category_id = request.data['category_id']
    print(category_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from ebaycategory where cat_parent_id=%s", [category_id])
        row = cursor.fetchall()
        # this will extract row headers
        row_headers = [x[0] for x in cursor.description]
        categorylist = []
        for result in row:
            categorylist.append(dict(zip(row_headers, result)))

    return Response(categorylist)


@api_view(['GET', 'POST'])
def uploadData(request):
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        print("type error")
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    keyword_list = []
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        keyword = column[0]
        keyword_list.append(keyword)

    min_price = request.data['minPrice']
    max_price = request.data['maxPrice']
    zip_code = request.data['zipCode']
    review = request.data['review']
    ranking = request.data['ranking']
    condition = request.data['condition']
    buy_format = request.data['format']
    category_id = request.data['category']
    item_list = []
    print(min_price, max_price, zip_code, review,
          ranking, condition, buy_format, category_id)
    index = 1
    for keyword in keyword_list:
        item_info = findItemsAdvanced(
            keyword, min_price, max_price, zip_code, review, ranking, condition, category_id, buy_format)
        item_info['id'] = index
        item_list.append(item_info)
        index = index + 1

    return Response(item_list)


def findItemsAdvanced(keyword, min_price, max_price, zip_code, review, ranking, condition, category_id, buy_format):

    try:

        token1 = 'AgAAAA**AQAAAA**aAAAAA**KlviYQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MHlYapDpOEqAydj6x9nY+seQ**d8oGAA**AAMAAA**zSMLmj+enSYAP9QMNZTqiPqso2+OtzbE7iPpz1p82DWfR0Og+7kXbyiEoGG6x0RkMYQcZ9ZXPkqfDHnRCVu4zKQry7gFq2ean5Kxu4g8B6Hj76Eu3Li6mTu/d1+jJwbGSl8IVjE2Ieo7MZRDUQwjnuYOSElFw5gTfLSY5Wa1ZdEGnaqltPY0yGtvtUYmkVvNCCy/5vdA/wqce0ixfiM4QnCj3vdWQzFasm33RhNiaisTxz9Cr6KkkD8IM2fR4JhUHhB/c2xS9hhxDMA6E4lnsxh82LMKh+O8xro3A+++j9iJUna6mCnc82DuhQGLM5sTCSaZeJlhr+RgjWKekbFz0pqXLq4Se/Y2GcR040ipKCbMy72vyfeQzMcfY0gsXGXOsBrHt9wHpAhWNU1wZnZjjyb8ycDn//ggxK5QkfmrOiJb3yHLXS/Fhrh1ZZ9bIrjR4i8s0h+DMegLFU7VOsXjVnkATJdb0R2qP7Uakm1Tg0Wb9Lk+pTLev5fgdyrIrkoFLVF35E+TfL8Ye1RQBArDYV9iDd3Ct4c35h97wqOYmGwG8Kv23NpGFwFSHiqmbY5uWnK9YI44ny6vECQPabrynYC5T5f4KyEb6GJHbKi0IC2uhTthSVmbGEnrbQ1lHGo2u65ZirBfZZJpc/88VD4EZ7vd/8ke8ypzwKGIwMpf4+NrjC8Pt1y4b/Gshkm+cE8TpDJnEP8jCLPWdvS2XHhGTS92ius3ebA/BfVyXAqIPveJeyWaV/7CZefs7cq/kZwX'
        api = finding(domain='svcs.ebay.com', appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
                      certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f', devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
                      token=token1, config_file=None)

        api_request = {
            'keywords': keyword,
            'itemFilter': [

                {'name': 'Condition',
                 'value': condition},
                {'name': 'MinPrice',
                 'value': min_price},
                {'name': 'MaxPrice',
                 'value': max_price},
                {'name': 'ListingType',
                 'value': buy_format},
                {'name': 'FeedbackScoreMin',
                 'value': review}
            ],
            'categoryId': category_id,
            'buyPorstalCode': zip_code,
            'affiliate': {'trackingId': 1},
            'sortOrder': 'PricePlusShippingLowest',
        }

        response = api.execute('findItemsAdvanced', api_request)
        res = response.dict()

        try:
            item_array = res['searchResult']['item']
            item = item_array[int(ranking)]
            item_id = item['itemId']
            condition = item['condition']['conditionDisplayName']
            price = item['sellingStatus']['currentPrice']['value']
            title = item['title']
            url = item['viewItemURL']
            shipping_cost = item['shippingInfo']['shippingServiceCost']['value']
            shipping_handlingtime = item['shippingInfo']['handlingTime']
            print(price, title, url, shipping_cost, shipping_handlingtime)
            try:
                token1 = 'AgAAAA**AQAAAA**aAAAAA**KlviYQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MHlYapDpOEqAydj6x9nY+seQ**d8oGAA**AAMAAA**zSMLmj+enSYAP9QMNZTqiPqso2+OtzbE7iPpz1p82DWfR0Og+7kXbyiEoGG6x0RkMYQcZ9ZXPkqfDHnRCVu4zKQry7gFq2ean5Kxu4g8B6Hj76Eu3Li6mTu/d1+jJwbGSl8IVjE2Ieo7MZRDUQwjnuYOSElFw5gTfLSY5Wa1ZdEGnaqltPY0yGtvtUYmkVvNCCy/5vdA/wqce0ixfiM4QnCj3vdWQzFasm33RhNiaisTxz9Cr6KkkD8IM2fR4JhUHhB/c2xS9hhxDMA6E4lnsxh82LMKh+O8xro3A+++j9iJUna6mCnc82DuhQGLM5sTCSaZeJlhr+RgjWKekbFz0pqXLq4Se/Y2GcR040ipKCbMy72vyfeQzMcfY0gsXGXOsBrHt9wHpAhWNU1wZnZjjyb8ycDn//ggxK5QkfmrOiJb3yHLXS/Fhrh1ZZ9bIrjR4i8s0h+DMegLFU7VOsXjVnkATJdb0R2qP7Uakm1Tg0Wb9Lk+pTLev5fgdyrIrkoFLVF35E+TfL8Ye1RQBArDYV9iDd3Ct4c35h97wqOYmGwG8Kv23NpGFwFSHiqmbY5uWnK9YI44ny6vECQPabrynYC5T5f4KyEb6GJHbKi0IC2uhTthSVmbGEnrbQ1lHGo2u65ZirBfZZJpc/88VD4EZ7vd/8ke8ypzwKGIwMpf4+NrjC8Pt1y4b/Gshkm+cE8TpDJnEP8jCLPWdvS2XHhGTS92ius3ebA/BfVyXAqIPveJeyWaV/7CZefs7cq/kZwX'
                api = Trading(domain='api.ebay.com', appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
                              certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f', devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
                              token=token1, config_file=None, siteid=0)
                api_request = {
                    'ItemID': item_id,
                    'DetailLevel': 'ReturnAll'
                }
                response = api.execute('GetItem', api_request)
                res = response.dict()
                picture_urls = res['Item']['PictureDetails']['PictureURL']
                description = res['Item']['Description']
                print(picture_urls, description)
                item_info = {"title": title, "item_id": item_id, "price": price, "time": shipping_handlingtime, "cost": shipping_cost, "condition": condition, "url": url,
                             "description": description, "picture_urls": picture_urls}
                return item_info
            except ConnectionError as e:
                print(e)
                print(e.response.dict())
        except:
            print("error")

    except ConnectionError as e:
        print(e)
        print(e.response.dict())