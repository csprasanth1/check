import subprocess as sp
import sys
etcd_pod=sp.getoutput("kubectl get pod -n kube-system |grep etcd|head -1|awk '{print $1}'")
coredns_pod=sp.getoutput("kubectl get pod -n kube-system |grep coredns|head -1|awk '{print $1}'")
mult_pod=sp.getoutput("kubectl get pod -n kube-system |grep multus|head -1|awk '{print $1}'")
api_pod=sp.getoutput("kubectl get pod -n kube-system |grep apiserver|head -1|awk '{print $1}'")
calico_pod=sp.getoutput("kubectl get pod -n kube-system |grep -i calico| wc -l")

etcd_version = sp.getoutput("kubectl get pod "+etcd_pod+" -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'")
coredns_version = sp.getoutput("kubectl get pod "+coredns_pod+" -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'")
multus_version = sp.getoutput("kubectl get pod "+mult_pod+" -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"-\" -f 1|sed 's/v//g'")

calico_version = sp.getoutput("calicoctl --allow-version-mismatch version | head -3 | tail -1 | cut -d \":\" -f 2 |sed 's/ //g'")
api_version = sp.getoutput("kubectl get pod "+api_pod+" -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'")

kube = sp.getoutput("kubectl version --short=true | tail -1 | cut -d \":\" -f2 |cut -d \"+\" -f 1|sed 's/ v//g' > kube.txt")
kube_version = sp.getoutput("cat kube.txt")
helm = sp.getoutput("helm version --short | cut -d \"+\" -f 1|sed 's/v//g' > helm.txt")
helm_version = sp.getoutput("cat helm.txt")
#print(helm_version)
containerd_version = sp.getoutput("sudo crictl version | tail -2 | head -1 | cut -d \":\" -f2 | sed 's/  v//g'")
kernel_version = sp.getoutput("uname -r | cut -d \"-\" -f1")
istio = sp.getoutput("helm ls -n istio-system | grep istio-base | awk '{print $10}' > istio.txt")
istio_version = sp.getoutput("cat istio.txt")
#print(helm_version)
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



etcd_web = sys.argv[1]
coredns_web = sys.argv[2]
mult_web = sys.argv[3]
calico_web = sys.argv[4]
api_web = sys.argv[5]
kube_web = sys.argv[6]
helm_web = sys.argv[7]
kernel_web = sys.argv[8]
containerd_web = sys.argv[9]
istio_web = sys.argv[10]

if etcd_version !="" and etcd_web !='0.0':
  ans = versionCompare(etcd_version, etcd_web)
  if ans < 0:
    print ("Failed.ETCD version check")
  else:
    print ("Success.ETCD version check ")
elif etcd_web != '0.0' and etcd_version == "":
   print("Failed: ETCD is not installed in cluster")
   
if coredns_web !='0.0' and coredns_version !="":	
  ans1 = versionCompare(coredns_version, coredns_web)
  if ans1 < 0:
    print ("Failed.Coredns version check")
  else:
    print ("Success.Coredns version check ")
elif coredns_web !='0.0' and coredns_version =="":
  	print("Failed: Coredns is not installed in cluster")

if mult_web != '0.0' and multus_version !="":
   ans2 = versionCompare(multus_version, mult_web)
   if ans2 < 0:
    print ("Failed.Multus version check")
   else:
    print ("Success.Multus version check ")
elif mult_web != '0.0' and multus_version == "":
   print("Failed: Multas is not installed in cluster")	
 
if int(calico_pod) > 0:
   if calico_web !='0.0' and calico_version !="":
      ans3 = versionCompare(calico_version, calico_web)
      if ans3 < 0:
        print ("Failed.Calico version check")
      else:
        print ("Success.Calico version check ")
else:
  print("Failed: Calico is not installed in cluster")

if api_web !='0.0' and api_version !="":
  ans4 = versionCompare(api_version, api_web)
  if ans4 < 0:
    print ("Failed.Api_server version check")
  else:
    print ("Success.Api_server version check ")
elif api_web !='0.0' and api_version =="":
  print("Failed: Api_server is not installed in cluster")

if kube_web !='0.0' and kube_version !="":
  ans5 = versionCompare(kube_version, kube_web)
  if ans5 < 0:
    print ("Failed.Kubernetes version check")
  else:
    print ("Success.Kubernetes version check ")
elif kube_web !='0.0' and kube_version =="":
  print("Failed: Kubernetes is not installed in cluster")
  
if helm_web !='0.0' and helm_version !="":
  ans6 = versionCompare(helm_version, helm_web)
  if ans6 < 0:
    print ("Failed.Helm version check")
  else:
    print ("Success.Helm version check ")
elif helm_web !='0.0' and helm_version =="":
  print("Failed: Helm is not installed in cluster")


if kernel_web !='0.0' and kernel_version !="":
  ans7 = versionCompare(kernel_version, kernel_web)
  if ans7 < 0:
    print ("Failed.Kernel version check")
  else:
    print ("Success.Kernel version check ")
elif kernel_web !='0.0' and kernel_version =="":
  print("Failed: Kernel is not installed in cluster")

if containerd_web !='0.0' and containerd_version !="":
  ans8 = versionCompare(containerd_version, containerd_web)
  if ans8 < 0:
    print ("Failed.Containerd version check")
  else:
    print ("Success.Containerd version check ")
elif containerd_web !='0.0' and containerd_version =="":
  print("Failed: Containerd is not installed in cluster")

if istio_web !='0.0' and istio_version !="":
  ans8 = versionCompare(istio_version, istio_web)
  if ans8 < 0:
    print ("Failed.Istio version check")
  else:
    print ("Success.Istio version check ")
elif istio_web !='0.0' and istio_version =="":
  print("Failed: Istio is not installed in cluster")
  
