#encoding:utf-8

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
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class rainsoft_account_stock(osv.osv):
    _name='rainsoft.account.stock'

    _columns={
        'location':fields.many2one('stock.location','Location'),
        'period_id':fields.many2one('account.period','Period'),
        'direct_origin':fields.many2one('stock.location','Origin Location'),
        'direct_dest':fields.many2one('stock.location','Dest Location'),
        'inventory':fields.many2one('stock.location','Inventory Location'),
    }

    def action_query(self,cr,uid,ids,context=None):
        if context is None:
            context={}
        #every time you query,loop the products 
        #if product is not in current lines, insert it.
        products = self.pool.get('product.product').search(cr,uid,[],context=context)
        period = self.browse(cr,uid,ids[0]).period_id
        location = self.browse(cr,uid,ids[0]).location
        direct_origin = self.browse(cr,uid,ids[0]).direct_origin
        direct_dest = self.browse(cr,uid,ids[0]).direct_dest
        inventory_loc = self.browse(cr,uid,ids[0]).inventory
        for product in products:
	    if len(self.pool.get('rainsoft.account.stock.line').search(cr,uid,[('product_id','=',product)],context=context))==0:
		self.pool.get('rainsoft.account.stock.line').create(cr,uid,{'product_id':product,},context=context)
        context['location']=self.browse(cr,uid,ids[0]).location.id
        
        return {
            'name':u'库存报表',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'rainsoft.account.stock.line',
            'type':'ir.actions.act_window',
            'context':{
                'location': location.id,
                'date_start':period.date_start,
                'date_stop':period.date_stop,
                'period':period.id,
                'direct_origin':direct_origin.id,
                'direct_dest':direct_dest.id,
                'inventory':inventory_loc.id,
            },
	    'limit':10000,
        }
    
    def action_query_history(self,cr,uid,ids,context=None):
	if context is None:
            context={}
                
        return {
            'name':u'历史库存报表',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'rainsoft.account.carryover',
            'type':'ir.actions.act_window',
            'context':{
                'location': self.browse(cr,uid,ids[0]).location.id,
                'date_start':self.browse(cr,uid,ids[0]).period_id.date_start,
                'date_stop':self.browse(cr,uid,ids[0]).period_id.date_stop,                
            },
        }

rainsoft_account_stock()

