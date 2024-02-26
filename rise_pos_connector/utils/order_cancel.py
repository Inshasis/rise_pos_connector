# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today

#Invoice Cancelled
@frappe.whitelist(allow_guest=True)
def cancel_invoice_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
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