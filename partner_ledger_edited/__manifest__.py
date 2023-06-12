# -*- coding: utf-8 -*-
{
    'name': 'Partner Ledger Edited',
    'version': '14.1.0',
    'sequence': 15,
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['account', 'web', 'base', 'sale_renting', 'renting', 'account_accountant', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_ledger_view_edited.xml',
        'wizard/partner_ledger_view_edited.xml',
        'data/account_financial_report_data.xml',
        'views/report_financial.xml',
    ],
    'demo': [],

    'assets': {
        'account_reports.assets_financial_report': [
            ('include', 'web._assets_helpers'),
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),
            'web/static/fonts/fonts.scss',

            'partner_ledger_edited/static/src/scss/account_financial_report.scss',
            'partner_ledger_edited/static/src/scss/account_report_print.scss',
        ],
        'web.assets_qweb': [
            'partner_ledger_edited/static/src/xml/**/*',
        ],

        'web.assets_backend': [
            'partner_ledger_edited/static/src/js/select2.full.min.js',
            'partner_ledger_edited/static/src/js/script.js',
            'partner_ledger_edited/static/src/scss/dynamic_common_style.scss',

            'partner_ledger_edited/static/src/js/mail_activity.js',
            'partner_ledger_edited/static/src/js/account_reports.js',
            'partner_ledger_edited/static/src/js/action_manager_account_report_dl.js',
            'partner_ledger_edited/static/src/scss/account_financial_report.scss',]

    },

    'license': 'OPL-1',
    'qweb': ['static/src/xml/view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
