import datetime
from flask import Flask
from flask import request
import pymongo
import requests
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/dbopenapi',
    'APISPEC_SWAGGER_UI_URL': '/dbswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)

cors = CORS(app)
service_name = "admin_core_service"
service_ip = "35.190.119.123"

ecostreet_core_service = "35.190.119.123"
database_core_service = "35.190.119.123"
configuration_core_service = "35.190.119.123"


class NoneSchema(Schema):
    response = fields.Str()

# HEALTH PAGE
@app.route("/")
@marshal_with(NoneSchema, description='200 OK', code=200)
def health():
    return {"response": "200"}, 200
docs.register(health)

# HOME PAGE
@app.route("/ad")
@marshal_with(NoneSchema, description='200 OK', code=200)
def hello_world():
    return {"response": "Admin microservice."}, 200
docs.register(hello_world)


 
# SERVICE IP UPDATE FUNCTION
@app.route("/adupdate_ip", methods = ['POST'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def update_ip():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global service_ip
    global service_name
    global users
    print("/adupdate_ip accessed")
    
    service_ip = request.form["ip"]
    
    data = {"name": service_name, "ip": service_ip}
    try:
        url = 'http://' + configuration_core_service + '/cfupdate'
        response = requests.post(url, data=data)
        return {"response": response.text}, 200
    except:
        return {"response": "Something went wrong."}, 500
docs.register(update_ip)

# FUNCTION TO UPDATE IP'S OF OTHER SERVICES
@app.route("/adconfig", methods = ['POST'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def config_update():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global service_ip
    global service_name
    global users
    print("/adconfig accessed")
    
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        if microservice == "database_core_service":
            database_core_service = ms_ip
        if microservice == "ecostreet_core_service":
            ecostreet_core_service = ms_ip
        if microservice == "configuration_core_service":
            configuration_core_service = ms_ip
        return {"response": "200 OK"}, 200
    except Exception as err:
        return {"response": "Something went wrong."}, 500
docs.register(config_update)

# FUNCTION TO GET CURRENT CONFIG
@app.route("/adgetconfig")
@marshal_with(NoneSchema, description='200 OK', code=200)
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global service_ip
    global service_name
    global users
    print("/adgetconfig accessed")
    
    return {"response": str([ecostreet_core_service, configuration_core_service, database_core_service])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/admetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
def get_health():
    print("/admetrics accessed")
    start = datetime.datetime.now()
    try:
        url = 'http://' + database_core_service + '/cfhealthcheck'
        response = requests.get(url)
    except Exception as err:
        return {"response": "METRIC CHECK FAIL: configuration unavailable"}, 500
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/lghealthcheck'
        response = requests.get(url)
    except Exception as err:
        return {"response": "METRIC CHECK FAIL: login service unavailable"}, 500
    end2 = datetime.datetime.now()
    
    delta1 = end-start
    crt = delta1.total_seconds() * 1000
    delta2 = end2-start2
    lrt = delta2.total_seconds() * 1000
    health = {"metric check": "successful", "database response time": crt, "login response time": lrt}
    return {"response": str(health)}, 200
docs.register(get_health)

# HEALTH CHECK
@app.route("/adhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
def send_health():
    print("/adhealthcheck accessed")
    try:
        url = 'http://' + ecostreet_core_service + '/lg'
        response = requests.get(url)
        url = 'http://' + configuration_core_service + '/cf'
        response = requests.get(url)
        url = 'http://' + database_core_service + '/db'
        response = requests.get(url)
    except Exception as err:
        return {"response": "Healthcheck fail: depending services unavailable"}, 500
    return {"response": "200 OK"}, 200
docs.register(send_health)
