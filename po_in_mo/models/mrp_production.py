# models/mrp_production.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchase_order = fields.Many2one('purchase.order', string='Purchase Order', domain="[('id', 'in', available_purchase_orders)]")

    available_purchase_orders = fields.Many2many('purchase.order', compute='_compute_available_purchase_orders')

    partner_id = fields.Many2one('res.partner', string='Farmer')

    number_plate = fields.Char(string="Number Plate", readonly="true")

    @api.depends('product_id', 'partner_id')
    def _compute_available_purchase_orders(self):
        """
        Compute the list of available Purchase Orders that are not yet linked to any Manufacturing Order.
        """
        # Fetch all Purchase Orders that are already linked to any Manufacturing Order
        linked_po_ids = self.env['mrp.production'].search([('purchase_order', '!=', False)]).mapped('purchase_order.id')

        # Create domain for available POs
        domain = [('id', 'not in', linked_po_ids)]

        # If a customer is selected, filter POs by the customer's partner_id
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        
        # Find POs that are not linked to any Manufacturing Order and match the domain
        available_pos = self.env['purchase.order'].search(domain)

        # Assign the available POs to each MO record
        for record in self:
            record.available_purchase_orders = available_pos

    @api.onchange('partner_id')  # Trigger when the customer is selected
    def _onchange_partner_id(self):
        """
        Update available Purchase Orders when the customer is changed.
        """
        self.available_purchase_orders = self.env['purchase.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('id', 'not in', self.env['mrp.production'].search([('purchase_order', '!=', False)]).mapped('purchase_order.id'))
        ])

    @api.onchange('purchase_order')
    def _onchange_purchase_order(self):
        """
        When a Purchase Order is selected, add the total PO quantity to the MO quantity.
        """
        if self.purchase_order:
            # Get all PO lines and sum the quantities of the products (raw materials)
            total_po_qty = sum(self.purchase_order.order_line.mapped('product_qty'))

            # Add the total PO quantity to the MO quantity
            self.product_qty = total_po_qty

            """ Fetch the Number Plate from the selected PO and assign it to the MO """
            # Number Plate is stored in purchase.order as a field 'number_plate'
            self.number_plate = self.purchase_order.number_plate
        else:
            self.number_plate = False

    @api.constrains('product_id', 'purchase_order')
    def _check_purchase_order_required(self):
        """
        Ensure a Purchase Order is required for products selected in the settings.
        """
        param = self.env['ir.config_parameter'].sudo().get_param('custom_mrp.mo_po_required_products', '')
        required_product_ids = list(map(int, param.split(','))) if param else []
        if self.product_id.id in required_product_ids and not self.purchase_order:
            raise ValidationError('A Purchase Order is required for this Manufacturing Order.')

    @api.model
    def create(self, vals):
        # Validate before creating an MO
        product_id = vals.get('product_id')
        purchase_order = vals.get('purchase_order')

        param = self.env['ir.config_parameter'].sudo().get_param('custom_mrp.mo_po_required_products', '')
        required_product_ids = list(map(int, param.split(','))) if param else []

        if product_id in required_product_ids and not purchase_order:
            raise ValidationError('A Purchase Order is required for this Manufacturing Order.')

        """ Set the number plate when creating a new Manufacturing Order """
        if vals.get('purchase_order'):
            po = self.env['purchase.order'].browse(vals['purchase_order'])
            vals['number_plate'] = po.number_plate

            """ Set quantity """
            total_po_qty = sum(po.order_line.mapped('product_qty'))
            vals['product_qty'] = total_po_qty

        return super(MrpProduction, self).create(vals)

    def write(self, vals):
        # Validate on update
        product_id = vals.get('product_id', self.product_id.id)
        purchase_order = vals.get('purchase_order', self.purchase_order.id)

        param = self.env['ir.config_parameter'].sudo().get_param('custom_mrp.mo_po_required_products', '')
        required_product_ids = list(map(int, param.split(','))) if param else []

        if product_id in required_product_ids and not purchase_order:
            raise ValidationError('A Purchase Order is required for this Manufacturing Order.')

        """ Set the number plate when updating a Manufacturing Order """
        if vals.get('purchase_order'):
            po = self.env['purchase.order'].browse(vals['purchase_order'])
            vals['number_plate'] = po.number_plate

            """ Set MO quantity """
            total_po_qty = sum(po.order_line.mapped('product_qty'))
            vals['product_qty'] = total_po_qty

        return super(MrpProduction, self).write(vals)
