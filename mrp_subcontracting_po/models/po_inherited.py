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

class PurchaseOrder_inherit(models.Model):
	_inherit = 'purchase.order'

	mrp_id = fields.Many2one('mrp.production',string="MRP")
	po_created = fields.Boolean("po created for wo")
	

class PurchaseOrderLine_inherit(models.Model):
	_inherit = 'purchase.order.line'

	service = fields.Many2one("product.product",string="Service")
	final_product = fields.Many2one("product.product",string="Final Product")



class mrp_service(models.Model):
	_name = "mrp.service"

	product_id = fields.Many2one('product.product',string = "product" , domain = [('type','=','service')])
	product_qty = fields.Integer(string = "Product Quantity")
	bom_id = fields.Many2one('mrp.bom')
	production_id = fields.Many2one('mrp.production')


	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.product_qty = self.bom_id.product_qty

