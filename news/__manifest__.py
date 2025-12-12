{
    'name': 'News',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Connects Odoo with the Argus API to import prices and metadata',
    'description': """
Module developed by HSO Technology (https://www.hsotechnology.com).
This module allows you to:
 - Configure the connection to the Argus API.
 - Import product metadata (code_id, description, units, delivery mode).
 - Import historical and updated prices from Argus with all available fields.
 - Enrich price records with human-readable descriptions and units.
""",
    'author': 'HSO Technology',
    'website': 'https://www.hsotechnology.com',
    'depends': ['base'],
    'data': [
        # 1. SECURITY PRIMERO
        'security/ir.model.access.csv',
        
        # 2. DATOS/CONFIGURACIÓN       
        'data/cron_news.xml',
        
        # 3. VISTAS BASE
        'views/api_config_model.xml',
        'views/api_config_view.xml',
        'views/api_config_menu.xml',
        
        # 4. VISTAS DE MODELOS
        
        'views/news_template.xml',
        'views/server_actions.xml',
        
        # 5. WIZARDS
        'wizards/argus_price_wizard_view.xml',
        'wizards/argus_metadata_wizard_view.xml',
    ],
    'icon': '/news/static/description/icon.png',
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
