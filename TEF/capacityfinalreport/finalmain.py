"""
Script to calculate cluster space
Version: 0.0.1
Author:

Parameters
    (-w) -> Json file from web with node requirements
    (-c) -> CSV file from shell with cluster space
    (-o) -> JSON ourtput file name
    ( please use -h for command line help)

"""

import os
import argparse
import math
import json
import csv

# Define global variables for processing
InputWorkerNodePool = []
InputMasterNode = []
InputBusiness = []
InputClusterCapacity = []
InputClusterNames = []
InputClusterStorageCapacity = []

# Constant settings
ClusterReservedCapacity = 10 # Percentage of reserved cluster to leave free for calculation
MASTERNODE_FROMWEB = 1 # Set to 1 incase the master node calcualtions should be taken from web API, or the below constant is used
MasterNodeCapacity = [
            {
                "Capacity" : 10, # Capacity for <= 10
                "ReqMasterNodeCnt" : 3, # Required master node count
                "CPU": 2,
                "RAM": 8,
                "Storage": 50
            },
            {
                "Capacity" : 100, # Capacity for <= 100
                "ReqMasterNodeCnt" : 3, # Required master node count
                "CPU": 4,
                "RAM": 16,
                "Storage": 50
            },
            {
                "Capacity" : 250, # Capacity for <= 250
                "ReqMasterNodeCnt" : 3, # Required master node count
                "CPU": 8,
                "RAM": 32,
                "Storage": 50
            },
            {
                "Capacity" : 500, # Capacity for <= 500
                "ReqMasterNodeCnt" : 3, # Required master node count
                "CPU": 16,
                "RAM": 64,
                "Storage": 50
            }
]

#Result variables defintion
ResultCalculations_WN = [
    {   # Capacity Worker node pool calculated from web input json
        #"Web_NoOfWorkerNodePool" : 0,
        "WorkerNodes" : 0,
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity master nodes calculated from predefined constant
        "MasterNodes" : 0,
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity Net total worker nodes including worker node (WorkerNodePool + WorkerNode)
        "TotalReqNodes" : 0,
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    }
]
# Result to hold the final calculated cluster allocation
ResultClusters = []
ResultClustersConsolidated = []
ResultMasterNode = []
ResultWorkerNode = []
ResultUnallocatedNodes = []
ResultFreeCluster = []
# Result to dump out JSON data
ResultJSONDumpOut = {}
poolnames = []
masterpool = []
workerpool = []
worker_storage={}
exceptcls = []
storagealloc = []

# JSON Write out result
def writeresultJSON(filepath):
    # Data write results out from variables
    #ResultJSONDumpOut.update ({"Business": InputBusiness})
    #ResultJSONDumpOut.update ({"RequiredMasterNode": ResultCalculations_WN[1]})

    #Find the best cluster that has more space
    BestCluster = ""
    BestClusterCPUCap = 0
    for Cluster in ResultFreeCluster:
        if(Cluster['FreeCPU'] > BestClusterCPUCap):
            BestClusterCPUCap = Cluster['FreeCPU']
            BestCluster = Cluster['ClusterName']
    #BestCluster = "cluster2"

    # Extract only Best Cluster details
    ResultPrintLoc = []
    for Cluster in ResultFreeCluster:
        if(BestCluster == Cluster['ClusterName']):
            ResultPrintLoc.append(Cluster)
    ResultJSONDumpOut.update ({"NodeAllocation": ResultPrintLoc})

    # Extract only Best Cluster details
    ResultPrintLoc = []
    for Cluster in ResultMasterNode:
        if(BestCluster == Cluster['ClusterName']):
            ResultPrintLoc.append(Cluster)
    ResultJSONDumpOut.update ({"MasterNodeAllocation": ResultPrintLoc})

    # Extract only Best Cluster details
    ResultPrintLoc = []
    for Cluster in ResultfinalWorkerNode:
        if(BestCluster == Cluster['ClusterName']):
            ResultPrintLoc.append(Cluster)
    ResultJSONDumpOut.update ({"WorkerNodeAllocation": ResultPrintLoc})
    # Extract only Best Cluster details for storage
    ResultPrintLoc = []
    for Cluster in storagealloc:
        for pool in masterpool:
            if(BestCluster == Cluster['ClusterName'] and Cluster['AllocatedNode']) == pool:
                ResultPrintLoc.append(Cluster)
    ResultJSONDumpOut.update ({"MasterNodeStorageAllocation": ResultPrintLoc})

    # Extract only Best Cluster details for storage
    ResultPrintLoc = []
    for Cluster in storagealloc:
        for pool in workerpool:
            if(BestCluster == Cluster['ClusterName'] and Cluster['AllocatedNode']) == pool:
                ResultPrintLoc.append(Cluster)
    ResultJSONDumpOut.update ({"WorkerNodeStorageAllocation": ResultPrintLoc})


    with open(filepath, "w") as outfile:
        json_object = json.dumps(ResultJSONDumpOut, indent = 4)
        outfile.write(json_object)


