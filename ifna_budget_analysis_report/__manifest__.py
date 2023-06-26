# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Budget Report Analysis',
    'summary': 'budget Report Analysis ',
    'author': "Samah Kandil,",
    'website': "samahqandeel22@gmail.com",
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_accountant',
        'account_budget',
        'ifna_project_budget',


    ],
    'data': [
        'views/budget.xml',
        # 'views/purchase.xml',
    ],
    'auto_install': False,
    'installable': True,
}
