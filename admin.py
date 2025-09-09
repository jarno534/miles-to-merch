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

class UserAdminView(SecuredModelView):
    def _designs_link(view, context, model, name):
        design_count = len(model.designs)
        if design_count == 0:
            return "0 Designs"
        url = url_for('design.index_view', flt1_user_id_equals=model.id)
        return Markup(f'<a href="{url}">{design_count} Designs</a>')

    def _orders_link(view, context, model, name):
        order_count = len(model.orders)
        if order_count == 0:
            return "0 Orders"
        url = url_for('order.index_view', flt1_user_id_equals=model.id)
        return Markup(f'<a href="{url}">{order_count} Orders</a>')

    column_list = ('email', 'name', 'is_admin', 'designs', 'orders')
    column_formatters = {
        'designs': _designs_link,
        'orders': _orders_link
    }
    column_searchable_list = ['email', 'name']
    column_filters = ['is_admin']
    form_columns = ('email', 'name', 'is_admin', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country')

class ProductAdminView(SecuredModelView):
    column_list = ('name', 'printful_product_id')
    column_searchable_list = ['name']
    form_columns = ('name', 'description', 'printful_product_id')

class VariantAdminView(SecuredModelView):
    column_list = ('product.name', 'color', 'size', 'price', 'is_active', 'merch_color_type')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name', 'merch_color_type']
    column_searchable_list = ['color', 'size', 'product.name']
    page_size = 100

    @action('activate', 'Activeer op site', 'Geselecteerde varianten activeren?')
    def action_activate(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)).all()
            for v in variants: v.is_active = True
            db.session.commit()
            flash(f"{len(variants)} varianten succesvol geactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

    @action('deactivate', 'Deactiveer op site', 'Geselecteerde varianten deactiveren?')
    def action_deactivate(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)).all()
            for v in variants: v.is_active = False
            db.session.commit()
            flash(f"{len(variants)} varianten succesvol gedeactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

    @action('set_dark_type', 'Stel in als \'donker\'', 'Geselecteerde varianten instellen als \'donker\'?')
    def action_set_dark_type(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)).all()
            for v in variants: v.merch_color_type = 'dark'
            db.session.commit()
            flash(f"{len(variants)} varianten ingesteld als 'donker'.", 'success')
        except Exception as e:
            flash(f"Kon type niet instellen: {e}", 'error')
            db.session.rollback()

    @action('set_light_type', 'Stel in als \'licht\'', 'Geselecteerde varianten instellen als \'licht\'?')
    def action_set_light_type(self, ids):
        try:
            variants = Variant.query.filter(Variant.id.in_(ids)).all()
            for v in variants: v.merch_color_type = 'light'
            db.session.commit()
            flash(f"{len(variants)} varianten ingesteld als 'licht'.", 'success')
        except Exception as e:
            flash(f"Kon type niet instellen: {e}", 'error')
            db.session.rollback()

class PrintAreaAdminView(SecuredModelView):
    column_list = ('product.name', 'name', 'placement', 'price', 'width', 'height', 'top', 'left')
    column_editable_list = ['price', 'width', 'height', 'top', 'left']
    column_filters = ['product.name']
    form_columns = ('product', 'placement', 'name', 'price', 'width', 'height', 'top', 'left', 'mockup_width', 'mockup_height')

class DesignAdminView(SecuredModelView):
    column_list = ('id', 'name', 'user.email', 'product.name', 'created_at')
    column_searchable_list = ['name', 'user.email', 'product.name']
    column_default_sort = ('created_at', True)
    column_filters = ['user.email', 'product.name']
    # --- TOEGEVOEGD: Oplossing voor de Internal Server Error ---
    form_columns = ('name', 'user', 'product', 'variant', 'preview_url')


class OrderAdminView(SecuredModelView):
    column_list = ('id', 'user.email', 'order_date', 'total_price', 'order_status')
    column_filters = ['order_status', 'user.email']
    column_default_sort = ('order_date', True)
    form_columns = ('user', 'design', 'quantity', 'order_status', 'total_price', 'shipping_name', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country')

def setup_admin(app):
    admin = Admin(app, name='Miles-to-Merch Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

    admin.add_view(UserAdminView(User, db.session, category='Gebruikers'))
    admin.add_view(DesignAdminView(Design, db.session, category='Gebruikers'))
    admin.add_view(OrderAdminView(Order, db.session, category='Gebruikers'))

    admin.add_view(ProductAdminView(Product, db.session, category='Producten'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Producten'))
    admin.add_view(PrintAreaAdminView(PrintArea, db.session, category='Producten'))