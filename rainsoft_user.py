#-*- coding:utf-8 -*-

from openerp.osv import osv,fields
from openerp.tools.translate import _

class rainsoft_user(osv.osv):
    _name='res.groups'
    _inherit='res.groups'

    def copy(self, cr, uid, id, default=None, context=None):
        group_name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({'name': _('%s (copy)') % group_name})
        return super(rainsoft_user, self).copy(cr, uid, id, default=default, context=context)

rainsoft_user()
        