# JSON parser to read WorkerNodePool details
def readjsonwebform(filpath):
    filejson = open(filpath,)
    data = json.load(filejson)
    WorkerNode = {}
    MasterNode = {}
    #InputBusiness.append (data['Business'])

    #Look for Field Capacity
    for field in data['categories']:
        if(field['categoryName'] == "capacity"):
            capacitydata = field['fields']

    for field in capacitydata:
        if(field['fieldName'] == "Cluster Instance Name"):
            ClusterInstanceName = field['fieldValue']
        if(field['fieldName'] == "Cluster type" and (field['fieldValue'] == "Workload" or field['fieldValue'] == "Management")):
                        if "children" in field.keys():
                            #print(Clustertypesfield['children'])
                            for NodeTypefield in field['children']:   ##103
                                #print(NodeTypefield)
                                #print("%%%%%%%%%%%%%%%%%%%%%%")
                                # Find for Worker nodes
                                #print(NodeTypefield['children'])
                                #print("%%%%%%%%%%%%%%%%%%%%%%")
                                if(NodeTypefield['children'][0]['fieldName'] == "Node Pool Type" and NodeTypefield['children'][0]['fieldValue'] == "Worker"):
                                    #print(NodeTypefield["children"])
                                    #print("%%%%%%%%%%%%%%%%%%%%%%")
                                    #print("worker is")
                                    WorkerNode = {}
                                    Storage1 = 0
                                    Storage2 = 0
                                    if "children" in NodeTypefield.keys():
                                        for Nodes in NodeTypefield['children']:
                                            #print(Nodes)

                                            #WorkerNode = {}
                                            # Loop through all node pools and extract data
                                            #if(NodePoolfield['fieldName'] == "Node Pool"):
                                                #if "children" in NodePoolfield.keys():
                                                   # WorkerNode.clear
                                            #Storage1 = 0
                                            #Storage2 = 0
                                            #for Nodes in NodePoolfield['children']:
                                            if(Nodes['fieldName'] == "Number of Replica"): WorkerNode.update ({"Nodecount": int(Nodes['fieldValue'])})
                                            if(Nodes['fieldName'] == "Node Pool Name"): WorkerNode.update ({"NodeName": Nodes['fieldValue']})
                                            if(Nodes['fieldName'] == "Node Pool CPU (vCPUs)"): WorkerNode.update ({"NodeCPU": int(Nodes['fieldValue'])})
                                            if(Nodes['fieldName'] == "Node Memory (MB)"): WorkerNode.update ({"NodeRAM": int(Nodes['fieldValue'])/1024})
                                            if(Nodes['fieldName'] == "Node Storage (GB)"): Storage1 = int(Nodes['fieldValue'])
                                            if(Nodes['fieldName'] == "Node Persistent Storage (GBi)"): Storage2 = int(Nodes['fieldValue'])
                                    WorkerNode.update ({"NodeStorage": Storage1 + Storage2})
                                    InputWorkerNodePool.append (WorkerNode)

                                    #print(WorkerNode)
                                #############################################################################################                                
                                # Find for Master nodes
                                if(NodeTypefield['children'][0]['fieldName'] == "Node Pool Type" and NodeTypefield['children'][0]['fieldValue'] == "Master"):

                                    MasterNode.clear
                                    Storage1 = 0
                                    Storage2 = 0
                                    if "children" in NodeTypefield.keys():
                                        for Nodes in NodeTypefield['children']:
                                            # Loop through all node pools and extract data
                                            #if(NodePoolfield['fieldName'] == "Node Pool"):
                                                #if "children" in NodePoolfield.keys():
                                                    #MasterNode.clear
                                                    #Storage1 = 0
                                                    #Storage2 = 0
                                                    #for Nodes in NodePoolfield['children']:
                                            if(Nodes['fieldName'] == "Number of Replica"): MasterNode.update ({"ReqMasterNodeCnt": int(Nodes['fieldValue'])})
                                            if(Nodes['fieldName'] == "Node Pool Name"): MasterNode.update ({"NodeName": Nodes['fieldValue']})
                                            if(Nodes['fieldName'] == "Node Pool CPU (vCPUs)"): MasterNode.update ({"CPU": int(Nodes['fieldValue'])})
                                            if(Nodes['fieldName'] == "Node Memory (MB)"): MasterNode.update ({"RAM": int(Nodes['fieldValue'])/1024})
                                            if(Nodes['fieldName'] == "Node Storage (GB)"): Storage1 = int(Nodes['fieldValue'])
                                            if(Nodes['fieldName'] == "Node Persistent Storage (GBi)"): Storage2 = int(Nodes['fieldValue'])
                                    MasterNode.update ({"Storage": Storage1 + Storage2})
                                    InputMasterNode.append (MasterNode)
    print(InputWorkerNodePool)
    print(InputMasterNode)
    filejson.close()

