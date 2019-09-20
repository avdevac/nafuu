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


class MrpProduction_Inherit(models.Model):
    _inherit = "mrp.production"

    po_count = fields.Integer(string="Purchase Order")
    subcontract_bom = fields.Boolean(string="Subcontract BOM",related="bom_id.subcontract_bom")
    service_ids = fields.One2many('mrp.service' , 'production_id' ,string = "service" ,related="bom_id.service_ids")

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self._check_lots()
        self.post_inventory()
        moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_cancel._action_cancel()
        self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
        self.compute_final_cost()
        return self.write({'state': 'done'})

    def compute_final_cost(self):
        total_component  = total_service = total_purchase =  0.0
        if self.subcontract_bom:
            for line in self.bom_id.bom_line_ids:
                total_component += (line.product_id.standard_price * line.product_qty)
            for line in self.service_ids:
                total_service += line.product_id.standard_price
            purchase_obj = self.env['purchase.order'].search([('mrp_id','=',self.id)])
            if purchase_obj.order_line:
                for line in purchase_obj.order_line:
                    total_purchase += line.price_unit
            self.product_id.manufacture_cost = total_purchase + total_component
        return True

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        if self.service_ids.product_id:
            self.service_ids.product_qty = self.product_qty

    # @api.multi
    # def button_mark_done(self):
    #     self.ensure_one()
    #     for wo in self.workorder_ids:
    #         if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
    #             raise UserError(_('Work order %s is still running') % wo.name)
    #     self._check_lots()
    #     self.post_inventory()
    #     moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
    #     moves_to_cancel._action_cancel()
    #     self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
    #     self.compute_final_cost()
    #     return self.write({'state': 'done'})

    # def compute_final_cost(self):
    #     total_component  = total_service = 0.0
    #     if self.subcontract_bom:
    #         for line in self.bom_id.bom_line_ids:
    #             total_component += line.product_id.standard_price
    #         for line in self.service_ids:
    #             total_service += line.product_id.standard_price
    #         self.product_id.manufacture_cost = total_service + total_component
    #     return True

    # @api.model
    # def create(self, values):
    #     if not values.get('name', False) or values['name'] == _('New'):
    #         picking_type_id = values.get('picking_type_id') or self._get_default_picking_type()
    #         picking_type_id = self.env['stock.picking.type'].browse(picking_type_id)
    #         if picking_type_id:
    #             values['name'] = picking_type_id.sequence_id.next_by_id()
    #         else:
    #             values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
    #     if not values.get('procurement_group_id'):
    #         values['procurement_group_id'] = self.env["procurement.group"].create({'name': values['name']}).id
    #     production = super(MrpProduction, self).create(values)
    #     production._generate_moves()
    #     return production


    # @api.multi
    # def _generate_moves(self):
    #     for production in self:
    #         production._generate_finished_moves()
    #         factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
    #         boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
    #         production._generate_raw_moves(lines)
    #         # Check for all draft moves whether they are mto or not
    #         production._adjust_procure_method()
    #         production.move_raw_ids._action_confirm()
    #     return True    




class MrpProduction_Inherit(models.TransientModel):
    _inherit = "change.production.qty"

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        if self.mo_id.service_ids.product_id:
            self.mo_id.service_ids.product_qty = self.product_qty
