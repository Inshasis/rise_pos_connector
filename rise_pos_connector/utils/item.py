# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from requests.structures import CaseInsensitiveDict
import re

@frappe.whitelist(allow_guest=True)
def sync_items_rise_api():
    url = "https://dev.onegreendiary.com/erp/get_all_items"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["api_key"] = "12345"
    headers["Auth_token"] = "6ceea044fa6fdc82d76bd7c567bbd2dd"

    data = {
        "limit":100,
        "page": 1,
        "shop_code": "SH0226"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    # print(response)
    if (response.status_code == 200):
        itm = response.json()
        for item in itm['result']['items']:
            #Create Item
            item_check = frappe.get_list('Item', fields=['item_code'])
            check = {'item_code': item['item_code']}
            if check not in item_check:
                itm_crt = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item['item_code'],
                    "item_name": item['name'],
                    "item_group":'Products',
                    "stock_uom":'Nos',
                    "is_stock_item":'1',
                    "include_item_in_manufacturing":'1'
                })
                itm_crt.insert()
        
