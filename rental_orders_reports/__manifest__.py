{
    'name': 'Rental Orders Reports',
    'version': '1.0',
    'category': '',
    'sequence': 15,
    'author': '',
    'company': '',
    'license': 'LGPL-3',
    'website': '',
    'summary': '',
    'depends': ['base', 'report_xlsx', 'sale_renting','renting'],
    'data': [

        # 'security/contact.xml',
        'security/ir.model.access.csv',
        # 'views/social_insurance.xml',
        # 'views/employee_contract.xml',
        'views/excel_report.xml',
        'views/pdf_report.xml',

    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
