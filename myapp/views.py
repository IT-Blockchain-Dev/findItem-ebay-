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
    token_list = ['AgAAAA**AQAAAA**aAAAAA**KlviYQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MHlYapDpOEqAydj6x9nY+seQ**d8oGAA**AAMAAA**zSMLmj+enSYAP9QMNZTqiPqso2+OtzbE7iPpz1p82DWfR0Og+7kXbyiEoGG6x0RkMYQcZ9ZXPkqfDHnRCVu4zKQry7gFq2ean5Kxu4g8B6Hj76Eu3Li6mTu/d1+jJwbGSl8IVjE2Ieo7MZRDUQwjnuYOSElFw5gTfLSY5Wa1ZdEGnaqltPY0yGtvtUYmkVvNCCy/5vdA/wqce0ixfiM4QnCj3vdWQzFasm33RhNiaisTxz9Cr6KkkD8IM2fR4JhUHhB/c2xS9hhxDMA6E4lnsxh82LMKh+O8xro3A+++j9iJUna6mCnc82DuhQGLM5sTCSaZeJlhr+RgjWKekbFz0pqXLq4Se/Y2GcR040ipKCbMy72vyfeQzMcfY0gsXGXOsBrHt9wHpAhWNU1wZnZjjyb8ycDn//ggxK5QkfmrOiJb3yHLXS/Fhrh1ZZ9bIrjR4i8s0h+DMegLFU7VOsXjVnkATJdb0R2qP7Uakm1Tg0Wb9Lk+pTLev5fgdyrIrkoFLVF35E+TfL8Ye1RQBArDYV9iDd3Ct4c35h97wqOYmGwG8Kv23NpGFwFSHiqmbY5uWnK9YI44ny6vECQPabrynYC5T5f4KyEb6GJHbKi0IC2uhTthSVmbGEnrbQ1lHGo2u65ZirBfZZJpc/88VD4EZ7vd/8ke8ypzwKGIwMpf4+NrjC8Pt1y4b/Gshkm+cE8TpDJnEP8jCLPWdvS2XHhGTS92ius3ebA/BfVyXAqIPveJeyWaV/7CZefs7cq/kZwX',
                  'AgAAAA**AQAAAA**aAAAAA**Tkw5YQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AAkouiDZmEpAudj6x9nY+seQ**ND0GAA**AAMAAA**HObrWfrPXHiWzSJ74ciTrkL0rv+huq2YUDwZIhhtAj3jsn/S01/tsg/FM4Z0nSM0UA5l5EQOLPIZrh4OxdWkLDKhCY6fsNfb78Mf7MqYWyOPm6EM3U+TgmoKtL3xigLkW0s8E+QojGUnFRWBZ1PRIz8d4cDd+1n7R/Q8UnRpZC0LPRAcW1uc1gUwyOpo08yChLIKhcsKoaCkb4gNxy4LSQLi7rLAjnPvcKHDwY34cAgTsZhSev2w5QY2RBw+5/zzpPb5NkJdw4jKfDuiGZCQ/IQyHMZMad+HeZ77hQGf3N/KRkob/ao4v7qCPNvfUTPnEcWwNorSaCuQ6oXn9VIGgDunisPACL5FsZ9BETPY3iwWkk7Ot++pDNkHsWh4zl+6VefejpuHuVJu5Qg/gJ0xAQsh5En6+JTrjYgIRgGYS5e9TRljLsBpUnlI+vYWpoht4f+C4v3jS1keYq2C4H26i59hJouO8GPVeKAM1z4jX5kKehBnXbbWejsPKo2FToInEl56qgHeiJX1K3WiPxzfDaoOHCLWHTPOh1Ec+DTbp7JzYX2NrDgLVtE9urdDQVc0dzxYW45I4GPAK3a1g6ok66JdMbOxHRZQvKbY4lnveAkLRknVr3IFuVA5o08ZraHYiZ08M8SHWTKGmcqVgooSiHxe5TknCV5wBlzUyy7UYwbOVg8r44E1Yp/P3AW5uKJZBOzxUa7O55LINA8GEQzuYuM8csGYHm+prI666Wsnv+C9wUrmF/vBatG6K7kuMSXP',
                  'AgAAAA**AQAAAA**aAAAAA**xg4CYg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MHlYqpCJeGow6dj6x9nY+seQ**SuUGAA**AAMAAA**hHyECWkjSlrs+4t72yg/SnqD9fjvEVjNWSwXQ7CW84qZTYpPc/B9WnzUURKUb4WXyg4qP4JpT59Zj6UFbFRghhYp/IgArcZ9DJlNiJ1kkA6NHpsEN3DazGQd6pUxAunW3Ft3RPdEtpsFdwhtrSdKuQ+ztyNKcCpUWsdyeRXPnd1o0MJwOh7XcddWCsaBWtfc5rpJWrtsPKO2xyHXjHpZJoNmR56a7lUDYw+Ji9gNtLWvW7n2TVubqpiUJtUZ0O21TD3TiTjCxj0KfJFS5Xxoeu84RFm+mqXLzozU6K5BQJWIbSoneMgl6qaXTIYMKIAFXgOfecBvijqP4WWsFlAqGfP+n7l/IVTisFK+DYQzxqFEQ1bZQl/BBW2w4TiMPSxzSsjTEM6rwFWl44M9Qtuqd7aGs9o4fYs/3iHwp7wFbcf1Aera9voIOY2841YrmBr0yjueTbJlyg0MuMSMZzzSdDn8Dz9+nfxv2WElSPHbQ38qy1zNnz9mHbycdzumeZCZ0Q80uBXihe8WdSkWnAT9DnmEJsYIab0wtrrkGxstnl/v/0hFAvLtwWqG9AmRGt4MtZTQcwyVxO7iPFY9aJSeGdjeE6uTvVIUAs2YMAYclSl/t6eHgFY6YGfL4Zr/IXjnIo4BQXPnjb233RgoTa0NAgxpwzwP46MQB5T3j3pqM6ebYLGwjYXJ4RIERuRCwA0ab5D0H57BYnr8A1WGK+JdmyB0St4BbLVARcytACxx1FcsPE1BFSG5iu45obzHMTE0',
                  'v^1.1#i^1#f^0#I^3#r^1#p^3#t^Ul4xMF84OjBERDA5NjAwRTEwRDVBNDA5NTVDNzE5QUEwRDA3MjA3XzJfMSNFXjI2MA==']
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
    index = 0
    for keyword in keyword_list:
        # keyword = keyword.replace(" ",",")
        token_id = index % 4
        token = token_list[token_id]
        print("token=>", token)
        item_info = findItemsAdvanced(
            token, keyword, min_price, max_price, zip_code, review, ranking, condition, category_id, buy_format)
        # print("item_info=>", item_info)
        if item_info != None:
            item_info['id'] = index
            item_list.append(item_info)
            index = index + 1

    return Response(item_list)


