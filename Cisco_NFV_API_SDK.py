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
        if response.status_code != 204:
            code=response.status_code
            response=response.json()
        else:
            reponse=json.dumps('None')
            code=response.status_code
        return code, response

    def delete(username,password,uri,header):
        '''gets the specified uri and returns: response code, response. '''
        response = requests.delete(uri, verify=False, auth=HTTPBasicAuth(username,password),headers=header)
        return response.status_code, response

    def post(username,password,uri,header,xml_data='',json_data=''):
        '''gets the specified uri and returns: response code, json formatted response. '''
        if xml_data != '':
            data=xml_data
        else:
            data = json_data
        response = requests.post(uri, verify=False, auth=HTTPBasicAuth(username,password),headers=header,data=data)
        return response.status_code, response


class NFVIS_URNs:

    def __init__(self,url):
        self.url=url

    def get(self,url,format='json'):
        '''returns appropriate REST GET uri and header given shorthand key'''
        rest_get_uri={'deployments':'%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments'%url,
                      'platform-detail':"%s/api/operational/platform-detail"%url,
                      'networks':'%s/api/config/networks?deep'%url,
                      'bridges':'%s/api/config/bridges?deep'%url}
        rest_get_header={'json':{"content-type": "application/vnd.yang.collection+json","Accept": "application/vnd.yang.data+json"},'xml':None}
        return rest_get_uri[self],rest_get_header[format]
    def post(self,url,format='json',vnf=None,bridge=None,network=None):
        '''returns appropriate REST POST uri and header given shorthand key and object to be posted
        url arguemnt needs to be in format: https://<ip or name of nfvis system>'''
        rest_post_uri={'bridges':"%s/api/config/bridges"%url,
                       'networks':"%s/api/config/networks"%url,
                       'deployments':"%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments"%url}
        rest_post_header={'json':{'content-type': "application/vnd.yang.data+json", 'accept': "application/vnd.yang.data+json"},
                          'xml':{"content-type": "application/vnd.yang.data+xml","Accept": "application/vnd.yang.data+xml"}}
        rest_post_json_data={'bridges':"{\"bridge\": [{\"name\": \"%s\"}]}"%bridge,
                             'networks':"{\"network\":[{\"name\":\"%s\",\"bridge\":\"%s\"}]}"%(network,bridge),
                             'deployments':None}
        return rest_post_uri[self],rest_post_header[format],rest_post_json_data[self]
    def delete(self,url,format='json',vnf='',bridge='',network=''):
        '''returns appropriate REST DELETE uri and header given shorthand key and object to be deleted'''
        rest_delete_uri={'vnf':"%s/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/%s"%(url,vnf),
                        'network':'%s/api/config/networks/network/%s'%(url,network),
                        'bridge':'%s/api/config/bridges/bridge/%s'%(url,bridge)}
        rest_delete_header={'json':{"content-type": "application/vnd.yang.collection+json","Accept": "application/vnd.yang.data+json"},'xml':None}
        return rest_delete_uri[self],rest_delete_header[format]
