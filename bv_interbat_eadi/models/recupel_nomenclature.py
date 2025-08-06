from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RecupelNomenclature(models.Model):
    _name = 'recupel.nomenclature'
    _description = 'Ecotax Nomenclature Config'
    
    # parent product that contains batteries
    product_template_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
        help='The product that contains batteries requiring ecotax'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Ecotax Product',
        required=True,
        help='The ecotax product to be added to the order'
    )
    
    quantity = fields.Integer(
        string='Battery Quantity',
        default=1,
        required=True,
        help='Number of batteries in this product package'
    )
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Battery quantity must be greater than zero!")