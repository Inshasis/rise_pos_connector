# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe


def on_submit(doc,methods):
    rps = frappe.get_doc('Rise POS Settings')
    if doc.outstanding_amount != 0.00:
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
            if pay_type.amount != 0.00 and pay_type.code != "PAYT0001" and pay_type.payment_entry == 0:  
                #Order Payment Summary Payment Entry 
                frappe.db.set_value('Order Payment Summary', str(pay_type.name), {
                    'payment_entry': '1'
                })
                frappe.db.commit()
                #Payment Entry
                pe = frappe.new_doc("Payment Entry")
                pe.payment_type = "Receive"
                pe.mode_of_payment = pay_type.payment_name
                pe.company = doc.company
                pe.posting_date = doc.posting_date
                pe.party_type = "Customer"
                pe.party = doc.customer
                pe.paid_to = "Cash - "+rps.abbr
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
                frappe.db.commit()
            

def on_change(doc,methods):
    rps = frappe.get_doc('Rise POS Settings')
    if doc.docstatus == 1 and doc.outstanding_amount != 0.00 and doc.status == "Partly Paid" or doc.status == "Partly Paid and Discounted" or doc.status == "Overdue and Discounted" or doc.status == "Overdue":
        for pay_type in doc.custom_payment_summary:
            #Create Mode of Payment
            # mop_check = frappe.get_list('Mode of Payment', fields=['mode_of_payment'])
            # check = {'mode_of_payment': pay_type.payment_name}
            # if check not in mop_check:
            #     mop = frappe.get_doc({
            #         "doctype": "Mode of Payment",
            #         "mode_of_payment": pay_type.payment_name,
            #         "enabled":'1',
            #         "type":"Bank"
            #     })
            #     mop.insert()
            if pay_type.amount != 0.00 and pay_type.code != "PAYT0001" and pay_type.payment_entry == 0:
                #Order Payment Summary Payment Entry 
                frappe.db.set_value('Order Payment Summary', str(pay_type.name), {
                    'payment_entry': '1'
                })
                frappe.db.commit()
                # Payment Entry
                pe = frappe.new_doc("Payment Entry")
                pe.payment_type = "Receive"
                pe.mode_of_payment = pay_type.payment_name
                pe.company = doc.company
                pe.posting_date = doc.posting_date
                pe.party_type = "Customer"
                pe.party = doc.customer
                pe.paid_to = "Cash - "+rps.abbr
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
                frappe.db.commit()