# -*- coding: utf-8 -*-
import requests
import json
import logging
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class MarineRegistration(models.Model):
    _name = 'marine.registration'
    _description = 'Marine User Registration'
    _order = 'create_date desc'

    email = fields.Char(string='Email', required=True)
    password = fields.Char(string='Password', required=True)
    password_confirmation = fields.Char(string='Confirm Password', required=True)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    phone = fields.Char(string='Phone')
    company = fields.Char(string='Company')
    website = fields.Char(string='Website')
    bio = fields.Text(string='Bio')
    plan_id = fields.Integer(string='Plan ID', default=1)
    billing_period = fields.Selection([
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semiannual', 'Semiannual'),
        ('Annual', 'Annual')
    ], string='Billing Period', default='Quarterly')
    role = fields.Selection([
        ('user', 'User'),
        ('admin', 'Admin')
    ], string='Role', default='user')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('failed', 'Failed')
    ], string='Status', default='draft', readonly=True)
    response_message = fields.Text(string='API Response', readonly=True)

    def action_register_user(self):
        for record in self:
            if record.password != record.password_confirmation:
                raise UserError(_("Passwords do not match!"))
            
            # API Configuration from environment variables
            base_url = os.environ.get('MARINE_API_URL', 'http://host.docker.internal:8000')
            admin_email = os.environ.get('MARINE_ADMIN_EMAIL', 'support@markdebrand.com')
            admin_password = os.environ.get('MARINE_ADMIN_PASSWORD', '12345678')

            # 1. Login to get token
            login_url = f"{base_url}/auth/login"
            login_payload = {
                "email": admin_email,
                "password": admin_password
            }
            
            try:
                login_response = requests.post(login_url, json=login_payload, timeout=10)
                if login_response.status_code != 200:
                    record.write({
                        'state': 'failed',
                        'response_message': f"Login Failed (Status {login_response.status_code}): {login_response.text}"
                    })
                    continue
                
                login_data = login_response.json()
                access_token = login_data.get('access_token')
                if not access_token:
                    record.write({
                        'state': 'failed',
                        'response_message': "Login Succeeded but no access token received."
                    })
                    continue

                # 2. Register user
                register_url = f"{base_url}/auth/register"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                register_payload = {
                    "email": record.email,
                    "password": record.password,
                    "password_confirmation": record.password_confirmation,
                    "role": record.role,
                    "first_name": record.first_name,
                    "last_name": record.last_name,
                    "phone": record.phone or "",
                    "company": record.company or "",
                    "website": record.website or "",
                    "bio": record.bio or "",
                    "plan_id": record.plan_id,
                    "billing_period": record.billing_period
                }
                
                register_response = requests.post(register_url, json=register_payload, headers=headers, timeout=10)
                
                if register_response.status_code in [200, 201]:
                    record.write({
                        'state': 'registered',
                        'response_message': f"Registration Successful: {register_response.text}"
                    })
                else:
                    record.write({
                        'state': 'failed',
                        'response_message': f"Registration Failed (Status {register_response.status_code}): {register_response.text}"
                    })
                    
            except requests.exceptions.RequestException as e:
                record.write({
                    'state': 'failed',
                    'response_message': f"Connection Error: {str(e)}"
                })

        return True