# Read Cluster capacity details from csv file
def readcsvclustercapacity(filpath):
    with open(filpath, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader) # Read field names, but its not used at the moment
        for row in csvreader:
            InputClusterCapacity.append(row)
            if((row[0] not in InputClusterNames) and (len(row[0]) > 0)): # Collect Cluster names (unique only)
                InputClusterNames.append (row[0])
    # Reserved capacity divider
    ClusterReservedCapacity_Divider = 0.9
    #print(InputClusterCapacity)
    for cluster in InputClusterCapacity:
        if (len(cluster[0]) == 0):
            continue
        cluster[2] = math.floor(float(cluster[2]) * ClusterReservedCapacity_Divider) #Excel Col-3 Free CPU, reduce 10% as buffer and round down
        cluster[3] = math.floor(float(cluster[3]) * ClusterReservedCapacity_Divider) #Excel Col-4 Free RAM, reduce 10% as buffer and round down
        #cluster[4] = math.floor(float(cluster[4]) * ClusterReservedCapacity_Divider) #Excel Col-5 Free Memory, reduce 10% as buffer and round down
        #cluster[5] = cluster[5] #Excel Col-6 Datastorev name
    #print("InputClusterNames")
    #print(InputClusterNames)


# Calculate WorkerNode
def calculate_workernode():

    # Calculate required worker nodes from worker node pool
    for WorkerNode in InputWorkerNodePool:
        #ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] = ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] + 1
        ResultCalculations_WN[0]['WorkerNodes'] = ResultCalculations_WN[0]['WorkerNodes'] + WorkerNode['Nodecount']
        ResultCalculations_WN[0]['CPU'] = ResultCalculations_WN[0]['CPU'] + (WorkerNode['Nodecount'] * WorkerNode['NodeCPU'])
        ResultCalculations_WN[0]['RAM'] = ResultCalculations_WN[0]['RAM'] + (WorkerNode['Nodecount'] * WorkerNode['NodeRAM'])
        #ResultCalculations_WN[0]['Storage'] = ResultCalculations_WN[0]['Storage'] + (WorkerNode['Nodecount'] * WorkerNode['NodeStorage'])

    if(MASTERNODE_FROMWEB == 1): #Settings if the master node calculation should be taken from the web API JSON
        ResultCalculations_WN[1]['MasterNodes'] = InputMasterNode[0]['ReqMasterNodeCnt']
        ResultCalculations_WN[1]['CPU'] = InputMasterNode[0]['CPU']
        ResultCalculations_WN[1]['RAM'] = InputMasterNode[0]['RAM']
        #ResultCalculations_WN[1]['Storage'] =  InputMasterNode[0]['Storage']
    else:
        # Calculate required Master Node from required workernodes based on internal constant
        for MasterNodeConst in MasterNodeCapacity:
            if (ResultCalculations_WN[0]['WorkerNodes'] <= MasterNodeConst['Capacity']):
                ResultCalculations_WN[1]['MasterNodes'] = MasterNodeConst['ReqMasterNodeCnt']
                ResultCalculations_WN[1]['CPU'] = MasterNodeConst['CPU']
                ResultCalculations_WN[1]['RAM'] = MasterNodeConst['RAM']
                #ResultCalculations_WN[1]['Storage'] = MasterNodeConst['Storage']
                break


    # Calculate consolidated net capacity requirement
    ResultCalculations_WN[2]['TotalReqNodes'] = ResultCalculations_WN[0]['WorkerNodes'] + ResultCalculations_WN[1]['MasterNodes']
    ResultCalculations_WN[2]['CPU'] = ResultCalculations_WN[0]['CPU'] + ResultCalculations_WN[1]['CPU']
    ResultCalculations_WN[2]['RAM'] = ResultCalculations_WN[0]['RAM'] + ResultCalculations_WN[1]['RAM']
    #ResultCalculations_WN[2]['Storage'] = ResultCalculations_WN[0]['Storage'] + ResultCalculations_WN[1]['Storage']
    #print("ResultCalculations_WN")
    #print(ResultCalculations_WN)
