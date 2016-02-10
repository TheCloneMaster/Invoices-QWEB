# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
#from common_report_header import common_report_header

class pos_session_report(report_sxw.rml_parse): #, common_report_header):
    def __init__(self, cr, uid, name, context):
        super(pos_session_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_total': self._get_total,
        })
        self.context = context

    def _get_total(self, lines, field):
        total = 0.0
        ##for line in lines :
        ##    total += line.product_uom_qty or 0.0
        return total

##report_sxw.report_sxw('report.voucher.print1','account.voucher','addons/account_voucher_print/report/account_voucher_print1.rml', parser=voucher_print1,header="internal")

class report_sales_invoice_qweb(osv.AbstractModel):
    _name = 'report.report_pos_session_qweb.report_pos_session_qweb'
    _inherit = 'report.abstract_report'
    _template = 'report_pos_session_qweb.report_pos_session_qweb'
    _wrapped_report_class = pos_session_report

