from flask_httpauth import HTTPBasicAuth
from model import *
from sqlalchemy import func, text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, json, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf import FlaskForm

def customer_table_list_item_serialize(row):
    session['No'] = session['No'] + 1
    # meterRead = "Yes"
    # if row.MeterRead == 0:
        # meterRead = "No"
    return {
        # "N": session['No'],
        "CI": row.CustomerId,
        "SN": row.SupplyNo,
        "Nm": row.Name,
        "P": row.Phone,
        "B": row.MeterBarcodeNo,
        "MS": row.MeterSerialNo,
        "TS": row.TagSerialNo
        # "Action": ' <td>  <div class="dropdown"> <button class="btn btn-secondary btn-sm dropdown-toggle" id="' + str(row.MeterBarcodeNo) + '" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> Action </button> <ul class="dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="' + str(row.MeterBarcodeNo) + '"> <li><a class="dropdown-item" onclick="form_submit_edit(' + str(row.MeterBarcodeNo) + ')" href="javascript:void(0)">Edit</a></li> <li><a class="dropdown-item" onclick="form_submit_view(' + str(row.MeterBarcodeNo) + ')" href="javascript:void(0)">View</a></li> </ul> </div> </td> '
    # return {
    #     "No": session['No'],
    #     "Name": row.Name,
    #     "Phone": row.Phone,
    #     "MeterBarcodeNo": row.MeterBarcodeNo,
    #     "District": row.District,
    #     "Bill": row.Bill,
    #     "Paid": row.Paid,
    #     # "Outstanding" : row.Outstanding,
    #     # "MeterRead" : row.MeterRead
    #     "Outstanding": row.Outstanding,
    #     "MeterRead": meterRead,
    #     "Action": ' <td>  <div class="dropdown"> <button class="btn btn-secondary btn-sm dropdown-toggle" id="' + str(row.MeterBarcodeNo) + '" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> Action </button> <ul class="dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="' + str(row.MeterBarcodeNo) + '"> <li><a class="dropdown-item" onclick="form_submit_edit(' + str(row.MeterBarcodeNo) + ')" href="javascript:void(0)">Edit</a></li> <li><a class="dropdown-item" onclick="form_submit_view(' + str(row.MeterBarcodeNo) + ')" href="javascript:void(0)">View</a></li> </ul> </div> </td> '
    }

# def get_customer_table_list(district):
#     session['No'] = 0
#     customers = [customer_table_list_item_serialize(row) for row in db.engine.execute("dbo.sp_CustomerList_ByDistrict  ?, ?", session['username'], district).fetchall()]
#     if customers:
#         return jsonify({ 'data': customers})
#     return jsonify({ 'data': []})

def get_customer_table_list():
    session['No'] = 0
    customers = [customer_table_list_item_serialize(row) for row in db.engine.execute("dbo.sp_CustomerList_Search").fetchall()]
    if customers:
        return jsonify({ 'data': customers})
    return jsonify({ 'data': []})

def get_payment_table_list(user_name, post):
    draw = post['Draw'];
    page = post['Page'];
    start = draw * (page-1)
    end = start + 10
    session['No'] = start

    customers = db.engine.execute("dbo.sp_CustomerList ?", user_name).fetchall()
    db.session.commit()

    end = end if len(customers) > end else len(customers)
    customer_list = []
    for i in range(start, end):
        customer_list.append(customer_table_list_item_serialize(customers[i]))

    draw = end - start
    if customer_list:
        return jsonify({ 'draw': draw, 'recordsTotal': len(customers) , 'recordsFiltered': len(customers), 'data': customer_list, 'error':""})
    return None

def sql_text( data ):
    if data is None:
        data = "NULL"
    return str(data)

