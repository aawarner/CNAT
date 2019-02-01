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

import sys
import requests
import json
import getpass
from requests.auth import HTTPBasicAuth

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
    username = input("Username: ")
    global password
    password = getpass.getpass()
    return

def sdwan_reset():
    response = requests.get("https://" + vmanage + "/dataservice/system/device/vedges", verify=False,
                            auth=HTTPBasicAuth(vmanage_username, vmanage_password),
                            headers={'content-type': 'application/json', 'Accept': 'application/json'})
    print("API Response Code: ", response.status_code)
    print("https://" + vmanage + "/dataservice/system/device/vedges")
    if response.status_code == 401:
        print("Authentication Failed to Device")
        sys.exit()
    else:
        print()
    print("Getting list of SDWAN UUID's from vManage:")
    print()
    data = response.json()
    for event in data["data"]:
        print(event["uuid"])
    print()
    uuid = input("Enter the UUID of the SDWAN router you wish to decommission: ")
    print("Deccommissioning SDWAN Router...")
    response = requests.put("https://" + vmanage + "/dataservice/system/device/decommission/" + uuid, verify=False,
                            auth=HTTPBasicAuth(vmanage_username, vmanage_password),
                            headers={'content-type': 'application/json', 'Accept': 'application/json'})
    print("API Response Code: ", response.status_code)
    print()
    if response.status_code != 200:
        print("SDWAN decommissioning failed")
        print()
    else:
        print("SDWAN decommissioning successful")
        print()
    return

def nfvis_reset():
    getcreds()
    print("Currently Deployed VNF's...")
    response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False,
                            auth=HTTPBasicAuth(username, password),
                            headers={'content-type': 'application/vnd.yang.collection+json',
                                     'Accept': 'application/vnd.yang.data+json'})
    print("API Response Code: ", response.status_code)
    print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments")
    if response.status_code == 401:
        print()
        print("Authentication Failed to Device")
        sys.exit()
    else:
        print()
    try:
        data = response.json()
        for event in data["vmlc:deployments"]["deployment"]:
            print(event["name"])
    except Exception as e:
        if response.status_code == 204:
            print("There are no running VNF deployments on device.")
            print()
            return
        else:
            print(repr(e))
    print()
    vnf = input("What VNF would you like to delete? ")
    response = requests.delete(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf,
                                verify=False, auth=HTTPBasicAuth(username, password),
                                headers={'content-type': 'application/vnd.yang.collection+json',
                                         'Accept': 'application/vnd.yang.data+json'})
    print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf)
    if response.status_code != 204:
        print("VNF deletion failed")
        print(response.status_code)
    else:
        print("VNF deletion successful")
        print(response.status_code)
    return

def dnac_reset():
    headers = {'content-type' : 'application/json'}
    payload = {'isForceDelete' : 'true'}
    response = requests.post("https://" + dnac + "/dna/system/api/v1/auth/token", verify=False,
                            auth=HTTPBasicAuth(dnac_username, dnac_password),
                            headers=headers)
    print("API Response Code: ", response.status_code)
    if response.status_code == 401:
        print("Authentication Failed to Device")
        sys.exit()
    else:
        token = response.json()["Token"]
    headers['x-auth-token'] = token
    response = requests.get("https://" + dnac + "/dna/intent/api/v1/network-device", headers=headers, verify=False)
    print()
    print("Getting list of Network Devices in inventory from DNA-C")
    print()
    data = response.json()
    for event in data["response"]:
        print("Hostname: ", event["hostname"], "with Device ID: ", event["id"])
    print()
    device_id = input("Enter the Device ID of the device you wish to delete: ")

    response = requests.delete("https://" + dnac + "/dna/intent/api/v1/network-device/" + device_id, params=payload, headers=headers, verify=False)
    if response.status_code != 202:
        print("Device deletion from inventory failed")
        print("API Response Code: ", response.status_code)
        print()
    else:
        print("Device deletion from inventory successful")
        print("API Response Code: ", response.status_code)
        print()
    return

#Menu Options
def print_options():
    print("Options: ")
    print(" '1' List system information")
    print(" '2' List running VNF's from NFVIS")
    print(" '3' Delete VNF from NFVIS")
    print(" '4' Delete Virtual Switch from NFVIS")
    print(" '5' Deploy VNF to NFVIS")
    print(" '6' Deploy Service Chained VNFs to NFVIS from DNA-C")
    print(" '7' Reset demo environment")
    print(" 'p' print options")
    print(" 'q' quit the program")


