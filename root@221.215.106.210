#-*- coding:utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_payment(osv.osv):
    _name="payment.line"
    _inherit="payment.line"

    _order="partner_id"

    def _get_info_partner(self,cr, uid, partner_record, context=None):
      if not partner_record:
	  return False
      st = partner_record.street or ''
      st1 = partner_record.street2 or ''
      zip = partner_record.zip or ''
      city = partner_record.city or  ''
      zip_city = zip + ' ' + city.name
      cntry = partner_record.country_id and partner_record.country_id.name or ''
      return partner_record.name + "\n" + st + " " + st1 + "\n" + zip_city + "\n" +cntry
      
rainsoft_payment()
