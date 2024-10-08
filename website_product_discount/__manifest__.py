# -*- coding: utf-8 -*-

{
    'name': "Website Product Discount",
    'version': '17.0',
    'category': '',
    "sequence": 3,
    'summary': "This module is used for a Product Discount Feature where a percentage discount can be applied to specific products, and the discounted price should be reflected in the product listings and on the product detail page in the eCommerce store",
    "license": "LGPL-3",
    'author': 'Rminds Inc.',
    'depends': ["base",'website_sale','product'],
    'data': [
        "views/product_template_view.xml",
        "views/template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
