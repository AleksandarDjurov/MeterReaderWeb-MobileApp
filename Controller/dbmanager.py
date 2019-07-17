from flask_httpauth import HTTPBasicAuth
from model import *
from sqlalchemy import func, text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, json, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            db.session.commit()
            return False
    g.user = user
    db.session.commit()
    
    return True


def new_user(username, password, phone):
    if username is None or password is None:
        return None
    if User.query.filter_by(username=username).first() is not None:
        db.session.commit()
        return None  # existing user

    user = User(username=username, Phone=phone, IsUserActive=False)
    user.hash_password(password)

    db.session.add(user)
    db.session.commit()

    return user

def get_user(id):
    user = User.query.get(id)
    db.session.commit()
    return user


# @auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return token


def get_resource():
    # return jsonify({'data': 'Hello, %s!' % g.user.username})
    token = g.user.generate_auth_token(600)

    return token


def paid_sms_list(smsList):
    if len(smsList) < 1:
        return False

    for sms in smsList:
        adress = sms['adress']
        date = sms['date']
        body = sms['body']
        smsIncoming = SmsIncoming.query.filter_by(
            SentFromNumber=adress, SentDatetime=date).first()
        if not smsIncoming:
            smsIncoming = SmsIncoming(
                SentFromNumber=adress, SmsMessage=body, SentDatetime=date, CreateDate=datetime.now())
            db.session.add(smsIncoming)

    db.session.commit()
    return True

def get_customer_detail(barcode_num):
    meter = Meter.query.filter_by(MeterBarcodeNo=barcode_num).first()
    if not meter:
        abort(400)

    customerId = meter.CustomerId
    customerDetail = CustomerDetail.query.filter_by(CustomerId=customerId).first()
    db.session.commit()
    if not customerDetail:
        abort(400)

    customer = Customer.query.filter_by(CustomerId=customerId).first()
    db.session.commit()
    if not customer:
        abort(400)

    tarrif = Tarrif.query.filter_by(TarrifId=meter.TarrifId).first()
    db.session.commit()
    if not tarrif:
        abort(400)

    history = UsageHistory.query.filter_by(CustomerId=customerId).order_by(
        UsageHistory.UsageId.desc()).first()
    db.session.commit()
    return customer, customerDetail, tarrif, history

from datetime import timedelta
def new_read(barcode, curRead, curReadDate, unitRate, discounted, readImage, location_x, location_y, createdUser, phone):
    meter = Meter.query.filter_by(MeterBarcodeNo=barcode).first()
    db.session.commit()
    if not meter:
        abort(400)

    customerDetail = CustomerDetail.query.filter_by(
        CustomerId=meter.CustomerId).first()
    if not customerDetail:
        abort(400)

    if phone != customerDetail.MobileNumber1:
        customerDetail.MobileNumber4 = customerDetail.MobileNumber3
        customerDetail.MobileNumber3 = customerDetail.MobileNumber2
        customerDetail.MobileNumber2 = customerDetail.MobileNumber1
        customerDetail.MobileNumber1 = phone

    customer = Customer.query.filter_by(CustomerId=meter.CustomerId).first()
    db.session.commit()
    if not customer:
        abort(400)

    history = UsageHistory.query.filter_by(CustomerId=meter.CustomerId).order_by(UsageHistory.UsageId.desc()).first()
    prevReadDate = meter.ModifiedDate
    usedKw = curRead
    prevRead = 0.0
    if history:
        usedKw = curRead - history.CurrRead
        prevRead = history.CurrRead
        prevReadDate = history.CurrReadDate

    if prevReadDate == datetime.strptime(curReadDate, "%Y-%m-%d %H:%M:%S"):
        return jsonify({
            'status': 200,
            'usedKw':history.UsedKW,
            'prevRead':history.PrevRead,
            'prevReadDate':history.PrevReadDate,
            'customerId':history.CustomerId,
            'barcode':history.MeterBarcodeNo,
            'customerName':(customer.FirstName + " " + customer.LastName),
            'phone1':customerDetail.MobileNumber1,
            'phone2':customerDetail.MobileNumber2,
            'phone3':customerDetail.MobileNumber3,
            'discounted':history.Discounted
        }), 200

    # minDate = datetime.strptime("2019-06-19 21:34:23", "%Y-%m-%d %H:%M:%S")
    # minDate += timedelta(hours=4)
    minDate = prevReadDate + timedelta(hours=4)
    
    if minDate > datetime.strptime(curReadDate, "%Y-%m-%d %H:%M:%S"):
        return jsonify({'status': 201}), 200
    
    bill = usedKw
    if usedKw < 10:
        bill = 10

    if discounted:
        bill = round(bill*unitRate, 2)
    # float("{0:.2f}".format(bill*unitRate))

    new_read = UsageHistory(Meterid=meter.MeterId, CustomerId=meter.CustomerId, MeterBarcodeNo=barcode, PrevRead=prevRead, \
                            PrevReadDate=prevReadDate, CurrRead=curRead, CurrReadDate=curReadDate, UsedKW=usedKw, \
                            UnitRate=unitRate, Discounted=discounted, Bill=bill, Location_X=location_x, \
                            Location_Y=location_y, Description="Entered from Jesco App", CreatedByUser=createdUser, CreateDate=curReadDate)

    db.session.add(new_read)
    db.session.commit()

    smsHeader = "Send Bill as Txt to " + customer.FirstName + " " + customer.LastName
    smsBody = "Adeegga JESCO\n" + "Asc " + \
        customer.FirstName + " " + customer.LastName + "\n"
    smsBody += "Waxaad istimaashay: " + \
        str(usedKw) + "kw\n" + "Lacagtu wa : $" + str(bill) + "\n"
    smsBody += "Fadlan EVC plus numberka 612233757 ku so dir."
    
    smsSent = SmsSent(PhoneNumber=phone, SmsHeader=smsHeader,
                      SmsMessage=smsBody, CreateDate=curReadDate, MeterBarcodeNo=barcode)

    db.session.add(smsSent)
    db.session.commit()

    return jsonify({
            'status': 200,
            'usedKw':usedKw,
            'prevRead':prevRead,
            'prevReadDate':prevReadDate,
            'customerId':history.CustomerId,
            'barcode':history.MeterBarcodeNo,
            'customerName':(customer.FirstName + " " + customer.LastName),
            'phone1':customerDetail.MobileNumber1,
            'phone2':customerDetail.MobileNumber2,
            'phone3':customerDetail.MobileNumber3,
            'discounted':discounted
        }), 200
