# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import today


#Create Journal Entry - Expenses
@frappe.whitelist(allow_guest=True)
def sync_jv_rise_api():
    rps = frappe.get_doc('Rise POS Settings')
    if rps.enable and rps.url:
        for shop in rps.shop_code_details:
            if shop.sync_orders:
                url = rps.url+"/erp/get_cash_register_list"
                payload = {
                    "shop_code": shop.shop_code,
                    "start_date":"2024-03-20",
                    "end_date":"2024-03-21",
                    "terminal_ids":"null",
                    "is_til_detail_include":"true"
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
                    cash_reg = response.json()
                    for get_cash_reg in cash_reg['result']:
                        for cash_data in get_cash_reg['data']:
                            if cash_data['category'] != None and cash_data['is_paid_in'] == True:
                                # Create Account
                                account_list = frappe.get_list('Account', fields=['account_name'])
                                check = {'account_name': cash_data['category']}
                                if check not in account_list:
                                    acc_create = frappe.get_doc({
                                        "doctype": "Account",
                                        "account_name": cash_data['category'],
                                        "parent_account": "Expenses"+" - "+rps.abbr,
                                        "account_type":'Expense Account'
                                    })
                                    acc_create.insert()

                                # Transaction Id Check In Journal Entry
                                jv_name = frappe.db.get_value("Journal Entry",{'custom_cash_register_id':cash_data['id']}, ['name'])
                                if jv_name:
                                    pass
                                else:
                                    #Journal Entry
                                    jv_entry = frappe.get_doc({
                                        "doctype": "Journal Entry",
                                        "voucher_type":"Journal Entry",
                                        "custom_cash_register_id":cash_data['id'],
                                        "custom_shop_code":cash_data['shop_code'],
                                        "company": rps.company,
                                        "posting_date": today(),
                                        "user_remark": cash_data['remark']
                                    })
                                    # Account
                                    jv_entry.append("accounts", {
                                        "account": "Cash"+" - "+rps.abbr,
                                        "debit_in_account_currency": abs(cash_data['total_cash']),
                                        "debit": abs(cash_data['total_cash']),
                                        "credit_in_account_currency": 0.00,
                                        "credit": 0.00                                
                                    })
                                    jv_entry.append("accounts", {
                                    "account": cash_data['category']+" - "+rps.abbr,
                                        "debit_in_account_currency": 0.00,
                                        "debit": 0.00,
                                        "credit_in_account_currency": abs(cash_data['total_cash']),
                                        "credit": abs(cash_data['total_cash'])                                
                                    })
                                    jv_entry.insert()
                                    # jv_entry.submit()
            
    else:
        frappe.throw("Please Check Rise POS Setting")