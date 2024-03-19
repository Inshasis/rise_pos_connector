// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Item'] = {
	onload: function(listview) {
	   listview.page.add_inner_button("Sync Items", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.item.sync_items_rise_api",
			   args: {},
			   freeze:true,
			   freeze_message:__("Sync Items")
		   });
	   });
	}
   };