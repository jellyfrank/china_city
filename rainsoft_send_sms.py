# -*- coding:utf-8 -*-

from openerp.osv import osv,fields
from xml.etree import ElementTree
import httplib,urllib

class rainsoft_send_sms(osv.osv):
    _name='rainsoft.sendsms'
    _description='Text Message Interface'

    def send(self,cr,uid,ids,mobile,content,context=None):
	user_id = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.userid",context=context),
        send_address = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.address",context=context)
        username = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.username",context=context)
        password = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.password",context=context)
        appendix = self.pool.get("ir.config_parameter").get_param(cr,uid,"rainsoft.sms.appendix",context=context)
      
	httpclient=None
	res ={}
	try:
	    params=urllib.urlencode({
		"action":"send",
		"userid":int(user_id[0]),
		"account":username,
		"password":password,
		"mobile":mobile,
		"content":content+appendix,
		"sendTime":'',
		"extno":'',
	    })
	    
	    address = send_address.split(':')
	    port = len(address)>1 and address[1] or 80
	    print address,port

	    headers={"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
	    httpclient = httplib.HTTPConnection(address[0],int(port),timeout=30)
	    httpclient.request("POST","/sms.aspx",params,headers)

	    response=httpclient.getresponse()
	    result = response.read()
	    
	    # handle the xml result.
	    root = ElementTree.fromstring(result)
	    lst_node = root.getiterator("returnstatus")
	    for node in lst_node:
		res['status'] = node.text
	    mes_node = root.getiterator("message")
	    res['message'] = mes_node[0].text
	except Exception,e:
	    print e
	finally:
	    if httpclient:
		httpclient.close() 
	    return res
rainsoft_send_sms()
