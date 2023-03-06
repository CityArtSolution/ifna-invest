# -*- coding: utf-8 -*-

{
    'name': 'Custom Invoice Report',
    'version': '15.0.0.0',
    'category': 'Tools',
    'author': 'City Art',
    'depends': ['web', 'base', 'account','l10n_sa_invoice','l10n_gcc_invoice'],
    'data': [
        "views/res_partner_bank.xml",
        "views/report_invoice.xml",
        "views/invoice.xml",

    ],

    'demo': [],
    'test': [],
}
