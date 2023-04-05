# -*- coding: utf-8 -*-
{
    'name': "Update Tenants Report",
    'depends': ['base','mail','report_xlsx', 'account', 'sale', 'sale_renting','renting'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/activity_report.xml',
    ],
}