################################# Changes#################################################
def calculate_nodepool():
    #master_storage={}
    for Node in InputWorkerNodePool:
        worker_storage.update ({Node['NodeName']: int(Node['Nodecount']) * int(Node['NodeStorage'])})
        poolnames.append(Node['NodeName'])
        workerpool.append(Node['NodeName'])
    for Node in InputMasterNode:
        worker_storage.update ({Node['NodeName']: int(Node['ReqMasterNodeCnt']) * int(Node['Storage'])})
        poolnames.append(Node['NodeName'])
        masterpool.append(Node['NodeName'])
    #print("master_storage")
    #print(master_storage)
    #print("worker_storage")
    #print(worker_storage)
    #print(poolnames)
    #print(masterpool)
    #print(workerpool)

#InputClusterStorageCapacity = []
def readcsvclustercStorageapacity(filpath):
    with open(filpath, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader) # Read field names, but its not used at the moment
        for row in csvreader:
            #print(row)
            InputClusterStorageCapacity.append(row)
            #print(InputClusterStorageCapacity)
        ClusterReservedCapacity_Divider = 0.9
    for storage in InputClusterStorageCapacity:
        if (len(storage[0]) == 0):
            continue
        storage[1] = math.floor(float(storage[1]) * ClusterReservedCapacity_Divider) #Excel Col-3 Free CPU, reduce 10% as buffer and round down
def checkstoragecapacity(ClusterName, DSList, WorkerNodeName, Nodepoolstorage, exceptlist, storealloc):
    # find space for Node Pools
            #print(ClusterName)
            #print(WorkerNodeName)
            #print(finalcls)
            #print(DSList)

            StorageRes = {}
            # Loop through all clustres and check if capacity is possible
            for storage in DSList:
                #print("storage")
                #print(storage)
                # skip processing if cluster name or row is empty or if it was already allocated
                if (len(storage[0]) == 0):
                    continue

                # Check space only from the specified cluster
                if (storage[0] != ClusterName):
                    continue

                # Skip if host was already allocated
                #if (len(cluster[1]) == 0):
                    #continue

                StorageActCAP = float(storage[1])    #Excel Col-5 Free Memory, reduce 10% as buffer and round down

                if(Nodepoolstorage <= StorageActCAP):
                    #print(storage)
                    StorageRes.update ({"ClusterName": storage[0]})
                    StorageRes.update ({"AllocatedNode": WorkerNodeName})
                    StorageRes.update ({"Datastore": storage[2]})
                    storealloc.append(StorageRes)
                    #cluster[1] = "" # Invalidate so no other Node can be allocated here
                    storage[1] = StorageActCAP - Nodepoolstorage
                    #print("StorageRes")
                    #print(StorageRes)

                    break
            #print("StorageRes")
            #print(StorageRes)
            if("AllocatedNode" not in StorageRes):
                unallocRes = {}
                unallocRes.update ({"NodeName": WorkerNodeName})
                unallocRes.update ({"ClusterName": ClusterName})
                if ClusterName not in exceptlist:
                    exceptlist.append(ClusterName)
                #print(finalcls)
                #finalcls.remove(ClusterName)
                #print("unallocRes")
                #print(unallocRes)
