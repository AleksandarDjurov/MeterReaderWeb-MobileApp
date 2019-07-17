#!/usr/bin/env python
import os
# import pyodbc
import urllib
import datetime

from flask import Flask, abort, request, jsonify, g, url_for, json, render_template, flash, redirect, session
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from Controller import dbmanager as dm, smsManger as smsM, adminManager as adminM, \
                        customerManager as cM, homeManger as homeM, reportManger, \
                        profileManager as pM

from forms import *
from model import *

from gevent.pywsgi import WSGIServer # Imports the WSGIServer
from gevent import monkey; monkey.patch_all() 

# Privacy_policy -------------------------------------
@app.route('/privacypolicy')
def privacypolicy():
    return render_template('privacy_policy.html')

# WEB VIEW--------------------------------------

def loged_in():
    if 'logged_in' in session:
        if session['logged_in'] is True:
            return True
    
    session['logged_in'] = False
    return False
        

@app.route('/')
def home():
    if loged_in() is True:
        form = homeForm();
        form.months.choices = [(0, "")]
        customers = homeM.getRecentCustomers()
        if customers is False:
            flash(f'Database access error!', 'danger')
        else:
            return render_template('home.html', customers=customers, form = form)
    else:
        return redirect(url_for('login'))

@app.route('/home/datas')
def getHomeData():
    # districtNames, customerCnts, Usages = homeM.get_usage_customers_by_district()
    months, totalPerDistrictList = homeM.get_usage_customers_by_district()
    UsagesPerMonth = homeM.getTotalUsagePerMonth()
    return jsonify({"months": months, "totalPerDistrictList":totalPerDistrictList, "UsagesPerMonth":UsagesPerMonth })

@app.route('/home/reads')
def getRecentReads():
    return jsonify({'recentReads': homeM.getRecentReads()})

@app.route('/reports')
def reports():
    if loged_in() is True:
        form = ReportForm()
        months = cM.getMonths()
        form.months_discounted.choices = [(g[0], g[0]) for g in months]
        form.months_usage.choices = [(g[0], g[0]) for g in months]
        form.isread.choices = [("Read", "Read"), ("Unread", "Unread")]
        return render_template('reports.html', form = form)
    else:
        return redirect(url_for('login'))

@app.route('/reports/evc', methods=['GET', 'POST'])
def get_report_list():
    return reportManger.get_report_list()

@app.route('/reports/discounted', methods=['GET', 'POST'])
def get_report_discounted_list():
    month = request.args['month']
    return reportManger.get_report_discounted_list(month)

@app.route('/reports/usage', methods=['GET', 'POST'])
def get_report_usage_list():
    month = request.args['month']
    isread = request.args['isread']
    return reportManger.get_report_usage_list(month, isread)

@app.route('/sms')
def sms():
    if loged_in() is True:
        return render_template('sms.html')
    else:
        return redirect(url_for('login'))
       
@app.route('/sms/<string:type>', methods=['GET', 'POST'])
def get_sms_list(type):
    return smsM.get_sms_list(type)

@app.route('/sms/assign')
def sms_assign():
    if loged_in() is True:
        return render_template('sms_assign.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/admin')
def admin():
    if loged_in() is True:
        users = adminM.getAllUsers()
        districts = adminM.getAllDistricts()
        if users is False:
            flash(f'Database access error!', 'danger')
        if districts is False:
            flash(f'Database access error!', 'danger')
        else:
            return render_template('admin.html', users=users, districts = districts)
    else:
           return redirect(url_for('login'))
       
@app.route('/admin/customer_manage')
def admin_customer_management():
    if loged_in() is True and session['accessType'] == "Admin":
        form = adminCustomerForm()
        form.district.choices = [(g.DistrictCode, g.DistrictCode) for g in adminM.getAllDistricts()]
        form.district_update.choices = [(g.DistrictCode, g.DistrictCode) for g in adminM.getAllDistricts()]
        
        return render_template('admin_customer.html', form=form)
    else:
        return redirect(url_for('login'))

@app.route('/admin/customer_manage/customer_table', methods=['GET', 'POST'])
def admin_customer_table():
    if loged_in() is True:
        district = request.args['district']
        return adminM.get_customer_table_list(district)
    else:
        return redirect(url_for('login'))

@app.route('/admin/customer_manage/update_district', methods=['GET', 'POST'])
def admin_customer_update_district():
    if loged_in() is True:
        return adminM.customer_update_district(request)
    else:
        return redirect(url_for('login'))

