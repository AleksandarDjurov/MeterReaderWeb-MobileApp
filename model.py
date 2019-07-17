import os
import urllib
from flask import Flask, abort, request, jsonify, g, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash


# initialization
app = Flask(__name__)

params = urllib.parse.quote_plus(
    'DRIVER={SQL Server};SERVER=jesco.cgxxej6y2ygv.eu-west-1.rds.amazonaws.com;DATABASE=jesco;UID=admin;PWD=$Flavas51')
# params = urllib.parse.quote_plus(
    # 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=jesco.cgxxej6y2ygv.eu-west-1.rds.amazonaws.com;DATABASE=jesco;UID=admin;PWD=$Flavas51')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

# app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SECRET_KEY'] = 'be4b2171d3876ec78c8345938aedba54'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    Phone = db.Column(db.String(50))
    UserAccessType = db.Column(db.String(255))
    IsUserActive = db.Column(db.Boolean)
    RoleId = db.Column(db.Integer)
    
    def hash_password(self, password):
        self.password = pwd_context.hash(password)
        # self.password = generate_password_hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)
        # return check_password_hash(password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

class UserRoles(db.Model):
    __tablename__ = "UserRoles"
    Id = db.Column(db.Integer)
    RoleId = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(100))
    
class Meter(db.Model):
    __tablename__ = "Meter"
    MeterId = db.Column(db.Integer, primary_key=True)
    CustomerId = db.Column(db.Integer)
    MeterBarcodeNo = db.Column(db.String(255))
    DistrictId = db.Column(db.Integer)
    Make = db.Column(db.String(255))
    Model = db.Column(db.String(255))
    MeterSerialNo = db.Column(db.String(255))
    TagSerialNo = db.Column(db.String(255))
    MeterLocation = db.Column(db.String(255))
    MeterInstalledDate = db.Column(db.String(255))
    TarrifId = db.Column(db.Integer)
    isMeterActive = db.Column(db.Boolean)
    ConnectedToPoleNo = db.Column(db.String(255))
    ConnectedToPhase = db.Column(db.Integer)
    ModifiedByUser = db.Column(db.Integer)
    ModifiedDate = db.Column(db.DateTime)
    
class Comment(db.Model):
    __tablename__ = "Comment"
    CommentId = db.Column(db.Integer, primary_key=True)
    CustomerId = db.Column(db.Integer)
    MeterBarcodeNo = db.Column(db.String(255))
    Comment = db.Column(db.String(max))
    CreatedByUser = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)
    CurrRead = db.Column(db.Float)
    Location_X = db.Column(db.Float)
    Location_Y = db.Column(db.Float)
    Image = db.Column(db.String(max))

class Customer(db.Model):
    __tablename__ = "Customer"
    CustomerId = db.Column(db.Integer, primary_key=True)
    SupplyNo = db.Column(db.String(255))
    FirstName = db.Column(db.String(255))
    LastName = db.Column(db.String(max))
    IsAccountActive = db.Column(db.Boolean)
    CustomerType = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)
    ModifiedByUser = db.Column(db.String(255))
    ModifiedDate = db.Column(db.DateTime)

class CustomerDetail(db.Model):
    __tablename__ = "CustomerDetail"
    CustomerDetailId = db.Column(db.Integer, primary_key=True)
    CustomerId = db.Column(db.Integer)
    MobileNumber1 = db.Column(db.String(255))
    MobileNumber2 = db.Column(db.String(255))
    MobileNumber3 = db.Column(db.String(255))
    MobileNumber4 = db.Column(db.String(255))
    EmailAddress = db.Column(db.String(255))
    Neighbour = db.Column(db.String(max))
    HouseTaxIdNumber = db.Column(db.String(max))
    City = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    PostalCode = db.Column(db.String(20))
    ModifiedByUser = db.Column(db.Integer)
    ModifiedDate = db.Column(db.DateTime)
    DhameenName = db.Column(db.String(255))
    DhameenMobileNumber1 = db.Column(db.String(255))
    DhameenMobileNumber2 = db.Column(db.String(255))
    Deposit = db.Column(db.Float)
    Comment = db.Column(db.String(max))

