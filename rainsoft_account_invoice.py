# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class rainsoft_account_invoice(osv.osv):
    _name='account.invoice'
    _inherit = 'account.invoice'
    
    _columns={	'p_comment':fields.related('partner_id','comment',type='text',relation='res.partner',string='p_comment'),
      }
rainsoft_account_invoice()

   