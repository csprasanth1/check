import requests
import argparse
import json
import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#requests.packages.urllib3.exceptions

user= sys.argv[1]
passwd=sys.argv[2]
url= sys.argv[3]
url1= url+"/login"
nsxu=sys.argv[4]
nsxp=sys.argv[5]
nsxurl=sys.argv[6]
nf=sys.argv[7]
def web_login():
    data = {
    "usernameOrEmail": user,
    "password": passwd
    }
#    print(url1)
    r = requests.post(url1, json=data, verify=False)
#    print(r)
    token=r.json()['accessToken']
    token = "Bearer "+ token
 #   print(token)
    return token


def get_details():
    token = web_login()
    url2=url+"/jenkinsapi/assets"
    headers = {'Authorization': token, 'accept': 'application/json'}
    r1 = requests.get(url2,headers=headers, verify=False)
    data2=r1.json()
    for i in range(len(data2['items'])):

    #    print(data2['items'][i]['nfName'])
        if (data2['items'][i]['nfName']) == nf:
            nf_id=(data2['items'][i]['assetId'])
        #    print(nf_id)
            return nf_id

def nf_form():
    token = web_login()
    headers = {'Authorization': token, 'accept': 'application/json'}
    nf_id=get_details()
    url2= url+"/jenkinsapi/assets/"+str(nf_id)
    cluster2 = requests.get(url2, headers=headers, verify=False)
    #output2 = json.loads(cluster2.text)
    web_input = cluster2.json()
    #json_object = json.dumps(web_input, indent=2)
    #print(json_object)
    return web_input


def versions(version_key, data, value):
    if (version_key in data):
        eidx=data.index(version_key)
        version=value[eidx]
    else:
        version="0.0"
    return version


if __name__=='__main__':
    web_input = nf_form()
#    filejson = open("./webinput_new.json")
#    web_input = json.load(filejson)

