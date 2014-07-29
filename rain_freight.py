# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class rain_freight(osv.osv):
    _name = 'rain.freight'

    _columns = {
        'from_date': fields.date(u'开始时间', requried=True),
        'to_date': fields.date(u'结束时间', requried=True),
        'preight_product_id': fields.many2one('product.product', u'运费产品',requried=True),
    }

    def action_query(self, cr, uid, ids, context=None):
        """
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        :description: 进行查询工作
        """
        if context is None:
            context = {}

        from_date = self.browse(cr, uid, ids[0]).from_date
        to_date = self.browse(cr, uid, ids[0]).to_date
        preight_product_id = self.browse(cr, uid, ids[0]).preight_product_id.id



         #清空表
        rain_freight_lines = self.pool.get('rain.freight.line').search(cr, uid, [], context=context)
        self.pool.get('rain.freight.line').unlink(cr, uid, rain_freight_lines)
        #获取这段时间的 订单
        sale_orders = self.pool.get('sale.order').search(cr, uid, [('date_confirm', '>=', from_date),
                                                                   ('date_confirm', '<=', to_date),
                                                                ('state', '=', 'done'), ],
                                                         context=context)
        #搜索订单（含有preight_product_id)的订单
        for sale_order in sale_orders:
            obj_order = self.pool.get('sale.order').browse(cr, uid, sale_order, context=context)
            for order_line in obj_order.order_line:
                #判断是否是 费用产品
                if order_line.product_id.id == preight_product_id:
                    self.pool.get('rain.freight.line').create(cr, uid, {'order_id': obj_order.id},
                                                                 context=context)

        return {
            'name': u'运费统计' + '(' + from_date + u'到' + to_date + ')',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'rain.freight.line',
            'type': 'ir.actions.act_window',
            'context': {
                'from_date': from_date,
                'to_date': to_date,
                'preight_product_id': preight_product_id,
            },
            'limit': 10000,
        }

rain_freight()


class rain_freight_line(osv.osv):
    _name = "rain.freight.line"

    def _address(self, cr, uid, ids, field_name, arg, context=None):
        """
        :dec ： 拼接地区（pro，city，street）
        :param cr:
        :param uid:
        :param ids:
        :param field_name:
        :param arg:
        :param context:
        :return:
        """
        res = {}
        lines = self.browse(cr, uid, ids)

        for line in lines:
            res[line.id] = {
                'address' : None
            }
            #省
            state = line.order_id.partner_id.state_id.name
            #城市修改后
            city = line.order_id.partner_id.city.name
            #city = line.order_id.partner_id.city
            #区
            district = line.order_id.partner_id.district.name
            #街道
            street = line.order_id.partner_id.street
            #street2 = line.order_id.partner_id.street2

            res[line.id]['address'] = state + city + district +street

            #res[line.id]['address'] = state + city  +street

        return res

    def _freigth_abs(self, cr, uid, ids, field_name, arg, context=None):
        """
        :descript: 将费用取绝对值
        :param cr:
        :param uid:
        :param ids:
        :param field_name:
        :param arg:
        :param context:
        :return:
        """
        res = {}
        lines = self.browse(cr, uid, ids)

        for line in lines:
            res[line.id] = {
                'freight_total' : 0.0
            }
            res[line.id]['freight_total'] = abs(line.order_id.amount_total)
        return res


    _columns = {
        'order_id':fields.many2one('sale.order','Sale'),
        'partner_id': fields.related('order_id', 'partner_id', type='many2one', relation='res.partner',string='Customer',store=True),
        'address':fields.function(_address, multi='adr',type="char",method=True,string='地址',store=True),
        'icontact':fields.related('partner_id', 'icontact' ,string="Contact",type='char'),
         'mobile':fields.related('partner_id', 'mobile', string='Mobile', type='char'),
         'freight_total':fields.function(_freigth_abs,  multi='sums', digits_compute=dp.get_precision('Account'),
                                  method=True,type='float', string='Total'),
         'date_order': fields.related('order_id', 'date_order',string='创建日期',type='date'),
         'date_confirm': fields.related('order_id', 'date_confirm',string='确定日期',type='date'),
    }

rain_freight_line()