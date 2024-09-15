# -*- coding: utf-8 -*-\
{
    'name': "Custom Payment Order",
    'summary': """Custom Payment Order""",
    'description': """Custom Payment Order""",
    'author': "City Art",
    'website': "",
    'category': 'Uncategorized',
    'version': '15.0.0.0',
    'depends': ['web', 'base', 'account','account_payment_order'],
    'qweb': [],
    'data': [
        "views/account_payment_order_view.xml",
        "report/account_payment_order_report.xml",
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'sequence': 5,
    'auto_install': False,
    'installable': True,
    'application': True,
}
