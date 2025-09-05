# In admin.py

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for
from models import db, User, Product, Variant, Design, Order

# --- Verbeterde Beveiliging ---
# Deze views controleren nu de 'is_admin' vlag in de database.

class SecuredModelView(ModelView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            # Controleert nu of de gebruiker een admin is
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
    # Toont de belangrijkste productinformatie en maakt prijzen direct bewerkbaar
    column_list = ('name', 'printful_product_id', 'base_price', 'additional_price_per_area', 'variants')
    column_searchable_list = ['name']
    column_editable_list = ['base_price', 'additional_price_per_area']
    form_columns = ('name', 'description', 'printful_product_id', 'base_price', 'additional_price_per_area')

class VariantAdminView(SecuredModelView):
    # Meest gebruikte view: toont varianten met krachtige filters en bewerkbare velden
    column_list = ('product.name', 'color', 'size', 'price', 'is_active', 'merch_color_type')
    column_editable_list = ['is_active', 'price']
    column_filters = ['is_active', 'color', 'size', 'product.name', 'merch_color_type']
    column_searchable_list = ['color', 'size', 'product.name']
    # Paginering voor als je veel varianten hebt
    page_size = 100

class UserAdminView(SecuredModelView):
    # Geeft een overzicht van je gebruikers
    column_list = ('id', 'email', 'name', 'strava_id', 'is_admin')
    column_searchable_list = ['email', 'name']
    column_filters = ['is_admin']
    # Maak wachtwoorden niet zichtbaar of bewerkbaar in het admin panel
    form_excluded_columns = ['password_hash']

class OrderAdminView(SecuredModelView):
    # Toont een overzicht van alle bestellingen, gesorteerd op datum
    column_list = ('id', 'user.name', 'order_date', 'total_price', 'order_status', 'printful_order_status')
    column_filters = ['order_status', 'printful_order_status']
    column_default_sort = ('order_date', True) # True for descending

class DesignAdminView(SecuredModelView):
    # Geeft een overzicht van gemaakte designs
    column_list = ('id', 'name', 'user.name', 'product.name', 'created_at')
    column_searchable_list = ['name', 'user.name', 'product.name']
    column_default_sort = ('created_at', True)

# --- Setup Functie ---
def setup_admin(app):
    admin = Admin(
        app, 
        name='Miles-to-Merch Admin', 
        template_mode='bootstrap3', 
        index_view=MyAdminIndexView()
    )
    
    # Voeg de views toe met categorieën voor een netter menu
    admin.add_view(UserAdminView(User, db.session, category='Management'))
    admin.add_view(OrderAdminView(Order, db.session, category='Management'))
    admin.add_view(DesignAdminView(Design, db.session, category='Management'))
    admin.add_view(ProductAdminView(Product, db.session, category='Catalogus'))
    admin.add_view(VariantAdminView(Variant, db.session, category='Catalogus'))