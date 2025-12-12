# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import datetime

class NewsController(http.Controller):

    @http.route('/news/ultimas', type='json', auth='user')
    def get_latest_news(self):
        News = request.env['api.news'].sudo()

        # Noticias de los últimos 3 días
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=3)
        str_start = start_date.strftime('%Y-%m-%dT%H:%M:%S')
        str_end = end_date.strftime('%Y-%m-%dT%H:%M:%S')

        try:
            noticias = News.fetch_updated_news(str_start, str_end)
            result = []
            for n in noticias:
                detail = News.fetch_news_detail(n['NewsId'])
                result.append({
                    'id': detail.get('NewsId'),
                    'headline': detail.get('Headline'),
                    'date': detail.get('PublicationDate'),
                    'html': detail.get('Text'),
                    'free': detail.get('Free'),
                    'featured': detail.get('Featured'),
                    'language_id': detail.get('LanguageId'),
                })
            return {'status': 'ok', 'news': result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