#    print(type(web_input))
#    print(((web_input['categories'])))

    for i in range(len(web_input['categories'])):
        #print(web_input['categories'][i]['categoryName'])
        #print(i)

        if (web_input['categories'][i].get('categoryName')) == "capacity":
            plat_idx2=i
            #print(plat_idx2)
            break
    for n in range(len(web_input['categories'][plat_idx2]['fields'])):
        if web_input['categories'][plat_idx2]['fields'][n]['fieldName'] == "Cluster Instance Name":
            clsname = web_input['categories'][plat_idx2]['fields'][n]['fieldValue']
        elif((web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Workload") or (web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Management")):
        #if(web_input['categories'][plat_idx2]['fields'][n]['fieldName'])=="Kubernetes Min Version":
            field_idx=n
            #print(field_idx)
            break
    for x in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'])):
        if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][x]['fieldName']) == "Cluster Networking details":
            net_idx=x
            #print(x)
            break
    for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'])):
        if  (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][y]['fieldName']) == "Network Infrastructure configuration":
            network_idx=y
            #print(network_idx)
            data=[]
            version_value=[]
            data.clear()
            version_value.clear()
            for  zz in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'])):
                data.append(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'][zz]['fieldName'])
                version_value.append(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'][zz]['fieldValue'])
      #  print(data)
      #  print(version_value)
            segment_name=versions('Segment name', data, version_value)
            Tier1=versions('Tier1 name', data, version_value)
            Tier0=versions('Tier0 name', data, version_value)
            Edge_Cluster=versions('Edge Cluster ID', data, version_value)
            gateway_address=versions('gateway_address', data, version_value)
            DHCP_ranges=versions('DHCP_ranges', data, version_value)
            DHCP_server=versions('DHCP server IP', data, version_value)
            DNS_server=versions('DNS server', data, version_value)
            Network_range=versions('Network range', data, version_value)
            Transport_zone=versions('Transport zone id', data, version_value)

            if segment_name == "MANAGEMENT":
                segment = clsname+'_'+segment_name
            else:
                segment = segment_name

            '''
            print(segment)
            print(Tier1)
            print(Tier0)
            print(Edge_Cluster)
            print(gateway_address)
            print(DHCP_ranges)
            print(DHCP_server)
            print(DNS_server)
            print(Network_range)
            print(Transport_zone)
            '''
            segurl=nsxurl+"/policy/api/v1/infra/segments"
            url=nsxurl+"/policy/api/v1/infra"
            dhcpurl=nsxurl+"/policy/api/v1/infra/dhcp-server-configs/dhcpconf_"+segment
            headers={'Content-Type': 'application/json'}
            maindata = {
                "resource_type" : "Infra",
                "id" : "infra",
                "display_name" : "infra",
                "children" : [ {
                    "Tier1" : {
                        "tier0_path" : "/infra/tier-0s/"+Tier0,
                        "failover_mode" : "NON_PREEMPTIVE",
                        "enable_standby_relocation" : "false",
                        "route_advertisement_types" : ["TIER1_CONNECTED", "TIER1_NAT", "TIER1_IPSEC_LOCAL_ENDPOINT"],
                        "force_whitelisting" : "false",
                        "default_rule_logging" : "false",
                        "disable_firewall" : "false",
                        "pool_allocation" : "ROUTING",
                        "resource_type" : "Tier1",
                        "id" : Tier1,
                        "display_name" : Tier1,
                        "children" : [ {
                            "LocaleServices" : {
                                "edge_cluster_path" : "/infra/sites/default/enforcement-points/default/edge-clusters/"+Edge_Cluster,
                                "resource_type" : "LocaleServices",
                                "id" : "default",
                                "display_name" : "default"
                            },
                        "resource_type" : "ChildLocaleServices",
                        "id" : "default",
                        "marked_for_delete" : "false"
                        }]
                    },
                "resource_type" : "ChildTier1",
                "id" : Tier1,
                "marked_for_delete" : "false"
                },
                {
                    "Segment" : {
                        "subnets" : [ {
                            "gateway_address" : gateway_address,
                            "dhcp_ranges" : [ DHCP_ranges ],
                            "dhcp_config" : {
                                "resource_type" : "SegmentDhcpV4Config",
                                "server_address" : DHCP_server,
                                "lease_time" : 86400,
                                "dns_servers" : [ DNS_server ]
                            },
                            "network" : Network_range
                        } ],
                        "connectivity_path" : "/infra/tier-1s/"+Tier1,
                        "transport_zone_path" : "/infra/sites/default/enforcement-points/default/transport-zones/"+Transport_zone,
                        "advanced_config" : {
                            "connectivity" : "ON"
                        },
                        "resource_type" : "Segment",
                        "dhcp_config_path" : "/infra/dhcp-server-configs/dhcpconf_"+segment,
                        "id" : segment,
                        "display_name" : segment
                    },
                    "resource_type" : "ChildSegment",
                    "id" : segment,
                    "marked_for_delete" : "false"
                }]
                }
            dhcpdata = {
                "server_address" : DHCP_server,
                "edge_cluster_path" : "/infra/sites/default/enforcement-points/default/edge-clusters/"+Edge_Cluster,
                "resource_type" : "DhcpServerConfig",
                "id" : "dhcpconf_"+segment,
                "display_name" : "dhcpconf_"+segment,
            }

            #print(maindata)
            #print(dhcpdata)
            ################# Validating segment ####################
            response = requests.get(segurl, auth=(nsxu, nsxp), json=dhcpdata, verify=False, headers=headers)
            data=response.json()
            #print(data)
            #data = data['results']
            #print(data['results'][0]['id'])
            for i in range(len(data['results'])):
                #print(data['results'][i]['id'])
                if segment == data['results'][i]['id']:
                    print("Segment " +segment+ " is already exists")
                    sys.exit(1)
            #data=json.load(data)
            #print(data)
            print("Creating DHCP Config.....")
            response = requests.patch(dhcpurl, auth=(nsxu, nsxp), json=dhcpdata, verify=False, headers=headers)
            if response.status_code != 200:
                print("Error in DHCP config Creation")
                print(response.text)
                sys.exit(1)
            else:
                print("DHCP Config Created")

            ############# Tier1 with Segment Creation ###################
            print("Creating Tier1 with Segment.....")
            response = requests.patch(url, auth=(nsxu, nsxp), json=maindata, verify=False, headers=headers)
            if response.status_code != 200:
                print("Error in Tier1 with segment Creation")
                print(response.text)
                sys.exit(1)
            else:
                print("Tier1 with segment is Created successfully")
            ###################################################################################
