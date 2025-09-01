# In extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

# We initialiseren CORS hier zonder de app, 
# zodat we het later in app.py met de juiste configuratie kunnen opzetten.
cors = CORS()