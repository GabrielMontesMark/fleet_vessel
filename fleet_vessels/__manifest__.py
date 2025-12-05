# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Fleet Vessels',
    'version': '19.0.1.0.0',
    'sequence': 186,
    'category': 'Human Resources/Fleet',
    'summary': 'Manage vessels and maritime fleet',
    'description': """
Fleet Vessels Extension
=======================
This module extends the Fleet module to add support for vessels (ships, boats, yachts, etc.).

Main Features
-------------
* Add vessels as a new vehicle type
* Vessel-specific fields (length, beam, draft, tonnage, etc.)
* Maritime identification (IMO number, MMSI, call sign, flag)
* Vessel categories (yacht, cargo ship, fishing vessel, etc.)
* Hull material and engine type tracking
* Passenger and crew capacity management
    """,
    'depends': [
        'fleet',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/fleet_vessel_categories.xml',
        'views/fleet_vehicle_model_views.xml',
        'views/fleet_vehicle_views.xml',
    ],
    'demo': [
        'data/fleet_vessel_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
