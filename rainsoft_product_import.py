# -*- coding:utf-8 -*-
from openerp.osv import osv,fields
import xlrd,base64

class rainsoft_product_import(osv.osv):
    _name='rainsoft.product.import'
    
    _columns={
            'file':fields.binary('xls file'),
            }

    def btn_import(self,cr,uid,ids,context=None):
        for wiz in self.browse(cr,uid,ids):
            if not wiz.file:continue

            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.file))
            sheets = excel.sheets()
            for sh in sheets:
                if sh.name==u"青岛工厂" or sh.name==u'哈尔滨工厂' or sh.name==u'济南工厂':
                    lines=[]
                    cate = 0
                    for row in range(3,sh.nrows):
                        if sh.cell(row,1).value:
                            if sh.cell(row,0).value:
                                cate = sh.cell(row,0).value
                            cate_ids = self.pool.get('product.category').search(cr,uid,[('name','=',cate)],context=context)
                            print cate_ids
                            if len(cate_ids):
                                pro_uoms = self.pool.get('product.uom').search(cr,uid,[('name','=',sh.cell(row,5).value)],context=context)
                                if sh.cell(row,6).value=='MTO':
                                    product_method='make_to_order'
                                else:
                                    product_method='make_to_stock'

                                if sh.cell(row,7).value==u'购买':
                                    supplier_method='buy'
                                else:
                                    supplier_method='produce'

                                if sh.cell(row,8).value==u'标准价格':
                                    cost_method='standard'
                                else:
                                    cost_method='average'
                                if sh.cell(row,9).value==u'实时':
                                    valuation='real_time'
                                else:
                                    valuation='manual_periodic'
                                line={
                                    'name':sh.cell(row,2).value,
                                    'categ_id':cate_ids[0],
                                    'uom_id':pro_uoms[0],
                                    'uom_po_id':pro_uoms[0],
                                    'default_code':str(sh.cell(row,1).value).split('.')[0],
                                    'procure_method':product_method,
                                    'supply_method':supplier_method,
                                    'cost_method':cost_method,
                                    'valuation':valuation,
                                    }
                                self.pool.get('product.product').create(cr,uid,line,context=context)


rainsoft_product_import()

