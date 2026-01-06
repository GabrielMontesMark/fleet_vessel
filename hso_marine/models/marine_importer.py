# -*- coding: utf-8 -*-
import psycopg2
import logging
from odoo import models, fields, exceptions
import os

_logger = logging.getLogger(__name__)

import json

class MarineHSOImporter(models.TransientModel):
    _name = 'marine.hso.importer'
    _description = 'HSO Marine Importer Wizard'

    def action_import_data(self):
        db_host = os.environ.get("EXTERNAL_DB_HOST")
        db_name = os.environ.get("EXTERNAL_DB_NAME")
        db_user = os.environ.get("EXTERNAL_DB_USER")
        db_password = os.environ.get("EXTERNAL_DB_PASSWORD")
        
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            cursor = conn.cursor()
            
            # Select relevant columns - using ext_refs and removing limit
            query = "SELECT name, imo, mmsi, ext_refs, flag, length, width, type FROM marine_vessel"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            Vessel = self.env['marine.vessel']
            count_created = 0
            count_updated = 0

            for row in rows:
                v_name = row[0]
                v_imo = str(row[1]) if row[1] else False
                v_mmsi = str(row[2]) if row[2] else False
                
                # Handle ext_refs (row[3]) which might be dict or string
                raw_refs = row[3]
                v_json = {}
                if isinstance(raw_refs, dict):
                    v_json = raw_refs
                elif isinstance(raw_refs, str):
                    try:
                        v_json = json.loads(raw_refs)
                    except:
                        v_json = {}
                
                v_flag = row[4]
                v_length = row[5]
                v_width = row[6]
                v_type = row[7]

                v_call_sign = v_json.get('call_sign', '').strip() if isinstance(v_json, dict) else False
                v_draft = v_json.get('draught', 0.0) if isinstance(v_json, dict) else 0.0

                vals = {
                    'name': v_name or "Unknown",
                    'imo': v_imo,
                    'mmsi': v_mmsi,
                    'vessel_type': v_type,
                    'flag': v_flag,
                    'length': v_length,
                    'width': v_width,
                    'call_sign': v_call_sign,
                    'draft': v_draft,
                    'raw_json': str(v_json)
                }

                # Identification: MMSI or IMO
                domain = []
                if v_mmsi:
                    domain = [('mmsi', '=', v_mmsi)]
                elif v_imo:
                    domain = [('imo', '=', v_imo)]
                
                existing = False
                if domain:
                    existing = Vessel.search(domain, limit=1)
                
                if existing:
                    existing.write(vals)
                    count_updated += 1
                else:
                    Vessel.create(vals)
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
            raise exceptions.UserError(f"Import Error: {str(e)}")
