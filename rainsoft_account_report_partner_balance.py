#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_account_report_balance(osv.osv):
    _name="account.partner.balance"
    _inherit="account.partner.balance"

    _columns={
        'partner_id':fields.many2one('res.partner',string="Partner"),
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_partner'])[0])
        data['form'].update({'partner_id':self.browse(cr, uid, ids[0], context=context).partner_id.id})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.partner.balance',
            'datas': data,
    }
rainsoft_account_report_balance()
