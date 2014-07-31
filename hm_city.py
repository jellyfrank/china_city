#coding:utf-8

from openerp.osv import osv,fields

class hm_city(osv.osv):
		_name='hm.city'

		_columns={
						'name':fields.char('name'),
						'state':fields.many2one('res.country.state','state'),
						}


class hm_district(osv.osv):
		_name="hm.district"

		_columns={
						'name':fields.char('name'),
						'city':fields.many2one('hm.city',"city"),
						}