@app.route('/admin/customer_manage/reactivate_user', methods=['GET', 'POST'])
def admin_customer_reactivate_user():
    if loged_in() is True:
        return adminM.customer_reactivate_user(request)
    else:
        return redirect(url_for('login'))

@app.route('/admin/user_manage')
def admin_user_management():
    if loged_in() is True and session['accessType'] == "Admin":
        return render_template('admin_user.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/user_manage/user_table')
def admin_user_management_table():
    if loged_in() is True and session['accessType'] == "Admin":
        isNew = request.args['showNew']
        return adminM.user_management_table(isNew)
    else:
        return redirect(url_for('login'))

@app.route('/admin/user_manage/update_user', methods=['GET', 'POST'])
def admin_user_management_update_user():
    if loged_in() is True and session['accessType'] == "Admin":
        return adminM.admin_user_management_update_user(request)
    else:
        return redirect(url_for('login'))

@app.route('/admin/billing_month')
def admin_set_billing_month():
    if loged_in() is True and session['accessType'] == "Admin":
        return render_template('admin_set_billing_month.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/billing_month/billing_month_table', methods=['GET', 'POST'])
def admin_billing_month_table():
    if loged_in() is True and session['accessType'] == "Admin":
        return adminM.admin_billing_month_table()
    else:
        return redirect(url_for('login'))

@app.route('/admin/billing_month/set_billing_month', methods=['GET', 'POST'])
def admin_billing_month_set_billing_month():
    if loged_in() is True and session['accessType'] == "Admin":
        return adminM.admin_billing_month_set_billing_month(request)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    session['logged_in'] = False
    form = RegistrationForm()
    if form.validate_on_submit():
        if(dm.register_user( form.username.data, form.phone.data, form.password.data)):
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if loged_in() is True:
        user = pM.getLogedinUserInfo()
        if user is not None:
            form = ProfileForm()
            form.username_profile.data = user.username
            form.phone_profile.data = user.Phone
            form.password_profile.data = ""
            form.confirm_password_profile.data = ""
            return render_template('profile.html', form=form)
        
    return redirect(url_for('login'))

@app.route('/profile/update', methods=['GET', 'POST'])
def profile_update():
    if loged_in() is True:
        user = pM.update_user(request.form)
        if user:
            session['username'] = user.username
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "failed"})
        
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    session['logged_in'] = False
    session['username'] = None
    session['password'] = None
    session['accessType'] = ""

    form = LoginForm()
    if form.validate_on_submit():
        if dm.check_user(form.username.data, form.password.data) is True:
            flash(f'You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login failed!', 'danger')
    return render_template('login.html', title='Login', form=form, logged_in=False)

@app.route('/customer')
def customer():
    if loged_in() is True:
        form = CustomerForm()
        form.district.choices = [(g.DistrictCode, g.DistrictCode) for g in cM.getDistricts()]

        pageInfo = "0"
        if 'customerPageInfo' in session:
            if session['customerPageInfo'] != "":
                pageInfo = session['customerPageInfo']
        session['customerPageInfo'] = ""

        return render_template('customer.html', form=form, pageInfo=pageInfo)
    else:
        return redirect(url_for('login'))

@app.route('/customer_table', methods=['GET', 'POST'])
def customer_table():
    if loged_in() is True:
        # district = request.args['district']
        # return cM.get_customer_table_list(district)
        return cM.get_customer_table_list()
    else:
        return redirect(url_for('login'))

