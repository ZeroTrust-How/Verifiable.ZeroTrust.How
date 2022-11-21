#!/usr/bin/python

from flask import Flask
from flask_caching import Cache
import json
import logging
import sys, os
import requests
import msal
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

cache = Cache()

log = logging.getLogger() 
log.setLevel(logging.INFO)

configFile = os.getenv('CONFIGFILE')
if configFile is None:
    configFile = os.path.realpath(os.path.join(os.path.dirname(__file__), 'config.json'))
    #configFile = sys.argv[1]
config = json.load(open(configFile))

msalCca = msal.ConfidentialClientApplication( config["azClientId"], 
    authority="https://login.microsoftonline.com/" + config["azTenantId"],
    client_credential=config["azClientSecret"],
    )

if config["azCertificateName"] != "":
    with open(config["azCertificatePrivateKeyLocation"], "rb") as file:
        private_key = file.read()
    with open(config["azCertificateLocation"]) as file:
        public_certificate = file.read()
    cert = load_pem_x509_certificate(data=bytes(public_certificate, 'UTF-8'), backend=default_backend())
    thumbprint = (cert.fingerprint(hashes.SHA1()).hex())
    print("Cert based auth using thumbprint: " + thumbprint)    
    msalCca = msal.ConfidentialClientApplication( config["azClientId"], 
       authority="https://login.microsoftonline.com/" + config["azTenantId"],
        client_credential={
            "private_key": private_key,
            "thumbprint": thumbprint,
            "public_certificate": public_certificate
        }
    )    

# Check if it is an EU tenant and set up the endpoint for it
r = requests.get("https://login.microsoftonline.com/" + config["azTenantId"] + "/v2.0/.well-known/openid-configuration")
resp = r.json()
print("tenant_region_scope = " + resp["tenant_region_scope"])
config["tenant_region_scope"] = resp["tenant_region_scope"]
config["msIdentityHostName"] = "https://verifiedid.did.msidentity.com/v1.0/"
# Check that the Credential Manifest URL is in the same tenant Region and throw an error if it's not
if False == config["CredentialManifest"].startswith( config["msIdentityHostName"] ):
    raise ValueError("Error in config file. CredentialManifest URL configured for wrong tenant region. Should start with: " + config["msIdentityHostName"])