# -*- coding:utf-8 -*-

from openerp.osv import osv,fields
from xml.etree import ElementTree
import httplib,urllib

class rainsoft_sms(osv.osv):
    _name='rainsoft.sms'   
	  
    _columns={
	'partner_id':fields.many2one('res.partner',string='partner'),
        'mobile':fields.char('Mobile'),
        'content':fields.text('Contents'),
        'status':fields.char('Status'),
        'message':fields.char('Message'),
        'template_id':fields.many2one('rainsoft.sms.template',string='template'),
    }    
    
    def _get_mobile(self,cr,uid,context=None):
	mobile=''
	if context.get('active_id'):
	    if context.get('active_model')=="sale.order":
		mobile = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id'),context=context).partner_id.mobile
	    if context.get('active_model')=="purchase.order":
		mobile = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id'),context=context).client.mobile
	return mobile
	  
    def _get_partner(self,cr,uid,context=None):
	client_id=''
	if context.get('active_model')=='sale.order':
	    active_model =context.get('active_model')
	    client_id = self.pool.get(active_model).browse(cr,uid,context.get('active_id'),context=context).partner_id.id
	if context.get('active_model')=='purchase.order':
	    active_model =context.get('active_model')
	    client_id = self.pool.get(active_model).browse(cr,uid,context.get('active_id'),context=context).client.id
	return client_id
    
    _defaults={
	'mobile':_get_mobile,
	'partner_id':_get_partner,
      }
    
    def on_change_template(self,cr,uid,ids,template_id,context=None):
	res={}	
	if template_id and context.get('active_model'):	
	    if context.get('active_model')=='sale.order':
		partner_name = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id')).partner_id.name
	    if context.get('active_model')=='purchase.order':
		client = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id')).client
		partner_name = client.name
	    template = self.pool.get('rainsoft.sms.template').browse(cr,uid,template_id,context=context)
	    content=template.content.replace('{shop}',partner_name)
	    val={
	      'content':content
	      }
	    res["value"]=val
	return res

    def send_sms(self,cr,uid,ids,context=None):
        if context==None:
            context={}

        message = self.pool.get('rainsoft.sms').browse(cr,uid,ids[0],context=context)
        rs_send_service = self.pool.get('rainsoft.sendsms')
        res = rs_send_service.send(cr,uid,ids,message.mobile,message.content,context=context)
        val={
	    'status':res['status'],
	    'message':res['message'],
	  }
	return self.pool.get('rainsoft.sms').write(cr,uid,message.id,val,context=context)
     
    def fields_view_get(self,cr,uid,view_id=None,view_type='form',context={},tool_bar=False):
	print 'b'
	result = super(rainsoft_sms, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=tool_bar)
	###your modification in the view
	###result['fields'] will give you the fields. modify it if needed
	xml = """
	 <form string="Sms" version="7.0">
                    <sheet>
			  <group>
			    <label for="partner_id" string="Send To" />		  
			    <h1><field name="partner_id" readonly='1' string="Partner"/></h1>
			  </group>
			  <group>
                            <field name="mobile" string="mobile"  context="{'mobile':active_id}"/>			    
                            <field name="content" string="content"/>
			    <field name="template_id" string="template" on_change="on_change_template(template_id,context)" widget="selection" context="{'mobile':active_id}"/>
			  </group>
                        <!--<group>
			  <div>
			      <field name="status" string="Status" class="oe_view_only"/>
			      <field name="message" string="Message" class="oe_view_only"/>
			  </div>
			  </group>-->
                        <group>
                            <button string="Send" name="send_sms" type="object" class="oe_view_only"/>
                        </group>
                    </sheet>
                    </form>
	"""
	if view_type=="form":
	  result['arch']=xml
	###result['arch'] will give you the xml architecture. modify it if needed
	return result
    def read(self,cr,uid,ids,fields=None,context=None):
	print 'a'
	return super(rainsoft_sms,self).read(cr,uid,ids,fields=fields,context=context)
        
rainsoft_sms()

class rainsoft_sms_template(osv.osv):
    _name='rainsoft.sms.template'
    
    _columns={
	'name':fields.char('Name'),
	'content':fields.text('Context'),
      }
    
rainsoft_sms_template()

        

