#working with json to sto fetch NFS and NST are required or not from NF form##
$json = Get-Content -Raw -Path "TEF/capacityfinalreport/webforminput.json" | ConvertFrom-Json

#checking NFS status
$NFS = $false
foreach($category in $json.categories)
    {
    if($category.categoryName -eq "capacity")
        {
        #Write-Host $category.categoryName
        foreach($field in $category.fields)
            {
            foreach($child in $field.children)
                {
                #Write-Host $child.fieldName
                if($child.fieldName -eq "Cluster Storage details")
                    {
                    #Write-Host $child.fieldName
                    foreach($grandchild in $child.children)
                    {
                    #Write-Host $grandchild.fieldName
                    if($grandchild.fieldValue -eq "nfs" -or $grandchild.fieldValue -eq "both" ){
                        $NFS = $true
                        #Write-Output $NFS
                        }
                    }
                }
            }
        }
    }
}

Write-Host "NFS status is $NFS"

##checking NST status
$NSX = $false
foreach($category in $json.categories)
    {
    if($category.categoryName -eq "capacity")
        {
        #Write-Host $category.categoryName
        foreach($field in $category.fields)
            {
            foreach($child in $field.children)
                {
                #Write-Host $child.fieldName
                if($child.fieldName -eq "Cluster Networking details")
                    {
                    #Write-Host $child.fieldName
                    foreach($grandchild in $child.children)
                        {
                        #Write-Host $grandchild.fieldName
                        if($grandchild.fieldName -eq "Network Infrastructure configuration"){
                            #Write-Host $grandchild.fieldName
                            foreach($subchild in $grandchild.children)
                                {
                                #Write-Host $subchild.fieldName
                                if($subchild.fieldName -eq "Tier1 name")
                                    {
                                    $tier1 = $subchild.fieldValue
                                    #Write-Host $tier1
                                    if(![string]::IsNullOrWhiteSpace($tier1))
                                        {
                                        $NSX = $true
                                        #Write-Host $NSXT
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

Write-Host "NSXT Status is $NSX "

#working with json to store the nfs input from NF form##

foreach($category in $json.categories)
    {
    if($category.categoryName -eq "capacity")
        {
        #Write-Host $category.categoryName
        foreach($field in $category.fields)
            {
            foreach($child in $field.children)
                {
                #Write-Host $child.fieldName
                if($child.fieldName -eq "Cluster Storage details")
                    {
                    #Write-Host $child.fieldName
                    foreach($grandchild in $child.children)
                        {
                        #Write-Host $grandchild.fieldName
                        if($grandchild.fieldName -eq "NFS Storage configuration"){
                        foreach($subchild in $grandchild.children)
                            {
                            #Write-Host $subchild.fieldName
                            if($subchild.fieldName -eq "RootSquash")
                                {
                                $RootSquash = $subchild.fieldValue
                                #Write-Host "Rootsquash = $RootSquash"
                                }
                            if($subchild.fieldName -eq "VSANFileShareAccessPermission")
                                {
                                $AccessPermission = $subchild.fieldValue
                                #Write-Host "NFS Share permission level = $AccessPermission"
                                }
                            if($subchild.fieldName -eq "NFSAccessControlIPSectorSubnet")
                                {
                                $IPSetSub = $subchild.fieldValue
                                #Write-Host "NFS IP persmission = $IPSetSub "
                                }
                            if($subchild.fieldName -eq "NFSSharename")
                                {
                                $Sharename = $subchild.fieldValue
                                #Write-Host "NFS Share Name = $Sharename"
                                }
                           if($subchild.fieldName -eq "HardQuotaGB")
                                {
                                $HardQuotaGB = $subchild.fieldValue
                                Write-Host "NFS Hard quota = $HardQuotaGB"
                                }
                           if($subchild.fieldName -eq "SoftQuotaGB")
                                {
                                $SoftQuotaGB = $subchild.fieldValue
                                Write-Host "NFS soft quota = $SoftQuotaGB"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


#################################################

#export Path for host cpu & Memory
$FileName = "TEF/capacityfinalreport/esxireport.csv"
if (Test-Path $FileName){Remove-Item $FileName}

#export Path details## for datastore##
$FileName1 = "TEF/capacityfinalreport/storage.csv"
if (Test-Path $FileName1){Remove-Item $FileName1}

#export path for nfs best cluster
$FileName2 = "TEF/capacityfinalreport/esxireport2.csv"
if (Test-Path $FileName2){Remove-Item $FileName2}

 ##IF NSX-T AND NFS REQUIRED####
if($NSX -eq $true -and $NFS -eq $true)
 {

### Disable SSL Check depends on Environment#####################
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
#################################################################

$servername=$args[0]
$pass=$args[2]
$user=$args[1]
Connect-VIServer -Server $servername -User $user -password $pass

$bestcluster = $null
$bestclusterfreespace = 0

$clusters = Get-Cluster
Write-Host "NSXT & NFS Required"
$output = foreach ($cluster in $clusters )
{
    $ClusterName = $cluster.Name
    $hosts = Get-Cluster -Name $ClusterName | Get-VMHost
    ##checking nsx-t status on the cluster
    $nsxT=$false
    foreach ($Hosts in $hosts)
    {
        $esxcli = Get-EsxCli -VMHost $hosts
        $vibs = $esxcli.software.vib.list() | where {$_.Name -like "*nsx*"}

        if($vibs)
        {
            $nsxT = $true
            #Write-Host "nsx-t installed on the host $cluster"
        }
    }

        if($nsxT -eq $true)
        {

            #Get host and loop through each of them##
            $hostlist=Get-Cluster -Name $ClusterName | Get-VMHost

            foreach ($hostobj in $hostlist)
            {
                $TotalCPUMhz = Get-VMHost $hostobj | Select CpuTotalMhz
                $UsedCPUMhz = Get-VMHost $hostobj | Select CpuUsageMhz
                $NumCPU = Get-VMHost $hostobj | Select NumCpu
                $FreeCpuCore = [math]::Round((($TotalCPUMhz.CpuTotalMhz - $UsedCPUMhz.CpuUsageMhz)/1000)/($TotalCPUMhz.CpuTotalMhz/(1000*$NumCPU.NumCpu)),0)
                $TotalMemoryGB = Get-VMHost $hostobj | Select MemoryTotalGB
                $UsedMemoryGB = Get-VMHost $hostobj | Select MemoryUsageGB
                $FreeMemoryGB = [math]::Round(($TotalMemoryGB.MemoryTotalGB - $UsedMemoryGB.MemoryUsageGB),0)

                Write-Host $ClusterName, $hostobj,$FreeCpuCore,$FreeMemoryGB
                New-Object -TypeName PSObject -Property @{
                ClusterName= $ClusterName
                HostName = $hostobj.Name
                FreeCPUCore = $FreeCpuCore
                FreeMemoryGB = $FreeMemoryGB
                } | Select-Object ClusterName,HostName, FreeCPUCore, FreeMemoryGB
            }
        ##Fetch Datastore detail in cluster wise###

        $datastores = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True}

        #Loop each datastore
        $output1= foreach ($datastore in $datastores)
        {
            $freedisk = Get-datastore -name $datastore | Select FreeSpaceGB
            Write-Host $ClusterName,$datastore,$freedisk

            New-Object -TypeName PSObject -Property @{
            ClusterName = $ClusterName
            Datastore = $datastore
            FreeSpaceGB = [math]::Round($FreeDisk.FreeSpaceGB,0)

            } | Select-Object clustername, FreeSpaceGB, Datastore

        }

        }

    $vsan = $false
    $nfsshare = $false
    #Loop the VSAN STatus
    $Vsanstatus = Get-VsanClusterConfiguration -Cluster $ClusterName | Select-Object VsanEnabled
    $NFSstatus= Get-VsanFileServiceDomain -Cluster $ClusterName -ErrorAction SilentlyContinue | Select-Object Name
    #Write-Host $Vsanstatus, $vsanfsdomainstatus
    if($NFSstatus -ne $null)
    {
        $clusterfreespace = 0
        $Datastorecluster = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.Type -eq "vsan"}
        foreach($datastore in $Datastorecluster)
        {
            $datastorefreeSpaceGB = $datastore.FreeSpaceGB
            $clusterfreespace += $datastorefreeSpaceGB
            #Write-Host $datastorefreeSpaceGB, $clusterfreespace
        }
       if($HardQuotaGB -ne $null -and $SoftQuotaGB -ne $null)
       {
            $HardQuotaGB = [int]$HardQuotaGB
            $SoftQuotaGB = [int]$SoftQuotaGB
            if($clusterfreespace -gt $HardQuotaGB -and $clusterfreespace -gt $bestclusterfreespace)
            {
                $bestcluster = $cluster
                $bestclusterfreespace = $clusterfreespace
                #Write-Host $bestcluster, $bestclusterfreespace
            }
            else
            {
                Write-Host "$cluster space $clusterfreespace doesn't met the expectation $HardQuotaGB"
            }
       }

    }

}

if($bestcluster -ne $null)
{
    Write-Host $bestcluster.Name $bestclusterfreespace
    $exportData = [PSCustomObject]@{
    "ClusName" = $bestcluster.Name
    "FreeSpacecluster" = $bestclusterfreespace
    }
    $exportData | Export-Csv $FileName2 -Append -Force -NoTypeInformation -UseCulture
    #Get-Template | select Name | Out-File esxireport2.txt
}
##Output1## for CPU and Memory###
$Output | Export-Csv $FileName -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport.txt
##Output1## for Datastore capacity
$Output1 | Export-Csv $FileName1 -Append -Force -NoTypeInformation -UseCulture
get-template |select Name |Out-File -FilePath template.txt

}

##IF NSX-T ONLY REQUIRED###
elseif($NSX -eq $true)
{
 ### Disable SSL Check depends on Environment#####################
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
#################################################################

$servername=$args[0]
$pass=$args[2]
$user=$args[1]
Connect-VIServer -Server $servername -User $user -password $pass

$clusters = Get-Cluster
Write-Host "NSX-T Only"

$output = foreach ($cluster in $clusters )
{
    $ClusterName = $cluster.Name
    $hosts = Get-Cluster -Name $ClusterName | Get-VMHost
    foreach ($Hosts in $hosts)
    {

        #$hostname = $host.Name
        $esxcli = Get-EsxCli -VMHost $hosts
        $vibs = $esxcli.software.vib.list() | where {$_.Name -like "*nsx*"}
        $nsx=$false

        if($vibs)
        {
            $nsx = $true
            #Write-Host "NSX-T installed on cluster $ClusterName"
        }
       #else
       #{ Write-Host "NSX-T Not installed on cluster $ClusterName"}
    }

    if($nsx -eq $true)
    {
        #Write-Host $cluster

        #Get host and loop through each of them##
        $hostlist=Get-Cluster -Name $ClusterName | Get-VMHost

        foreach ($hostobj in $hostlist)
        {
            $TotalCPUMhz = Get-VMHost $hostobj | Select CpuTotalMhz
            $UsedCPUMhz = Get-VMHost $hostobj | Select CpuUsageMhz
            $NumCPU = Get-VMHost $hostobj | Select NumCpu
            $FreeCpuCore = [math]::Round((($TotalCPUMhz.CpuTotalMhz - $UsedCPUMhz.CpuUsageMhz)/1000)/($TotalCPUMhz.CpuTotalMhz/(1000*$NumCPU.NumCpu)),0)
            $TotalMemoryGB = Get-VMHost $hostobj | Select MemoryTotalGB
            $UsedMemoryGB = Get-VMHost $hostobj | Select MemoryUsageGB
            $FreeMemoryGB = [math]::Round(($TotalMemoryGB.MemoryTotalGB - $UsedMemoryGB.MemoryUsageGB),0)

            Write-Host $ClusterName, $hostobj,$FreeCpuCore,$FreeMemoryGB
            New-Object -TypeName PSObject -Property @{
            ClusterName= $ClusterName
            HostName = $hostobj.Name
            FreeCPUCore = $FreeCpuCore
            FreeMemoryGB = $FreeMemoryGB
            } | Select-Object ClusterName,HostName, FreeCPUCore, FreeMemoryGB
        }
        ##Fetch Datastore detail in cluster wise###


        $datastores = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True}

        #Loop each datastore
        $output1= foreach ($datastore in $datastores)
        {
            $freedisk = Get-datastore -name $datastore | Select FreeSpaceGB
            Write-Host $ClusterName,$datastore,$freedisk

            New-Object -TypeName PSObject -Property @{
            ClusterName = $ClusterName
            Datastore = $datastore
            FreeSpaceGB = [math]::Round($FreeDisk.FreeSpaceGB,0)

            } | Select-Object clustername, FreeSpaceGB, Datastore
        }
    }
}

##Output1## for CPU and Memory###
$Output | Export-Csv $FileName -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport.txt
##Output1## for Datastore capacity
$Output1 | Export-Csv $FileName1 -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport1.txt
get-template |select Name |Out-File -FilePath template.txt
}

##IF NFS ONLY REQUIRED##
elseif($NFS -eq $true)
{
### Disable SSL Check depends on Environment#####################
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
#################################################################

$servername=$args[0]
$pass=$args[2]
$user=$args[1]
Connect-VIServer -Server $servername -User $user -password $pass


Write-Host "NFS only Required"
$clusterlist = Get-Cluster
 #Loop through each Cluster##
$Output = foreach ($Cluster in $Clusterlist)
    {

    $ClusterName = $Cluster.Name

    #Get host and loop through each of them##
    $hostlist=Get-Cluster -Name $ClusterName | Get-VMHost

    foreach ($hostobj in $hostlist)
        {
        $TotalCPUMhz = Get-VMHost $hostobj | Select CpuTotalMhz
        $UsedCPUMhz = Get-VMHost $hostobj | Select CpuUsageMhz
        $NumCPU = Get-VMHost $hostobj | Select NumCpu
        $FreeCpuCore = [math]::Round((($TotalCPUMhz.CpuTotalMhz - $UsedCPUMhz.CpuUsageMhz)/1000)/($TotalCPUMhz.CpuTotalMhz/(1000*$NumCPU.NumCpu)),0)
        $TotalMemoryGB = Get-VMHost $hostobj | Select MemoryTotalGB
        $UsedMemoryGB = Get-VMHost $hostobj | Select MemoryUsageGB
        $FreeMemoryGB = [math]::Round(($TotalMemoryGB.MemoryTotalGB - $UsedMemoryGB.MemoryUsageGB),0)

        Write-Host $ClusterName, $hostobj,$FreeCpuCore,$FreeMemoryGB
        New-Object -TypeName PSObject -Property @{
            ClusterName= $ClusterName
            HostName = $hostobj.Name
            FreeCPUCore = $FreeCpuCore
            FreeMemoryGB = $FreeMemoryGB
           } | Select-Object ClusterName,HostName, FreeCPUCore, FreeMemoryGB
        }
    }

 ##Output1## for CPU and Memory###
 $Output | Export-Csv $FileName -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport.txt

##Fetch Datastore detail in cluster wise###

$Output1 = foreach ($Cluster in $Clusterlist)
{
 $ClusterName = $Cluster.Name

 $datastores = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True}

 #Loop each datastore
 foreach ($datastore in $datastores)
 {

 $freedisk = Get-datastore -name $datastore | Select FreeSpaceGB

 Write-Host $ClusterName,$datastore,$freedisk

  New-Object -TypeName PSObject -Property @{
   ClusterName = $ClusterName
   Datastore = $datastore
   FreeSpaceGB = [math]::Round($FreeDisk.FreeSpaceGB,0)

   } | Select-Object clustername, FreeSpaceGB, Datastore

  }
 }

 ##Output1## for Datastore capacity
 $Output1 | Export-Csv $FileName1 -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport1.txt

foreach($Cluster in $Clusterlist)
{
#=========================================

#Write-Host "Checking the $clustername"
$ClusterName = $Cluster.Name
        #Loop the VSAN STatus
        $Vsanstatus = Get-VsanClusterConfiguration -Cluster $ClusterName | Select-Object VsanEnabled
        $NFSstatus= Get-VsanFileServiceDomain -Cluster $ClusterName -ErrorAction SilentlyContinue | Select-Object Name
        #Write-Host $Vsanstatus, $vsanfsdomainstatus
        if($NFSstatus -ne $null)
        {
        $clusterfreespace = 0
        $Datastorecluster = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.Type -eq "vsan"}
        foreach($datastore in $Datastorecluster)
            {
            $datastorefreeSpaceGB = $datastore.FreeSpaceGB
            $clusterfreespace += $datastorefreeSpaceGB
            #Write-Host $datastorefreeSpaceGB, $clusterfreespace
            }
       if($HardQuotaGB -ne $null)
       {
       $HardQuotaGB = [int]$HardQuotaGB
       $SoftQuotaGB = [int]$SoftQuotaGB
       if($clusterfreespace -gt $HardQuotaGB -and $clusterfreespace -gt $bestclusterfreespace)
       {
       $bestcluster = $cluster
       $bestclusterfreespace = $clusterfreespace
       #Write-Host $bestcluster, $bestclusterfreespace
       }
       else{ Write-Host "$cluster capacity $clusterfreespace doesn't met the requirement GB $SoftQuotaGB"}
       }

        }else{ "Vsan or NFS not enabled on the cluster $clusters"}
}

if($bestcluster -ne $null)
{
Write-Host $bestcluster.Name $bestclusterfreespace
$exportData = [PSCustomObject]@{
"ClusName" = $bestcluster.Name
"FreeSpacecluster" = $bestclusterfreespace
}
$exportData | Export-Csv $FileName2 -Append -Force -NoTypeInformation -UseCulture
#Get-Template | select Name | Out-File esxireport2.txt

}

}


##IF NSX & NFS NOT REQUIRED###
elseif($NSX -ne $true -and $NFS -ne $true)
    {

     ### Disable SSL Check depends on Environment#####################
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
#################################################################
$pass=$args[2]
$user=$args[1]
Connect-VIServer -Server $servername -User $user -password $pass

Write-Host "NSX & NFS Not Required"
$clusterlist = Get-Cluster
    #Loop through each Cluster##
$Output = foreach ($Cluster in $Clusterlist)
    {

    $ClusterName = $Cluster.Name

    #Get host and loop through each of them##
    $hostlist=Get-Cluster -Name $ClusterName | Get-VMHost

    foreach ($hostobj in $hostlist)
        {
        $TotalCPUMhz = Get-VMHost $hostobj | Select CpuTotalMhz
        $UsedCPUMhz = Get-VMHost $hostobj | Select CpuUsageMhz
        $NumCPU = Get-VMHost $hostobj | Select NumCpu
        $FreeCpuCore = [math]::Round((($TotalCPUMhz.CpuTotalMhz - $UsedCPUMhz.CpuUsageMhz)/1000)/($TotalCPUMhz.CpuTotalMhz/(1000*$NumCPU.NumCpu)),0)
        $TotalMemoryGB = Get-VMHost $hostobj | Select MemoryTotalGB
        $UsedMemoryGB = Get-VMHost $hostobj | Select MemoryUsageGB
        $FreeMemoryGB = [math]::Round(($TotalMemoryGB.MemoryTotalGB - $UsedMemoryGB.MemoryUsageGB),0)

        Write-Host $ClusterName, $hostobj,$FreeCpuCore,$FreeMemoryGB
        New-Object -TypeName PSObject -Property @{
            ClusterName= $ClusterName
            HostName = $hostobj.Name
            FreeCPUCore = $FreeCpuCore
            FreeMemoryGB = $FreeMemoryGB
           } | Select-Object ClusterName,HostName, FreeCPUCore, FreeMemoryGB
        }
    }

 ##Output1## for CPU and Memory###
 $Output | Export-Csv $FileName -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport.txt

##Fetch Datastore detail in cluster wise###

$Output1 = foreach ($Cluster in $Clusterlist)
{
 $ClusterName = $Cluster.Name

 $datastores = $cluster | Get-VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True}

 #Loop each datastore
 foreach ($datastore in $datastores)
 {

 $freedisk = Get-datastore -name $datastore | Select FreeSpaceGB

 Write-Host $ClusterName,$datastore,$freedisk

  New-Object -TypeName PSObject -Property @{
   ClusterName = $ClusterName
   Datastore = $datastore
   FreeSpaceGB = [math]::Round($FreeDisk.FreeSpaceGB,0)

   } | Select-Object clustername, FreeSpaceGB, Datastore

  }
 }

 ##Output1## for Datastore capacity
 $Output1 | Export-Csv $FileName1 -Append -Force -NoTypeInformation -UseCulture
#get-template |select Name |Out-File -FilePath esxireport1.txt


}

