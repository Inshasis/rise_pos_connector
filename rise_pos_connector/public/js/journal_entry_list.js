// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Journal Entry'] = {
	onload: function(listview) {
	   listview.page.add_inner_button("Sync Expenses", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.sync_jv.sync_jv_rise_api",
			   args: {},
			   freeze:true,
			   freeze_message:__("Sync Expenses")
		   });
	   });
	}
   };