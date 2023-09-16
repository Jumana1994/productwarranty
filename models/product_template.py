# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import timedelta


class Product(models.Model):
    """ warranty details to be added to product form"""
    _inherit = "product.template"

    warranty_exist = fields.Boolean(string=" Has warranty")
    warranty_period = fields.Integer(string="Warranty Period(days)")
    warranty_type = fields.Selection(
        [("service_type", "Service Type"), ("replacement_warranty", "Replacement warranty")],
        string='Warranty Type', default="replacement_warranty")
    property_id = fields.Many2one('product.warranty.model', string="property")

    warranty_location_id = fields.Many2one('stock.location', string='Warranty Location')
