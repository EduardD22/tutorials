import publicWidget from '@web/legacy/js/public/public_widget';
import WebsiteSale from '@website_sale/js/website_sale';
import '@website_sale/js/website_sale';

/**
 * @param {MouseEvent} ev - the event triggered
 */

WebsiteSale._onClickAddCartJSON = function(ev) {
    ev.preventDefault();
    var $link = $(ev.currentTarget);
    var $input = $link.closest('.css_quantity').find('.quantity');
    var webshopQuantity = parseInt($input.data('webshop-quantity')) || 1;
    var webshopMinimumQuantity = parseInt($input.data('webshop-minimum-quantity')) || 1;
    var previousQty = parseFloat($input.val() || 0);

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
    $input.data('webshop_cart_button_clicked', true);
    
    if (newQty !== previousQty) {
        $input.val(newQty).trigger('change');
    }
    
    return false;

}

publicWidget.registry.WebsiteSale.include({
   
    onClickAddCartJSON: function() {
        return WebsiteSale._onClickAddCartJSON.apply(this, arguments);
    },
    
});

WebsiteSale._onChangeCartQuantity = function(ev) {
    
    var $input = $(ev.currentTarget);
    if ($input.data('update_change')) {
        return;
    }

    var webshopQuantity = parseInt($input.data('webshop-quantity'));
    var webshopMinimumQuantity = parseInt($input.data('webshop-minimum-quantity'));
    var value = parseInt($input.val() || 0, 10);

    if (isNaN(value)) {
        value = 1;
    }

    if (!$input.data('webshop_cart_button_clicked') && parseInt(value) !== 0) {
       if (value < webshopMinimumQuantity) {
           $input.val(webshopMinimumQuantity);
           value = webshopMinimumQuantity
       } else {
           var remainder = (value - webshopMinimumQuantity) % webshopQuantity;
           if (remainder !== 0) {
               var newQuantity = value + (webshopQuantity - remainder);
               $input.val(newQuantity);
           }
       }
    }

    $input.removeData('webshop_cart_button_clicked');
    var $dom = $input.closest('tr');
    var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
    var line_id = parseInt($input.data('line-id'), 10);
    var productIDs = [parseInt($input.data('product-id'), 10)];
    this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
}

publicWidget.registry.WebsiteSale.include({
   
    _onChangeCartQuantity: function() {
        return WebsiteSale._onChangeCartQuantity.apply(this, arguments);
    },
});