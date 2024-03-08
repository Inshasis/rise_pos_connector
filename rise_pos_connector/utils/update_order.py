# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today


#Invoice Fetch
@frappe.whitelist(allow_guest=True)
def update_invoice_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
            if shop.sync_orders:
                url = rps.url+"/erp/get_shop_orders"
                payload = {
                    "shop_code": shop.shop_code,
                    "limit": 25
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
                    for ord_feach in ord['result']['orders']:
                        if ord_feach['order_id']:    
                            # Transaction Id Check In Sales Invoice
                            sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
                            check_inv = {'custom_order_id': ord_feach['order_id']}
                            if check_inv in sales_inv:
                                si = frappe.get_doc('Sales Invoice',ord_feach['order_id'])
                                si_name = str(si.name)
                                if si.docstatus == 1 and si_name and si.outstanding_amount != 0.00:
                                    #Payment Summary
                                    for pay in ord_feach['payment_type_summary']:
                                        for ps in si.custom_payment_summary:
                                            amt = 0.00
                                            for pay in ord_feach['payment_type_summary']:
                                                if pay['code'] != 'PAYT0001':
                                                    amt = amt + pay['amount']
                                            if pay['code'] != 'PAYT0001' and ps.payment_entry != 0 and si.outstanding_amount == amt:
                                                add_on_entry_child = si.append('custom_payment_summary',{})
                                                add_on_entry_child.code = pay['code']
                                                add_on_entry_child.payment_name = pay['name'].lower()
                                                add_on_entry_child.amount = si.outstanding_amount
                                                si.save()
                                                                                
                                            else:
                                                amount = 0.00
                                                for ps in si.custom_payment_summary:
                                                    if ps.code != 'PAYT0001':
                                                        amount = amount + ps.amount
                                                if ps.payment_entry != 0:
                                                    if pay['code'] != ps.code and amount != amt:
                                                        add_on_entry_child = si.append('custom_payment_summary',{})
                                                        add_on_entry_child.code = pay['code']
                                                        add_on_entry_child.payment_name = pay['name'].lower()
                                                        add_on_entry_child.amount = pay['amount']
                                                        si.save()                                                                                             
    else:
        frappe.msgprint("Please Check Rise POS Setting!")