@app.route('/customer/edit', methods=['GET', 'POST'])
def edit_customer():
    if loged_in() is True:
        if request.method != "POST":
            redirect(url_for('login'))

        form = CustomerEditForm()
        if "barcode" in request.form:
            barcode = str(request.form.get('barcode'))
            form.meter_barcode_no.data = barcode
            # form.description.data = "Sacad badal"
            form.user.data = session['username']
            meter, customer, customerDetail, district = dm.get_customerInfo(barcode)
            if meter is False:
                flash(f'Database Error!', 'danger')
            else:
                form.customer_id.data = customer.CustomerId
                form.firstname.data = customer.FirstName
                form.lastname.data = customer.LastName
                form.mobile1.data = customerDetail.MobileNumber1
                form.mobile2.data = customerDetail.MobileNumber2
                form.mobile3.data = customerDetail.MobileNumber3
                form.mobile4.data = customerDetail.MobileNumber4
                form.district.data = district.DistrictCode
                form.city.data = customerDetail.City
                form.neighbour.data = customerDetail.Neighbour
                form.house_tax_no.data = customerDetail.HouseTaxIdNumber
                form.customer_type.data = customer.CustomerType
                form.account_status.data = customer.IsAccountActive
                form.dhameen_name.data = customerDetail.DhameenName
                form.dhameen_mobile1.data = customerDetail.DhameenMobileNumber1
                form.dhameen_mobile2.data = customerDetail.DhameenMobileNumber2
                form.deposit.data = customerDetail.Deposit
                form.comment.data = customerDetail.Comment
                form.meter_make.data = meter.Make
                form.meter_model.data = meter.Model
                form.meter_serial_no.data = meter.MeterSerialNo
                form.tag_serial_no.data = meter.TagSerialNo
                return render_template('customer_edit.html', form=form)
        else:
            if cM.edit_customer(form):
                flash(f'Update Customer Success!', 'success')
                # return redirect('/customer/view/'+str(form.meterBarcodeNo.data))
                return redirect('/customer/view/' + form.meter_barcode_no.data)
            else:
                flash(f'Update Customer Failed!', 'danger')
    else:
        return redirect(url_for('login'))

@app.route('/customer/view/<string:barcode>', methods=['GET', 'POST'])
def view_customer(barcode):
    if loged_in() is True:
        # barcode = str(request.form.get('barcode'))
        customerInfo, historys = cM.getCustomerInfoForWeb(barcode)
        return render_template('customer_view.html', customerInfo=customerInfo, historys=historys)
    else:
        return redirect(url_for('login'))

@app.route('/customer/view/usage', methods=['GET', 'POST'])
def view_customer_usage():
    if loged_in() is True:
        barcode = request.args['barcode']
        return cM.get_view_customer_usage(barcode)
    else:
        return redirect(url_for('login'))

@app.route('/customer/view/bill', methods=['GET', 'POST'])
def view_customer_bill():
    if loged_in() is True:
        barcode = request.args['barcode']
        return cM.get_view_customer_bill(barcode)
    else:
        return redirect(url_for('login'))

@app.route('/customer/view/payment', methods=['GET', 'POST'])
def view_customer_payment():
    if loged_in() is True:
        barcode = request.args['barcode']
        return cM.get_view_customer_payment(barcode)
    else:
        return redirect(url_for('login'))

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    if loged_in() is True:
        form = CustomerAddForm()
        if 'pageInfo' in request.form:
            session['customerPageInfo'] = json.loads(request.form.get('pageInfo'))
            form.created_user.data = session["username"]
        else:
            new_customer_barcode = cM.add_customer(form.firstname.data, form.lastname.data, form.mobile1.data, form.mobile2.data, 
                            form.mobile3.data, form.mobile4.data, form.district.data, form.city.data, form.neighbour.data, 
                            form.house_tax_no.data, form.customer_type.data, form.account_status.data, form.dhameen_name.data, 
                            form.dhameen_mobile1.data, form.dhameen_mobile2.data, form.deposit.data, form.comment.data, 
                            form.meter_make.data, form.meter_model.data, form.meter_serial_no.data, form.tag_serial_no.data,
                            form.curr_kw.data, form.created_user.data)
            if new_customer_barcode:
                flash(f'New Customer added!', 'success')
                return redirect( '/customer/view/' + str(new_customer_barcode.MeterBarcodeNo) )
            else:
                flash(f'Add Customer Failed!', 'danger')
            
        return render_template('customer_add.html', form=form)
    else:
        return redirect(url_for('login'))
    
@app.route('/customer/usage', methods=['GET', 'POST'])
def customer_usage_manual_show():
    if loged_in() is True:
        form = CustomerUsagesForm()
        form.district.choices = [(g.DistrictCode, g.DistrictCode) for g in cM.getDistricts()]
        form.months.choices = [(g[0], g[0]) for g in cM.getMonths()]
        
        return render_template('customer_usage.html', form = form)
    else:
        return redirect(url_for('login'))
    
@app.route('/customer/usages', methods=['GET', 'POST'])
def customer_usages_for_month_district():
    if loged_in() is True:
        district = request.args['district']
        month = request.args['month']
        return cM.customer_usages_for_month_district(month, district)
    else:
        return redirect(url_for('login'))
    
