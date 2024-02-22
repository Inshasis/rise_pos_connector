# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today

#Invoice Fetch
@frappe.whitelist(allow_guest=True)
def sync_invoice_rise_api():
    shop_263()
    shop_265()

def shop_263():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        url = "http://dev.onegreendiary.com/erp/get_shop_orders"
        payload = {
            "shop_code": "SH0263",
            "limit": 10
            
        }
        headers = {
            'api_key': "12345",
            'Auth_token': "cc85cdca166aef1c3ee1e1869f39cc55"
        }
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # Process the response
        if response.status_code == 200:
            # Handle the API response as needed
            ord = response.json()
            for ord_feach in ord['result']['orders']:
                if ord_feach['shipping_type'] == "ST0003" and ord_feach['order_status'] == "ORDS0008" and ord_feach['prev_order_id'] == None:    
                    # Create customer
                    customer_list = frappe.get_list('Customer', fields=['customer_name'])
                    check = {'customer_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
                    if check not in customer_list:
                        customer = frappe.get_doc({
                            "doctype": "Customer",
                            "customer_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "customer_group": 'Individual',
                            "territory":'India'
                        })
                        customer.insert()

                    # Create contact
                    contact_list = frappe.get_list('Contact', fields=['first_name'])
                    check = {'first_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
                    if check not in contact_list:
                        guest = frappe.get_doc({
                            "doctype": "Contact",
                            "first_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
                        })
                        # Mobile Number
                        guest.append("phone_nos",{
                            'phone':ord_feach['customer_phone'],
                            'is_primary_mobile_no':1
                        })
                        # Customer Links
                        guest.append("links",{
                            'link_doctype':'Customer',
                            'link_name':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            'link_title':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
                        })
                        guest.insert()
                    

                    # Transaction Id Check In Sales Invoice
                    sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
                    check_inv = {'custom_order_id': ord_feach['order_id']}
                    
                    if check_inv not in sales_inv:
                        if ord_feach['discount']:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name'],
                            
                            #Discount
                            "apply_discount_on":"Net Total",
                            "discount_amount":ord_feach['discount']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()
                        
                        elif ord_feach['cash_discount']:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name'],
                            
                            #Discount
                            "apply_discount_on":"Grand Total",
                            "discount_amount":ord_feach['cash_discount']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()

                        else:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()


def shop_265():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        url = "http://dev.onegreendiary.com/erp/get_shop_orders"
        payload = {
            "shop_code": "SH0265",
            "limit": 10
            
        }
        headers = {
            'api_key': "12345",
            'Auth_token': "cc85cdca166aef1c3ee1e1869f39cc55"
        }
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # Process the response
        if response.status_code == 200:
            # Handle the API response as needed
            ord = response.json()
            for ord_feach in ord['result']['orders']:
                if ord_feach['shipping_type'] == "ST0003" and ord_feach['order_status'] == "ORDS0008" and ord_feach['prev_order_id'] == None:    
                    # Create customer
                    customer_list = frappe.get_list('Customer', fields=['customer_name'])
                    check = {'customer_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
                    if check not in customer_list:
                        customer = frappe.get_doc({
                            "doctype": "Customer",
                            "customer_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "customer_group": 'Individual',
                            "territory":'India'
                        })
                        customer.insert()

                    # Create contact
                    contact_list = frappe.get_list('Contact', fields=['first_name'])
                    check = {'first_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
                    if check not in contact_list:
                        guest = frappe.get_doc({
                            "doctype": "Contact",
                            "first_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
                        })
                        # Mobile Number
                        guest.append("phone_nos",{
                            'phone':ord_feach['customer_phone'],
                            'is_primary_mobile_no':1
                        })
                        # Customer Links
                        guest.append("links",{
                            'link_doctype':'Customer',
                            'link_name':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            'link_title':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
                        })
                        guest.insert()
                    

                    # Transaction Id Check In Sales Invoice
                    sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
                    check_inv = {'custom_order_id': ord_feach['order_id']}
                    
                    if check_inv not in sales_inv:
                        if ord_feach['discount']:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name'],
                            
                            #Discount
                            "apply_discount_on":"Net Total",
                            "discount_amount":ord_feach['discount']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()
                        
                        elif ord_feach['cash_discount']:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name'],
                            
                            #Discount
                            "apply_discount_on":"Grand Total",
                            "discount_amount":ord_feach['cash_discount']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()

                        else:
                            sales_inv_insert = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                            "custom_order_id": ord_feach['order_id'],
                            "custom_shop_code": ord_feach['shop_code'],
                            "custom_shop_user_name": ord_feach['shop_user_name']
                            })

                            #Payment Summary
                            for pay in ord_feach['payment_type_summary']:
                                sales_inv_insert.append("custom_payment_summary",{
                                    'code':pay['code'],
                                    'payment_name':pay['name'],
                                    'amount':pay['amount']                                     
                                })

                            #Items
                            for i in ord_feach['items']:
                                #Create Item
                                item_check = frappe.get_list('Item', fields=['item_code'])
                                check = {'item_code': i['item_code']}
                                if check not in item_check:
                                    itm_crt = frappe.get_doc({
                                        "doctype": "Item",
                                        "item_code": i['item_code'],
                                        "item_name": i['item_name'],
                                        "item_group":'Products',
                                        "stock_uom":'Nos',
                                        "is_stock_item":'1',
                                        "include_item_in_manufacturing":'1'
                                    })
                                    itm_crt.insert()

                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })

                                else:
                                    sales_inv_insert.append("items",{
                                    'item_code': i['item_code'],
                                    'qty':i['item_count'],
                                    'rate':i['item_price'],
                                    'amount':i['item_price'] * i['item_count']
                                    })
                                    #Tax
                                    for tax in i['tax_breakup']:
                                        sales_inv_insert.append("taxes",{
                                            'charge_type': "Actual",
                                            'account_head': tax['breakup_name']+" - RPO",
                                            'description':tax['breakup_name'],
                                            'custom_tax_rate':tax['rate'],
                                            'tax_amount':tax['value']
                                        })
                            sales_inv_insert.insert(ignore_permissions=True)
                            sales_inv_insert.submit()

