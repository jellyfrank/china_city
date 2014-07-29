# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from report import report_sxw
import xml.dom.minidom
import os, time
import osv
import re
import tools
import pooler
import re
import sys
from math import ceil

class rml_parse(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rml_parse, self).__init__(cr, uid, name, context=None)
        self.localcontext.update({
            'range': self._range,
            'comma_me': self.comma_me,
            'format_date': self._get_and_change_date_format_for_swiss,
            'strip_name' : self._strip_name,
            'explode_name' : self._explode_name,
            'paginate' : self._paginate,
            'rmb_upper' : self._rmb_upper,
            'rmb_format' : self._rmb_format,
            'account_name' :self._get_account_name,
            'account_partner' : self._get_account_partner,
        })

    def _range(self, num):
        return range(0,int(num))

    def _paginate(self, items, max_per_page=5):
        """
        分页函数
        items 为要分页的条目们
        max_per_page 设定每页条数
        返回：页数
        """
        count = len(items)
        return int(ceil(float(count) / max_per_page))

    def _rmb_upper(self, value):
        """
        人民币大写
        来自：http://topic.csdn.net/u/20091129/20/b778a93d-9f8f-4829-9297-d05b08a23f80.html
        传入浮点类型的值返回 unicode 字符串
        """
        rmbmap  = [u"零",u"壹",u"贰",u"叁",u"肆",u"伍",u"陆",u"柒",u"捌",u"玖"]
        unit = [u"分",u"角",u"元",u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"亿",
                u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"兆"]

        nums = map(int,list(str('%0.2f'%value).replace('.','')))
        words = []
        zflag = 0   #标记连续0次数，以删除万字，或适时插入零字
        start = len(nums)-3     
        for i in range(start, -3, -1):   #使i对应实际位数，负数为角分
            if 0 != nums[start-i] or len(words) == 0:
                if zflag:
                    words.append(rmbmap[0])
                    zflag = 0
                words.append(rmbmap[nums[start-i]])
                words.append(unit[i+2])
            elif 0 == i or (0 == i%4 and zflag < 3): #控制‘万/元’
                words.append(unit[i+2])
                zflag = 0
            else:
                zflag += 1
                
        if words[-1] != unit[0]:    #结尾非‘分’补整字
            words.append(u"整")
        return ''.join(words)

    def comma_me(self,amount):
        if not amount:
            amount = 0.0
        if  type(amount) is float :
            amount = str('%.2f'%amount)
        else :
            amount = str(amount)
        if (amount == '0'):
            return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def _ellipsis(self, string, maxlen=100, ellipsis = '...'):
        ellipsis = ellipsis or ''
        try:
            return string[:maxlen - len(ellipsis) ] + (ellipsis, '')[len(string) < maxlen]
        except Exception, e:
            return False

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen, '...')

    def _get_and_change_date_format_for_swiss (self,date_to_format):
        date_formatted=''
        if date_to_format:
            date_formatted = strptime (date_to_format,'%Y-%m-%d').strftime('%d.%m.%Y')
        return date_formatted

    def _explode_name(self,chaine,length):
        # We will test if the size is less then account
        full_string = ''
        if (len(str(chaine)) <= length):
            return chaine
        else:
            chaine = unicode(chaine,'utf8').encode('iso-8859-1')
            rup = 0
            for carac in chaine:
                rup = rup + 1
                if rup == length:
                    full_string = full_string + '\n'
                    full_string = full_string + carac
                    rup = 0
                else:
                    full_string = full_string + carac

        return full_string

    def makeAscii(self,str):
        try:
            Stringer = str.encode("utf-8")
        except UnicodeDecodeError:
            try:
                Stringer = str.encode("utf-16")
            except UnicodeDecodeError:
                print "UTF_16 Error"
                Stringer = str
            else:
                return Stringer
        else:
            return Stringer
        return Stringer

    def explode_this(self,chaine,length):
        #chaine = self.repair_string(chaine)
        chaine = rstrip(chaine)
        ast = list(chaine)
        i = length
        while i <= len(ast):
            ast.insert(i,'\n')
            i = i + length
        chaine = str("".join(ast))
        return chaine

    def repair_string(self,chaine):
        ast = list(chaine)
        UnicodeAst = []
        _previouslyfound = False
        i = 0
        while i < len(ast):
            elem = ast[i]
            try:
                Stringer = elem.encode("utf-8")
            except UnicodeDecodeError:
                to_reencode = elem + ast[i+1]
                Good_char = to_reencode.decode('utf-8')
                UnicodeAst.append(Good_char)
                i += i +2
            else:
                UnicodeAst.append(elem)
                i += i + 1

        return "".join(UnicodeAst)

    def ReencodeAscii(self,str):
        try:
            Stringer = str.decode("ascii")
        except UnicodeEncodeError:
            print "REENCODING ERROR"
            return str.encode("ascii")
        except UnicodeDecodeError:
            print "DECODING ERROR"
            return str.encode("ascii")

        else:
            print Stringer
            return Stringer

    def _rmb_format(self, value):
        """
        将数值按位数分开
        """
        if value < 0.01:
            # 值为0的不输出，即返回12个空格
            return ['' for i in range(12)]
        # 先将数字转为字符，去掉小数点，然后和12个空格拼成列表，取最后12个元素返回
        return (['' for i in range(12)] + list(('%0.2f'%value).replace('.','')))[-12:]

    def _get_account_name(self,id):
        account_name = self.pool.get('account.account').name_get(self.cr, self.uid, [id],{})[0]
        #Account move print use Account here:
        return account_name[1]

    def _get_account_partner(self, id,name):
        value = 'account.account,' + str(id)
        partner_prop_acc = self.pool.get('ir.property').search(self.cr, self.uid, [('value_reference','=',value)], {})
        if partner_prop_acc:
            return name
        else:
            return False

    # def _add_header(self, node):
    #   rml_head = tools.file_open('specific_param/report/header/corporate_rml_header_ch.rml').read()
    #   head_dom = xml.dom.minidom.parseString(rml_head)
    #   #for frame in head_dom.getElementsByTagName('frame'):
    #   #   frame.parentNode.removeChild(frame)
    #   node2 = head_dom.documentElement
    #   for tag in node2.childNodes:
    #       if tag.nodeType==tag.ELEMENT_NODE:
    #           found = self._find_node(node, tag.localName)
    #   #       rml_frames = found.getElementsByTagName('frame')
    #           if found:
    #               if tag.hasAttribute('position') and (tag.getAttribute('position')=='inside'):
    #                   found.appendChild(tag)
    #               else:
    #                   found.parentNode.replaceChild(tag, found)
    #   #       for frame in rml_frames:
    #   #           tag.appendChild(frame)
    #   return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
