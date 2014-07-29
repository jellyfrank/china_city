#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Designed For QingDao Xiangjie Company
#    Powered By Rainsoft(QingDao) Author:Kevin Kong 2014 (kfx2007@163.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
		"name":u"青岛惠美食品有限公司专用模块",
		"version":"1.0",
		"description":u"""
青岛惠美食品有限公司专用模块
================================================================
该模块为青岛惠美食品有限公司专用模块，由雨水软件根据香界商贸有限公司特定的业务需求量身定做。
改模块包括的业务功能主要有：


更多详情及参见使用说明或联系雨水软件事业部。
------------------------
版权 雨水软件 2014
作者：Kevin Kong
		  """,
		"author":"rainsoft",
		"website":"http://www.qdrainsoft.com",
		"depends":["base","product","purchase","sale","stock","crm"],
                "udpate_xml":["rainsoft_partner_view.xml"]
		"installable":True,
		"category":"Generic Modules/Others"
}
