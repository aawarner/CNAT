# Cisco NFVIS Automation Tool
A Python script that will automate the administration of NFVIS. 
This program will enable the retrieval of platform information 
as well as automate the deployment and deletion of bridges, networks,
and virtual network functions to NFVIS. This tool works in an interactive
and non-interactive mode.\
Cisco NFVIS is a KVM based hypervisor that is purpose built for the 
virtualization of network functions. A brief description of capabilities 
can be found here:

https://www.cisco.com/c/en/us/solutions/collateral/enterprise-networks/enterprise-network-functions-virtualization-nfv/datasheet-c78-738570.html

  * [Supported platforms](#supported-platforms)
  * [Usage](#usage)
  * [Operation](#operation)
  * [Contributing](#contributing)

## Supported platforms
NFVIS 3.9.1\
NFVIS 3.9.2\
NFVIS 3.10.1\
NFVIS 3.10.2

## Requirements
CNAT relies on the following packages:\
PyNFVSDK\
tabulate\
requests\
getpass\
Install theses packages using pip:
```
pip install -r requirements.txt
```
CNAT requires a system with NFVIS as the installed OS. All VNF images and packages should be preinstalled on the system.
An NFVIS sandbox is also available from Cisco dCloud.

https://dcloud2-rtp.cisco.com/content/demo/453732?returnPathTitleKey=content-view&isLoggingIn=true
## Usage

### Interactive Mode

```
usage: CNAT.py
```

### Non-Interactive Mode

```
usage: CNAT.py [method] [option] [ip-address] [file.xml]

usage: CNAT.py [method] [option] [bulk] [file.xml]
```

## Operation

### Interactive Mode
Interactive mode is a menu driven experience. The user should
select an option that corresponds with the desired task.
```
CNAT.py 

#################################
####Cisco NFVIS Automation Tool####
################################# 

Select an option from the menu below. 

 Options: 

 '1' List NFVIS system information
 '2' List running VNF's from NFVIS
 '3' Delete Virtual Switch from NFVIS
 '4' Delete VNF from NFVIS
 '5' Deploy Virtual Switch to NFVIS from file
 '6' Deploy VNF to NFVIS from file
 '7' Deploy Service Chained VNFs to NFVIS
 '8' Reset demo environment
 'p' print options
 'q' quit the program

Option: 1
What is the IP address of the NFVIS system: 
10.10.10.10
Enter your username and password. 
Username: admin
Password: 
API Response Code: 200 :
https://10.10.10.10/api/operational/platform-detail
Platform Details: 

╒════════════════════╤════════════════════════════════════════════════╕
│ Manufacturer       │ Cisco Systems, Inc.                            │
├────────────────────┼────────────────────────────────────────────────┤
│ PID                │ ENCS5412/K9                                    │
├────────────────────┼────────────────────────────────────────────────┤
│ SN                 │ FGL211310QJ                                    │
├────────────────────┼────────────────────────────────────────────────┤
│ hardware-version   │ M3                                             │
├────────────────────┼────────────────────────────────────────────────┤
│ UUID               │ 70DB98C0-1B64-0000-FE49-E01BEBC65375           │
├────────────────────┼────────────────────────────────────────────────┤
│ Version            │ 3.10.2-FC3                                     │
├────────────────────┼────────────────────────────────────────────────┤
│ Compile_Time       │ Friday, January 25, 2019 [15:25:34 PST]        │
├────────────────────┼────────────────────────────────────────────────┤
│ CPU_Information    │ Intel(R) Xeon(R) CPU D-1557 @ 1.50GHz 12 cores │
├────────────────────┼────────────────────────────────────────────────┤
│ Memory_Information │ 65768572 kB                                    │
├────────────────────┼────────────────────────────────────────────────┤
│ Disk_Size          │ 64.0 GB                                        │
├────────────────────┼────────────────────────────────────────────────┤
│ CIMC_IP            │ NA                                             │
├────────────────────┼────────────────────────────────────────────────┤
│ Entity-Name        │ ENCS                                           │
├────────────────────┼────────────────────────────────────────────────┤
│ Entity-Desc        │ Enterprise Network Compute System              │
├────────────────────┼────────────────────────────────────────────────┤
│ BIOS-Version       │ ENCS54_2.6.071220181123                        │
├────────────────────┼────────────────────────────────────────────────┤
│ CIMC-Version       │ NA                                             │
╘════════════════════╧════════════════════════════════════════════════╛

 
```
Deployment of bridges, networks, and VNF's in interactive mode require that
bridge.xml, network.xml, and vnf.xml files be present in the XML directory.
The program will rewrite these files for the POST operation to NFVIS based
on user input.

### Non-Interactive Mode

Non-Interactive mode supports the following arguments:
```
g = platform-detail, bridges, networks, deployments, flavors, images

p = bridges, networks, deployments
	
d = bridges, networks, deployments

h = help menu
```
g = get\
p = post\
d = delete

To retrieve information about the system use the get method. 
To deploy a bridge, network, or VNF use the post method. 
To delete an existing bridge, network, or VNF use the delete method.

When using the post method a .xml template is required for configuration
of the bridge, network, or VNF. Examples of the templates can be found
in the XML folder.

If the creds.json file is not present in the working directory the user
will be prompted to enter device credentials. The program will then create 
the creds.json file in the working directory. The IP address and credentials
entered will be stored in the creds.json file for future use providing a 
true non interactive experience. Alternatively, the creds.json file can be 
prepopulated for bulk automation. The creds.json file has been added to
.gitignore to ensure it is not tracked by git.

Non-interactive mode supports the use of the "bulk" argument. If the "bulk"
argument is used instead of an IP address then the requested operation will
be run on all devices that exist within creds.json.



**Examples**

**GET:**
```
CNAT.py g networks 10.10.10.10
Username: admin
Password: 
API Response Code: 200

Request URI: https://10.10.10.10/api/config/networks?deep

JSON Reponse:

{'network:networks': {'network': [{'name': 'wan-net', 'bridge': 'wan-br'}, {'name': 'lan-net', 'bridge': 'lan-br'}]}}


############################################################

Hierarchical Config:

network:networks
        |
        -->network
                |
                -->wan-net
                |
                -->wan-br
                |
                -->lan-net
                |
                -->lan-br

```

```
CNAT.py g deployments 10.10.10.10

API Response Code: 200

Request URI: https://10.10.10.10/api/config/vm_lifecycle/tenants/tenant/admin/deployments

JSON Reponse:

{'vmlc:deployments': {'deployment': [{'name': 'FIREWALL'}, {'name': 'ROUTER'}]}}


############################################################

Hierarchical Config:

vmlc:deployments
        |
        -->deployment
                |
                -->FIREWALL
                |
                -->ROUTER

```
**POST:**
```
CNAT.py p deployments 10.10.10.10 XML/ASAv_ENCS.xml 
Username: admin
Password: 
API Response Code: 201

Request URI: https://10.10.10.10/api/config/vm_lifecycle/tenants/tenant/admin/deployments

JSON Reponse:

<Response [201]>


VNF deployment successful

```
```
CDAT.py p networks bulk XML/network.xml 
API Response Code: 201

Request URI: https://10.10.10.10/api/config/networks

JSON Reponse:

<Response [201]>


Deployment successful
API Response Code: 201

Request URI: https://10.10.10.11/api/config/networks

JSON Reponse:

<Response [201]>


Deployment successful
API Response Code: 201

Request URI: https://10.10.10.12/api/config/networks

JSON Reponse:

<Response [201]>


Deployment successful
```
**DELETE:**
```
CNAT.py d deployments 10.10.10.10 ASAv
Username: admin
Password: 

https://10.10.10.10/api/config/vm_lifecycle/tenants/tenant/admin/deployments/deployment/ASAv 
API Status Code: 204

VNF deletion successful

```
```
CNAT.py d bridge bulk test-br

https://10.10.10.10/api/config/bridges/bridge/test-br 
API Status Code: 204

Deletion successful

https://10.10.10.11/api/config/bridges/bridge/test-br 
API Status Code: 204

Deletion successful

https://10.10.10.12/api/config/bridges/bridge/test-br 
API Status Code: 204

Deletion successful
```
## Contributing
See [CONTRIBUTING](./CONTRIBUTING.md)
