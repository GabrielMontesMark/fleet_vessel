# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ApiConfig(models.Model):
    _name = "api.config"
    _description = "API Connections"

    name = fields.Char(string="Nombre", required=True, default="argus")
    user = fields.Char(string="Usuario")
    password = fields.Char(string="Contraseña")
    endpoint = fields.Char(
        string="Endpoint",
        help=(
            "URL base o endpoint de login.\n"
            "Ejemplos válidos:\n"
            " - https://www.argusmedia.com/ArgusWSVSTO\n"
            " - https://www.argusmedia.com/ArgusWSVSTO/api/v1/login"
        ),
    )
    token = fields.Char(string="Token", readonly=True, copy=False)
    last_tested = fields.Datetime(string="Última Prueba", readonly=True)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _normalize_base(base_url: str) -> str:
        """
        Normaliza el dominio/base, quita trailing slash y asegura el root de Argus WebAPI2.
        Según doc, el servicio vive bajo /ArgusWSVSTO.
        """
        if not base_url:
            return ""
        base = base_url.strip().rstrip("/")

        # Si el usuario pegó el dominio sin root, agrégalo.
        if base in ("https://www.argusmedia.com", "http://www.argusmedia.com"):
            return base + "/ArgusWSVSTO"

        # Si ya trae /ArgusWSVSTO (con o sin rutas), recortar hasta el root.
        if "/ArgusWSVSTO" in base:
            return base.split("/ArgusWSVSTO", 1)[0].rstrip("/") + "/ArgusWSVSTO"

        return base

    @staticmethod
    def _login_candidates(base: str):
        """
        Candidatos oficiales de WebAPI2 (doc v1.02):
        - GET  /api/v1/login
        - POST /api/v1/price/login
        """
        base = base.rstrip("/")
        return [
            f"{base}/api/v1/price/login",  # POST (preferido)
            f"{base}/api/v1/login",        # GET  (fallback)
        ]

    def _fetch_token_variant(self, url: str, username: str, password: str, timeout=30):
        """
        Ejecuta la variante correcta según el endpoint:
        - Si termina en /api/v1/price/login => POST JSON con claves TitleCase (Username/Password/Application)
        - Si termina en /api/v1/login      => GET con querystring en minúsculas (username/password/application)
        Devuelve token o lanza UserError con diagnóstico claro.
        """
        ua = "Odoo-ArgusConnector/1.0"
        common_headers = {
            "User-Agent": ua,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
        }

        # Variante POST JSON (oficial WebAPI2)
        if url.endswith("/api/v1/price/login"):
            json_payload = {
                "Username": username,
                "Password": password,
                "Application": "Odoo-Loader",
            }
            safe_json = {**json_payload, "Password": "***"}
            _logger.info(">>> [POST JSON WebAPI2] %s payload=%s", url, safe_json)
            resp = requests.post(
                url,
                json=json_payload,
                headers={**common_headers, "Content-Type": "application/json"},
                timeout=timeout,
                allow_redirects=False,
            )
            token = self._parse_token_response(url, resp, phase="POST-JSON")
            if token is not None:
                return token

        # Variante GET (oficial WebAPI2)
        if url.endswith("/api/v1/login"):
            params = {
                "username": username,
                "password": password,
                "application": "Odoo-Loader",
            }
            safe_params = {**params, "password": "***"}
            _logger.info(">>> [GET WebAPI2] %s params=%s", url, safe_params)
            resp = requests.get(
                url,
                params=params,
                headers=common_headers,
                timeout=timeout,
                allow_redirects=False,
            )
            token = self._parse_token_response(url, resp, phase="GET")
            if token is not None:
                return token

        # Si llegó aquí, el endpoint no devolvió JSON válido con token
        self._raise_non_json_error(resp, url, phase="LOGIN")

    def _parse_token_response(self, url, resp, phase=""):
        """
        Interpreta la respuesta:
        - Redirección => error explícito (flujo web/logueo interactivo).
        - HTTP error => UserError con preview.
        - No-JSON => devuelve None (para que otra variante pruebe)
        - JSON => busca AuthToken/token/access_token
        """
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("Location")
            preview = (resp.text or "")[:200].replace("\n", " ")
            raise UserError(
                _("[%s] Redirección HTTP %s -> %s (flujo web). "
                  "Verifica credenciales y que usas el API de Argus WebAPI2. Respuesta: %s")
                % (phase, resp.status_code, loc or "-", preview)
            )

        if resp.status_code >= 400:
            try:
                resp.raise_for_status()
            except Exception as e:
                preview = (resp.text or "")[:200].replace("\n", " ")
                raise UserError(
                    _("[%s] Error HTTP %s al solicitar token. Respuesta (inicio): %s")
                    % (phase, resp.status_code, preview)
                ) from e

        ctype = (resp.headers.get("Content-Type") or "").lower()
        if "application/json" not in ctype:
            _logger.warning("[%s] Respuesta no-JSON (%s) desde %s", phase, ctype or "desconocido", url)
            return None

        try:
            data = resp.json() or {}
        except Exception:
            preview = (resp.text or "")[:200].replace("\n", " ")
            raise UserError(
                _("[%s] No se pudo parsear JSON. Respuesta (inicio): %s")
                % (phase, preview)
            )

        token = data.get("AuthToken") or data.get("token") or data.get("access_token") or ""
        if token:
            return token

        # JSON válido pero sin token
        raise UserError(
            _("[%s] JSON recibido pero sin token. Claves presentes: %s")
            % (phase, ", ".join(data.keys()))
        )

    def _raise_non_json_error(self, resp, url, phase=""):
        ctype = (resp.headers.get("Content-Type") or "").lower()
        loc = resp.headers.get("Location") or "-"
        preview = (resp.text or "")[:200].replace("\n", " ")
        raise UserError(
            _("[%s] El endpoint no devolvió JSON (Content-Type: %s). "
              "Status=%s Location=%s Respuesta (inicio): %s")
            % (phase, ctype or "desconocido", resp.status_code, loc, preview)
        )

    def _request_token(self, base_url: str, username: str, password: str, timeout=30):
        """
        Prueba los endpoints documentados en WebAPI2 sobre el root normalizado.
        Devuelve token o lanza UserError.
        """
        base = self._normalize_base(base_url)
        for url in self._login_candidates(base):
            try:
                return self._fetch_token_variant(url, username, password, timeout=timeout)
            except UserError as e:
                _logger.warning(">>> Variante fallida en %s: %s", url, e)

        raise UserError(
            _(
                "Ninguna variante de login devolvió JSON con token. "
                "Verifica que tu suscripción tenga habilitado el Argus Direct API y la ruta de login."
            )
        )

    def _generate_token(self):
        """
        Genera y guarda el token en el registro.
        - Acepta dominio base o endpoint de login.
        """
        for rec in self:
            base = self._normalize_base(rec.endpoint or "")
            if not base or not rec.user or not rec.password:
                _logger.warning(
                    ">>> No se puede generar token: faltan endpoint/usuario/contraseña "
                    "(endpoint=%s, user=%s)", base, bool(rec.user)
                )
                rec.token = ""
                continue

            try:
                token = self._request_token(base, rec.user, rec.password)
                rec.token = token or ""
                if not rec.token:
                    _logger.error(">>> Token vacío recibido desde %s", base)
                    raise UserError(_("No se recibió un token válido desde el endpoint."))
            except Exception as e:
                rec.token = ""
                _logger.error(">>> Error obteniendo token: %s", e)
                raise

    # -------------------------------------------------------------------------
    # Acciones UI
    # -------------------------------------------------------------------------
    def action_test_connection(self):
        """Botón 'Test Connection' en el formulario."""
        self.ensure_one()
        try:
            self._generate_token()
            self.last_tested = fields.Datetime.now()
            return {"type": "ir.actions.client", "tag": "reload"}
        except Exception as e:
            self.last_tested = fields.Datetime.now()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Resultado de conexión"),
                    "message": _("No se recibió un token válido. Detalle: %s") % (str(e)),
                    "type": "danger",
                    "sticky": False,
                },
            }

    def action_sync_metadata(self):
        self.ensure_one()
        price_model = self.env['argus.price'].sudo()
        meta_model = self.env['argus.metadata'].sudo()
        config = self.sudo()

        synced = []
        errors = []

        try:
            if hasattr(price_model, '_sync_v_unit'):
                price_model._sync_v_unit(config)
                synced.append('V_UNIT')
        except Exception as e:
            errors.append(f"V_UNIT: {e}")

        # ✅ llamado directo al modelo de metadatos
        try:
            created = updated = 0
            if hasattr(meta_model, 'sync_from_api'):
                created, updated = meta_model.sync_from_api(config)
                synced.append(f'V_CODE (metadata) [{created} new / {updated} upd]')
            else:
                errors.append("V_CODE: método sync_from_api no encontrado en argus.metadata")
        except Exception as e:
            errors.append(f"V_CODE: {e}")

        # (opcional) si tienes catálogo de delivery mode
        try:
            if hasattr(price_model, '_sync_v_del_mode'):
                price_model._sync_v_del_mode(config)
                synced.append('V_DEL_MODE')
        except Exception as e:
            errors.append(f"V_DEL_MODE: {e}")

        msg = "OK: %s" % (", ".join(synced) or "-")
        if errors:
            msg = msg + " | Errores: %s" % ("; ".join(errors))
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Sync Argus Metadata", "message": msg, "type": "warning", "sticky": False},
            }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": "Sync Argus Metadata", "message": msg, "type": "success", "sticky": False},
        }

    def action_consultar_metadatos_argus(self):
        """Botón 'View Argus Metadata' en el formulario."""
        self.ensure_one()
        action = self.env.ref("api_config_base.action_argus_delivery_mode", raise_if_not_found=False)
        if not action:
            raise UserError(_("No se encontró la acción de metadatos de Argus."))
        return action.read()[0]

    # -------------------------------------------------------------------------
    # Validaciones y eventos
    # -------------------------------------------------------------------------
    @api.constrains("endpoint")
    def _check_endpoint(self):
        for rec in self:
            if rec.endpoint:
                parsed = urlparse(rec.endpoint.strip())
                if not parsed.scheme or not parsed.netloc:
                    raise ValidationError(
                        _(
                            "Endpoint inválido. Ejemplo: "
                            "https://www.argusmedia.com/ArgusWSVSTO o "
                            "https://www.argusmedia.com/ArgusWSVSTO/api/v1/login"
                        )
                    )

    def write(self, vals):
        safe_vals = dict(vals)
        if "password" in safe_vals:
            safe_vals = {**safe_vals, "password": "*****"}
        _logger.info(">>> Editando configuración API con datos: %s", safe_vals)
        return super().write(vals)
