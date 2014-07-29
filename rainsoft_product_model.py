# -*- coding:utf-8 -*-
from openerp.osv import osv,fields
from openerp.tools.translate import _


class rainsoft_product_model(osv.osv):
	_name="rainsoft.product.model"
	_columns={
			"name":fields.char('Model Name',size=16,required=True),
			"model_id":fields.one2many('rainsoft.myproduct','myproduct_id','Products'),
			}
	_sql_constraints={
			('rainsoft_product_model_uniq','unique(name)','product model name can not be same!')
			}
		
	def create(self,cr,uid,values,context=None):
	    if values.has_key('model_id'):
		  if len(values['model_id'])>0:
		      pids = [x[2]["product_id"] for x in values['model_id'] if x[2]] 
		      print pids
		      res = list(set([ p for p in pids if pids.count(p)>1]))
		      if len(res) !=0:
			    raise osv.except_osv(_('warning!'),_('products can not be repetitive!'))
		  else:
		      raise osv.except_osv(_('Warning!'),_('product model can not be empty!'))
	    return super(rainsoft_product_model,self).create(cr,uid,values,context=context)
	      
	      
	def write(self,cr,uid,ids,values,context=None):
	    print values
	    if values.has_key('model_id'):
		  if len(values['model_id'])>0:
		      for product in values['model_id']:
			  if product[2]:
			    pids = [x[2]["product_id"] for x in values['model_id'] if x[2]] 
			    print pids
			    res = list(set([ p for p in pids if pids.count(p)>1]))
			    if len(res) !=0:
				  raise osv.except_osv(_('warning!'),_('products can not be repetitive!'))
		  else:
		      raise osv.except_osv(_('Warning!'),_('product model can not be empty!'))
	    return super(rainsoft_product_model,self).write(cr,uid,ids,values,context=context)

rainsoft_product_model()

class rainsoft_myproduct(osv.osv):
	_name="rainsoft.myproduct"
	_columns={
			"myproduct_id":fields.many2one('rainsoft.product.model','id'),
			"product_id":fields.many2one('product.product','products'),
            "amount":fields.integer('amount'),
			}


rainsoft_myproduct()

