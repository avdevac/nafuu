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

class mrpworkorder_inherit(models.Model):
	_inherit = "mrp.workorder"

	def do_finish(self):
		self.record_production()
		action = self.env.ref('mrp_workorder.mrp_workorder_action_tablet').read()[0]
		action['domain'] = [('state', 'not in', ['done', 'cancel', 'pending']), ('workcenter_id', '=', self.workcenter_id.id)]
		total_component  = total_service = 0.0
		if self.production_id.subcontract_bom:
			for line in self.production_id.bom_id.bom_line_ids:
				total_component += line.product_id.standard_price
			for line in self.production_id.service_ids:
				total_service += line.product_id.standard_price
			self.production_id.product_id.standard_price = total_service + total_component
		return action



	@api.multi
	def button_start(self):
		self.ensure_one()
		# As button_start is automatically called in the new view
		if self.state in ('done', 'cancel'):
			return True

		# Need a loss in case of the real time exceeding the expected
		timeline = self.env['mrp.workcenter.productivity']
		if self.duration < self.duration_expected:
			loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','productive')], limit=1)
			if not len(loss_id):
				raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
		else:
			loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','performance')], limit=1)
			if not len(loss_id):
				raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
		for workorder in self:
			if workorder.production_id.state != 'progress':
				workorder.production_id.write({
					'state': 'progress',
					'date_start': datetime.now(),
				})
			timeline.create({
				'workorder_id': workorder.id,
				'workcenter_id': workorder.workcenter_id.id,
				'description': _('Time Tracking: ')+self.env.user.name,
				'loss_id': loss_id[0].id,
				'date_start': datetime.now(),
				'user_id': self.env.user.id
			})
			po_id = False
			purchase_obj = self.env['purchase.order'].search([('mrp_id','=',self.production_id.id)])
			if purchase_obj.id == False:
				if self.production_id.subcontract_bom:
					if self.production_id.bom_id.supplier_id.id:
						po_id = purchase_obj.create({
								'partner_id': self.production_id.bom_id.supplier_id.id,
								'date_planned' : datetime.today(),
								'po_created':True,
								'mrp_id' : self.production_id.id,
								'origin' : self.production_id.name
							})
					if po_id.id:
						for line in self.production_id.service_ids:
							self.env['purchase.order.line'].create({
									'product_id' : line.product_id.id,
									'service':line.product_id.id,
									'final_product' : self.product_id.id,
									'name' : line.product_id.name,
									'date_planned' : datetime.today(),
									'product_uom' : line.product_id.uom_id.id,
									'price_unit' : line.product_id.standard_price,
									'product_qty' : self.production_id.product_qty,
									'order_id' : po_id.id
								})
		return self.write({'state': 'progress',
					'date_start': datetime.now(),
		})
