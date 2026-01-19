# -*- coding: utf-8 -*-
{
    'name': 'Marine Registration',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Module to register users to external API',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/marine_registration_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
