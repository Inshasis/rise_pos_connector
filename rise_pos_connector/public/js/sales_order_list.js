// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Sales Order'] = {
	onload: function(listview) {
	   listview.page.add_inner_button("Sync Order", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.order.sync_orders_rise_api",
			   args: {},
		   });
	   });
	}
};