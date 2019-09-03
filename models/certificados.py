from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class CertificadoItems(models.Model):
    _name = 'certificado.items'
    _description = 'Items Certificados'

    name = fields.Char(string='Referencia',size=56,required=True)
    cantidad = fields.Float(string='Cantidad', default=0)
    descripcion = fields.Char(string='Descripcion Técnica',size=56,required=True)
    precio = fields.Integer(string='Valor unitario', default=0)
    #total = fields.Integer(string='Valor total', compute='_compute_total', readonly=True)
    id_certificado = fields.Many2one('certificado.certificados')


class Certificados(models.Model):
    _name = 'certificado.certificados'
    _description = 'Certificados'
    _order = "id desc"
    _inherit = ['mail.thread']

    id_memo = fields.Many2one('memos.memorandums',string='Id Memorandum',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    ano = fields.Char(string='Año Presupuestario', default=lambda self: datetime.today().year,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    fecha = fields.Datetime(string='Fecha',default=lambda self: datetime.now(),store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    name = fields.Text(string='Bien o Servicio', required=True,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    items = fields.One2many('certificado.items','id_certificado',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    imputacion = fields.Many2one('certificado.imputaciones', required=True,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    monto = fields.Html(string='Monto a Comprometer', required=True,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    neto = fields.Integer(string='Total Neto', compute='_compute_total', store=True, readonly=True, default=0)
    iva = fields.Integer(string='IVA', compute='_compute_total', store=True, readonly=True,)
    total = fields.Integer(string='Total', compute='_compute_total', store=True, readonly=True)
    fecha_ap = fields.Datetime(string='Fecha', readonly=True)
    activo = fields.Boolean(default=True, readonly=True)
    #El correo se usa por defecto el del director DAF
    responsable = fields.Many2one('hr.employee', string='Responsable', required=True, default= lambda self: self.env['hr.employee'].search([('work_email','=','fernando.villarroel@uaysen.cl')]),store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    usuario = fields.Integer(string='Usuario', compute='_get_users', store=True, readonly=True)

    state = fields.Selection(
        selection=[('borrador','Borrador'),
                ('emitido', 'Emitido'),
                ('aprobado','Aprobado')],
        required=True, readonly=True, default='borrador')

    @api.multi
    def write(self,vals):
        
        if self.state == 'borrador' or self.state == 'emitido':
        #if vals.get('id_memorandum'):
            #if self.env.user.id == self.de.id or self.env.user.id == self.para.id:
            result = super(Certificados,self).write(vals)
            self.env.cr.commit()
            #else:
            #    raise ValidationError('Sólo los usuarios emisor o receptor de esta Solicitud la pueden modificar...')

        else:
            raise ValidationError(_('El Certificado solo se puede Modificar si su estado es Borrador o Emitido...'))
            #result = super(PurchaseOrder,self).write(vals)
        return result

    @api.depends('responsable')
    def _get_users(self):

        for r in self:
            r.usuario=self.env['res.users'].search([('login','=',self.responsable.work_email)])
            

    @api.depends('items')
    def _compute_total(self):

        subtotal=0
        for r in self:
            for rr in r.items:
                subtotal += (rr.cantidad * rr.precio)
            r.neto = subtotal
            r.iva = ( subtotal * 0.19 )
            r.total = r.neto + r.iva


    @api.multi
    def get_user(self,resp=None):

        qry="select work_email from hr_employee where id=%s" % (self.responsable.id,)
        self.env.cr.execute(qry)

        res=self.env.cr.dictfetchall()

        qry="select e.name as nombre, d.name as dpto  from hr_employee as e \
             join hr_department as d on e.department_id=d.id \
             where e.work_email='%s'" % (res[0]['work_email'])

        self.env.cr.execute(qry)
        us = self.env.cr.dictfetchall()

        qry="select signature from res_users where login='%s'" % (res[0]['work_email'],)
        self.env.cr.execute(qry)
        sig = self.env.cr.dictfetchall()


        us[0]['firma']=sig[0]['signature']

        return us

    @api.multi
    def button_emitido(self):

                for rec in self:
                    if self.env.user.id == rec.create_uid.id:
                        if self.state == 'borrador':
                            rec.write({'state':'emitido'})
                        else:
                            raise ValidationError(_('El Certificado solo se puede aprobar si su estado es Borrador...'))    
                    else:
                        raise ValidationError(_('Solo el emisor o creador del Certificado lo puede emitir'))

    @api.multi
    def button_aprobado(self):

                for rec in self:
                    print(rec.usuario)
                    if self.env.user.id == rec.usuario:
                        if  self.state == 'emitido':
                            rec.write({'state':'aprobado','fecha_ap':datetime.now()})
                        else:
                            raise ValidationError('Sólo es posible aprobar Certificado si su estado es Emitido...')
                    else:
                        raise ValidationError('Sólo el Responsable del memo lo puede aprobar')

    @api.multi
    def button_borrador(self):

        for rec in self:
            
            if  self.state == 'emitido':
                    if self.env.user.id == rec.create_uid.id:
                        rec.write({'state':'borrador'})
                    else:
                        raise ValidationError('No es posible cancelar el Certificado, sólo el usuario que lo creo lo puede volver a borrador ')
            else:
                raise ValidationError('Sólo se puede cancelar Certificado si su estado es emitido')

