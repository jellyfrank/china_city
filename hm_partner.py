# coding:utf-8


from openerp.osv import osv,fields

class hm_partner(osv.osv):
		_inherit='res.partner'

		_columns={
						'city':fields.many2one('hm.city','city'),
						'district':fields.many2one('hm.district','district'),
						}
