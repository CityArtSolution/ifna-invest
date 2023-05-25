# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CommentWizard(models.TransientModel):
    _name = 'comment.wizard'

    comment = fields.Text("Comment")

    def comment_log(self):
        active_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")
        if active_model == "sale.order":
            sales = self.env["sale.order"].browse(active_ids)
            sales.message_post(
                body=self.comment,
                subtype_xmlid='mail.mt_comment',
                message_type='comment')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('ff_review', 'Facility & Finance Review'),
        ('ceo', 'CEO Approve'),
        ('draft_qu', 'Issued Quotation'),
        ('sent', 'Quotation Sent'),
        ('initial_contract', 'Initial Contract'),
        ('ffl_review', 'Facility & Finance & Legal Review'),
        ('draft_contract', 'Draft Contract'),
        ('upload_doc', 'Upload Document'),
        ('view_all_ceo_approve', 'View All Doc & CEO Approve'),
        ('ejar_upload', 'Ejar Contract Upload'),
        ('finance_review', 'Finance Review'),
        ('sale', 'CEO Approval'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    rental_status = fields.Selection([
        ('draft', 'Quotation'),
        ('ff_review', 'Facility & Finance Review'),
        ('ceo', 'CEO Approve'),
        ('draft_qu', 'Issued Quotation'),
        ('sent', 'Quotation Sent'),
        ('initial_contract', 'Initial Contract'),
        ('ffl_review', 'Facility & Finance & Legal Review'),
        ('draft_contract', 'Draft Contract'),
        ('upload_doc', 'Upload Document'),
        ('view_all_ceo_approve', 'View All Doc & CEO Approve'),
        ('ejar_upload', 'Ejar Contract Upload'),
        ('finance_review', 'Finance Review'),
        ('sale', 'CEO Approval'),
        ('done', 'Locked'),
        ('pickup', 'Reserved'),
        ('return', 'Pickedup'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string="Rental Status", readonly=True)

    finance = fields.Boolean("Finance")
    facility = fields.Boolean("Facility")

    def finance_facility(self):
        for rec in self:
            group = self.env.ref('renting_workflow_customization.finance_facility_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    'res_id': rec.id,
                    'res_model_id': model_id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'End of Contract Notification',
                    'note': f'Contract is about to End Please review and take appropriate action.',
                })

                self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                rec.message_post(
                    body=f'Contract is about to End Please review and take appropriate action.',
                    subject='End of Contract Notification',
                    subtype_xmlid='mail.mt_comment',
                    message_type='comment',
                    partner_ids=email_to_custom.partner_id.ids)
            rec.state = "ff_review"

    def finance_facility_review(self):
        for rec in self:
            return self.env.ref('sale_report_custom.action_pickup_form').report_action(self)

    def finance_approve(self):
        for rec in self:
            rec.finance = True
            if rec.finance and rec.facility:
                rec.state = "ceo"
            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window'
            }

    def facility_approve(self):
        for rec in self:
            rec.facility = True
            if rec.finance and rec.facility:
                rec.state = "ceo"
            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window'
            }

    def finance_reject(self):
        for rec in self:
            rec.state = "draft"

    def facility_reject(self):
        for rec in self:
            rec.state = "draft"
