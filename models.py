from extensions import db

class Accounts(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    cusid = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.Enum('savings', 'current'), default='savings')
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    status = db.Column(db.Enum('active', 'frozen', 'closed'), default='active')
    transaction_limit = db.Column(db.Numeric(15, 2), default=100000.00)
    created_at = db.Column(db.DateTime)
    createdby = db.Column(db.String(20), nullable=False)

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    Othername = db.Column(db.String(20), nullable=True)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    BVN = db.Column(db.String(20), unique=True,nullable=True)
    NIN = db.Column(db.String(20), unique=True, nullable=True)
    gender = db.Column(db.Enum('F', 'M', 'Others'))


class BVNNIN(db.Model):
    __tablename__ = 'bvnninrecords'

    id = db.Column(db.Integer, primary_key=True)
    cusid = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    BVN = db.Column(db.String(200), nullable=False)
    NIN = db.Column(db.String(200), nullable=False)