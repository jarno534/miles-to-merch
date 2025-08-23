from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialiseer extensies hier zodat ze globaal beschikbaar zijn
# zonder circulaire importproblemen te veroorzaken.
db = SQLAlchemy()
cors = CORS()
