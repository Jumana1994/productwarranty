odoo.define('product_warranty.warranty_snippet', function (require) {
    var PublicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var qweb = require('web.core').qweb;
    var session = require('web.session');

    var Dynamic = PublicWidget.Widget.extend({
        selector: '#dynamic_snippet_blog',
        start: function () {
            var self = this;
            rpc.query({
                route: '/warranty_products',
            }).then((data) => {
                this.data = data;
                var chunks = _.chunk(this.data, 4)
                chunks[0].is_active = true
                this.$el.find('#courosel').html(
                    qweb.render('product_warranty.dynamic_carousel', {
                        chunks: chunks
                    })
                );
            }).catch(function (error) {
                console.error('RPC Error:', error);
            });
        }
    });

    PublicWidget.registry.dynamic_snippet_blog = Dynamic;
    return Dynamic;
});

