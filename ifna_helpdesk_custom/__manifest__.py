# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'HelpDesk Customization',
    'summary': 'HelpDesk Customization  ',
    'author': "Samah Kandil,",
    'website': "samahqandeel22@gmail.com",
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base','helpdesk','helpdesk_stock', 'renting'
    ],
    'data': [
        'views/views.xml',
    ],
    'auto_install': False,
    'installable': True,
}
