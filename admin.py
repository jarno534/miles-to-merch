# In admin.py
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
        return Markup(f'<a href="/admin/design/?flt1_0={model.id}">{len(model.designs)} Designs</a>')
    def _orders_link(view, context, model, name):
        return Markup(f'<a href="/admin/order/?flt1_0={model.id}">{len(model.orders)} Orders</a>')
        
    column_list = ('email', 'name', 'is_admin', 'designs', 'orders')
    column_searchable_list = ['email', 'name']
    column_filters = ['is_admin']
    column_formatters = {'designs': _designs_link, 'orders': _orders_link}
    form_columns = ('email', 'name', 'is_admin', 'shipping_address', 'shipping_city', 'shipping_zip', 'shipping_country')
    form_excluded_columns = ['password_hash']

class ProductAdminView(SecuredModelView):
    column_list = ('name', 'printful_product_id', 'variants')
    column_searchable_list = ['name']
    form_columns = ('name', 'description', 'printful_product_id')

class VariantAdminView(SecuredModelView):
    form_overrides = {'is_active': BooleanField}
    column_list = ('product.name', 'color', 'size', 'price', 'is_active')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name']
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

class OrderAdminView(SecuredModelView):
    column_list = ('id', 'user.email', 'order_date', 'total_price', 'order_status')
    column_filters = ['order_status', 'user.email']
    column_default_sort = ('order_date', True)

def setup_admin(app):
    admin = Admin(app, name='Miles-to-Merch Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(UserAdminView(User, db.session, category='Gebruikers'))
    admin.add_view(DesignAdminView(Design, db.session, category='Gebruikers'))
    admin.add_view(OrderAdminView(Order, db.session, category='Gebruikers'))
    admin.add_view(ProductAdminView(Product, db.session, category='Producten'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Producten'))
    admin.add_view(PrintAreaAdminView(PrintArea, db.session, category='Producten'))