// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Sales Invoice'] = {
	onload: function(listview) {
	//    listview.page.add_inner_button("Update Invoice", function() {
	// 	   frappe.call({
	// 		   method: "rise_pos_connector.utils.update_order.update_invoice_rise_api",
	// 		   args: {},
	// 		   freeze:true,
	// 		   freeze_message:__("Update Invoice")
	// 	   });
	//    });
	   
	   listview.page.add_inner_button("Sync Invoice", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.order.sync_invoice_rise_api",
			   args: {},
			   freeze:true,
			   freeze_message:__("Sync Invoice")
		   });
	   });
	   
	//    listview.page.add_inner_button("Cancel Invoice", function() {
	// 	   frappe.call({
	// 		   method: "rise_pos_connector.utils.order_cancel.cancel_invoice_rise_api",
	// 		   args: {},
	// 		   freeze:true,
	// 		   freeze_message:__("Cancel Invoice")
	// 	   });
	//    });
	}
   };