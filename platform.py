import requests
import re
import json
import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
user=sys.argv[1]
passwd=sys.argv[2]
url=sys.argv[3]
nf=sys.argv[4]
#url1=os.path.join(url,'login')
url1= url+"/login"
#print(url1)

def web_login():
    data = {
    "usernameOrEmail": user,
    "password": passwd
    }
    r = requests.post(url1, json=data, verify=False)
    token=r.json()['accessToken']
    token = "Bearer "+ token
#    print(token)
    return token


def get_details():
    token = web_login()
    headers = {'Authorization': token, 'accept': 'application/json'}
    url3= url+"/jenkinsapi/assets"
    r1 = requests.get(url3,headers=headers, verify=False)
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
    return web_input

def versions(version, plat, data):
    if (version in data):
        eidx=data.index(version)
        version=web_input['categories'][plat]['fields'][eidx]['fieldValue']
    else:
        version="0.0"
    return version


if __name__=='__main__':
    web_input = nf_form()
   # print(type(web_input))
   # print(range(len(web_input['categories'])))
    for i in range(len(web_input['categories'])):
#        print(web_input['categories'][i]['categoryName'])
        if (web_input['categories'][i].get('categoryName')) == "platform":
            plat_idx=i
            #print(plat_idx)
        elif (web_input['categories'][i].get('categoryName')) == "dependency":
            plat_idx1=i
            #print(plat_idx1)
    data=[]
    for n in range(len(web_input['categories'][plat_idx]['fields'])):

        data.append(web_input['categories'][plat_idx]['fields'][n]['fieldName'])
    #print(data)


    data1=[]
    for n in range(len(web_input['categories'][plat_idx1]['fields'])):
        data1.append(web_input['categories'][plat_idx1]['fields'][n]['fieldName'])
    #print(data1)

    kernel_ver= versions("Kernel Version", plat_idx1, data1)
    #print(kernel_ver)
    etcd_ver = versions("k8s.grc.io/etcd Version", plat_idx, data)
    #print(etcd_ver)

    core_ver = versions("k8s.grc.io/coredns Version", plat_idx, data)
    mul_ver = versions("Multus Version", plat_idx, data)
    kub_ver = versions("Kubernetes version", plat_idx, data)
    result = re.search('v(.*)\+', kub_ver)
    kub_ver=result.group(1)
    api_ver = versions("Kubernetes API Version", plat_idx, data)
    hel_ver = versions("Helm Version", plat_idx, data)
    pro_ver = versions("Prometheus Version", plat_idx, data)
    cal_ver = versions("Calico Version", plat_idx, data)
    gra_ver = versions("Grafana Version", plat_idx, data)
    ela_ver = versions("Elasticsearch Version", plat_idx, data)
    kib_ver = versions("Kibana Version", plat_idx, data)
    met_ver = versions("metrics-server Version", plat_idx, data)
    ope_ver = versions("K8S Operators Version", plat_idx, data)
    cont_ver = versions("containerd", plat_idx, data)
    istio_ver = versions("Istio Version", plat_idx, data)


    out={}
    out["etcd"] = etcd_ver.strip()
    out["core"] = core_ver.strip()
    out["mul"] = mul_ver.strip()
    out["kubernetes"] = kub_ver.strip()
    out["apiversion"] = api_ver.strip()
    out["helm"] = hel_ver.strip()
    out["calico"] = cal_ver.strip()
    out["grafana"] = gra_ver.strip()
    out["prometheus"] = pro_ver.strip()
    out["elasticsearch"] = ela_ver.strip()
    out["kibana"] = kib_ver.strip()
    out["metrics"] = met_ver.strip()
    out["operators"] = ope_ver.strip()
    out["kernel"] = kernel_ver.strip()
    out["containerd"] = cont_ver.strip()
    out["istio"] = istio_ver.strip()
    dataout=json.dumps(out)
    print(dataout)

