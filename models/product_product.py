# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import timedelta


class Product(models.Model):
    """ warranty details to be added to product form"""
    _inherit = "product.product"
    slug = fields.Char(string="Slug", compute='_compute_slug', store=True,
                       index=True, readonly=True)

    def _compute_slug(self):
        for product in self:
            product.slug = product.name.replace(' ',
                                                '-').lower()  # Create a basic slug from the product name