class UsageHistory(db.Model):
    __tablename__ = "UsageHistory"
    UsageId = db.Column(db.Integer, primary_key=True)
    Meterid = db.Column(db.Integer)
    CustomerId = db.Column(db.Integer)
    MeterBarcodeNo = db.Column(db.String(255))
    PrevRead = db.Column(db.Float)
    PrevReadDate = db.Column(db.DateTime)
    CurrRead = db.Column(db.Float)
    CurrReadDate = db.Column(db.DateTime)
    UsedKW = db.Column(db.Float)
    UnitRate = db.Column(db.Float)
    Discounted = db.Column(db.Boolean)
    Bill = db.Column(db.Float)
    Image = db.Column(db.String(max))
    Location_X = db.Column(db.Float)
    Location_Y = db.Column(db.Float)
    Description = db.Column(db.String(max))
    CreatedByUser = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)

class Tarrif(db.Model):
    __tablename__ = "Tarrif"
    TarrifId = db.Column(db.Integer, primary_key=True)
    CustomerType = db.Column(db.String(255))
    TarrifName = db.Column(db.String(255))
    UnitRate = db.Column(db.Float)
    
class SmsSent(db.Model):
    __tablename__ = "SmsSent"
    SmsId = db.Column(db.Integer, primary_key=True)
    PhoneNumber = db.Column(db.String(255))
    SmsHeader = db.Column(db.String(max))
    SmsMessage = db.Column(db.String(max))
    CreateDate = db.Column(db.DateTime)
    MeterBarcodeNo = db.Column(db.String(100))
    
class District(db.Model):
    __tablename__ = "District"
    DistrictId = db.Column(db.Integer, primary_key=True)
    DistrictCode = db.Column(db.String(3))
    DistrictName = db.Column(db.String(max))
    BillerResponsible = db.Column(db.String(max))
    
class CustomerList(db.Model):
    __tablename__ = "CustomerList"
    CustomerId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(max))
    MobileNumber1 = db.Column(db.String(255))
    MeterBarcodeNo = db.Column(db.String(255))
    DistrictName = db.Column(db.String(max))
    Bill = db.Column(db.Float)
    Paid = db.Column(db.Float)
    Outstanding = db.Column(db.Float)

    def serialize(self):
        return {
            'customer_id': self.CustomerId,
            'name': self.Name,
            'phone': self.MobileNumber1,
            'barcode': self.MeterBarcodeNo,
            'district': self.DistrictName,
            'bill': self.Bill,
            'paid': self.Paid,
            'outstanding': self.Outstanding
        }

class SmsIncoming(db.Model):
    __tablename__ = "SmsIncoming"
    SmsId = db.Column(db.Integer, primary_key=True)
    SentFromNumber = db.Column(db.String(255))
    SmsMessage = db.Column(db.String(max))
    SentDatetime = db.Column(db.DateTime)
    CreateDate = db.Column(db.DateTime)
    
class Payment(db.Model):
    __tablename__ = "Payment"
    PaymentId = db.Column(db.Integer, primary_key=True)
    UsageId = db.Column(db.Integer)
    CustomerId = db.Column(db.Integer)
    MeterBarcodeNo = db.Column(db.Integer)
    PaymentType = db.Column(db.String(50))
    EVCNumberPaymentSendFrom = db.Column(db.String(255))
    Currency = db.Column(db.String(50))
    Paid = db.Column(db.Float)
    UnitRate = db.Column(db.Float)
    Discount = db.Column(db.Float)
    Discounted = db.Column(db.Boolean)
    OutstandingBalance = db.Column(db.Float)
    Description = db.Column(db.String(255))
    BillingMonth = db.Column(db.String(100))
    CreatedByUser = db.Column(db.String(255))
    CreatedDate = db.Column(db.DateTime)