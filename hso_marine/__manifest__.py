# -*- coding: utf-8 -*-
{
    'name': 'HSO Marine',
    'version': '1.0',
    'category': 'Operations/Marine',
    'summary': 'Manage Marine Vessels',
    'description': """
HSO Marine
==========
Stand-alone application to manage marine vessel data.
Includes an importer for the external marine_vessel table.
    """,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/marine_vessel_views.xml',
        'views/marine_importer_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
