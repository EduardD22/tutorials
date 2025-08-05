import publicWidget from '@web/legacy/js/public/public_widget';
import VariantMixin from '@website_sale/js/sale_variant_mixin';
import '@website_sale/js/website_sale';

/**
 * @param {MouseEvent} ev - the event triggered
 */
VariantMixin.onClickAddCartJSON = function(ev) {
    ev.preventDefault();
    
    var $link = $(ev.currentTarget);
    var $input = $link.closest('.css_quantity').find('.quantity');
    
    // get webshop quantities
    var webshopQuantity = parseInt($input.data('webshop-quantity')) || 1;
    var webshopMinimumQuantity = parseInt($input.data('webshop-minimum-quantity')) || 1;
    var previousQty = parseFloat($input.val() || 0);
    
    // checking if it's incrementing or decrementing by targeting all possible combinations
    var isIncrement = $link.hasClass('fa-plus') || $link.find('.fa-plus').length > 0 ||
                     $link.attr('aria-label') === 'Add one' || $link.attr('title') === 'Add one';
    var isDecrement = $link.hasClass('fa-minus') || $link.find('.fa-minus').length > 0 ||
                     $link.attr('aria-label') === 'Remove one' || $link.attr('title') === 'Remove one';
    
    var newQty = previousQty;
    
    if (isIncrement) {
        if (previousQty < webshopMinimumQuantity) {
            newQty = webshopMinimumQuantity;
        } else {
            newQty = previousQty + webshopQuantity;
        }
    } else if (isDecrement) {
        // always substract but make sure not to go below minimum
        newQty = previousQty - webshopQuantity;
        
        if (newQty < webshopMinimumQuantity) {
            newQty = webshopMinimumQuantity;
        }
    } 
    
    // flag
    $input.data('webshop_button_clicked', true);
    
    if (newQty !== previousQty) {
        $input.val(newQty).trigger('change');
    }
    
    return false;
};

/**
 * overriding onChangeAddQuantity method to handle manual input validation
 * @param {Event} ev
 */
VariantMixin.onChangeAddQuantity = function(ev) {
    
    const $input = $(ev.currentTarget);
    
    // skip validation if this was triggered by our button click
    if ($input.data('webshop_button_clicked')) {
        $input.removeData('webshop_button_clicked');
        
        // still trigger variant change for price updates
        const $parent = $input.closest('form');
        if ($parent.length > 0) {
            this.triggerVariantChange($parent);
        }
        return;
    }
    
    var webshopQuantity = parseInt($input.data('webshop-quantity'));
    var webshopMinimumQuantity = parseInt($input.data('webshop-minimum-quantity'));
    
    // only validate if we have webshop configuration
    if (!webshopQuantity && !webshopMinimumQuantity) {
        // call original behavior if available
        const $parent = $input.closest('form');
        if ($parent.length > 0) {
            this.triggerVariantChange($parent);
        }
        return;
    }
    
    // Set defaults
    webshopQuantity = webshopQuantity || 1;
    webshopMinimumQuantity = webshopMinimumQuantity || 1;
    
    // manual input
    var quantity = parseFloat($input.val() || 0);
   
    // validate minimum
    if (quantity < webshopMinimumQuantity) {
        $input.val(webshopMinimumQuantity);
        quantity = webshopMinimumQuantity;
    } else {
        // step alignment
        var remainder = (quantity - webshopMinimumQuantity) % webshopQuantity;
        if (remainder !== 0) {
            var newQuantity = quantity + (webshopQuantity - remainder);
            $input.val(newQuantity);
        }
    }
    
    // trigger variant change for price updates
    const $parent = $input.closest('form');
    if ($parent.length > 0) {
        this.triggerVariantChange($parent);
    }
};

// apply overrides to the WebsiteSale widget
publicWidget.registry.WebsiteSale.include({
   
    onClickAddCartJSON: function() {
        return VariantMixin.onClickAddCartJSON.apply(this, arguments);
    },
    
   
    onChangeAddQuantity: function() {
        return VariantMixin.onChangeAddQuantity.apply(this, arguments);
    },
});