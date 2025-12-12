# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
import requests

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ArgusPriceWizard(models.TransientModel):
    _name = 'argus.price.wizard'
    _description = 'Importar Precios Argus (Wizard)'

    # Tu vista sólo usa estas dos fechas
    date_from = fields.Datetime(string='Fecha inicio', required=True,
                                default=lambda self: fields.Datetime.now() - timedelta(hours=24))
    date_to   = fields.Datetime(string='Fecha fin', required=True,
                                default=lambda self: fields.Datetime.now())

    # ---------------- Helpers locales (autónomos) ----------------
    @staticmethod
    def _base_url(endpoint: str) -> str:
        return (endpoint or '').strip().rstrip('/')

    @staticmethod
    def _cfg_get(config, *names, default=None):
        for n in names:
            if n in config._fields:
                val = getattr(config, n)
                if val:
                    return val
        return default

    @staticmethod
    def _parse_dt(s: str):
        try:
            if not s:
                return None
            s2 = s[:-1] if s.endswith('Z') else s
            fmt = "%Y-%m-%dT%H:%M:%S.%f" if '.' in s2 else "%Y-%m-%dT%H:%M:%S"
            return datetime.strptime(s2, fmt)
        except Exception:
            return None

    def _login_argus(self, endpoint, username, password):
        url = f"{self._base_url(endpoint)}/api/v1/login"
        r = requests.get(url, params={
            'username': username,
            'password': password,
            'application': 'Odoo-Argus',
        }, timeout=60)
        r.raise_for_status()
        return (r.json() or {}).get('AuthToken')

    def _ensure_token(self, config):
        token = self._cfg_get(config, 'token', 'auth_token')
        if token:
            return token
        endpoint = self._cfg_get(config, 'endpoint', 'base_url')
        username = self._cfg_get(config, 'username', 'usuario')
        password = self._cfg_get(config, 'password', 'clave')
        if not (endpoint and username and password):
            raise ValueError("Faltan endpoint/credenciales en api.config")
        token = self._login_argus(endpoint, username, password)
        if token:
            # guarda en el primer campo disponible
            for field in ('token', 'auth_token'):
                if field in config._fields:
                    config.sudo().write({field: token})
                    break
        return token

    # ---- Resolución local de unidades CORREGIDA ----
    def _find_unit(self, raw_value, is_currency=False):
        """Busca unidad por unit_id (CORREGIDO - solo por unit_id ya que external_id no existe)"""
        Unit = self.env['argus.unit'].sudo()
        
        if raw_value is None:
            return Unit.browse()
        
        try:
            unit_id = int(raw_value)
        except (ValueError, TypeError):
            return Unit.browse()
        
        # CORRECCIÓN: Buscar solo por unit_id ya que external_id no existe en el modelo
        unit = Unit.search([
            ('unit_id', '=', unit_id)
        ], limit=1)
        
        return unit

    # ---------------- Acción llamada por tu vista ----------------
    def action_consultar_precios(self):
        """Importa precios entre fechas del wizard (MANTENIENDO endpoint /updated por compatibilidad)."""
        self.ensure_one()
        Price = self.env['argus.price'].sudo()
        Config = self.env['api.config'].sudo()

        # Config básica
        config = Config.search([('name', '=', 'argus')], limit=1)
        if not config:
            raise ValueError("Config 'api.config' con name='argus' no encontrada.")

        endpoint = self._cfg_get(config, 'endpoint', 'base_url')
        if not endpoint:
            raise ValueError("Endpoint no configurado en api.config (endpoint/base_url).")

        token = self._ensure_token(config)
        if not token:
            raise ValueError("No fue posible obtener AuthToken de Argus.")

        # ✅✅✅ COMENTARIO: VOLVEMOS AL ENDPOINT /updated QUE SABEMOS QUE FUNCIONA
        # El endpoint /selected requiere parámetros diferentes y está dando error 400
        # Mantenemos /updated por ahora y mejoramos la agrupación
        url = f"{self._base_url(endpoint)}/api/v1/price/updated"
        params = {
            'authToken': token,
            'startDate': self.date_from.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'endDate': self.date_to.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'startId': 0,
        }

        total = 0
        precios_ignorados = 0
        
        # Diccionario temporal para agrupar por clave única 
        # ✅✅✅ COMENTARIO: Agrupamos por CodeId + PublicationDate + ForwardPeriod + ForwardYear
        precios_agrupados = {}

        def _do_get(_params):
            return requests.get(url, params=_params, timeout=180)

        while True:
            try:
                resp = _do_get(params)
                if resp.status_code == 401:
                    # relogin
                    username = self._cfg_get(config, 'username', 'usuario')
                    password = self._cfg_get(config, 'password', 'clave')
                    new_token = self._login_argus(endpoint, username, password)
                    if not new_token:
                        raise ValueError("No fue posible renovar AuthToken para Argus.")
                    for field in ('token', 'auth_token'):
                        if field in config._fields:
                            config.sudo().write({field: new_token})
                            break
                    params['authToken'] = new_token
                    resp = _do_get(params)

                resp.raise_for_status()
                payload = resp.json() or {}
                prices = payload.get('Prices', []) or []

                if not prices:
                    break

                for p in prices:
                    # ✅✅✅ ACEPTAR LOS 3 TIPOS DE PRECIO PRINCIPALES
                    pricetype_id = p.get('PricetypeId')
                    allowed_pricetypes = [1, 2, 8]  # Mínimo, Máximo, Medio
                    
                    if pricetype_id not in allowed_pricetypes:
                        _logger.debug("[ARGUS][WIZ] Ignorando precio con PricetypeId=%s para %s", 
                                    pricetype_id, p.get('CodeId'))
                        precios_ignorados += 1
                        continue
                    
                    price_value = p.get('Value')
                    
                    if price_value is None:
                        _logger.warning("[ARGUS][WIZ] Precio nulo para %s, ignorando", p.get('CodeId'))
                        continue
                    
                    # ✅✅✅ COMENTARIO: Clave única incluye ForwardPeriod y ForwardYear
                    code_id = p.get('CodeId')
                    pub_date = p.get('PublicationDate')
                    forward_period = p.get('ForwardPeriod', 0)
                    forward_year = p.get('ForwardYear', 0)
                    clave = f"{code_id}_{pub_date}_{forward_period}_{forward_year}"
                    
                    _logger.info("[ARGUS][WIZ] Precio %s para %s (Contrato %s-%s): %s (PricetypeId=%s)", 
                               "MÍNIMO" if pricetype_id == 1 else "MÁXIMO" if pricetype_id == 2 else "MEDIO",
                               code_id, forward_period, forward_year, price_value, pricetype_id)

                    # Agrupar por clave
                    if clave not in precios_agrupados:
                        u1 = p.get('UnitId1')
                        u2 = p.get('UnitId2')
                        unit1 = self._find_unit(u1)
                        unit2 = self._find_unit(u2)
                        
                        precios_agrupados[clave] = {
                            'repository_id': p.get('RepositoryId'),
                            'correction_id': p.get('CorrectionId'),
                            'quote_id': p.get('QuoteId'),
                            'code_id': code_id,
                            'timestamp_id': p.get('TimestampId'),
                            'continuous_forward': p.get('ContinuousForward'),
                            'publication_date': self._parse_dt(pub_date),
                            'fmt_date': p.get('FmtDate'),
                            'value': None,           # Mínimo (1)
                            'value_close': None,     # MÁXIMO (2)
                            'value_mid': None,       # Medio (8)
                            'value_open': None,      # Apertura (1 - mismo que mínimo)
                            'forward_period': forward_period,
                            'forward_year': forward_year,
                            'diff_base_roll': p.get('DiffBaseRoll'),
                            'pricetype_id': pricetype_id,
                            'decimal_places': p.get('DecimalPlaces'),
                            'unit_id1': u1,
                            'unit_id2': u2,
                            'diff_base_value': p.get('DiffBaseValue'),
                            'diff_base_timing_id': p.get('DiffBaseTimingId'),
                            'date_modified': self._parse_dt(p.get('DateModified')),
                            'correction': p.get('Correction'),
                            'error_id': p.get('ErrorId'),
                            'tag': p.get('Tag'),
                            'currency_unit_id': unit1.id or False,
                            'measure_unit_id': unit2.id or False,
                            'imported_at': fields.Datetime.now(),
                            'import_source': 'manual',
                        }
                    
                    # ✅✅✅ COMENTARIO: Asignación CORREGIDA según Argus
                    if pricetype_id == 1:  # Mínimo/Apertura
                        precios_agrupados[clave]['value'] = price_value
                        precios_agrupados[clave]['value_open'] = price_value
                    elif pricetype_id == 2:  # MÁXIMO
                        precios_agrupados[clave]['value_close'] = price_value
                    elif pricetype_id == 8:  # Medio
                        precios_agrupados[clave]['value_mid'] = price_value

            except Exception as e:
                _logger.error("[ARGUS][WIZ] Error en la API: %s", e)
                break

            # Verificar si hay más páginas
            if (payload.get('Amount') or 0) <= (payload.get('Limit') or 0):
                break
            params['startId'] = prices[-1].get('RepositoryId')

        # Procesar los precios agrupados
        for clave, vals in precios_agrupados.items():
            # Solo crear/actualizar si tenemos al menos un precio
            if vals['value'] is not None or vals['value_close'] is not None or vals['value_mid'] is not None:
                
                # ✅✅✅ COMENTARIO: Buscamos por clave compuesta para evitar duplicados
                existing = Price.search([
                    ('code_id', '=', vals['code_id']),
                    ('publication_date', '=', vals['publication_date']),
                    ('forward_period', '=', vals['forward_period']),
                    ('forward_year', '=', vals['forward_year'])
                ], limit=1)
                
                if existing:
                    existing.write(vals)
                    _logger.debug("[ARGUS][WIZ] Actualizado registro existente: %s", clave)
                else:
                    Price.create(vals)
                    _logger.debug("[ARGUS][WIZ] Creado nuevo registro: %s", clave)
                total += 1

        _logger.info("[ARGUS][WIZ] Import finalizado. Registros procesados=%s, Ignorados=%s", total, precios_ignorados)
        return {'type': 'ir.actions.act_window_close'}
