from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    number_plate = fields.Char(string="Number Plate")
