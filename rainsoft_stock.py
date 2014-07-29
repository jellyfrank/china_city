# -*-coding:utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class rainsoft_stock(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def do_partial_rpc(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                  like partner_id, partner_id, delivery_date,
                  delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % (move.id), {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty,
                                                            move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                                         move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                                           product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id]) \
                                             + (new_price * qty)) / (product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                       {'price_unit': product_price,
                                        'price_currency_id': product_currency})

                        product_avail[product.id] += qty

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id],
                               {'name': sequence_obj.get(cr, uid,
                                                         'stock.picking.%s' % (pick.type)),
                               })
                    new_picking = self.copy(cr, uid, pick.id,
                                            {
                                            'name': new_picking_name,
                                            'move_lines': [],
                                            'state': 'draft',
                                            })
                if product_qty != 0:
                    defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                    'picking_id': new_picking,
                    'state': 'assigned',
                    'move_dest_id': False,
                    'price_unit': move.price_unit,
                    'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                               {
                               'product_qty': move.product_qty - partial_qty[move.id],
                               'product_uos_qty': move.product_qty - partial_qty[move.id],  # TODO: put correct uos_qty
                               'prodlot_id': False,
                               'tracking_id': False,
                               })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                'product_qty': product_qty,
                'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = pick.id
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                self.message_post(cr, uid, new_picking,
                                  body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name),
                                  context=context)
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[str(pick.id)] = {'delivered_picking': delivered_pack.id or False}
        return res


class rainsoft_stock_inventory_line(osv.osv):
    _name = 'stock.inventory.line'
    _inherit = 'stock.inventory.line'

    _columns = {'product_name': fields.related('product_id', 'name', type='many2one', relation='product.product',
                                               string='product_name'),
    }

    # _order='product_name'


rainsoft_stock_inventory_line()


class rainsoft_stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    def _get_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        moves = self.browse(cr, uid, ids)
        for move in moves:
            res[move.id] = move.product_qty * move.price_unit
        return res


    _columns = {
    'amount': fields.function(_get_amount, 'Amount'),
    'product_name':fields.related('product_id','name_template', type='char', relation='product.product',string=u'产品名', store=True),
    }


rainsoft_stock_move()