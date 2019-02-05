#!/usr/bin/python
#-*-coding:utf-8-*-
'''
Filename: nfvis.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
         Wade Lehrschall (wlehrsch@cisco.com)
Description:    This program will perform API calls to automate the deployment and deletion of NFVIS VNF's and virtual
                switches. The program is currently interactive only. The program also has a "demo reset" option which
                will decommission SDWAN routers in Cisco vManage, delete ENCS from Cisco DNA Center inventory, and
                delete VNF's and virtual switches from NFVIS.
'''


import sys
import requests
import json
import getpass
from tabulate import tabulate
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def getcreds():
    # Collects NFVIS IP Address, Username, and Password
    nfvis = input("What is the IP address of the NFVIS system: ")
    url = "https://" + nfvis
    print("Enter your username and password. ")
    username = input("Username: ")
    password = getpass.getpass()
    return nfvis, url, username, password

def sdwan_reset():
    # Collect vManage IP Address, Username, and Password and decommission SDWAN Routers
    vmanage = input("Enter the vManage IP address: \n")
    print("Enter the Username and Password for vManage: \n")
    vmanage_username = input("Username: ")
    vmanage_password = getpass.getpass()
    response = requests.get("https://" + vmanage + "/dataservice/system/device/vedges", verify=False,
                            auth=HTTPBasicAuth(vmanage_username, vmanage_password),
                            headers={"content-type": "application/json", "Accept": "application/json"})
    print("API Response Code: ", response.status_code)
    print("https://" + vmanage + "/dataservice/system/device/vedges")
    if response.status_code == 401:
        print("Authentication Failed to Device")
        sys.exit()
    else:
        print("\nGetting list of SDWAN UUID's from vManage: \n")
        data = response.json()
        table = list()
        headers = ["SDWAN UUID"]
        for event in data["data"]:
            tr = [event['uuid']]
            table.append(tr)
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
        print()
    uuid = input("Enter the UUID of the SDWAN router you wish to decommission: ")
    print("Deccommissioning SDWAN Router...")
    response = requests.put("https://" + vmanage + "/dataservice/system/device/decommission/" + uuid, verify=False,
                            auth=HTTPBasicAuth(vmanage_username, vmanage_password),
                            headers={"content-type": "application/json", "Accept": "application/json"})
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
    # Delete running VNFs' from NFVIS
    nfvis, url, username, password = getcreds()
    print("Currently Deployed VNF's...")
    response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False,
                            auth=HTTPBasicAuth(username, password),
                            headers={"content-type": "application/vnd.yang.collection+json",
                                     "Accept": "application/vnd.yang.data+json"})
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
                                headers={"content-type": "application/vnd.yang.collection+json",
                                         "Accept": "application/vnd.yang.data+json"})
    print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf)
    if response.status_code != 204:
        print("VNF deletion failed")
        print(response.status_code)
    else:
        print("VNF deletion successful")
        print(response.status_code)
    return

def dnac_reset():
    # Gather DNAC IP Address, Username, Password, and delete ENCS from inventory
    dnac = input("Enter the Cisco DNA Center IP address: \n")
    print("Enter the Username and Password for Cisco DNA Center: \n")
    dnac_username = input("Username: ")
    dnac_password = getpass.getpass()
    headers = {"content-type" : "application/json"}
    payload = {"isForceDelete" : "true"}
    response = requests.post("https://" + dnac + "/dna/system/api/v1/auth/token", verify=False,
                            auth=HTTPBasicAuth(dnac_username, dnac_password),
                            headers=headers)
    print("API Response Code: ", response.status_code)
    if response.status_code == 401:
        print("Authentication Failed to Device")
        sys.exit()
    else:
        token = response.json()["Token"]
    headers["x-auth-token"] = token
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

# Menu Options
def print_options():
    print("Select an option from the menu below. \n")
    print(" Options: \n")
    print(" '1' List NFVIS system information")
    print(" '2' List running VNF's from NFVIS")
    print(" '3' Delete VNF from NFVIS")
    print(" '4' Delete Virtual Switch from NFVIS")
    print(" '5' Deploy Virtual Switch to NFVIS")
    print(" '6' Deploy VNF to NFVIS")
    print(" '7' Deploy Service Chained VNFs to NFVIS from Cisco DNA Center")
    print(" '8' Reset demo environment")
    print(" 'p' print options")
    print(" 'q' quit the program")

