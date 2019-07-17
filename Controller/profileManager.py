from flask_httpauth import HTTPBasicAuth
from model import *
from sqlalchemy import func, text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, json, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def update_user(json):
    user = User.query.filter_by(username=session['username']).first()
    db.session.commit()
    if user is None:
        return None  # not existing user
    
    update_type = json['update_type']
    newname = json['username']
    phone = json['phone']
    password = json['password']
    confirm_password = json['confirm_password']
    
    if update_type == "profile":
        user.username = newname
        user.Phone = phone
    else:
        user.hash_password(password)

    db.session.commit()
    return user

def getLogedinUserInfo():
    return User.query.filter_by(username=session['username']).first()