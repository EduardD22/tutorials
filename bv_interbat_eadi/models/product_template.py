from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit  = "product.template"
    
    nomenclature_ids = fields.One2many(
        'recupel.nomenclature',
        'product_template_id',
        string='Ecotax Nomenclatures',
        help='BEBAT and RECUPEL ecotaxes for this product'
    )