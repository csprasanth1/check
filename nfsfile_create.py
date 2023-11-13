import requests
import argparse
import json
import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#requests.packages.urllib3.exceptions
import subprocess


web_user=sys.argv[1]
web_passwd=sys.argv[2]
url=sys.argv[3]
url1= url+"/login"
user=sys.argv[4]
password=sys.argv[5]
nf=sys.argv[6]
server=sys.argv[7]

def web_login():
    data = {
    "usernameOrEmail": web_user,
    "password": web_passwd
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
#    print(type(web_input))
#    print(((web_input['categories'])))
    #print(web_input)
    for i in range(len(web_input['categories'])):
        #print(web_input['categories'][i]['categoryName'])
        #print(i)

        if (web_input['categories'][i].get('categoryName')) == "capacity":
            plat_idx2=i
            #print(plat_idx2)
            break
    for n in range(len(web_input['categories'][plat_idx2]['fields'])):
        if((web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Workload") or (web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Management")):
        #if(web_input['categories'][plat_idx2]['fields'][n]['fieldName'])=="Kubernetes Min Version":
            field_idx=n
            #print(field_idx)
            break
    for x in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'])):
        if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][x]['fieldName']) == "Cluster Storage details":
            cs_idx=x
            #print(x)
            break
    for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'])):
        if  (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][y]['fieldName']) == "NFS Storage configuration":
            nfs_idx=y
            #print(nfs_idx)
            break
        data=[]
        version_value=[]
        data.clear()
        version_value.clear()

    for z in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'])):
        print(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z])
        if web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'RootSquash':
            rootsquash = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']
        if web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'VSANFileShareAccessPermission':
            accesspermission = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']
        elif web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'NFSAccessControlIPSectorSubnet':
            ipsubnet = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']
        elif web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'NFSSharename':
            nfssharename = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']
        elif web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'HardQuotaGB':
            hardquota = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']
        elif web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldName'] == 'SoftQuotaGB':
            softquota = web_input['categories'][plat_idx2]['fields'][field_idx]['children'][cs_idx]['children'][nfs_idx]['children'][z]['fieldValue']



cmd = "TEF/capreport/fileshare.ps1"
#print(cmd)
sp=subprocess.run(['pwsh', '-File', cmd, accesspermission, ipsubnet, nfssharename, hardquota, softquota, user, password, rootsquash, server],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
#rc=sp.wait()
#output,error = sp.communicate()
if sp.returncode == 0:
#    print(f'OUTPUT is: {output}')
    print(sp.stdout)
else:
#    print(f'Error is: {error}')
    print(sp.stderr)
    sys.exit(1)

