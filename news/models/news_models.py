from odoo import models, fields, api
import requests
import logging
from datetime import datetime, timedelta
import json

_logger = logging.getLogger(__name__)


class ApiNews(models.Model):
    _name = 'api.news'
    _description = 'Noticias desde Argus'
    _order = 'publication_date desc, id desc'

    news_id = fields.Char(string='News ID', index=True)
    headline = fields.Char(string='Titular')
    publication_date = fields.Datetime(string='Fecha de publicación')
    date_modified = fields.Datetime(string='Última modificación')
    language_id = fields.Integer(string='Language ID')
    news_type_id = fields.Integer(string='News Type ID')
    free = fields.Boolean(string='Es pública')
    featured = fields.Boolean(string='Destacada')
    text_html = fields.Html(string='Contenido HTML')
    region_ids = fields.Char(string='IDs de región')
    sector_ids = fields.Char(string='IDs de sector')
    context_ids = fields.Char(string='IDs de contexto')
    stream_ids = fields.Char(string='IDs de stream')

    # ------------------------- Utilidades -------------------------
    @staticmethod
    def _strip_z(dt: str) -> str:
        if not dt:
            return dt
        return dt[:-1] if dt.endswith('Z') else dt

    @staticmethod
    def parse_iso_datetime(iso_str):
        """Convierte fecha ISO (con o sin 'Z') a datetime.
        Ejemplos de la API: "2024-08-13T20:03:07" o "2024-05-28T01:31:27Z".
        """
        try:
            s = ApiNews._strip_z(iso_str)
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S") if s else None
        except Exception:
            return None

    @staticmethod
    def _base_url(endpoint: str) -> str:
        return (endpoint or '').strip().rstrip('/')

    # ------------------------- Autenticación -------------------------
    @api.model
    def get_auth_token(self):
        """Obtiene/renueva token y lo guarda en api.config.token.
        Acepta variantes de clave de respuesta.
        """
        config = self.env['api.config'].sudo().search([('name', '=', 'argus')], limit=1)
        if not config:
            _logger.error("[ARGUS] No se encontró configuración válida para Argus")
            return None

        url = f"{self._base_url(config.endpoint)}/api/v1/login"
        params = {
            'username': config.user,             # corregido (antes: config.usuario)
            'password': config.password,
            'application': 'OdooNewsIntegration'
        }
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json() or {}
            token = data.get('AuthToken') or data.get('authToken') or data.get('token') or data.get('access_token')
            if token:
                config.sudo().write({'token': token})
                _logger.info('[ARGUS] Token actualizado con éxito')
                return token
            _logger.warning('[ARGUS] Token no recibido desde Argus: %s', json.dumps(data)[:300])
            return None
        except Exception as e:
            _logger.error("[ARGUS] Error al obtener token: %s", e)
            return None

    # ------------------------- Importador (CRON 4h) -------------------------
    @api.model
    def importar_noticias_argus_diarias(self):
        _logger.info('>>> [ARGUS] Import News (cron 4h) iniciando…')

        config = self.env['api.config'].sudo().search([('name', '=', 'argus')], limit=1)
        if not config:
            _logger.error("[ARGUS] No se encontró configuración válida para Argus")
            return

        token = config.token or self.sudo().get_auth_token()
        if not token:
            _logger.error("[ARGUS] Token de autenticación no disponible")
            return

        # Ventana: últimas 4 horas con 2 min de buffer para evitar carreras
        end_dt = datetime.utcnow() - timedelta(minutes=2)
        start_dt = end_dt - timedelta(hours=4)

        ids_url = f"{self._base_url(config.endpoint)}/api/v1/news/updated"
        ids_params = {
            'authToken': token,
            'startDate': start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'endDate': end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        try:
            r = requests.get(ids_url, params=ids_params, timeout=90)
            r.raise_for_status()
            noticias = (r.json() or {}).get('News', [])
        except Exception as e:
            _logger.error("[ARGUS] Error al obtener IDs de noticias: %s", e)
            return

        created, updated = 0, 0
        for noticia in noticias:
            news_id = noticia.get('NewsId')
            if not news_id:
                continue

            detalle_url = f"{self._base_url(config.endpoint)}/api/v1/news/{news_id}"
            detalle_params = {'authToken': token}

            try:
                resp = requests.get(detalle_url, params=detalle_params, timeout=90)
                if resp.status_code == 401:
                    token = self.sudo().get_auth_token() or token
                    resp = requests.get(detalle_url, params={'authToken': token}, timeout=90)
                resp.raise_for_status()
                detalle = resp.json() or {}
            except Exception as e:
                _logger.error("[ARGUS] Error al obtener detalle de noticia %s: %s", news_id, e)
                continue

            valores = {
                'news_id': detalle.get('NewsId'),
                'headline': detalle.get('Headline'),
                'publication_date': self.parse_iso_datetime(detalle.get('PublicationDate')),
                'date_modified': self.parse_iso_datetime(detalle.get('DateModified')),
                'free': detalle.get('Free'),
                'featured': detalle.get('Featured'),
                'language_id': detalle.get('LanguageId'),
                'news_type_id': detalle.get('NewsTypeId'),
                'text_html': detalle.get('Text'),
                'region_ids': json.dumps(detalle.get('RegionIds', []), ensure_ascii=False),
                'sector_ids': json.dumps(detalle.get('SectorIds', []), ensure_ascii=False),
                'context_ids': json.dumps(detalle.get('ContextIds', []), ensure_ascii=False),
                'stream_ids': json.dumps(detalle.get('StreamIds', []), ensure_ascii=False),
            }

            existente = self.search([('news_id', '=', news_id)], limit=1)
            if existente:
                existente.write(valores)
                updated += 1
            else:
                self.create(valores)
                created += 1

        _logger.info('[ARGUS] Import News finalizado. Creadas=%s, Actualizadas=%s', created, updated)

    # Botón manual (por si lo llamas desde la vista)
    def action_importar_noticias(self):
        self.env['api.news'].importar_noticias_argus_diarias()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Argus News',
                'message': 'Se ejecutó la importación. Revisa el listado.',
                'type': 'success',
                'sticky': False,
            }
        }