#OLD CODE
# def shop_265():
#     rps = frappe.get_doc('Rise POS Settings')
#     if rps.enable:
#         url = "http://dev.onegreendiary.com/erp/get_shop_orders"
#         payload = {
#             "shop_code": "SH0265",
#             "limit": 1
            
#         }
#         headers = {
#             'api_key': "12345",
#             'Auth_token': "cc85cdca166aef1c3ee1e1869f39cc55"
#         }
#         # Make the API request
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         # Process the response
#         if response.status_code == 200:
#             # Handle the API response as needed
#             ord = response.json()
#             for ord_feach in ord['result']['orders']:
#                 if ord_feach['shipping_type'] == "ST0003" and ord_feach['order_status'] == "ORDS0008" and ord_feach['prev_order_id'] == None:
#                     # Create customer
#                     customer_list = frappe.get_list('Customer', fields=['customer_name'])
#                     check = {'customer_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
#                     if check not in customer_list:
#                         customer = frappe.get_doc({
#                             "doctype": "Customer",
#                             "customer_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
#                             "customer_group": 'Individual',
#                             "territory":'India'
#                         })
#                         customer.insert()

#                     # Create contact
#                     contact_list = frappe.get_list('Contact', fields=['first_name'])
#                     check = {'first_name': ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']}
#                     if check not in contact_list:
#                         guest = frappe.get_doc({
#                             "doctype": "Contact",
#                             "first_name": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
#                         })
#                         # Mobile Number
#                         guest.append("phone_nos",{
#                             'phone':ord_feach['customer_phone'],
#                             'is_primary_mobile_no':1
#                         })
#                         # Customer Links
#                         guest.append("links",{
#                             'link_doctype':'Customer',
#                             'link_name':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
#                             'link_title':ord_feach['customer_phone'] +"-"+ ord_feach['customer_name']
#                         })
#                         guest.insert()
                    

