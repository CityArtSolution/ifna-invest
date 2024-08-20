# -*- coding: utf-8 -*-
{
    'name': "Legal Affairs Management",

    'summary': """
        Legal Affairs Management""",

    'description': """
        Legal Affairs Management
    """,

    'author': "",
    'website': "",

    'category': 'Uncategorized',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
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
        'views/legal_authorization_agency_view.xml',
        'views/legal_board_decision_view.xml',
        'views/legal_company_document_view.xml',
        'views/legal_authorization_agency_view.xml',
        'views/legal_board_decision_view.xml',
        'views/legal_conf_authorization_type_view.xml',
        'views/legal_conf_case_type_view.xml',
        'views/legal_conf_consultation_type.xml',
        'views/legal_conf_court_view.xml',
        'views/legal_account_move_view.xml',
        'views/legal_dashboard_view.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'assets': {
        'web.assets_backend': [
            'legal_affairs_management/static/src/css/lib/nv.d3.css',
            'legal_affairs_management/static/src/css/dashboard.css',
            "legal_affairs_management/static/src/js/dashboard.js",
            'legal_affairs_management/static/src/js/lib/d3.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
            'legal_affairs_management/static/src/css/dataTables.bootstrap5.css',
            'legal_affairs_management/static/src/css/responsive.bootstrap.min.css',
            'legal_affairs_management/static/src/css/buttons.dataTables.min.css',
            'legal_affairs_management/static/src/js/jquery.dataTables.min.js',
            'legal_affairs_management/static/src/js/dataTables.responsive.min.js',
            'legal_affairs_management/static/src/js/custom.js',
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
