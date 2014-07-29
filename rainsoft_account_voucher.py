# -*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_voucher(osv.osv):
    _name="account.voucher"
    _inherit="account.voucher"

    _columns={
        'p_comment':fields.related('partner_id','comment',type='text',relation='res.partner',string="p_comment"),
    }

rainsoft_voucher()
