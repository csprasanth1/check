#working with json to store the nfs input  from NF form##
$json = Get-Content -Raw -Path "TEF/capacityfinalreport/webforminput.json" | ConvertFrom-Json

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
                                Write-Host "Rootsquash = $RootSquash"
                                }
                            if($subchild.fieldName -eq "VSANFileShareAccessPermission")
                                {
                                $AccessPermission = $subchild.fieldValue
                                Write-Host "NFS Share permission level = $AccessPermission"
                                }
                            if($subchild.fieldName -eq "NFSAccessControlIPSectorSubnet")
                                {
                                $IPSetSub = $subchild.fieldValue
                                Write-Host "NFS IP persmission = $IPSetSub "
                                }
                            if($subchild.fieldName -eq "NFSSharename")
                                {
                                $Sharename = $subchild.fieldValue
                                Write-Host "NFS Share Name = $Sharename"
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



#select cluster name based on capacity analysis json file##
$csv= Import-Csv -Path "TEF/capacityfinalreport/esxireport2.csv" -Delimiter ',' -Header "ClusName","FreeSpacecluster"
#export Path for host cpu & Memory
$FileName = "error.csv"
if (Test-Path $FileName){Remove-Item $FileName}
$FileName1 = "nfsdomain.txt"
if (Test-Path $FileName1) {Remove-Item $FileName1}

$clusname = $csv.ClusName[1]
Write-Host $clusname

### Disable SSL Check depends on Environment#####################
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
#################################################################
$servername=$args[0]
$pass=$args[2]
$user=$args[1]


Connect-VIServer -Server $servername -User $user -Password $pass
$vsanFileShare = Get-VsanFileShare -Cluster $clusname | Where-Object{$_.Name -eq $Sharename}
Write-Host $vsanFileShare
 
#if the vsan file sharename already exisit
If($vsanFileShare -like $Sharename)
    {
    Write-Output "FileShare $Sharename already exist"
    $Output= "Fileshare already exit"
    $result = [PSCustomObject]@{Output = $Output}
    $result | Export-Csv -Path $FileName -NoTypeInformation
    exit 1
    }

#if the vsan file share name not exist##
elseif($Sharename -ne $vsanFileShare)
    {
    Write-Output "Creating file share $Sharename"
    $domainname = Get-VsanFileServiceDomain -Cluster $clusname
 
    $fsdomain = Get-VsanFileServiceDomain -Cluster $clusname -Name $domainname[0].Name
    if($RootSquash -eq 'True')
        {
        $permission = New-VsanFileShareNetworkPermission -IPSetOrSubnet $IPSetSub -VsanFileShareAccessPermission $AccessPermission
        }
    else
        {
        $permission = New-VsanFileShareNetworkPermission -IPSetOrSubnet $IPSetSub -VsanFileShareAccessPermission $AccessPermission -AllowSquashRoot
        }
   New-vsanfileshare -FileServiceDomain $fsdomain -Name $Sharename -HardQuotaGB $HardQuotaGB -SoftQuotaGB $SoftQuotaGB  -FileShareNetworkPermission $permission
   ##checking the file share status
   $vsanFileSharestatus = Get-VsanFileShare -Cluster $clusname | Where-Object{$_.Name -eq $Sharename}
   Write-Host $vsanFileSharestatus
   if ($vsanFileSharestatus -like $Sharename)
   {
   Write-Host "$vsanFileSharestatus fileshare created"
   $vsanFileSharestatus | Select-Object FileServiceDomain | ft -Hide | out-File -FilePath $FileName1 -NoClobber
     }
   else
   {
   Write-Host "File share creation Failed"
   exit 1
   }
    }