def edit_customer(form):
    account_status = form.account_status.data
    if form.account_status.data == "Off":
        account_status = 0

    query = "EXEC sp_CustomerUpdate @CustomerId = " + \
        str(form.customer_id.data) + ", @FirstName = '" + form.firstname.data
    query += "', @LastName = '" + form.lastname.data + "', @MobileNumber1 = " + \
        str(form.mobile1.data)
    query += ", @MobileNumber2 = " + sql_text(form.mobile2.data)
    query += ", @MobileNumber3 = " + sql_text(form.mobile3.data)
    query += ", @MobileNumber4 = " + sql_text(form.mobile4.data)
    query += ", @DistrictArea = '" + form.district.data
    query += "', @City = '" + form.city.data + "', @Neighbour = '" + \
        form.neighbour.data + "', @HouseTaxIdNumber = '" + form.house_tax_no.data
    query += "', @CustomerType = '" + form.customer_type.data + "', @AccountStatus = " + \
        account_status + ",@DhameenName = '" + form.dhameen_name.data
    query += "', @DhameenMobileNumber1 = " + sql_text(form.dhameen_mobile1.data)
    query += ", @DhameenMobileNumber2 = " + sql_text(form.dhameen_mobile2.data)
    query += ", @Deposit = " + sql_text(form.deposit.data)
    query += ", @Comment = '" + form.comment.data + \
        "', @MeterMake = '" + form.meter_make.data + \
        "', @MeterModel = '" + form.meter_model.data
    query += "', @MeterSerialNo = '" + form.meter_serial_no.data + \
        "', @TagSerialNo = '" + form.tag_serial_no.data + \
        "', @ModifiedByUser = '" + form.user.data
    query += "', @NewMeterRead = " + sql_text(form.meter_read.data)
    query += ", @Option = '" + dict(form.update_option.choices).get(form.update_option.data) + "'"

    connection = db.engine.raw_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    update_customer = cursor.execute(query)
    connection.commit()
    connection.close()

    if not update_customer:
        return False
    return True


def getCustomerInfoForWeb(barcode):
    # meter = Meter.query.filter_by(Meter.MeterBarcodeNo=barcode).first()
    customer_info = db.engine.execute(
        "dbo.Customer_View_Header ?", barcode).first()

    historys = UsageHistory.query.filter_by(
        MeterBarcodeNo=barcode).order_by(UsageHistory.UsageId.desc()).first()

    db.session.commit()
    return customer_info, historys


def add_customer(firstname, lastname, mobile1, mobile2, mobile3, mobile4, district, city, neighbour, houseTaxId, customerType, accountStatus, dhameenName,
                 dhameenMobile1, dhameenMobile2, deposit, comment, meterMake, meterModel, meterSerialNo, tagSerialNo, currKw, createdUser):
    if(accountStatus == "On"):
        accountStatus = 1
    else:
        accountStatus = 0

    if mobile2 == None:
        mobile2 = 0
    if mobile3 == None:
        mobile3 = 0
    if mobile4 == None:
        mobile4 = 0

    if dhameenMobile1 == None:
        dhameenMobile1 = 0
    if dhameenMobile2 == None:
        dhameenMobile2 = 0
    if currKw == None or currKw == "":
        currKw = "0"
    if deposit == None or deposit == "":
        deposit = "0"

    query = "EXEC sp_CustomerInsert @FirstName = '" + \
        firstname + "', @LastName = '" + lastname
    query += "' ,@MobileNumber1 = " + \
        str(mobile1) + ",@MobileNumber2 = " + str(mobile2)
    query += ",@MobileNumber3 = " + \
        str(mobile3) + ",@MobileNumber4 = " + str(mobile4)
    query += ", @DistrictArea = '" + district + \
        "', @City = '" + city + "', @Neighbour = '" + neighbour
    query += "', @HouseTaxIdNumber = '" + houseTaxId + \
        "', @CustomerType = '" + customerType
    query += "', @AccountStatus = " + \
        str(accountStatus) + ",@DhameenName = '" + dhameenName
    query += "', @DhameenMobileNumber1 = " + \
        str(dhameenMobile1) + ", @DhameenMobileNumber2 = " + str(dhameenMobile2)
    query += ", @Deposit = " + str(deposit) + ", @Comment = '" + \
        comment + "', @MeterMake = '" + meterMake
    query += "', @MeterModel = '" + meterModel + \
        "', @MeterSerialNo = '" + meterSerialNo
    query += "', @TagSerialNo = '" + tagSerialNo + \
        "', @CurrentMeterKw = '" + str(currKw)
    query += "', @CreatedByUser = '" + createdUser + "'"
    
    connection = db.engine.raw_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    # cursor.execute('SET NOCOUNT ON; ' + query)
    cursor.execute(query)
    new_customer_barcode = cursor.fetchone()
    connection.commit()
    
    # connection = db.engine.raw_connection()
    # cursor = connection.cursor()
    # cursor.execute('SET NOCOUNT OFF; ' + query)
    # connection.commit()

    return new_customer_barcode

