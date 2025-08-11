from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    def _is_ecotax_line(self):
        self.ensure_one()
        is_ecotax = bool(self.product_id and self.product_id.categ_id.is_ecotax_product)
        return is_ecotax
    
    def _should_apply_ecotax(self):
        self.ensure_one()
        partner = self.order_id.partner_id
        if not partner:
            return False
        
        should_apply_bebat = partner._should_apply_bebat()
        should_apply_recupel = partner._should_apply_recupel()
        should_apply = should_apply_bebat or should_apply_recupel
        
        return should_apply
    
    def write(self, vals):
        # skip if updating ecotax lines themselves (prevent recursion)
        if self.env.context.get('skip_ecotax_check'):
            return super().write(vals)
        
        old_values = {}
        for line in self:
            old_values[line.id] = {
                'product_id': line.product_id,
                'quantity': line.product_uom_qty,
                'is_ecotax': line._is_ecotax_line()
            }
            
        # the actual write
        result = super().write(vals)
        
        # check what changed and update ecotax
        for line in self:
            old = old_values[line.id]
            
            if old['is_ecotax']:
                continue
            
            # check if quantity changed
            if 'product_uom_qty' in vals and old['quantity'] != line.product_uom_qty:
                # only update if customer should have ecotax
                if line._should_apply_ecotax() and line.product_id:
                    line._update_ecotax_quantities()
        
        return result
    
    def _update_ecotax_quantities(self):
        self.ensure_one()
        
        if not self.product_id or not self.product_id.nomenclature_ids:
            return
        
        partner = self.order_id.partner_id
        apply_bebat = partner._should_apply_bebat()
        apply_recupel = partner._should_apply_recupel()
        
        for nomenclature in self.product_id.nomenclature_ids:
            if not nomenclature.nomenclature_id:
                continue
            
            ecotax_name = nomenclature.nomenclature_id.name.upper()
            is_bebat = 'BEBAT' in ecotax_name
            is_recupel = 'RECUPEL' in ecotax_name
            
            # kkip if not applicable
            if (is_bebat and not apply_bebat) or (is_recupel and not apply_recupel):
                continue
            
            # calculate new quantity
            new_ecotax_qty = self.product_uom_qty * nomenclature.quantity
            
            ecotax_product = nomenclature.nomenclature_id.product_variant_id
            if not ecotax_product:
                continue
            
            # find the ecotax line in the order
            ecotax_line = self.order_id.order_line.filtered(
                lambda l: l.product_id == ecotax_product and l._is_ecotax_line()
            )
            
            if ecotax_line:
                # update the quantity with context flag to prevent recursion
                ecotax_line.with_context(skip_ecotax_check=True).write({
                    'product_uom_qty': new_ecotax_qty
                })
    
    @api.model_create_multi
    def create(self, vals_list):
        
        # calling parent to create line normally
        lines = super().create(vals_list)
        
        # skip ecotax processing if we're creating an ecotax line
        if self.env.context.get('skip_ecotax_check'):
            return lines
        
        for line in lines:
            if not line.product_id:
                continue
            
            # skip ecotax line
            if line._is_ecotax_line():
                continue
            
            # if we don't need to apply ecotax (non-Belgian or exempt) continue
            if not line._should_apply_ecotax():
                continue
            
            # process nomenclatures
            if line.product_id.nomenclature_ids:
                
                for nomenclature in line.product_id.nomenclature_ids:
                    if not nomenclature.nomenclature_id:
                        continue
                    
                    ecotax_name = nomenclature.nomenclature_id.name.upper()
                    is_bebat = 'BEBAT' in ecotax_name
                    is_recupel = 'RECUPEL' in ecotax_name
                    
                    if is_bebat and not line.order_id.partner_id._should_apply_bebat():
                        continue
                    
                    if is_recupel and not line.order_id.partner_id._should_apply_recupel():
                        continue
                    
                    # calculate quantity 
                    ecotax_quantity = line.product_uom_qty * nomenclature.quantity
                    
                    # create the ecotax line
                    ecotax_vals = {
                        'order_id': line.order_id.id,
                        'product_id': nomenclature.nomenclature_id.product_variant_id.id,
                        'product_uom_qty': ecotax_quantity,
                        'product_uom': nomenclature.nomenclature_id.uom_id.id,
                        'discount': 0.0,
                    }
                    
                    # creating line and preventing recursion
                    self.env['sale.order.line'].with_context(skip_ecotax_check=True).create(ecotax_vals)
        
        return lines
    
    def unlink(self):
        ecotax_to_remove = self.env['sale.order.line']
        
        # checks to skip wrong lines
        for line in self:
            if line._is_ecotax_line():
                continue
            
            if not line.product_id or not line.product_id.nomenclature_ids:
                continue
            
            for nomenclature in line.product_id.nomenclature_ids:
                if not nomenclature.nomenclature_id:
                    continue
                
                ecotax_product = nomenclature.nomenclature_id.product_variant_id
                if not ecotax_product:
                    continue
                
                # finding the ecotax line
                ecotax_line = line.order_id.order_line.filtered(
                    lambda l: l.product_id == ecotax_product and l._is_ecotax_line()
                )
                
                if ecotax_line:
                    # checking if any OTHER line needs this ecotax
                    other_lines_need_it = False
                    for other_line in line.order_id.order_line:
                        # skiping the line being deleted and ecotax lines
                        if other_line == line or other_line._is_ecotax_line():
                            continue
                        
                        # check if this other line needs the same ecotax
                        if other_line.product_id:
                            for other_nom in other_line.product_id.nomenclature_ids:
                                if other_nom.nomenclature_id == nomenclature.nomenclature_id:
                                    other_lines_need_it = True
                                    break
                        
                        if other_lines_need_it:
                            break
                    
                    if not other_lines_need_it:
                        # no other line needs this ecotax so adding to ecotax_to_remove
                        ecotax_to_remove |= ecotax_line
        
        # deleting the parent lines first
        result = super().unlink()
        
        # then delete the ecotax lines that are no longer needed
        if ecotax_to_remove:
            ecotax_to_remove.unlink()
        
        return result