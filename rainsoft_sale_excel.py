# -*- coding:utf-8 -*-
from openerp.osv import osv,fields
import xlrd,base64

class rainsoft_sale_excel(osv.osv):
    _name='sale.order'
    _inherit='sale.order'

    _columns={
        'data':fields.binary('File')
    }

    def import_file(self,cr,uid,ids,context=None):
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(data))

        data = xlrd.open_workbook(fileobj)
        table = data.sheeets()[0]
        print table
rainsoft_sale_excel()
