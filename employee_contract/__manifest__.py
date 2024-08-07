# -*- coding: utf-8 -*-
{
    'name': "Contract",

    'summary': """
        Employee Contract Management""",

    'description': """
        Employee Contract Management
    """,

    'author': "",
    'website': "",

    # for the full list
    'category': 'Services',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/employee_contract_stage_data.xml',
        'views/employee_contract_stage_view.xml',
        'views/employee_contract_tag_view.xml',
        'views/employee_contract_view.xml',
    ],
}
