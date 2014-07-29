#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_city(osv.osv):
    _name='rainsoft.city'
    _description='City'

    _columns={
        'name':fields.char('City'),
        'state':fields.many2one('res.country.state','State'),
    }
rainsoft_city()

class rainsoft_district(osv.osv):
    _name='rainsoft.district'
    _description='District'
    

    _columns={
        'name':fields.char('District'),
        'city':fields.many2one('rainsoft.city','City'),
        }

rainsoft_district()
