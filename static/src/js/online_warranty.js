odoo.define('product_warranty.warranty', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
     var Dialog = require('web.Dialog');
     var _t = require('web.core')._t;
     var qweb = require('web.core').qweb;
     var session = require('web.session');
     var rpc = require('web.rpc');

    publicWidget.registry.WarrantyDetails = publicWidget.Widget.extend({
        selector: '#warranty',
        events: {
            'change select[name="invoice_id"]': 'on_invoice_change',
        },
        on_invoice_change: function (ev) {
        var invoiceId = $(ev.currentTarget).val();
        if (invoiceId) {
            rpc.query({
                model: 'product.warranty.model',
                method: 'get_product_options',
                args: [invoiceId],
            }).then(function (result) {
                var productOptions = result.options || [];
                console.log("Received product ID:", productOptions);
                var optionsHtml = '<option value="">Select product</option>';
                for (var i = 0; i < productOptions.length; i++) {
                    optionsHtml += '<option value="' + productOptions[i][0] + '">' + productOptions[i][1] + '</option>';
                    var productOption =  productOptions[i][1]
                }
                $("#products").html(optionsHtml);
            }).catch(function (error) {
                console.error('RPC Error:', error);
            });

        } else {
            $('select[name="products"]').html('<option value="">Select invoice first</option>');
        }
    },
     })
    });




