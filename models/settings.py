from odoo import models, fields

class ManufacturingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mo_po_required_products = fields.Many2many(
        'product.product',
        string='PO required for MOs with:',
        help="Select the products for which a PO is required when creating a Manufacturing Order."
    )

    def set_values(self):
        super(ManufacturingSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'custom_mrp.mo_po_required_products', ','.join(map(str, self.mo_po_required_products.ids))
        )

    def get_values(self):
        res = super(ManufacturingSettings, self).get_values()
        product_ids = self.env['ir.config_parameter'].sudo().get_param(
            'custom_mrp.mo_po_required_products', default=''
        )
        res.update(
            mo_po_required_products=[(6, 0, list(map(int, product_ids.split(','))))] if product_ids else False,
        )
        return res
