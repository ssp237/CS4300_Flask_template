from . import *


class Product(Base):
    """
    Class to represent product database entry.
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=False)
    name           = db.Column(db.String(128), nullable=False, primary_key=True, unique=True)
    link           = db.Column(db.String(512), nullable=False)
    brand          = db.Column(db.String(128), nullable=False)
    num_faves      = db.Column(db.Integer, nullable=False)
    claims         = db.Column(db.String(2048), nullable=False)
    ingredients    = db.Column(db.ARRAY(db.String(256)), nullable=False)
    price          = db.Column(db.Float, nullable=False)
    ptype          = db.Column(db.ARRAY(db.String(64)), nullable=False)

    def __init__(self, **kwargs):
        self.name            = kwargs.get("name", None)
        self.link            = kwargs.get("link", None)
        self.brand           = kwargs.get("brand", None)
        self.num_faves       = kwargs.get("num_faves", None)
        self.claims          = kwargs.get("claims", None)
        self.ingredients     = kwargs.get("ingredients", None)
        self.price           = kwargs.get("price", None)
        self.ptype           = kwargs.get("types", None)

    def __repr__(self):
        return str(self.__dict__)


class UserSchema(ModelSchema):
    class Meta:
        model = Product
