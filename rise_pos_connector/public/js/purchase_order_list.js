// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Purchase Order'] = {
	onload: function(listview) {
	   listview.page.add_inner_button("Sync Purchase Order", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.sync_po.sync_po_rise_api",
			   args: {},
			   freeze:true,
			   freeze_message:__("Sync Purchase Order")
		   });
	   });
	}
   };