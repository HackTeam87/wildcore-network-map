import os
import json
import requests


# WILDCORE_API_LINK=""
# WILDCORE_API_TOKEN="" 
url = os.getenv('WILDCORE_API_LINK', default=None)
token = os.getenv('WILDCORE_API_TOKEN', default=None)


payload = {}
headers = {'X-Auth-Key': token}

OUTPUT_TOPOLOGY_FILENAME = 'topology.js'
TOPOLOGY_FILE_HEAD = "\n\nvar topologyData = "
topology_dict = {'nodes': [], 'links': []}

response = requests.request("GET", url, headers=headers, data=payload)
data = response.json()
icon_model_map = {
    'Mikrotik CCR1016': 'router',
    'Mikrotik CCR1036': 'router',
    'CCR2116-12G-4S+': 'router',
    'Edge-core ES4612': 'router',
    'Cisco Switch (NX-OS)': 'switch',
    'Edge-core ES3528M': 'switch',
    'Edge-core ECS4120-28F': 'switch',
    'D-Link DES-3200-28/A1': 'switch',
    'D-Link DES-3200-26/A1': 'switch',
    'C-Data FD1204SN': 'switch',
    'C-Data FD1208': 'switch',
    'BDCOM GP3600-08': 'switch',
    'ps': 'host',
    }


def device_name(icon_model_map, device_model):
   
    
    if device_model:
        for model_shortname, icon_type in icon_model_map.items():
            if model_shortname in device_model:
                return icon_type
    return 'unknown'


def generate_topology_json():
    link_id = 0
    for link in data["data"]:
        
        topology_dict['links'].append({
            'id': link_id,
            'source': link["src_iface"]["device"]["id"],
            'srcDevice': link["src_iface"]["device"]["name"],
            'srcIfName': link["src_iface"]["name"],

            'target': link["dest_iface"]["device"]["id"],
            'tgtDevice': link["dest_iface"]["device"]["name"],
            'tgtIfName': link["dest_iface"]["name"], 
        })

        link_id += 1

    node_id = 0
    for host in data["data"]:

        topology_dict['nodes'].append({

            'id': host["src_iface"]["device"]["id"],
            'name': f'{host["src_device"]["ip"]} \n {host["src_device"]["name"]}',
            'primaryIP': host["src_device"]["ip"],
            'model': host["src_device"]["model"]["name"],
            'serial_number': "",
            'icon': device_name(icon_model_map, host["src_device"]["model"]["name"]),
            
        })

        topology_dict['nodes'].append({
            
            'id': host["dest_iface"]["device"]["id"],
            'name': f'{host["dest_device"]["ip"]}  {host["dest_device"]["name"]}',
            'primaryIP': host["dest_device"]["ip"],
            'model': host["dest_device"]["model"]["name"],
            'serial_number': "",
            'icon': device_name(icon_model_map, host["dest_device"]["model"]["name"])
        })
        node_id += 1

    return topology_dict    



def write_topology_file(topology_json, header=TOPOLOGY_FILE_HEAD, dst=OUTPUT_TOPOLOGY_FILENAME):
    with open(dst, 'w') as topology_file:
        topology_file.write(header)
        topology_file.write(json.dumps(topology_json, indent=4, sort_keys=True))
        topology_file.write(';')

TOPOLOGY_DICT = generate_topology_json()
write_topology_file(TOPOLOGY_DICT)        