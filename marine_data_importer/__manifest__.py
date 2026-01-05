# -*- coding: utf-8 -*-
{
    'name': 'Marine Data Importer',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Import marine vessel data from external database',
    'description': """
Marine Data Importer
====================
 This module imports data from an external PostgreSQL database table 'marine_vessel' 
 into Odoo records (fleet.vehicle).
    """,
    'depends': ['base', 'fleet', 'fleet_vessels'],
    'data': [
        'security/ir.model.access.csv',
        'views/marine_importer_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
