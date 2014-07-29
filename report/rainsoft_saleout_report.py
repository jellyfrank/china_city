# -*- coding:utf-8 -*-

from report import report_sxw
from tools.translate import _
import rml_parse
import time

class rainsoft_saleout_report(rml_parse.rml_parse):
    def __init__(self,cr,uid,name,context):
	super(rainsoft_saleout_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_partner':self._get_partner,
            'get_sale_order':self._get_sale_order,
            'get_product_name':self._get_product_name,
            'get_mrp_product_name':self._get_mrp_product_name,
            'get_uom':self._get_uom,
        })
	
    def _get_partner(self,partner_id):
	partner = self.pool.get('res.partner').browse(self.cr,self.uid,partner_id.id,None)
	return partner.name
      
    def _get_sale_order(self,order_id):
	sale_order = self.pool.get('sale.order').browse(self.cr,self.uid,order_id.id,None)
	return sale_order.name
      
    def _get_product_name(self,product_id,mrp_product_id):
	if mrp_product_id:
	    return ''
	if product_id:
	    product = self.pool.get('product.product').browse(self.cr,self.uid,product_id.id,None)
	    return product.name
    def _get_mrp_product_name(self,product_id,mrp_product_id):
	if not mrp_product_id:
	    return ''
	if product_id:
	    product = self.pool.get('product.product').browse(self.cr,self.uid,product_id.id,None)
	    return product.name
	  
    def _get_uom(self,uom_id):
	if uom_id:
	    uom = self.pool.get('product.uom').browse(self.cr,self.uid,uom_id.id,None)
	    return uom.name

report_sxw.report_sxw('report.rainsoft.saleout', 'rainsoft.saleout',   \
                      'Rainsoft_Xiangjie/report/rainsoft_saleout.rml',  \
                      parser=rainsoft_saleout_report,header=False)