def customer_usage_serialize(row):
    prevDate = row.PrevReadDate.strftime('%b/%d/%Y')

    return {
        "SupplyNo": row.SupplyNo,
        "CustomerId": row.CustomerId,
        "MeterId": row.MeterId,
        "MeterBarcodeNo": row.MeterBarcodeNo,
        "Name": row.Name,
        "PrevRead": row.PrevRead,
        "PrevDate": prevDate,
        # "Biller": row.Biller,
        "User": session['username'],
        "BillingMonth": row.BillingMonth,
        "CurrRead": "",
        "UnitRate": "",
        "Discounted": False,
        "Discount": "",
        "ChkDiscounted": ' <td> <input type="checkbox" id="d' + row.MeterBarcodeNo + '"> </td> ',
        "UsedKw": "0.0",
        "Bill": "0.0"
    }


def customer_usages_for_month_district(month, district):
    usages_list = [customer_usage_serialize(x) for x in db.engine.execute(
        "dbo.sp_Customer_UsageManualShow ?, ?", month, district).fetchall()]
    db.session.commit()
    if usages_list:
        return jsonify({'usagesList': usages_list})
    return jsonify({'usagesList': []})


def customer_manual_read(request):
    Datas = request.json['sendData']
    for data in Datas :
        meterId = data['MeterId']
        customerId = data['CustomerId']
        barcode = data['MeterBarcodeNo']
        prevRead = data['PrevRead']
        prevDate = data['PrevDate']
        currRead = data['CurrRead']
        unitRate = data['UnitRate']
        discounted = data['Discounted']
        # biller = data['Biller']
        user = session['username']
        usedKW = data['UsedKw']
        bill = data['Bill']

        # prevDate = datetime.strptime(prevDate, '%a, %d %b %Y %H:%M:%S %Z')
        prevDate = datetime.strptime(prevDate, '%b/%d/%Y')

        newHistory = UsageHistory(Meterid=meterId, CustomerId=customerId, MeterBarcodeNo=barcode, PrevRead=prevRead, PrevReadDate=prevDate,
                                CurrRead=currRead, CurrReadDate=datetime.now(), UsedKW=usedKW, UnitRate = unitRate,
                                Discounted = discounted, Bill = bill, Description = 'Manually insert from web', CreatedByUser = user, 
                                CreateDate = datetime.now() )

        db.session.add(newHistory)
        db.session.commit()

    return jsonify({'result': "success"}), 200

def getDistricts():
    districts = District.query.all()
    districtList = []
    if session['accessType'] == "Admin" or session['accessType'] == "Back-office":
        districtList = districts
    else:
        for district in districts:
            if session['username'] == district.BillerResponsible:
                districtList.append(district)

    return districtList

def getMonths():
    query = "SELECT BillingMonth FROM vw_BillingMonths_current WHERE CurrentBillingMonth = 1"
    connection = db.engine.raw_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    monthList = cursor.execute(query).fetchall()
    connection.commit()
    connection.close()

    return monthList

def payment_manual_list_item_serialize(row):
    return {
        "SupplyNo": row.SupplyNo,
        "UsageId": row.UsageId,
        "Barcode": row.MeterBarcodeNo,
        "ReadDate": row.CurrReadDate.strftime('%Y-%m-%d'),
        "PrevRead": row.PrevRead,
        "CurrRead": row.CurrRead,
        "UsedKw": row.UsedKw,
        "Bill": row.Bill,
        "ChkPaymentType": '<td><select class="payment_select" style="border: none" id="pt_' + row.MeterBarcodeNo + '">' + \
                        '<option value="Collector">Collector</option>' + \
                        '<option value="EVC">EVC</option>' + \
                        '<option value="Cheque">Cheque</option>' + \
                        '<option value="Bank Transfer">Bank Transfer</option>' + \
                        '<option value="Cash">Cash</option></select></td>',
        "PaymentType":"Collector",
        "Paid": "",
        "UnitRate": "",
        "Discount": "",
        "Discounted": False,
        "ChkDiscounted": ' <td> <input type="checkbox" id="b_' + row.MeterBarcodeNo + '"> </td> ',
        "Outstanding": row.OutstandingBalance,
        "Biller": session['username'],
        "BillingMonth": row.BillingMonth
    }

