# -*- coding: utf-8 -*-
{
    'name': "IFNA API SIMAT",

    'summary': """
        IFNA API SIMAT""",

    'description': """
        IFNA API SIMAT
    """,

    'author': "",
    'website': "",

    # for the full list
    'category': 'Services',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'employee_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_corn_data.xml',
        'views/res_partner_view.xml',
        'views/employee_contract_view.xml',
    ],
}
