# -*- coding: utf-8 -*-
{
    'name': "Legal Affairs Management",

    'summary': """
        CityArt Legal Affairs Management""",

    'description': """
        CityArt Legal Affairs Management
    """,

    'author': "",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'mail', 'contacts', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'data/legal_ir_cron_data.xml',
        'data/product_product_data.xml',
        'views/legal_menus.xml',
        'views/external_legal_consultation_view.xml',
        'views/legal_case_view.xml',
        'views/legal_contract_view.xml',
        'views/legal_execution_request_view.xml',
        'views/legal_letter_view.xml',
        'views/legal_res_partner_view.xml',
        'views/legal_res_partner_defendant_view.xml',
        'views/legal_res_partner_lawyer_view.xml',
        'views/legal_res_partner_judge_view.xml',
        'views/legal_res_partner_authorized_view.xml',
        'views/legal_trial_view.xml',
        'views/legal_board_decision_view.xml',
        'views/legal_company_document_view.xml',
        'views/legal_authorization_agency_view.xml',
        'views/legal_conf_authorization_type_view.xml',
        'views/legal_conf_case_type_view.xml',
        'views/legal_conf_consultation_type.xml',
        'views/legal_conf_court_view.xml',
        'views/legal_conf_court_level_view.xml',
        'views/legal_account_move_view.xml',
        'views/legal_dashboard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'legal_affairs_management/static/src/js/dashboard.js',
        ],
        'web.assets_qweb': [
            'legal_affairs_management/static/src/xml/dashboard.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 5,
}
