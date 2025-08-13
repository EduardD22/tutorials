from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RecupelNomenclature(models.Model):
    _name = 'recupel.nomenclature'
    _description = 'Ecotax Nomenclature Config'
    
    nomenclature_id = fields.Many2one(
        'product.template',
        string='Nomenclature',
    )
    
    product_id = fields.Many2one(
        'product.template',
        string='Ecotax Product',
    )
    
    quantity = fields.Integer(
        string='Quantity',
        default=1,
        help='Number of batteries in this product package'
    )
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Battery quantity must be greater than zero!")