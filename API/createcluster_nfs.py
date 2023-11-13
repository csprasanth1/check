import requests
import json
import ruamel.yaml
import sys
import base64
import time
import re
import argparse
import os

from jinja2 import Environment, FileSystemLoader
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
file_loader = FileSystemLoader('API/templates')
env = Environment(extensions=['jinja2.ext.loopcontrols'],loader=file_loader,trim_blocks=True)

parser = argparse.ArgumentParser(description='Script for Cluster Deployment using TCA')
parser.add_argument('-p1', '--cpass',required=True, help="Cluster Password")
parser.add_argument('-p2', '--telco',required=True, help="TCA Cluster IP")
parser.add_argument('-p3', '--tpass',required=True, help="TCA Password")
parser.add_argument('-p4', '--vfolder',required=True, help="Vsphere Folder")
#parser.add_argument('-p5', '--vnet',required=True, help="Vsphere VLAN")
parser.add_argument('-p6', '--vres',required=True, help="Vsphere Resource Pool")
parser.add_argument('-p7', '--mgtcls',required=True, help="Management Cluster Name")
parser.add_argument('-p8', '--tcacp',required=True, help="TCA-CP URL")
parser.add_argument('-p9', '--webpass',required=True, help="Web Portal Password")
parser.add_argument('-p10', '--nfname',required=True, help="NF Name")
parser.add_argument('-p11', '--weburl',required=True, help="Web Portal URL")
parser.add_argument('-p12', '--clusterip',required=True, help="Cluster IP")
parser.add_argument('-p13', '--tuser',required=True, help="TCA Username")
parser.add_argument('-p14', '--webuser',required=True, help="Web Portal Username")
parser.add_argument('-p15', '--aurl',required=True, help="Airgap URL")
#parser.add_argument('-p16', '--aext',required=True, help="Airgap Extension ID")
parser.add_argument('-p17', '--hurl',required=True, help="Harbor URL")
#parser.add_argument('-p18', '--hext',required=True, help="Harbor Extension ID")
parser.add_argument('-p19', '--slog', help="Syslog Server IP", nargs='?', const='')
parser.add_argument('-p20', '--huser',required=True, help="Harbor User")
parser.add_argument('-p21', '--hpass',required=True, help="Harbor Password")
#parser.add_argument('-p22', '--nip', help="NFS Server IP", nargs='?', const='')
#parser.add_argument('-p23', '--clsname',required=True, help="Cluster Name")
args = parser.parse_args()


clspass = args.cpass
tca = args.telco
tcapass = args.tpass
folder = args.vfolder
#net = args.vnet
RP = args.vres
mgt = args.mgtcls
tcp = args.tcacp
web_pass = args.webpass
nf = args.nfname
filecls= "clustername"
clsip = args.clusterip
tcauser = args.tuser
webuser = args.webuser
airgap = args.aurl
#airgap_extn = args.aext
harbor = args.hurl
#harbor_extn = args.hext
syslog = args.slog
harbor_user = args.huser
harbor_pass = args.hpass
#nfs_svr = args.nip
#nfs_path = args.nfolder
weburl = args.weburl
#cluster_name = args.clsname
'''
#############################################
'''
###############Final Code Functions #############################################################################
# Encode password with base64
def base64_encode(string_pass):
    message_bytes = string_pass.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    passwd_en = base64_bytes.decode('ascii')
    return passwd_en

# REST API requests
def restapi(url,data,header,method):
    try:
        if method == "session":
            response = requests.post(url, json=data, verify=False)
        elif method == "get":
            response = requests.get(url, headers=header, verify=False)
        elif method == "post":
            response = requests.post(url, json=data, headers=header, verify=False)
        return response
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Connection Error:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Wrong",err)

###############Final Code#####################

tca_session_url = "https://"+tca+"/hybridity/api/sessions"
tca_query_url="https://"+tca+"/hybridity/api/infra/k8s/clusters/query"
ext_url = "https://"+tca+"/hybridity/api/extensions"
web_url = weburl+"/login"
web_asset_url = weburl+"/jenkinsapi/assets"
template_url = "https://"+tca+"/hybridity/api/infra/cluster-templates"
cluster_url = "https://"+tca+"/hybridity/api/infra/k8s/clusters"
tca_session_data = {
  "username": tcauser,
  "password": tcapass
}
tca_query_data = {
         "filter": {
             "clusterType": "MANAGEMENT"
             }
        }
web_data = {
    "usernameOrEmail": webuser,
    "password": web_pass
}
t_data = ""
t_header = ""


harbor_passwd = base64_encode(harbor_pass) #Harbor password encode with base64
clspass_en = base64_encode(clspass) #Cluster  password encode with base64 
# TCA session header
out = restapi(tca_session_url,tca_session_data,t_header,"session")
tca_out = out.headers["x-hm-authorization"]
headers_tca={'x-hm-authorization': tca_out}

