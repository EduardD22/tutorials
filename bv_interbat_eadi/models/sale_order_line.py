from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
     # Temporary field for debugging
    ecotax_debug_info = fields.Text(string="Ecotax Debug Info", readonly=True)
    
    def _is_ecotax_line(self):
        self.ensure_one()
        is_ecotax = bool(self.product_id and self.product_id.categ_id.is_ecotax_product)
        return is_ecotax
    
    def _should_apply_ecotax(self):
        self.ensure_one()
        partner = self.order_id.partner_id
        if not partner:
            return False
        
         # Check BEBAT (with exemption check)
        should_apply_bebat = partner._should_apply_bebat()
        # Check RECUPEL (no exemption)
        should_apply_recupel = partner._should_apply_recupel()
        
        should_apply = should_apply_bebat or should_apply_recupel
        
        return should_apply
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add ecotax lines automatically"""
        # First create the lines normally
        lines = super().create(vals_list)
        
        # Skip ecotax processing if we're creating an ecotax line
        # This prevents infinite recursion
        if self.env.context.get('skip_ecotax_check'):
            return lines
        
        # Now process each line to add ecotax if needed
        for line in lines:
            # Skip if no product
            if not line.product_id:
                continue
            
            # Skip if this IS an ecotax line
            if line._is_ecotax_line():
                line.ecotax_debug_info = "This is an ecotax line"
                continue
            
            # Check if we should apply ecotax
            if not line._should_apply_ecotax():
                line.ecotax_debug_info = "Ecotax not applicable (non-Belgian or exempt)"
                continue
            
            # Process nomenclatures
            if line.product_id.nomenclature_ids:
                debug_info = []
                debug_info.append(f"Processing ecotax for: {line.product_id.name}")
                
                for nomenclature in line.product_id.nomenclature_ids:
                    if not nomenclature.nomenclature_id:
                        debug_info.append("ERROR: Nomenclature missing ecotax product!")
                        continue
                    
                    ecotax_name = nomenclature.nomenclature_id.name.upper()
                    is_bebat = 'BEBAT' in ecotax_name
                    is_recupel = 'RECUPEL' in ecotax_name
                    
                    if is_bebat and not line.order_id.partner_id._should_apply_bebat():
                        continue
                    
                    if is_recupel and not line.order_id.partner_id._should_apply_recupel():
                        continue
                    
                    # Calculate quantity needed
                    ecotax_quantity = line.product_uom_qty * nomenclature.quantity
                    
                    debug_info.append(f"Creating ecotax line: {nomenclature.nomenclature_id.name}")
                    debug_info.append(f"  Quantity: {line.product_uom_qty} × {nomenclature.quantity} = {ecotax_quantity}")
                    
                    # Create the ecotax line
                    ecotax_vals = {
                        'order_id': line.order_id.id,
                        'product_id': nomenclature.nomenclature_id.product_variant_id.id,
                        'product_uom_qty': ecotax_quantity,
                        'product_uom': nomenclature.nomenclature_id.uom_id.id,
                        'discount': 0.0,  # No discount on ecotax
                    }
                    
                    # Create it! But prevent recursion
                    ecotax_line = self.env['sale.order.line'].with_context(skip_ecotax_check=True).create(ecotax_vals)
                    debug_info.append(f"  Created line ID: {ecotax_line.id}")
                
                line.ecotax_debug_info = "\n".join(debug_info)
            else:
                line.ecotax_debug_info = "No nomenclatures configured"
        
        return lines