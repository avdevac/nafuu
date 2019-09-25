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
	btn_shw = fields.Boolean("Show Button")
	# btn_hide = fields.Boolean("Hide Button",default=True)

	@api.multi
	def wo_close(self):
		if self.state == 'purchase':
			if self.mrp_id.workorder_ids:
				rcd_pro = self.env['mrp.workorder'].browse(self.mrp_id.workorder_ids.id).record_production()
				if rcd_pro:
					mo_done = self.env['mrp.production'].browse(self.mrp_id.id).button_mark_done()
				if mo_done:
					if self.order_line:
						if self.mrp_id.state == 'done':
							self.order_line[0].qty_received = self.mrp_id.finished_move_line_ids[0].qty_done

					self.btn_shw = False
					# self.btn_hide = False
		else:
			raise UserError(_('Please confirm the Purchase Quotation.'))

	@api.multi
	def wo_success(self):
		return True


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

