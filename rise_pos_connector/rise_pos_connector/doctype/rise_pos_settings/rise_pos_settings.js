// Copyright (c) 2024, Huda Infoteh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rise POS Settings', {
	refresh(frm) {
	    if(cur_frm.doc.enable && cur_frm.doc.status == "Active"){
	        frm.set_df_property('url',  'hidden', 1);
	        frm.set_df_property('api_key',  'hidden', 1);
	    }
	},
	validate(frm) {
	    if(cur_frm.doc.enable && cur_frm.doc.status == "Active"){
	        frm.set_df_property('url',  'hidden', 1);
	        frm.set_df_property('api_key',  'hidden', 1);
	    }
	},
	enable(frm) {
	    if(cur_frm.doc.enable){
	        frm.set_df_property('url',  'reqd', 1);
	        frm.set_df_property('api_key',  'reqd', 1);
	        frm.set_df_property('licence_no',  'reqd', 1);
	    }
	    else{
	        frm.set_df_property('url',  'reqd', 0);
	        frm.set_df_property('api_key',  'reqd', 0);
	        frm.set_df_property('licence_no',  'reqd', 0);
	    }
	},
	refresh: function(frm) {
		// Add a custom button to trigger the API call
		frm.add_custom_button(__('Get All Shops'), function() {

			frappe.call({
				method: 'rise_pos_connector.rise_pos_connector.doctype.rise_pos_settings.rise_pos_settings.get_all_customers',
				args: {
					licence_no: frm.doc.licence_no,
					api_key:frm.doc.api_key
				},
				callback: function(r) {
					console.log(r)
					frm.doc.shop_code_details = []
					$.each(r.message, function(_i, e){
						let entry = frm.add_child("shop_code_details");
						entry.merchant_id = e.merchant_id;
						entry.shop_code = e.shop_code;
						entry.shop_name = e.name;
						entry.shop_phone = e.shop_phone_number;
						entry.erp_token = e.erp_token;
						entry.latitude = e.location['latitude'];
						entry.longitude = e.location['longitude'];
						entry.address = e.location['address'];
					})
					refresh_field("shop_code_details")
					frm.save();
				}
			});
		});
	}
	
});
