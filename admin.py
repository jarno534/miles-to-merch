# In admin.py
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect
from models import db, User, Product, Variant, PrintArea, Design, Order
from wtforms.fields import BooleanField
from flask_admin.actions import action
from flask import flash

class SecuredModelView(ModelView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_admin:
                return True
        return False
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_admin:
                return True
        return False
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

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
            variants_to_activate = Variant.query.filter(Variant.id.in_(ids)).all()
            for variant in variants_to_activate:
                variant.is_active = True
            db.session.commit()
            flash(f"{len(variants_to_activate)} varianten succesvol geactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')
    @action('deactivate', 'Deactiveer op site', 'Geselecteerde varianten deactiveren?')
    def action_deactivate(self, ids):
        try:
            variants_to_deactivate = Variant.query.filter(Variant.id.in_(ids)).all()
            for variant in variants_to_deactivate:
                variant.is_active = False
            db.session.commit()
            flash(f"{len(variants_to_deactivate)} varianten succesvol gedeactiveerd.", 'success')
        except Exception as e: flash(f"Fout: {e}", 'error')

class PrintAreaAdminView(SecuredModelView):
    column_list = ('product.name', 'name', 'placement', 'price', 'width', 'height', 'top', 'left')
    column_editable_list = ['price', 'width', 'height', 'top', 'left']
    column_filters = ['product.name']
    form_columns = ('product', 'placement', 'name', 'price', 'width', 'height', 'top', 'left', 'mockup_width', 'mockup_height')

class UserAdminView(SecuredModelView):
    column_list = ('id', 'email', 'name', 'is_admin')
    column_searchable_list = ['email', 'name']
    form_excluded_columns = ['password_hash', 'designs', 'orders']

class OrderAdminView(SecuredModelView):
    column_list = ('id', 'user.name', 'order_date', 'total_price', 'order_status')
    column_filters = ['order_status']
    column_default_sort = ('order_date', True)

class DesignAdminView(SecuredModelView):
    column_list = ('id', 'name', 'user.name', 'product.name', 'created_at')
    column_searchable_list = ['name', 'user.name', 'product.name']
    column_default_sort = ('created_at', True)

def setup_admin(app):
    admin = Admin(app, name='Miles-to-Merch Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(UserAdminView(User, db.session, category='Beheer'))
    admin.add_view(OrderAdminView(Order, db.session, category='Beheer'))
    admin.add_view(DesignAdminView(Design, db.session, category='Beheer'))
    admin.add_view(ProductAdminView(Product, db.session, category='Catalogus'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Catalogus'))
    admin.add_view(PrintAreaAdminView(PrintArea, db.session, category='Catalogus'))