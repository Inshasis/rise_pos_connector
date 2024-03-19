# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today

# Invoice Fetch
@frappe.whitelist(allow_guest=True)
def update_invoice_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
            if shop.sync_orders:
                url = rps.url+"/erp/get_shop_orders"
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
                    ord = response.json()
                    for ord_feach in ord['result']['orders']:
                        if ord_feach['order_id']:    
                            # Transaction Id Check In Sales Invoice
                            sales_invoices = frappe.get_list('Sales Invoice', fields=['name'], filters={'custom_order_id': ord_feach['order_id']})
                            if sales_invoices:
                                sales_invoice = frappe.get_doc('Sales Invoice', sales_invoices[0]['name'])
                                if sales_invoice.outstanding_amount != 0.00:
                                    # Get existing payment codes and names
                                    existing_codes = [ps.code for ps in sales_invoice.custom_payment_summary if ps.payment_entry != 0]
                                    existing_name = [pyn.payment_name for pyn in sales_invoice.custom_payment_summary if pyn.code != 'PAYT0001']

                                    # Iterate through payment summaries
                                    for payment_summary in ord_feach['payment_type_summary']:
                                        if payment_summary['code'] != 'PAYT0001' and payment_summary['amount'] > 0:
                                            payment_code = payment_summary['code']
                                            payment_amount = payment_summary['amount']
                                            payment_name = payment_summary['name'].lower()

                                            # Add payment entry if not already present
                                            if payment_code not in existing_codes or payment_name not in existing_name:
                                                add_on_entry_child = sales_invoice.append('custom_payment_summary', {})
                                                add_on_entry_child.code = payment_code
                                                add_on_entry_child.payment_name = payment_name
                                                add_on_entry_child.amount = payment_amount
                                                sales_invoice.save()
                                            
                                                existing_codes.append(payment_code)
                                                existing_name.append(payment_name)
                                            elif sales_invoice.outstanding_amount != 0.00:
                                                # Adjust existing payment entry
                                                existing_amount = sum([ps.amount for ps in sales_invoice.custom_payment_summary if ps.payment_name == payment_name])
                                                payment_amount_diff = payment_amount - existing_amount
                                                if payment_amount_diff != 0:
                                                    add_on_entry_child = sales_invoice.append('custom_payment_summary', {})
                                                    add_on_entry_child.code = payment_code
                                                    add_on_entry_child.payment_name = payment_name
                                                    add_on_entry_child.amount = payment_amount_diff
                                                    sales_invoice.save()
                                            else:    
                                                # Check for missing payment entries
                                                for ps in sales_invoice.custom_payment_summary:
                                                    if ps.code not in existing_codes:
                                                        add_on_entry_child = sales_invoice.append('custom_payment_summary', {})
                                                        add_on_entry_child.code = ps.code
                                                        add_on_entry_child.payment_name = ps.payment_name
                                                        add_on_entry_child.amount = ps.amount
                                                        sales_invoice.save()

    else:
        frappe.msgprint("Please Check Rise POS Setting!")
