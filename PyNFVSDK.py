#!/usr/bin/python
# -*-coding:utf-8-*-
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

Filename: NFVIS_API_SDK.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
         Wade Lehrschall (wlehrsch@cisco.com)
         Kris Swanson (kriswans@cisco.com)
Description:    This program will provide reusable calls when interacting with NFVIS, DNA-C, and vManage APIs.
"""

import requests
import json
from termcolor import cprint
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class NFVIS_API_Calls:
    """NFVIS class to define REST API URLs and Headers with
    get, post and delete methods.
    username=string,
    password=string
    url=string :formatted from NFVIS_URNs class
    header=dictionary :from NFVIS_URNs class

    """

    def __init__(self, username=None, password=None, url=None, data=None):
        self.username = username
        self.password = password
        self.url = url
        self.data = data

    def get(username, password, uri, header):
        """gets the specified uri and returns: response code, json formatted response. """
        try:
            response = requests.get(
                uri,
                verify=False,
                auth=HTTPBasicAuth(username, password),
                headers=header,
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            cprint(e, "red")
            code = 400
            response = {}
            return code, response

        if response.status_code == 400:
            code = response.status_code
            response = {}
        elif response.status_code == 401:
            code = response.status_code
            response = {}
        elif response.status_code != 204:
            code = response.status_code
            response = response.json()
        else:
            code = response.status_code
            response = json.dumps({})
        return code, response

    def delete(username, password, uri, header):
        """gets the specified uri and returns: response code, response. """
        response = requests.delete(
            uri,
            verify=False,
            auth=HTTPBasicAuth(username, password),
            headers=header,
            timeout=10,
        )
        return response.status_code, response

    def post(username, password, uri, header, xml_data="", json_data=""):
        """gets the specified uri and returns: response code, json formatted response. """
        if xml_data != "":
            data = xml_data
        else:
            data = json_data
        response = requests.post(
            uri,
            verify=False,
            auth=HTTPBasicAuth(username, password),
            headers=header,
            data=data,
            timeout=10,
        )
        return response.status_code, response


class NFVIS_URNs:
    def __init__(self, url):
        self.url = url

    def get(self, url, format="json"):
        """returns appropriate REST GET uri and header given shorthand key"""
        rest_get_uri = {
            "deployments": "%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments"
            % url,
            "platform-details": "%s/api/operational/platform-detail" % url,
            "networks": "%s/api/config/networks?deep" % url,
            "bridges": "%s/api/config/bridges?deep" % url,
            "images": "%s/api/config/vm_lifecycle/images" % url,
            "flavors": "%s/api/config/vm_lifecycle/flavors" % url,
        }
        rest_get_header = {
            "json": {
                "content-type": "application/vnd.yang.collection+json",
                "Accept": "application/vnd.yang.data+json",
            },
            "xml": None,
        }
        return rest_get_uri[self], rest_get_header[format]

    def post(self, url, format="json", vnf=None, bridge=None, network=None):
        """returns appropriate REST POST uri and header given shorthand key and object to be posted
        url argument needs to be in format: https://<ip or name of nfvis system>"""
        rest_post_uri = {
            "bridges": "%s/api/config/bridges" % url,
            "networks": "%s/api/config/networks" % url,
            "deployments": "%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments"
            % url,
        }
        rest_post_header = {
            "json": {
                "content-type": "application/vnd.yang.data+json",
                "accept": "application/vnd.yang.data+json",
            },
            "xml": {
                "content-type": "application/vnd.yang.data+xml",
                "Accept": "application/vnd.yang.data+xml",
            },
        }
        rest_post_json_data = {
            "bridges": '{"bridge": [{"name": "%s"}]}' % bridge,
            "networks": '{"network":[{"name":"%s","bridge":"%s"}]}' % (network, bridge),
            "deployments": None,
        }
        return rest_post_uri[self], rest_post_header[format], rest_post_json_data[self]

    def delete(self, url, format="json", vnf="", bridge="", network=""):
        """returns appropriate REST DELETE uri and header given shorthand key and object to be deleted"""
        rest_delete_uri = {
            "deployments": "%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/%s"
            % (url, vnf),
            "networks": "%s/api/config/networks/network/%s" % (url, network),
            "bridges": "%s/api/config/bridges/bridge/%s" % (url, bridge),
        }
        rest_delete_header = {
            "json": {
                "content-type": "application/vnd.yang.collection+json",
                "Accept": "application/vnd.yang.data+json",
            },
            "xml": None,
        }
        return rest_delete_uri[self], rest_delete_header[format]


class SDWAN_API_Calls:
    def __init__(self, username=None, password=None, url=None, data=None):
        self.username = username
        self.password = password
        self.url = url
        self.data = data

    def get(username, password, uri, header):
        """gets the specified uri and returns: response code, json formatted response. """
        response = requests.get(
            uri, verify=False, auth=HTTPBasicAuth(username, password), headers=header
        )
        if response.status_code != 204:
            code = response.status_code
            response = response.json()
        else:
            response = json.dumps("None")
            code = response.status_code
        return code, response

    def put(username, password, uri, header):
        """gets the specified uri and returns: response code, response. """
        response = requests.put(
            uri, verify=False, auth=HTTPBasicAuth(username, password), headers=header
        )
        return response.status_code, response


class SDWAN_URNs:
    def __init__(self, url):
        self.url = url

    def get(self, url):
        """returns appropriate REST GET uri and header given shorthand key"""
        rest_get_uri = {"vedges": "%s/dataservice/system/device/vedges" % url}
        rest_get_json_header = {
            "content-type": "application/json",
            "Accept": "application/json",
        }
        return rest_get_uri[self], rest_get_json_header

    def put(self, url, data=""):
        """returns appropriate REST PUT uri and header given shorthand key and object to be posted"""
        rest_put_uri = {
            "decommission": "%s/dataservice/system/device/decommission/%s" % (url, data)
        }
        rest_put_json_header = {
            "content-type": "application/json",
            "Accept": "application/json",
        }
        return rest_put_uri[self], rest_put_json_header


class DNAC_API_Calls:
    def __init__(self, username=None, password=None, url=None, data=None):
        self.username = username
        self.password = password
        self.url = url
        self.data = data

    def get(uri, header):
        """gets the specified uri and returns: response code, json formatted response. """
        response = requests.get(uri, verify=False, headers=header)
        if response.status_code != 204:
            code = response.status_code
            response = response.json()
        else:
            response = json.dumps("None")
            code = response.status_code
        return code, response

    def delete(uri, header, payload):
        """gets the specified uri and returns: response code, response. """
        response = requests.delete(uri, verify=False, headers=header, params=payload)
        return response.status_code, response


class DNAC_URNs:
    def __init__(self, url):
        self.url = url

    def get(self, url, token=""):
        """returns appropriate REST GET uri and header given shorthand key"""
        rest_get_uri = {"network-devices": "%s/dna/intent/api/v1/network-device" % url}
        rest_get_json_header = {
            "content-type": "application/json",
            "x-auth-token": "%s" % token,
        }
        return rest_get_uri[self], rest_get_json_header

    def delete(self, url, device_id="", token=""):
        """returns appropriate REST GET uri and header given shorthand key"""
        rest_delete_uri = {
            "device": "%s/dna/intent/api/v1/network-device/%s" % (url, device_id)
        }
        rest_delete_json_header = {
            "content-type": "application/json",
            "x-auth-token": "%s" % token,
        }
        reset_delete_payload = {"isForceDelete": "true"}
        return rest_delete_uri[self], rest_delete_json_header, reset_delete_payload
