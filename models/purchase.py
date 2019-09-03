from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    id_memorandum = fields.Many2one('memos.memorandums',string='Memorandum')

    @api.model
    def create(self,vals):
        
        result =''
        if vals['id_memorandum']:
            result = super(PurchaseOrder,self).create(vals)
            actualiza = self.env['memos.memorandums'].search([('id','=',vals['id_memorandum'])])
            dic = {'id_oc':result.id}
            #dic = {'id_oc':result.id,'activo':False}
            actualiza.write(dic)
            self.env.cr.commit()
        else:
            result = super(PurchaseOrder,self).create(vals)
        return result

    @api.multi
    def write(self,vals):
        
        #if vals['id_memorandum']:
        if vals.get('id_memorandum'):
            result = super(PurchaseOrder,self).write(vals)
            actualiza = self.env['memos.memorandums'].search([('id','=',vals['id_memorandum'])])
            dic = {'id_oc':self.id}
            #dic = {'id_oc':self.id,'activo':False}
            actualiza.write(dic)
            self.env.cr.commit()
        else:
            result = super(PurchaseOrder,self).write(vals)
        return result
