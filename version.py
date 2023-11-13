import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Script for Cluster Componets Validation')
parser.add_argument('-p1', '--build',required=True, help="Build ID")
parser.add_argument('-p2', '--user',required=True, help="Host username")
parser.add_argument('-p3', '--passwd',required=True, help="Host Password")
parser.add_argument('-p4', '--nf',required=True, help="NF Name")
parser.add_argument('-p5', '--host',required=True, help="Host IP")
parser.add_argument('-p6', '--wuser',required=True, help="Web Username")
parser.add_argument('-p7', '--wpasswd',required=True, help="Web Password")
parser.add_argument('-p8', '--wurl',required=True, help="Web URL")
args = parser.parse_args()

BUILD = args.build
user = args.user
passwd = args.passwd
nf = args.nf
host = args.host
web_user = args.wuser
web_pass = args.wpasswd
web_url = args.wurl

CMD="export ROBOT_OPTIONS=\"--outputdir /report/"+BUILD+"/version_reports --suitestatlevel 2\";robot -v username:"+user+" -v password:"+passwd+" -v nf:"+nf+" -v host:"+host+" -v web_user:"+web_user+" -v web_pass:"+web_pass+" -v web_url:"+web_url+" Version_Checks.robot"

out=os.system(CMD)
if out != 0:
    print("Error")
    print("Reports can view here http://iserver/"+BUILD+"/version_reports/report.html")
    sys.exit(1)
else:
    print("Reports can view here http://server/"+BUILD+"/version_reports/report.html")
    sys.exit(0)
