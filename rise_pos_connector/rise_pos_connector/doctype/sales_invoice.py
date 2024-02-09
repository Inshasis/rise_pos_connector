# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe


def on_submit(doc,methods):
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.company = doc.company
    pe.posting_date = doc.posting_date
    pe.party_type = "Customer"
    pe.party = doc.customer
    pe.paid_to = "Cash - RP"
    pe.paid_amount = doc.grand_total
    pe.received_amount = doc.grand_total

    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": doc.name,
        "total_amount": doc.grand_total,
        "outstanding_amount": doc.grand_total,
        "allocated_amount": doc.grand_total
    })
    
    pe.insert()
    pe.submit()
