import requests
import json
import sys
import base64
import time
import re
import subprocess as sp
import os

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

web_pass = sys.argv[2]
web_user = sys.argv[1]
nf = sys.argv[3]
harbor_user = sys.argv[4]
harbor_pass = sys.argv[5]
file=sys.argv[6]
harbor = sys.argv[7]
weburl = sys.argv[8]

def versionCompare(v1, v2):

    # This will split both the versions by '.'
    arr1 = v1.split(".")
    arr2 = v2.split(".")
    n = len(arr1)
    m = len(arr2)

    # converts to integer from string
    arr1 = [int(i) for i in arr1]
    arr2 = [int(i) for i in arr2]

    # compares which list is bigger and fills
    # smaller list with zero (for unequal delimiters)
    if n > m:
      for i in range(m, n):
         arr2.append(0)
    elif m > n:
      for i in range(n, m):
         arr1.append(0)

    # returns 1 if version 1 is bigger and -1 if
    # version 2 is bigger and 0 if equal
    for i in range(len(arr1)):
      if arr1[i]>arr2[i]:
         return 1
      elif arr2[i]>arr1[i]:
         return -1
    return 0


######## Fetch from WebForm #############
url = weburl+"/login"
headers={'Content-Type': 'application/json'}
data = {
    "usernameOrEmail": web_user,
    "password": web_pass
}

response = requests.post(url, json=data, headers=headers, verify=False)
token = response.json()['accessToken']
token = "Bearer "+ token
headers={'Authorization': token, 'accept': 'application/json'}

url3= weburl+"/jenkinsapi/assets"
cluster3 = requests.get(url3, headers=headers, verify=False)
data2 = cluster3.json()
for i in range(len(data2['items'])):
    if (data2['items'][i]['nfName']) == nf:
        nf_id=(data2['items'][i]['assetId'])

url2= weburl+"/jenkinsapi/assets/"+str(nf_id)
cluster2 = requests.get(url2, headers=headers, verify=False)
#output2 = json.loads(cluster2.text)
web_input = cluster2.json()

#print(web_input)
for i in range(len(web_input['categories'])):
    if (web_input['categories'][i].get('categoryName')) == "platform":
        plat_idx=i
    elif (web_input['categories'][i].get('categoryName')) == "dependency":
        plat_idx1=i

data=[]
for n in range(len(web_input['categories'][plat_idx]['fields'])):
    data.append(web_input['categories'][plat_idx]['fields'][n]['fieldName'])
if ("Istio Version" in data):
    istiodx=data.index("Istio Version")
#    print(istiodx)
    istio=web_input['categories'][plat_idx]['fields'][istiodx]['fieldValue']
########################################
######## Fetch from Harbor #############
url = ""+harbor+"/api/v2.0"
#print(url)
headers={'Content-Type': 'application/json'}
data = {
    "username": harbor_user,
    "password": harbor_pass
}

url1= ""+harbor+"/api/chartrepo/registry/charts/istio-base"
#print(url1)
cluster = requests.get(url1, headers=headers, verify=False)
data1 = cluster.json()
#print(data1)
aval_ver = []
for i in (data1):
    aval_ver.append(i['appVersion'])
#print(aval_ver)
#################################################
########################################
large_ver = []
for i in aval_ver:
    istio1=versionCompare(istio, i)
#    #print(istio)
    if istio1 == 0 or istio1 == -1:
       large_ver.append(i)
if large_ver == []:
   print("User Provided version is not available")
   sys.exit()
#print(large_ver)
list = sorted(large_ver)
version = list[0]
#print(version)

for i in data1:
    if (i['appVersion']) == version:
        istio_url = (i['urls'][0])
        #print(istio_url)

url2= ""+harbor+"/api/chartrepo/registry/charts/istio-discovery"
cluster1 = requests.get(url2, headers=headers, verify=False)
disc = cluster1.json()

for i in disc:
    if (i['appVersion']) == version:
        disc_url = (i['urls'][0])
        #print(disc_url)

url3= ""+harbor+"/api/chartrepo/registry/charts/istio-ingress"
cluster2 = requests.get(url3, headers=headers, verify=False)
ingress = cluster2.json()

for i in ingress:
    if (i['appVersion']) == version:
        ingress_url = (i['urls'][0])
        #print(ingress_url)

print("istio base installation is in progress...")
basecmd='helm upgrade --install istio-base '+harbor+'/chartrepo/registry/'+istio_url+' --create-namespace -n istio-system --wait --insecure-skip-tls-verify --kubeconfig '+file
#print(basecmd)

base_pod=sp.getoutput(basecmd)
basechk='helm status istio-base -n istio-system --kubeconfig '+file+'|grep STATUS:'
check_base=sp.getoutput(basechk)
if check_base.split(":")[1].strip() == "deployed":
    print("istio base installation.....SUCCESS")
else:
    print("istio base installation.....FAILED")
    sys.exit(1)



print("istio discovery installation is in progress...")
harborrepo=harbor.split("//")[1]
discmd='helm upgrade --install istiodis '+harbor+'/chartrepo/registry/'+disc_url+' -n istio-system --wait --insecure-skip-tls-verify --set global.hub=\"'+harborrepo+'/registry/istio\" --kubeconfig '+file
#print(discmd)
dispod=sp.getoutput(discmd)
dischk='helm status istiodis -n istio-system --kubeconfig '+file+'|grep STATUS:'
check_dis=sp.getoutput(dischk)
if check_dis.split(":")[1].strip() == "deployed":
    print("istio discovery installation.....SUCCESS")
else:
    print("istio discovery installation.....FAILED")
    sys.exit(1)

print("istio ingress installation is in progress...")
task1='kubectl create ns istio-ingress --kubeconfig '+file
sp.Popen(task1, shell=True)
task2='kubectl label namespace istio-ingress istio-injection=enabled --kubeconfig '+file
sp.Popen(task2, shell=True)
istio_ing='helm upgrade --install istio-ingress '+harbor+'/chartrepo/registry/'+ingress_url+' -n istio-ingress --insecure-skip-tls-verify --set global.hub=\"'+harborrepo+'/registry/istio\" --kubeconfig '+file
#print(istio_ing)
retcode = sp.getoutput(istio_ing)
ingress_check='helm status istio-ingress -n istio-ingress --kubeconfig '+file+'|grep STATUS:'
i_check=sp.getoutput(ingress_check)
if i_check.split(":")[1].strip() == "deployed":
    print("istio ingress installation.....SUCCESS")
else:
    print("istio ingress installation.....FAILED")
    sys.exit(1)

