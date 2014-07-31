#coding:utf-8

from openerp.osv import osv,fields
import xlrd,base64

class hm_region(osv.osv):
		_name="hm.region"

		_columns={
						'xls':fields.binary('XLS File'),
						}

		def btn_import(self,cr,uid,ids,context=None):
				for wiz in self.browse(cr,uid,ids):
						if not wiz.xls:
								continue
						excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
						sheets=excel.sheets()
						cty_id=0
						for sh in sheets:
								for row in range(1,sh.nrows):
										state = sh.cell(row,0).value
										city = sh.cell(row,1).value
										district = sh.cell(row,2).value

										#read state
										states = self.pool.get('res.country.state').search(cr,uid,[('name','=',state)],context=context)
										if len(states):
												cities = self.pool.get('hm.city').search(cr,uid,[('name','=',city)],context=context)
												if len(cities):
														dises = self.pool.get('hm.district').search(cr,uid,[('name','=',district)],context=context)
														if len(dises):
																continue
														else:
																self.pool.get('hm.district').create(cr,uid,{'name':district,'city':cities[0]})
												else:
														c_id=self.pool.get('hm.city').create(cr,uid,{'name':city,'state':states[0]})
												
														self.pool.get('hm.district').create(cr,uid,{'name':district,'city':c_id})		
										else:
												china = self.pool.get('res.country').search(cr,uid,[('name','=','China')],context=context)
												if len(china):
														cty_id=china[0]
														s_id = self.pool.get('res.country.state').create(cr,uid,{'name':state,'country_id':china[0],'code':'0'})
														c_id=self.pool.get('hm.city').create(cr,uid,{'name':city,'state':s_id})
														self.pool.get('hm.district').create(cr,uid,{'name':district,'city':c_id})
												else:
														ch_id = self.pool.get('res.country').create(cr,uid,{'name':'China'})
														cty_id=ch_id
														s_id = self.pool.get('res.country.state').create(cr,uid,{'name':state,'country_id':ch_id,'code':'0'})
														c_id=self.pool.get('hm.city').create(cr,uid,{'name':city,'state':s_id})
														self.pool.get('hm.district').create(cr,uid,{'name':district,'city':c_id})
														
																
							
