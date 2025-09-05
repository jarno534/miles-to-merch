# In admin.py

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect
from models import db, User, Product, Variant

# --- Beveiliging van het Admin Panel ---
# Deze custom views zorgen ervoor dat alleen JIJ toegang hebt tot het admin panel.

class SecuredModelView(ModelView):
    def is_accessible(self):
        # Controleert of de ingelogde gebruiker de admin is
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            # BELANGRIJK: Vervang dit door JOUW admin e-mailadres
            if user and user.email == 'jouw-admin-email@voorbeeld.com':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # Stuurt niet-admins weg
        return redirect('/')

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Zelfde controle voor de admin hoofdpagina
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            # BELANGRIJK: Vervang dit door JOUW admin e-mailadres
            if user and user.email == 'jarno.blomme@telenet.be':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

# --- Specifieke Views voor je Modellen ---

class ProductAdminView(SecuredModelView):
    # Toont de naam van het product en het aantal varianten
    column_list = ('name', 'variants')
    form_columns = ('name', 'description', 'printful_product_id', 'base_price', 'additional_price_per_area')

class VariantAdminView(SecuredModelView):
    # Toont de belangrijkste variant-info en maakt 'is_active' en 'price' direct bewerkbaar in de lijst
    column_list = ('product.name', 'color', 'size', 'price', 'is_active')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name']
    column_searchable_list = ['color', 'size', 'product.name']

# --- Setup Functie ---
def setup_admin(app):
    admin = Admin(app, name='Miles-to-Merch Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(ProductAdminView(Product, db.session))
    admin.add_view(VariantAdminView(Variant, db.session))