#!/usr/bin/python
#-*-coding:utf-8-*-
# This program will perform API calls necessary to demonstrate API capability in
# Cisco NFVIS. This program will also reset the ENFV DNA Demo enviroment
# Order of operations for reset is as follows:
# API calls to decomission SDWAN routers in vManage
# API calls to delete VNF's at all sites
# API calls to delete SDWAN registered images at all sites
# API call to delete Site200 ENCS from DNA-C inventory
# API call to rediscover Site200
# Repackage SDWAN NFVIS tar balls
# Upload packages tar ball to site

import requests
import json
from requests.auth import HTTPBasicAuth
import getpass

requests.packages.urllib3.disable_warnings()

print("####DNA Demo Automation Tool####")

def getcreds():
    #Collects NFVIS IP Address, Username, and Password
    global nfvis
    nfvis = input("What is the IP address of the NFVIS system: ")
    global url
    url = "https://" + nfvis
    print("Enter your username and password.")
    global username
    username = input("Username:")
    global password
    password = getpass.getpass()
    return url, username, password

#Menu Options
def print_options():
    print("Options: ")
    print(" '1' List system information")
    print(" '2' List running VNF's")
    print(" '3' Delete VNF")
    print(" '4' Deploy VNF")
    print(" '5' Reset demo environment")
    print(" 'c' Change system IP and credentials")
    print(" 'p' print options")
    print(" 'q' quit the program")

getcreds()

choice = "p"
while choice != "q":
    if choice == "1":
        #API call to retrieve system info, then displays it, return to options
        response = requests.get(url + "/api/operational/platform-detail", verify=False, auth=HTTPBasicAuth(username, password),
                                headers={'content-type':'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
        print(response.status_code)
        print(url + "/api/operational/platform-detail")
        try:
            parsed_json = json.loads(response.content)
            print(json.dumps(parsed_json, indent = 4,sort_keys=False))
        except Exception as e:
            print(repr(e))
        print_options()
        choice = input("Option: ")
    elif choice == "2":
        #API call to list running VNFs, display info, return to options
        print("Currently Running VNF's...")
        response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False, auth=HTTPBasicAuth(username, password),
                                headers={'content-type':'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
        print(response.status_code)
        print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments")
        try:
            parsed_json = json.loads(response.content)
            print(json.dumps(parsed_json, indent = 4,sort_keys=False))
        except Exception as e:
            print(repr(e))
        print_options()
        choice = input("Option: ")
    elif choice == "3":
        #API call to delete VNF on NFVIS device
        vnf = input("What VNF would you like to delete?")
        response = requests.delete(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf, verify=False, auth=HTTPBasicAuth(username, password),
                                headers={'content-type': 'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
        print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf)
        if response.status_code != 204:
            print("VNF deletion failed")
            print(response.status_code)
        else:
            print("VNF deletion successful")
            print(response.status_code)
        print_options()
        choice = input("Option: ")
    elif choice == "4":
        #API call to deploy VNF on NFVIS device
        vnfdata = input("What is the name of data file for the VNF to be deployed?")
        contents = open(vnfdata).read()
        print(contents)
        response = requests.post(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments",
                                   verify=False, auth=HTTPBasicAuth(username, password),
                                   headers={'content-type': 'application/vnd.yang.data+xml',
                                            'Accept': 'application/vnd.yang.data+xml'}, data=contents)
        print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/")
        if response.status_code != 201:
            print("VNF deployment failed")
            print(response.status_code)
            print(response)
        else:
            print("VNF deployment successful")
            print(response.status_code)
        print_options()
        choice = input("Option: ")
    elif choice == "5":
        #API call to reset demo environment, print demo environment reset
        print("The demo environment is being reset. Please be patient...5")
        print_options()
        choice = input("Option: ")
    elif choice == "c":
        #Call getcreds function to change System IP and credentials
        getcreds()
        print_options()
        choice = input("Option: ")
    elif choice == "p":
        print_options()
        choice = input("Option: ")