# Fetch Management Cluster ID using Name
query_out = restapi(tca_query_url,tca_query_data,headers_tca,"post")
outputmgt = query_out.json()
mgtcheck=0
for i in range(len(outputmgt)):
    if outputmgt[i]['clusterName'] == mgt:
        mgtid = outputmgt[i]['id']
        mgtcheck=1
        break
if mgtcheck == 0:
    print("Management Cluster ID is missing")
    sys.exit(1)
# Fetch Extension IDs
headers_ext={'x-hm-authorization': tca_out, "accept": "application/json"}
ext_response = restapi(ext_url,t_data,headers_ext,"get")
ext_out = ext_response.json()
for i in range(len(ext_out["extensions"])):
    if (ext_out["extensions"][i]["extensionSubtype"]) == "Harbor" and ext_out["extensions"][i]["interfaceInfo"]["url"] in harbor:
        harbor_extn = (ext_out["extensions"][i]["extensionId"])


    elif (ext_out["extensions"][i]["extensionSubtype"]) == "Airgap" and ext_out["extensions"][i]["interfaceInfo"]["fqdn"] in airgap:
        airgap_extn = (ext_out["extensions"][i]["extensionId"])


######### Fetch from WebForm #############
web_header = {'Content-Type': 'application/json'}
web_sess_response = restapi(web_url,web_data,web_header,"post")
token = web_sess_response.json()['accessToken']
web_token = "Bearer "+ token
web_headers={'Authorization': web_token, 'accept': 'application/json'}
web_response = restapi(web_asset_url,t_data,web_headers,"get")
data2 = web_response.json()
for i in range(len(data2['items'])):
    if (data2['items'][i]['nfName']) == nf:
        nf_id=(data2['items'][i]['assetId'])

web_url2 = weburl+"/jenkinsapi/assets/"+str(nf_id)
web_out = restapi(web_url2,t_data,web_headers,"get")
web_input = web_out.json()
for i in range(len(web_input['categories'])):
    cat_idx=i

    if (web_input['categories'][cat_idx].get('categoryName')) == "capacity":
        plat_idx2=i
    elif (web_input['categories'][cat_idx].get('categoryName')) == "platform":
        plat_idx=i
    elif (web_input['categories'][cat_idx].get('categoryName')) == "dependency":
        plat_idx3=i

for n in range(len(web_input['categories'][plat_idx2]['fields'])):

    if((web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Workload") or (web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Management")):
            field_idx=n
            break

for s in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'])):
    if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][s]['fieldName']) == "Node Pool":
        node_pool_idx=s


        for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'])):
            if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'][y]['fieldName'] == "Node Pool Type" and web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'][y]['fieldValue'] == "Master"):
               node_pool_type = y
               #for z in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'])):
    #        elif (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'][y]['fieldName'] == "Node Pool Type" and web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'][y]['fieldValue'] == "Worker"):
                #print("Welcome to Worker")
                #for z in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'])):
                    #print(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][node_pool_idx]['children'][z])

    elif (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][s]['fieldName']) == "Cluster Networking details":
        #print(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][s])
        net_idx = s
        for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'])):
            if  (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][y]['fieldName']) == "Network Infrastructure configuration":
                network_idx=y
                for  zz in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'])):
                    if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'][zz]['fieldName']) == "DNS server":
                        dns_server = (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][net_idx]['children'][network_idx]['children'][zz]['fieldValue'])

    elif (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][s]['fieldName']) == "Cluster Storage details":
        #print("Welcome container storage")
        csi_idx=s
        for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'])):
           if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['fieldName'] == "Storage" and web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['fieldValue'] == "vsphere"):
               nfs_path = ''
               break

           elif web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['fieldName'] == "NFS Storage configuration":
               for m in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['children'])):
                   if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['children'][m]['fieldName'] ==  "NFSSharename" and web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['children'][m]['fieldValue']):
                       nfs_path = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['children'][m]['fieldValue']
                       nfs_path = "/vsanfs/" + nfs_path


############Save Cluster Name into Jenkins Variable###############
for n in range(len(web_input['categories'][plat_idx2]['fields'])):
    if web_input['categories'][plat_idx2]['fields'][n]['fieldName'] == 'Cluster Instance Name':
        cluster_name = web_input['categories'][plat_idx2]['fields'][n]['fieldValue']

############################################################
######## NFS SERVER DOMAIN #################################

isExist = os.path.exists('nfsdomain.txt')
if isExist == True:
    f = open('nfsdomain.txt','r')
    nfs_svr = f.read()
    print(nfs_svr)
else:
    nfs_svr = ''



#######Validating VM Template #################
for n in range(len(web_input['categories'][plat_idx]['fields'])):
    if web_input['categories'][plat_idx]['fields'][n]['fieldName'] == 'Kubernetes version':
        kver = web_input['categories'][plat_idx]['fields'][n]['fieldValue']
