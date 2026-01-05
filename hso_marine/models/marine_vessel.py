# -*- coding: utf-8 -*-
from odoo import models, fields

class MarineVessel(models.Model):
    _name = 'marine.vessel'
    _description = 'Marine Vessel'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, index=True)
    mmsi = fields.Char(string='MMSI', index=True)
    imo = fields.Char(string='IMO Number', index=True)
    vessel_type = fields.Char(string='Type')
    flag = fields.Char(string='Flag')
    length = fields.Float(string='Length')
    width = fields.Float(string='Width')
    call_sign = fields.Char(string='Call Sign')
    draft = fields.Float(string='Draft')
    raw_json = fields.Text(string='Raw Data (JSON)')
