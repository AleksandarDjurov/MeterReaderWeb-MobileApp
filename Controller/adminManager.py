from flask_httpauth import HTTPBasicAuth
from model import *
from sqlalchemy import func, text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, json, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


def getAllUsers():
    users = User.query.all()
    db.session.commit()
    
    return users


def getAllDistricts():
    districts = District.query.all()
    db.session.commit()
    return districts

def serialize_customer_list(row):
    accountActive = "On"
    meterActive = "On"
    if row.IsAccountActive == False:
        accountActive = "Off"
    if row.isMeterActive == False:
        meterActive = "Off"
    return {
        "CustomerId": row.CustomerId,
        "SupplyNo": row.SupplyNo,
        "Name": row.FirstName + " " + row.LastName,
        "IsAccountActive": accountActive,
        "CustomerType": row.CustomerType,
        "IsMeterActive": meterActive,
        "DistrictCode": row.DistrictCode,
        "MeterBarcodeNo": row.MeterBarcodeNo,
        "CreateDate": row.CreateDate.strftime("%Y-%m-%d"),
        "Mange": '''<div class="dropdown">
            <button class="btn btn-info dropdown-toggle" data-toggle="dropdown" aria-expanded="false" type="button">Manage <span class="caret"></span></button>
            <ul class="dropdown-menu dropdown-menu-right" role="menu">
                <li><a  class="dropdown-item" id="update_''' + str(row.CustomerId) + '''">Update District</a></li>
                <li><a  class="dropdown-item" id="ra_''' + str(row.CustomerId) + '''">ReActivate Customer</a></li>
            </ul></div>
        '''
    }
    
def get_customer_table_list(district):
    customer_list = Customer.query.join(Meter, Customer.CustomerId==Meter.CustomerId).\
                            join(District, Meter.DistrictId==District.DistrictId).\
                            add_columns(Customer.CustomerId, Customer.SupplyNo, Customer.FirstName, Customer.LastName, \
                                        Customer.IsAccountActive, Customer.CustomerType, Meter.isMeterActive, Customer.CreateDate, \
                                        Customer.CreateDate, District.DistrictCode, Meter.MeterBarcodeNo).\
                            filter(District.DistrictCode == district).all()
    db.session.commit()
        
    return jsonify({ "data": [ serialize_customer_list(row) for row in customer_list], "user": session['username']})

def customer_update_district(request):
    update_data = request.json['data']
    barcode = update_data['Barcode']
    district = update_data['District']
    user = update_data['User']
    
    query = "EXEC sp_superuser_Customer_UpdateDistrictArea @Meterbarcodeno = " + \
        barcode + ", @DistrictArea = '" + district + "', @ModifiedByuser = '" + user + "'"
    
    connection = db.engine.raw_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    new_customer = cursor.execute(query)
    connection.commit()
    connection.close()
    
    # ret_val = db.engine.execute("dbo.sp_superuser_Customer_UpdateDistrictArea ?, ?, ?", [barcode, str(district), str(user)] )
    # db.session.commit()
    
    return jsonify({'district': district}), 200
    
def customer_reactivate_user(request):
    data = request.json['data']
    barcode = data['Barcode']
    IsAccountActive = data['IsAccountActive']
    
    accountStatus = 1
    if str(IsAccountActive) == "On":
        accountStatus = 0
        IsAccountActive = "Off"
    else:
        IsAccountActive = "On"
    
    query = "EXEC sp_superuser_ReactivateCustomer @Meterbarcodeno = " + \
        str(barcode) + ", @IsAccountActive = " + str(accountStatus) + ", @ModifiedByuser = '" + session['username'] + "'"
    
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
   
    return jsonify({'active': IsAccountActive}), 200

def serialize_user_list(row, roles):
    chk_user_active_html = '<input onchange = "ChangeUserActive()" type="checkbox" id="act_' + str(row.id) + '"'
    if row.IsUserActive :
        chk_user_active_html += ' checked>'
    else:
        chk_user_active_html += '>'

    sel_role_html = '<select style="border: none" id="role_' + str(row.id) + '" onchange="ChangeUserRole()">'
    for role in roles:
        if row.RoleId == role.RoleId:
            sel_role_html += '<option value=' + str(role.RoleId) + ' selected="selected">' + role.RoleName + '</option>'
        else:
            sel_role_html += '<option value=' + str(role.RoleId) + '>' + role.RoleName + '</option>'
            
    sel_role_html += '</select>'

    return {
        "id": row.id,
        "username": row.username,
        "Phone": row.Phone,
        "UserAccessType": row.UserAccessType,
        "IsUserActive": row.IsUserActive,
        "ChkUserActive": chk_user_active_html,
        "RoleId": row.RoleId,
        "SelRoleId": sel_role_html,
        "NewPwd": '<input onchange="ChangeNewPassword()" id="new_pwd_' + str(row.id) + '" type="password" style="width:40px; text-align:center; background: none; border: none" value="" readonly autocomplete="new-password">',
        "ConfirmPwd": '<input onchange="ChangeConfirmPassword()" id="confirm_pwd_' + str(row.id) + '" type="password" style="width:40px; text-align:center; background: none; border: none" value="" readonly autocomplete="new-password">',
        "ChkPwd": '<input type="checkbox" id="pwd_' + str(row.id) + '">'
    }
    