@app.route('/customer/manual_usage', methods=['GET', 'POST'])
def customer_manual_read():
    if loged_in() is True:
        return cM.customer_manual_read(request)
    else:
        return redirect(url_for('login'))
    
@app.route('/customer/payment', methods=['GET', 'POST'])
def customer_payment_show():
    if loged_in() is True:
        form = PaymentForm()
        form.district.choices = [(g.DistrictCode, g.DistrictCode) for g in cM.getDistricts()]
        form.months.choices = [(g[0], g[0]) for g in cM.getMonths()]
        
        return render_template('customer_payment.html', form = form)
    else:
        return redirect(url_for('login'))

@app.route('/customer/payment/save_paid', methods=['GET', 'POST'])
def customer_payment_save():
    if loged_in() is True:
        return cM.customer_payment_save(request)
    else:
        return redirect(url_for('login'))
    
@app.route('/customer/manual_payment/table', methods=['GET', 'POST'])
def get_manual_payment_list():
    if loged_in() is True:
        district = request.args['district']
        month = request.args['month']
        return cM.getManualPaymentList(district, month)
    else:
        return redirect(url_for('login'))
# =============================================================

# API----------------------------------------------------------
@app.route('/api/users', methods=['GET', 'POST'])
def new_user():
    username = request.json['username']
    password = request.json['password']
    phone = request.json['Phone']
    user = dm.new_user(username, password, phone)
    if user is None:
        abort(400)

    return (
        jsonify({'username': user.username}),
        201,
        {'Location': url_for('get_user', id=user.id, _external=True)}
    )


@app.route('/api/users/<int:id>')
def get_user(id):
    user = dm.get_user(id)
    
    if not user:
        abort(400)
    return jsonify({'username':user.username,'password':user.password,'Phone':user.Phone}), 200
    
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = dm.get_auth_token()
    return jsonify({'token': token.decode('ascii'), 'duration': 600}), 200

# from __future__ import division
# from __future__ import absolute_import
# from __future__ import print_function

# from .modelsmap import modelsmap
# from json import JSONEncoder
# def model_to_dict(item, expand=True):
#     data = {}
#     for prop in modelsmap[type(item)]:
#         if hasattr(item, prop):
#             data[prop] = getattr(item, prop)
#     return data

# class Encoder(JSONEncoder):
#     def default(self, o):
#         if type(o) in modelsmap:
#             return model_to_dict(o)
        
#         return JSONEncoder.default(self, o)

import flask
@app.route('/api/resource')
@auth.login_required
def get_resource():
    if g.user.IsUserActive is not True:
        abort(403)
    token = dm.get_resource()
    # data = {
    #             'id':g.user.id,
    #             'username':g.user.username,
    #             'Phone':g.user.Phone,
    #             'token':token.decode('ascii')
    #         }
    # data = json.dumps(data, cls=JSONEncoder)
    # response = flask.make_response(data, 200)
    # response.mimetype = 'application/json'
    # return response
    return jsonify({
        'id':g.user.id,
        'username':g.user.username,
        'Phone':g.user.Phone,
        'token':token.decode('ascii')
    }), 200

@app.route('/api/customer_detail', methods=['GET', 'POST'])
@auth.login_required
def get_customer_detail_1():
    barcode_num = request.json['barcode']
    customer, customerDetail, tarrif, history = dm.get_customer_detail(str(barcode_num))
    if history.UnitRate is None:
        history.UnitRate = 1

    if not history:
        return jsonify({
            'isHistory':'no',
            'firstName': customer.FirstName,
            'lastName': customer.LastName,
            'customerId': customer.CustomerId,
            'phone1': customerDetail.MobileNumber1,
            'phone2': customerDetail.MobileNumber2,
            'phone3': customerDetail.MobileNumber3,
            'unitRate':history.UnitRate
        }), 200
    else:
        return jsonify({
            'isHistory':'yes',
            'firstName':customer.FirstName,
            'lastName':customer.LastName,
            'customerId':customer.CustomerId,
            'phone1':customerDetail.MobileNumber1,
            'phone2':customerDetail.MobileNumber2,
            'phone3':customerDetail.MobileNumber3,
            'unitRate':tarrif.UnitRate,
            'prevReadDate':history.CurrReadDate,
            'prevRead':history.CurrRead,
            'prevBill':history.Bill,
            # 'image':history.Image,
            'usedKW':history.UsedKW,
            'discounted':history.Discounted
        }), 200
        
