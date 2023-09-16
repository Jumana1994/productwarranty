/** @odoo-module **/

import { registry } from "@web/core/registry";

import { Component } from  "@odoo/owl";

class MyClientAction extends Component {}
MyClientAction.template = "product_warranty.clientaction";

// remember the tag name we put in the first step
registry.category("actions").add("product_warranty.MyClientAction", MyClientAction);
