# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today

@frappe.whitelist(allow_guest=True)
def sync_orders_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    for item in rps.shop_code_details:
        url = "http://dev.onegreendiary.com/erp/get_shop_orders"
        payload = {
            "limit": 5,
            "page": 1,
            "shop_code": "SH0226"
        }
        headers = {
            'api_key': "12345",
            'Auth_token': "6ceea044fa6fdc82d76bd7c567bbd2dd",
        }
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # Process the response
        if response.status_code == 200:
            # Handle the API response as needed
            ord = response.json()
            for ord_feach in ord['result']['orders']:
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

                # Transaction Id Check
                sales_order = frappe.get_list('Sales Order', fields=['custom_order_id'])
                check = {'custom_order_id': ord_feach['order_id']}

                if check not in sales_order:
                    sales_order_insert = frappe.get_doc({
                    "doctype": "Sales Order",
                    "customer": ord_feach['customer_phone'] +"-"+ ord_feach['customer_name'],
                    "custom_order_id": ord_feach['order_id'],
                    "delivery_date":today()

                    })
                    sales_order_insert.append("items",{
                        'item_code':"ITABD7FOGV-198158",
                        'item_name':"ITABD7FOGV-198158",
                        'description':"ITABD7FOGV-198158",
                        'delivery_date':today(),
                        'qty':1,
                        'rate':"100",
                        'amount':"100"
                    })
                    sales_order_insert.insert(ignore_permissions=True)
                
                
