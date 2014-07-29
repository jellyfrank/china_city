#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_crm_lead(osv.osv):
    _name="crm.lead"
    _inherit="crm.lead"

    _columns={
        "city":fields.many2one('rainsoft.city','City'),
    }
rainsoft_crm_lead()
