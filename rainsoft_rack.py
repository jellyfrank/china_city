#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_rack(osv.osv):
    _name="rainsoft.rack"
    _description="Rack Manger"

    _columns={
            "name":fields.char('Rack',size=16,select=True),
    }

    _sql_constraints=[
        ('name','UNIQUE(name)','Name must be unique!')
    ]

rainsoft_rack()
