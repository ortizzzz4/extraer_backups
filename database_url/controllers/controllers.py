# -*- coding: utf-8 -*-
# from odoo import http


# class DatabaseUrl(http.Controller):
#     @http.route('/database_url/database_url', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/database_url/database_url/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('database_url.listing', {
#             'root': '/database_url/database_url',
#             'objects': http.request.env['database_url.database_url'].search([]),
#         })

#     @http.route('/database_url/database_url/objects/<model("database_url.database_url"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('database_url.object', {
#             'object': obj
#         })
