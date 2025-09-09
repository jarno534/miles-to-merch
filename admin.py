from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for
from models import db, User, Product, Variant, PrintArea, Design, Order
from wtforms.fields import BooleanField
from flask_admin.actions import action
from flask import flash
from markupsafe import Markup

class SecuredModelView(ModelView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return user and user.is_admin
        return False
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return user and user.is_admin
        return False
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

class InspirationAdminView(SecuredModelView):
    def _image_formatter(view, context, model, name):
        if not model.preview_urls or not isinstance(model.preview_urls, dict):
            return ''

        main_preview_filename = model.preview_urls.get('front')
        if not main_preview_filename:
            return 'Geen preview'

        url = url_for('static', filename=f'uploads/previews/{main_preview_filename}')
        return Markup(f'<a href="{url}" target="_blank"><img src="{url}" width="100"></a>')

    column_list = ('preview_urls', 'name', 'user.email', 'product.name', 'created_at')
    column_labels = {'preview_urls': 'Preview'}
    column_formatters = {'preview_urls': _image_formatter}

    can_create = False
    can_edit = False
    can_delete = False

class UserAdminView(SecuredModelView):
    def _designs_link(view, context, model, name):
        count = len(model.designs)
        if count == 0: return "0 Designs"
        url = url_for('design.index_view', flt1_user_id_equals=model.id)
        return Markup(f'<a href="{url}">{count} Designs</a>')

    def _orders_link(view, context, model, name):
        count = len(model.orders)
        if count == 0: return "0 Orders"
        url = url_for('order.index_view', flt1_user_id_equals=model.id)
        return Markup(f'<a href="{url}">{count} Orders</a>')

    column_list = ('email', 'name', 'strava_name', 'is_admin', 'strava_id', 'shipping_city', 'shipping_country', 'designs', 'orders')
    column_formatters = {'designs': _designs_link, 'orders': _orders_link}
    column_searchable_list = ['email', 'name', 'strava_name', 'shipping_city', 'shipping_country']
    column_filters = ['is_admin', 'shipping_country']
    form_columns = ('email', 'name', 'is_admin', 'strava_id', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country')
    column_details_list = ('id', 'email', 'name', 'is_admin', 'strava_id', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country', 'designs', 'orders')

class ProductAdminView(SecuredModelView):
    def _variants_link(view, context, model, name):
        count = model.variants.count()
        if count == 0: return "0 Varianten"
        url = url_for('variant.index_view', flt1_product_id_equals=model.id)
        return Markup(f'<a href="{url}">{count} Varianten</a>')

    def _print_areas_link(view, context, model, name):
        count = len(model.print_areas)
        if count == 0: return "0 Vlakken"
        url = url_for('printarea.index_view', flt1_product_id_equals=model.id)
        return Markup(f'<a href="{url}">{count} Vlakken</a>')

    column_list = ('name', 'printful_product_id', 'variants', 'print_areas')
    column_formatters = {
        'variants': '_variants_link',
        'print_areas': '_print_areas_link'
    }
    column_searchable_list = ['name']
    form_columns = ('name', 'description', 'printful_product_id')

class VariantAdminView(SecuredModelView):
    column_list = ('product.name', 'color', 'size', 'price', 'is_active', 'merch_color_type', 'printful_variant_id')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name', 'merch_color_type']
    column_searchable_list = ['color', 'size', 'product.name']
    page_size = 100

    @action('activate', 'Activeer', 'Geselecteerde varianten activeren?')
    def action_activate(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)); variants.update({'is_active': True}); db.session.commit()
            flash(f"{len(ids)} varianten geactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

    @action('deactivate', 'Deactiveer', 'Geselecteerde varianten deactiveren?')
    def action_deactivate(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)); variants.update({'is_active': False}); db.session.commit()
            flash(f"{len(ids)} varianten gedeactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

    @action('set_dark_type', 'Stel in als \'donker\'', 'Geselecteerde varianten instellen als \'donker\'?')
    def action_set_dark_type(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)); variants.update({'merch_color_type': 'dark'}); db.session.commit()
            flash(f"{len(ids)} varianten ingesteld als 'donker'.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

    @action('set_light_type', 'Stel in als \'licht\'', 'Geselecteerde varianten instellen als \'licht\'?')
    def action_set_light_type(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)); variants.update({'merch_color_type': 'light'}); db.session.commit()
            flash(f"{len(ids)} varianten ingesteld als 'licht'.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

class PrintAreaAdminView(SecuredModelView):
    column_list = ('product.name', 'name', 'placement', 'price', 'width', 'height')
    column_filters = ['product.name']
    form_columns = ('product', 'placement', 'name', 'price', 'width', 'height', 'top', 'left', 'mockup_width', 'mockup_height', 'image_url')

class DesignAdminView(SecuredModelView):
    def _image_formatter(view, context, model, name):
        if not model.preview_urls or not isinstance(model.preview_urls, dict):
            return ''
        main_preview_filename = model.preview_urls.get('front')
        if not main_preview_filename:
            available_previews = ", ".join(model.preview_urls.keys())
            return f'Previews: {available_previews}'
        url = url_for('static', filename=f'uploads/previews/{main_preview_filename}')
        return Markup(f'<a href="{url}" target="_blank"><img src="{url}" width="100"></a>')

    column_list = ('preview_urls', 'name', 'user.email', 'product.name', 'variant.color', 'variant.size', 'created_at')
    column_labels = {'preview_urls': 'Preview'}
    column_formatters = {'preview_urls': _image_formatter}
    column_searchable_list = ['name', 'user.email', 'product.name']
    column_default_sort = ('created_at', True)
    column_filters = ['user.email', 'product.name']
    form_columns = ('name', 'user', 'product', 'variant', 'preview_urls')

class OrderAdminView(SecuredModelView):
    column_list = ('id', 'user.email', 'design.name', 'order_date', 'total_price', 'order_status', 'shipping_city')
    column_filters = ['order_status', 'user.email', 'shipping_city']
    column_default_sort = ('order_date', True)
    form_columns = ('user', 'design', 'quantity', 'order_status', 'total_price', 'shipping_name', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country')


def setup_admin(app):
    admin = Admin(app, name='Miles-to-Merch Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

    admin.add_view(InspirationAdminView(Design, db.session, name='Inspiratie', endpoint='inspiration', category='Tools'))

    admin.add_view(UserAdminView(User, db.session, category='Gebruikers'))
    admin.add_view(DesignAdminView(Design, db.session, category='Gebruikers'))
    admin.add_view(OrderAdminView(Order, db.session, category='Gebruikers'))
    admin.add_view(ProductAdminView(Product, db.session, category='Producten'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Producten'))
    admin.add_view(PrintAreaAdminView(PrintArea, db.session, category='Producten'))