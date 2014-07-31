# coding:utf-8

from openerp.osv import osv,fields

class hm_users(osv.osv):
		_inherit='res.users'

		_columns={
						'city':fields.many2one('hm.city','city'),
						}
