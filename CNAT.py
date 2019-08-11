# !/usr/bin/env python3
"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

Filename: CNAT.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
         Wade Lehrschall (wlehrsch@cisco.com)
         Kris Swanson (kriswans@cisco.com)
Description:    This program will perform API calls to automate the deployment and deletion of NFVIS VNF's and virtual
                switches. The program also has a "demo reset" option which
                will decommission SDWAN routers in Cisco vManage, delete ENCS from Cisco DNA Center inventory, and
                delete VNF's and virtual switches from NFVIS.
"""

from PyNFVSDK import NFVIS_API_Calls as nfvis_calls
from PyNFVSDK import NFVIS_URNs as nfvis_urns
import xml.etree.ElementTree as ET
import json
import netmiko
from os import listdir
from termcolor import cprint
import sys
import requests
import getpass
import socket
import scp
from tabulate import tabulate
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def getcreds():
    # Collects NFVIS IP Address, Username, and Password
    nfvis = input("What is the IP address of the NFVIS system: ")
    url = "https://" + nfvis
    print("Enter your username and password. ")
    username = input("Username: ")
    password = getpass.getpass()
    return url, username, password


def response_parser(response_json):
    o = response_json
    print(60 * "#" + "\n\n" "Hierarchical Config:\n")
    try:
        for i in o.keys():
            print(i)
            j = o[i]
            try:
                for k in j.keys():
                    print("\t|\n\t-->%s" % k)
                    l = o[i][k]
                    for m in l:
                        if type(m) == type({}):
                            for n in m.keys():
                                try:
                                    if type(m[n]) == type({}):
                                        for a in (m[n]).keys():
                                            print(
                                                "\t\t\t\t|\n\t\t\t\t-->%s" % (m[n][a])
                                            )
                                except:
                                    pass
                                try:
                                    if type(m[n]) == type(""):
                                        print("\t\t|\n\t\t-->%s" % m[n])
                                except:
                                    pass
                                try:
                                    if type(m[n]) == type([]):
                                        for b in m[n]:
                                            for c in b.keys():
                                                print("\t\t\t|\n\t\t\t-->%s" % b[c])
                                except:
                                    pass
                        if type(l) == type({}):
                            print("\t\t|\n\t\t-->%s:%s" % (m, l[m]))
                        if type(m) == type([]):
                            for d in m:
                                print("\t\t|\n\t\t-->%s" % d)
            except:
                pass
    except:
        pass


def cli(args):
    if len(sys.argv) == 7:
        method, name_ip, username, password, s_file, d_file = (
            sys.argv[1],
            sys.argv[2],
            sys.argv[3],
            sys.argv[4],
            sys.argv[5],
            sys.argv[6],
        )
    elif len(sys.argv) == 5:
        method, key, name_ip, setting = (
            sys.argv[1],
            sys.argv[2],
            sys.argv[3],
            sys.argv[4],
        )
    elif len(sys.argv) == 2:
        method = sys.argv[1]
        if method is "h":
            print(
                "Non-Interactive mode supports the following arguments:\n"
                "\nArgument 1:\n"
                "g = get\n"
                "p = post\n"
                "d = delete\n"
                "\nArgument 2:\n"
                "\nGet Method:\n"
                "platform-detail, bridges, networks, deployments, flavors, images\n"
                "\nPost Method:\n"
                "bridges, networks, deployments\n"
                "\nDelete Method:\n"
                "bridges, networks, deployments\n"
                "\nArgument 3:\n"
                "Enter the IP address of the NFVIS system. Alternatively, substitute the \n"
                "key word 'bulk' instead of the IP address to run API calls on all devices\n"
                "in the creds.json file.\n"
                "\nArgument 4:\n"
                "When using the post method a .xml template is required for configuration\n"
                "of the bridge, network, or VNF. Examples of the templates can be found\n"
                "in the XML folder.\n"
                "\nWhen using the delete method argument 4 is the name of the bridge,"
                "\nnetwork, or VNF that is to be deleted."
                "\nTo retrieve information about the system use the get method.\n"
                "To delete an existing bridge, network, or VNF use the delete method.\n"
                "To deploy a new bridge, network, or VNF use the post method.\n"
                "\nWhen using method g, p, or d this program will check the given IP address\n"
                "against the creds.json file. If the IP address is present, then the credentials\n"
                "in the creds.json file will be used. If the key work 'bulk' is used instead of\n"
                "an IP address then the API call will be run on all devices in the creds.json file.\n"
                "\nExamples:\n"
                "Get Method - CNAT.py g networks 10.10.10.10\n"
                "Post Method - CNAT.py P deployments 10.10.10.10 ASAv_ENCS.xml\n"
                "Delete Method - CNAT.py d deployments 10.10.10.10 ASAv\n"
                "\nTo upload an image to NFVIS the 's' method can be used. This requires 6 arguments.\n"
                "Method, IP Address, username, password, source file, and destination file\n"
                ""
            )
            sys.exit()
        else:
            cprint("Invalid option entered. Use sys.argv 'h' for help.", "red")
            sys.exit()
    else:
        method, key, name_ip = (sys.argv[1], sys.argv[2], sys.argv[3])
    if "creds.json" not in listdir():
        username = input("Username: ")
        password = getpass.getpass()
        creds = {name_ip: {username: password}}
        with open("creds.json", "w") as f:
            json.dump(creds, f)
    with open("creds.json", "r") as f:
        creds = json.load(f)

    if name_ip not in creds.keys():
        if name_ip != "bulk":
            username = input("Username: ")
            password = getpass.getpass()
            creds.update({name_ip: {username: password}})
            with open("creds.json", "w") as f:
                json.dump(creds, f)
            ip_list = [name_ip]
        else:
            ip_list = list(creds.keys())
    else:
        ip_list = [name_ip]

    if method is "g":
        for i in ip_list:
            url = "https://%s" % i
            username, password = (list(creds[i].keys())[0], list(creds[i].values())[0])
            uri, header = nfvis_urns.get(key, url)
            code, response_json = nfvis_calls.get(username, password, uri, header)
            cprint(
                "API Response Code: %i\n\nRequest URI: %s\n\nJSON Reponse:\n\n%s\n\n"
                % (code, uri, response_json), "green"
            )
            response_parser(response_json)
    if method is "p":
        for i in ip_list:
            url = "https://%s" % i
            username, password = (list(creds[i].keys())[0], list(creds[i].values())[0])
            uri, header, post_data = nfvis_urns.post(key, url, format="xml")
            with open(setting) as f:
                contents = f.read()
            code, response = nfvis_calls.post(
                username, password, uri, header, xml_data=contents
            )
            cprint(
                "API Response Code: %i\n\nRequest URI: %s\n\nJSON Reponse:\n\n%s\n\n"
                % (code, uri, response), "green"
            )
            if code == 201:
                cprint("Deployment successful", "green")
            else:
                cprint("Deployment failed", "red")
    if method is "d":
        for i in ip_list:
            url = "https://%s" % i
            username, password = (list(creds[i].keys())[0], list(creds[i].values())[0])
            uri, header, = nfvis_urns.delete(
                key, url, vnf=setting, bridge=setting, network=setting
            )
            code, response = nfvis_calls.delete(username, password, uri, header)
            cprint(
                "API Response Code: %i\n\nRequest URI: %s\n\nJSON Reponse:\n\n%s\n\n"
                % (code, uri, response), "green"
            )
            if code == 204:
                cprint("Deletion successful", "green")
            else:
                cprint("Deletion failed"), "red"
    if method is "s":
        for i in ip_list:
            nfvis = key
            s_file = name_ip
            d_file = setting
            username, password = (list(creds[i].keys())[0], list(creds[i].values())[0])
            scp_file(nfvis, username, password, s_file, d_file)

def nfvis_reset():
    # Delete running VNFs' from NFVIS
    url, username, password = getcreds()
    uri, header = nfvis_urns.get("deployments", url)
    code, response_json = nfvis_calls.get(username, password, uri, header)
    print("API Response Code: %i :\n%s" % (code, uri))
    if code == 401:
        cprint("\nAuthentication Failed to Device", "red")
    else:
        print("\nCurrently Deployed VNF's...\n")
    try:
        print(
            tabulate(
                [i for i in response_json["vmlc:deployments"]["deployment"]],
                tablefmt="fancy_grid",
            )
            + "\n"
        )
    except Exception as e:
        if code == 204:
            print("There are no running VNF deployments on device.\n")
            return
        else:
            print(repr(e))
    print()
    vnf = input("\nWhat VNF would you like to delete? ")
    uri, header = nfvis_urns.delete("deployments", url, vnf=vnf)
    code, response = nfvis_calls.delete(username, password, uri, header)
    print("\n%s \nAPI Status Code: %i\n" % (uri, code))
    if code != 204:
        cprint("VNF deletion failed", "red")
    else:
        cprint("VNF deletion successful", "green")


def deploy_bridge(url, username, password):
    tree = ET.parse("XML/bridge.xml")
    root = tree.getroot()
    for child in root:
        child.text = input("Enter the name of the bridge to be deployed: ")
    tree.write("XML/bridge.xml")
    contents = open("XML/bridge.xml").read()
    print(contents)
    uri, header, post_data = nfvis_urns.post("bridges", url, format="xml")
    code, response = nfvis_calls.post(
        username, password, uri, header, xml_data=contents
    )
    print("\n%s \nAPI Status Code: %i\n" % (uri, code))

    if code != 201:
        cprint("Bridge deployment failed\n", "red")
    else:
        cprint("Bridge deployment successful\n", "green")


def deploy_vnetwork(url, username, password):
    tree = ET.parse("XML/network.xml")
    root = tree.getroot()
    for child in root:
        if child.tag == str("name"):
            child.text = input("Enter the name of the network to be deployed: ")
            tree.write("XML/network.xml")
        if child.tag == str("bridge"):
            child.text = input(
                "Enter the name of the bridge to be associated with the network.\n"
                "This should be the bridge that was previously created: "
            )
            tree.write("XML/network.xml")
            contents = open("XML/network.xml").read()
            print(contents)
    uri, header, post_data = nfvis_urns.post("networks", url, format="xml")
    code, response = nfvis_calls.post(
        username, password, uri, header, xml_data=contents
    )
    print("\n%s \nAPI Status Code: %i\n" % (uri, code))
    if code != 201:
        cprint("Network deployment failed\n", "red")
    else:
        cprint("Network deployment successful\n", "green")


def deploy_vnf(url, username, password):
    tree = ET.parse("XML/vnf.xml")
    root = tree.getroot()
    for child in root.findall("./name"):
        child.text = input("Enter a name for the deployment: ")
        tree.write("XML/vnf.xml")

    for child in root.findall("./vm_group/name"):
        child.text = input("Enter a name for the VNF: ")
        tree.write("XML/vnf.xml")

    uri, header = nfvis_urns.get("images", url)
    code, response_json = nfvis_calls.get(username, password, uri, header)
    print("API Response Code: %i :\n%s" % (code, uri))
    if code == 401:
        cprint("\nAuthentication Failed to Device", "red")
    else:
        print()
    try:
        for i in response_json["vmlc:images"]["image"]:
            print(i["name"] + "\n")
    except Exception as e:
        if code == 204:
            print("There are no images on this device.\n")
            return
        else:
            print(repr(e))

    for child in root.iter("image"):
        child.text = input(
            "Enter the name of the image to be deployed.\nImage must exist on the system: "
        )
        tree.write("XML/vnf.xml")

    uri, header = nfvis_urns.get("flavors", url)
    code, response_json = nfvis_calls.get(username, password, uri, header)
    print("API Response Code: %i :\n%s" % (code, uri))
    if code == 401:
        cprint("\nAuthentication Failed to Device", "red")
    else:
        print()
    try:
        for i in response_json["vmlc:flavors"]["flavor"]:
            print(i["name"] + "\n")
    except Exception as e:
        if code == 204:
            print("There are no flavors on this device.\n")
            return
        else:
            print(repr(e))

    for child in root.iter("flavor"):
        child.text = input("Enter the VNF flavor\nFlavor must exist on the system: ")
        tree.write("XML/vnf.xml")

    uri, header = nfvis_urns.get("networks", url)
    code, response_json = nfvis_calls.get(username, password, uri, header)
    print("API Response Code: %i :\n%s" % (code, uri))

    if code == 401:
        cprint("Authentication Failed to Device", "red")
        sys.exit()
    else:
        print("Currently Deployed Virtual Switches on NFVIS: \n")
    try:
        [print(i["name"] + "\n") for i in response_json["network:networks"]["network"]]
    except Exception as e:
        print(repr(e))

    for child in root.findall("./vm_group/interfaces/interface/network[@id='1']"):
        if child.tag == str("network"):
            child.text = input("Enter the name of the network to connect to nicid 1: ")
            tree.write("XML/vnf.xml")
        else:
            continue

    for child in root.findall("./vm_group/interfaces/interface/network[@id='2']"):
        if child.tag == str("network"):
            child.text = input("Enter the name of the network to connect to nicid 2: ")
            tree.write("XML/vnf.xml")
        else:
            continue

    for child in root.findall("./vm_group/interfaces/interface/network[@id='3']"):
        if child.tag == str("network"):
            child.text = input("Enter the name of the network to connect to nicid 3: ")
            tree.write("XML/vnf.xml")
        else:
            continue

    for child in root.findall("./vm_group/interfaces/interface/port_forwarding/port/"):
        if child.tag == str("vnf_port"):
            child.text = input("Enter the VNF port to forward. Usually port 22: ")
            tree.write("XML/vnf.xml")

    for child in root.findall(
        "./vm_group/interfaces/interface/port_forwarding/port/external_port_range/"
    ):
        if child.tag == str("start"):
            child.text = input(
                "Enter the first port in the range for external port forwarding: "
            )
            tree.write("XML/vnf.xml")
        elif child.tag == str("end"):
            child.text = input(
                "Enter the last port in the range for external port forwarding: "
            )
            tree.write("XML/vnf.xml")
        else:
            continue

    contents = open("XML/vnf.xml").read()
    print(contents, "\n")

    uri, header, post_data = nfvis_urns.post("deployments", url, format="xml")
    code, response = nfvis_calls.post(
        username, password, uri, header, xml_data=contents
    )
    print("\n%s \nAPI Status Code: %i\n" % (uri, code))
    if code != 201:
        cprint("VNF deployment failed\n", "red")
    else:
        cprint("VNF deployment successful\n", "green")


def scp_file(nfvis, username, password, s_file, d_file):
    try:
        conn = netmiko.ConnectHandler(
            host=nfvis,
            port=22222,
            device_type="linux",
            username=username,
            password=password,
            timeout=10
        )
        scp_conn = netmiko.SCPConn(conn)
        print("#" * 20)
        cprint("Beginning SCP file transfer...\nPlease wait...", "green")
        scp_conn.scp_transfer_file(s_file, d_file)
        print("#" * 20)
        cprint("SCP file transfer complete.\n", "green")
        conn.disconnect()
        image = s_file.split("/")
        name = image[-1]
        payload = "<image><name>" + name + "</name>" \
                  "<src>" + d_file + "</src></image>"
        print(payload)
        url = "https://" + nfvis
        uri, header, post_data = nfvis_urns.post("images", url, format="xml")
        code, response = nfvis_calls.post(
            username, password, uri, header, xml_data=payload
        )
        print("\n%s \nAPI Status Code: %i\n" % (uri, code))

        if code != 201:
            cprint("Bridge deployment failed\n", "red")
        else:
            cprint("Bridge deployment successful\n", "green")

    except netmiko.NetMikoTimeoutException:
        cprint("\nFailed: SSH session timed out. Check network connectivity and try again.\n", "red")
    except netmiko.NetMikoAuthenticationException:
        cprint("\nFailed: Authentication failed.\n", "red")
    except FileNotFoundError:
        cprint("Invalid source file name entered. Please try again.", "red")
    except scp.SCPException:
        cprint("Invalid destination file name entered. Please try again.", "red")


def portCheck(nfvis, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((nfvis, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def print_options():
    # Menu Options
    print("#################################")
    print("###Cisco NFVIS Automation Tool###")
    print("################################# \n")
    print("Select an option from the menu below. \n")
    print(" Options: \n")
    print(" '1' List NFVIS system information")
    print(" '2' List running VNF's from NFVIS")
    print(" '3' Delete Virtual Switch from NFVIS")
    print(" '4' Delete VNF from NFVIS")
    print(" '5' Deploy Virtual Switch to NFVIS from file")
    print(" '6' Deploy VNF to NFVIS from file")
    print(" '7' Deploy Service Chained VNFs to NFVIS")
    print(" '8' Upload VNF image to NFVIS")
    print(" 'p' print options")
    print(" 'q' quit the program\n")


def main():
    """

    Program Entry Point
    """

    choice = "p"
    while choice != "q":
        if choice == "1":
            # API call to retrieve system info, then displays it, return to options
            url, username, password = getcreds()
            uri, header = nfvis_urns.get("platform-details", url)
            code, response_json = nfvis_calls.get(username, password, uri, header)
            print("API Response Code: %i\n%s" % (code, uri))
            if code == 401:
                cprint("Authentication Failed to Device \n", "red")
            elif code == 400:
                cprint("Connection timed out. Check network connection.\n", "red")
            else:
                print("Platform Details: \n")
                try:
                    print(
                        tabulate(
                            [
                                i
                                for i in response_json["platform_info:platform-detail"][
                                    "hardware_info"
                                ].items()
                            ],
                            tablefmt="fancy_grid",
                        )
                    )
                except Exception as e:
                    print(repr(e))
            print_options()
            choice = input("Option: ")

        elif choice == "2":
            # API call to list running VNFs, display info, return to options
            url, username, password = getcreds()
            uri, header = nfvis_urns.get("deployments", url)
            code, response_json = nfvis_calls.get(username, password, uri, header)
            print("API Response Code: %i \n%s" % (code, uri))
            if code == 401:
                cprint("Authentication Failed to Device \n", "red")
            elif code == 400:
                cprint("Connection timed out. Check network connection.\n", "red")
            else:
                print("\nCurrently Deployed VNF's: \n")
                try:
                    print(
                        tabulate(
                            [i for i in response_json["vmlc:deployments"]["deployment"]],
                            tablefmt="fancy_grid",
                        )
                        + "\n"
                    )
                except Exception as e:
                    if code == 204:
                        print("There are no running VNF deployments on device. \n")
                    else:
                        print(repr(e))
            print_options()
            choice = input("Option: ")

        elif choice == "3":
            # API call to display running bridges/networks. Then API call to delete bridge/network of choice

            url, username, password = getcreds()

            uri, header = nfvis_urns.get("networks", url)
            code, response_json = nfvis_calls.get(username, password, uri, header)
            print("API Response Code: %i \n%s" % (code, uri))

            if code == 401:
                cprint("Authentication Failed to Device", "red")
            elif code == 400:
                cprint("Connection timed out. Check network connection.\n", "red")
            else:
                print("Currently Deployed Virtual Switches on NFVIS: \n")
                try:
                    print(
                        tabulate(
                            [i for i in response_json["network:networks"]["network"]],
                            tablefmt="fancy_grid",
                        )
                        + "\n"
                    )
                except Exception as e:
                    print(repr(e))
                print()
                cprint(
                    "NOTE:  Do not delete the lan-net, wan-net, wan2-net or SRIOV vswitches, these are system generated! \n", "red"
                )
                vswitch = input("Which Virtual Switch would you like to delete? ")
                uri, header = nfvis_urns.delete("networks", url, network=vswitch)
                code, response = nfvis_calls.delete(username, password, uri, header)
                print("API Response Code: %i \n%s" % (code, uri))

                if code != 204:
                    cprint("Virtual Switch deletion failed \n", "red")
                else:
                    cprint("Virtual Switch deletion successful \n", "green")

                # API call to get running bridges on NFVIS device

                uri, header = nfvis_urns.get("bridges", url)
                code, response_json = nfvis_calls.get(username, password, uri, header)
                print("API Response Code: %i \n%s" % (code, uri))

                if code == 401:
                    cprint("Authentication Failed to Device", "red")
                    sys.exit()
                else:
                    print("Currently Deployed Virtual Bridges on NFVIS: \n")
                try:
                    [
                        print(i["name"] + "\n")
                        for i in response_json["network:bridges"]["bridge"]
                    ]
                except Exception as e:
                    print(repr(e))
                print()
                cprint(
                    "NOTE:  Do not delete the lan-br, wan-br, wan2-br or SRIOV vswitches, these are system generated! \n", "red"
                )
                bridge = input("Which Virtual Bridge would you like to delete? ")

                uri, header = nfvis_urns.delete("bridges", url, bridge=bridge)
                code, response = nfvis_calls.delete(username, password, uri, header)
                print("API Response Code: %i \n%s" % (code, uri))

                if code != 204:
                    cprint("Virtual Bridge deletion failed \n", "red")
                else:
                    cprint("Virtual Bridge deletion successful \n", "green")
            print_options()
            choice = input("Option: ")

        elif choice == "4":
            # API call to display currently running VNF's then enter VNF to delete and API call to delete

            nfvis_reset()
            print_options()
            choice = input("Option: ")

        elif choice == "5":
            # API call to deploy bridges/networks to NFVIS

            url, username, password = getcreds()
            deploy_bridge(url, username, password)
            deploy_vnetwork(url, username, password)
            print_options()
            choice = input("Option: ")

        elif choice == "6":
            # API call to deploy VNF to NFVIS

            url, username, password = getcreds()
            deploy_vnf(url, username, password)
            print_options()
            choice = input("Option: ")

        elif choice == "7":
            # API calls to deploy virtual networking and VNF's to NFVIS
            url, username, password = getcreds()

            deploy_bridge(url, username, password)
            answer = input("Would you like to deploy another bridge? (y or n) ")
            while answer == "y":
                deploy_bridge(url, username, password)
                answer = input("Would you like to deploy another bridge? (y or n) ")
            else:
                print("Bridge deployment complete. Let's deploy the virtual network. ")
            deploy_vnetwork(url, username, password)
            answer = input(
                "Would you like to deploy another virtual network? (y or n) "
            )
            while answer == ("y"):
                deploy_vnetwork(url, username, password)
                answer = input(
                    "Would you like to deploy another virtual network? (y or n) "
                )
            else:
                print(
                    "Virtual network deployment complete. Let's deploy the virtual network functions. \n"
                )
            deploy_vnf(url, username, password)
            answer = input(
                "Would you like to deploy another virtual network function? (y or n) "
            )
            while answer == ("y"):
                deploy_vnf(url, username, password)
                answer = input(
                    "Would you like to deploy another virtual network function? (y or n) "
                )
            else:
                print(
                    "Virtual network function deployment complete.\n Service chain deployment complete. \n"
                )
            print_options()
            choice = input("Option: ")

        elif choice == "8":
            # SCP image to NFVIS system
            url, username, password = getcreds()
            nfvis = url.strip("https://")

            if portCheck(nfvis, 22222) is True:

                s_file = input(
                    "Example: Images/TinyLinux.tar.gz\nEnter the image name along with the full path of the image: "
                )
                d_file = input(
                    "\nExample: /data/intdatastore/uploads/TinyLinuxNew.tar.gz\nEnter the destination file path and name: "
                )
                scp_file(nfvis, username, password, s_file, d_file)
                print_options()
                choice = input("Option: ")
            else:
                cprint("SCP is not enabled on the system.\n", "red")
                answer = input("Would you like to enable SCP now? (y or n)")
                if answer == "y":
                    acl = input("Enter the permitted IP range for SCP access to the device: (0.0.0.0/0) ")
                    config = ["system settings ip-receive-acl " + acl + " service scpd priority 1 action accept", "commit"]
                    cprint("Enabling SCP on the system", "green")
                    cprint("Sending command, " + config[0], "green")
                    try:
                        conn = netmiko.ConnectHandler(ip=nfvis, device_type="cisco_ios", username=username,
                                                      password=password)
                        conn.send_config_set(config)
                        cprint("SCP enabled for " + acl, "green")
                        s_file = input(
                            "Example: Images/TinyLinux.tar.gz\nEnter the image name along with the full path of the image: "
                        )
                        d_file = input(
                            "\nExample: /data/intdatastore/uploads/TinyLinuxNew.tar.gz\nEnter the destination file path and name: "
                        )
                        scp_file(nfvis, username, password, s_file, d_file)
                    except netmiko.NetMikoTimeoutException:
                        cprint("\nFailed: SSH session timed out. Check network connectivity and try again.\n", "red")
                    except netmiko.NetMikoAuthenticationException:
                        cprint("\nFailed: Authentication failed.\n", "red")
                    except FileNotFoundError:
                        cprint("Invalid source file name entered. Please try again.", "red")
                    except scp.SCPException:
                        cprint("Invalid destination file name entered. Please try again.", "red")
                    print_options()
                    choice = input("Option: ")

                else:
                    print_options()
                    choice = input("Option: ")

        elif choice == "p":
            print_options()
            choice = input("Option: ")

        elif (
            choice != "1" or "2" or "3" or "4" or "5" or "6" or "7" or "8" or "p" or "q"
        ):
            cprint("Invalid option was selected. Please choose a valid option. \n", "red")
            print_options()
            choice = input("Option: ")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    else:
        cli(sys.argv)
