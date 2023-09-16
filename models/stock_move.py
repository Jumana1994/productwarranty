# -*- coding: utf-8 -*-
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    warranty_requests_id = fields.Many2one('product.warranty.model', string="warranty request")
