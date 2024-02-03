# Copyright (c) 2024, Huda Infoteh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import requests

class RisePOSSettings(Document):
	def before_save(self):
		url = "http://dev.onegreendiary.com/erp/get_all_shops"

		# Define the JSON payload
		payload = {
			"licence_no": self.licence_no
		}

		# Specify the API key in the headers
		headers = {
			"api_key": self.api_key
		}

		# Make a POST request
		response = requests.post(url, json=payload, headers=headers)
		
		if response.status_code == 200:
			try:
				# Attempt to parse the JSON content of the response
				data = response.json()
				if data['status'] == 1:
					self.status = 'Active'
				else:
					frappe.msgprint("API key and Licence No is missing or invalid. Try updating your application.")
					self.status = 'Inactive'
				
			except json.JSONDecodeError as e:
				frappe.msgprint(f"Error decoding JSON: {e}")
		else:
			frappe.msgprint(f"Error: {response.status_code} - {response.text}")

@frappe.whitelist()
def get_all_customers(licence_no,api_key):

	url = "http://dev.onegreendiary.com/erp/get_all_shops"

	# Define the JSON payload
	payload = {
		"licence_no": licence_no
	}

	# Specify the API key in the headers
	headers = {
		"api_key": api_key
	}

	# Make a POST request
	response = requests.post(url, json=payload, headers=headers)

	if response.status_code == 200:
		try:
			# Attempt to parse the JSON content of the response
			data = response.json()
			for shop in data['result']['shops']:
				rps = frappe.get_doc('Rise POS Settings')
				rps.append('shop_code_details', {'merchant_id': shop['merchant_id'],'shop_code':shop['shop_code'], 'shop_name': shop['name'],'erp_token':shop['erp_token']})
				rps.save(ignore_permissions=True)
				
		except json.JSONDecodeError as e:
			frappe.msgprint(f"Error decoding JSON: {e}")
	else:
		frappe.msgprint(f"Error: {response.status_code} - {response.text}")