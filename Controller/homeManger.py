from flask_httpauth import HTTPBasicAuth
from model import *
from sqlalchemy import func, text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, json, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def recent_customer_item_serialize(meter, customer, customerDetail):
    return {
        "Name": customer.FirstName + " " + customer.LastName,
        "createdDate": customer.CreateDate,
        "MeterBarcodeNo": meter.MeterBarcodeNo,
        "Phone": customerDetail.MobileNumber1,
        "SupplyNo": customer.SupplyNo,
        "CustomerType": customer.CustomerType,
        "Comment": customerDetail.Comment
    }

def getTotalUsagePerMonth():
    # curtime = datetime.today()
    # cy = curtime.year-1
    # cm = curtime.month + 1
    # if cm > 12:
    #     cm = cm - 12
    #     cy = cy + 1

    # UsagesPerMonth = []
    # for i in range(0, 12):
    #     start = datetime(cy, cm, 1)
    #     em = cm+1
    #     ey = cy
    #     if em > 12:
    #         ey = ey+1
    #         em = 1
    #     end = datetime(ey, em, 1)

    #     usage = sum(usage.UsedKW for usage in UsageHistory.query.filter(
    #         UsageHistory.CurrReadDate >= start, UsageHistory.CurrReadDate < end).all())
    #     UsagesPerMonth.append({"Month": str(ey)+"-"+str(em), "Usage": usage})
    #     cm = cm+1
    #     if cm > 12:
    #         cy = cy+1
    #         cm = 1

    # db.session.commit()
    
    UsagesPerMonth = db.engine.execute("dbo.sp_Report_Home_AllUsagesPerMonth").fetchall()
    db.session.commit()

    return [{ "BillingMonth":row.BillingMonth,
             "Used":row.Used, 
             "NoOfMetersRead":row.NoOfMetersRead,
             "MonthlyNewUsers":row.MonthlyNewUsers,
             "Customers":row.Customers } for row in UsagesPerMonth]

def serializeRecentRead(row):
    discounted = "Yes"
    if row.Discounted is False:
        discounted = "No"
    return {
        "Name": row.FirstName + " " + row.LastName,
        "MeterBarcodeNo": row.MeterBarcodeNo,
        "PrevRead": row.PrevRead,
        "CurrRead": row.CurrRead,
        "UsedKW": row.UsedKW,
        "Bill": row.Bill,
        "Image": row.Image,
        "CreatedByUser": row.CreatedByUser,
        "SupplyNo": row.SupplyNo,
        "Discounted": discounted,
        "CurrReadDate": row.CurrReadDate.strftime('%Y-%m-%d')
    }

def getRecentReads():
    reads = False
    if session['accessType'] == "Admin" or session['accessType'] == "Back-office":
        reads = UsageHistory.query.join(Meter, UsageHistory.MeterBarcodeNo==Meter.MeterBarcodeNo).\
                join(Customer, Meter.CustomerId==Customer.CustomerId).\
                add_columns(UsageHistory.MeterBarcodeNo, UsageHistory.PrevRead, UsageHistory.CurrRead,\
                             UsageHistory.UsedKW, UsageHistory.Bill, UsageHistory.Image, UsageHistory.CreatedByUser,\
                             Customer.SupplyNo, Customer.FirstName, Customer.LastName, UsageHistory.UnitRate,\
                             UsageHistory.Discounted, UsageHistory.CurrReadDate).\
                order_by(UsageHistory.UsageId.desc()).limit(5).all()
        # reads = UsageHistory.query.order_by(UsageHistory.UsageId.desc()).limit(5).all()
    else:
        # reads = UsageHistory.query.filter_by(CreatedByUser=session['username']).order_by(UsageHistory.UsageId.desc()).limit(5).all()
        reads = UsageHistory.query.join(Meter, UsageHistory.MeterBarcodeNo==Meter.MeterBarcodeNo).\
                join(Customer, Meter.CustomerId==Customer.CustomerId).\
                add_columns(UsageHistory.MeterBarcodeNo, UsageHistory.PrevRead, UsageHistory.CurrRead,\
                             UsageHistory.UsedKW, UsageHistory.Bill, UsageHistory.Image, UsageHistory.CreatedByUser,\
                             Customer.SupplyNo, Customer.FirstName, Customer.LastName, UsageHistory.UnitRate,\
                             UsageHistory.Discounted, UsageHistory.CurrReadDate).\
                filter(UsageHistory.CreatedByUser == session['username']).\
                order_by(UsageHistory.UsageId.desc()).limit(5).all()
    # SupplyNo, and CustomerName, UnitRate, Discounted, Curr Read Date
    db.session.commit()    
    if not reads:
        return False
    return [serializeRecentRead(row) for row in reads]

