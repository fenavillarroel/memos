from odoo import models, fields, api, _
from datetime import datetime

class Anotaciones(models.Model):
    _name = 'anotaciones.anotaciones'
    _description = 'Anotaciones'
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Anotación', required=True)
    fecha = fields.Datetime(string='Fecha',default=lambda self: datetime.now(),readonly=True)
    texto = fields.Html(string='Descripción')
    id_memo = fields.Many2one('memos.memorandums',string='Memorandum')