import requests
import json
import argparse

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Fetch from WebForm 
def fetchjsonfromweb(web_pass, nf, web_user, weburl, resultfile):
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
    nf_id = ""
    for i in range(len(data2['items'])):
        if (data2['items'][i]['nfName']) == nf:
            nf_id=(data2['items'][i]['assetId'])

    if(nf_id != ""):
        url2= weburl+"/jenkinsapi/assets/"+str(nf_id)
        cluster2 = requests.get(url2, headers=headers, verify=False)
        web_input = cluster2.json()
        with open(resultfile, "w") as outfile:
            json_object = json.dumps(web_input, indent = 4)
            outfile.write(json_object)
        print("Info: JSON Export complete..")
    else:
        print("Error: Provided NF does does not match with the available results..")

if __name__ == "__main__":

    # configuration of command line interface:
    parser = argparse.ArgumentParser(description='Script to extract inputs from webAPI')
    parser.add_argument('-p', '--password',required=True, help="Password for web login")
    parser.add_argument('-n', '--nfname',required=True, help="input NF name")
    parser.add_argument('-u', '--user',required=True, help="User for web login")
    parser.add_argument('-w', '--weburl',required=True, help="Webform Url")
    parser.add_argument('-o', '--outjson',required=True, help="output result JSON file to be saved from web")
    args = parser.parse_args()
    args_dict = vars(args)

    fetchjsonfromweb(args.password, args.nfname, args.user, args.weburl, args.outjson)
    print("Script processing complete...")
