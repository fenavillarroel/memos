from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
import xml.etree.ElementTree as ET

class SolicitudItems(models.Model):
    _name = 'solicitud.items'
    _description = 'Items Solicitud'

    name = fields.Char(string='Nombre Producto o Servicio',size=56,required=True)
    cantidad = fields.Float(string='Cantidad')
    id_convenio = fields.Char(string='Id convenio Marco',size=56)
    descripcion = fields.Char(string='Descripcion Tecnica',size=56,required=True)
    precio = fields.Integer(string='Precio Referencia (IVA incluido)')
    id_solicitud = fields.Many2one('solicitud.solicitudes')

    @api.multi
    def write(self,vals):
        
        actualiza = self.env['solicitud.solicitudes'].search([('id','=',self.id_solicitud.id)])

        if actualiza.state == 'solicitud':
        #if vals.get('id_memorandum'):
            #if self.env.user.id == actualiza.de.id or self.env.user.id == self.para.id:
        
            result = super(SolicitudItems,self).write(vals)
            self.env.cr.commit()
            #else:
            #    raise ValidationError('Sólo usuario emisor o receptor de la Solicitud la pueden modificar...')

        else:
            raise ValidationError(_('La Solicitud solo se puede Modificar si su estado es Solicitud...'))
            #result = super(PurchaseOrder,self).write(vals)
        return result





class Solicitudes(models.Model):
    _name = 'solicitud.solicitudes'
    _description = 'Solicitudes'
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
    #id_oc = fields.Many2one('purchase.order',string='Id OC')
    items = fields.One2many('solicitud.items','id_solicitud',store=True, readonly=False, states={'aprobado': [('readonly', True)]})
    fecha_ap = fields.Datetime(string='Fecha Aprobación',readonly=True)
    fecha_re = fields.Datetime(string='Fecha Rechazo',readonly=True)

    state = fields.Selection(
        selection=[('solicitud','Solicitud'),
                ('aprobado', 'Aprobado'),
                ('rechazado','Rechazado')],
        required=True, readonly=True, default='solicitud')


    @api.multi
    def write(self,vals):
        
        if self.state == 'solicitud':
        #if vals.get('id_memorandum'):
            #if self.env.user.id == self.de.id or self.env.user.id == self.para.id:
            result = super(Solicitudes,self).write(vals)
            self.env.cr.commit()
            #else:
            #    raise ValidationError('Sólo los usuarios emisor o receptor de esta Solicitud la pueden modificar...')

        else:
            raise ValidationError(_('La Solicitud solo se puede Modificar si su estado es Solicitud...'))
            #result = super(PurchaseOrder,self).write(vals)
        return result


    @api.multi
    def button_cancelar(self):

                for rec in self:
                    if self.env.user.id == self.para.id:
                        if self.state == 'solicitud':
                            rec.write({'state':'rechazado','fecha_re':datetime.now()})
                        else:
                            raise ValidationError(_('La Solicitud solo se puede rechazar si su estado es Solicitud...'))    
                    else:
                        raise ValidationError(_('Solo el receptor de la Solicitud la puede Rechazar'))

    @api.multi
    def button_aprobado(self):

                for rec in self:
                    if self.env.user.id == self.para.id:
                        if  self.state == 'solicitud':
                            #qry="insert into memos_memorandums (name,fecha,de,para,id_project,texto,state,create_uid,create_date,write_uid,write_date) values \
                            #   ('%s','%s',%s,%s,%s,'%s','%s',%s,'%s',%s,'%s');" % (rec.name,rec.fecha,rec.para.id,rec.para.id,rec.id_project.id,''.join(ET.fromstring(rec.texto).itertext()),'borrador',rec.de.id,datetime.now(),rec.de.id,datetime.now())
                            #print(''.join(ET.fromstring(rec.texto).itertext()))
                            self.env['memos.memorandums'].create({'name':rec.name,
                                                                'fecha':rec.fecha,
                                                                'de':rec.para.id,
                                                                'para':rec.para.id,
                                                                'id_project':rec.id_project.id,
                                                                'id_solicitud':rec.id,
                                                                'texto':''.join(ET.fromstring(rec.texto).itertext()),
                                                                'state':'borrador'})
                            #self.env.cr.execute(qry)
                            self.env.cr.commit()
                            self.env.cr.execute("SELECT currval('memos_memorandums_id_seq') AS id;")
                            lastid=self.env.cr.fetchone()[0]
                            for i in rec.items:
                                #qry="insert into memos_items (name,cantidad,id_convenio,descripcion,precio,id_memo,create_uid,create_date,write_uid,write_date) values \
                                #    ('%s',%s,%s,'%s',%s,%s,%s,'%s',%s,'%s')" % (i.name,i.cantidad,i.id_convenio,i.descripcion,i.precio,lastid,rec.de.id,datetime.now(),rec.de.id,datetime.now())
                                self.env['memos.items'].create({'name':i.name,
                                                                'cantidad':i.cantidad,
                                                                'id_convenio':i.id_convenio,
                                                                'descripcion':i.descripcion,
                                                                'precio':i.precio,
                                                                'id_memo':lastid
                                                                })
                                #self.env.cr.execute(qry)
                                self.env.cr.commit()
                                
                            rec.write({'state':'aprobado','fecha_ap':datetime.now()})

                            message="Se ha Aprobado Solicitud de Memorandum #%s" % (rec.id,)
                            self.env['mail.message'].create({'message_type':"notification",
                            "subtype": self.env.ref("mail.mt_comment").id, # subject type
                            'body': message,
                            'subject': "Solicitud de Memorandum #%s Aprobado" % (rec.id,),
                            'needaction_partner_ids': [(4,rec.de.partner_id.id)],   # partner to whom you send notification
                            'model': rec._name,
                            'res_id': rec.id,
                            })


                        else:
                            raise ValidationError('Sólo es posible aprobar Solicitud de Memo si su estado es Aprobado')
                    else:
                        raise ValidationError('Sólo el receptor de la Solicitud la puede aprobar')
