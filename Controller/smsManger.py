from flask import session
from model import *

def serialize(row):
    session['No'] = session['No'] + 1
    # SmsId, SentFromNumber, SmsMessage, SentDateTime, CreateDate, MoneyDirection, Amount, Phone
    return {
        "No": session['No'],
        "Assign": '''<div class="dropdown">
            <button class="btn btn-info dropdown-toggle" data-toggle="dropdown" aria-expanded="false" type="button">Assign <span class="caret"></span></button>
            <ul class="dropdown-menu dropdown-menu-right" role="menu">
                <li><a  class="dropdown-item" id="ci_''' + str(row.SmsId) + '''">Customer Id</a></li>
                <li><a  class="dropdown-item" id="mb_''' + str(row.SmsId) + '''">Meter Barcode No</a></li>
            </ul></div>
        ''',
        "SmsId": row.SmsId,
        "SentFromNumber": row.SentFromNumber,
        "SmsMessage": row.SmsMessage,
        "SentDateTime": row.SentDateTime,
        "Amount": row.Amount,
        "Phone": row.Phone,
        "User":session['username']
    }

def get_sms_list( type ):
    # type : Received, Sent, TransferFromBank
    session['No'] = 0
    smsList = [serialize(x) for x in db.engine.execute(
        "dbo.sp_EVC ?", type).fetchall()]
    db.session.commit()
    if smsList:
        return jsonify({'smsList': smsList})
    else:
        return None