#!/bin/bash
#export https_proxy=
#export http_proxy=
pass=$2
user=$1
weburl=$3
export NO_PROXY=$weburl
#pass=$2
#user=$1
access=`curl -s -k -H "Content-Type: application/json"  -X POST $weburl/login --data @/dev/stdin<<EOF 
{ "usernameOrEmail": "$user", "password": "$pass" }
EOF`
tok=`echo $access |/tmp/bareprd/jq -r '.accessToken'`
curl -s -k -H "Accept: application/json" -H "Authorization: Bearer ${tok}" $weburl/jenkinsapi/assets -X GET |/tmp/bareprd/jq '.items[] | select(.type == "CNF")| select(.platform == "vmware")'|/tmp/bareprd/jq -r '.nfName'
