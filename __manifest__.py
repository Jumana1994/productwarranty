{
    "name": "Warranty Module",
    "version": "16.0.1.0.0",
    "author": "cybrosys",
    "description": "product warranty module",
    'license': 'LGPL-3',
    "depends": [
        "base_setup",
        "sale",
        "account",
        "product",
        'stock',
        'sale_management',
        'website',
        'web',
        'website_sale',

    ],
    "data": [
        "security/security_access_groups.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/warranty_location.xml",
        "view/product_warranty_model_view.xml",
        "view/account_move_view.xml",
        "view/product_template_view.xml",
        "view/stock_move_view.xml",
        "wizard/warranty_report_view.xml",
        'reports/report_template.xml',
        'reports/warranty_report.xml',
        'view/warranty_request_view.xml',
        'view/online_template_view.xml',
        'view/snippet_template_view.xml',
    ],
    'assets': {
        'web.assets_backend':
            ['product_warranty/static/src/js/action_manager.js', ],
        'web.assets_frontend':
            ['product_warranty/static/src/js/online_warranty.js',
             'product_warranty/static/src/js/warranty_snippet.js',
             # 'product_warranty/static/src/js/client_action.js',
             'product_warranty/static/src/xml/dynamic_carousel.xml',
             # 'product_warranty/static/src/js/client_action.xml',

             ]

    },

    "application": True,
    "installable": True,

}
