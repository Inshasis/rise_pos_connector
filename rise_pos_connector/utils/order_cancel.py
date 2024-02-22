# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today

#Invoice Cancelled
@frappe.whitelist(allow_guest=True)
def cancel_invoice_rise_api():
    shop_263()
    shop_265()

def shop_263():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        for item in rps.shop_code_details:
            url = "http://dev.onegreendiary.com/erp/get_shop_orders"
            payload = {
                "shop_code": "SH0263",
                "limit": 50
                
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
                    if ord_feach['prev_order_id']:
                        # Transaction Id Check In Sales Invoice
                        sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
                        check_inv = {'custom_order_id': ord_feach['prev_order_id']}
                        
                        if check_inv in sales_inv:
                            pay_reff = frappe.db.sql("select parent from `tabPayment Entry Reference` where reference_doctype = 'Sales Invoice' AND reference_name = %s", ord_feach['prev_order_id'])
                            for pay_entry in pay_reff:
                                # Payment Entry Cancel
                                pe = frappe.get_doc("Payment Entry", pay_entry[0])
                                pe.cancel()
                                frappe.db.commit()
                                
                                # Sales Invoice Cancel
                                si = frappe.db.get_value("Sales Invoice", {'custom_order_id': ord_feach['prev_order_id']}, "name")
                                si_doc = frappe.get_doc("Sales Invoice", si)
                                si_doc.cancel()
                                frappe.db.commit()

def shop_265():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable:
        for item in rps.shop_code_details:
            url = "http://dev.onegreendiary.com/erp/get_shop_orders"
            payload = {
                "shop_code": "SH0265",
                "limit": 50
                
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
                    if ord_feach['prev_order_id']:
                        # Transaction Id Check In Sales Invoice
                        sales_inv = frappe.get_list('Sales Invoice', fields=['custom_order_id'])
                        check_inv = {'custom_order_id': ord_feach['prev_order_id']}
                        
                        if check_inv in sales_inv:
                            pay_reff = frappe.db.sql("select parent from `tabPayment Entry Reference` where reference_doctype = 'Sales Invoice' AND reference_name = %s", ord_feach['prev_order_id'])
                            for pay_entry in pay_reff:
                                # Payment Entry Cancel
                                pe = frappe.get_doc("Payment Entry", pay_entry[0])
                                pe.cancel()
                                frappe.db.commit()
                                
                                # Sales Invoice Cancel
                                si = frappe.db.get_value("Sales Invoice", {'custom_order_id': ord_feach['prev_order_id']}, "name")
                                si_doc = frappe.get_doc("Sales Invoice", si)
                                si_doc.cancel()
                                frappe.db.commit()
                           