#!/usr/bin/python
#-*-coding:utf-8-*-
'''
Filename: NFVIS_API_SDK.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
         Wade Lehrschall (wlehrsch@cisco.com)
         Kris Swanson (kriswans@cisco.com)
Description:    This program will provide reuasable calls when interacting with NFVIS, DNA-C, and vManage APIs.
'''



import requests
import json
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class NFVIS_API_Calls:
    '''NFVIS class to define REST API URLs and Headers with
    get, post and delete methods.
    username=string,
    password=string
    url=string :formatted from NFVIS_URNs class
    header=dictionary :from NFVIS_URNs class

    '''

    def __init__(self,username=None,password=None,url=None,data=None):
        self.username=username
        self.password=password
        self.url=url
        self.data=data

    def get(username,password,uri,header):
        '''gets the specified uri and returns: response code, json formatted response. '''
        response = requests.get(uri, verify=False, auth=HTTPBasicAuth(username,password),headers=header)
        return response.status_code, response.json()

    def delete(username,password,uri,header):
        '''gets the specified uri and returns: response code, response. '''
        response = requests.delete(uri, verify=False, auth=HTTPBasicAuth(username,password),headers=header)
        return response.status_code, response

    def post(username,password,uri,header,data):
        '''gets the specified uri and returns: response code, json formatted response. '''
        response = requests.get(uri, verify=False, auth=HTTPBasicAuth(username,password),headers=header,data=data)
        return response.status_code, response.json()


class NFVIS_URNs:

    def __init__(self,url):
        self.url=url

    def get(self,url):
        '''returns appropriate REST GET uri and header given shorthand key'''
        rest_get_uri={'deployments':'%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments'%url,
                      'platform-detail':"%s/api/operational/platform-detail"%url,
                      'networks':'%s/api/config/networks?deep'%url,
                      'bridges':'%s/api/config/bridges?deep'%url}
        rest_get_json_header={"content-type": "application/vnd.yang.collection+json","Accept": "application/vnd.yang.data+json"}
        rest_get_xml_header={}
        return rest_get_uri[self],rest_get_json_header
    def post(self,url):
        '''returns appropriate REST POST uri and header given shorthand key and object to be posted'''
        rest_post_uri={'bridges':"%s/api/config/bridges"%url,
                       'networks':"%s/api/config/networks"%url,
                       'deployments':"%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments"%url}
        rest_post_json_header={}
        rest_post_xml_header={"content-type": "application/vnd.yang.data+xml","Accept": "application/vnd.yang.data+xml"}
        return rest_post_uri[self],rest_post_xml_header
    def delete(self,url,vnf='',bridge='',vswitch=''):
        '''returns appropriate REST DELETE uri and header given shorthand key and object to be deleted'''
        rest_delete_uri={'vnf':"%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/%s"%(url,vnf),
                        'vswitch':'%s/api/config/networks/network/%s'%(url,vswitch),
                        'bridge':'%s/api/config/bridges/bridge/%s'%(url,bridge)}
        rest_delete_json_header={"content-type": "application/vnd.yang.collection+json","Accept": "application/vnd.yang.data+json"}
        rest_delete_xml_header={}
        return rest_delete_uri[self],rest_delete_json_header
