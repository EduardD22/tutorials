from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    _inherit = 'sale.order'
    
    @api.onchange('order_line')
    def _onchange_order_line_ecotax(self):
        if not self.partner_id:
            return
        
        apply_bebat = self.partner_id._should_apply_bebat()
        apply_recupel = self.partner_id._should_apply_recupel()
        
        if not apply_bebat and not apply_recupel:
            return
        
        ecotax_needed = {}  # {ecotax_product_id: total_quantity}
        
        # calculate total quantities needed for each ecotax
        for line in self.order_line:
            
            if line.product_id and line.product_id.categ_id.is_ecotax_product:
                continue
            
            if not line.product_id:
                continue
            
            for nomenclature in line.product_id.nomenclature_ids:
                if not nomenclature.nomenclature_id:
                    continue
                
                ecotax_name = nomenclature.nomenclature_id.name.upper()
                is_bebat = 'BEBAT' in ecotax_name
                is_recupel = 'RECUPEL' in ecotax_name
                
                if (is_bebat and not apply_bebat) or (is_recupel and not apply_recupel):
                    continue
                
                # getting the actual product(Recupel or Bebat)
                ecotax_product = nomenclature.nomenclature_id.product_variant_id
                if not ecotax_product:
                    continue
                
                # if nomenclature id already present in the map, add quantity to the already present quantity
                # if not just add nomenclature with the quantity
                qty_needed = line.product_uom_qty * nomenclature.quantity
                if ecotax_product.id in ecotax_needed:
                    ecotax_needed[ecotax_product.id] += qty_needed
                else:
                    ecotax_needed[ecotax_product.id] = qty_needed
        
        # updating existing ecotax lines with the calculated quantities
        for line in self.order_line:
            # ONLY process ecotax lines
            if not line.product_id or not line.product_id.categ_id.is_ecotax_product:
                continue
            
            # checking if we have a new quantity for this ecotax
            if line.product_id.id in ecotax_needed:
                new_qty = ecotax_needed[line.product_id.id]
                if line.product_uom_qty != new_qty:
                    line.product_uom_qty = new_qty