def user_management_table(isNew):
    users = 0
    if isNew == "true":
        users = User.query.filter_by(RoleId = None).all()
    else:
        users = User.query.all()
    
    roles = UserRoles.query.all()
    return jsonify( { "data": [ serialize_user_list(row, roles) for row in users]} )

def admin_user_management_update_user(request):
    update_users = request.json['sendData']
    for update_user in update_users:
        role_id = update_user['RoleId']
        user_role = UserRoles.query.filter_by(RoleId = role_id).first()
        
        user = User.query.filter_by(id = update_user['id'] ).first()
        user.UserAccessType = user_role.RoleName
        user.IsUserActive = update_user['IsUserActive']
        user.RoleId = role_id
        
        if update_user['ChkPwd'] == "true":
            user.password = update_user['password']
        db.session.commit()
    
    return jsonify({"result":"success"})

def serialize_billing_month_table_row(row):
    createDate = ""
    if row.CreatedDate:
        createDate = row.CreatedDate.strftime("%Y-%m-%d")

    chk_curr_month_html = '<input onchange = "CheckCurrBillingMonth()" type="checkbox" id="curr_' + str(row.id) + '"'
    if row.CurrentBillingMonth :
        chk_curr_month_html += ' checked>'
    else:
        chk_curr_month_html += '>'

    return {
        "id": row.id,
        "BillingMonth": row.BillingMonth,
        "BillingFromDate": row.BillingFromDate.strftime("%Y-%m-%d"),
        "BillingToDate": row.BillingToDate.strftime("%Y-%m-%d"),
        "CurrBillingMonth": row.CurrentBillingMonth,
        "ChkCurrBillingMonth": chk_curr_month_html,
        "CreatedByUser": row.CreatedByUser,
        "CreatedDate": createDate,
        "PickerFromDate":'<div class="input-group date"" style="background:none; border:none" id="month_from_' + str(row.id) + '''">
                                <input  type="text" class="form-control" style="background:none; border:none">
                                <div class="input-group-addon" style="background:none; border:none">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </div>
                            </div>''',
        "PickerToDate": '<div class="input-group date"" style="background:none; border:none" id="month_to_' + str(row.id) + '''">
                                <input  type="text" class="form-control" style="background:none; border:none">
                                <div class="input-group-addon" style="background:none; border:none">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </div>
                            </div>'''
    }

def admin_billing_month_table():
    billing_months = db.engine.execute("dbo.sp_superuser_SetBillingMonth_Showupcoming").fetchall()
    return jsonify({"data": [serialize_billing_month_table_row(row) for row in billing_months]})

def admin_billing_month_set_billing_month(request):
    seted_months = request.json['sendData']
    for set_month in seted_months:
        id = set_month['id']
        billing_from_date = (datetime.strptime(set_month['BillingFromDate'], "%Y-%m-%d")).strftime("%Y%m%d")
        billing_to_date = (datetime.strptime(set_month['BillingToDate'], "%Y-%m-%d")).strftime("%Y%m%d")
        curr_billing_month = 1
        if set_month['CurrBillingMonth'] == False:
            curr_billing_month = 0
            
        created_by_user = session['username']
        created_date = datetime.now().strftime("%Y%m%d")
        
        query = "EXEC sp_superuser_SetBillingMonth_Set @Id = " + str(id) + \
                 ", @BillingFromDate = '" + str(billing_from_date) + \
                 "', @BillingToDate = '" + str(billing_to_date) + \
                 "', @CurrentBillingMonth = " + str(curr_billing_month) + \
                 ", @CreatedByUser = '" + str(created_by_user) + \
                 "', @CreatedDate = '" + str(created_date) + "'"

        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        
    return jsonify({"result":"success"})    
    