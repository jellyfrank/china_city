# -*- coding:utf-8 -*-
from openerp.osv import osv,fields
from rsms import send

class rainsoft_stock_partial_picking(osv.osv):
    _name='stock.partial.picking'
    _inherit='stock.partial.picking'
    def do_partial(self, cr, uid, ids, context=None):
        stock = self.pool.get('stock.picking.out').browse(cr,uid,context['active_id'],context=context)
        partner = self.pool.get('res.partner').browse(cr,uid,stock.partner_id.id,context=context)
        return super(rainsoft_stock_partial_picking,self).do_partial(cr,uid,ids,context=context)
rainsoft_stock_partial_picking()
