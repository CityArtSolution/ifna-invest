odoo.define('pj_dashboard.Dashboard', function(require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;
    var session = require('web.session');
    var web_client = require('web.web_client');
    var flag = 0;
    var tot_so = [];
    var tot_consultation = [];
    var tot_auth_agen = [];
    var tot_client = [];
    var tot_decisions = [];
    var tot_opened_case = [];
    var tot_request = [];
    var tot_paid = [];
    var tot_unpaid = [];
    var tot_margin = [];

    var PjDashboard = AbstractAction.extend({
        template: 'PjDashboard',

        events: {
            'click .tot_consultations': 'tot_consultations',
            'click .tot_auths_agens': 'tot_auths_agens',
            'click .tot_decisions': 'tot_decisions',
            'click .tot_opened_cases': 'tot_opened_cases',
            'click .tot_requests': 'tot_requests',
            'click .tot_paids': 'tot_paids',
            'click .tot_unpaids': 'tot_unpaids',
            'click .tot_sale': 'tot_sale',
            'click .tot_client': 'tot_client',
        },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['LegalCaseDashboard'];
            this.today_sale = [];
        },

        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function() {
                return self.fetch_data();
            });
        },

        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
            });
        },

        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_pj_dashboard').append(QWeb.render(template, {
                    widget: self
                }));
            });
        },

        on_reverse_breadcrumb: function() {
            var self = this;
            web_client.do_push_state({});
            this.fetch_data().then(function() {
                self.$('.o_pj_dashboard').empty();
                self.render_dashboards();
            });
        },

        // The rest of the methods go here...
        fetch_data: function() {
            var self = this;
            var def1 = this._rpc({
                model: 'legal.case',
                method: 'get_tiles_data'
            }).then(function(result) {
                self.total_consultations = result['total_consultations'];
                self.total_auths_agens = result['total_auths_agens'];
                self.total_decisions = result['total_decisions'];
                self.total_opened_cases = result['total_opened_cases'];
                self.total_requests = result['total_requests'];
                self.total_paids = result['total_paids'];
                self.total_unpaids = result['total_unpaids'];
                self.total_profitability = result['total_profitability'];
                self.total_clients = result['total_clients'];
            });

            var def2 = self._rpc({
                model: "legal.case",
                method: "get_legal_case_data",
            }).then(function(res) {
                self.case_data = res['case_data'];
            });
            return $.when(def1, def2);
        },

        /**
        for opening project view
        */
        tot_consultations: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Consultations"),
                    type: 'ir.actions.act_window',
                    res_model: 'external.legal.consultation',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options)
            } else {
                if (tot_consultation) {
                    this.do_action({
                        name: _t("Consultations"),
                        type: 'ir.actions.act_window',
                        res_model: 'external.legal.consultation',
                        domain: [
                            ["id", "in", tot_consultation]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

        /**
        for opening project task view
        */
        tot_auths_agens: function(e) {
                var self = this;
                e.stopPropagation();
                e.preventDefault();
                var options = {
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                };
                if (flag == 0) {
                    this.do_action({
                        name: _t("Authorizations & Agencies"),
                        type: 'ir.actions.act_window',
                        res_model: 'legal.authorization.agency',
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                } else {
                    if (tot_auth_agen) {
                        this.do_action({
                            name: _t("Authorizations & Agencies"),
                            type: 'ir.actions.act_window',
                            res_model: 'legal.authorization.agency',
                            domain: [
                                ["id", "in", tot_auth_agen]
                            ],
                            view_mode: 'tree,form',
                            views: [
                                [false, 'list'],
                                [false, 'form']
                            ],
                            target: 'current'
                        }, options)
                    }
                }
            },

        /**
        for opening account analytic line view
        */
        tot_decisions: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Board Decisions"),
                    type: 'ir.actions.act_window',
                    res_model: 'legal.board.decision',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options)
            } else {
                if (tot_decisions) {
                    this.do_action({
                        name: _t("Board Decisions"),
                        type: 'ir.actions.act_window',
                        res_model: 'legal.board.decision',
                        domain: [
                            ["id", "in", tot_decisions]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

         /**
        for opening opened cases view
        */
        tot_opened_cases: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Legal Opened Cases"),
                    type: 'ir.actions.act_window',
                    res_model: 'legal.case',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                    domain: [["case_status", "=", "open"]]
                }, options)
            } else {
                if (tot_opened_case) {
                    this.do_action({
                        name: _t("Legal Opened Cases"),
                        type: 'ir.actions.act_window',
                        res_model: 'legal.case',
                        domain: [
                            ["id", "in", tot_opened_case],
                            ["case_status", "=", "open"]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

        /**
        for opening Execution Requests view
        */
        tot_requests: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Execution Requests"),
                    type: 'ir.actions.act_window',
                    res_model: 'legal.execution.request',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options)
            } else {
                if (tot_request) {
                    this.do_action({
                        name: _t("Execution Requests"),
                        type: 'ir.actions.act_window',
                        res_model: 'egal.execution.request',
                        domain: [
                            ["id", "in", tot_request]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

       /**
        for opening Paid Execution Requests view
        */
        tot_paids: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Paid Execution Requests"),
                    type: 'ir.actions.act_window',
                    res_model: 'legal.execution.request',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                    domain: [["state", "=", "paid"]]
                }, options)
            } else {
                if (tot_paid) {
                    this.do_action({
                        name: _t("Paid Execution Requests"),
                        type: 'ir.actions.act_window',
                        res_model: 'legal.execution.request',
                        domain: [
                            ["id", "in", tot_paid],
                            ["state", "=", "paid"]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

        /**
        for opening Not Paid Execution Requests view
        */
        tot_unpaids: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Paid Execution Requests"),
                    type: 'ir.actions.act_window',
                    res_model: 'legal.execution.request',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                    domain: [["state", "=", "not_paid"]]
                }, options)
            } else {
                if (tot_unpaid) {
                    this.do_action({
                        name: _t("Paid Execution Requests"),
                        type: 'ir.actions.act_window',
                        res_model: 'legal.execution.request',
                        domain: [
                            ["id", "in", tot_unpaid],
                            ["state", "=", "not_paid"]
                        ],
                        view_mode: 'tree,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options)
                }
            }
        },

        /**
        for opening hr employee view
        */
        tot_client: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (flag == 0) {
                this.do_action({
                    name: _t("Defendants"),
                    type: 'ir.actions.act_window',
                    res_model: 'res.partner',
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: [['is_legal_defendant', '=', true]],
                    target: 'current'
                }, options)
            } else {
                this.do_action({
                    name: _t("Defendants"),
                    type: 'ir.actions.act_window',
                    res_model: 'res.partner',
                    domain: [
                        ["id", "in", tot_client]
                    ],
                    view_mode: 'tree,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: [['is_legal_defendant', '=', true]],
                    target: 'current'
                }, options)

            }
        },

    });

    core.action_registry.add('project_dashboard', PjDashboard);

    return PjDashboard;
});
