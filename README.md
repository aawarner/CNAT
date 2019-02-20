# Cisco NFVIS Automation Tool
A Python script that will automate the administration of NFVIS. 
This program will enable the retrieval of platform information 
as well as automate the deployment and deletion of bridges, networks,
and virtual network functions to NFVIS. This tool works in an interactive
and non-interactive mode.

  * [Supported platforms](#supported-platforms)
  * [Usage](#usage)
  * [Operation](#operation)

## Supported platforms
NFVIS 3.9.1\
NFVIS 3.9.2\
NFVIS 3.10.1\
NFVIS 3.10.2

## Usage

Interactive Mode

```
usage: CDAT.py
```

Non-Interactive Mode

```
usage: CDAT.py [p] deployments {ip-address} ASAv.xml
```

## Operation

Interactive Mode

```

CDAT.py

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

Option: 
```


**Non-Interactive Mode**

Non-Interactive mode supports the following arguments:
```
g = platform-detail, bridges, networks, deployments, flavors, images

p = bridges, networks, deployments
	
d = bridges, networks, deployments
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

**Examples**

GET:
```
python3 CDAT.py g networks 172.16.82.123
Username: admin
Password: 
API Response Code: 200 :

Request URI: https://172.16.82.123/api/config/networks?deep

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

```CDAT.py g flavors 172.16.82.123
Username: admin
Password: 
API Response Code: 200 :

Request URI: https://172.16.82.123/api/config/vm_lifecycle/flavors

JSON Reponse:

{'vmlc:flavors': {'flavor': [{'name': 'ASAv10'}, {'name': 'ASAv30'}, {'name': 'ASAv5'}, {'name': 'ISRv-medium'}, {'name': 'ISRv-mini'}, {'name': 'ISRv-small'}]}}


############################################################

Hierarchical Config:

vmlc:flavors
        |
        -->flavor
                |
                -->ASAv10
                |
                -->ASAv30
                |
                -->ASAv5
                |
                -->ISRv-medium
                |
                -->ISRv-mini
                |
                -->ISRv-small
```
POST:
```
CDAT.py p deployments 172.16.82.123 ASAv.xml
```
DELETE:
```
CDAT.py d deployments 172.16.82.123 ASAv.xml
```
