# In admin.py

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect
from models import db, User, Product, Variant, Design, Order
from wtforms.fields import BooleanField # <-- NIEUWE IMPORT

# --- Beveiliging van het Admin Panel ---
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

# --- Verbeterde Views voor je Modellen ---

class ProductAdminView(SecuredModelView):
    # Toont nu een gedetailleerde weergave met alle varianten als je op een product klikt
    column_list = ('name', 'printful_product_id', 'base_price', 'variants')
    column_searchable_list = ['name']
    column_editable_list = ['base_price', 'additional_price_per_area']
    # Definieert de velden voor het aanmaken/bewerken van een product
    form_columns = ('name', 'description', 'printful_product_id', 'base_price', 'additional_price_per_area')
    # Maakt de kolomkoppen gebruiksvriendelijker
    column_labels = dict(printful_product_id='Printful ID', base_price='Basisprijs (€)', additional_price_per_area='Extra Prijs per Zone (€)')

class VariantAdminView(SecuredModelView):
    # --- DE CRUCIALE FIX ---
    # Vertelt Flask-Admin expliciet om een BooleanField widget te gebruiken voor is_active.
    # Dit zorgt ervoor dat het vinkje correct wordt opgeslagen.
    form_overrides = {
        'is_active': BooleanField
    }
    # --- EINDE FIX ---
    
    column_list = ('product.name', 'color', 'size', 'price', 'is_active')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name']
    column_searchable_list = ['color', 'size', 'product.name']
    # Definieert de velden voor het aanmaken/bewerken van een variant
    form_columns = ('product', 'printful_variant_id', 'color', 'size', 'price', 'merch_color_type', 'print_areas', 'available_regions', 'is_active')
    column_labels = dict(product.name='Product', is_active='Actief op site?', price='Prijs (€)')
    page_size = 100

class UserAdminView(SecuredModelView):
    column_list = ('id', 'email', 'name', 'is_admin')
    column_searchable_list = ['email', 'name']
    column_filters = ['is_admin']
    form_excluded_columns = ['password_hash', 'designs', 'orders'] # Verbergt onnodige velden in het bewerk-formulier
    column_labels = dict(is_admin='Is Admin?')

class OrderAdminView(SecuredModelView):
    column_list = ('id', 'user.name', 'order_date', 'total_price', 'order_status', 'printful_order_status')
    column_filters = ['order_status', 'printful_order_status']
    column_default_sort = ('order_date', True)
    column_labels = dict(user.name='Klant', order_date='Datum', total_price='Totaalprijs (€)', order_status='Status', printful_order_status='Printful Status')

class DesignAdminView(SecuredModelView):
    column_list = ('id', 'name', 'user.name', 'product.name', 'created_at')
    column_searchable_list = ['name', 'user.name', 'product.name']
    column_default_sort = ('created_at', True)
    column_labels = dict(user.name='Gebruiker', product.name='Product', created_at='Aangemaakt op')

# --- Setup Functie ---
def setup_admin(app):
    admin = Admin(
        app, 
        name='Miles-to-Merch Admin', 
        template_mode='bootstrap3', 
        index_view=MyAdminIndexView()
    )
    
    admin.add_view(UserAdminView(User, db.session, category='Beheer'))
    admin.add_view(OrderAdminView(Order, db.session, category='Beheer'))
    admin.add_view(DesignAdminView(Design, db.session, category='Beheer'))
    admin.add_view(ProductAdminView(Product, db.session, category='Catalogus'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Catalogus'))