##########################################################################################

# check Cluster Capacity
def checkclustercapacity(ClusterName,ClusterList, ResultUnallocatedNodes, WorkerNodeName, WorkerCPU, WorkerRAM, NodeCount, ResultList):
    # find space for Worker Nodes
            ClustersRes = {}
            # Loop through all clustres and check if capacity is possible
            for cluster in ClusterList:
                #print("cluster")
                #print(cluster)
                # skip processing if cluster name or row is empty or if it was already allocated
                if (len(cluster[0]) == 0):
                    continue

                # Check space only from the specified cluster
                if (cluster[0] != ClusterName):
                    continue

                # Skip if host was already allocated
                if (len(cluster[1]) == 0):
                    if (cluster[4] == WorkerNodeName):
                        continue


                ClusterActCPU = float(cluster[2])    #Excel Col-3 Free CPU, reduce 10% as buffer and round down
                ClusterActRAM = float(cluster[3])    #Excel Col-4 Free RAM, reduce 10% as buffer and round down
                #ClusterActCAP = float(cluster[4])    #Excel Col-5 Free Memory, reduce 10% as buffer and round down
                #print(ClusterActCPU,ClusterActRAM)
                if((WorkerCPU <= ClusterActCPU) and (WorkerRAM <= ClusterActRAM)):
                    ClustersRes.update ({"ClusterName": cluster[0]})
                    ClustersRes.update ({"HostName": cluster[1]})
                    ClustersRes.update ({"AllocatedNode": WorkerNodeName})
                    ClustersRes.update ({"AllocatedNodeCount": NodeCount})
                    #ClustersRes.update ({"Datastore": cluster[5]})
                    ResultList.append (ClustersRes)
                    #print("ClustersRes")
                    #print(ClustersRes)
                    cluster[1] = "" # Invalidate so no other Node can be allocated here
                    cluster[2] = ClusterActCPU - WorkerCPU
                    cluster[3] = ClusterActRAM - WorkerRAM
                    if len(cluster) == 4:
                        cluster.append(WorkerNodeName)
                    else:
                        cluster[4] = WorkerNodeName

                    break

            # Check if we have unallocated Nodes
            if("AllocatedNode" not in ClustersRes):
                unallocRes = {}
                unallocRes.update ({"NodeName": WorkerNodeName})
                unallocRes.update ({"NodeCount": NodeCount})
                ResultUnallocatedNodes.append (unallocRes)


