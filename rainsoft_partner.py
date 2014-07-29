#-*- coding:utf-8 -*-

from openerp.osv import fields,osv,orm
from rainsoft_message import message

class rainsoft_partner(osv.osv):
	_name="res.partner"
	_inherit="res.partner"
	_description="add QQ number."
	
	def _display_address(self, cr, uid, address, without_company=False, context=None):

	    '''
	    The purpose of this function is to build and return an address formatted accordingly to the
	    standards of the country where it belongs.

	    :param address: browse record of the res.partner to format
	    :returns: the address formatted in a display that fit its country habits (or the default ones
		if not country is specified)
	    :rtype: string
	    '''

	    # get the information that will be injected into the display format
	    # get the address format
	    address_format = address.country_id and address.country_id.address_format or \
		  "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
	    args = {
		'state_code': address.state_id and address.state_id.code or '',
		'state_name': address.state_id and address.state_id.name or '',
		'country_code': address.country_id and address.country_id.code or '',
		'country_name': address.country_id and address.country_id.name or '',
		'company_name': address.parent_id and address.parent_id.name or '',
	    }
	    for field in self._address_fields(cr, uid, context=context):
		args[field] = getattr(address, field) or ''
	    if without_company:
		args['company_name'] = ''
	    elif address.parent_id:
		address_format = '%(company_name)s\n' + address_format
	    args['city']=address.city.name
	    return address_format % args	
	
	_columns={
			"QQ":fields.char("QQ",size=16),
			"contract_end_date":fields.date("contract_end_date",select=1),
			"icontact":fields.char('Contact'),
			"city":fields.many2one('rainsoft.city','City'),
			"district":fields.many2one('rainsoft.district','District'),
			"is_internal":fields.boolean('Is internal department',help="check if it's a internal department"),
            "brand":fields.many2one('rainsoft.brand','Customer Brand'),
			}
	_order="state_id,city"
	#_sql_constraints=[
	#		('rainsoft_partner','unique(ref)',"partner's no must be unique"),
	#		]
	def _check_supplier_company_unique(self,cr,uid,ids,context=None):
		for partner in self.browse(cr,uid,ids,context):
			if partner.supplier and partner.is_company:
				suppliers = self.pool.get('res.partner').search(cr,uid,[('name','=',partner.name),('supplier','=',True),('is_company','=',True)])
				for supplier in suppliers:
					if supplier!=partner.id:			
						return False
		return True


	def _check_customer_company_unique(self,cr,uid,ids,context=None):
		for partner in self.browse(cr,uid,ids,context):
			if partner.customer and partner.is_company:
				customers = self.pool.get('res.partner').search(cr,uid,[('name','=',partner.name),('customer','=',True),('is_company','=',True)])
				for customer in customers:
					if customer!=partner.id:
						return False
		return True

	def _check_supplier_person_unique(self,cr,uid,ids,context=None):
		for partner in self.browse(cr,uid,ids,context):
			if partner.supplier and partner.is_company==False:
				suppliers = self.pool.get('res.partner').search(cr,uid,[('name','=',partner.name),('supplier','=',True),('is_company','=',False)])
				for supplier in suppliers:
					if supplier!=partner.id:
						return False
		return True

	def _check_customer_person_unique(self,cr,uid,ids,context=None):
		for partner in self.browse(cr,uid,ids,context):
			if partner.customer and partner.is_company==False:
				customers = self.pool.get('res.partner').search(cr,uid,[('name','=',partner.name),('customer','=',True),('is_company','=',False)])
				for customer in customers:
					if customer!=partner.id:
						return False
		return True
	def _check_partner_ref(self,cr,uid,ids,context=None):
		for partner in self.browse(cr,uid,ids,context):
			if partner.supplier or partner.customer:
			    partners = self.pool.get('res.partner').search(cr,uid,[('ref','=',partner.ref),('is_company','=',True)])
			    for p in partners:
				if p != partner.id:
				  return False
		return True
        
	def onchange_city(self,cr,uid,ids,city,context=None):
	    if city:
		return {'value':{'district':''}}
	    return {}
	  
	def onchange_state(self, cr, uid, ids, state_id, context=None):
	    if state_id:
		country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
		return {'value':{'country_id':country_id,'city':'','district':''}}
	    return {}


	_constraints=[
			(_check_supplier_company_unique,'supplier already exists!',['name']),
			(_check_customer_company_unique,'customer already exists!',['name']),
			(_check_supplier_person_unique,'supplier person already exists!',['name']),
			(_check_customer_person_unique,'customer person already exists!',['name']),
			(_check_partner_ref,u'已经存在的编号！',['ref']),
			]
	def create(self,cr,uid,value,context=None):
	    if value.has_key('mobile'):
		mobile = value['mobile']
		if mobile.isdigit():
		    return super(rainsoft_partner,self).create(cr,uid,value,context=context)
		else:
		    raise osv.except_osv(u'手机号格式错误!',message.get_joke())
	    else:
		return super(rainsoft_partner,self).create(cr,uid,value,context=context)
		  
	def write(self,cr,uid,ids,values,context=None):
	    if values.has_key('mobile'):
		mobile = values['mobile']
		if mobile.isdigit():
		    return super(rainsoft_partner,self).write(cr,uid,ids,values)
		else:
		    raise osv.except_osv(u'手机号格式错误!',message.get_joke())
	    else:
		return super(rainsoft_partner,self).write(cr,uid,ids,values)
	
rainsoft_partner()


