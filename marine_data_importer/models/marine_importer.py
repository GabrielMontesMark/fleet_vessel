# -*- coding: utf-8 -*-
import psycopg2
import logging
from odoo import models, fields, api, exceptions

_logger = logging.getLogger(__name__)

class MarineDataImporter(models.TransientModel):
    _name = 'marine.data.importer'
    _description = 'Marine Data Importer Wizard'

    def action_import_data(self):
        # Database connection parameters
        db_host = "host.docker.internal" 
        db_name = "hso_marine_test"
        db_user = "postgres"
        db_password = "postgres"
        
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            cursor = conn.cursor()
            
            # Query to fetch data
            # Updated to match user schema: id, mmsi, imo, name, type, flag, ext_refs, updated_at, ext_refs_jsonb, length, width
            query = "SELECT name, imo, mmsi, ext_refs_jsonb, flag, length, width, type FROM marine_vessel LIMIT 50"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            Vehicle = self.env['fleet.vehicle']
            Model = self.env['fleet.vehicle.model']
            
            # Ensure a default model exists for imported vessels
            brand = self.env['fleet.vehicle.model.brand'].search([('name', '=', 'Generic Marine')], limit=1)
            if not brand:
                brand = self.env['fleet.vehicle.model.brand'].create({'name': 'Generic Marine'})
                
            default_model = Model.search([('name', '=', 'Imported Vessel'), ('brand_id', '=', brand.id)], limit=1)
            if not default_model:
                default_model = Model.create({
                    'name': 'Imported Vessel',
                    'brand_id': brand.id,
                    'vehicle_type': 'car', # Odoo default
                })

            count_created = 0
            count_updated = 0

            for row in rows:
                # Mapping columns by index
                # 0: name, 1: imo, 2: mmsi, 3: ext_refs_jsonb, 4: flag, 5: length, 6: width, 7: type
                
                v_name = row[0]
                v_imo = str(row[1]) if row[1] else False
                v_mmsi = str(row[2]) if row[2] else False
                v_json = row[3] or {} # psycopg2 converts jsonb to dict automatically
                v_flag = row[4]
                v_length = row[5]
                v_beam = row[6] # 'width' in DB -> 'beam' in Odoo
                v_type = row[7]

                # Extract from JSON
                v_call_sign = v_json.get('call_sign', '').strip() if isinstance(v_json, dict) else False
                v_draft = v_json.get('draught', 0.0) if isinstance(v_json, dict) else 0.0

                vals = {
                    'vessel_imo_number': v_imo,
                    'vessel_mmsi': v_mmsi,
                    'vessel_call_sign': v_call_sign,
                    'vessel_flag': v_flag,
                    'vessel_length': v_length,
                    'vessel_beam': v_beam,
                    'vessel_draft': v_draft,
                    'model_id': default_model.id,
                }

                # Identification logic: try MMSI first, then IMO
                domain = []
                if v_mmsi:
                    domain = [('vessel_mmsi', '=', v_mmsi)]
                elif v_imo:
                    domain = [('vessel_imo_number', '=', v_imo)]
                
                existing = False
                if domain:
                    existing = Vehicle.search(domain, limit=1)
                
                if existing:
                    existing.write(vals)
                    count_updated += 1
                else:
                    # New record
                    vals['name'] = v_name or f"Vessel {v_mmsi or v_imo}"
                    # license_plate is required
                    vals['license_plate'] = v_call_sign or v_name or "Unknown"
                    Vehicle.create(vals)
                    count_created += 1
            
            message = f"Import finished. Created: {count_created}, Updated: {count_updated}"
            _logger.info(message)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error("Failed to import marine data: %s", str(e))
            raise exceptions.UserError(f"Connection or Import Error: {str(e)}")
