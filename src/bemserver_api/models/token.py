from . import db
from bemserver_core.model import User
import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Token(db.Model, Base):
    __tablename__ = "authenticationtoken"

    id = sqla.Column(sqla.Integer, primary_key=True)
    token = sqla.Column(sqla.String(6), nullable=True)
    token_expiry = sqla.Column(sqla.DateTime())
    token_type = sqla.Column(sqla.String(20))
    # user_id = sqla.Column(sqla.ForeignKey("users.id"), nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey(User.id), nullable=True)
    user = sqla.orm.relationship(User, backref="auth_tokens")
