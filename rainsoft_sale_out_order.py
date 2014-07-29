#-*- coding:utf-8 -*-

##############################################################################
#
#    This module is designed for QingDao Xiangjie company,written by Kevin Kong.
#    you can freely changed the code for your own purpose,any suggestions,please
#    contact kfx2007@163.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv,fields
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools.translate import _

class rainsoft_sale_out_order(osv.osv):
    _name='rainsoft.saleout'
    _description='Compare Sale Order and Delivery Order'
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_amount': 0.0,
                'amount_send_amount': 0.0,
                'amount_order_money': 0.0,
                'amount_send_money': 0.0,
            }
            val2 = val1=val3=val4 = 0.0
            for line in order.sale_order_line:
                val1 += line.amount
                val2 += line.send_amount
                val3 += line.order_money
                val4 += line.send_money
            res[order.id]['amount_amount'] = val1
            res[order.id]['amount_send_amount'] = val2
            res[order.id]['amount_order_money'] = val3
            res[order.id]['amount_send_money'] = val4            
        return res

    _columns={
        "name":fields.char(string='name',required=True),
        "partner_id":fields.many2one('res.partner','Partner',requried=True),
        "sale_order_id":fields.many2one('sale.order','Sale Order',required=True),
        "sale_order_line":fields.one2many('rainsoft.saleout.line','order_id','Order Lines'),
        "state":fields.selection(
	  [('new','New'),
	   ('done','Done'),],'Stage',readonly=True
	  ),
        
    }	  		
    
    _order='name'
	  
	  
    def action_view_invoice(self, cr, uid, ids, context=None):
	sale_out_order = self.browse(cr,uid,ids[0],context=context)
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for so in self.pool.get('sale.order').browse(cr, uid, [sale_out_order.sale_order_id.id], context=context):
            inv_ids += [invoice.id for invoice in so.invoice_ids]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result
	
    def saleout_invoice(self,cr,uid,ids,context=None):
	sale_out_order = self.browse(cr,uid,ids[0],context=context)
	sale_order = self.pool.get('sale.order').browse(cr,uid,sale_out_order.sale_order_id.id,context=context)
	""" create invoices for the given sales orders (ids), and open the form
            view of one of the newly created invoices
        """
        mod_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")

        # create invoices through the sales orders' workflow
        inv_ids0 = set(inv.id for sale in self.pool.get('sale.order').browse(cr, uid, [sale_out_order.sale_order_id.id], context) for inv in sale.invoice_ids)
        for id in ids:
            wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
        inv_ids1 = set(inv.id for sale in self.pool.get('sale.order').browse(cr, uid, [sale_out_order.sale_order_id.id], context) for inv in sale.invoice_ids)
        # determine newly created invoices
        new_inv_ids = list(inv_ids1 - inv_ids0)

        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        
        #create customer invoice
        val = {
	    "partner_id":sale_out_order.partner_id.id,
	    "account_id":sale_order.partner_id.property_account_receivable.id,	    
	    "origin":sale_order.name,
	  }
	
	invocie_id =self.pool.get('account.invoice').create(cr,uid,val,context=context)
	
	cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (sale_order.id, invocie_id))
	#create invocie line
	values={}
	for line in sale_out_order.sale_order_line:
	    #if line is MRP product then skip it
	    if line.mrp_product_id.id:
		continue
	  
	    account_id = line.product_id.property_account_income.id
	    if not account_id:
		account_id = line.product_id.categ_id.property_account_income_categ.id
	    if not account_id:
		raise osv.except_osv(_('Error!'),
			_('Please define income account for this product: "%s" (id:%d).') % \
			    (line.product_id.name, line.product_id.id,))
	  
	    values={
		'invoice_id':invocie_id,
		'product_id':line.product_id.id,
		'name':line.product_id.name,
		'quantity':line.send_amount,
		'price_unit':line.price,
		'account_id':account_id,
	      }
	    self.pool.get('account.invoice.line').create(cr,uid,values,context=context)
	
	self.write(cr,uid,ids,{'state':'done'})
	
	#checking the out_order's state,if it is not done,cancel it
	out_order_ids = self.pool.get('stock.picking.out').search(cr,uid,[('origin','=',sale_order.name)],context=context)
        out_orders = self.pool.get('stock.picking.out').browse(cr,uid,out_order_ids,context=context)
        
        for out_order in out_orders:
	    if out_order.state != 'done':
		self.pool.get('stock.picking.out').write(cr,uid,out_order.id,{'state':'cancel'})
        
	self.pool.get('sale.order').write(cr,uid,sale_out_order.sale_order_id.id,{'state':'done'},context=context)
	self.write(cr,uid,ids,{'state':'done'})
	return True
	  
    def saleout_new(self,cr,uid,ids,context=None):	
	sale_out_order = self.browse(cr,uid,ids[0],context=context)
	sale_order = self.pool.get('sale.order').browse(cr,uid,sale_out_order.sale_order_id.id,context=context)
	
	
	self.write(cr,uid,ids,{'state':'new'})
	return True
      
    def saleout_done(self,cr,uid,ids,context=None):	
	sale_out_order = self.browse(cr,uid,ids[0],context=context)
	sale_order = self.pool.get('sale.order').browse(cr,uid,sale_out_order.sale_order_id.id,context=context)
	invoice = self.pool.get('account.invoice').browse(cr,uid,sale_order.invoice_ids[0],context=context)
	#checking the invoice's state
	if invoice.state !='paid':
	    raise osv.except_osv(_('Error!'),
			_("you haven't paid your invoice yet!"))
	#checking the out_order's state,if it is not done,cancel it
	out_order_ids = self.pool.get('stock.picking.out').search(cr,uid,[('origin','=',sale_order.name)],context=context)
        out_orders = self.pool.get('stock.picking.out').browse(cr,uid,out_order_ids,context=context)
        
        for out_order in out_orders:
	    if out_order.state != 'done':
		self.pool.get('stock.picking.out').write(cr,uid,out_order.id,{'state':'cancel'})
        
	self.pool.get('sale.order').write(cr,uid,sale_out_order.sale_order_id.id,{'state':'done'},context=context)
	self.write(cr,uid,ids,{'state':'done'})
	return True

