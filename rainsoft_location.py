#-*- coding:utf-8 -*-
from openerp.osv import osv,fields

class rainsoft_location(osv.osv):
    _name="stock.inventory.line"
    _inherit="stock.inventory.line"


    def _get_first_location(self,cr,uid,ids,context=None):
        locations=self.pool.get('stock.location')
        first_location_id = locations.search(cr,uid,[('name','=',u'合格品库')],context=context)
        return first_location_id[0]

    _defaults={
        "location_id":_get_first_location,
    }
rainsoft_location()
