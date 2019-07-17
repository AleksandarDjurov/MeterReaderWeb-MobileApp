from flask import session
from model import *

def serialize_report(row):
    session['No'] = session['No'] + 1
    # BillingMonth, TotalPaymentReceived, NoOfPayments, AveragePayment
    return {
        "No": session['No'],
        "BillingMonth": str(row.BillingMonth),
        "TotalPaymentReceived": str(row.TotalPaymentReceived),
        "NoOfPayments": str(row.NoOfPayments),
        "AveragePayment": str(row.AveragePayment)
    }

def get_report_list():
    # type : Received, Sent, TransferFromBank
    session['No'] = 0
    reportList = [serialize_report(x) for x in db.engine.execute(
        "dbo.sp_Report_EVCReport").fetchall()]
    db.session.commit()
    if reportList:
        return jsonify({'reportList': reportList})
    else:
        return jsonify({'reportList': []})

def sqlText( data ):
    if not data:
        return ""
    else:
        return data

def sqlNumber( data ):
    if not data:
        return 0
    else:
        return data

def serialize_report_discounted(row):
    session['No'] = session['No'] + 1
    return {
        "No": session['No'],
        "UsageId": sqlText(row.UsageId),
        "SupplyNo": sqlText(row.SupplyNo),
        "CustomerName": sqlText(row.CustomerName),
        "MeterBarcodeNo": sqlText(row.MeterBarcodeNo),
        "PrevRead": sqlNumber(row.PrevRead),
        "CurrRead": sqlNumber(row.CurrRead),
        "UsedKW": sqlText(row.UsedKW),
        "UnitRate": sqlNumber(row.UnitRate),
        "Bill": sqlNumber(row.Bill),
        "Discounted": round(row.Discounted, 2),
        "Biller": sqlText(row.Biller),
        "CreateDate": row.CreateDate.strftime('%Y-%m-%d')
    }
    
def get_report_discounted_list(month):
    session['No'] = 0
    reportDiscountedList = [serialize_report_discounted(x) for x in db.engine.execute(
        "dbo.sp_Report_DiscountReport ?", month).fetchall()]
    db.session.commit()
    if reportDiscountedList:
        return jsonify({'reportDiscountedList': reportDiscountedList})
    else:
        return jsonify({'reportDiscountedList': []})

def serialize_report_usage(row):
    session['No'] = session['No'] + 1
    prevDate = ""
    if row.PrevReadDate:
        prevDate = row.PrevReadDate.strftime('%Y-%m-%d')
    currDate = ""
    if row.CurrReadDate:
        currDate = row.CurrReadDate.strftime('%Y-%m-%d')

    return {
        "No": session['No'],
        "SupplyNo": sqlText(row.SupplyNo),
        "Name": sqlText(row.Name),
        "MeterBarcodeNo": sqlText(row.MeterBarcodeNo),
        "PrevReadDate": prevDate,
        "CurrReadDate": currDate,
        "PrevRead": sqlNumber(row.PrevRead),
        "CurrRead": sqlNumber(row.CurrRead),
        "UsedKW": sqlNumber(row.UsedKw),
        "UnitRate": sqlNumber(row.UnitRate),
        "Discounted": row.Discounted,
        "Bill": sqlNumber(row.Bill),
        "Biller": sqlText(row.CreatedByUser),
        "CreateDate": row.CreateDate.strftime('%Y-%m-%d')
    }

def get_report_usage_list(month, isread):
    session['No'] = 0
    reportUsageList = [serialize_report_usage(x) for x in db.engine.execute(
        "dbo.sp_Report_UsageReport ?, ?", month, isread).fetchall()]
    db.session.commit()
    if reportUsageList:
        return jsonify({'reportUsageList': reportUsageList})
    else:
        return jsonify({'reportUsageList': []})
