#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_account_report_partner_ledger(osv.osv):
    _name="account.partner.ledger"
    _inherit="account.partner.ledger"

    _columns={
        'partner_id':fields.many2one('res.partner',string="Partner"),
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update({'partner_id':self.browse(cr, uid, ids[0], context=context).partner_id.id})
        data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'filter', 'page_split', 'amount_currency'])[0])
        if data['form']['page_split']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.third_party_ledger',
                'datas': data,
        }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.third_party_ledger_other',
                'datas': data,
        }

rainsoft_account_report_partner_ledger()
