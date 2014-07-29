#-*- coding:utf-8 -*-

from openerp.osv import osv,fields
from openerp.tools.translate import _

class rainsoft_purchase_order(osv.osv):
    _name='purchase.order'
    _inherit='purchase.order'
    
    def _get_client(self,cr,uid,ids,name,args,context=None):
        res={}
        purchase_order = self.browse(cr,uid,ids[0])
        if purchase_order.origin:
            origin = purchase_order.origin.split(' ')[0]
        else:
            origin = ' '
        sale_order_id = self.pool.get('sale.order').search(cr,uid,[('name','=',origin)],context=context)
        partner_id = self.pool.get('sale.order').read(cr,uid,sale_order_id,['partner_id'],context=context)
        if partner_id:
            res[ids[0]]=partner_id[0]['partner_id'][0]
        else:
            res[ids[0]]=[]
        return res

    _columns={
        'client':fields.function(_get_client,type='many2one',obj='res.partner',method=True,string='Client')
    }

    def send_sms(self,cr,uid,ids,context=None):
	  purchase_order = self.browse(cr,uid,ids[0])
	  mod_obj=self.pool.get('ir.model.data')
	  form_res=mod_obj.get_object_reference(cr,uid,'Rainsoft_Xiangjie','rainsoft_sms_form_view')
	  form_id = form_res and form_res[1] or False
	  value =  {
		  'name':_('Send Text Message'),
		  'view_mode': 'form',
		  'view_id': form_id,
		  'views': [(form_id,'form')],
		  'view_type': 'form',		    
		  'res_model': 'rainsoft.sms', # object name
		  'type': 'ir.actions.act_window',
		  'target': 'new', # if you want to open the form in new tab,
		  }
	  return value
rainsoft_purchase_order()
