# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from requests.structures import CaseInsensitiveDict
import re

@frappe.whitelist(allow_guest=True)
def sync_items_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        for item in rps.shop_code_details:
            url = "https://dev.onegreendiary.com/erp/get_all_items"
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            headers["api_key"] = "12345"
            headers["Auth_token"] =  "cc85cdca166aef1c3ee1e1869f39cc55"

            data = {
                "shop_code": "SH0263"
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

                        #Create Item Selling Price
                        it_pr_check = frappe.get_list('Item Price', fields=['item_code'])
                        check_ip = {'item_code': item['item_code'],'price_list': 'Standard Selling'}
                        if check_ip not in it_pr_check:
                            itm_pr = frappe.get_doc({
                                "doctype": "Item Price",
                                "item_code": item['item_code'],
                                "price_list":'Standard Selling',
                                "price_list_rate":item['per_unit_price']
                            })
                            itm_pr.insert()

                        #Create Item Selling Price
                        it_pr_check = frappe.get_list('Item Price', fields=['item_code'])
                        check_ip = {'item_code': item['item_code'],'price_list': 'Standard Buying'}
                        if check_ip not in it_pr_check:
                            itm_pr = frappe.get_doc({
                                "doctype": "Item Price",
                                "item_code": item['item_code'],
                                "price_list":'Standard Buying',
                                "price_list_rate":item['unit_cost']
                            })
                            itm_pr.insert() 

    else:
        frappe.throw("Please Check Rise POS Setting.")
            
