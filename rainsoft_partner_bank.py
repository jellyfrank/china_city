#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_bank(osv.osv):
    _name='res.partner.bank'
    _inherit='res.partner.bank'

    _columns={
        "city":fields.many2one('rainsoft.city','City'),
    }
rainsoft_bank()
