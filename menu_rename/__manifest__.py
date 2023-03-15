# -*- coding: utf-8 -*-
{
    'name': "Menu Rename ",

    'summary': """ Menu Rename for customer""",

    'description': """ """,

    'author': "Samah kandil",
    'website': " ",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode

}
