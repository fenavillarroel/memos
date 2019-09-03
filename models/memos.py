from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime

class MemosItems(models.Model):
    _name = 'memos.items'
    _description = 'Items Memorandums'

    name = fields.Char(string='Nombre Producto o Servicio',size=56,required=True)
    cantidad = fields.Float(string='Cantidad')
    id_convenio = fields.Char(string='Id convenio Marco',size=56)
    descripcion = fields.Char(string='Descripcion Tecnica',size=56,required=True)
    precio = fields.Integer(string='Precio Referencia (IVA incluido)')
    id_memo = fields.Many2one('memos.memorandums')

    @api.multi
    def write(self,vals):
        
        actualiza = self.env['memos.memorandums'].search([('id','=',self.id_memo.id)])

        if actualiza.state == 'borrador' or actualiza.state == 'emitido':
        #if vals.get('id_memorandum'):
            #if self.env.user.id == actualiza.de.id or self.env.user.id == self.para.id:
        
            result = super(MemosItems,self).write(vals)
            self.env.cr.commit()
            #else:
            #    raise ValidationError('Sólo usuario emisor o receptor de la Solicitud la pueden modificar...')

        else:
            raise ValidationError(_('El Memorandum solo se puede Modificar si su estado es Borrador o Emitido...'))
            #result = super(PurchaseOrder,self).write(vals)
        return result



class Memorandums(models.Model):
    _name = 'memos.memorandums'
    _description = 'Memorandums'
    _inherit = ['mail.thread']
    
    #_inherit = ['project.project']
    _order = "id desc"

    name = fields.Char(string='Asunto', required=True,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    fecha = fields.Datetime(string='Fecha',default=lambda self: datetime.now(),readonly=True)
    de = fields.Many2one('res.users',string='De',default=lambda self: self.env.user,readonly=True)
    para = fields.Many2one('res.users',string='Para',required=True,store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    id_project = fields.Many2one('project.project',string='Proyecto',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    texto = fields.Html(string='Descripción',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    activo = fields.Boolean(default=True, readonly=True)
    id_oc = fields.Many2one('purchase.order',string='Id OC',readonly=True)
    id_solicitud = fields.Integer(string='Id Solicitud',readonly=True)
    items = fields.One2many('memos.items','id_memo',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    anotacion = fields.One2many('anotaciones.anotaciones','id_memo',readonly=True)
    fecha_ap = fields.Datetime(string='Fecha Aprobación',readonly=True)
    state = fields.Selection(
        selection=[('borrador','Borrador'),
                ('emitido', 'Emitido'),
                ('aprobado','Aprobado')],
        required=True, readonly=True, default='borrador')
    
    
    #@api.multi
    #def write(self,vals):
        
        #if self.state == 'borrador' or self.state == 'emitido':
        #if vals.get('id_memorandum'):
            #if self.env.user.id == self.de.id or self.env.user.id == self.para.id:
    #    result = super(Memorandums,self).write(vals)
    #    self.env.cr.commit()
            #else:
            #    raise ValidationError('Sólo los usuarios emisor o receptor de esta Solicitud la pueden modificar...')

        #else:
        #    raise ValidationError(_('El Memorandum solo se puede Modificar si su estado es Borrador o Emitido...'))
            #result = super(PurchaseOrder,self).write(vals)
    #    return result


    @api.multi
    def sql_user(self):

        qry="select e.name as nombre, d.name as dpto  from hr_employee as e \
             join hr_department as d on e.department_id=d.id \
             where e.work_email='%s'" % (self.env.user.login,)

        self.env.cr.execute(qry)

        us = self.env.cr.dictfetchall()

        qry="select signature from res_users where login='%s'" % (self.env.user.login,)
        self.env.cr.execute(qry)
        sig = self.env.cr.dictfetchall()


        us[0]['firma']=sig[0]['signature']

        return us

    @api.multi
    def button_emitido(self):

                for rec in self:
                    if self.env.user.id == self.de.id:
                        if self.state == 'borrador':
                            rec.write({'state':'emitido'})
                            #to = self.env['res_partners'].search([('email','=',rec.para.login)])
                            #print(to)
                            message="Se ha emitido memorandum #%s, espera tú aprobación" % (rec.id,)
                            self.env['mail.message'].create({'message_type':"notification",
                            "subtype": self.env.ref("mail.mt_comment").id, # subject type
                            'body': message,
                            'subject': "Memorandum #%s emitido" % (rec.id,),
                            'needaction_partner_ids': [(4,rec.para.partner_id.id)],   # partner to whom you send notification
                            'model': rec._name,
                            'res_id': rec.id,
                            })
                        else:
                            raise ValidationError(_('El memo solo se puede aprobar si su estado es Borrador...'))    
                    else:
                        raise ValidationError(_('Solo el emisor del memo lo puede emitir'))

    @api.multi
    def button_aprobado(self):

                for rec in self:
                    if self.env.user.id == self.para.id:
                        if  self.state == 'emitido':
                            rec.write({'state':'aprobado','fecha_ap':datetime.now()})
                            message="Se ha Aprobado memorandum #%s" % (rec.id,)
                            self.env['mail.message'].create({'message_type':"notification",
                            "subtype": self.env.ref("mail.mt_comment").id, # subject type
                            'body': message,
                            'subject': "Memorandum #%s Aprobado" % (rec.id,),
                            'needaction_partner_ids': [(4,rec.de.partner_id.id)],   # partner to whom you send notification
                            'model': rec._name,
                            'res_id': rec.id,
                            })

                        else:
                            raise ValidationError('Sólo es posible aprobar memo si su estado es emitido')
                    else:
                        raise ValidationError('Sólo el receptor del memo lo puede aprobar')

    @api.multi
    def button_borrador(self):

        for rec in self:
            
            if  self.state == 'emitido':
                    if self.env.user.id == self.de.id:
                        rec.write({'state':'borrador'})
                    else:
                        raise ValidationError('No es posible cancelar el memo, sólo el usuario que lo creo lo puede volver a borrador ')
            else:
                raise ValidationError('Sólo se puede cancelar si su estado es emitido')
