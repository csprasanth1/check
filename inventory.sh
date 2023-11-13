#!/bin/bash
pass=$1
task=$2
loc=$4
giturl=$3
cd /tmp
#rm -rf /tmp/inventory
#url=`echo $giturl|cut -d '/' -f3-`
#echo ${url}
#echo http://gitlab:$pass@${url} --quiet
#git clone http://gitlab:$pass@${url} --quiet
if [ $task == "loc" ];then
        rm -rf /tmp/inventory-bare
        url=`echo $giturl|cut -d '/' -f3-`
        git clone http://gitlab:$pass@${url} --quiet
	cat /tmp/inventory-bare/inventory.csv |awk -F, '{print $1}'|tail -n +2 |sort -u
elif [ $task == "tca" ];then
	awk -F, -v search="$loc" '$1==search{print $3}' /tmp/inventory-bare/inventory.csv| sed 's/"//g'|awk NF
elif [ $task == "vcenter" ];then
	awk -F, -v search="$loc" '$1==search{print $2}' /tmp/inventory-bare/inventory.csv| sed 's/"//g'
fi


