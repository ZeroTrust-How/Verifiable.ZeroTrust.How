#!/usr/bin/python

from flask import Flask, render_template
from flask import request,Response,redirect
from flask_caching import Cache
from flask.json import jsonify
import json
import logging
import sys, os, tempfile, uuid, time, datetime
import configparser
import argparse
import requests
from random import randint
import msal
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from common.extensions import cache
from Issuance.identityIssuer import identity_issuer 
from Presentations.identityVerifier import identity_verifier
from Issuance.employerIssuer import employer_issuer
from Issuance.insuranceIssuer import insurance_issuer
from Presentations.identityEmployeeVerifier import identity_employee_verifier
from Presentations.identityInsuranceVerifier import identity_insurance_verifier

cacheConfig = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__,static_url_path='',static_folder='static',template_folder='static')
app.register_blueprint(identity_issuer)
app.register_blueprint(identity_verifier)
app.register_blueprint(employer_issuer)
app.register_blueprint(insurance_issuer)
app.register_blueprint(identity_employee_verifier)
app.register_blueprint(identity_insurance_verifier)

cache.init_app(app, config=cacheConfig)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/identity-provider/')
def identityProvider():
    return render_template('identity-issuer.html')

@app.route('/identity-verification/')
def identityVerifier():
    return render_template('identity-verifier.html')

@app.route('/employer/')
def employer():
    return render_template('employer-verify_issue.html')

@app.route('/insurance-provider/')
def insuranceProvider():
    return render_template('insurance-provider.html')

@app.route('/insurance-individual/')
def insuranceIndividual():
    return render_template('insurance-individual-verify_issue.html')

@app.route('/insurance-group/')
def insuranceGroup():
    return render_template('insurance-group-verify_issue.html')

@app.route('/healthcare-provider/')
def healthcareProvider():
    return render_template('healthcare-verifier.html')

    
@app.route('/picture-credits/')
def pictureCredits():
    return render_template('picture-credits.html')

@app.route("/echo", methods = ['GET'])
def echoApi():
    result = {
        'date': datetime.datetime.utcnow().isoformat(),
        'api': request.url,
        'Host': request.headers.get('host'),
        'x-forwarded-for': request.headers.get('x-forwarded-for'),
        'x-original-host': request.headers.get('x-original-host')
    }
    return Response( json.dumps(result), status=200, mimetype='application/json')

if __name__ == "__main__":
    port = os.getenv('PORT')
    if port is None:
        port = 5000
    app.run(host="0.0.0.0", port=port)