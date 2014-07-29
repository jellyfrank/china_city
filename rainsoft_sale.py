#-*- coding:utf-8 -*-

from openerp.osv import osv,fields
from openerp.tools.translate import _
from tempfile import TemporaryFile
import openerp.addons.decimal_precision as dp
import xlrd,base64
import logging

_logger = logging.getLogger(__name__)

class rainsoft_sale(osv.osv):
	_name="sale.order"
	_inherit="sale.order"

	def _get_product_model(self,cr,uid,context=None):		
		ids = self.pool.get('rainsoft.product.model').search(cr,uid,[])
		models = self.pool.get('rainsoft.product.model').read(cr,uid,ids)
		res=[]
		for model in models:
			res.append([model["id"],model["name"]])
		return res
	
	def _get_items_count(self,cr,uid,ids, name,arg,context=None):
		return {ids[0]:len(self.pool.get('sale.order.line').search(cr,uid,[('order_id','=',ids[0])],context=context))}
	      
	def _get_partner_credit_limit(self,cr,uid,ids,name,arg,context=None):
		sale = self.browse(cr,uid,ids[0])
		partner = self.pool.get('res.partner').browse(cr,uid,sale.partner_id.id,context=context)
		return {ids[0]:partner.credit_limit}
	def _get_partner_credit(self,cr,uid,ids,name,arg,context=None):
		sale = self.browse(cr,uid,ids[0])
		partner = self.pool.get('res.partner').browse(cr,uid,sale.partner_id.id,context=context)
		return {ids[0]:partner.credit}
	

	_columns={
			"product_model":fields.selection(_get_product_model),
			'data':fields.binary('File'),
			'item_count':fields.function(_get_items_count,string='Items  Count'),
			'credit_limit':fields.function(_get_partner_credit_limit,string='Credit Limit'),
			'credit':fields.function(_get_partner_credit,string='Credit'),
			'is_internal':fields.related('partner_id','is_internal',type="boolean",string='is internal'),
			
		}
	
	
	def import_file(self,cr,uid,ids,context=None):
			for wiz in self.browse(cr,uid,ids):
					if not wiz.data:continue
			excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.data))
			sheets = excel.sheets()
			sheet_names = self.pool.get('ir.config_parameter').get_param(cr,uid,"rainsoft.sms.sheet_name",context=context).split(';')
			for sh in sheets:
					if len([sh.name for s_name in sheet_names if sh.name==s_name]):
							lines=[]
							for row in range(4,sh.nrows-5):
									if sh.cell(row,1).value and sh.cell(row,5).value:
											product_no = int(str(sh.cell(row,1).value).strip().split('.')[0])
											product_amount=sh.cell(row,5).value
											product_price =sh.cell(row,6).value
											product_method=sh.cell(row,12).value
											if product_method == u'订单':
													product_method='make_to_order'
											else:
													product_method='make_to_stock'
				    
											products = self.pool.get('product.product').search(cr,uid,[('default_code','=',product_no)],context=context)
											_logger.info("importing product_no:"+str(product_no)+";products:"+str(products))
											if len(products)>0 and product_amount>0 and product_amount:
													product = self.pool.get('product.product').browse(cr,uid,products[0],context=context)
													line={
															'order_id':ids[0],
															'name':product.name,
															'product_id':product.id,
															'price_unit':product_price,
															'product_uom':product.uom_id.id,
															'product_uom_qty':product_amount,
												'type':product_method,
												'state':'draft',
															}
													self.pool.get('sale.order.line').create(cr,uid,line,context)
											else:
													_logger.info("product insert failed. No:"+str(product_no))
													_logger.info("probably caused by 1.len(products):"+str(len(products))+",2.product_amount:"+str(product_amount))
									else:
											_logger.info('row 1 and row 5 is invalid! Error Column 1:'+str(sh.cell(row,1).value)+";Error Column 2:"+str(sh.cell(row,5).value))
				    
	
	def onchange_product_model(self,cr,uid,ids,order_line,product_model,context=None):
		if not product_model:
			return {}
		product_model = self.pool.get('rainsoft.product.model').browse(cr,uid,product_model,context)
		if product_model:
			lines=[]
			for myproduct in product_model.model_id:
				
				product = self.pool.get('product.product').browse(cr,uid,myproduct.product_id.id,context)
				
				line={
					'name':product.name,
					'product_id':product.id,
					'price_unit':product.list_price,
					'product_uom':product.uom_id.id,
					'product_uom_qty':myproduct.amount,
                    'type':product.procure_method,
                    'state':'draft',
					}
				lines.append(line) 
			return {'value':{'order_line':lines}}
		return {}

	def del_products(self,cr,uid,ids,context=None):
		order = self.browse(cr,uid,ids[0],context=context)
		if order.order_line:
			ids = [line.id for line in order.order_line if line.product_uom_qty==0]
			self.pool.get('sale.order.line').unlink(cr,uid,ids)
		
		
	def action_button_confirm(self, cr, uid, ids, context=None):
		sale_order = self.browse(cr,uid,ids[0])	
		#验证信用额度
		order = self.pool.get('sale.order').browse(cr, uid, ids[0],context=context)	
		part = self.pool.get('res.partner').browse(cr, uid, order.partner_id.id, context=context)
		if part.credit_limit - part.credit - order.amount_total >=0: 
		    #写入对比表头
		    value = {
			"name":sale_order.name,
			"partner_id":sale_order.partner_id.id,
			"sale_order_id":sale_order.id,
			#"sale_order_line":lines,
			"state":"new",
		    }
		    order_id = self.pool.get('rainsoft.saleout').create(cr,uid,value,context=context)
		    #写入产品明细
		    for line in sale_order.order_line:
			#检查产品是否为组合产品
			mrp = self.pool.get('mrp.bom').search(cr,uid,[('product_id','=',line.product_id.id)],context=context)
			if len(mrp)>0:
			    #先写入组合产品
			    val = {
				    "order_id":order_id,
				    "product_id":line.product_id.id,
				    "price":line.price_unit,
				    "amount":line.product_uom_qty,
				    "unit":line.product_uom.id,
				}
			    self.pool.get('rainsoft.saleout.line').create(cr,uid,val,context=None)
			    #在写入组合产品明细
			    bom = self.pool.get('mrp.bom').browse(cr,uid,mrp[0],context=context)
			    for bom_line in bom.bom_lines:
				val = {
				    "order_id":order_id,
				    "mrp_product_id":line.product_id.id,
				    "product_id":bom_line.product_id.id,
				    "price":0,
				    "amount":line.product_uom_qty*bom_line.product_qty,
				    "unit":bom_line.product_uom.id,
				}
				self.pool.get('rainsoft.saleout.line').create(cr,uid,val,context=None)
			else:			
			    val = {
				"order_id":order_id,
				"product_id":line.product_id.id,
				"price":line.price_unit,
				"amount":line.product_uom_qty,
				"unit":line.product_uom.id,
				}
			    self.pool.get('rainsoft.saleout.line').create(cr,uid,val,context=None)
		    
		    return super(rainsoft_sale,self).action_button_confirm(cr, uid, ids, context=context)
		else:
		     raise osv.except_osv(_('Error!'),_('Not have enough money.'))

	def onchange_partner_id(self, cr, uid, ids, part, context=None):
		if not part:
		      return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

		part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
		addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
		pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
		payment_term = part.property_payment_term and part.property_payment_term.id or False
		fiscal_position = part.property_account_position and part.property_account_position.id or False
		dedicated_salesman = part.user_id and part.user_id.id or uid
		val = {
		    'partner_invoice_id': addr['invoice'],
		    'partner_shipping_id': addr['delivery'],
		    'payment_term': payment_term,
		    'fiscal_position': fiscal_position,
		    'user_id': dedicated_salesman,
		    'credit':part.credit,
		    'credit_limit':part.credit_limit,
		}
		if pricelist:
		    val['pricelist_id'] = pricelist
		return {'value': val}
	
	def send_sms(self,cr,uid,ids,context=None):
	    mod_obj=self.pool.get('ir.model.data')
	    form_res=mod_obj.get_object_reference(cr,uid,'Rainsoft_Xiangjie','rainsoft_sms_form_view')
	    form_id = form_res and form_res[1] or False
	    value =  {
		    'name':_('Send Text Message'),
		    'view_mode': 'form',
		    'view_id': False,
		    'views': [(form_id,'form')],
		    'view_type': 'form',		    
		    'res_model': 'rainsoft.sms', # object name
		    'type': 'ir.actions.act_window',
		    'target': 'new', # if you want to open the form in new tab
		    }
	    return value

rainsoft_sale()

class rainsoft_sale_line(osv.osv):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    def _categ_name_fun(self, cr, uid, ids, field_name, arg, context):

        res = {}
        lines = self.browse(cr, uid, ids)
        for line in lines:
            res[line.id] = {
                'categ_name': None
            }

            category = self.pool.get('product.category').browse(cr, uid, line.product_id.categ_id.id, context=None)
            res[line.id]['categ_name'] = category.name
        return res


    _columns = {
        'date': fields.related('order_id', 'date_order', type='date', relation='sale.order', string='date'),
        'categ_id': fields.related('product_id', 'categ_id', type='many2one', relation='product.category', string=u'分类',
                                   store=True),
        'categ_name': fields.function(_categ_name_fun, type='char', multi='cate', method=True, string=u'分类'),
    }
rainsoft_sale_line()