class rainsoft_account_stock_line(osv.osv):
    _name="rainsoft.account.stock.line"
      
    def _get_locations(self,cr,uid,ids,name,args,location,context=None):
	res = context['res']
	locations = self.pool.get('stock.location').search(cr,uid,[('location_id','=',location)],context=context)
	if len(locations)>0:
	    for location in locations:
	      self._get_locations(cr,uid,ids,name,args,location,context=context)
	else:
	    res.append(location)
	    context['res']=res	
    
    def _get_current(self,cr,uid,ids,name,args,context=None):
	res={}
	if context == None:
	    context={}
	if context.has_key('location') and context.has_key('date_start') and context.has_key('date_stop') and context.has_key('direct_origin') and context.has_key('direct_dest') and context.has_key('inventory'):
	    direct_origin = context['direct_origin']
	    direct_dest = context['direct_dest']
	    location=context['location']
	    inventory_loc = context['inventory']
	    context['res']=[]
	    self._get_locations(cr,uid,ids,name,args,location,context=context)
	    locs = []
	    if isinstance(context['res'],list):
		locs = context['res']
	    else:
		locs = [context['res']]
	    
	    date_start = context['date_start']
	    date_stop = context['date_stop']
	    periods = self.pool.get('account.period').search(cr,uid,[('special','=',False),('state','=','done')],context=context)
	    last_period_id = periods and max(periods)
	    #last_period = self.pool.get('account.period').browse(cr,uid,last_period_id,context=context)
	    
	    lines = self.browse(cr,uid,ids)
	    for line in lines:
		res[line.id]={
		    'init_remainder':0.0,
		    'init_money':0.0,
		    'current_in_count':0.0,
		    'current_in_money':0.0,
		    'inventory_in_count':0.0,
		    'inventory_in_money':0.0,
		    'inventory_out_count':0.0,
		    'inventory_out_count':0.0,
		    'current_out_count':0.0,
		    'current_out_money':0.0,
		    'end_remainder':0.0,
		    'end_money':0.0,
		  }
		average_price=0.0
		
		#init remainder (from last account period)
		carr_ids = self.pool.get('rainsoft.account.carryover').search(cr,uid,[('period','=',last_period_id)],context=context)
		
		if len(carr_ids)>0:
		    carryover = self.pool.get('rainsoft.account.carryover').browse(cr,uid,carr_ids[0],context=context)
		    carryover_line_id = self.pool.get('rainsoft.account.carryover.line').search(cr,uid,[('carryover_id','=',carryover.carry_over_line[0].carryover_id.id),('product_id','=',line.product_id.id)],context=context)
		    if len(carryover_line_id)>0:
		      res[line.id]['init_remainder'] = self.pool.get('rainsoft.account.carryover.line').browse(cr,uid,carryover_line_id[0],context=context).end_remainder
		      res[line.id]['init_money'] = self.pool.get('rainsoft.account.carryover.line').browse(cr,uid,carryover_line_id[0],context=context).end_money
		      
		#inventory in stock
		inventory_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','=',inventory_loc),('location_dest_id','in',locs),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		
		if len(inventory_moves)>0:
		    for inventory_move in inventory_moves:
			inventory_line = self.pool.get('stock.move').browse(cr,uid,inventory_move,context=context)
			res[line.id]['inventory_in_count'] +=inventory_line.product_qty
		
		#inventory out stock
		inventory_out_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','in',locs),('location_dest_id','=',inventory_loc),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		
		if len(inventory_out_moves)>0:
		    for inventory_out_move in inventory_out_moves:
			inventory_out_line = self.pool.get('stock.move').browse(cr,uid,inventory_out_move,context=context)
			res[line.id]['inventory_out_count'] +=inventory_out_line.product_qty
		
		#in stock
		stock_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','=',direct_origin),('location_dest_id','in',locs),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		if len(stock_moves)>0:
		    for stock in stock_moves:
			stock_line = self.pool.get('stock.move').browse(cr,uid,stock,context=context)
			res[line.id]['current_in_count'] +=stock_line.product_qty
			res[line.id]['current_in_money'] +=stock_line.price_unit*stock_line.product_qty
			     
		#back to supplier
		stock_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','in',locs),('location_dest_id','=',direct_origin),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		if len(stock_moves)>0:
		    for stock in stock_moves:
			stock_line = self.pool.get('stock.move').browse(cr,uid,stock,context=context)
			res[line.id]['current_in_count'] -=stock_line.product_qty
			res[line.id]['current_in_money'] -=stock_line.price_unit*stock_line.product_qty
			
			
		
		#back to stock
		stock_out_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','=',direct_dest),('location_dest_id','in',locs),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		
		if len(stock_out_moves)>0:
		    for stock in stock_out_moves:
		        stock_out_line = self.pool.get('stock.move').browse(cr,uid,stock,context=context)
		        res[line.id]['current_out_count'] -=stock_out_line.product_qty	
			
		#out stock	
		stock_out_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','in',locs),('location_dest_id','=',direct_dest),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		
		if len(stock_out_moves)>0:
		    for stock in stock_out_moves:
		        stock_out_line = self.pool.get('stock.move').browse(cr,uid,stock,context=context)
		        res[line.id]['current_out_count'] +=stock_out_line.product_qty
		        
		
		
		
		#the direct goods from supplier to customer
		direct_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','=',context['direct_origin']),('location_dest_id','=',context['direct_dest']),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
	    
		if len(direct_moves)>0:
		    for direct_line in direct_moves:
			direct_move = self.pool.get('stock.move').browse(cr,uid,direct_line,context=context)
			res[line.id]['current_in_count']+= direct_move.product_qty
			res[line.id]['current_in_money']+= direct_move.price_unit*direct_move.product_qty
			res[line.id]['current_out_count']+=direct_move.product_qty
			res[line.id]['current_out_money']+=direct_move.price_unit*direct_move.product_qty
			
		#compute the back goods
		direct_back_moves = self.pool.get('stock.move').search(cr,uid,[('location_id','=',context['direct_dest']),('location_dest_id','=',context['direct_origin']),('product_id','=',line.product_id.id),('state','=','done'),('date','>=',date_start),('date','<',date_stop)],context=context)
		
		if len(direct_back_moves)>0:
		    for direct_back_line in direct_back_moves:
			direct_back_move = self.pool.get('stock.move').browse(cr,uid,direct_back_line,context=context)			
			res[line.id]['current_in_count']-= direct_back_move.product_qty
			res[line.id]['current_in_money']-= direct_back_move.price_unit*direct_back_move.product_qty
			res[line.id]['current_out_count']-=direct_back_move.product_qty
			res[line.id]['current_out_money']-=direct_back_move.price_unit*direct_back_move.product_qty
		
		#average price
		if (res[line.id]["current_in_count"]+res[line.id]['init_remainder']) !=0:		  
		    average_price = (res[line.id]['init_money']+res[line.id]['current_in_money'])/(res[line.id]["current_in_count"]+res[line.id]['init_remainder'])
		
		res[line.id]['current_out_money'] = average_price*res[line.id]['current_out_count']
		res[line.id]['inventory_out_money']=average_price*res[line.id]['inventory_out_count']
		res[line.id]['inventory_in_money']=average_price*res[line.id]['inventory_in_count']
			    
		res[line.id]['end_remainder'] =res[line.id]['init_remainder']+ res[line.id]['current_in_count']-res[line.id]['current_out_count']+res[line.id]['inventory_in_count']-res[line.id]['inventory_out_count']
		res[line.id]['end_money'] =res[line.id]['init_money']+res[line.id]['current_in_money']-res[line.id]['current_out_money']+res[line.id]['inventory_in_money']-res[line.id]['inventory_out_money']
    	return res
    
    _columns={
        'product_id':fields.many2one('product.product',string='Product'),
        'category':fields.related('product_id','categ_id',type='many2one',relation='product.category',string='category',store=True),
        'init_remainder':fields.function(_get_current,multi="all",string='Init_Remainder',method=True,digits_compute=dp.get_precision('Account')),
        'init_money':fields.function(_get_current,multi="all",string="Init_Money",method=True,digits_compute=dp.get_precision('Account')),
        'current_in_count':fields.function(_get_current,multi='all',string='Current_In_Count',
	 method=True,digits_compute=dp.get_precision('Account')),
        'current_in_money':fields.function(_get_current,multi='sums',string='current_in_money',digits_compute=dp.get_precision('Account')
	),	'inventory_in_count':fields.function(_get_current,multi='sums',string='inventory_in_count',digits_compute=dp.get_precision('Account')),
	'inventory_in_money':fields.function(_get_current,multi='sums',string='inventory_in_money',digits_compute=dp.get_precision('Account')),
        'current_out_count':fields.function(_get_current,multi='sums',string='current_out',digits_compute=dp.get_precision('Account')
	),
        'current_out_money':fields.function(_get_current,multi='sums',string='current_out_money',digits_compute=dp.get_precision('Account')
	),	'inventory_out_count':fields.function(_get_current,multi='sums',string='inventory_out_count',digits_compute=dp.get_precision('Account')
	),
      'inventory_out_money':fields.function(_get_current,multi='sums',string='inventory_out_money',digits_compute=dp.get_precision('Account')
	),
        'end_remainder':fields.function(_get_current,multi='sums',string='end_remainder',digits_compute=dp.get_precision('Account')
	),
        'end_money':fields.function(_get_current,multi='sums',string='end_money',digits_compute=dp.get_precision('Account')
	),
        'period':fields.many2one('account.period','period'),
        'location':fields.many2one('stock.location','location'),
        'detail':fields.one2many('rainsoft.account.stock.detail','stock_id',string="detail"),

    }
    
    def action_carry_over(self,cr,uid,ids,context=None):      
	conditions = self.pool.get('rainsoft.account.stock').search(cr,uid,[],context=context)
	condition = conditions and max(conditions)
	
	stock = self.pool.get('rainsoft.account.stock').browse(cr,uid,condition,context=context)
	stock_lines = self.browse(cr,uid,ids)
	date_start = stock.period_id.date_start
	date_stop = stock.period_id.date_stop
	location = stock.location.id
	context['location']=location
	context['date_start'] = date_start
	context['date_stop'] = date_stop
	context['direct_origin'] = stock.direct_origin.id
	context['direct_dest'] = stock.direct_dest.id
	context['inventory']=stock.inventory.id
	
	#check if carry over is already existed
	carrys = self.pool.get('rainsoft.account.carryover').search(cr,uid,[('location','=',location),('period','=',stock.period_id.id)],context=context)
	if len(carrys)>0:
	  raise osv.except_osv(_('Error!'),_('Carry Over Already Exists!'))
	
	res = self._get_current(cr,uid,ids,'','',context=context)
	
	#create header
	line_id = self.pool.get('rainsoft.account.carryover').create(cr,uid,{'period':stock.period_id.id,'carry_date':datetime.now(),'location':location},context=context)
	
	for line in stock_lines:
	    val={
	      'carryover_id':line_id,
	      'product_id':line.product_id.id,
	      'init_remainder':res[line.id]["init_remainder"],
	      'init_money':res[line.id]["init_money"],
	      'current_in_count':res[line.id]["current_in_count"],
	      'current_in_money':res[line.id]["current_in_money"],
	      'current_out_count':res[line.id]["current_out_count"],
	      'current_out_money':res[line.id]["current_out_money"],
	      'end_remainder':res[line.id]["end_remainder"],
	      "end_money":res[line.id]["end_money"],
	      }
	    self.pool.get('rainsoft.account.carryover.line').create(cr,uid,val,context=context)
	    
    def action_stock_detail(self,cr,uid,ids,context=None):
	if context is None:
            context={}
        stock_detail = self.browse(cr,uid,ids[0])
                
        return {
            'name':u'产品库存明细',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'stock.move',
            'type':'ir.actions.act_window',
            'context':{
		'product_id':stock_detail.product_id.id,
            },
        }

