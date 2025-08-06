from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    bebat_exemption = fields.Boolean(
        string='Vrijstelling op BEBAT',
        default=False,
        help='Check if this Belgian customer is exempt from BEBAT'
    )
    
    def _should_apply_bebat(self):
        self.ensure_one()
        belgium = self.env.ref('base.be', raise_if_not_found=False)
        if not belgium:
            return False
        
        is_belgian = self.country_id == belgium
        # applying bebat if belgian and field not checked
        return is_belgian and not self.bebat_exemption
    
    def _should_apply_recupel(self):
        self.ensure_one()
        belgium = self.env.ref('base.be', raise_if_not_found=False)
        if not belgium:
            return False
        
        return self.country_id == belgium