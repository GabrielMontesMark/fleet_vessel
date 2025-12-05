# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Vessel dimensions
    vessel_length = fields.Float(
        string='Length',
        compute='_compute_vessel_length',
        store=True,
        readonly=False,
        tracking=True
    )
    vessel_beam = fields.Float(
        string='Beam',
        compute='_compute_vessel_beam',
        store=True,
        readonly=False,
        tracking=True
    )
    vessel_draft = fields.Float(
        string='Draft',
        compute='_compute_vessel_draft',
        store=True,
        readonly=False,
        tracking=True
    )
    vessel_tonnage = fields.Float(
        string='Tonnage',
        compute='_compute_vessel_tonnage',
        store=True,
        readonly=False,
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
    ], string='Vessel Type',
        compute='_compute_vessel_type_detail',
        store=True,
        readonly=False,
        tracking=True
    )

    # Maritime identification
    vessel_flag = fields.Char(
        string='Flag State',
        compute='_compute_vessel_flag',
        store=True,
        readonly=False,
        tracking=True
    )
    vessel_imo_number = fields.Char(
        string='IMO Number',
        tracking=True
    )
    vessel_mmsi = fields.Char(
        string='MMSI',
        tracking=True
    )
    vessel_call_sign = fields.Char(
        string='Call Sign',
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
    ], string='Hull Material',
        compute='_compute_hull_material',
        store=True,
        readonly=False,
        tracking=True
    )

    engine_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('sail', 'Sail'),
        ('nuclear', 'Nuclear'),
    ], string='Propulsion Type',
        compute='_compute_engine_type',
        store=True,
        readonly=False,
        tracking=True
    )

    # Performance
    max_speed_knots = fields.Float(
        string='Max Speed (knots)',
        compute='_compute_max_speed_knots',
        store=True,
        readonly=False,
        tracking=True
    )

    # Capacity
    passenger_capacity = fields.Integer(
        string='Passenger Capacity',
        compute='_compute_passenger_capacity',
        store=True,
        readonly=False,
        tracking=True
    )
    crew_capacity = fields.Integer(
        string='Crew Capacity',
        compute='_compute_crew_capacity',
        store=True,
        readonly=False,
        tracking=True
    )

    # Units
    length_unit = fields.Selection([
        ('m', 'Meters'),
        ('ft', 'Feet'),
    ], string='Length Unit',
        compute='_compute_length_unit',
        store=True,
        readonly=False,
        default='m',
        tracking=True
    )

    tonnage_unit = fields.Selection([
        ('mt', 'Metric Tons'),
        ('lt', 'Long Tons'),
        ('st', 'Short Tons'),
        ('gt', 'Gross Tonnage'),
    ], string='Tonnage Unit',
        compute='_compute_tonnage_unit',
        store=True,
        readonly=False,
        default='mt',
        tracking=True
    )

    # Compute methods to inherit from model
    @api.depends('model_id.vessel_length')
    def _compute_vessel_length(self):
        for vehicle in self:
            vehicle.vessel_length = vehicle.model_id.vessel_length

    @api.depends('model_id.vessel_beam')
    def _compute_vessel_beam(self):
        for vehicle in self:
            vehicle.vessel_beam = vehicle.model_id.vessel_beam

    @api.depends('model_id.vessel_draft')
    def _compute_vessel_draft(self):
        for vehicle in self:
            vehicle.vessel_draft = vehicle.model_id.vessel_draft

    @api.depends('model_id.vessel_tonnage')
    def _compute_vessel_tonnage(self):
        for vehicle in self:
            vehicle.vessel_tonnage = vehicle.model_id.vessel_tonnage

    @api.depends('model_id.vessel_type_detail')
    def _compute_vessel_type_detail(self):
        for vehicle in self:
            vehicle.vessel_type_detail = vehicle.model_id.vessel_type_detail

    @api.depends('model_id.vessel_flag')
    def _compute_vessel_flag(self):
        for vehicle in self:
            vehicle.vessel_flag = vehicle.model_id.vessel_flag

    @api.depends('model_id.hull_material')
    def _compute_hull_material(self):
        for vehicle in self:
            vehicle.hull_material = vehicle.model_id.hull_material

    @api.depends('model_id.engine_type')
    def _compute_engine_type(self):
        for vehicle in self:
            vehicle.engine_type = vehicle.model_id.engine_type

    @api.depends('model_id.max_speed_knots')
    def _compute_max_speed_knots(self):
        for vehicle in self:
            vehicle.max_speed_knots = vehicle.model_id.max_speed_knots

    @api.depends('model_id.passenger_capacity')
    def _compute_passenger_capacity(self):
        for vehicle in self:
            vehicle.passenger_capacity = vehicle.model_id.passenger_capacity

    @api.depends('model_id.crew_capacity')
    def _compute_crew_capacity(self):
        for vehicle in self:
            vehicle.crew_capacity = vehicle.model_id.crew_capacity

    @api.depends('model_id.length_unit')
    def _compute_length_unit(self):
        for vehicle in self:
            vehicle.length_unit = vehicle.model_id.length_unit

    @api.depends('model_id.tonnage_unit')
    def _compute_tonnage_unit(self):
        for vehicle in self:
            vehicle.tonnage_unit = vehicle.model_id.tonnage_unit
