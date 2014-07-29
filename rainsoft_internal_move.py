# -*- coding:utf-8 -*-

from openerp.osv import osv,fields
from datetime import * 
from openerp.tools.translate import _


class rainsoft_internal_move(osv.osv):
	_name="stock.picking"
	_inherit="stock.picking"
	
	_columns={
	      'origin_stock':fields.many2one('stock.location','Origin Stock',select=True,states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},domain=[('usage','=','internal')]),
	      'dest_stock':fields.many2one('stock.location','Dest Stock',select=True,states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},domain=[('usage','=','internal')]),
	  }
	
	def qa_stock_to_move(self,cr,uid,ids,origin_stock,dest_stock,context=None):
		#find the QA stock
		#stock_location=self.pool.get('stock.location').search(cr,uid,[('name','=','QA')])
		stock_location = [origin_stock]
		stock_dest_location = [dest_stock]

		product_ids =  self.pool.get('product.product').search(cr,uid,[('type','<>','Service')])
		company = self.pool.get('product.product').browse(cr,uid,1)

		move_lines=[]
		for product_id in product_ids:
			res = self.pool.get('stock.location')._product_value(cr,uid,stock_location,['stock_real'],0,{'product_id':product_id})
			if res[stock_location[0]]["stock_real"]>0:
				product = self.pool.get('product.product').browse(cr,uid,product_id)
				move_line = {
				"product_qty":res[stock_location[0]]["stock_real"],
				"name":product.name,
				"product_id":product.id,
				"product_uom":product.uom_id.id,
				"location_id":stock_location[0],
				"location_dest_id":stock_dest_location[0],
				"company_id":company.id,
				"date_expected":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				"state":'draft'
				}
				move_lines.append(move_line)
		print move_lines
		#return self.write(cr,uid,ids,{'move_lines':move_lines})
		return {'value':{'move_lines':move_lines}}

rainsoft_internal_move()
