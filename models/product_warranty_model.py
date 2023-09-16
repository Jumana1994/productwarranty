# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from datetime import timedelta


class Warranty(models.Model):
    """new model creation for product warranty"""

    _name = "product.warranty.model"
    _description = "Warranty Request"
    _rec_name = "name"

    sale_order_id = fields.Many2one('sale.order', string='state')
    invoice_id = fields.Many2one('account.move', string="Invoice reference",
                                 domain="[('state','!=','draft')]")
    product_id = fields.Many2one('product.product', string="Product Name",
                                 required=True)
    lot_num_id = fields.Many2one('stock.lot', string="lot/serial number",
                                 domain="[('product_id', '=', product_id)]")
    request_date = fields.Date(string="Request date",
                               default=fields.Date.today())

    customer_details_id = fields.Many2one("res.partner", string="Customer",
                                          related='invoice_id.partner_id',store=True)
    current_user = fields.Many2one('res.users', 'Current User',
                                   default=lambda self: self.env.user)
    manager_id = fields.Many2one('res.users')
    purchase_date = fields.Date(string='Purchase date',
                                related='invoice_id.invoice_date',
                                readonly=True)
    name = fields.Char(string='Sequence number', copy=False, readonly=True,
                       Index=True,
                       default=lambda self: _('New'))
    warranty_exist = fields.Boolean(string=" Has warranty",
                                    related='product_id.warranty_exist')
    warranty_type = fields.Selection(
        [("service_type", "Service Type"),
         ("replacement_warranty", "Replacement warranty")],
        string='Warranty Type', default="replacement_warranty",
        related='product_id.warranty_type')
    warranty_period = fields.Integer(string="Warranty Period",
                                     related='product_id.warranty_period')
    warranty_exp_date = fields.Date(compute="compute_exp_date",
                                    string="Warranty Expiration Date",store=True)
    states = fields.Selection(
        [('draft', 'Draft'), ('to approve', 'To approve'),
         ('approved', 'Approved'),
         ('product received', 'Product received'), ('done', 'Done'),
         ('cancel', 'Cancel')],
        default='draft', string='State')

    warranty_relate_id = fields.One2many('product.template', 'property_id',
                                         string='Warranty Relation')
    location_id = fields.Many2one('stock.move', string='Warranty Location')
    # moves_count = fields.Integer(compute='compute_stock_moves', string='Count')
    stock_move_ids = fields.One2many('stock.move', 'warranty_requests_id',
                                     string="Stock Moves")

    # def compute_stock_moves(self):
    #     """compute stock moves in each invoice"""
    #     for record in self:
    #         record.moves_count = self.env['stock.picking'].search_count(
    #             [("origin", "=", self.name)])

    @api.depends('invoice_id', 'product_id.warranty_period')
    def compute_exp_date(self):
        """calculate warranty expiration date based on invoice date and warranty period"""
        for record in self:
            if record.invoice_id.invoice_date and record.product_id.warranty_period:
                record.warranty_exp_date = record.invoice_id.invoice_date + timedelta(
                    days=record.product_id.warranty_period)
            else:
                record.warranty_exp_date = False

    @api.model
    def get_product_options(self, invoice_id):
        options = []
        if invoice_id:
            invoice = self.env['account.move'].browse(int(invoice_id))
            for line in invoice.invoice_line_ids:
                if line.product_id.warranty_exist:
                    options.append(
                        (line.product_id.id, line.product_id.display_name))
        return {'options': options}

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        """fetching details from invoice based on onchange field"""
        if self.invoice_id:
            self.product_id = False

            invoice_lines = self.invoice_id.invoice_line_ids

            product_options = [
                (line.product_id.id, line.product_id.display_name) for line in
                invoice_lines if line.product_id.warranty_exist]
            return {'domain': {'product_id': [
                ('id', 'in', [option[0] for option in product_options])]}}

    @api.model
    def create(self, vals):
        """ sequence creation """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'product.warranty.model') or _('New')
        res = super(Warranty, self).create(vals)
        return res

    def action_to_approve(self):
        """action to confirm request"""
        self.write({'states': 'to approve'})

    def action_cancel(self):
        """action to cancel request"""
        self.write({'states': 'cancel'})

    def action_approve(self):
        self.states = 'approved'
        # stock_location = self.env.ref('stock.stock_location_customers')

    def create_smart_button(self):
        """
              To see the stock moves related to warranty.
              """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfers',
            'view_mode': "tree,form",
            'res_model': 'stock.picking',
            "domain": [("origin", "=", self.name)],
            "context": "{'create': False}",

        }

    def create_transfer(self, location_id, location_dest_id, picking_type):
        """ Used to create a transfer in stock picking."""

        stock_picking = self.env["stock.picking"].create({
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_type_id': picking_type,
            'partner_id': self.customer_details_id.id,
            'origin': self.name,
        })
        self.env["stock.move"].create({
            'product_id': self.product_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_id': stock_picking.id,
            'name': self.product_id.name,
            'quantity_done': 1,
        })
        stock_picking.action_confirm()
        # stock_picking.button_validate()

    def action_receive_product(self):
        """
              To receive products from customer to warranty location after approval for warranty for warranty
              """
        self.ensure_one()
        if self.warranty_type in ['replacement_warranty', 'service_type']:
            location_id = self.env.ref("stock.stock_location_customers").id
            location_dest_id = self.product_id.warranty_location_id.id
            picking_type = self.env.ref("stock.picking_type_internal").id
            self.create_transfer(location_id, location_dest_id, picking_type)
            self.write({'states': 'product received'})

    def action_return_product(self):
        """ To return product back to customer from warranty location to customer location to customer."""
        self.ensure_one()
        if self.warranty_type in ['replacement_warranty', 'service_type']:
            location_id = self.product_id.warranty_location_id.id
            location_dest_id = self.env.ref("stock.stock_location_customers").id
            picking_type = self.env.ref("stock.picking_type_out").id
            self.create_transfer(location_id, location_dest_id, picking_type)
            self.write({'states': 'done'}),

    def action_warranty_report(self):
        self.ensure_one()
        return {
            'name': 'Product Warranty',
            'res_model': 'warranty.report',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_order_id': self.id},
            'target': 'new',
        }

    # def action_share_warranty_request(self):
    #
    #     user_share_with = self.env['res.users']
    #
    #     if user_share_with:
    #         self.write({'manager_id': user_share_with.id})
    #
    #     return True

