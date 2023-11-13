#!/bin/bash
user=$1
pass=$2
tca=$3
task=$4
curl -s -k -o /dev/null -D /tmp/headers-bare.txt -H "Content-Type: application/json" -H "accept: application/json" -H "Accept: application/json" -X POST https://$tca/hybridity/api/sessions --data @/dev/stdin <<EOF
{ "username": "$user", "password": "$pass" }
EOF

head=`cat /tmp/headers-bare.txt|grep x-hm-authorization:|cut -d " " -f 2`

if [ $task == "mgt" ];then
curl -s -k -H "Content-Type: application/json" -H "x-hm-authorization: ${head//[$'\t\r\n ']}" -H "accept: application/json" https://$tca/hybridity/api/infra/k8s/clusters/query -d "{"filter": {"clusterType": "MANAGEMENT"}}" -X POST|/tmp/bareprd/jq -r '.[].clusterName'|sort -r
elif [ $task == "vim" ];then
curl -s -k -H "Content-Type: application/json" -H "x-hm-authorization: ${head//[$'\t\r\n ']}" -H "accept: application/json" https://$tca/hybridity/api/vims/v1/tenants |/tmp/bareprd/jq '.items[] | select(.vimType == "VC")'|/tmp/bareprd/jq -r '.hcxCloudUrl'
fi
