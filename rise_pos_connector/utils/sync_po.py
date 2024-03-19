# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today


#Invoice Fetch
@frappe.whitelist(allow_guest=True)
def sync_po_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
            if shop.sync_po:
                url = rps.url+"/erp/get_shop_purchase_orders"
                payload = {
                    "shop_code": shop.shop_code,
                    "only_special": 1,
                    "limit": 1
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
                    ord = response.json()
                    for get_po in ord['result']:
                        if get_po['is_special_order'] == True:
                            # Create Supplier
                            supplier_list = frappe.get_list('Supplier', fields=['supplier_name'])
                            check = {'supplier_name': get_po['supplier_information']['name']}
                            if check not in supplier_list:
                                supplier = frappe.get_doc({
                                    "doctype": "Supplier",
                                    "supplier_name": get_po['supplier_information']['name'],
                                    "supplier_group": 'All Supplier Groups',
                                    "country":'India'
                                })
                                supplier.insert()

                            # Create Address
                            address_list = frappe.get_list('Address', fields=['address_title'])
                            check = {'address_title': get_po['supplier_information']['name']}
                            if check not in address_list:
                                get_supp = frappe.get_doc({
                                    "doctype": "Address",
                                    "address_title": get_po['supplier_information']['name'],
                                    "address_line1": get_po['supplier_information']['address'],
                                    "state": get_po['supplier_information']['state'],
                                    "city": get_po['supplier_information']['city']
                                })
                                # Supplier Links
                                get_supp.append("links",{
                                    'link_doctype':'Supplier',
                                    'link_name':get_po['supplier_information']['name']
                                })
                                get_supp.insert()

                            # PO Number Check In Purchase Order
                            po_entry = frappe.get_list('Purchase Order', fields=['custom_po_number'])
                            check_po = {'custom_po_number': get_po['po_number']}

                            if check_po not in po_entry:
                                po_entry_insert = frappe.get_doc({
                                "doctype": "Purchase Order",
                                "supplier": get_po['supplier_information']['name'],
                                "custom_po_number": get_po['po_number'],
                                "schedule_date":today()
                                })
                                #Sp.Order Photo
                                po_entry_insert.append("custom_special_order_photo",{
                                'photo': rps.url+"/"+get_po['special_order_img_url']
                                })
                                
                                #Item
                                for itm in get_po['po_order_items']:
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

                                        po_entry_insert.append("items",{
                                        'item_code': itm['item_code'],
                                        'schedule_date': today(),
                                        'qty':itm['quantity'],
                                        'rate':itm['unit_cost'],
                                        'amount':itm['unit_cost'] * itm['quantity']
                                        })

                                        for tax in itm['tax_breakup']:
                                            tax_cat = int(tax['rate']) / 2
                                            tax_amount = float(itm['unit_cost']) * float(itm['quantity']) * tax_cat / 100.00

                                            po_entry_insert.append("taxes",{
                                                'charge_type': "Actual",
                                                'account_head': "SGST"+" - "+rps.abbr,
                                                'description':"SGST",
                                                'custom_tax_rate':int(tax['rate']) / 2,
                                                'tax_amount':float(tax_amount)
                                            })

                                            po_entry_insert.append("taxes",{
                                                'charge_type': "Actual",
                                                'account_head': "CGST"+" - "+rps.abbr,
                                                'description':"CGST",
                                                'custom_tax_rate':int(tax['rate']) / 2,
                                                'tax_amount':float(tax_amount)
                                            })

                                    else:
                                        
                                        po_entry_insert.append("items",{
                                        'item_code': itm['item_code'],
                                        'schedule_date': today(),
                                        'qty':itm['quantity'],
                                        'rate':itm['unit_cost'],
                                        'amount':itm['unit_cost'] * itm['quantity']
                                        })

                                        for tax in itm['tax_breakup']:
                                            tax_cat = int(tax['rate']) / 2
                                            tax_amount = float(itm['unit_cost']) * float(itm['quantity']) * tax_cat / 100.00

                                            po_entry_insert.append("taxes",{
                                                'charge_type': "Actual",
                                                'account_head': "SGST"+" - "+rps.abbr,
                                                'description':"SGST",
                                                # 'custom_tax_rate':float(tax_cat) / 2,
                                                'tax_amount':float(tax_amount)
                                            })

                                            po_entry_insert.append("taxes",{
                                                'charge_type': "Actual",
                                                'account_head': "CGST"+" - "+rps.abbr,
                                                'description':"CGST",
                                                # 'custom_tax_rate':float(tax_cat) / 2,
                                                'tax_amount':float(tax_amount)
                                            })
                                po_entry_insert.insert(ignore_permissions=True)
                                # po_entry_insert.submit()
            
    else:
        frappe.throw("Please Check Rise POS Setting")