@app.route('/api/customer_detail/<string:barcode>', methods=['GET', 'POST'])
# @auth.login_required
def get_customer_detail(barcode):
    barcode_num = barcode
    customer, customerDetail, tarrif, history = dm.get_customer_detail(str(barcode_num))
    if history.UnitRate is None:
        history.UnitRate = 1

    if not history:
        return jsonify({
            'isHistory':'no',
            'firstName': customer.FirstName,
            'lastName': customer.LastName,
            'customerId': customer.CustomerId,
            'phone1': customerDetail.MobileNumber1,
            'phone2': customerDetail.MobileNumber2,
            'phone3': customerDetail.MobileNumber3,
            'unitRate':history.UnitRate
        }), 200
    else:
        return jsonify({
            'isHistory':'yes',
            'firstName':customer.FirstName,
            'lastName':customer.LastName,
            'customerId':customer.CustomerId,
            'phone1':customerDetail.MobileNumber1,
            'phone2':customerDetail.MobileNumber2,
            'phone3':customerDetail.MobileNumber3,
            'unitRate':tarrif.UnitRate,
            'prevReadDate':history.CurrReadDate,
            'prevRead':history.CurrRead,
            'prevBill':history.Bill,
            'image':history.Image,
            'usedKW':history.UsedKW,
            'discounted':history.Discounted
        }), 200

@app.route('/api/new_read', methods=['GET', 'POST'])
@auth.login_required
def new_read():
    barcode = request.json['barcode']
    curRead = request.json['curRead']
#    curReadDate = datetime.strptime(request.json['curReadDate'], format)
    #date_str = request.json['curReadDate']
    #curReadDate = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.000")
    curReadDate = request.json['curReadDate']
    unitRate = request.json['unitRate']
    discounted = request.json['disCounted']
    
    readImage = ""
    if "readImage" in request.json:
        readImage = request.json['readImage']
        
    location_x = request.json['location_x']
    location_y = request.json['location_y']
    createdUser = request.json['userName']
    phone = request.json['phone']
   
    return dm.new_read(barcode, curRead, curReadDate, unitRate, discounted, readImage, location_x, location_y, createdUser,phone)
    
@app.route('/api/customer_list', methods=['GET', 'POST'])
@auth.login_required
def get_customer_list():
    username = request.json['username']
    
    customer_list = dm.get_customer_list(username)
 
    customers = []
    for customer in customer_list:
        customers.append({
            'name': customer.Name,
            'phone': customer.Phone,
            'barcode': customer.MeterBarcodeNo,
            'district': customer.District,
            'bill': customer.Bill,
            'paid': customer.Paid,
            'outstanding': customer.Outstanding,
            'meterread': customer.MeterRead
        })
   
    return jsonify({'result': customers}), 200

@app.route('/api/customer_list/get_latest_all', methods=['GET', 'POST'])
@auth.login_required
def customer_profile_get_latest():
    return dm.customer_profile_get_latest()

@app.route('/api/comment', methods=['GET', 'POST'])
@auth.login_required
def set_comment():
    if dm.set_comment(request.json):
        return jsonify({'result': "success"}), 200
    else:
        abort(400)

@app.route('/api/paidSms', methods=['GET', 'POST'])
def paid_sms_list():
    smsList = request.json['smsList']
    if dm.paid_sms_list(smsList):
        return jsonify({'result': "success"}), 200
    else:
        return jsonify({'result': "data erro"}), 200



import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.info('%s %s %s %s %s %s',
                        ts,
                        request.remote_addr,
                        request.method,
                        request.scheme,
                        request.full_path,
                        response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.info('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                  ts,
                  request.remote_addr,
                  request.method,
                  request.scheme,
                  request.full_path,
                  tb)
    return "Internal Server Error", 500

from waitress import serve
if __name__ == '__main__':
    if not os.path.exists('mssql+pyodbc:///?odbc_connect'):
        db.create_all()

    # maxBytes to small number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler('jmeter.log', maxBytes=10000, backupCount=3)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # using waitress
    # serve(app, host='0.0.0.0', port=80)
    
    # using gevent
    http_server = WSGIServer( ('0.0.0.0',80), app )
    http_server.serve_forever()
    
    ## Production
    # app.run(debug=False, host='0.0.0.0', port=80)
    # app.run(host='0.0.0.0', port=80)