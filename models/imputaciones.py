from odoo import models, fields, api, _


class CertificadoImputaciones(models.Model):
    _name = 'certificado.imputaciones'
    _inherit = ['mail.thread']
    _description = 'Imputaciones'

    name = fields.Text(string='Título', required=True)
    