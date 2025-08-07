from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_ecotax_product = fields.Boolean(string="Ecotax Product", default=False)