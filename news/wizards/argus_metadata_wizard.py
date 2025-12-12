from odoo import models, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class ArgusMetadataWizard(models.TransientModel):
    _name = 'argus.metadata.wizard'
    _description = 'Asistente para consultar metadatos de Argus'

    def action_consultar_metadatos(self):
        config = self.env['api.config'].search([('name', '=', 'argus')], limit=1)
        if not config:
            raise UserError("No se encontró configuración API para 'argus'")

        url = f"{config.endpoint}/price/metadata?authToken={config.token}"
        _logger.info("Consultando metadatos desde: %s", url)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            result = response.json()
            data = result.get("data", [])
            
            # Pre-cargar códigos existentes (convertidos a enteros)
            existing_codes = set(
                str(int(float(code))) if '.' in code else code 
                for code in self.env['argus.metadata.code'].search([]).mapped('code_id')
            )
            
            count = 0
            for item in data:
                raw_code = item.get("V_CODE", "")
                if not raw_code:
                    continue
                
                # Normalizar a entero (eliminar decimales)
                try:
                    # Primero intentar convertir a float y luego a int
                    code_val = str(int(float(raw_code)))
                except (ValueError, TypeError):
                    # Si falla, usar el valor original limpio
                    code_val = str(raw_code).strip()
                
                # Verificar si ya existe (en formato entero)
                if code_val in existing_codes:
                    continue
                
                # Crear nuevo registro
                self.env['argus.metadata.code'].create({
                    'code_id': code_val,
                    'description': (item.get("V_DESCRIPTION") or "").strip(),
                    'category': (item.get("V_CATEGORY") or "").strip(),
                    'delivery_mode': (item.get("V_DEL_MODE") or "").strip(),
                    'unit': (item.get("V_UNIT") or "").strip(),
                    'region': (item.get("V_REGION_NAME") or "").strip(),
                    'quote': (item.get("V_QUOTE") or "").strip(),
                    'pricetype': (item.get("V_PRICETYPE") or "").strip(),
                    'diffbase': (item.get("V_DIFFBASE") or "").strip(),
                })
                count += 1
                existing_codes.add(code_val)  # Actualizar cache

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Metadatos actualizados'),
                    'message': _(f'{count} nuevos metadatos importados'),
                    'type': 'success',
                    'sticky': True,
                }
            }

        except Exception as e:
            error_msg = f"Error al consultar metadatos: {str(e)}"
            _logger.error(error_msg, exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _(error_msg),
                    'type': 'danger',
                    'sticky': True,
                }
            }
