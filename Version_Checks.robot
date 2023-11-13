*** Settings ***
Documentation      Robot Framework for Component Validation
Library            SSHLibrary
Library            Compare.py
Library		   Process
#Suite Setup	   SSH Connection	${username}	${password}
#Suite Teardown     Close All Connections
*** Variables ***
${nf}		   Test3
${web_user}        adm
${web_pass}        pas
${web_url}         http://api-service.requirements.svc.cluster.local:8080

*** Test Cases ***

fetch values from portal
    ${result}=		Run Process		python3		platform.py	${web_user}	${web_pass}	 ${web_url}	${nf}
    Log			${result.stdout}
    ${out}=		evaluate        json.loads('''${result.stdout}''')    json
#    Log			${out['etcd']}
    Set Suite Variable    ${output}    ${out}

SSH Connection
    Open Connection     ${host}        alias=${alias}
    Login               ${username}    ${password}    delay=1

Validate ETCD version
    Skip If		"${output['etcd']}" == "0.0"	msg="ETCD is not in required check"
    ${etcd_pod}=         Execute Command    kubectl get pod -n kube-system |grep etcd|head -1|awk '{print $1}'
    ${etcd}=		Execute Command		kubectl get pod ${etcd_pod} -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'
    Should Be True	"${etcd}" != ""		msg="ETCD is not found"
    ${etcd_out}=		version compare		${etcd}        ${output['etcd']}
    Log 		${etcd}
    Should Be True		${etcd_out} >= 0	msg="Installed ETCD version is lower than required"

Validate CoreDNS version
    Skip If             "${output['core']}" == "0.0"  msg="CoreDNS is not in required check"
    ${core_pod}=         Execute Command    kubectl get pod -n kube-system |grep coredns|head -1|awk '{print $1}'
    ${core}=            Execute Command         kubectl get pod ${core_pod} -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'
    Should Be True      "${core}" != ""         msg="CoreDNS is not found"
    ${core_out}=                version compare         ${core}        ${output['core']}
    Log                 ${core}
    Should Be True              ${core_out} >= 0        msg="Installed CoreDNS version is lower than required"

Validate Multus version
    Skip If             "${output['mul']}" == "0.0"  msg="Multus is not in required check"
    ${multus_pod}=         Execute Command    kubectl get pod -n kube-system |grep multus|head -1|awk '{print $1}'
    ${multus}=            Execute Command         kubectl get pod ${multus_pod} -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"-\" -f 1|sed 's/v//g'
    Should Be True      "${multus}" != ""         msg="Multus is not found"
    ${multus_out}=                version compare         ${multus}        ${output['mul']}
    Log                 ${multus}
    Should Be True              ${multus_out} >= 0        msg="Installed Multus version is lower than required"

Validate Calico version
    Skip If             "${output['calico']}" == "0.0"  msg="Calico is not in required check"
    ${calico_pod_no}=         Execute Command    kubectl get pod -n kube-system |grep -i calico| wc -l
    Should Be True	${calico_pod_no} > 0	msg="Calico is not found"
    ${calico}=            Execute Command         calicoctl --allow-version-mismatch version | head -3 | tail -1 | cut -d \":\" -f 2 |sed 's/ //g'
    Should Be True      "${calico}" != ""         msg="Calico is not found"
    ${calico_out}=                version compare         ${calico}        ${output['calico']}
    Log                 ${calico}
    Should Be True              ${calico_out} >= 0        msg="Installed Calico version is lower than required"

Validate API version
    Skip If             "${output['apiversion']}" == "0.0"  msg="API Server is not in required check"
    ${api_pod}=         Execute Command    kubectl get pod -n kube-system |grep apiserver|head -1|awk '{print $1}'
    ${api}=            Execute Command         kubectl get pod ${api_pod} -n kube-system -o jsonpath='{.spec.containers[*].image}'|cut -d \":\" -f 2|cut -d \"_\" -f 1|sed 's/v//g'
    Should Be True      "${api}" != ""         msg="API Server is not found"
    ${api_out}=                version compare         ${api}        ${output['apiversion']}
    Log                 ${api}
    Should Be True              ${api_out} >= 0        msg="Installed API Server version is lower than required"

Validate Kubernets version
    Skip If             "${output['kubernetes']}" == "0.0"  msg="Kubernetes Version is not in required check"
    ${kube}=         Execute Command    kubectl version --short=true | tail -1 | cut -d ":" -f2 |cut -d "+" -f 1|sed 's/ v//g'
    Should Be True      "${kube}" != ""         msg="Kubernetes cluster is not stable"
    ${kube_out}=                version compare         ${kube}        ${output['kubernetes']}
    Log                 ${kube}
    Should Be True              ${kube_out} >= 0        msg="Installed Kubernetes Cluster version is lower than required"

Validate Helm version
    Skip If             "${output['helm']}" == "0.0"  msg="Helm Version is not in required check"
    ${helm}=         Execute Command    helm version --short | cut -d \"+\" -f 1|sed 's/v//g'
    Should Be True      "${helm}" != ""         msg="Helm is not found"
    ${helm_out}=                version compare         ${helm}        ${output['helm']}
    Log                 ${helm}
    Should Be True              ${helm_out} >= 0        msg="Installed Helm version is lower than required"

Validate Kernal version
    Skip If             "${output['kernel']}" == "0.0"  msg="Kernal Version is not in required check"
    ${kernal}=         Execute Command    uname -r | cut -d \"-\" -f1
    Should Be True      "${kernal}" != ""         msg="Kernal is not found"
    ${kernal_out}=                version compare         ${kernal}        ${output['kernel']}
    Log                 ${kernal}
    Should Be True              ${kernal_out} >= 0        msg="Installed Kernal version is lower than required"

Validate Containerd version
    Skip If             "${output['containerd']}" == "0.0"  msg="Containerd Version is not in required check"
    ${containerd}=         Execute Command    sudo crictl version | tail -2 | head -1 | cut -d ":" -f 2|sed 's/ v//g'
    Should Be True      "${containerd}" != ""         msg="Containerd is not found"
    ${containerd_out}=                version compare         ${containerd}        ${output['containerd']}
    Log                 ${containerd}
    Should Be True              ${containerd_out} >= 0        msg="Installed Containerd version is lower than required"

Validate ISTIO version
    Skip If             "${output['istio']}" == "0.0"  msg="ISTIO Version is not in required check"
    ${istio}=         Execute Command    helm ls -n istio-system | grep istio-base | awk '{print $10}'
    Should Be True      "${istio}" != ""         msg="ISTIO is not found"
    ${istio_out}=                version compare         ${istio}        ${output['istio']}
    Log                 ${istio}
    Should Be True              ${istio_out} >= 0        msg="Installed ISTIO version is lower than required"

Close session
    Close All Connections


