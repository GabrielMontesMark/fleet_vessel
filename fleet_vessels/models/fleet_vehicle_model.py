# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    # Extend vehicle_type selection to include 'vessel'
    vehicle_type = fields.Selection(
        selection_add=[('vessel', 'Vessel')],
        ondelete={'vessel': 'set default'}
    )

    # Vessel dimensions
    vessel_length = fields.Float(
        string='Length',
        help='Overall length of the vessel',
        tracking=True
    )
    vessel_beam = fields.Float(
        string='Beam',
        help='Width of the vessel at its widest point',
        tracking=True
    )
    vessel_draft = fields.Float(
        string='Draft',
        help='Vertical distance between the waterline and the bottom of the hull',
        tracking=True
    )
    vessel_tonnage = fields.Float(
        string='Tonnage',
        help='Gross tonnage or displacement tonnage',
        tracking=True
    )

    # Vessel classification
    vessel_type_detail = fields.Selection([
        ('cargo', 'Cargo Ship'),
        ('passenger', 'Passenger Ship'),
        ('fishing', 'Fishing Vessel'),
        ('yacht', 'Yacht'),
        ('tanker', 'Tanker'),
        ('container', 'Container Ship'),
        ('naval', 'Naval/Military'),
        ('tugboat', 'Tugboat'),
        ('ferry', 'Ferry'),
        ('research', 'Research Vessel'),
    ], string='Vessel Type', tracking=True)

    # Maritime identification
    vessel_flag = fields.Char(
        string='Flag State',
        help='Country of registration',
        tracking=True
    )
    vessel_imo_number = fields.Char(
        string='IMO Number',
        help='International Maritime Organization number - unique vessel identifier',
        tracking=True
    )
    vessel_mmsi = fields.Char(
        string='MMSI',
        help='Maritime Mobile Service Identity - 9-digit number for AIS',
        tracking=True
    )
    vessel_call_sign = fields.Char(
        string='Call Sign',
        help='Radio call sign',
        tracking=True
    )

    # Construction details
    hull_material = fields.Selection([
        ('steel', 'Steel'),
        ('aluminum', 'Aluminum'),
        ('fiberglass', 'Fiberglass'),
        ('wood', 'Wood'),
        ('composite', 'Composite'),
        ('concrete', 'Concrete'),
    ], string='Hull Material', tracking=True)

    engine_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('sail', 'Sail'),
        ('nuclear', 'Nuclear'),
    ], string='Propulsion Type', tracking=True)

    # Performance
    max_speed_knots = fields.Float(
        string='Max Speed (knots)',
        help='Maximum speed in nautical miles per hour',
        tracking=True
    )

    # Capacity
    passenger_capacity = fields.Integer(
        string='Passenger Capacity',
        help='Maximum number of passengers',
        tracking=True
    )
    crew_capacity = fields.Integer(
        string='Crew Capacity',
        help='Required or maximum crew members',
        tracking=True
    )

    # Units
    length_unit = fields.Selection([
        ('m', 'Meters'),
        ('ft', 'Feet'),
    ], string='Length Unit', default='m', tracking=True)

    tonnage_unit = fields.Selection([
        ('mt', 'Metric Tons'),
        ('lt', 'Long Tons'),
        ('st', 'Short Tons'),
        ('gt', 'Gross Tonnage'),
    ], string='Tonnage Unit', default='mt', tracking=True)
