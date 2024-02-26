# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
import re

@frappe.whitelist(allow_guest=True)
def sync_items_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        for shop in rps.shop_code_details:
            if shop.sync_orders:
                url = rps.url+"/erp/get_all_items"
                payload = {
                    "shop_code": shop.shop_code,
                    "limit": 50
                }
                headers = {
                    'api_key': rps.api_key,
                    'Auth_token': shop.erp_token
                }
                # Make the API request
                response = requests.post(url, headers=headers, data=json.dumps(payload))
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
                            for tax in item['tax_settings']:
                                if str(tax['rate']) == '18':
                                    itm_crt.append("taxes",{
                                        'item_tax_template':"18 - RP"
                                    }) 
                                elif str(tax['rate']) == '5':
                                    itm_crt.append("taxes",{
                                        'item_tax_template':"5 - RP"
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

            
