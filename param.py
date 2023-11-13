import requests
import json
import sys
import argparse
import os

parser = argparse.ArgumentParser(description='Script to check Required installation')
parser.add_argument('-p1', '--field',required=True, help="Field to check")
args = parser.parse_args()
check = args.field
def data():
    file = open('TEF/capacityfinalreport/webforminput.json')
    webinput = json.load(file)
    file.close()
    return webinput

def NFS():
    web_input = data()
    for i in range(len(web_input['categories'])):
        if (web_input['categories'][i].get('categoryName')) == "capacity":
            plat_idx2=i
            break
    for n in range(len(web_input['categories'][plat_idx2]['fields'])):
        if((web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Workload") or (web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Management")):
            field_idx=n
            break
    for s in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'])):
        if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][s]['fieldName']) == "Cluster Storage details":
            csi_idx=s
            for y in range(len(web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'])):
                if (web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['fieldName'] == "Storage" and web_input['categories'][plat_idx2]['fields'][field_idx]['children'][csi_idx]['children'][y]['fieldValue'] == "nfs"):
                    return "Required"
                else:
                    return "Not Required"

def TYPE():
    web_input = data()
    for i in range(len(web_input['categories'])):
        if (web_input['categories'][i].get('categoryName')) == "capacity":
            plat_idx2=i
            break
    for n in range(len(web_input['categories'][plat_idx2]['fields'])):
        if web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Workload":
            return "Workload"
        elif web_input['categories'][plat_idx2]['fields'][n]['fieldValue'] == "Management":
            return "Management"



def cls():
    web_input = data()
    for i in range(len(web_input['categories'])):
        if (web_input['categories'][i].get('categoryName')) == "capacity":
            plat_idx2=i
            break
    for n in range(len(web_input['categories'][plat_idx2]['fields'])):
        if web_input['categories'][plat_idx2]['fields'][n]['fieldName'] == 'Cluster Instance Name':
            cluster_name = web_input['categories'][plat_idx2]['fields'][n]['fieldValue']
            return cluster_name

def istio():
    web_input = data()
    for i in range(len(web_input['categories'])):
        if (web_input['categories'][i].get('categoryName')) == "platform":
            plat_idx=i
            break
    comps=[]
    for n in range(len(web_input['categories'][plat_idx]['fields'])):
        comps.append(web_input['categories'][plat_idx]['fields'][n]['fieldName'])
    if ("Istio Version" in comps):
        return "Required"
    else:
        return "Not Required"


if check == "nfs":
    nfs = NFS()
    print(nfs)
elif check == "type":
    clstype = TYPE()
    print(clstype)
elif check == "cls":
    clsname = cls()
    print (clsname)
elif check == "istio":
    istio =  istio()
    print (istio)
