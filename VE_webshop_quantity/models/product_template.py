from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    webshop_quantity = fields.Integer(string="Webshop Quantity",default=1)
    webshop_minimum_quantity = fields.Integer(string="Minimum Quantity",default=1)