rainsoft_account_stock_line()

class rainsoft_account_carry_over(osv.osv):
  _name="rainsoft.account.carryover"
  
  _columns={
      'period':fields.many2one('account.period',string="Period"),
      'carry_date':fields.datetime('carry_date'),
      'location':fields.many2one('stock.location','Location'),
      'carry_over_line':fields.one2many('rainsoft.account.carryover.line','carryover_id',string='Products'),
    }
rainsoft_account_carry_over()

class rainsoft_account_carry_over_line(osv.osv):
  _name="rainsoft.account.carryover.line"
  
  _columns={
      'carryover_id':fields.many2one('rainsoft.account.carryover',string='Carryover'),
      'category':fields.related('product_id','categ_id',type='many2one',relation='product.category',string='category',store=True),
      'product_id':fields.many2one('product.product',string='Product'),
      'init_remainder':fields.float("init_remainder",digits_compute=dp.get_precision('Account')),
      'init_money':fields.float("init_money",digits_compute=dp.get_precision('Account')),
      'current_in_count':fields.float("current_in_count",digits_compute=dp.get_precision('Account')),
      'current_in_money':fields.float("current_in_money",digits_compute=dp.get_precision('Account')),
      'inventory_in_count':fields.float('inventory_in_count',digits_compute=dp.get_precision('Account')),
      'inventory_in_money':fields.float('inventory_in_money',digits_compute=dp.get_precision('Account')),
      'current_out_count':fields.float("current_out_count",digits_compute=dp.get_precision('Account')),
      'current_out_money':fields.float("current_out_money",digits_compute=dp.get_precision('Account')),
      'inventory_out_count':fields.float("inventory_out_count",digits_compute=dp.get_precision('Account')),
      'inventory_out_money':fields.float("inventory_out_money",digits_compute=dp.get_precision('Account')),
      'end_remainder':fields.float("end_remainder",digits_compute=dp.get_precision('Account')),
      'end_money':fields.float("end_money",digits_compute=dp.get_precision('Account')),
    }
  
rainsoft_account_carry_over_line()

class rainsoft_account_stock_detail(osv.osv):
    _name="rainsoft.account.stock.detail"
    _columns={
	'stock_id':fields.many2one('rainsoft.account.stock.line'),
	'date':fields.datetime('Date'),
	'origin':fields.char('Origin'),
	'name':fields.char('name'),
	'unit':fields.many2one('product.uom',string='unit'),
	'in_price':fields.float('in_price',digits_compute=dp.get_precision('Account')),
	'in_count':fields.float('in_count',digits_compute=dp.get_precision('Account')),
	'in_money':fields.float('in_money',digits_compute=dp.get_precision('Account')),
	'out_price':fields.float('out_price',digits_compute=dp.get_precision('Account')),
	'out_count':fields.float('out_count',digits_compute=dp.get_precision('Account')),
	'out_money':fields.float('out_money',digits_compute=dp.get_precision('Account')),
	'sum_count':fields.float('sum_count',digits_compute=dp.get_precision('Account')),
	'sum_money':fields.float('sum_money',digits_compute=dp.get_precision('Account')),
      }
rainsoft_account_stock_detail()
