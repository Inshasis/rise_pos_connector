# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today


#Invoice Fetch
@frappe.whitelist(allow_guest=True)
def sync_material_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
            if shop.sync_material:
                url = rps.url+"/erp/get_shop_purchase_orders"
                payload = {
                    "shop_code": shop.shop_code,
                    "limit": 5
                }
                headers = {
                    'api_key': rps.api_key,
                    'Auth_token': shop.erp_token
                }
                # Make the API request
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                # Process the response
                if response.status_code == 200:
                    # Handle the API response as needed
                    mr = response.json()
                    for get_mr in mr['result']:
                        mr_list = frappe.get_list('Material Request', fields=['custom_id'])
                        mr_check = {'custom_id': get_mr['po_number']}
                        if mr_check not in mr_list:
                            mr_entry_insert = frappe.get_doc({
                            "doctype": "Material Request",
                            "schedule_date":today(),
                            "material_request_type":"Purchase",
                            "custom_id":get_mr['po_number'],
                            "custom_shop_code":get_mr['shop_code'],
                            "set_warehouse":get_mr['supplier_name']+" - "+rps.abbr
                            })
                                                            
                            #Item
                            for itm in get_mr['po_order_items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': itm['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": itm['item_code'],
                                        "item_name": itm['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    mr_entry_insert.append("items",{
                                    'item_code': itm['item_code'],
                                    'schedule_date': today(),
                                    'qty':itm['quantity'],
                                    'uom':"Nos",
                                    'conversion_factor':"1",
                                    'rate':itm['unit_cost']
                                    })
                                
                                else:
                                    mr_entry_insert.append("items",{
                                    'item_code': itm['item_code'],
                                    'schedule_date': today(),
                                    'qty':itm['quantity'],
                                    'uom':"Nos",
                                    'conversion_factor':"1",
                                    'rate':itm['unit_cost']
                                    })
                            mr_entry_insert.insert(ignore_permissions=True)
    else:
        frappe.throw("Please Check Rise POS Setting")