def getRecentCustomers():
    if session['accessType'] != "Admin" and session['accessType'] != "Back-office":
        username = session['username']
        districts = District.query.filter_by(BillerResponsible=username).all()
        db.session.commit()
        
        if not districts:
            return False, False

        cond = []
        for district in districts:
            cond.append(district.DistrictId)
        meters = Meter.query.filter(Meter.DistrictId.in_(cond)).order_by(
            Meter.MeterId.desc()).limit(5).all()
        db.session.commit()
    else:
        meters = Meter.query.order_by(Meter.MeterId.desc()).limit(5).all()
        db.session.commit()

    if not meters:
        return False

    customers = []
    for meter in meters:
        customer = Customer.query.filter_by(
            CustomerId=meter.CustomerId).first()
        if not customer:
            db.session.commit()
            return False

        customerDetail = CustomerDetail.query.filter_by(
            CustomerId=meter.CustomerId).first()
        db.session.commit()
        if not customerDetail:
            return False
        customers.append(recent_customer_item_serialize(
            meter, customer, customerDetail))
    
    return customers

def getDistricts():
    districts = District.query.all()
    districtList = []
    
    for district in districts:
        districtList.append(district.DistrictCode)
    
    return districtList

def get_usage_customers_by_district():
    rows = db.engine.execute("dbo.sp_Report_Home_AllUsagesandCustomersPerMonthByDistrict").fetchall()
    db.session.commit()
    districts = getDistricts()
    months = []
    
    for row in rows:
        if len(months) < 1:
            months.append(row.BillingMonth)
            continue
        isNew = True
        for i in range(0, len(months)):
            if months[i] == row.BillingMonth:
                isNew = False
                break
        if isNew:
            months.append(row.BillingMonth)
                
    months.insert(0, "All")
    
    totalList = [{"district":district, 
                  "totalPerMonth": [{"month": month,
                                     "UsedKw": 0,
                                     "ChangeCustomer": 0,
                                     "Customers": 0} for month in months ]} for district in districts]
    
    for row in rows:
        for total in totalList:
            if row.DistrictCode == total['district']:
                for monthData in total['totalPerMonth']:
                    if row.BillingMonth == monthData['month']:
                        monthData['UsedKw'] = row.UsedKw
                        monthData['ChangeCustomer'] = row.CustomersCountChangesPerMonth
                        monthData['Customers'] = row.Customers
                        break
                break
            
    for total in totalList:
        usedSum = chageSum = 0
        length = len(total['totalPerMonth'])    
        for i in range(1,length):
            usedSum += total['totalPerMonth'][i]['UsedKw']
            chageSum += total['totalPerMonth'][i]['ChangeCustomer']
        
        total['totalPerMonth'][0]['UsedKw'] = usedSum
        total['totalPerMonth'][0]['Customers'] = total['totalPerMonth'][length-1]['Customers']
        total['totalPerMonth'][0]['ChangeCustomer'] = chageSum
    
    return months, totalList
                
    # districts = District.query.all()
    # db.session.commit()
    # if not districts:
    #     return False, False, False

    # districtNames = []
    # customerCnts = []
    # usages = []
    # for district in districts:
    #     usage = 0
    #     meters = Meter.query.filter_by(DistrictId=district.DistrictId).all()
    #     db.session.commit()
    #     if not meters:
    #         return False, False, False

    #     for meter in meters:
    #         usageHistory = UsageHistory.query.filter_by(CustomerId=meter.CustomerId).order_by(
    #             UsageHistory.UsageId.desc()).limit(1).first()
    #         if usageHistory:
    #             usage = usage + usageHistory.CurrRead
    #     districtNames.append(district.DistrictCode)
    #     customerCnts.append(len(meters))
    #     usages.append(usage)

    # db.session.commit()
    # return districtNames, customerCnts, usages