#                     # Transaction Id Check In Sales Invoice
#                     sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
#                     check_inv = {'custom_order_id': ord_feach['order_id']}
                    
#                     if check_inv not in sales_inv:
#                         if ord_feach['discount']:
#                             sales_inv_insert = frappe.get_doc({
#                             "doctype": "Sales Invoice",
#                             "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
#                             "custom_order_id": ord_feach['order_id'],
#                             "custom_shop_code": ord_feach['shop_code'],
#                             "custom_shop_user_name": ord_feach['shop_user_name'],
                            
#                             #Discount
#                             "apply_discount_on":"Net Total",
#                             "discount_amount":ord_feach['discount']
#                             })
                        
#                         elif ord_feach['cash_discount']:
#                             sales_inv_insert = frappe.get_doc({
#                             "doctype": "Sales Invoice",
#                             "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
#                             "custom_order_id": ord_feach['order_id'],
#                             "custom_shop_code": ord_feach['shop_code'],
#                             "custom_shop_user_name": ord_feach['shop_user_name'],
                            
#                             #Discount
#                             "apply_discount_on":"Grand Total",
#                             "is_cash_or_non_trade_discount":1,
#                             "additional_discount_account":"Cash Discount - RPO",
#                             "discount_amount":ord_feach['cash_discount']
#                             })
                        
#                         else:
#                             sales_inv_insert = frappe.get_doc({
#                             "doctype": "Sales Invoice",
#                             "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
#                             "custom_order_id": ord_feach['order_id'],
#                             "custom_shop_code": ord_feach['shop_code'],
#                             "custom_shop_user_name": ord_feach['shop_user_name']
#                             })

#                             #Payment Summary
#                             for pay in ord_feach['payment_type_summary']:
#                                 sales_inv_insert.append("custom_payment_summary",{
#                                     'code':pay['code'],
#                                     'payment_name':pay['name'],
#                                     'amount':pay['amount']                                     
#                                 })

#                             #Items
#                             for i in ord_feach['items']:
#                                 #Create Item
#                                 item_check = frappe.get_list('Item', fields=['item_code'])
#                                 check = {'item_code': i['item_code']}
#                                 if check not in item_check:
#                                     itm_crt = frappe.get_doc({
#                                         "doctype": "Item",
#                                         "item_code": i['item_code'],
#                                         "item_name": i['item_name'],
#                                         "item_group":'Products',
#                                         "stock_uom":'Nos',
#                                         "is_stock_item":'1',
#                                         "include_item_in_manufacturing":'1'
#                                     })
#                                     itm_crt.insert()

#                                     sales_inv_insert.append("items",{
#                                     'item_code': i['item_code'],
#                                     'qty':i['item_count'],
#                                     'rate':i['item_price'],
#                                     'amount':i['item_price'] * i['item_count']
#                                     })
#                                     #Tax
#                                     for tax in i['tax_breakup']:
#                                         sales_inv_insert.append("taxes",{
#                                             'charge_type': "Actual",
#                                             'account_head': tax['breakup_name']+" - RPO",
#                                             'description':tax['breakup_name'],
#                                             'custom_tax_rate':tax['rate'],
#                                             'tax_amount':tax['value']
#                                         })

#                                 else:
#                                     sales_inv_insert.append("items",{
#                                     'item_code': i['item_code'],
#                                     'qty':i['item_count'],
#                                     'rate':i['item_price'],
#                                     'amount':i['item_price'] * i['item_count']
#                                     })
#                                     #Tax
#                                     for tax in i['tax_breakup']:
#                                         sales_inv_insert.append("taxes",{
#                                             'charge_type': "Actual",
#                                             'account_head': tax['breakup_name']+" - RPO",
#                                             'description':tax['breakup_name'],
#                                             'custom_tax_rate':tax['rate'],
#                                             'tax_amount':tax['value']
#                                         })
#                             sales_inv_insert.insert(ignore_permissions=True)
#                             sales_inv_insert.submit()