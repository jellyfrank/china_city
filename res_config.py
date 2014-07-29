# -*- conding:utf-9 -*-

from openerp.osv import osv,fields

class rainsoft_sms_config(osv.osv):
    _name='rainsoft.config.settings'
    _inherit='res.config.settings'

    _columns={
        'user_id':fields.char('User ID',Help='user id that service provider gives to you'),
        'send_address':fields.char('Interface Address',Help='The address that your sms send to'),
        'user_name':fields.char('Account',Help='The username that can pass interface'),
        'pass_word':fields.char('Password',),
        'appendix':fields.char('End Text',Help="The text that append to every message's end"),
        'model_price':fields.boolean("Allow Import Price From Excel File"),
		'sheet_name':fields.text('Sheet Names'),
    }

    def get_default_val(self,cr,uid,fields,context=None):
			user_id = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.userid",context=context),
			send_address = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.address",context=context)
			username = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.username",context=context)
			password = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.password",context=context)
			appendix = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.appendix",context=context)
			model_price = self.pool.get('ir.config_parameter').get_param(cr,uid,"rainsoft.sms.model_price",context=context)
			sheet_names = self.pool.get('ir.config_parameter').get_param(cr,uid,"rainsoft.sms.sheet_name",context=context)
			res= {"user_id":user_id,"send_address":send_address,"user_name":username,"pass_word":password,"appendix":appendix,"model_price":model_price,"sheet_name":sheet_names}
			return res

    def set_default_val(self,cr,uid,ids,context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr,uid,ids,context=context):
            config_parameters.set_param(cr,uid,'rainsoft.sms.userid',record.user_id),
            config_parameters.set_param(cr,uid,'rainsoft.sms.address',record.send_address,context=context)
            config_parameters.set_param(cr,uid,'rainsoft.sms.username',record.user_name,context=context)
            config_parameters.set_param(cr,uid,'rainsoft.sms.password',record.pass_word,context=context)
            config_parameters.set_param(cr,uid,'rainsoft.sms.appendix',record.appendix,context=context)
            config_parameters.set_param(cr,uid,'rainsoft.sms.model_price',record.model_price,context=context)
            config_parameters.set_param(cr,uid,'rainsoft.sms.sheet_name',record.sheet_name,context=context)

            
    def default_get(self,cr,uid,fields,context=None):
        res = super(rainsoft_sms_config, self).default_get(cr, uid, fields, context)
        return res

rainsoft_sms_config()
