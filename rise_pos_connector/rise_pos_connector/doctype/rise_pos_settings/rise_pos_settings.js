// Copyright (c) 2024, Huda Infoteh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rise POS Settings', {
	refresh: function(frm) {
		// Add a custom button to trigger the API call
		frm.add_custom_button(__('Get All Shops'), function() {

			frappe.call({
				method: 'rise_pos_connector.rise_pos_connector.doctype.rise_pos_settings.rise_pos_settings.get_all_customers',
				args: {
					licence_no: frm.doc.licence_no,
					api_key:frm.doc.api_key
				},
				callback: function(response) {
					frm.refresh();
				}
			});
		});
	}
	
});
