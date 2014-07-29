# -*- coding:utf-8 -*-

from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp import netsvc

class rainsoft_picking_out(osv.osv):
    _name='stock.picking.out'
    _inherit='stock.picking.out'

    def send_sms(self,cr,uid,ids,context=None):
        mod_obj=self.pool.get('ir.model.data')
        form_res=mod_obj.get_object_reference(cr,uid,'Rainsoft_Xiangjie','rainsoft_sms_form_view')
        form_id = form_res and form_res[1] or False
        value ={
               'name':_('Send Text Message'),
               'view_mode': 'form',
               'iew_id': False,
               'views': [(form_id,'form')],
               'view_type': 'form',            
               'res_model': 'rainsoft.sms', # object name
               'type': 'ir.actions.act_window',
               'target': 'new', # if you want to open the form in new tab
               }
	
	wf_service = netsvc.LocalService("workflow")
	out_order = self.browse(cr,uid,ids[0],context=context)
	sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('name','=',out_order.origin)],context=context)
	sale_order = self.pool.get('sale.order').browse(cr,uid,sale_order_ids[0],context=context)
	for line in sale_order.order_line:
	    mrp = self.pool.get('mrp.bom').search(cr,uid,[('product_id','=',line.product_id.id),('bom_id','=',False),('type','=','phantom')],context={})
	    if len(mrp):
		p_order_ids = self.pool.get('procurement.order').search(cr,uid,[('origin','=',out_order.origin),('product_id','=',line.product_id.id)],context=context)
		
		if len(p_order_ids):
		    wf_service.trg_trigger(uid, 'procurement.order', p_order_ids[0],cr)
		    
        return value
      
rainsoft_picking_out()

class rainsoft_stock_move(osv.osv):
    _name="stock.move"
    _inherit="stock.move"
    
    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_uos_qty': 0.00
          }
        warning = {}

        if (not product_id) or (product_qty <=0.0):
            result['product_qty'] = 0.0
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        
        # Warn if the quantity was decreased 
        if ids:
            for move in self.read(cr, uid, ids, ['product_qty']):
		print product_qty,move['product_qty']
                if product_qty < move['product_qty']:
                    warning.update({
                       'title': _('Information'),
                       'message': _("By changing this quantity here, you accept the "
                                "new quantity as complete: OpenERP will not "
                                "automatically generate a back order.") })
		if product_qty > move['product_qty']:
		    product_qty = move['product_qty']
		    result['product_qty']=product_qty
                break

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty

        return {'value': result, 'warning': warning}
rainsoft_stock_move()