# @auth.login_required


def get_customer_list(username):
    customer_list = db.engine.execute(
        "dbo.sp_CustomerList ?", username).fetchall()

    db.session.commit()
    return customer_list

def customer_profile_get_latest():
    username = g.user.username
    latest_usages = db.engine.execute("dbo.sp_CustomerProfile_getlatest ?", username).fetchall()

    profiles = []
    for profile in latest_usages:
        profiles.append({
            'Name': profile.Name,
            'CustomerId': profile.CustomerId,
            'MeterBarcodeNo': profile.MeterBarcodeNo,
            'SupplyNo': profile.SupplyNo,
            'Phone1': profile.MobileNumber1,
            'Phone2': profile.MobileNumber2,
            'Phone3': profile.MobileNumber3,
            'CurrRead': profile.CurrRead,
            'CurrReadDate': profile.CurrReadDate,
            'UsedKw': profile.UsedKw,
            'Bill': profile.Bill
        })

    return jsonify({"profiles": profiles}), 200

def set_comment(json):
    barcode = str(json['barcode'])
    commentTxt = json['comment']
    username = json['username']
    createddate = json['createdate']
    Location_X = json['Location_X']
    Location_Y = json['Location_Y']       
    
    prevComment = Comment.query.filter_by(MeterBarcodeNo=barcode).order_by(Comment.CommentId.desc()).first()
    if prevComment:
        if datetime.strptime(createddate, "%Y-%m-%d %H:%M:%S") == prevComment.CreateDate:
            return True
    
    meter = Meter.query.filter_by(MeterBarcodeNo=barcode).first()
    if not meter:
        abort(400)

    if commentTxt == "Saacad badal":
        CurrRead = json['CurrRead']
        # image = json['Image']
        comment = Comment(CustomerId=meter.CustomerId, MeterBarcodeNo=barcode, Comment=commentTxt, CreatedByUser=username,
                        CreateDate=createddate, CurrRead=CurrRead, Location_X=Location_X, Location_Y=Location_Y)
        
        history = UsageHistory.query.filter_by(CustomerId=meter.CustomerId).order_by(UsageHistory.UsageId.desc()).first()
        # usedKw = CurrRead - history.CurrRead
        usedKw = 0
        new_read = UsageHistory(Meterid=meter.MeterId, CustomerId=meter.CustomerId, MeterBarcodeNo=barcode, PrevRead=history.CurrRead, \
                            PrevReadDate=history.CurrReadDate, CurrRead=CurrRead, CurrReadDate=createddate, UsedKW=usedKw, \
                            UnitRate=1, Discounted=0, Bill=usedKw, Location_X=Location_X, \
                            Location_Y=Location_Y, Description="Sacad badal from Jesco App", CreatedByUser=g.user.username, CreateDate=createddate)

        db.session.add(new_read)
        db.session.commit()
    else:
        comment = Comment(CustomerId=meter.CustomerId, MeterBarcodeNo=barcode, Comment=commentTxt, CreatedByUser=username,
                        CreateDate=createddate, Location_X=Location_X, Location_Y=Location_Y)
    db.session.add(comment)
    db.session.commit()
    return True

def get_customerInfo(barcode):
    meter = Meter.query.filter_by(MeterBarcodeNo=barcode).first()
    if not meter:
        return False, False, False, False

    customer = Customer.query.filter_by(CustomerId=meter.CustomerId).first()
    if not customer:
        db.session.commit()
        return False, False, False, False

    customerDetail = CustomerDetail.query.filter_by(
        CustomerId=meter.CustomerId).first()
    if not customerDetail:
        db.session.commit()
        return False, False, False, False

    district = District.query.filter_by(DistrictId=meter.DistrictId).first()
    if not district:
        db.session.commit()
        return False, False, False, False

    db.session.commit()
    return meter, customer, customerDetail, district

def read_user():
    users = User.query.fetchall()
    return users


def register_user(username, phone, password):
    user = new_user(username, password, phone)
    if not user:
        return False

    return True

def check_user(username, password):
    org_password = ""
    
    user = User.query.filter_by(username=username).first()
    if user:
        org_password = user.password
        if user.IsUserActive is not True:
            return False
    else:
        return False

    checked = user.verify_password(password)
    if checked is True:
        userRoles = UserRoles.query.filter_by(RoleId=user.RoleId).first()
        session['accessType'] = userRoles.RoleName
        session['logged_in'] = True
        session['username'] = username
        session['password'] = password
        session['enableWrite'] = False
        if session['accessType'] == "Admin" or session['accessType'] == "Back-office":
            session['enableWrite'] = True
    db.session.commit()
    return checked