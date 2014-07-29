# -*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_brand(osv.osv):
    _name="rainsoft.brand"

    _columns={
        'name':fields.char('Brand Name'),
    }
rainsoft_brand()
