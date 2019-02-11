# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import except_orm, UserError
import re


CL_FACTORS = [3, 2, 7, 6, 5, 4, 3, 2]
CL_VERIFICATION_DIGITS = '0123456789K0'


class res_partner(models.Model):
    _inherit = 'res.partner'

    document_number = fields.Char(string='Document Number')
    formated_vat = fields.Char(
        translate=True, string='Printable VAT',
        help='Show formatted vat')
    vat = fields.Char(
        string='VAT',
        compute='_compute_vat', inverse='_inverse_vat',
        store=True, compute_sudo=False)

    def check_vat_cl(self, vat):
        """Perform VAT number validation for Chile RUT number.

        Also see https://es.wikipedia.org/wiki/Rol_%C3%9Anico_Tributario
        """
        if len(vat) > 9:
            vat = vat.replace('-', '', 1).replace('.', '', 2)

        if len(vat) != 9:
            return False

        body, verification_digit = vat[:-1], vat[-1].upper()
        total = sum(int(digit) * factor
                    for digit, factor in zip(body, CL_FACTORS))

        return verification_digit == CL_VERIFICATION_DIGITS[11 - (total % 11)]

    @staticmethod
    def format_document_number(vat):
        clean_vat = (
            re.sub('[^1234567890Kk]', '',
                   str(vat))).zfill(9).upper()
        return '%s.%s.%s-%s' % (
            clean_vat[0:2], clean_vat[2:5], clean_vat[5:8], clean_vat[-1])

    @api.onchange('document_number')
    def onchange_document(self):
        self.document_number = self.format_document_number(self.document_number)

    @api.depends('document_number')
    def _compute_vat(self):
        for x in self:
            clean_vat = (
                re.sub('[^1234567890Kk]', '',
                       str(x.document_number))).zfill(9).upper()
            x.vat = 'CL%s' % clean_vat

    def _inverse_vat(self):
        self.document_number = self.format_document_number(self.vat)
