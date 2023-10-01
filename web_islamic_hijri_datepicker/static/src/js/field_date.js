odoo.define('web_hijri_datepicker.FieldDate', function (require) {
    "use strict";

    var FieldDate = require('web.basic_fields').FieldDate;

    FieldDate.include({
        _renderReadonly: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.value) {
                this.datewidget = this._makeDatePicker();
                var $div = $('<div/>');
                $div.addClass(this.$el.attr('class'));
                var value = this.value ? this.datewidget._formatClient(this.value) : '';
                var parsed_date = this.value ? this.datewidget._parseDate(this.value) : '';
                var hijri_value = parsed_date ? this.datewidget._convertGregorianToHijri(parsed_date)['hijri_value_month_name'] : '';
                $('<div>', {
                    class: this.$el.attr('class'),
                    text: this.$el.text(),
                }).appendTo($div);
                $('<div>', {
                    class: this.$el.attr('class') + ' hijri_value',
                    text: hijri_value,
                }).appendTo($div);

                this.datewidget.appendTo('<div>').then(function () {
                    self._replaceElement($div);
                });
            }
        },
    })

});