choice = "p"
while choice != "q":
    try:
        if choice == "1":
            getcreds()
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
            getcreds()
            #API call to list running VNFs, display info, return to options
            response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False, auth=HTTPBasicAuth(username, password),
                                    headers={'content-type':'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
            print("API Response Code: ", response.status_code)
            print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments")
            print()
            if response.status_code == 401:
                print("Authentication Failed to Device")
                sys.exit()
            else:
                print("Currently Deployed VNF's: ")
            try:
                data = response.json()
                for event in data["vmlc:deployments"]["deployment"]:
                    print(event["name"])
            except Exception as e:
                if response.status_code == 204:
                    print("There are no running VNF deployments on device.")
                else:
                    print(repr(e))
            print()
            print_options()
            choice = input("Option: ")
        elif choice == "3":
            getcreds()
            #API call to delete VNF on NFVIS device
            response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False, auth=HTTPBasicAuth(username, password),
                                    headers={'content-type':'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
            print("API Response Code: ", response.status_code)
            print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments")
            print()
            if response.status_code == 401:
                print("Authentication Failed to Device")
                sys.exit()
            else:
                print("Currently Deployed VNF's: ")
            try:
                data = response.json()
                for event in data["vmlc:deployments"]["deployment"]:
                    print(event["name"])
            except Exception as e:
                if response.status_code == 204:
                    print("There are no running VNF deployments on device.")
                    print()
                    sys.exit()
                else:
                    print(repr(e))
            print()
            vnf = input("What VNF would you like to delete? ")
            response = requests.delete(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf, verify=False, auth=HTTPBasicAuth(username, password),
                                    headers={'content-type': 'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
            print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf)
            print()
            if response.status_code != 204:
                print("API Response Code: ", response.status_code)
                print("VNF deletion failed")
            else:
                print("API Response Code: ", response.status_code)
                print("VNF deletion successful")
            print()
            print_options()
            choice = input("Option: ")
        elif choice == "4":
            getcreds()
            #API call to delete virtual switch on NFVIS device
            response = requests.get(url + "/api/config/networks?deep", verify=False, auth=HTTPBasicAuth(username, password),
                                    headers={'content-type':'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
            print("API Response Code: ", response.status_code)
            print()
            if response.status_code == 401:
                print("Authentication Failed to Device")
                sys.exit()
            else:
                print("Currently Deployed Virtual Switches on NFVIS: ")
            try:
                data = response.json()
                print(data)
                for event in data["network:networks"]["network"]:
                    print(event["name"])
            except Exception as e:
                print(repr(e))
            print()
            print("NOTE:  Do not delete the lan-net, wan-net, wan2-net or SRIOV vswitches, these are system generated!")
            vswitch = input("Which Virtual Switch would you like to delete? ")
            response = requests.delete(url + "/api/config/networks/network/" + vswitch, verify=False, auth=HTTPBasicAuth(username, password),
                                    headers={'content-type': 'application/vnd.yang.collection+json', 'Accept': 'application/vnd.yang.data+json'})
            print(url + "/api/config/bridges/bridge/" + vswitch)
            print()
            if response.status_code != 204:
                print("API Response Code: ", response.status_code)
                print("Virtual Switch deletion failed")
            else:
                print("API Response Code: ", response.status_code)
                print("Virtual Switch deletion successful")
            print()
            print_options()
            choice = input("Option: ")
        elif choice == "5":
            getcreds()
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
        elif choice == "6":
            #Deploy service chained VNFs from DNA-C
            print_options()
            choice = input("Option: ")
        elif choice == "7":
            #API call to reset demo environment, print demo environment reset
            vmanage = input("Enter the vManage IP address: ")
            print("Enter the Username and Password for vManage: ")
            vmanage_username = input("Username: ")
            vmanage_password = getpass.getpass()
            sdwan_reset()
            answer = input("Would you like to decommission another SDWAN router? (y or n)")
            if answer == ('y'):
                sdwan_reset()
            else:
                print("Great. Let's reset NFVIS.")
            nfvis_reset()
            print()
            answer = input("Would you like to decommission another NFVIS VNF? (y or n)")
            if answer == ('y'):
                nfvis_reset()
            else:
                print("Great. Let's reset Cisco DNA Center.")
            print()
            dnac = input("Enter the Cisco DNA Center IP address: ")
            print("Enter the Username and Password for Cisco DNA Center: ")
            dnac_username = input("Username: ")
            dnac_password = getpass.getpass()
            dnac_reset()
            answer = input("Would you like to delete another device from DNA-C inventory? (y or n)")
            if answer == ('y'):
                dnac_reset()
            else:
                print("Great. Demo Environment has been reset.")
                print()
            print_options()
            choice = input("Option: ")
        elif choice == "p":
            print_options()
            choice = input("Option: ")
        elif choice != "1" or "2" or "3" or "4" or "5" or "6" or "7" or "p" or "q":
            print("Wrong option was selected")
            print()
            sys.exit()
    except:
        print_options()
        choice = input("Option: ")
