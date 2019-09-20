# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp


class MrpBom_Inherit(models.Model):
	_inherit = "mrp.bom"

	subcontract_bom = fields.Boolean(string="Subcontract BOM")
	supplier_id = fields.Many2one('res.partner', string = "Supplier",domain = [('supplier','=',True)])
	service_ids = fields.One2many('mrp.service' , 'bom_id' , string = "Services")

	@api.onchange('product_qty')
	def onchange_product_qty(self):
		if self.service_ids.product_id:
			self.service_ids.product_qty = self.product_qty
		if self.bom_line_ids:
			for line in self.bom_line_ids:
				line.product_qty *= self.product_qty 