if __name__ == "__main__":

    # configuration of command line interface:
    parser = argparse.ArgumentParser(description='Script for parsing POD details using JSON outputs')
    parser.add_argument('-w', '--webjson',required=True, help="path to json file from web input")
    parser.add_argument('-c', '--clustcsv',required=True, help="path to excel file with cluster free capacity")
    parser.add_argument('-s', '--dscsv',required=True, help="path to excel file with storage free capacity")
    parser.add_argument('-o', '--outfile', help="path to output file to write the results")
    args = parser.parse_args()
    args_dict = vars(args)

    print ("Calculating Cluster capacity with " + str(ClusterReservedCapacity) + " percent reserverd capacity...")
    #Read inputs JSON + CSV files
    readjsonwebform(args.webjson)
    readcsvclustercapacity(args.clustcsv)
    readcsvclustercStorageapacity(args.dscsv)

    #Calcualtions
    calculate_workernode()
    calculate_nodepool()
    #print(InputClusterStorageCapacity)
    ########################### Changes#########################
    #print(InputClusterNames)
    #storage_clusters = (InputClusterNames)
    for ClusterName in InputClusterNames:
        DSList = (InputClusterStorageCapacity)
        #print(DSList)
        #print(poolnames)
        for pool in poolnames:
            checkstoragecapacity(ClusterName, DSList, pool, worker_storage[pool], exceptcls, storagealloc)
        #print("exceptcls")
        #print(exceptcls)
    #print(InputClusterNames)
    clslist = []
    for cls in InputClusterNames:
        #print(cls)
        if cls not in exceptcls:
            clslist.append(cls)
    #print(clslist)
    #print(storagealloc)



    ###########################################################






    print ("-----------------------------------------------------------------------")
    print ("Required Master Nodes:")
    print(ResultCalculations_WN[1])

    # Find capacity for Master Node

    InputClusterNames = (clslist)
    for ClusterName in InputClusterNames:
        print ("-----------------------------------------------------------------------")
        print ("Allocation for Cluster: " + ClusterName)

        ResultUnallocatedMasterNodes = []
        ResultUnallocatedWorkerNodes = []
        ClusterList = (InputClusterCapacity)
        for MasterCount in range(ResultCalculations_WN[1]['MasterNodes']):
            checkclustercapacity(ClusterName,ClusterList,ResultUnallocatedMasterNodes,"MasterNode",ResultCalculations_WN[1]['CPU'],ResultCalculations_WN[1]['RAM'],MasterCount,ResultMasterNode)
        #print(ResultMasterNode)

        for WorkerNode in InputWorkerNodePool:
            for NodeCount in range(WorkerNode['Nodecount']):
                checkclustercapacity(ClusterName,ClusterList,ResultUnallocatedWorkerNodes,WorkerNode['NodeName'],WorkerNode['NodeCPU'],WorkerNode['NodeRAM'],NodeCount,ResultWorkerNode)
        #print(ResultWorkerNode)

        # Print unallocated Master and worker nodes per cluster
        print ("---------------------------------------")
        print ("Unallocated Master Nodes: ")
        for ResultUnallocatedMasterNode in ResultUnallocatedMasterNodes:
            print (ResultUnallocatedMasterNode['NodeName'] + "    " + str(ResultUnallocatedMasterNode['NodeCount']))

        print ("---------------------------------------")
        print ("Unallocated Worker Nodes: ")
        for ResultUnallocatedWorkerNode in ResultUnallocatedWorkerNodes:
            print (ResultUnallocatedWorkerNode['NodeName'] + "    " + str(ResultUnallocatedWorkerNode['NodeCount']))

        # Print unallocated clusters
        print ("---------------------------------------")
        print ("Unallocated ESXI in clusters: ")
        for freecluster in ClusterList:
            if((len(freecluster[1]) != 0) and (freecluster[0] == ClusterName)):
                print (freecluster[0] + "  " + freecluster[1])

        # Print consolidated result
        if(ResultUnallocatedMasterNodes) or (ResultUnallocatedWorkerNodes):
            ResultClustersConsolidated.append ((ClusterName + "   -   No Capacity"))
        else:
            FreeClustdetails = {}
            ClusterFreeCPU = 0
            for cluster in ClusterList: #Calculate avialable CPU after allocation
                if (cluster[0] != ClusterName):
                    continue
                ClusterFreeCPU = ClusterFreeCPU + cluster[2]
            FreeClustdetails.update ({"ClusterName": ClusterName})
            FreeClustdetails.update ({"FreeCPU": ClusterFreeCPU})
            ResultFreeCluster.append (FreeClustdetails)
            ResultClustersConsolidated.append ((ClusterName + "   -   Has Capacity => FreeCPU " + str(ClusterFreeCPU)))
            HasCapResult = 1
    #print("ResultMasterNode")
    #print(ResultMasterNode)
    #print("ResultWorkerNode")
    #print(ResultWorkerNode)
    '''
    ResultfinalWorkerNode = []
    dumpcls = []
    for cls in ResultWorkerNode:
        if cls['AllocatedNode'] in dumpcls and cls['ClusterName'] in dumpcls:
            continue
        else:
            dumpcls.append(cls['AllocatedNode'])
            ResultfinalWorkerNode.append(cls)
    print("ResultfinalWorkerNode")
    print(ResultfinalWorkerNode)
    '''
    ResultfinalWorkerNode=(ResultWorkerNode)
    #Write result
    writeresultJSON(args.outfile)
    print ("-----------------------------------------------------------------------")
    print ("-----------------------------------------------------------------------")
    print ("Consolidated Result: ")
    for ConsRes in ResultClustersConsolidated:
        print (ConsRes)

    print("Script processing complete...")
    print(HasCapResult)
    if HasCapResult > 0:
        exit(0)
    else:
        exit(0)


