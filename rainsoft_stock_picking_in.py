# -*- coding:utf-8 -*-

from openerp.osv import osv,fields
import re

class rainsoft_picking_in(osv.osv):
    _name='stock.picking.in'
    _inherit='stock.picking.in'

    def _get_stock_picking_in_client(self,cr,uid,ids,name,args,context=None):
        return self.pool.get('stock.picking')._get_stock_picking_in_client(cr,uid,ids,name,args,context=context)
        #res={}
        #stock_in_order = self.browse(cr,uid,ids[0])
        #sale_order_id = self.pool.get('sale.order').search(cr,uid,[('name','=',stock_in_order.origin)],context=context)
        #partner_id = self.pool.get('sale.order').read(cr,uid,sale_order_id,['partner_id'],context=context)
        #if partner_id:
        #    res[ids[0]]=partner_id[0]['partner_id'][0]
        #else:
        #    res[ids[0]]=[]
        #return {}

    _columns={
        'origin_partner':fields.function(_get_stock_picking_in_client,type='many2one',obj='res.partner',method=True,string='Client'),        
    }

rainsoft_picking_in()

class rainsoft_picking(osv.osv):
    _name="stock.picking"
    _inherit="stock.picking"

    def _get_stock_picking_in_client(self,cr,uid,ids,name,args,context=None):
        res={}
        stock_in_order=self.browse(cr,uid,ids[0])
        if stock_in_order.origin:
            origin = re.split(' |:',stock_in_order.origin)
            sale_order_id = self.pool.get('sale.order').search(cr,uid,[('name','=',origin[len(origin)-1])],context=context) 
            partner_id = self.pool.get('sale.order').read(cr,uid,sale_order_id,['partner_id'],context=context)
            if partner_id:
                res[ids[0]]=partner_id[0]['partner_id'][0]
        else:
            res[ids[0]]=[]
        return res



    _columns={
        'origin_partner':fields.function(_get_stock_picking_in_client,type='many2one',obj='res.partner',method=True,string='Client'),
    }
rainsoft_picking()