def findItemsAdvanced(token, keyword, min_price, max_price, zip_code, review, ranking, condition, category_id, buy_format):

    try:

        token1 = token
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
            # 'categoryId': category_id,
            # 'buyerPostalCode': zip_code,
            'affiliate': {'trackingId': 1},
            'sortOrder': 'PricePlusShippingLowest',
        }

        response = api.execute('findItemsAdvanced', api_request)
        res = response.dict()
        # print("res1=>", res)

        try:
            item_array = res['searchResult']['item']
            ranking_int = int(ranking) - 1
            item = item_array[ranking_int]
            item_id = item['itemId']
            print("item_id=>", item_id)
            condition = item['condition']['conditionDisplayName']
            price = item['sellingStatus']['currentPrice']['value']
            title = item['title']
            url = item['viewItemURL']
            shipping_cost = item['shippingInfo']['shippingServiceCost']['value']
            shipping_handlingtime = item['shippingInfo']['handlingTime']
            # print(price, title, url, shipping_cost, shipping_handlingtime)
            try:
                token1 = token
                api = Trading(domain='api.ebay.com', appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
                              certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f', devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
                              token=token1, config_file=None, siteid=0)
                api_request = {
                    'IncludeItemSpecifics': 'true',
                    'ItemID': item_id,
                    'DetailLevel': 'ReturnAll'
                }
                response = api.execute('GetItem', api_request)
                res = response.dict()
                ItemSpecifics = res['Item']['ItemSpecifics']['NameValueList']
                specifics = ''
                for item_specific in ItemSpecifics:
                    name = item_specific['Name']
                    value = item_specific['Value']

                    if isinstance(value, list) == False:
                        if value != 'NA':
                            specifics = specifics + name + ':' + value + ','
                print('hi', specifics)
                picture_urls = res['Item']['PictureDetails']['PictureURL']
                description = specifics
                item_info = {"keyword": keyword, "title": title, "item_id": item_id,  "price": price, "condition": condition, "time": shipping_handlingtime, "cost": shipping_cost, "condition": condition, "url": url,
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
