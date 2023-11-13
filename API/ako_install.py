import requests
import json
import sys
import base64
import time
import re
import subprocess
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
ako = sys.argv[9]

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
'''
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
if ("AKO Version" in data):
    akodx=data.index("AKO Version")
#    print(istiodx)
    ako=web_input['categories'][plat_idx]['fields'][akoodx]['fieldValue']
'''
########################################
######## Fetch from Harbor #############
url = ""+harbor+"/api/v2.0"
#print(url)
headers={'Content-Type': 'application/json'}
data = {
    "username": harbor_user,
    "password": harbor_pass
}

url1= ""+harbor+"/api/chartrepo/registry/charts/ako"
cluster = requests.get(url1, headers=headers, verify=False)
data1 = cluster.json()
#print(data1)
aval_ver = []
for i in (data1):
    aval_ver.append(i["appVersion"])
#print(aval_ver)

large_ver = []
for i in aval_ver:
    ako1=versionCompare(ako, i)
#    print(ako1)
    if ako1 == 0 or ako1 == -1:
       large_ver.append(i)
if large_ver == []:
   print("User Provided version not available")
   sys.exit()
#print(large_ver)
list = sorted(large_ver)
version = list[0]
#print(version)

basecmd = 'helm install ako '+harbor+'/chartrepo/registry/charts/ako-'+version+'.tgz --create-namespace -n avi-system -f values.yaml --set avicredentials.username="" --set avicredentials.password="" --wait --insecure-skip-tls-verify --kubeconfig '+file
#print(basecmd)

sp=subprocess.run(basecmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
#rc=sp.wait()
#output,error = sp.communicate()
#print(sp)
if sp.returncode == 0:
    #print(sp.stdout)
    print("AKO Operator installation.....SUCCESS")
else:
    print("AKO Operator installation.....FAILED")
    print(sp.stderr)
    sys.exit(1)
