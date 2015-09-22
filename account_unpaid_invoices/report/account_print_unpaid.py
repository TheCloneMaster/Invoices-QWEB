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

from openerp.report import report_sxw
from openerp.osv import osv


class Unpaid(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Unpaid, self).__init__(cr, uid, name, context=context)
        ids = context.get('active_ids')
        partner_obj = self.pool['res.partner']
        docs = partner_obj.browse(cr, uid, ids, context)

        self.due = {}
        self.paid = {}
        self.mat = {}
        self.moves = {}
        self.invoices = {}

        for partner in docs:
            self.moves[partner.id] = self._lines_get(partner)
            self.invoices[partner.id] = self._invoices_get(partner)

            self.due[partner.id] = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) or (y['account_id']['type'] == 'payable' and y['credit'] * -1 or 0)), self.moves[partner.id], 0)
            self.paid[partner.id] = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and sum( z['credit'] for z in y['reconcile_partial_id']['line_partial_ids']) or 0) or (y['account_id']['type'] == 'payable' and sum( z['debit'] for z in y['reconcile_partial_id']['line_partial_ids']) or 0)), self.moves[partner.id], 0)
            self.mat[partner.id] = self.due[partner.id] - self.paid[partner.id]

            self.due[partner.id] += reduce(lambda x, y: x + (y['amount_total']), self.invoices[partner.id], 0)
            self.paid[partner.id] += reduce(lambda x, y: x + (y['amount_total'] - y['residual']), self.invoices[partner.id], 0)
            self.mat[partner.id] += reduce(lambda x, y: x + (y['residual']), self.invoices[partner.id], 0)

        addresses = self.pool['res.partner']._address_display(cr, uid, ids, None, None)
        self.localcontext.update({
            'docs': docs,
            'time': time,
            'getLines': self.lines_get,
            'getInvoices': self.invoices_get,
            'tel_get': self._tel_get,
            'message': self._message,
            'due': self.due,
            'paid': self.paid,
            'mat': self.mat,
            'addresses': addresses
        })
        self.context = context

    def _tel_get(self,partner):
        if not partner:
            return False
        res_partner = self.pool['res.partner']
        addresses = res_partner.address_get(self.cr, self.uid, [partner.id], ['invoice'])
        adr_id = addresses and addresses['invoice'] or False
        if adr_id:
            adr=res_partner.read(self.cr, self.uid, [adr_id])[0]
            return adr['phone']
        else:
            return partner.phone or False
        return False

    def lines_get(self, partner):
        return self.moves[partner.id]

    def _lines_get(self, partner):
        moveline_obj = self.pool['account.move.line']
        movelines = moveline_obj.search(self.cr, self.uid,
                [('partner_id', '=', partner.id),
                    ('account_id.type', '=', 'receivable'),
                    ('journal_id.type', '=', 'situation'),
                    ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        return moveline_obj.browse(self.cr, self.uid, movelines)

    def invoices_get(self, partner):
        return self.invoices[partner.id]

    def _invoices_get(self, partner):
        invoices_obj = self.pool['account.invoice']
        invoices = invoices_obj.search(self.cr, self.uid,
                [('partner_id', '=', partner.id),
                    ('type', '=', 'out_invoice'),
                    ('state', '=', 'open')])

        return invoices_obj.browse(self.cr, self.uid, invoices)

    def _message(self, obj, company):
        company_pool = self.pool['res.company']
        message = company_pool.browse(self.cr, self.uid, company.id, {'lang':obj.lang}).overdue_msg
        return message.split('\n')


class report_unpaid(osv.AbstractModel):
    _name = 'report.account_unpaid_invoices.report_unpaid'
    _inherit = 'report.abstract_report'
    _template = 'account_unpaid_invoices.report_unpaid'
    _wrapped_report_class = Unpaid

