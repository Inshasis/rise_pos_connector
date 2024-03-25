// Copyright (c) 2024, InshaSiS Technologes and contributors
// For license information, please see license.txt

frappe.listview_settings['Material Request'] = {
	onload: function(listview) {
	   listview.page.add_inner_button("Sync Material Request", function() {
		   frappe.call({
			   method: "rise_pos_connector.utils.sync_material.sync_material_rise_api",
			   args: {},
			   freeze:true,
			   freeze_message:__("Sync Material Request")
		   });
	   });
	}
   };