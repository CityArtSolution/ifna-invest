# -*- coding: utf-8 -*-
{
    'name': "Renting Workflow Customization",
    'summary': """Sale Renting Workflow""",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['sale_renting', 'renting', 'sale', 'base', 'product','account','stock'],
    'data': [
        'security/security.xml',
        'views/user.xml',
        'views/sales_views.xml',
        'security/ir.model.access.csv',
    ]
}