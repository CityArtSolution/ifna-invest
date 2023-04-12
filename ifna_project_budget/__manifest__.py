# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Project Account Budget',
    'summary': 'Project account budget ',
    'author': "Samah Kandil,",
    'website': "samahqandeel22@gmail.com",
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_accountant',
        'hr_expense',
        'account_budget',
        'purchase',


    ],
    'data': [
        'views/budget.xml',
        # 'views/purchase.xml',
    ],
    'auto_install': False,
    'installable': True,
}
