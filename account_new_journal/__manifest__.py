# -*- coding: utf-8 -*-
{
    'name': 'Journal Print ',
    'version': '14.1.0',
    'summary': "Journal Print",
    'sequence': 15,
    'category': 'Accounting/Accounting',
    "price": 150,
    'author': 'Pycus',
    'maintainer': 'Pycus Technologies',
    'website': '',
    'images': ['static/description/banner.gif'],
    'depends': ['account', 'web','base'],
    'data': [

        'views/views.xml',
        # 'views/journal_entry_report.xml',
    ],
    'demo': [],
    'license': 'OPL-1',
    'qweb': ['static/src/xml/view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