rainsoft_sale_out_order()

class rainsoft_sale_out_line(osv.osv):
    _name='rainsoft.saleout.line'


    def _get_order_money(self,cr,uid,ids,name,args,context=None):
        res={}
        lines = self.browse(cr,uid,ids)
        for line in lines:
            res[line.id]=line.price * line.amount
        return res

    def _get_send_data(self,cr,uid,ids,name,args,context=None):
        res={}
        orders=''
        amount = 0
        location=[]
        line = self.browse(cr,uid,ids)
        sale_out_order = self.pool.get('rainsoft.saleout').browse(cr,uid,line.order_id.id,context=context)
        sale_order = self.pool.get('sale.order').browse(cr,uid,sale_out_order.sale_order_id.id,context=context)
        out_order_ids = self.pool.get('stock.picking.out').search(cr,uid,[('origin','=',sale_order.name)],context=context)
        out_orders = self.pool.get('stock.picking.out').browse(cr,uid,out_order_ids,context=context)
       
        for out_order in out_orders:
	    #验证产品是否在出库单中
	    for move_line in out_order.move_lines:
		if line.product_id == move_line.product_id and move_line.state=='done' and out_order.name.startswith('OUT'):
		    amount +=move_line.product_qty
		    orders +=' '+str(out_order.name)
		    location.append(move_line.location_id.id)
		if line.product_id == move_line.product_id and move_line.state=='done' and out_order.name.startswith('IN'):#退货
		    amount -=move_line.product_qty
		    orders +=' '+str(out_order.name)
		    location.append(move_line.location_id.id)
        res["orders"]=orders
        res["amount"]=amount
        res["location"]=location
        return res

    def _get_send_order(self,cr,uid,ids,name,args,context=None):
        res={}
        lines = self.browse(cr,uid,ids)
        for line in lines:
            result=self._get_send_data(cr,uid,line.id,name,args,context=context)
            res[line.id]=result["orders"]
        return res 

    def _get_send_amount(self,cr,uid,ids,name,args,context=None):
        res={}
        MRP={}
        lines = self.browse(cr,uid,ids)
        #odd code:here the code will execute towice,first time execute by line id asc
        #but second time it will execute by line id desc
        #so,I have to sort it before the loop.
        lines.sort(key=lambda x:x.id)
        for line in lines:
	    result=self._get_send_data(cr,uid,line.id,name,args,context=context)
	    if result["amount"] > line.amount:
		if not MRP.has_key(line.product_id.id):
		    MRP[line.product_id.id]=result["amount"]-line.amount
		    res[line.id]=line.amount
		elif MRP[line.product_id.id]-line.amount>0:
		    res[line.id]=line.amount
		    MRP[line.product_id.id] -=line.amount
		else:
		    res[line.id]=MRP[line.product_id.id]
		    MRP[line.product_id.id]=0
	    else:
		res[line.id]=result["amount"]
	    #check the product if it is mrp product
	    mrp = self.pool.get('mrp.bom').search(cr,uid,[('product_id','=',line.product_id.id),('bom_id','=',False)],context=context)
	    if len(mrp)>0:	      
		mrp_lines = self.search(cr,uid,[('mrp_product_id','=',line.product_id.id),('order_id','=',line.order_id.id)],context=context)		
		#relation
		x = min([self.browse(cr,uid,mrp_line,context=context).amount for mrp_line in mrp_lines])/line.amount		
		amount = min([self.browse(cr,uid,mrp_line,context=context).send_amount for mrp_line in mrp_lines])/x		
		res[line.id]=amount
        return res

    def _get_send_money(self,cr,uid,ids,name,args,context=None):
        res={}
        lines = self.browse(cr,uid,ids)
        for line in lines:
                res[line.id]=line.price * line.send_amount
        return res  
      
    def _get_location(self,cr,uid,ids,name,args,context=None):
	res={}
	stock_loc=''
	lines = self.browse(cr,uid,ids)	
	for line in lines:
	      result=self._get_send_data(cr,uid,line.id,name,args,context=context)
	      for loc in result["location"]:
		  location = self.pool.get('stock.location').browse(cr,uid,loc,context=context)
		  stock_loc=" "+str(location.name)
	      res[line.id] =stock_loc
	return res
    
        
    _columns={
        "order_id":fields.many2one('rainsoft.saleout','Order Reference'),
        "product_id":fields.many2one('product.product','Product',required=True),
        "mrp_product_id":fields.many2one('product.product','MRP Prodct'),
        "price":fields.float('Price',digits_compute= dp.get_precision('Product Price'),required=True),
        "amount":fields.float('Amount',digits_compute= dp.get_precision('Product UoS'),required=True),
        "unit":fields.many2one('product.uom','Unit of Measure'),
        "send_amount":fields.function(_get_send_amount,string='Send_Amount',digits_compute= dp.get_precision('Product UoS')),
        "send_order_id":fields.function(_get_send_order,type='char',string='Send_Order'),
        "order_money":fields.function(_get_order_money,string='Order_Money',digits_compute= dp.get_precision('Account')),
        "send_money":fields.function(_get_send_money,string='Send_Money',digits_compute= dp.get_precision('Account')),
        "location":fields.function(_get_location,string="loc",type='char'),
        }

rainsoft_sale_out_line()