def getManualPaymentList(district, month):
    paymentManualList = db.engine.execute("dbo.sp_Customer_PaymentManualShow ?, ?", month, district).fetchall()
    db.session.commit()
    # SupplyNo, UsageId, MeterBarcodeNo, Name, CurrReadDate, PrevRead, CurrRead, UsedKw, Bill, Paid, UnitRate, Discount,
    # OutstandingBalance, BillingMonth, LastPayment, LastPaymentDate
    return jsonify({"data":[ payment_manual_list_item_serialize(row) for row in paymentManualList]})

def customer_payment_save(request):
    Datas = request.json['sendData']
    for data in Datas :
        usageId = data['UsageId']
        barcode = data['Barcode']
        meter = Meter.query.filter_by(MeterBarcodeNo=barcode).first()
        customerId = meter.CustomerId
        paymentType = data['PaymentType']
        currency = "USD"
        paid = data['Paid']
        unitRate = data['UnitRate']
        discount = data['Discount']
        outstanding = data['Outstanding']
        description = "Manually insert from web"
        billingMonth = data['BillingMonth']
        biller = data['Biller']
        discounted = data['Discounted']
        
        newPaid = Payment(UsageId=usageId, CustomerId=customerId, MeterBarcodeNo=barcode, PaymentType=paymentType,
                          Currency=currency, Paid=paid, UnitRate=unitRate, Discount=discount, Discounted=discounted,
                          OutstandingBalance=outstanding, Description=description, BillingMonth=billingMonth,
                          CreatedByUser=biller, CreatedDate=datetime.now())

        db.session.add(newPaid)
        db.session.commit()

    return jsonify({'result': "success"}), 200

def view_usage_item_serialize(row):
    return {
        "UsageId": row.UsageId,
        "CustomerId": row.CustomerId,
        "PrevReadDate": row.PrevReadDate.strftime("%Y-%m-%d"),
        "PrevRead": row.PrevRead,
        "CurrReadDate": row.CurrReadDate.strftime("%Y-%m-%d"),
        "CurrRead": row.CurrRead,
        "UsedKw": row.UsedKw,
        "UnitRate": row.UnitRate,
        "Bill": row.Bill,
        "BillingMonth": row.BillingMonth
    }
    
def get_view_customer_usage(barcode):
    customer_usages = db.engine.execute("dbo.sp_Customer_View_UsageHistory ?", barcode).fetchall()
    db.session.commit()
    return jsonify({"data":[ view_usage_item_serialize(row) for row in customer_usages]})

def view_bill_item_serialize(row):
    return {
        "CustomerId": row.CustomerId,
        "PrevReadDate": row.PrevReadDate.strftime("%Y-%m-%d"),
        "PrevRead": row.PrevRead,
        "CurrReadDate": row.CurrReadDate.strftime("%Y-%m-%d"),
        "CurrRead": row.CurrRead,
        "UsedKw": row.UsedKw,
        "UnitRate": row.UnitRate,
        "Bill": row.Bill,
        "BillingMonth": row.BillingMonth,
        "NoOfRead": row.NoOfReadsTaken
    }
    
def get_view_customer_bill(barcode):
    customer_bills = db.engine.execute("dbo.sp_Customer_View_UsageHistory_ByBillingMonth ?", barcode).fetchall()
    db.session.commit()
    return jsonify({"data":[ view_bill_item_serialize(row) for row in customer_bills]})

def view_payment_item_serialize(row):
    return {
        "SupplyNo": row.SupplyNo,
        "CustomerId": row.CustomerId,
        "PaymentType": row.PaymentType,
        "Paid": row.Paid,
        "Discount": row.Discount,
        "Outstanding": row.Outstandingbalance,
        "BillingMonth": row.BillingMonth,
        "User": row.CreatedByuser,
        "CreateDate": row.CreateDate.strftime("%Y-%m-%d")
    }
    
def get_view_customer_payment(barcode):
    customer_payments = db.engine.execute("dbo.sp_Customer_View_Payments ?", barcode).fetchall()
    db.session.commit()
    return jsonify({"data":[ view_payment_item_serialize(row) for row in customer_payments]})