val = False
result = re.search('v(.*)\+', kver)
data=result.group(1)
with open('template.txt') as f:
        datafile = f.readlines()
for line in datafile:
    if data in line:
        temname=line.strip()
        val = True
        break
if not val:
    sys.exit("VM Template not found in vCenter for Kubernetes Ver " + kver)




######Template Creation##########

template = env.get_template("template_web.yaml")
output = template.render(data=web_input, plat_idx2=plat_idx2, field_idx=field_idx, net_idx=net_idx,node_pool_idx=node_pool_idx, csi_idx=csi_idx, plat_idx=plat_idx, node_pool_type=node_pool_type, plat_idx3=plat_idx3 )
file1 = open('input_yaml.yaml', 'w')
file1.write(output)
file1.close()
in_file = 'input_yaml.yaml'
out_file = 'output.json'

yaml = ruamel.yaml.YAML(typ='safe')
with open(in_file) as fpi:
    data = yaml.load(fpi)
with open(out_file, 'w') as fpo:
    json.dump(data, fpo, indent=2)
file = open('output.json')
data1 = json.load(file)

template_response = restapi(template_url,data1,headers_tca,"post")
if template_response:
    output=template_response.json()
    template_id=output['id']
    print ("Cluster Template Creation....... Success.")
    print(" Template ID is ",template_id)
else:
    print('"Cluster Template Creation Failed!!!!!!!')
    print(template_response.text)
################################

###### Fetch Datastore & Cluster from Capacity Report ####################
file = open('TEF/capacityfinalreport/refout.json')
data1 = json.load(file)


##########################################################################
######Cluster Creation##########
template = env.get_template('cluster_web.yaml')

output = template.render(data=web_input, data1=data1, plat_idx2=plat_idx2, field_idx=field_idx, net_idx=net_idx,node_pool_idx=node_pool_idx, csi_idx=csi_idx, plat_idx=plat_idx, node_pool_type=node_pool_type, plat_idx3=plat_idx3, clspass=clspass_en, syslog_server=syslog, clusterTempId=template_id, folder=folder, RP=RP, mgtid=mgtid, tcp=tcp, clsip=clsip, temname=temname, Airgap_fqdn=airgap, Airgap_extensionID=airgap_extn, Harbor_url=harbor, Harbor_extensionID=harbor_extn, harbor_user=harbor_user, harbor_passwd=harbor_passwd, nfs_svr=nfs_svr, nfs_path=nfs_path, dns_server=dns_server, cluster_name=cluster_name )

file1 = open('input_yaml1.yaml', 'w')
file1.write(output)
file1.close()
in_file = 'input_yaml1.yaml'
out_file = 'output1.json'

yaml = ruamel.yaml.YAML(typ='safe')
with open(in_file) as fpi:
    data = yaml.load(fpi)
with open(out_file, 'w') as fpo:
    json.dump(data, fpo, indent=2)
file = open('output1.json')
data1 = json.load(file)
cluster_response = restapi(cluster_url,data1,headers_tca,"post")
if cluster_response:
    output=cluster_response.json()
    print ("Cluster Creation is initiated Successfully")
    #print(output)
    clusterid=output['id']
else:
    print('"Cluster Creation Failed!!!!!!!')
    print(cluster_response.text)
###############################

node_url="https://"+tca+"/hybridity/api/infra/k8s/clusters/"+clusterid
timeout = time.time() + 60*45  # 45 minutes from now
n = 45
while True:
    cls_response = restapi(node_url,t_data,headers_tca,"get")
    output=cls_response.json()
    STAT = output['status']
    ACTCNT = output['activeTasksCount']

    if STAT == "ACTIVE":
        print ("Cluster is Ready")
        break
    elif time.time() > timeout:
        print ("Cluster is taking time...Please check")
        sys.exit(1)
        break

    elif STAT == "NOT ACTIVE" and ACTCNT > 0:
        print ("Cluster deployment is in progress....Will wait for "+str(n)+" minutes")
        time.sleep(300)
        n = n - 5
    elif STAT != "ACTIVE" or STAT != "NOT ACTIVE" or (STAT == "NOT ACTIVE" and ACTCNT == 0):
        print ("Cluster Creation Failed...Please check")
        sys.exit(1)
        break

##########################################################################
###### Fetch kubeconfig file from Workload Cluster #######
#url5="https://"+tca+"/hybridity/api/infra/k8s/clusters/"+clusterid
wkld_response = restapi(node_url,t_data,headers_tca,"get")
output=wkld_response.json()
STAT = output['kubeConfig']
out=base64.b64decode(STAT)
file2 = open('workloadconfig', 'wb')
file2.write(out)
file2.close()
os.chmod("workloadconfig", 0o600)

