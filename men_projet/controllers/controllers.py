# -*- coding: utf-8 -*-
from odoo import http

# class MenProjet(http.Controller):
#     @http.route('/men_projet/men_projet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/men_projet/men_projet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('men_projet.listing', {
#             'root': '/men_projet/men_projet',
#             'objects': http.request.env['men_projet.men_projet'].search([]),
#         })

#     @http.route('/men_projet/men_projet/objects/<model("men_projet.men_projet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('men_projet.object', {
#             'object': obj
#         })