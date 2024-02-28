# Copyright (c) 2024, Huda Infoteh and contributors
# For license information, please see license.txt

from faulthandler import is_enabled
import frappe
from frappe.model.document import Document
import json
import requests

class RisePOSSettings(Document):
	def validate(self):
		if self.enable == 0:
			self.set("api_key", '')
			self.set("company", '')
			self.set("abbr", '')
			self.set("url", '')
			self.set("licence_no", '')
			self.set("status", 'Inactive')
			self.set("shop_code_details", [])
		
	def before_save(self):
		if self.enable == 1: 
			url = self.url+"/erp/get_all_shops"
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
						frappe.msgprint("API Key and Licence No is Missing or Invalid. Try Updating Your Details.")
						self.status = 'Inactive'
						self.set("shop_code_details", [])
					
				except json.JSONDecodeError as e:
					frappe.msgprint(f"Error decoding JSON: {e}")
			else:
				frappe.msgprint(f"Error: {response.status_code} - {response.text}")

@frappe.whitelist()
def get_all_customers(licence_no,api_key):
	rps = frappe.get_doc('Rise POS Settings')
	url = rps.url+"/erp/get_all_shops"
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
				# rps = frappe.get_doc('Rise POS Settings')
				# rps.append('shop_code_details', {'merchant_id': shop['merchant_id'],'shop_code':shop['shop_code'], 'shop_name': shop['name'], 'shop_phone': shop['shop_phone_number'],'erp_token':shop['erp_token'],'latitude': shop['location']['latitude'],'longitude': shop['location']['longitude'],'address': shop['location']['address']})
				# rps.save(ignore_permissions=True)
				
				# Create Warehouse
				wh_list = frappe.get_list('Warehouse', fields=['warehouse_name'])
				check_wh = {'warehouse_name': shop['name']}
				if check_wh not in wh_list:
					warehouse = frappe.get_doc({
						"doctype": "Warehouse",
						"warehouse_name": shop['name'],
						"custom_shop_code": shop['shop_code']
					})
					warehouse.insert()

			return data['result']['shops']	
				
		except json.JSONDecodeError as e:
			frappe.msgprint(f"Error decoding JSON: {e}")
	else:
		frappe.msgprint(f"Error: {response.status_code} - {response.text}")