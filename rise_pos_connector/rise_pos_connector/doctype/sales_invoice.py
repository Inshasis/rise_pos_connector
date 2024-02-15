# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe


def on_submit(doc,methods):
    if doc.grand_total != 0.00:
        for pay_type in doc.custom_payment_summary:
            #Create Mode of Payment
            mop_check = frappe.get_list('Mode of Payment', fields=['mode_of_payment'])
            check = {'mode_of_payment': pay_type.payment_name}
            if check not in mop_check:
                mop = frappe.get_doc({
                    "doctype": "Mode of Payment",
                    "mode_of_payment": pay_type.payment_name,
                    "enabled":'1',
                    "type":"Bank"
                })
                mop.insert()

            if pay_type.amount != 0.00:                   
                    pe = frappe.new_doc("Payment Entry")
                    pe.payment_type = "Receive"
                    pe.mode_of_payment = pay_type.payment_name
                    pe.company = doc.company
                    pe.posting_date = doc.posting_date
                    pe.party_type = "Customer"
                    pe.party = doc.customer
                    pe.paid_to = "Cash - RPO"
                    pe.paid_amount = pay_type.amount
                    pe.received_amount = pay_type.amount

                    pe.append("references", {
                        "reference_doctype": "Sales Invoice",
                        "reference_name": doc.name,
                        "total_amount": pay_type.amount,
                        "outstanding_amount": pay_type.amount,
                        "allocated_amount": pay_type.amount
                    })
                    
                    pe.insert()
                    pe.submit()
                
            