def main():

    '''

    Program Entry Point
    '''

    print("#################################")
    print("####Cisco DNA Automation Tool####")
    print("################################# \n")

    choice = "p"
    while choice != "q":
        try:
            if choice == "1":
                nfvis, url, username, password = getcreds()
                # API call to retrieve system info, then displays it, return to options
                response = requests.get(url + "/api/operational/platform-detail", verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type":"application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print(response.status_code, "\n")
                print(url + "/api/operational/platform-detail \n")
                if response.status_code == 401:
                    print("Authentication Failed to Device \n")
                    sys.exit()
                else:
                    print("Platform Details: \n")
                try:
                    jsl = json.loads(response.content)
                    print(tabulate([i for i in jsl['platform_info:platform-detail']['hardware_info'].items()],tablefmt="fancy_grid"))
                except Exception as e:
                    print(repr(e))
                print_options()
                choice = input("Option: ")
            elif choice == "2":
                nfvis, url, username, password = getcreds()
                #API call to list running VNFs, display info, return to options
                response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type":"application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print("API Response Code: ", response.status_code, "\n")
                print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments\n")
                if response.status_code == 401:
                    print("Authentication Failed to Device \n")
                    sys.exit()
                else:
                    print("Currently Deployed VNF's: \n")
                try:
                    data = response.json()
                    for event in data["vmlc:deployments"]["deployment"]:
                        print(event["name"])
                except Exception as e:
                    if response.status_code == 204:
                        print("There are no running VNF deployments on device. \n")
                    else:
                        print(repr(e))
                print_options()
                choice = input("Option: ")
            elif choice == "3":
                nfvis, url, username, password = getcreds()
                # API call to delete VNF on NFVIS device
                response = requests.get(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments", verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type":"application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print("API Response Code: ", response.status_code, "\n")
                print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments\n")
                if response.status_code == 401:
                    print("Authentication Failed to Device \n")
                    sys.exit()
                else:
                    print("Currently Deployed VNF's: \n")
                try:
                    data = response.json()
                    for event in data["vmlc:deployments"]["deployment"]:
                        print(event["name"])
                except Exception as e:
                    if response.status_code == 204:
                        print("There are no running VNF deployments on device.\n")
                        sys.exit()
                    else:
                        print(repr(e))
                vnf = input("What VNF would you like to delete? ")
                response = requests.delete(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf, verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type": "application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/" + vnf, "\n")
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code != 204:
                    print("VNF deletion failed\n")
                else:
                    print("VNF deletion successful\n")
                print_options()
                choice = input("Option: ")
            elif choice == "4":
                nfvis, url, username, password = getcreds()
                # API call to get running virtual switch on NFVIS device
                response = requests.get(url + "/api/config/networks?deep", verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type":"application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code == 401:
                    print("Authentication Failed to Device")
                    sys.exit()
                else:
                    print("Currently Deployed Virtual Switches on NFVIS: \n")
                try:
                    data = response.json()
                    for event in data["network:networks"]["network"]:
                        print(event["name"])
                except Exception as e:
                    print(repr(e))
                print()
                print("NOTE:  Do not delete the lan-net, wan-net, wan2-net or SRIOV vswitches, these are system generated! \n")
                vswitch = input("Which Virtual Switch would you like to delete? ")
                # API Call to delete virtual network
                response = requests.delete(url + "/api/config/networks/network/" + vswitch, verify=False, auth=HTTPBasicAuth(username, password),
                                        headers={"content-type": "application/vnd.yang.collection+json", "Accept": "application/vnd.yang.data+json"})
                print(url + "/api/config/bridges/bridge/" + vswitch, "\n")
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code != 204:
                    print("Virtual Switch deletion failed \n")
                else:
                    print("Virtual Switch deletion successful \n")
                # API call to get running bridges on NFVIS device
                response = requests.get(url + "/api/config/bridges?deep", verify=False,
                                        auth=HTTPBasicAuth(username, password),
                                        headers={"content-type": "application/vnd.yang.collection+json",
                                                    "Accept": "application/vnd.yang.data+json"})
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code == 401:
                    print("Authentication Failed to Device")
                    sys.exit()
                else:
                    print("Currently Deployed Virtual Bridges on NFVIS: \n")
                try:
                    data = response.json()
                    for event in data["network:bridges"]["bridge"]:
                        print(event["name"])
                except Exception as e:
                    print(repr(e))
                print()
                print("NOTE:  Do not delete the lan-br, wan-br, wan2-br or SRIOV vswitches, these are system generated! \n")
                bridge = input("Which Virtual Bridge would you like to delete? ")
                response = requests.delete(url + "/api/config/bridges/bridge/" + bridge, verify=False,
                                            auth=HTTPBasicAuth(username, password),
                                            headers={"content-type": "application/vnd.yang.collection+json",
                                                    "Accept": "application/vnd.yang.data+json"})
                print(url + "/api/config/bridges/bridge/" + bridge, "\n")
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code != 204:
                    print("Virtual Bridge deletion failed \n")
                else:
                    print("Virtual Bridge deletion successful \n")
                print_options()
                choice = input("Option: ")
            elif choice == "5":
                nfvis, url, username, password = getcreds()
                # API call to deploy bridge and network on NFVIS device
                bridgedata = input("What is the name of data file for the bridge to be deployed?\n")
                contents = open(bridgedata).read()
                print(contents)
                response = requests.post(url + "/api/config/bridges",
                                         verify=False, auth=HTTPBasicAuth(username, password),
                                         headers={"content-type": "application/vnd.yang.data+xml",
                                                  "Accept": "application/vnd.yang.data+xml"}, data=contents)
                print(url + "/api/config/bridges/\n")

                print("API Response Code: ", response.status_code, "\n")
                if response.status_code != 201:
                    print("Bridge deployment failed\n")
                else:
                    print("Bridge deployment successful\n")

                networkdata = input("What is the name of data file for the network to be deployed?\n")
                contents = open(networkdata).read()
                print(contents)
                response = requests.post(url + "/api/config/networks", verify=False,
                                         auth=HTTPBasicAuth(username, password),
                                         headers={"content-type": "application/vnd.yang.data+xml", "Accept": "application/vnd.yang.data+xml"},
                                         data=contents)
                print(url + "/api/config/networks/\n")
                print("API Response Code: ", response.status_code, "\n")
                if response.status_code != 201:
                    print("Network deployment failed\n")
                else:
                    print("Network deployment successful\n")

                print_options()
                choice = input("Option: ")
            elif choice == "6":
                nfvis, url, username, password = getcreds()
                # API call to deploy VNF on NFVIS device
                vnfdata = input("What is the name of data file for the VNF to be deployed?\n")
                contents = open(vnfdata).read()
                print(contents)
                response = requests.post(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments",
                                           verify=False, auth=HTTPBasicAuth(username, password),
                                           headers={"content-type": "application/vnd.yang.data+xml",
                                                    "Accept": "application/vnd.yang.data+xml"}, data=contents)
                print(url + "/api/config/vm_lifecycle/tenants/tenant/admin/deployments/\n")
                print("API Response Code:", response.status_code, "\n")
                if response.status_code != 201:
                    print("VNF deployment failed\n")
                else:
                    print("VNF deployment successful\n")
                print_options()
                choice = input("Option: ")
            elif choice == "7":
                # Deploy service chained VNFs
                print_options()
                choice = input("Option: ")
            elif choice == "8":
                # API call to reset demo environment, print demo environment reset
                sdwan_reset()
                answer = input("Would you like to decommission another SDWAN router? (y or n) \n")
                if answer == ('y'):
                    sdwan_reset()
                else:
                    print("Great. Let's reset NFVIS. \n")
                nfvis_reset()
                answer = input("Would you like to decommission another NFVIS VNF? (y or n) \n")
                if answer == ('y'):
                    nfvis_reset()
                else:
                    print("Great. Let's reset Cisco DNA Center. \n")
                dnac_reset()
                answer = input("Would you like to delete another device from DNA-C inventory? (y or n) \n")
                if answer == ('y'):
                    dnac_reset()
                else:
                    print("Great. Demo Environment has been reset. \n")
                print_options()
                choice = input("Option: ")
            elif choice == "p":
                print_options()
                choice = input("Option: ")
            elif choice != "1" or "2" or "3" or "4" or "5" or "6" or "7" or "p" or "q":
                print("Wrong option was selected \n")
                sys.exit()
        except:
            print_options()
            choice = input("Option: ")

if __name__ == '__main__':
    main()
