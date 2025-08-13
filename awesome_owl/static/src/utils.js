import { useRef, onMounted } from "@odoo/owl";

export function useAutofocus(elRef) {
    const ref = useRef(elRef);
    onMounted(() => {
        ref.el.focus();
    });
}