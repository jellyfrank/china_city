# -*- utf-8 -*-

from openerp.osv import osv,fields

class rainsoft_sale_stock(osv.osv):
    _name="sale.order"
    _inherit="sale.order"
    
    #def test_state(self, cr, uid, ids, mode, *args):
        #assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        #finished = True
        #canceled = False
        #write_done_ids = []
        #write_cancel_ids = []
        #for order in self.browse(cr, uid, ids, context={}):
            #for line in order.order_line:
                #if (not line.procurement_id) or (line.procurement_id.state=='done'):
                    #if line.state != 'done':
                        #write_done_ids.append(line.id)
                #else:
		    #mrp = self.pool.get('mrp.bom').search(cr,uid,[('product_id','=',line.product_id.id),('bom_id','=',False),('type','=','phantom')],context={})
		    #if len(mrp):
			#for move_line in line.move_ids:
			    #move_line.product_id.id,line.product_id.id,move_line.state
			    #if move_line.product_id.id==line.product_id.id:
			      #continue
			    
			    #if move_line.product_id.id != line.product_id.id and move_line.state!='done':
				#finished=False
		    #else:
			#finished = False
                #if line.procurement_id:
                    #if (line.procurement_id.state == 'cancel'):
                        #canceled = True
                        #if line.state != 'exception':
                            #write_cancel_ids.append(line.id)
        #if write_done_ids:
            #self.pool.get('sale.order.line').write(cr, uid, write_done_ids, {'state': 'done'})
        #if write_cancel_ids:
            #self.pool.get('sale.order.line').write(cr, uid, write_cancel_ids, {'state': 'exception'})

        #if mode == 'finished':
            #return finished
        #elif mode == 'canceled':
            #return canceled
    
rainsoft_sale_stock()
    
