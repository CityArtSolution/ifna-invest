odoo.define('web_hijri_datepicker.datepicker', function (require) {
    "use strict";

    var core = require('web.core');
    var datepicker = require('web.datepicker');
    var time = require('web.time');

    var _t = core._t;

    var hijriMonths = {
        "Muharram": "‎مُحَرَّم",
        "Safar": "‎صَفَر",
        "Rabi' al-awwal": "‎رَبِيْعُ الأَوّل",
        "Rabi' al-thani": "‎رَبِيْعُ الثَّانِي",
        "Jumada al-awwal": "‎جَمَادِي الأَوّل",
        "Jumada al-thani": "‎جَمَادِي الثَّانِي",
        "Rajab": "‎رَجَب",
        "Sha'aban": "‎شَعْبَان",
        "Ramadan": "‎رَمَضَان",
        "Shawwal": "‎شَوَّال",
        "Dhu al-Qi'dah": "‎ذُوالْقَعْدَة",
        "Dhu al-Hijjah": "‎ذُوالْحِجَّة"
    }

    String.prototype.fromDigits = function () {
        var id = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
        return this.replace(/[0-9]/g, function (w) {
            return id[+w]
        });
    }
    var fixNumbers = function (str){
        var arabicNumbers  = [/٠/g, /١/g, /٢/g, /٣/g, /٤/g, /٥/g, /٦/g, /٧/g, /٨/g, /٩/g];
        var enNumbers  = [/0/g, /1/g, /2/g, /3/g, /4/g, /5/g, /6/g, /7/g, /8/g, /9/g];
      if(typeof str === 'string')
          {
            for(var i=0; i<10; i++)
            {
              str = str.replace(arabicNumbers[i], i).replace(enNumbers[i], i);
            }
          }
          return str;
    };

    datepicker.DateWidget.include({
        start: function () {
            var self = this;
            this.$input = this.$('input.o_datepicker_input');
            this.$input_hijri = this.$('input.o_hijri');
            this.$spanDisplay_hijri = this.$('span.hijridisplay');
            this.$spanDisplay_hijri.click(function (e) {
                e.preventDefault();
                self.$input_hijri.calendarsPicker('show');
            });
            this.$input.focus(function(e) {
                e.preventDefault();
                e.stopImmediatePropagation();
                var parsed_date = self.$input.val() ? self._parseDate(self._parseClient(self.$input.val())) : null;

                //omara now

                  var confert_date = Date.parse(parsed_date) ;
             confert_date = new Date(confert_date) ;
             confert_date =  new Date(confert_date.setDate (confert_date.getDate() - 1));//subtract 1 day from it
             confert_date =  moment(confert_date).format('YYYY-MM-DD');
//             confert_date = confert_date.toLocaleString();//subtract 1 day from it
//            parsed_date = confert_date;
            console.log('parsed_dateii converted to date',typeof confert_date);
            console.log('parsed_dateii converted to date', confert_date);

//now
//                if (parsed_date){
//                    parsed_date =confert_date;
//                }

                //

                var hijri_value = parsed_date ? self._convertGregorianToHijri(parsed_date)['hijri_value_month_name'] : null;
               console.log('hijri_value',hijri_value);
               //omara now
                self.$input_hijri.val(hijri_value);
            });
            this.$input_hijri.calendarsPicker({
                onSelect: this._convertDateToHijri.bind(this),
                calendar: $.calendars.instance('islamic', this.options.locale),
                closeText : '',
                clearText : '',
                nextText : '>',
                prevText : '<',
                showAnim : "slideDown",
                showOptions: { direction: "up" },
                showSpeed: 'fast',
            });
            this.__libInput++;
            this.$el.datetimepicker(this.options);
            this.__libInput--;
            this._setReadonly(false);
        },
        _convertGregorianToHijri: function (date) {
            console.log('date greo',date);
            var year, month, day, jd, formatted_date;
            var calendar = $.calendars.instance('islamic');
            if (date && !_.isUndefined(date)) {
                date = moment(date).locale('en');
                month = parseInt(date.format('M'));
                //omara as some cases that gerogrian date not available and causes error


                day = parseInt(date.format('D'));//omara -1
                year = parseInt(date.format('YYYY'));

                jd = $.calendars.instance('gregorian').toJD(year, month, day);
                formatted_date = calendar.fromJD(jd);
                var month = calendar.formatDate('MM', formatted_date);
                var year = calendar.formatDate('YYYY', formatted_date);
                var day = calendar.formatDate('d', formatted_date);//omara -1


                if (this.options.locale == 'ar') {
                    month = _.find(hijriMonths, function (value, key) {
                        if (key === month) {
                            return value;
                        }
                    });
                }
                var hijri_value_date_format = _.str.sprintf("%s/%s/%s", year,calendar.formatDate('mm', formatted_date),day );
                var hichri_value_month_name = _.str.sprintf("%s %s %s", day,month,year );
                return {'hijri_value_month_name':hichri_value_month_name,
                        'hijri_value_date_format' :hijri_value_date_format
                        }

         //omara
            }
        },
        _convertDateToHijri: function (date) {
        console.log('datedate',date);
        console.log('datedate',typeof date);

        //omara just subtract 1 day from date
        //if has an error let it work as it was that show the day after one user selected
//                   try{

                   //omara only one line added in this function and try & catch
                console.log('date[0]._day',date);
                if (date[0]._day>1){
                  date[0]._day= date[0]._day-1;
                  }



           if (!date || date.length === 0) {
                return false;
            }

            $(document).on('click', '.calendars a', function (e) {
                e.preventDefault();
                e.stopImmediatePropagation();
                return false;
            });

            var jd = $.calendars.instance('islamic').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
            var formatted_date = $.calendars.instance('gregorian').fromJD(jd);
            console.log('formatted_date',formatted_date);

            if (this.type_of_date === 'datetime'){
                if (!this.get('value')){
                    this.set({'value': moment(time.str_to_datetime(formatted_date + " 00:00:00"))});
                }
                var current_time = this.getValue().format("HH:mm:ss");
                if (this.options.locale == 'ar') {
                    current_time = fixNumbers(this.getValue().format("HH:mm:ss"));
                }
                if (typeof(current_time) != 'undefined'){
                    formatted_date = formatted_date+ ' ' + current_time;
                    var date_value = moment(time.str_to_datetime(formatted_date)).add(1, 'days');
                }
                else{
                    var date_value = moment(time.str_to_date(formatted_date)).add(1, 'days');
                }
            }
            else {
                var date_value = moment(time.str_to_date(formatted_date)).add(1, 'days');;
            }
            this.setValue(this._parseClient(date_value));
            this.trigger("datetime_changed");

//                  }
//                  catch (e){
//
//
//
//
//                              if (!date || date.length === 0) {
//                return false;
//            }
//
//            $(document).on('click', '.calendars a', function (e) {
//                e.preventDefault();
//                e.stopImmediatePropagation();
//                return false;
//            });
//
//            var jd = $.calendars.instance('islamic').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
//            var formatted_date = $.calendars.instance('gregorian').fromJD(jd);
//            console.log('formatted_date',formatted_date);
//
//            if (this.type_of_date === 'datetime'){
//                if (!this.get('value')){
//                    this.set({'value': moment(time.str_to_datetime(formatted_date + " 00:00:00"))});
//                }
//                var current_time = this.getValue().format("HH:mm:ss");
//                if (this.options.locale == 'ar') {
//                    current_time = fixNumbers(this.getValue().format("HH:mm:ss"));
//                }
//                if (typeof(current_time) != 'undefined'){
//                    formatted_date = formatted_date+ ' ' + current_time;
//                    var date_value = moment(time.str_to_datetime(formatted_date)).add(1, 'days');
//                }
//                else{
//                    var date_value = moment(time.str_to_date(formatted_date)).add(1, 'days');
//                }
//            }
//            else {
//                var date_value = moment(time.str_to_date(formatted_date)).add(1, 'days');;
//            }
//            this.setValue(this._parseClient(date_value));
//            this.trigger("datetime_changed");
//
//
//                  }

        //omara stopped not working correct
/*
        console.log('date fter subtt',date);
        var m = moment( date[0]._year+'/'+date[0]._month+'/'+date[0]._day, 'iYYYY/iM/iD').subtract(1, "days");

            //prepare hijri date valus

            var date_too = date;
            date_too[0]._day= m.day();
            date_too[0]._month= m.month();
            date_too[0]._year= m.year();

            date = date_too;

         console.log('date fter subtt lasssst',date_too);
         console.log('datetoo fter subtt lasssst',date);
*/
//omara


        },
        _parseDate: function (v) {
            return v.clone().locale('en').format('YYYY-MM-DD');
        },



        setValue: function (value) {
        console.log('value1',value);
            this._super.apply(this, arguments);
            var parsed_date = value ? this._parseDate(value) : null;
            console.log('parsed_dateii',parsed_date);
            console.log('parsed_dateii',typeof parsed_date);

            var confert_date = Date.parse(parsed_date) ;
             confert_date = new Date(confert_date) ;
             confert_date =  new Date(confert_date.setDate (confert_date.getDate() - 1));//subtract 1 day from it
             confert_date =  moment(confert_date).format('YYYY-MM-DD');
//             confert_date = confert_date.toLocaleString();//subtract 1 day from it
//            parsed_date = confert_date;
            console.log('parsed_dateii converted to date',typeof confert_date);
            console.log('parsed_dateii converted to date', confert_date);

//now
//            if (parsed_date){
//                parsed_date =confert_date;
//            }


            var hijri_value = parsed_date ? this._convertGregorianToHijri(parsed_date)['hijri_value_month_name'] : null;
            var hijri_value_date_format = parsed_date ? this._convertGregorianToHijri(parsed_date)['hijri_value_date_format'] : null;
            this.$input_hijri.val(hijri_value_date_format)
            this.$el.find('.hijridisplay').text(hijri_value);

                    console.log('value2',hijri_value);
                    console.log('value3',hijri_value_date_format);

        },
        destroy: function () {
            if (this.$el) {
                this.__libInput++;
                this.$el.datetimepicker('destroy');
                this.__libInput--;
            }
        },
        _onInputClicked: function (e) {
            if (e && e.target && ! $(e.target).hasClass('o_hijri')){
                return this._super();
            }
        },
    });
});
