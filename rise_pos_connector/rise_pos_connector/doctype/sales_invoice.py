# Copyright (c) 2024, InshaSiS Technologies and contributors
# For license information, please see license.txt

import frappe


def on_submit(doc,methods):
    if doc.rounded_total != 0.00:
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.company = doc.company
        pe.posting_date = doc.posting_date
        pe.party_type = "Customer"
        pe.party = doc.customer
        pe.paid_to = "Cash - RPO"
        pe.paid_amount = doc.rounded_total
        pe.received_amount = doc.rounded_total

        pe.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": doc.name,
            "total_amount": doc.rounded_total,
            "outstanding_amount": doc.rounded_total,
            "allocated_amount": doc.rounded_total
        })
        
        pe.insert()
        pe.submit()
