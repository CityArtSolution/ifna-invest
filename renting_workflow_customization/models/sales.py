# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    finance = fields.Many2many("ir.attachment", 'finance_sig_id', 'finance_id', 'sig_id', string="Finance Signature")
    facility = fields.Many2many("ir.attachment", 'facility_sig_id', 'facility_id', 'sig_id',
                                string="Facility Signature")
    legal = fields.Many2many("ir.attachment", 'legal_sig_id', 'legal_id', 'sig_id', string="Legal Signature")
    pm = fields.Many2many("ir.attachment", 'pm_sig_id', 'pm_id', 'sig_id', string="PM Signature")


class CommentWizard(models.TransientModel):
    _name = 'email.wizard'

    email_from = fields.Text("Email From")
    email_to = fields.Text("Email to")
    sale_id = fields.Many2one("sale.order")

    def send_email(self):
        active_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")
        if active_model == "sale.order":
            sales = self.env["sale.order"].sudo().browse(active_ids)
            self.sale_id = sales
            email_pm_rent_order = self.env.ref(
                'renting_workflow_customization.email_pm_rent_order')
            if email_pm_rent_order:
                email_pm_rent_order.send_mail(self.id)


class CommentWizard(models.TransientModel):
    _name = 'comment.wizard'

    comment = fields.Text("Comment")
    source = fields.Text("Source")

    def comment_log(self):
        active_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")
        if active_model == "sale.order":
            sales = self.env["sale.order"].browse(active_ids)
            if self.source == "facility":
                sales.message_post(
                    body=self.comment + ", Order-" + sales.name,
                    subtype_xmlid='mail.mt_comment',
                    subject="Facility",
                    message_type='comment')
            if self.source == "finance":
                sales.message_post(
                    body=self.comment + ", Order-" + sales.name,
                    subtype_xmlid='mail.mt_comment',
                    subject="Finance",
                    message_type='comment')
            if self.source == "legal":
                sales.message_post(
                    body=self.comment + ", Order-" + sales.name,
                    subtype_xmlid='mail.mt_comment',
                    subject="Legal",
                    message_type='comment')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    finance_user = fields.Many2one("res.users", string="Finance")
    facility_user = fields.Many2one("res.users", string="Facility")
    legal_user = fields.Many2one("res.users", string="Legal")
    pm_user = fields.Many2one("res.users", string="PM")

    state = fields.Selection([
        ('draft_qu', 'Draft Quotation'),
        ('ff_review', 'Facility & Finance Review'),
        ('ceo', 'CEO Approve'),
        ('draft', 'Issued Quotation'),
        ('sent', 'Quotation Sent'),
        ('initial_contract', 'Initial Contract'),
        ('ffl_review', 'Facility & Finance & Legal Review'),
        ('draft_contract', 'Draft Contract'),
        ('upload_doc', 'Upload Document'),
        ('view_all_ceo_approve', 'View All Doc & CEO Approve'),
        ('ejar_upload', 'Ejar Contract Upload'),
        ('finance_review', 'Finance Review'),
        ('ceo_approve', 'CEO Approval'),
        ('sale', 'Sales Order'),
        ('terms', 'Terms & Create Invoices'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft_qu')

    rental_status = fields.Selection([
        ('draft_qu', 'Quotation'),
        ('ff_review', 'Facility & Finance Review'),
        ('ceo', 'CEO Approve'),
        ('draft', 'Issued Quotation'),
        ('sent', 'Quotation Sent'),
        ('initial_contract', 'Initial Contract'),
        ('ffl_review', 'Facility & Finance & Legal Review'),
        ('draft_contract', 'Draft Contract'),
        ('upload_doc', 'Upload Document'),
        ('view_all_ceo_approve', 'View All Doc & CEO Approve'),
        ('ejar_upload', 'Ejar Contract Upload'),
        ('finance_review', 'Finance Review'),
        ('ceo_approve', 'CEO Approval'),
        ('sale', 'Sales Order'),
        ('terms', 'Terms & Create Invoices'),
        ('done', 'Locked'),
        ('pickup', 'Reserved'),
        ('return', 'Pickedup'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string="Rental Status", readonly=True)

    partner_id = fields.Many2one(readonly=False)
    finance = fields.Boolean("Finance", default=False)
    facility = fields.Boolean("Facility", default=False)

    finance_second = fields.Boolean("Finance", default=False)
    facility_second = fields.Boolean("Facility", default=False)
    legal = fields.Boolean("Facility", default=False)

    signature_doc = fields.Many2many("ir.attachment", 'sign_sale_rel', "doc_id", "sale_id", string="Signature Doc")
    commercial_register = fields.Many2many("ir.attachment", 'comm_sale_rel', 'comm_id', 'sale_id',
                                           string="السجل التجاري")
    authorization = fields.Many2many("ir.attachment", 'auth_sale_rel', 'auth_id', 'sale_id',
                                     string="مرفق التفويض لصاحب الصلاحية")
    company_contract = fields.Many2many("ir.attachment", "cont_sale_rel", "cont_id", "sale_id",
                                        string="عقد تأسيس الشركة")
    tax_certificate = fields.Many2many("ir.attachment", 'tex_sale_id', 'tax_id', 'sale_id', string="الشهادة الضريبية")
    ejar_cont = fields.Many2many("ir.attachment", 'ejar_sale_id', 'ejar_id', 'sale_id', string="عقد منصة ايجار")
    tenant_directory = fields.Many2many("ir.attachment", 'tenant_sale_id', 'tenant_id', 'sale_id',
                                        string="دليل المستأجر")

    pickup_signed = fields.Many2many("ir.attachment", 'pickup_signed_sale_id', 'pickup_id', 'sale_id',
                                     string="محضر الإستلام بعد التوقيع")

    directory_signed = fields.Many2many("ir.attachment", 'directory_signed_sale_id', 'directory_id', 'sale_id',
                                        string="دليل المستخدم بعد التوقيع")

    deleg_name = fields.Char(string="اسم صاحب التفويض")
    deleg_id = fields.Char(string="رقم الهوية")
    deleg_birth = fields.Date(string="تاريح الميلاد")
    company_add = fields.Text(string="العنوان الوطني للشركة")

    def create_mail_message_notification(self,rec,email_to_custom,message_txt):
        action = self.env.ref('sale_renting.rental_order_action').id
        menu = self.env.ref('sale_renting.rental_orders_all').id

        self.env['mail.message'].sudo().create({
            'subject': 'Finance - Rent Order',
            'body': _(
                " <a href='/web?debug=0#id=%s&action=%s&model=sale.order&view_type=kanban&menu_id=%s'> %s</a>") % (
                    rec.id, action, menu, rec.name),
            'email_from': self.env.user.name,
            'partner_ids': [(6, 0, email_to_custom.partner_id.ids)],
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
        })

    def finance_facility(self):
        for rec in self:
            rec.pm_user = self.env.user.id

            finance_group = self.env.ref('renting_workflow_customization.finance_group')
            notification_finance_group = self.env['res.users'].search([]).filtered(
                lambda i: finance_group in i.groups_id)
            for email_to_custom in notification_finance_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id

                #omara stopped activity and made it as mail.message notification to be able to open specific window action
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Finance - Rent Order',
                #     'note': f'Finance - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                # rec.message_post(
                #     body=f'Finance - Rent Order.' + self.name,
                #     subject='Finance - Rent Order',
                #     subtype_xmlid='mail.mt_comment',
                #     message_type='comment',
                #     partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Finance - Rent Order.' + self.name
                self.create_mail_message_notification(rec,email_to_custom,message_txt)


            facility_group = self.env.ref('renting_workflow_customization.facility_group')
            notification_facility_group = self.env['res.users'].search([]).filtered(
                lambda i: facility_group in i.groups_id)
            for email_to_custom in notification_facility_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Facility - Rent Order',
                #     'note': f'Facility - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                # rec.message_post(
                #     body=f'Facility - Rent Order.' + self.name,
                #     subject='Facility - Rent Order',
                #     subtype_xmlid='mail.mt_comment',
                #     message_type='comment',
                #     partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Facility - Rent Order.' + self.name
                self.create_mail_message_notification(rec,email_to_custom,message_txt)

            rec.state = "ff_review"

    def finance_facility_review(self):
        for rec in self:
            return self.env.ref('sale_report_custom.action_pickup_form').report_action(self)

    def return_review(self):
        for rec in self:
            return self.env.ref('sale_report_custom.action_return_form').report_action(self)

    def pickup_review(self):
        for rec in self:
            return self.env.ref('sale_report_custom.action_pickup_custom').report_action(self)

    def ceo_approve(self):
        for rec in self:
            pm_group = self.env.ref('renting_workflow_customization.pm_group')
            notification_pm_group = self.env['res.users'].search([]).filtered(
                lambda i: pm_group in i.groups_id)
            for email_to_custom in notification_pm_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'PM - Rent Order',
                #     'note': f'PM - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt =  f'PM - Rent Order.' + self.name
                self.create_mail_message_notification(rec,email_to_custom,message_txt)

            rec.state = "draft"
            # return {
            #     'name': 'Email',
            #     'view_mode': 'form',
            #     'res_model': 'email.wizard',
            #     'target': 'new',
            #     'type': 'ir.actions.act_window',
            # }

    def finance_approve(self):
        for rec in self:
            rec.finance = True
            rec.finance_user = self.env.user.id
            if rec.finance and rec.facility:

                facility_group = self.env.ref('renting_workflow_customization.ceo_group')
                notification_facility_group = self.env['res.users'].search([]).filtered(
                    lambda i: facility_group in i.groups_id)
                for email_to_custom in notification_facility_group:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', self._name)]).id
                    #omara stopped
                    # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    #     'res_id': rec.id,
                    #     'res_model_id': model_id,
                    #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    #     'summary': 'CEO - Rent Order',
                    #     'note': f'CEO - Rent Order.' + self.name,
                    # })
                    # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                    message_txt = f'CEO - Rent Order.' + self.name
                    self.create_mail_message_notification(rec, email_to_custom, message_txt)

                rec.state = "ceo"
            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}
            }

    def facility_approve(self):
        for rec in self:
            rec.facility = True
            rec.facility_user = self.env.user.id

            if rec.finance and rec.facility:
                facility_group = self.env.ref('renting_workflow_customization.ceo_group')
                notification_facility_group = self.env['res.users'].search([]).filtered(
                    lambda i: facility_group in i.groups_id)
                for email_to_custom in notification_facility_group:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', self._name)]).id
                    #omara stopped
                    # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    #     'res_id': rec.id,
                    #     'res_model_id': model_id,
                    #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    #     'summary': 'CEO - Rent Order',
                    #     'note': f'CEO - Rent Order.' + self.name,
                    # })
                    # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                    message_txt =  f'CEO - Rent Order.' + self.name
                    self.create_mail_message_notification(rec, email_to_custom, message_txt)

                rec.state = "ceo"
            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'facility'}

            }

    def finance_reject(self):
        for rec in self:
            rec.state = "draft_qu"
            rec.finance = False
            rec.facility = False

            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rejected Rental Order by Finance',
                #     'note': f'Rejected Rental Order by Finance.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rejected Rental Order by Finance.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Reason',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}

            }

    def facility_reject(self):
        for rec in self:
            rec.state = "draft_qu"
            rec.finance = False
            rec.facility = False

            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rejected Rental Order by Facility',
                #     'note': f'Rejected Rental Order by Facility.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt =  f'Rejected Rental Order by Facility.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Reason',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'facility'}
            }

    def action_initial_contract(self):
        for rec in self:
            rec.state = "initial_contract"

    @api.onchange('signature_doc')
    def action_initial_contract_doc(self):
        for rec in self:
            if rec.signature_doc:
                rec.state = "initial_contract"

    def sent_ff_legal(self):
        for rec in self:
            rec.state = "ffl_review"
            rec.legal_user = self.env.user.id

            finance_group = self.env.ref('renting_workflow_customization.finance_group')
            notification_finance_group = self.env['res.users'].search([]).filtered(
                lambda i: finance_group in i.groups_id)
            for email_to_custom in notification_finance_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Finance - Rent Order',
                #     'note': f'Finance - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Finance - Rent Order.' + self.name
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            facility_group = self.env.ref('renting_workflow_customization.facility_group')
            notification_facility_group = self.env['res.users'].search([]).filtered(
                lambda i: facility_group in i.groups_id)
            for email_to_custom in notification_facility_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Facility - Rent Order',
                #     'note': f'Facility - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt =f'Facility - Rent Order.' + self.name,
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            legal_group = self.env.ref('renting_workflow_customization.legal_group')
            notification_legal_group = self.env['res.users'].search([]).filtered(
                lambda i: legal_group in i.groups_id)
            for email_to_custom in notification_legal_group:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Legal - Rent Order',
                #     'note': f'Legal - Rent Order.' + self.name,
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Legal - Rent Order.' + self.name
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

    def finance_second_approve(self):
        for rec in self:
            rec.finance_second = True
            if rec.finance_second and rec.facility_second and rec.legal:
                rec.state = "draft_contract"

                group = self.env.ref('renting_workflow_customization.pm_group')
                notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
                for email_to_custom in notification_user:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', self._name)]).id
                    #omara stopped
                    # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    #     'res_id': rec.id,
                    #     'res_model_id': model_id,
                    #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    #     'summary': 'Rejected Rental Order by Finance',
                    #     'note': f'Rejected Rental Order by Finance.',
                    # })
                    # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                    message_txt =  f'Rejected Rental Order by Finance.'
                    self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}
            }

    def facility_second_approve(self):
        for rec in self:
            rec.facility_second = True
            if rec.finance_second and rec.facility_second and rec.legal:
                rec.state = "draft_contract"

                group = self.env.ref('renting_workflow_customization.pm_group')
                notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
                for email_to_custom in notification_user:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', self._name)]).id
                    #omara stopped
                    # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    #     'res_id': rec.id,
                    #     'res_model_id': model_id,
                    #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    #     'summary': 'Rejected Rental Order by Finance',
                    #     'note': f'Rejected Rental Order by Finance.',
                    # })
                    # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                    message_txt = f'Rejected Rental Order by Finance.'
                    self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}
            }

    def legal_approve(self):
        for rec in self:
            rec.legal = True
            if rec.finance_second and rec.facility_second and rec.legal:
                rec.state = "draft_contract"

                group = self.env.ref('renting_workflow_customization.pm_group')
                notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
                for email_to_custom in notification_user:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', self._name)]).id
                    #omara stopped
                    # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                    #     'res_id': rec.id,
                    #     'res_model_id': model_id,
                    #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    #     'summary': 'Rejected Rental Order by Finance',
                    #     'note': f'Rejected Rental Order by Finance.',
                    # })
                    # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                    message_txt = f'Rejected Rental Order by Finance.'
                    self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Comment',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}
            }

    def finance_second_reject(self):
        for rec in self:
            rec.state = "initial_contract"
            rec.finance_second = False

            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rejected Rental Order by Finance',
                #     'note': f'Rejected Rental Order by Finance.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rejected Rental Order by Finance.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Reason',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'finance'}
            }

    def facility_second_reject(self):
        for rec in self:
            rec.state = "initial_contract"
            rec.facility_second = False

            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rejected Rental Order by Facility',
                #     'note': f'Rejected Rental Order by Facility.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rejected Rental Order by Facility.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Reason',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'facility'}
            }

    def legal_reject(self):
        for rec in self:
            rec.state = "initial_contract"
            rec.legal = False

            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rejected Rental Order by Legal',
                #     'note': f'Rejected Rental Order by Legal.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rejected Rental Order by Legal.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

            return {
                'name': 'Reason',
                'view_mode': 'form',
                'res_model': 'comment.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_source': 'legal'}
            }

    def upload_docs(self):
        for rec in self:
            rec.state = "upload_doc"

    def send_view_docs_ceo(self):
        for rec in self:
            rec.state = "view_all_ceo_approve"

            group = self.env.ref('renting_workflow_customization.ceo_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rental Order',
                #     'note': f'Rental Order.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rental Order.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

                # return {
                #     'name': 'Email',
                #     'view_mode': 'form',
                #     'res_model': 'email.wizard',
                #     'target': 'new',
                #     'type': 'ir.actions.act_window',
                # }

                # email_pm_rent_order = self.env.ref(
                #     'renting_workflow_customization.email_pm_rent_order')
                # if email_pm_rent_order:
                #     email_pm_rent_order.send_mail(self.id)

    def view_docs_ceo(self):
        for rec in self:
            rec.state = "ejar_upload"
            group = self.env.ref('renting_workflow_customization.pm_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rental Order',
                #     'note': f'Rental Order.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rental Order.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

    def send_finance(self):
        for rec in self:
            rec.state = "finance_review"
            group = self.env.ref('renting_workflow_customization.finance_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara stopped
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Rental Order',
                #     'note': f'Rental Order.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rental Order.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

    def send_ceo_approval(self):
        for rec in self:
            rec.state = "ceo_approve"
            group = self.env.ref('renting_workflow_customization.ceo_group')
            notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
            for email_to_custom in notification_user:
                model_id = self.env['ir.model'].search(
                    [('model', '=', self._name)]).id
                #omara
                # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                #     'res_id': rec.id,
                #     'res_model_id': model_id,
                #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                #     'summary': 'Finance Review - Rental Order',
                #     'note': f'Rental Order.',
                # })
                # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                message_txt = f'Rental Order.'
                self.create_mail_message_notification(rec, email_to_custom, message_txt)

    def action_confirm(self):
        group = self.env.ref('renting_workflow_customization.finance_group')
        notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
        for email_to_custom in notification_user:
            model_id = self.env['ir.model'].search(
                [('model', '=', self._name)]).id
            #omara
            # self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
            #     'res_id': self.id,
            #     'res_model_id': model_id,
            #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            #     'summary': 'Finance Review - Rental Order',
            #     'note': f'Rental Order.',
            # })
            # self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
            message_txt = f'Rental Order.'
            self.create_mail_message_notification(self, email_to_custom, message_txt)

        result = super(SaleOrder, self).action_confirm()

    def create_invoices_button(self):
        for rec in self:
            rec.state = "terms"
        result = super(SaleOrder, self).create_invoices_button()

    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        for rec in self.order_contract_invoice:
            rec.status = "uninvoiced"
        self.state = "sale"

    def finance_cancel(self):
        for rec in self:
            pass

    def to_init(self):
        for rec in self:
            pass

    def pickup_return_review(self):
        for rec in self:
            pass
