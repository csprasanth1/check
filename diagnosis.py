import requests
import time
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


tcauser = sys.argv[1]
tcapass = sys.argv[2]
tca = sys.argv[3]
cluster = sys.argv[4]
mgt = sys.argv[5]
build = sys.argv[6]
fold = "/report/"+build+"/diagnosis_reports"
######## Fetch Session ID #############
url = "https://"+tca+"/hybridity/api/sessions"
data = {
  "username": tcauser,
  "password": tcapass
}
response = requests.post(url, json=data, verify=False)
out=response.headers["x-hm-authorization"]
headers_tca={'x-hm-authorization': out}
datamgt = {"clusters": [{"clusterName": cluster}],"caseSelectors":["pre-upgrade","etcd","cni","csi","ntp"]}

####### Fetch mgtid ###################
url1="https://"+tca+"/hybridity/api/infra/k8s/clusters/query"
datamgt = {
         "filter": {
             "clusterType": "MANAGEMENT"
             }
        }
clustermgt = requests.post(url1, json=datamgt, headers=headers_tca, verify=False)
outputmgt=clustermgt.json()
mgtcheck=0
for i in range(len(outputmgt)):
    if outputmgt[i]['clusterName'] == mgt:
        mgtid = outputmgt[i]['id']
        mgtcheck=1
        break
if mgtcheck == 0:
    print("Management Cluster ID is missing")
    sys.exit(1)


######## Run Scan #########################
url1 = "https://"+tca+"/telco/api/caas/v2/diagnosis?managementClusterId="+mgtid
datamgt = {"clusters": [{"clusterName": cluster}],"caseSelectors":["pre-upgrade","etcd","cni","csi","ntp"]}
clustermgt = requests.post(url1, json=datamgt, headers=headers_tca, verify=False)
if clustermgt.status_code != 201:
    print("Error in trigger")
    exit(1)
else:
    print("Diagnose scan triigered on cluster")
############### Verify the Output##############
url2="https://"+tca+"/telco/api/caas/v2/diagnosis/result?managementClusterId="+mgtid
timeout = time.time() + 60*45  # 45 minutes from now
n = 10
TEST = 0
while True:
    clusterout = requests.post(url2, json=datamgt, headers=headers_tca, verify=False)
    output=clusterout.json()
    STAT = output["status"]["overallStatus"]

    if STAT == "PASS":
        print ("Scan Completed.......Success")
        break
    elif time.time() > timeout:
        print ("Cluster is taking time...Please check")
        sys.exit(1)
        break

    elif STAT == "IN_PROGRESS":
        print ("Scanning is in progress....Will wait for "+str(n)+" minutes")
        time.sleep(10)
        n = n - 1
    elif STAT != "PASS" or STAT != "IN_PROGRESS" :
        print ("Scan Completed.......Failed")
        TEST = 1
        break




######### Download Report ########################
url3 = "https://"+tca+"/telco/api/caas/v2/diagnosis/result/download?managementClusterId="+mgtid
r = requests.post(url3, json=datamgt, headers=headers_tca, verify=False, allow_redirects=True)
open('result.tar.gz', 'wb').write(r.content)
#cmd="mkdir "+fold
#os.system(cmd)
cmd1 = "tar xzmf result.tar.gz --no-same-owner -C "+fold 
os.system(cmd1)
cmd2 = "cat "+fold+"/"+cluster+"-diagnosis.log"
print("Please see results below")
os.system(cmd2)
print("Reports can view here.....")
print("http://server/"+build+"/diagnosis_reports/report.html")

if TEST == 1:
    print ("Please check the cluster as alll components are not UP")
    sys.exit(1)
