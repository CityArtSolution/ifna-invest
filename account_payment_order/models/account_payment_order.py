# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre - alexis.delattre@akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from .num_to_text_ar import amount_to_text_arabic
import datetime
from num2words import num2words


class PaymentBeneficiary(models.Model):
    _name = "payment.beneficiary"
    _description = "Payment Order"

    name = fields.Char(string="Name", readonly=False, copy=False)


class AccountPaymentOrder(models.Model):
    _name = "account.payment.order"
    _description = "Payment Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(string="Number", readonly=True, copy=False)
    request_date = fields.Date(string="Request Date", required=True, default=fields.Date.context_today)
    payment_request_type = fields.Selection(string="Payment Request Type", selection=[('account', 'Account')])
    amount = fields.Float(string="Amount")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    transaction_currency_id = fields.Many2one('res.currency', string='Currency', compute='get_transaction_currency_id')
    bank_id = fields.Many2one(comodel_name="res.bank", string="Bank Name")
    bank_account_no = fields.Many2one(comodel_name="res.partner.bank", string="Bank Account No")

    beneficiary_name = fields.Many2one(comodel_name="payment.beneficiary", string="Beneficiary Name", )

    # bank_account_no = fields.Char(string="Bank Account No")
    # beneficiary_name = fields.Char(string="Beneficiary Name")

    communication = fields.Char(string='Details', required=False,
                                help="Label of the payment that will be seen by the destinee")
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        required=True,
        ondelete="restrict",
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
    )
    payment_type = fields.Selection(
        selection=[("inbound", "Inbound"), ("outbound", "Outbound")],
        readonly=True,
        required=True,
    )
    payment_method_id = fields.Many2one(
        comodel_name="account.payment.method",
        related="payment_mode_id.payment_method_id",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        related="payment_mode_id.company_id", store=True, readonly=True
    )
    company_currency_id = fields.Many2one(
        related="payment_mode_id.company_id.currency_id", store=True, readonly=True
    )
    bank_account_link = fields.Selection(
        related="payment_mode_id.bank_account_link", readonly=True
    )
    allowed_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        compute="_compute_allowed_journal_ids",
        string="Allowed journals",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Bank Journal",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        check_company=True,
    )
    # The journal_id field is only required at confirm step, to
    # allow auto-creation of payment order from invoice
    company_partner_bank_id = fields.Many2one(
        related="journal_id.bank_account_id",
        string="Company Bank Account",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Confirmed"),
            ("generated", "Draft Journal Entry"),
            ("uploaded", "Posted Journal Entry"),
            ("cancel", "Cancel"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    date_prefered = fields.Selection(
        selection=[
            ("now", "Immediately"),
            ("due", "Due Date"),
            ("fixed", "Fixed Date"),
        ],
        string="Payment Execution Date Type",
        required=True,
        default="due",
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_scheduled = fields.Date(
        string="Payment Execution Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        help="Select a requested date of execution if you selected 'Due Date' "
             "as the Payment Execution Date Type.",
    )
    date_generated = fields.Date(string="File Generation Date", readonly=True)
    date_uploaded = fields.Date(string="File Upload Date", readonly=True)
    generated_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Generated by",
        readonly=True,
        ondelete="restrict",
        copy=False,
        check_company=True,
    )
    current_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Current user",
        default=lambda self: self.env.user
    )
    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="order_id",
        string="Transactions",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    bank_line_ids = fields.One2many(
        comodel_name="bank.payment.line",
        inverse_name="order_id",
        string="Bank Transactions",
        readonly=True,
        help="The bank payment lines are used to generate the payment file. "
             "They are automatically created from transaction lines upon "
             "confirmation of the payment order: one bank payment line can "
             "group several transaction lines if the option "
             "'Group Transactions in Payment Orders' is active on the payment "
             "mode.",
    )
    total_company_currency = fields.Monetary(
        compute="_compute_total", store=True, currency_field="company_currency_id"
    )
    bank_line_count = fields.Integer(
        compute="_compute_bank_line_count", string="Number of Bank Transactions"
    )
    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="payment_order_id",
        string="Journal Entries",
        readonly=True,
    )
    move_count = fields.Integer(
        compute="_compute_move_count", string="Number of Journal Entries"
    )
    bank_statements_count = fields.Integer(compute="_compute_bank_statements_count")
    description = fields.Char(string='Purpose')
    payment_method = fields.Selection(string='Payment Method',
                                      selection=[('cash', 'Cash'), ('check', 'Check'), ('sadad', 'SADAD'),
                                                 ('transfer', 'Transfer')], default='cash')
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount", store=True)
    department_id = fields.Many2one(comodel_name='account.analytic.account', string='Department')
    beneficiary_partner_id = fields.Many2one(comodel_name='res.partner', string='Beneficiary Name')

    @api.depends("payment_mode_id")
    def _compute_allowed_journal_ids(self):
        for record in self:
            if record.payment_mode_id.bank_account_link == "fixed":
                record.allowed_journal_ids = record.payment_mode_id.fixed_journal_id
            elif record.payment_mode_id.bank_account_link == "variable":
                record.allowed_journal_ids = record.payment_mode_id.variable_journal_ids
            else:
                record.allowed_journal_ids = False

    @api.depends("payment_line_ids")
    def get_transaction_currency_id(self):
        for rec in self:
            rec.transaction_currency_id = self.env.company.currency_id.id
            for line in rec.payment_line_ids:
                rec.transaction_currency_id = line.currency_id

    def unlink(self):
        for order in self:
            if order.state == "uploaded":
                raise UserError(
                    _(
                        "You cannot delete an uploaded payment order. You can "
                        "cancel it in order to do so."
                    )
                )
        return super(AccountPaymentOrder, self).unlink()

    @api.constrains("payment_type", "payment_mode_id")
    def payment_order_constraints(self):
        for order in self:
            if (
                    order.payment_mode_id.payment_type
                    and order.payment_mode_id.payment_type != order.payment_type
            ):
                raise ValidationError(
                    _(
                        "The payment type (%(ptype)s) is not the same as the payment "
                        "type of the payment mode (%(pmode)s)",
                        ptype=order.payment_type,
                        pmode=order.payment_mode_id.payment_type,
                    )
                )

    @api.constrains("date_scheduled")
    def check_date_scheduled(self):
        today = fields.Date.context_today(self)
        for order in self:
            if order.date_scheduled:
                if order.date_scheduled < today:
                    raise ValidationError(
                        _(
                            "On payment order %(porder)s, the Payment Execution Date "
                            "is in the past (%(exedate)s).",
                            porder=order.name,
                            exedate=order.date_scheduled,
                        )
                    )

    @api.depends("payment_line_ids", "payment_line_ids.amount_company_currency", "payment_request_type", "amount")
    def _compute_total(self):
        for rec in self:
            if rec.payment_request_type == 'account':
                rec.total_company_currency = rec.amount
            else:
                rec.total_company_currency = sum(
                    rec.mapped("payment_line_ids.amount_company_currency") or [0.0]
                )

    @api.depends("bank_line_ids")
    def _compute_bank_line_count(self):
        for order in self:
            order.bank_line_count = len(order.bank_line_ids)

    @api.depends("move_ids")
    def _compute_move_count(self):
        rg_res = self.env["account.move"].read_group(
            [("payment_order_id", "in", self.ids)],
            ["payment_order_id"],
            ["payment_order_id"],
        )
        mapped_data = {
            x["payment_order_id"][0]: x["payment_order_id_count"] for x in rg_res
        }
        for order in self:
            order.move_count = mapped_data.get(order.id, 0)

    def _compute_bank_statements_count(self):
        self.bank_statements_count = self.env['account.bank.statement'].search_count(
            [('payment_request_id', '=', self.id)])

    def get_pr_sequence(self):
        # date = datetime.datetime.strptime(vals.get("request_date"), '%Y-%m-%d').date()
        date = self.request_date
        if self.payment_mode_id.is_receipt:
            all_payments = self.env['account.payment.order'].search(
                [('payment_mode_id.is_receipt', '=', True), ('state', '!=', 'draft'), ('id', '!=', self.id)])
        else:
            all_payments = self.env['account.payment.order'].search([('state', '!=', 'draft'), ('id', '!=', self.id)])

        same_month_payments_ids = []
        for payment in all_payments:
            if payment.request_date.year == date.year and payment.request_date.month == date.month:
                same_month_payments_ids.append(payment.id)
        last_payment = self.env['account.payment.order'].sudo().search([('id', 'in', same_month_payments_ids)],
                                                                       limit=1)
        month_zeros = ""
        month_digits_no = len(str(date.month))
        if month_digits_no == 1:
            month_zeros = "0"
        last_date = False
        if self.name != "/":
            last_sequence = self.name.split('-')
            last_date = last_sequence[0].split('/')
        if last_date != False:
            if int(last_date[0]) != int(date.year) or int(last_date[1]) != int(date.month):
                if last_payment:
                    last_sequence = last_payment.name.split('-')
                    digits_no = len(str(int(last_sequence[1]) + 1))
                    self.name = "%s/%s%s-" % (date.year, month_zeros, date.month) + ((4 - digits_no) * "0") + str(
                        int(last_sequence[1]) + 1)
                else:
                    self.name = "%s/%s%s-" % (date.year, month_zeros, date.month) + "0001"
        else:
            if last_payment:
                last_sequence = last_payment.name.split('-')
                digits_no = len(str(int(last_sequence[1]) + 1))
                self.name = "%s/%s%s-" % (date.year, month_zeros, date.month) + ((4 - digits_no) * "0") + str(
                    int(last_sequence[1]) + 1)
            else:
                self.name = "%s/%s%s-" % (date.year, month_zeros, date.month) + "0001"

    @api.model
    def create(self, vals):
        # # if vals.get("name", "New") == "New":
        # date = datetime.datetime.strptime(vals.get("request_date"), '%Y-%m-%d').date()
        # all_payments = self.env['account.payment.order'].search([])
        # same_month_payments_ids = []
        # for payment in all_payments:
        #     if payment.request_date.year == date.year and payment.request_date.month == date.month:
        #         same_month_payments_ids.append(payment.id)
        # last_payment = self.env['account.payment.order'].search([('id', 'in', same_month_payments_ids)], limit=1)
        # month_zeros=""
        # month_digits_no = len(str(date.month))
        # if month_digits_no == 1:
        #     month_zeros ="0"
        # if last_payment:
        #     last_sequence = last_payment.name.split('-')
        #     digits_no = len(str(int(last_sequence[1]) + 1))
        #     vals["name"] = "PR %s/%s%s-" % (date.year,month_zeros, date.month) + ((4 - digits_no) * "0") + str(
        #         int(last_sequence[1]) + 1)
        # else:
        vals["name"] = "/"
        if vals.get("payment_mode_id"):
            payment_mode = self.env["account.payment.mode"].browse(
                vals["payment_mode_id"]
            )
            vals["payment_type"] = payment_mode.payment_type
            if payment_mode.bank_account_link == "fixed":
                vals["journal_id"] = payment_mode.fixed_journal_id.id
            if not vals.get("date_prefered") and payment_mode.default_date_prefered:
                vals["date_prefered"] = payment_mode.default_date_prefered
        return super(AccountPaymentOrder, self).create(vals)

    @api.onchange("payment_mode_id")
    def payment_mode_id_change(self):
        if len(self.allowed_journal_ids) == 1:
            self.journal_id = self.allowed_journal_ids
        if self.payment_mode_id.default_date_prefered:
            self.date_prefered = self.payment_mode_id.default_date_prefered

    def action_uploaded_cancel(self):
        for move in self.move_ids:
            move.button_cancel()
            for move_line in move.line_ids:
                move_line.remove_move_reconcile()
            move.with_context(force_delete=True).unlink()
        self.action_cancel()
        return True

    def cancel2draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        for order in self:
            order.write({"state": "cancel"})
            order.bank_line_ids.unlink()
        return True

    @api.model
    def _prepare_bank_payment_line(self, paylines):
        return {
            "order_id": paylines[0].order_id.id,
            "payment_line_ids": [(6, 0, paylines.ids)],
            "communication": "-".join([line.communication for line in paylines]),
        }

    def reset2draft(self):
        self.write({"state": "draft"})

    def draft2open(self):
        """
        Called when you click on the 'Confirm' button
        Set the 'date' on payment line depending on the 'date_prefered'
        setting of the payment.order
        Re-generate the bank payment lines
        """
        bplo = self.env["bank.payment.line"]
        today = fields.Date.context_today(self)
        for order in self:
            order.get_pr_sequence()
            if not order.journal_id:
                raise UserError(
                    _("Missing Bank Journal on payment order %s.") % order.name
                )
            if (
                    order.payment_method_id.bank_account_required
                    and not order.journal_id.bank_account_id
            ):
                raise UserError(
                    _("Missing bank account on bank journal '%s'.")
                    % order.journal_id.display_name
                )
            if not order.payment_line_ids and order.payment_request_type != 'account':
                raise UserError(
                    _("There are no transactions on payment order %s.") % order.name
                )
            if not order.journal_id and order.payment_request_type == 'account':
                raise UserError(
                    _("There are no Bank Journal on payment order %s.") % order.name
                )
            # Delete existing bank payment lines
            order.bank_line_ids.unlink()
            # Create the bank payment lines from the payment lines
            group_paylines = {}  # key = hashcode
            for payline in order.payment_line_ids:
                payline.draft2open_payment_line_check()
                # Compute requested payment date
                if order.date_prefered == "due":
                    requested_date = payline.ml_maturity_date or payline.date or today
                elif order.date_prefered == "fixed":
                    requested_date = order.date_scheduled or today
                else:
                    requested_date = today
                # No payment date in the past
                if requested_date < today:
                    requested_date = today
                # inbound: check option no_debit_before_maturity
                if (
                        order.payment_type == "inbound"
                        and order.payment_mode_id.no_debit_before_maturity
                        and payline.ml_maturity_date
                        and requested_date < payline.ml_maturity_date
                ):
                    raise UserError(
                        _(
                            "The payment mode '%(pmode)s' has the option "
                            "'Disallow Debit Before Maturity Date'. The "
                            "payment line %(pline)s has a maturity date %(mdate)s "
                            "which is after the computed payment date %(pdate)s.",
                            pmode=order.payment_mode_id.name,
                            pline=payline.name,
                            mdate=payline.ml_maturity_date,
                            pdate=requested_date,
                        )
                    )
                # Write requested_date on 'date' field of payment line
                # norecompute is for avoiding a chained recomputation
                # payment_line_ids.date
                # > payment_line_ids.amount_company_currency
                # > total_company_currency
                # with self.env.norecompute():
                #     payline.date = requested_date
                # Group options
                if order.payment_mode_id.group_lines:
                    hashcode = payline.payment_line_hashcode()
                else:
                    # Use line ID as hascode, which actually means no grouping
                    hashcode = payline.id
                if hashcode in group_paylines:
                    group_paylines[hashcode]["paylines"] += payline
                    group_paylines[hashcode]["total"] += payline.amount_currency
                else:
                    group_paylines[hashcode] = {
                        "paylines": payline,
                        "total": payline.amount_currency,
                    }
            order.recompute()
            # Create bank payment lines
            for paydict in list(group_paylines.values()):
                # Block if a bank payment line is <= 0
                if paydict["total"] <= 0:
                    raise UserError(
                        _(
                            "The amount for Partner '%(partner)s' is negative "
                            "or null (%(amount).2f) !",
                            partner=paydict["paylines"][0].partner_id.name,
                            amount=paydict["total"],
                        )
                    )
                vals = self._prepare_bank_payment_line(paydict["paylines"])
                bplo.create(vals)
        self.write({"state": "open"})
        return True

    def generate_payment_file(self):
        """Returns (payment file as string, filename)"""
        self.ensure_one()
        if self.payment_method_id.code == "manual":
            return (False, False)
        else:
            raise UserError(
                _(
                    "No handler for this payment method. Maybe you haven't "
                    "installed the related Odoo module."
                )
            )

    def open2generated(self):
        self.ensure_one()
        payment_file_str, filename = self.generate_payment_file()
        action = {}
        if payment_file_str and filename:
            attachment = self.env["ir.attachment"].create(
                {
                    "res_model": "account.payment.order",
                    "res_id": self.id,
                    "name": filename,
                    "datas": base64.b64encode(payment_file_str),
                }
            )
            simplified_form_view = self.env.ref(
                "account_payment_order.view_attachment_simplified_form"
            )
            action = {
                "name": _("Payment File"),
                "view_mode": "form",
                "view_id": simplified_form_view.id,
                "res_model": "ir.attachment",
                "type": "ir.actions.act_window",
                "target": "current",
                "res_id": attachment.id,
            }
        self.write(
            {
                "date_generated": fields.Date.context_today(self),
                "state": "generated",
                "generated_user_id": self._uid,
            }
        )
        return action

    def generated2uploaded(self):
        for order in self:
            if order.payment_mode_id.generate_move:
                order.generate_move()
        self.write(
            {"state": "uploaded", "date_uploaded": fields.Date.context_today(self)}
        )
        return True

    def generate_bank_statement(self):
        self.env["account.bank.statement"].create(
            {
                "journal_id": self.journal_id.id,
                "date": self.request_date,
                "line_ids": [(0, 0, {
                    'date': self.request_date,
                    'payment_ref': self.communication,
                    'amount': self.amount * -1,
                })],
                "payment_request_id": self.id
            }
        )
        self.write(
            {"state": "uploaded", "date_uploaded": fields.Date.context_today(self)}
        )
        return True

    def _prepare_move(self, bank_lines=None):
        if self.payment_type == "outbound":
            ref = _("Payment order %s") % self.name
        else:
            ref = _("Debit order %s") % self.name
        if bank_lines and len(bank_lines) == 1:
            ref += " - " + bank_lines.name
        details = f"- {self.description} - {self.payment_line_ids[0].communication}"
        vals = {
            "date": bank_lines[0].date,
            "journal_id": self.journal_id.id,
            "ref": ref + details,
            "payment_order_id": self.id,
            "line_ids": [],
        }
        total_company_currency = total_payment_currency = 0
        for bline in bank_lines:
            total_company_currency += bline.amount_company_currency
            total_payment_currency += bline.amount_currency
            partner_ml_vals = self._prepare_move_line_partner_account(bline)
            vals["line_ids"].append((0, 0, partner_ml_vals))
        trf_ml_vals = self._prepare_move_line_offsetting_account(
            total_company_currency, total_payment_currency, bank_lines
        )
        vals["line_ids"].append((0, 0, trf_ml_vals))
        return vals

    def _prepare_move_line_offsetting_account(
            self, amount_company_currency, amount_payment_currency, bank_lines
    ):
        vals = {}
        payment_method = self.payment_mode_id.payment_method_id
        account_id = False
        if self.payment_type == "inbound":
            name = _("Debit order %s") % self.name
            account_id = (
                    self.journal_id.inbound_payment_method_line_ids.filtered(
                        lambda x: x.payment_method_id == payment_method
                    ).payment_account_id.id
                    or self.journal_id.company_id.account_journal_payment_debit_account_id.id
            )
        elif self.payment_type == "outbound":
            name = _("Payment order %s") % self.name
            account_id = (
                    self.journal_id.outbound_payment_method_line_ids.filtered(
                        lambda x: x.payment_method_id == payment_method
                    ).payment_account_id.id
                    or self.journal_id.company_id.account_journal_payment_credit_account_id.id
            )

        partner_id = False
        for index, bank_line in enumerate(bank_lines):
            if index == 0:
                partner_id = bank_line.payment_line_ids[0].partner_id.id
            elif bank_line.payment_line_ids[0].partner_id.id != partner_id:
                # we have different partners in the grouped move
                partner_id = False
                break
        vals.update(
            {
                "name": f"{name} - {self.description} - {self.payment_line_ids[0].communication}",
                "partner_id": partner_id,
                "account_id": account_id,
                "credit": (
                        self.payment_type == "outbound" and amount_company_currency or 0.0
                ),
                "debit": (
                        self.payment_type == "inbound" and amount_company_currency or 0.0
                ),
            }
        )
        if bank_lines[0].currency_id != bank_lines[0].company_currency_id:
            sign = self.payment_type == "outbound" and -1 or 1
            vals.update(
                {
                    "currency_id": bank_lines[0].currency_id.id,
                    "amount_currency": amount_payment_currency * sign,
                }
            )
        return vals

    def _prepare_move_line_partner_account(self, bank_line):
        if bank_line.payment_line_ids[0].move_line_id:
            account_id = bank_line.payment_line_ids[0].move_line_id.account_id.id
        else:
            if self.payment_type == "inbound":
                account_id = bank_line.partner_id.property_account_receivable_id.id
            else:
                account_id = bank_line.partner_id.property_account_payable_id.id
        if self.payment_type == "outbound":
            name = _("Payment bank line %s") % bank_line.name
        else:
            name = _("Debit bank line %s") % bank_line.name
        vals = {
            "name": f"{name} - {self.description} - {self.payment_line_ids[0].communication}",
            "bank_payment_line_id": bank_line.id,
            "partner_id": bank_line.partner_id.id,
            "account_id": account_id,
            "credit": (
                    self.payment_type == "inbound"
                    and bank_line.amount_company_currency
                    or 0.0
            ),
            "debit": (
                    self.payment_type == "outbound"
                    and bank_line.amount_company_currency
                    or 0.0
            ),
        }

        if bank_line.currency_id != bank_line.company_currency_id:
            sign = self.payment_type == "inbound" and -1 or 1
            vals.update(
                {
                    "currency_id": bank_line.currency_id.id,
                    "amount_currency": bank_line.amount_currency * sign,
                }
            )
        return vals

    def _create_reconcile_move(self, hashcode, blines):
        self.ensure_one()
        post_move = self.payment_mode_id.post_move
        am_obj = self.env["account.move"]
        mvals = self._prepare_move(blines)
        move = am_obj.create(mvals)
        if post_move:
            move.action_post()
        blines.reconcile_payment_lines()

    def _prepare_trf_moves(self):
        """
        prepare a dict "trfmoves" that can be used when
        self.payment_mode_id.move_option = date or line
        key = unique identifier (date or True or line.id)
        value = bank_pay_lines (recordset that can have several entries)
        """
        self.ensure_one()
        trfmoves = {}
        for bline in self.bank_line_ids:
            hashcode = bline.move_line_offsetting_account_hashcode()
            if hashcode in trfmoves:
                trfmoves[hashcode] += bline
            else:
                trfmoves[hashcode] = bline
        return trfmoves

    def generate_move(self):
        """
        Create the moves that pay off the move lines from
        the payment/debit order.
        """
        self.ensure_one()
        trfmoves = self._prepare_trf_moves()
        for hashcode, blines in trfmoves.items():
            self._create_reconcile_move(hashcode, blines)

    def action_bank_payment_line(self):
        self.ensure_one()
        action = self.env.ref("account_payment_order.bank_payment_line_action")
        action_dict = action.read()[0]
        action_dict["domain"] = [("id", "in", self.bank_line_ids.ids)]
        return action_dict

    def action_move_journal_line(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_journal_line").sudo().read()[0]
        if self.move_count == 1:
            action.update(
                {
                    "view_mode": "form,tree,kanban",
                    "views": False,
                    "view_id": False,
                    "res_id": self.move_ids[0].id,
                }
            )
        else:
            action["domain"] = [("id", "in", self.move_ids.ids)]
        ctx = self.env.context.copy()
        ctx.update({"search_default_misc_filter": 0})
        action["context"] = ctx
        return action

    def action_bank_statements(self):
        self.ensure_one()
        tree_view = self.env.ref(
            "account.view_bank_statement_tree")
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.bank.statement",
            "views": [[tree_view.id, "tree"], [False, "form"]],
            "context": {"create": False},
            'view_mode': 'tree,form',
            "domain": [["payment_request_id", "=", self.id]],
            "name": "Bank Statement",
        }

    @api.depends('payment_line_ids.amount_currency')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.payment_line_ids.mapped('amount_currency'))

    def _convert_num_to_text(self, amount):
        if self.payment_request_type == 'account':
            return amount_to_text_arabic(abs(amount), self.currency_id.name)
        else:
            return amount_to_text_arabic(abs(amount), self.transaction_currency_id.name)

    # def _convert_num_to_text_en(self, amount):
    #     if self.payment_request_type == 'account':
    #         if self.currency_id.name == 'SAR':
    #             x = num2words(abs(amount), to='currency')
    #             x_riyal = x.replace("euro", "Riyal")
    #             real_x = x_riyal.replace("cents", "Halala")
    #             return str(real_x)
    #         else:
    #             x = num2words(abs(amount), to='currency', currency=self.currency_id.name)
    #             return str(x)
    #     else:
    #         if self.transaction_currency_id.name == 'SAR':
    #             x = num2words(abs(amount), to='currency')
    #             x_riyal = x.replace("euro", "Riyal")
    #             real_x = x_riyal.replace("cents", "Halala")
    #             return str(real_x)
    #         else:
    #             x = num2words(abs(amount), to='currency', currency=self.transaction_currency_id.name)
    #             return str(x)
    def _convert_num_to_text_en(self, amount):
        if self.payment_request_type == 'account':
            if self.currency_id.name == 'SAR':
                x = num2words(abs(amount), to='currency')
                x_riyal = x.replace("euro", "Riyal")
                real_x = x_riyal.replace("cents", "Halala")
                return str(real_x)
            elif self.currency_id.name == 'JOD':
                # Custom handling for Jordanian Dinar (JOD)
                return f"{abs(amount):,.2f} Jordanian Dinars"
            else:
                x = num2words(abs(amount), to='currency', currency=self.currency_id.name)
                return str(x)
        else:
            if self.transaction_currency_id.name == 'SAR':
                x = num2words(abs(amount), to='currency')
                x_riyal = x.replace("euro", "Riyal")
                real_x = x_riyal.replace("cents", "Halala")
                return str(real_x)
            elif self.transaction_currency_id.name == 'JOD':
                # Custom handling for Jordanian Dinar (JOD)
                return f"{abs(amount):,.2f} Jordanian Dinars"
            else:
                x = num2words(abs(amount), to='currency', currency=self.transaction_currency_id.name)
                return str(x)

class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'
    payment_request_id = fields.Many2one(comodel_name="account.payment.order")
