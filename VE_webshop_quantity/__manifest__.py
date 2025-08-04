{
    'name': 'Van Der Eng Webshop Quantity',
    'version': '18.0.1.0.0',
    'depends': ['sale_management', 'website_sale_stock'],
    'data': ['views/product_template.xml',
             'views/VE_templates.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'VE_webshop_quantity/static/src/js/VE_add_cart.js'
        ],
    },
    'license': 'OEEL-1',
    'category': 'Customizations',
    'author': 'Odoo PS',
    'website': 'https://www.odoo.com',
}