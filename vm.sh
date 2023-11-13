#!/bin/bash
user=$1
pass=$2
vc=$3
task=$4
makesession=`curl -s -k -X POST https://$vc/rest/com/vmware/cis/session -u  $user:$pass`

if [[ "$makesession" =~ \{\"value.?* ]]; then
sessionid=`echo $makesession  | awk -F\" '{print $(NF-1)}'`
else
echo "Error: Can not connect to vcenter"
exit 1
fi
if [ $task == "folder" ];then
curl -s -k -X GET -H "vmware-api-session-id: $sessionid" "https://$vc/rest/vcenter/folder"|/tmp/bareprd/jq -r '.value[].name'|sort -fr
elif [ $task == "network" ];then
curl -s -k -X GET -H "vmware-api-session-id: $sessionid" "https://$vc/rest/vcenter/network"|/tmp/bareprd/jq -r '.value[].name'
elif [ $task == "rpool" ];then
curl -s -k -X GET -H "vmware-api-session-id: $sessionid" "https://$vc/rest/vcenter/resource-pool"|/tmp/bareprd/jq -r '.value[].name'
fi
