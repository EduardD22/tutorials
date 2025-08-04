import publicWidget from '@web/legacy/js/public/public_widget';
import VariantMixin from '@website_sale/js/sale_variant_mixin';
import { patch } from "@web/core/utils/patch";


patch(VariantMixin, {

    onClickAddCartJSON(ev) {
        const $input = $(ev.currentTarget).closest("input-group").find("input[name='add_qty']");
        const webshopQuantity = parseInt($input.data("webshop-quantity") || 1);
        const webshopMinQuantity = parseInt($input.data("webshop-minimum-quantity") || 1);
        const currentQty = parseInt($input.val()) || webshopMinQuantity;

        let increment; 
        if (webshopQuantity === 1) {
            increment = 1;
        } else if (webshopQuantity === 10) {
            increment = 10;
        } else if (webshopQuantity === 100) {
            increment = 100;
        } else {
            increment = webshopQuantity;
        }

        const newQty = currentQty + increment;

        $input.val(newQty);

        return super.onClickAddCartJSON(ev);
    }
});

