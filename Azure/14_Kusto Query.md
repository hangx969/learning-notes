---
title: Kusto Query Language (KQL) Reference
tags:
  - azure/monitoring
  - azure/kusto
  - azure/KQL
  - azure/diagnostics
aliases:
  - KQL
  - Kusto Query
  - KQL Reference
date: 2026-04-16
---

# Kusto Query Language (KQL) Reference

## Related Notes

- [[Azure/0_Azure-VM-VMSS]]
- [[Azure/2_AKS-basics]]

> [!info]
> This file contains a collection of KQL queries for Azure diagnostics and troubleshooting across various services including VM/Node management, AKS, Storage, ACR/ACI, CRP, Backup/ASR, Monitoring, AAD, and Health Events.
>
> The identifiers in these examples are synthetic placeholders. Replace them with the IDs and resource names for your environment before running a query.

---

## VM ID and Nodes

> [!tip]
> Key tables: ==LogContainerSnapshot==, ==LogNodeSnapshot==, ==LogContainerHealthSnapshot==, ==TMMgmtNodeEventsEtwTable==, ==RdmResourceSnapshot==

### Container and node identifiers

#### 查询节点与容器 ID

```kusto
//---------------------- Query all kind of IDs -------------------------------------------------------
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2023-12-01 00:00:00) and PreciseTimeStamp <= datetime(2023-12-12 23:00:00)
//| where nodeId == "12345678-1234-4000-8000-000000000001"
| where subscriptionId == "12345678-1234-4000-8000-000000000002"
| where roleInstanceName contains "example-roleinstancename-1"
//| where availabilitySetName contains "example-availabilitysetname-1"
//| where containerId contains "12345678-1234-4000-8000-000000000003"
//| where virtualMachineUniqueId contains "123454"
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId, subscriptionId
| order by creationTime desc
```

#### 看区域日志最近的产生时间

```kusto
//看区域日志最近的产生时间
//Azurecm - azurecm
LogContainerSnapshot | summarize max(ingestion_time()) by Region
```

#### container health - up/down

```kusto
//---------------- container health - up/down-------------------------------------
//Azurecm - azurecm
LogContainerHealthSnapshot
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where containerId contains "12345678-1234-4000-8000-000000000004"
| project PreciseTimeStamp, actualOperationalState, containerLifecycleState, containerState, containerOsState,nodeId, containerId, faultInfo
```

#### Node Status

```kusto
//----------------------- Node Status --------------------------------------
//Check state of nodes, simplified version
//Azurecm - azurecm
LogNodeSnapshot
| where nodeId == "12345678-1234-4000-8000-000000000005"
| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 03:20:00)
| project PreciseTimeStamp, Tenant,nodeId,nodeState,nodeAvailabilityState, faultInfo, Region, containerCount,diskConfiguration,healthSignals
```

#### Check state of nodes, detailed version

```kusto
//Check state of nodes, detailed version
cluster('Azurecm').database('AzureCM').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(2023-10-26 07:00:00) and PreciseTimeStamp <= datetime(2023-10-26 08:00:00)
| where NodeId == "12345678-1234-4000-8000-000000000006"
| project PreciseTimeStamp, Message
```

#### Check state of tenant, detailed version

```kusto
//Check state of tenant, detailed version
cluster('Azurecm').database('AzureCM').TMMgmtTenantEventsEtwTable
| where TenantName == "12345678-1234-4000-8000-000000000007"
| where PreciseTimeStamp >= datetime(2023-06-07 00:20:00) and PreciseTimeStamp <= datetime(2023-06-07 19:30:00)
| where Message !contains "[AuditEvent]"
| project PreciseTimeStamp, Message
```

#### Check node lifecycle status

```kusto
//Check node lifecycle status
//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
cluster("Azuredcmmc").database("AzureDcmDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-07-09 07:00:00) and PreciseTimeStamp <= datetime(2023-07-09 09:30:00)
| where ResourceId == "12345678-1234-4000-8000-000000000008"
| project-reorder PreciseTimeStamp, ResourceId, LifecycleState, FaultCode, FaultDescription, RepairFaultDetails, RepairResolutionDetails
| sort by PreciseTimeStamp desc
| take 100
```

#### check containers list on the node

```kusto
//check containers list on the node
let starttime = datetime("2023-06-25T03:48:29.415Z");
let endtime = datetime("2023-06-27T03:48:32.933Z");
let nodeid = "12345678-1234-4000-8000-000000000009";
//let nodeid = "12345678-1234-4000-8000-000000000010";
cluster("azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").LogContainerSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeId == nodeid
| distinct creationTime, roleInstanceName, subscriptionId, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId, tenantOwners, containerType, Region, AvailabilityZone
| order by creationTime
```

#### TMMgmtNodeEventsEtwTable

```kusto
let queryFrom = datetime("2023-06-12T19:40:00.000Z");
let queryTo = datetime("2023-06-12T20:30:00.000Z");
let queryNodeId = "12345678-1234-4000-8000-000000000011";
let queryContainerId = "12345678-1234-4000-8000-000000000012";
let queryCheckContainerOnly = true;
cluster("azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where queryCheckContainerOnly != true or Message contains queryContainerId
| project  PreciseTimeStamp, Message, RoleInstance
| extend level = case(
    Message contains "faultInfo changed", "error",
    Message contains "Setting node Fault", "error",
    Message contains "repair request", "warning",
    Message ==  "Out of goal state", "warning",
    Message contains "Reason to regenerate CCF for container", "warning",
    Message contains "->", "warning",
    "info")
```

#### RdmResourceSnapshot

```kusto
cluster("azuredcmmc.kusto.chinacloudapi.cn").database("AzureDCMDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-06-25 19:30:00) and PreciseTimeStamp <= datetime(2023-06-26 23:30:00)
| where ResourceId == "12345678-1234-4000-8000-000000000010" //Node id
| project PreciseTimeStamp, ResourceId, OSType, LifecycleState, PfState, PfRepairState, HealthGrade, HealthSummary, FaultCode, FaultDescription
| order by PreciseTimeStamp asc
| where LifecycleState != prev(LifecycleState)
    or PfState != prev(PfState)
    or PfRepairState != prev(PfRepairState)
    or OSType != prev(OSType)
    or FaultCode != prev(FaultCode)
    or FaultDescription != prev(FaultDescription)
    or HealthGrade != prev(HealthGrade)
    or HealthSummary != prev(HealthSummary)
| extend level = case(PfState in ("D", "C", "F"), "error",
    PfRepairState <> "None" or FaultCode <> 0 or isnull(FaultDescription) or PfState <> "H", "warning",
    "info")
```

### ARM operations

#### ARM operation

```kusto
//------------------ ARM operation----------------------------------------------
// ARM operation
//armmcadx - armmc
EventServiceEntries
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
//| where correlationId contains "12345678-1234-4000-8000-000000000014"
| where resourceUri contains "example-targeturi-4"
| where status contains "Succeed"
//| where operationName notcontains "/extensions/write"
//| where operationName notcontains "Microsoft.Network"
//| where operationName contains "Microsoft.Compute/virtualMachines/extensions"
| where operationName notcontains "Microsoft.Authorization/policies"
| where operationName notcontains "Microsoft.Authorization/policies/auditIfNotExists/action"
| where operationName notcontains "Microsoft.Authorization/policies/audit/action"
//| where operationName contains "Microsoft.Compute/"
//| where operationName contains "Microsoft.Compute/virtualMachines/"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp, operationName, resourceProvider, correlationId, status, subStatus, properties, resourceUri, eventName, operationId, armServiceRequestId, subscriptionId, claims
```

#### HttpIncomingRequests

```kusto
//armmcadx - armmc
HttpIncomingRequests
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where correlationId ==  "12345678-1234-4000-8000-000000000015"
//| where targetUri contains "example-targeturi-1"
// | where status notcontains "Accepted"
| where httpMethod != "GET"
```

#### ASC - operation 拿到correlation id 来这里查具体出错细节

```kusto
//ASC - operation 拿到correlation id 来这里查具体出错细节
//https://armmcadx.chinaeast2.kusto.chinacloudapi.cn
let starttime = datetime(2023-12-07 01:00:00);
let endtime = datetime(2023-12-07 02:30:59);
JobTraces
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
| where correlationId ==  "12345678-1234-4000-8000-000000000016"
| project TIMESTAMP, subscriptionId, correlationId, ActivityId, message, exception
```

### VMA diagnostics

#### VMA Related

```kusto
//-------------------------VMA Related--------------------------------------------------------
//查node的windows事件
cluster('vmainsight.kusto.windows.net').database('vmadb').WindowsEventTable
| where PreciseTimeStamp >= datetime(2023-08-07 07:00:00) and PreciseTimeStamp <= datetime(2023-08-07 08:50:00)
| where NodeId == "12345678-1234-4000-8000-000000000017"
| where Cluster == "example-cluster-1"
| where Description contains "PCI"
| project TIMESTAMP, ProviderName, EventId, Description, Cluster, NodeId
| sort by TIMESTAMP asc
//| distinct NodeId
```

#### WindowsEventTable

```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').WindowsEventTable
| where PreciseTimeStamp >= datetime(2023-11-01 00:00:00) and PreciseTimeStamp <= datetime(2023-11-01 05:30:00)
//| where Description contains "12345678-1234-4000-8000-000000000018" and (Description contains "Ethernet" or Description contains "started successfully")
| where NodeId == "12345678-1234-4000-8000-000000000019"
| project PreciseTimeStamp, EventId, Channel , Description
| sort by PreciseTimeStamp asc
```

#### Windows 磁盘事件与健康分类

```kusto
let queryFrom = datetime('2023-07-22T21:30:28.000Z');
let queryTo = datetime('2023-07-23T01:30:28.000Z');
let queryNodeId = '12345678-1234-4000-8000-000000000020';
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // disk
    "disk", 7, "disk", "Disk", "Unhealthy",
    "LSI_SAS2i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 16, "VhdDiskPrt", "Disk", "Degraded",
    "VhdDiskPrt", 17, "VhdDiskPrt", "Disk", "Unhealthy",
    "disk", 52, "disk", "Disk", "Degraded",
    "Ntfs", 55, "Ntfs", "Disk", "Degraded",
    "Storahci", 129, "Storahci", "Disk", "Unhealthy",
    "vhdmp", 129, "vhdmp", "Disk", "Unhealthy",
    "elxstor", 129, "elxstor", "Disk", "Unhealthy",
    "HpCISSs3", 129, "HpCISSs3", "Disk", "Unhealthy",
    "stornvme", 129, "stornvme", "Disk", "Unhealthy",
    "LSI_SAS2i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 129, "VhdDiskPrt", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 141, "NTFS", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 147, "NTFS", "Disk", "Degraded",
    "Microsoft-Windows-Ntfs", 149, "NTFS", "Disk", "Degraded",
    "disk", 153, "disk", "Disk", "Degraded",
    "disk", 154, "disk", "Disk", "Degraded",
    "Microsoft-Windows-StorPort", 500, "StorPort", "Disk", "Unhealthy",
    "Microsoft-Windows-Hyper-V-NvmeDirectDriver", 5006, "HyperV NVME", "Disk", "Unhealthy",
    "Microsoft-Windows-Hyper-V-NvmeDirectDriver", 6003, "HyperV NVME", "Disk", "Unhealthy",
];
cluster('https://rdosmc.kusto.chinacloudapi.cn').database('rdos').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend Content = strcat (ShortName, ", ", EventId)
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

#### Check RCA level2

```kusto
//Check RCA level2
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where NodeId == "12345678-1234-4000-8000-000000000021" and RoleInstanceName has "CNCORPRSOPAPP1A" //and RCAEngineCategory !contains "Customer"
| distinct bin(StartTime,2m), bin(EndTime,2m), Cluster, RoleInstanceName,  RCALevel1, RCALevel2, Watson_CrashDumpLink,Hardware_Generation
```

#### VMA

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp >= datetime(2023-06-28 16:00:00) and PreciseTimeStamp <= datetime(2023-06-28 18:30:00)
//| where ResourceId == "/subscriptions/12345678-1234-4000-8000-000000000022/resourceGroups/EC2PRDDLRG01/providers/Microsoft.Compute/virtualMachines/CNCORPAZPDLDW8"
| where RoleInstanceName has "example-roleinstancename-2"
| project StartTime, EndTime, RoleInstanceName, Cluster, RCALevel1, RCALevel2
```

#### AirNMAgentUpdateEvents

```kusto
AirNMAgentUpdateEvents
| where EventTime >= datetime(2022-12-18 00:00:00) and EventTime <= datetime(2022-12-19 03:00:00)
| where NodeId == "12345678-1234-4000-8000-000000000018" //and ContainerId == "12345678-1234-4000-8000-000000000023"// and MACAddress == "123454678123"
```

#### RnmOperationEvents

```kusto
//https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm
RnmOperationEvents
| where PreciseTimeStamp >= datetime(2023-07-07 02:00:00) and PreciseTimeStamp <= datetime(2023-07-07 02:15:00) and tenantName == "12345678-1234-4000-8000-000000000024"
| project PreciseTimeStamp, Cluster, EventMessage, status
```

#### RhcAnnotationReportsEtwTable

```kusto
let queryFrom = datetime("2023-07-07T02:00:00.000Z");
let queryTo = datetime("2023-07-07T02:30:00.000Z");
let queryVMId = "12345678-1234-4000-8000-000000000025";
let queryContainerId = "12345678-1234-4000-8000-000000000026";
RhcAnnotationReportsEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where (isnotempty(queryVMId) and VmId == queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VmId, ContainerId, Annotation
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = Annotation, VmId, ContainerId, Annotation
```

#### check host OS update

```kusto
//check host OS update
//https://vmainsight.kusto.windows.net/Air
database("Air").AirManagedEvents
| where EventTime >= datetime(2023-07-07 01:00:00) and EventTime <= datetime(2023-07-07 03:00:00)
| where NodeId contains "12345678-1234-4000-8000-000000000008" and RoleInstanceName contains "T-123-45-003-02"
| distinct EventTime,Cluster, NodeId, RoleInstanceName, EventType, EventSource
```

#### aznwsdn_aznwmds().InterfaceProgramEndFiveMinuteTable

```kusto
//https://vmainsight.kusto.windows.net/Air
aznwsdn_aznwmds().InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP >= datetime(2022-12-19 00:00:00) and TIMESTAMP <= datetime(2022-12-19 03:00:00)
| where NodeId == "12345678-1234-4000-8000-000000000018" and ContainerId == "12345678-1234-4000-8000-000000000023"// and MACAddress == "123454678123"
| project FirstTimeStamp,Detail,StateVersion,FirstTimeProgramming
```

### RDOS and guest agent

#### RDOS related

```kusto
//------------------------RDOS related-----------------------------------------------------------------------
cluster('rdos.kusto.windows.net').database('rdos').HyperVAnalyticEvents
| where PreciseTimeStamp >= datetime(2023-11-01 03:00:00) and PreciseTimeStamp <= datetime(2023-11-01 04:10:00)
| where NodeId contains '12345678-1234-4000-8000-000000000019'
| project PreciseTimeStamp, Cluster, Level, ProviderName, EventId, OpcodeName, TaskName, EventMessage, Message
```

#### vmagent log

```kusto
//vmagent log
//rdosmc
GuestAgentGenericLogs
| where PreciseTimeStamp >= datetime(2023-07-09 08:00:00) and PreciseTimeStamp <= datetime(2023-07-09 08:30:00)
| where ContainerId == '12345678-1234-4000-8000-000000000026'
//| where CapabilityUsed contains "Error"
| project PreciseTimeStamp, Cluster, Level, RoleInstanceName, GAVersion, EventName, CapabilityUsed, Context1, Context2, Context3, OSVersion, ExecutionMode, RAM
```

#### different WindowsEventTable

```kusto
//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
//| where PreciseTimeStamp > ago(24h)
| where PreciseTimeStamp >= datetime(2023-11-01 03:00:00) and PreciseTimeStamp <= datetime(2023-11-01 04:50:00)
| where NodeId in~ ('12345678-1234-4000-8000-000000000019')
//| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170','155','15')
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId
```

#### check Guest OS extension heartbeat

```kusto
//check Guest OS extension heartbeat
let queryContainerId = "12345678-1234-4000-8000-000000000027";
cluster("rdosmc.kusto.chinacloudapi.cn").database("rdos").GuestAgentExtensionEvents
| where PreciseTimeStamp >= datetime(2023-06-21 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where ContainerId == queryContainerId
| project PreciseTimeStamp, Level, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message
| order by PreciseTimeStamp asc
```

#### VmHealthRawStateEtwTable

```kusto
// https://rdosmc.kusto.chinacloudapi.cn/rdos
VmHealthRawStateEtwTable
| where NodeId == "12345678-1234-4000-8000-000000000027"
| where PreciseTimeStamp >= datetime(2023-06-21 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where ContainerId contains "12345678-1234-4000-8000-000000000028"
| project PreciseTimeStamp,  VmHyperVIcHeartbeat, IsVscStateOperational, VmPowerState, Context
```

#### WindowsEventTable

```kusto
WindowsEventTable
| where NodeId in ("12345678-1234-4000-8000-000000000027")
| where PreciseTimeStamp >= datetime(2023-06-20 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where EventId !in ("3095")
| where Description !contains "GetBoardModel" and Description !contains "IO latency summary" and Description !contains "summary for Storport" and Description !contains "Summary of disk space usage"
| project TimeCreated, Cluster,EventId, ProviderName, Description,Level
| order by TimeCreated asc
```

### Node root cause and capacity

#### identify deeper RCA

```kusto
//===============identify deeper RCA==================================
//check node lifecycle state
cluster("Azuredcmmc").database("AzureDcmDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-07-06 06:00:00) and PreciseTimeStamp <= datetime(2023-07-06 08:30:00)
| where ResourceId == "12345678-1234-4000-8000-000000000029" //node id
| project PreciseTimeStamp, ResourceId, LifecycleState, FaultCode, FaultDescription, RepairFaultDetails, RepairResolutionDetails
| sort by PreciseTimeStamp desc
| take 100
```

#### RdmResourceSnapshot

```kusto
let starttime = datetime("2023-07-07T02:00:00.000Z");
let endtime = datetime("2023-07-07T02:15:00.000Z");
let nodeid = "12345678-1234-4000-8000-000000000008";
cluster("azuredcmmc.kusto.chinacloudapi.cn").database("AzureDCMDb").RdmResourceSnapshot
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| project PreciseTimeStamp, ResourceId, OSType, LifecycleState, PfState, PfRepairState, HealthGrade, HealthSummary, FaultCode, FaultDescription
| order by PreciseTimeStamp asc
| where LifecycleState != prev(LifecycleState)
    or PfState != prev(PfState)
    or PfRepairState != prev(PfRepairState)
    or OSType != prev(OSType)
    or FaultCode != prev(FaultCode)
    or FaultDescription != prev(FaultDescription)
    or HealthGrade != prev(HealthGrade)
    or HealthSummary != prev(HealthSummary)
| extend level = case(PfState in ("D", "C", "F"), "error",
    PfRepairState <> "None" or FaultCode <> 0 or isnull(FaultDescription) or PfState <> "H", "warning",
    "info")
```

#### To collect details about Fault codes

```kusto
//#connect "https://azuredcm.kusto.windows.net/AzureDCMDb"
//To collect details about Fault codes
cluster("Azuredcm"). database("AzureDCMDb").FaultCodeTeamMapping
| where FaultCode == "10038"
| project FaultCode, FaultReason
```

#### ResourceSnapshotHistoryV1

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where ResourceId == "12345678-1234-4000-8000-000000000029" //node id
| where PreciseTimeStamp >= datetime(2023-07-06 06:00:00) and PreciseTimeStamp <= datetime(2023-07-06 08:30:00)
| project PreciseTimeStamp, LifecycleState, NeedFlags, FaultCode, FaultDescription, Tenant, ResourceId
```

#### or (filterValue == "All" and healthSignals <> prev(healthSigna…

```kusto
let filterValue = "";
let queryNodeId = "12345678-1234-4000-8000-000000000021";
cluster("azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").LogNodeSnapshot
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where nodeId == queryNodeId
| project PreciseTimeStamp, RoleInstance, nodeState, nodeAvailabilityState, containerCount, faultInfo, healthSignals, diskConfiguration, cmNodeChannelAggregatedHealthStatus,  cmNodeWasChannelHealthStatus, cmNodeWillBeChannelHealthStatus
| order by PreciseTimeStamp asc
| extend flag = case ( nodeState <> prev(nodeState)
   or nodeAvailabilityState <> prev(nodeAvailabilityState)
   or (filterValue == "All" and containerCount <> prev(containerCount))
   or faultInfo <> prev(faultInfo) , "changed", "")
   // or (filterValue == "All" and healthSignals <> prev(healthSignals)), "changed", "")
| where flag <> ""
| extend level = case (
   nodeAvailabilityState in ("Faulted", "OutForRepair") or nodeState in ("Booting", "OutForRepair", "PoweringOn", "HumanInvestigate", "PoweredOff", "Dead", "Recovering"), "error",
   nodeAvailabilityState == "Available" and nodeState == "Ready", "info", "warning");
cluster('azuredcmmc.kusto.chinacloudapi.cn').database('AzureDcmDb').RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where ResourceId =~ queryNodeId
| project PreciseTimeStamp, ResourceId, OSType, LifecycleState, PfState, PfRepairState, FaultCode, RepairFaultDetails, RepairCode, RepairResolutionDetails, FaultDescription, HealthGrade, HealthSummary
| order by PreciseTimeStamp asc
| where LifecycleState != prev(LifecycleState)
    or PfState != prev(PfState)
    or PfRepairState != prev(PfRepairState)
    or OSType != prev(OSType)
    or FaultCode != prev(FaultCode)
    or FaultDescription != prev(FaultDescription)
    or HealthGrade != prev(HealthGrade)
    or HealthSummary != prev(HealthSummary)
| extend level = case(PfState in ("D", "C", "F"), "error",
    PfRepairState <> "None" or FaultCode <> 0 or isnull(FaultDescription) or PfState <> "H", "warning",
    "info");
cluster('azuredcmmc.kusto.chinacloudapi.cn').database('AzureDcmDb').RhwDcmxCSIDiagEtwTable
| where ResourceId =~ queryNodeId
| where FileContents contains "62034" or FileContents contains "62010"
| where FileContents contains "HFS960G32MED-3410A";
cluster('azuredcmmc.kusto.chinacloudapi.cn').database('AzureDcmDb').dcmInventoryComponentDiskDirect
| where DataCollectedOn between (datetime(2023-08-18 06:00:00) .. datetime(2023-08-18 07:00:00))
| where NodeId =~ queryNodeId
| summarize arg_max(DataCollectedOn, *) by OSDiskNumber, DriveProductId, FirmwareRevision
```

#### 查询集群容量上限和支持的虚拟机类型

```kusto
//----------//查当前cluster的容量上限以及支持虚拟机类型的--------------------------------------------------
LogAllocatableVmCountMetric
| where Tenant == "example-tenant-1"//"BJBPrdApp03"//"SH3PrdApp02"//"BJBPrdApp13"
//| where Region contains "chinaeast2"
| where TIMESTAMP > ago(5h)
//| where vmType contains "XIOVM9"  //DS14
//| where vmType contains "SSDVM9"  // "D13"
//| where vmType contains "F8sv2"   //DS13
//| where vmType == "XIOVM3v2"
//| where vmType contains "M"
//| where vmType contains "SSDVM8v2"  //D13_v2
| where limitType == "NewDeployment"
| summarize max(PreciseTimeStamp) by Tenant, vmType, vmCount, limitType
| summarize arg_max(max_PreciseTimeStamp, *) by Tenant, vmType, limitType
| project Tenant, vmType, limitType, vmCount
//| limit 5
```

#### 查看特定机型的capacity

```kusto
//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
// 查看特定机型的capacity
LogAllocatableVmCountMetric
//| where Region == "chinan3" and Tenant contains "PrdApp" and
| where TIMESTAMP > ago(1h)
//| where AvailabilityZone == "chinan3-AZ01"
| where Tenant contains "example-tenant-2"
| where vmType contains "D2s" //or vmType contains "M64ls"
| where limitType in ("NewDeployment","Upgrade","ServiceHealing")
| summarize max(PreciseTimeStamp) by Tenant, vmType, vmCount, limitType
```

#### LogAllocatableVmCountMetric

```kusto
LogAllocatableVmCountMetric
| where Tenant contains "example-tenant-2"//"BJBPrdApp03"//"SH3PrdApp02"//"BJBPrdApp13"
//| where Region == "chinan3"
//| distinct Tenant
```

#### to check capacity of specific cluster

```kusto
//https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm
// to check capacity of specific cluster
cluster('azurecm.chinanorth2.kusto.chinacloudapi.cn').database('azurecm').LogClusterCapacity
| where Tenant == "example-tenant-2" //or Tenant == "example-tenant-1"
| where PreciseTimeStamp >= ago(1h)//(15min)
| project PreciseTimeStamp, Tenant, allocatableNodes, totalHen, totalCores, usedCores, newDeploymentEmptyNodesLimitForAllocation, upgradeEmptyNodesLimitForAllocation
| sort by PreciseTimeStamp desc
```

#### I distinct Tenant

```kusto
AllocableVmCount
| where TIMESTAMP > ago(1h)
| where deploymentType in ("NewDeployment" "Upgrade")
//| where AvailabilityZone contains "chinan3-Az01"
//| where Region contains "chinan3"
| where Tenant contains "example-tenant-2"
//| where vmType contains "M32"
|summarize by Tenant, vmType, vmCount, Region, deploymentType
// I distinct Tenant
// I distinct vmType
// I sort by Tenant asc
```

#### LogClusterCapacity

```kusto
//cluster("https://azurecm.chinanorth2.kusto.chinacloudapi.cn/").database("azurecm");
let starttime = datetime('2023-08-09T00:00:00.000Z');
let endtime = datetime('2023-08-09T23:00:00.000Z');
let cluster = 'example-tenant-2';
LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, isAcceptedNewDeployment = tostring(parse_json(newDeploymentStatusJson).isAcceptingNewDeployments), rejectReason = tostring(parse_json(newDeploymentStatusJson).rejectReason)
| order by PreciseTimeStamp asc
| extend flag = case (prev(isAcceptedNewDeployment) <> isAcceptedNewDeployment, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, Content = ""
| extend EndTime = case (isnotempty(next(isAcceptedNewDeployment)), next(PreciseTimeStamp), endtime)
| extend Health = case (isAcceptedNewDeployment == "true", "healthy",
    isAcceptedNewDeployment == "false", "unhealthy",
    "degraded")
| project StartTime, EndTime, Content, Health
```

### Resource and migration lookup

#### use the summarize to remove duplicate results

```kusto
ResourceDeletions
| where subscriptionId contains "12345678-1234-4000-8000-000000000030"
| where resourceGroupName contains "3"
| where TIMESTAMP > ago(3d)
| project providerNamespace, resourceType, resourceName
//use the summarize to remove duplicate results
//| summarize by providerNamespace, resourceGroupLocation, resourceLocation, resourceType, resourceName
```

#### 根据node的TOR来查node id

```kusto
//根据node的TOR来查node id
//find all nodes under the ToR
//https://azdhmc.chinaeast2.kusto.chinacloudapi.cn/azdhmds
cluster('azdhmc.chinaeast2.kusto.chinacloudapi.cn').database('azdhmds').DeviceInterfaceLinks
| where LinkType =~ 'DeviceInterfaceLink' and EndDevice =~ '123-45-004-123-45-005'
| summarize by DeviceName = StartDevice
| join kind = inner
    (
        Servers
        | where DeviceName =~ DeviceName
    ) on DeviceName
    | project NodeId
```

#### list哪些VM在node list里面

```kusto
//list哪些VM在node list里面
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2023-07-01T00:00:00) and PreciseTimeStamp <= datetime(2023-07-07T23:00)
| where nodeId in (
'12345678-1234-4000-8000-000000000031',
'12345678-1234-4000-8000-000000000032',
'12345678-1234-4000-8000-000000000033',
'12345678-1234-4000-8000-000000000034',
'12345678-1234-4000-8000-000000000035',
'12345678-1234-4000-8000-000000000036',
'12345678-1234-4000-8000-000000000037',
'12345678-1234-4000-8000-000000000038',
'12345678-1234-4000-8000-000000000039',
'12345678-1234-4000-8000-000000000040',
'12345678-1234-4000-8000-000000000041',
'12345678-1234-4000-8000-000000000042',
'12345678-1234-4000-8000-000000000043',
'12345678-1234-4000-8000-000000000044',
'12345678-1234-4000-8000-000000000045',
'12345678-1234-4000-8000-000000000046',
'12345678-1234-4000-8000-000000000047',
'12345678-1234-4000-8000-000000000048',
'12345678-1234-4000-8000-000000000049',
'12345678-1234-4000-8000-000000000050',
'12345678-1234-4000-8000-000000000051',
'12345678-1234-4000-8000-000000000052',
'12345678-1234-4000-8000-000000000053',
'12345678-1234-4000-8000-000000000054'
)
| where subscriptionId in (
'12345678-1234-4000-8000-000000000055'
)
//| project PreciseTimeStamp,roleInstanceName,nodeId,subscriptionId
| distinct roleInstanceName,subscriptionId,nodeId
```

#### LogNodeSnapshot

```kusto
LogNodeSnapshot
| where nodeId in (
'12345678-1234-4000-8000-000000000031',
'12345678-1234-4000-8000-000000000032',
'12345678-1234-4000-8000-000000000033',
'12345678-1234-4000-8000-000000000034',
'12345678-1234-4000-8000-000000000035',
'12345678-1234-4000-8000-000000000036',
'12345678-1234-4000-8000-000000000037',
'12345678-1234-4000-8000-000000000038',
'12345678-1234-4000-8000-000000000039',
'12345678-1234-4000-8000-000000000040',
'12345678-1234-4000-8000-000000000041',
'12345678-1234-4000-8000-000000000042',
'12345678-1234-4000-8000-000000000043',
'12345678-1234-4000-8000-000000000044',
'12345678-1234-4000-8000-000000000045',
'12345678-1234-4000-8000-000000000046',
'12345678-1234-4000-8000-000000000047',
'12345678-1234-4000-8000-000000000048',
'12345678-1234-4000-8000-000000000049',
'12345678-1234-4000-8000-000000000050',
'12345678-1234-4000-8000-000000000051',
'12345678-1234-4000-8000-000000000052',
'12345678-1234-4000-8000-000000000053',
'12345678-1234-4000-8000-000000000054'
)
| where PreciseTimeStamp >= datetime(2023-07-06 16:00:00) and PreciseTimeStamp <= datetime(2023-07-07 18:30:00)
//| project PreciseTimeStamp, Tenant, nodeId, nodeState, nodeAvailabilityState, faultInfo, Region, containerCount
| distinct nodeId,faultInfo
```

#### LiveMigrationSessionCompleteLog

```kusto
LiveMigrationSessionCompleteLog
| where vmUniqueId == "12345678-1234-4000-8000-000000000056"
| project PreciseTimeStamp, sourceNodeId, sourceContainerId, destinationContainerId, destinationNodeId, tenantName, triggerType, status, Role, RoleInstance, resourceId
```

---

## AKS

> [!tip]
> Key tables: ==FrontEndQoSEvents==, ==AsyncQoSEvents==, ==BlackboxMonitoringActivity==, ==ControlPlaneEvents==, ==RemediatorEvent==, ==AutoUpgraderEvents==

> [!info]
> - rp service分前后端，前端是frontend* 后端是async*
> - frontendqos是用户发来的request；asyncqos是前段发给后端的request，是内部实现用的
> - blackbox不是rp的组件，是monitoring的组件，会不停扫描用户的master pod状态，blackbox跟用户的请求没有直接关系
> - ==ServiceRequestId== in ARM EventServices == ==OperationID== in AKS RP QOS tables
> - ==OperationID== in AKS RP QOS tables == ==OperationID== in ContextActivity

### Cluster operations and request tracing

#### AKS operations

```kusto
	//AKS operations
	//cluster创建失败：get operation id by filter failed!!!，cluster级别的一些操作升级也可以，看AKS RP收到的request
	//获取 operation ID
	union
	cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').FrontEndQoSEvents,
	cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncQoSEvents
	| where PreciseTimeStamp >= datetime(2023-12-04 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-12-06 23:00:00.0000000)
	//| where PreciseTimeStamp  > ago(4d)
	| where subscriptionID == "12345678-1234-4000-8000-000000000057" and resourceName contains "aks-tap-cn3-prd"
	| where operationName !contains "get" and operationName !contains "list"
	| extend Count = parse_json(tostring(parse_json(propertiesBag).LinuxAgentsCount))
	| project PreciseTimeStamp,correlationID, operationID, Count, operationName, suboperationName, result,resultSubCode,resultCode,errorDetails
    //|project PreciseTimeStamp,correlationID, operationID, operationName, suboperationName, result,resultSubCode,resultCode,errorDetails
```

#### and resourceGroupName == "cn-devcne2-rtm2-k8s-rg"

```kusto
    union
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').FrontEndQoSEvents,
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncQoSEvents
	| where PreciseTimeStamp >= datetime(2023-10-12 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-10-12 23:00:00.0000000)
	| where subscriptionID == "12345678-1234-4000-8000-000000000058" and resourceName contains "123-45-006-AKS-NP-SMTR"
    //| where resourceName contains "example-resourcename-1"
    //| where operationID == "12345678-1234-4000-8000-000000000059"
    //and resourceGroupName == "cn-devcne2-rtm2-k8s-rg"
    //| where operationName == "PutManagedClusterHandler.PUT"
    | where operationName notcontains "GET"
    | where operationName notcontains "ListManagedCluster"
```

#### error detail，用前面的operation id来查具体的出错信息

```kusto
	//RP
	//error detail，用前面的operation id来查具体的出错信息
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncContextActivity
	//cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').HcpAsyncContextActivity
	| where PreciseTimeStamp >= datetime(2023-12-01 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-12-06 23:00:00.0000000)
	| where operationID == "12345678-1234-4000-8000-000000000060"
	| where level !="info"
    | project PreciseTimeStamp, level, msg, fileName, lineNumber,operationID
```

#### 拿到subid，vmss name，来查cm和crp

```kusto

	//拿到subid，vmss name，来查cm和crp
    let starttime = datetime(2022-08-21 00:10);
	let endtime = datetime(2022-08-21 23:30);
	cluster('azurecm.chinanorth2.kusto.chinacloudapi.cn').database('azurecm').LogContainerSnapshot
	| where TIMESTAMP >= starttime and TIMESTAMP <=endtime
	| where subscriptionId == "12345678-1234-4000-8000-000000000136" and roleInstanceName contains ""
	//"aks-nodepool1-123454678-7"
	//|where availabilitySetName == "example-availabilitysetname-2"
	//| where roleInstanceName contains "example-availabilitysetname-2"
	//| where containerId contains "12345678-1234-4000-8000-000000000061"
	| project TIMESTAMP, Tenant, tenantName, containerId, nodeId, roleInstanceName, availabilitySetName, updateDomain,subscriptionId,RoleInstance
    | sort by TIMESTAMP asc nulls last
```

#### 拿到container id，去查vm agent和extension信息

```kusto
    //rdosmc - rdos
    //拿到container id，去查vm agent和extension信息
    GuestAgentExtensionEvents
	| where PreciseTimeStamp > datetime(2022-08-10 00:10) and PreciseTimeStamp < datetime(2022-08-10 23:30)
	| where ContainerId == "12345678-1234-4000-8000-000000000062"
	//"12345678-1234-4000-8000-000000000063"
	| where Operation !in ('HeartBeat', 'HttpErrors')
	| where isnotempty(Message)
    | project PreciseTimeStamp, ContainerId, Level, GAVersion, Version, Operation,Message,Duration
```

#### AKS RP outgoing，akscn - aksprod

```kusto
    // AKS RP outgoing，akscn - aksprod
    // RP的operation会对应好多个crp的operation和correlation id，要在crp中找到具体哪一个
    // 拿correlation id
    OutgoingRequestTrace
	| where TIMESTAMP > datetime(2022-08-10 00:00) and TIMESTAMP < datetime(2022-08-10 23:00)
	| where operationID == "12345678-1234-4000-8000-000000000064"
	| where targetURI contains "example-targeturi-2"
    | project TIMESTAMP,correlationID, clientRequestID, operationID,msg, operationName, statusCode, level, Environment,targetURI
```

#### 拿到correlation id，去crp查，获取operation id

```kusto
    //#connect "https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc"
    // 拿到correlation id，去crp查，获取operation id
    ApiQosEvent
	| where TIMESTAMP > datetime(2021-06-21 23:00) and TIMESTAMP < datetime(2021-06-24 01:00)
	| where correlationId == "12345678-1234-4000-8000-000000000065"
	| where operationName !contains "GET"
    | project  resourceGroupName, resourceName, goalSeekingActivityId, operationId
```

#### 拿这个operation id = activity id到CRP里再去查#

```kusto
    //拿这个operation id = activity id到CRP里再去查#
	cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity
	| where TIMESTAMP > datetime(2023-07-20 16:00) and TIMESTAMP < datetime(2021-06-24 01:00)
    | where activityId == "12345678-1234-4000-8000-000000000066"
```

#### get operation ID

```kusto

	//get operation ID
	// Akscn - AKSprod
	FrontEndQoSEvents
    | where PreciseTimeStamp >= datetime(2022-07-15 06:00:00.0000000) and PreciseTimeStamp <= datetime(2022-07-15 10:00:00.0000000)
    | where subscriptionID == "12345678-1234-4000-8000-000000000067" and resourceGroupName == "example-targeturi-2" and resourceName == "example-targeturi-2"
    //| where operationName == "PutManagedClusterHandler.PUT"
    | project TIMESTAMP, operationID, operationName
    | take 20
```

#### check cluster error

```kusto
    //check cluster error
    union FrontEndQoSEvents, AsyncQoSEvents
    | where PreciseTimeStamp >= datetime(2023-07-20 16:00:00) and PreciseTimeStamp <= datetime(2023-07-20 19:59:59)
    | where subscriptionID == "12345678-1234-4000-8000-000000000068"
    | where resourceName contains "example-resourcename-2"
    //| where operationName !contains"get" | where operationName !contains"list"
```

#### cluster failed

```kusto
    //ARM
    //cluster failed
    //cluster("Armmcadx.chinaeast2.kusto.chinacloudapi.cn").database("armmc").EventServiceEntries
    EventServiceEntries
    | where PreciseTimeStamp >= datetime(2023-11-15 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:59:59)
    | where subscriptionId == "12345678-1234-4000-8000-000000000057"
    | where resourceUri contains "aks-tap-cn3-prd"
    //| where status == "Failed"
    //| where TIMESTAMP > ago(2d)
    //| where operationName contains "cluster"
    | project PreciseTimeStamp, status, operationName , correlationId ,properties
```

#### ARM https://akscn.kusto.chinacloudapi.cn/AKSprod

```kusto
    //ARM https://akscn.kusto.chinacloudapi.cn/AKSprod
    OutgoingRequestTrace
    | where TIMESTAMP > datetime(2022-10-26 00:00) and TIMESTAMP < datetime(2022-10-31 23:00)
    | where operationID == "12345678-1234-4000-8000-000000000069"
    | where targetURI contains "example-targeturi-3"
    | project TIMESTAMP,correlationID, clientRequestID, operationID, msg, operationName, statusCode, level, Environment, targetURI
```

#### HttpIncomingRequests

```kusto
    //armmcadx - armmc
    HttpIncomingRequests
    | where TIMESTAMP > datetime(2022-09-04 11:00) and TIMESTAMP < datetime(2022-09-04 15:00)
    | where subscriptionId contains "12345678-1234-4000-8000-000000000070"
    | where operationName !contains "METRICBATCH"
    | where httpStatusCode == "202"
    | where httpMethod != "GET"
    | where userAgent contains "Remediator"
    | where operationName contains "RESTART"
```

#### query by operation ID

```kusto
    //query by operation ID
    union FrontEndContextActivity,AsyncContextActivity,HcpAsyncContextActivity
    //union HcpAsyncContextActivity,HcpSyncContextActivity
    | where PreciseTimeStamp > ago (1d)
    | where operationID == ""
    //| where level!="info"
    | project PreciseTimeStamp, level, msg, fileName, lineNumber
```

#### akscn - AKSprod

```kusto
//akscn - AKSprod
RemediatorEvent
| where PreciseTimeStamp >= datetime(2023-06-07 00:20:00) and PreciseTimeStamp <= datetime(2023-06-07 19:30:00)
| where ccpNamespace contains "123454678000000000000001"
//| where reason contains "CustomerLinuxNodesNotReady"
//| where msg contains "failed"
| project PreciseTimeStamp, reason, msg, correlationID, hostMachine
```

#### Here is the autoupgrader

```kusto
//Here is the autoupgrader
AutoUpgraderEvents
| where PreciseTimeStamp >= datetime(2023-12-01 00:20:00) and PreciseTimeStamp <= datetime(2023-12-08 19:30:00)
| where subscriptionID contains '12345678-1234-4000-8000-000000000013'
//| where resourceGroupName has "example-resourcegroupname-1"
| where resourceName contains "example-resourcename-3"//clustername
//| where msg contains "Upgrade node image"
//| where msg contains "Autoupgrade not enabled"
| project PreciseTimeStamp,level,msg
```

#### Autoupgrade related

```kusto
//Autoupgrade related
//database->looper->autoupgrader
//Here is the looper to get enquene
RegionalLooperEvents
| where PreciseTimeStamp > ago(1d)
//| where fileName contains 'upgrade'
| where msg contains "Enqueuing message" and msg has "/subscriptions/12345678-1234-4000-8000-000000000013/resourceGroups/example-resourcegroupname-1/providers/Microsoft.ContainerService/managedClusters/example-resourcename-3" //resourceURI in format /managedClusters/myAKS
| project PreciseTimeStamp,msg,error,Environment, fileName, api
```

### Cluster health and monitoring

#### cluster 状态 BBM

```kusto
//============cluster 状态 BBM==============================================
//=================akscn - AKSprod=========================================================
    //BBM只是一个general的信息，不一定展示出全部的错误。是靠外部监控组件来的，不是直接从后台组件抓出来的。
    let starttime = datetime(2023-12-07 01:00:00);
    let endtime = datetime(2023-12-07 02:00:00);
    BlackboxMonitoringActivity
    | where TIMESTAMP >= starttime and TIMESTAMP <= endtime
    | where subscriptionID == "12345678-1234-4000-8000-000000000013"
    | where clusterName contains "example-resourcename-3"
    //| where agentNodeName contains "aks"
    | where state != "Healthy"
    | project clusterName, PreciseTimeStamp, fqdn, ccpNamespace, agentNodeName, state, reason, podsState, resourceState, addonPodsState, agentNodeCount, provisioningState, msg, resourceGroupName, resourceName, underlayName
```

#### BlackboxMonitoringActivity

```kusto
    let starttime = datetime(2023-05-04 16:00:00.3320075);
    let endtime = datetime(2023-05-06 19:30:00.3320075);
    BlackboxMonitoringActivity
    | where TIMESTAMP >= starttime and TIMESTAMP <= endtime
    | where fqdn == "example-1.hcp.example.invalid"
    | where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
    | project PreciseTimeStamp, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP
```

#### BlackboxMonitoringActivity

```kusto
    BlackboxMonitoringActivity
    | where TIMESTAMP > datetime(2019-08-22) and fqdn contains "example-cluster.hcp.example.invalid"
    | project PreciseTimeStamp, state, reason
    | summarize count() by bin(PreciseTimeStamp, 30m), state
    | render timechart
```

#### 查看aks 自动修复是否进行了

```kusto
    // 查看aks 自动修复是否进行了
	BlackboxMonitoringActivity
	| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:59:59)
	| where fqdn == "example-2.hcp.example.invalid"
	| where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
	| project PreciseTimeStamp, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP
```

#### BlackboxMonitoringActivity

```kusto
cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').BlackboxMonitoringActivity
| where PreciseTimeStamp >= datetime(2023-11-27 11:00:00) and PreciseTimeStamp <= datetime(2023-11-27 12:00:00)
//| where fqdn == "example-3.hcp.example.invalid"
| where subscriptionID == "12345678-1234-4000-8000-000000000072"
//| where fqdn == "example-4.hcp.example.invalid"
//| where clusterName contains "example-clustername-1"
| where clusterName == "example-clustername-2"
| where state != "Healthy"
//| where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
| project PreciseTimeStamp, clusterName, isCCPPoolingEnabled, isPrivateCluster, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP, apiserverCPU, apiserverLatency, coreDNSConfig, etcdCPU, etcdMemory,fqdn
```

#### 查看集群kubesystem信息

```kusto
//查看集群kubesystem信息
KubeSystemEvents
| where PreciseTimeStamp >= datetime(2023-11-27 11:00:00) and PreciseTimeStamp <= datetime(2023-11-27 12:00:00)
| where (((* has @'12345678-1234-4000-8000-000000000072' and * has @'example-clustername-2'))) //and * has @'error') )
| limit 100

```

#### AKS RP outgoing

```kusto
    //AKS RP outgoing
    OutgoingRequestTrace
	| where TIMESTAMP > datetime(2023-12-07 01:00) and TIMESTAMP < datetime(2023-12-07 02:00)
	//| where operationID == "12345678-1234-4000-8000-000000000073"
	| where targetURI contains "example-targeturi-4"
    | project TIMESTAMP,correlationID, clientRequestID, operationID,msg, operationName, statusCode, level, Environment,targetURI
```

#### GuestAgentExtensionEvents

```kusto
    //rdosmc - rdos
    GuestAgentExtensionEvents
	| where PreciseTimeStamp > datetime(2021-06-22 00:10) and PreciseTimeStamp < datetime(2021-06-24 14:30)
	| where ContainerId ==
	"12345678-1234-4000-8000-000000000074"
	//"12345678-1234-4000-8000-000000000063"
	| where Operation !in ('HeartBeat', 'HttpErrors')
	| where isnotempty(Message)
    | project PreciseTimeStamp, ContainerId, Level, GAVersion, Version, Operation,Message,Duration
```

#### 查看aks 自动修复是否进行了

```kusto
	// 查看aks 自动修复是否进行了
	RemediatorEvent
	| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:00:59)
	| where ccpNamespace == "123454678000000000000002"
	//| where reason contains "CustomerLinuxNodesNotReady"
    | project PreciseTimeStamp, reason, msg, correlationID
```

### Control plane and pod events

#### check node pod deployment scale endpoints

```kusto
// check node pod deployment scale endpoints
// Akscn - AKSprod
//pod, node, service, scaler, API等control panel的改变
ControlPlaneEvents //NonShoebox    <-- depend on whether customer enable insights
| where ccpNamespace == '123454678000000000000001'  //在BBM的表里能查出来
| where PreciseTimeStamp >= datetime(2023-06-07 00:20:00) and PreciseTimeStamp <= datetime(2023-06-07 19:30:00)
// | where PreciseTimeStamp >= ago(30d)
// | where category == 'kube-audit'
// | extend Pod = extractjson('$.pod', properties, typeof(string))
| extend Log = extractjson('$.log', properties , typeof(string))
| extend _jlog = parse_json(Log)
| extend requestURI = tostring(_jlog.requestURI)
| extend verb = tostring(_jlog.verb)
| extend verb = extractjson('$.verb', Log, typeof(string))
| extend user = tostring(_jlog.user.username)
| where verb !in ('get', 'list', 'watch')
//*********** Switching area, uncomment below sections for specific query
//***** deployment query
//| where properties contains 'cre-bff'
| where requestURI contains "deployment" and requestURI contains "internal-app"
| extend replicas = _jlog.responseObject.status.replicas
| extend readyReplicas = _jlog.responseObject.status.readyReplicas
| extend unavailableReplicas = _jlog.responseObject.status.unavailableReplicas
| project PreciseTimeStamp, requestURI, verb, user, replicas, readyReplicas, unavailableReplicas, category //, Log
//***** pod query 拆开
//| where properties contains 'kube-proxy'
//| where properties contains '/pods/'
//| where verb == 'delete'
//| project PreciseTimeStamp, requestURI, verb, user
//***** node availability
//| where user != 'nodeclient'
//| where properties contains '/nodes/'
//| extend nodecond = tostring(_jlog.requestObject.status.conditions)
//| mv-expand nodecond = _jlog.requestObject.status.conditions
//| where nodecond['type'] == 'Ready'
//| project PreciseTimeStamp, requestURI, verb, user, nodecond, Log
//***** pod tracking
//| where properties contains 'prome'
// or properties contains 'extractor-1234546780-d8fhj'
// or properties contains 'extractor-1234546780-kfvns'
// or properties contains 'change-1234546780-mdqgk'
// or properties contains 'change-1234546780-8cdn5'
// or properties contains 'change-1234546780-8cdn5'
// or properties contains 'change-1234546780-c6qcm'
// or properties contains 'inf-reportcron-123454678-sg245'
//| mv-expand podCond = _jlog.requestObject.status.conditions
//| extend ownerType = tostring(_jlog.requestObject.metadata.ownerReferences[0].kind)
//| extend ownerName = tostring(_jlog.requestObject.metadata.ownerReferences[0].name)
//| project PreciseTimeStamp, requestURI, verb, user, podCond//, ownerType, ownerName, Log
//***** endpoints
// | where properties contains '/endpoints/'
// | mv-expand subsets = _jlog.requestObject.subsets
// | mv-expand notReadyAddresses = subsets.notReadyAddresses, addresses = subsets.addresses
// | project PreciseTimeStamp, requestURI, verb, user, notReadyAddresses, addresses, Log
//***** pod binding
//| where properties contains '/pods/'
//| where properties contains 'chargingservice-deploy-1234546780-mh7ph'
// | where properties contains 'webservicesdrugdata-1234546780-j7hb5'
// | where properties contains 'webservicesdrugdata'
// | mv-expand podCond = _jlog.requestObject.status.conditions
// | extend ownerType = tostring(_jlog.requestObject.metadata.ownerReferences[0].kind)
// | extend ownerName = tostring(_jlog.requestObject.metadata.ownerReferences[0].name)
// | extend podCondType = tostring(podCond.type)
// | extend podCondStatus = tostring(podCond.status)
// | extend podCondReason = tostring(podCond.reason)
// | extend podCondMessage = tostring(podCond.message)
// | where podCondType contains 'Ready' // and podCondStatus == 'False'
// | where properties contains 'jieyzhou'
// | project PreciseTimeStamp, requestURI, verb, user, podCondType, podCondStatus, podCondReason, podCondMessage, Log, properties
// | summarize count() by requestURI, podCondType, podCondStatus
// | where podCondType == "ContainersReady"
// | order by requestURI, podCondStatus
// | take 1000
```

#### control plane的记录

```kusto
//control plane的记录
//可以查POD，node，service、API等control plane上的life cycle改变
let queryCcpNamespace = "123454678000000000000003";
let query = "konnectivity-agent-123454678";
union
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEvents,
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp >= datetime(2023-11-01 00:00:00) and PreciseTimeStamp <= datetime(2023-12-20 02:00:00)
| where ccpNamespace == queryCcpNamespace and properties has query
//| where category == 'kube-audit'
| extend log = parse_json(tostring(parse_json(properties).log))
| where log.objectRef.resource == 'pods' and log.stage == "ResponseComplete"
| extend level = tostring(log.level)
| extend verb = tostring(log.verb)
| extend user = tostring(log.user.username)
| extend namespace = tostring(log.objectRef.namespace)
| extend name = tostring(log.objectRef.name)
| extend userAgent = tostring(log.userAgent)
| extend nodeName = case(
  verb == "create", tostring(log.reauestObject.target.name),
  level == "RequestResponse" and verb != "create", tostring(log.responseObject.spec.nodeName),
  level == "RequestResponse", tostring(log.responseObject.spec.nodeName),
  tostring(split(log.user.username, "system:node:")[1]))
 | where isnotempty(nodeName)
// | where namespace contains "kube-system" //and name contains "kube-proxy"
 | extend StartTime = PreciseTimeStamp
 | extend Content = strcat(verb, "</br>", userAgent, "</br>", nodeName)
 | project StartTime, Content, verb, user, nodeName, namespace, name, userAgent
 | order by StartTime asc
 //| limit 100
```

#### check pod creation

```kusto
//======check pod creation================
let queryFrom = datetime("2023-11-05T00:00:00.000Z");
let queryTo = datetime("2023-12-10T12:30:00.000Z");
let queryCcpNamespace = "123454678000000000000003";
let queryPod = "konnectivity-agent-123454678-m2pm6";
union
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEvents,
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ccpNamespace == queryCcpNamespace and properties has queryPod
| where category == 'kube-audit'
| extend log = parse_json(tostring(parse_json(properties).log))
| where log.objectRef.name == queryPod
| where log.objectRef.resource == "pods" and log.stage == "ResponseComplete" and log.verb != "get"
| extend level = tostring(log.level)
| extend verb = tostring(log.verb)
| extend user = tostring(log.user.username)
| extend namespace = tostring(log.objectRef.namespace)
| extend name = tostring(log.objectRef.name)
| extend userAgent = tostring(log.userAgent)
| extend nodeName = case(
    verb == "create", tostring(log.requestObject.target.name),
    level == "RequestResponse" and verb != "create", tostring(log.responseObject.spec.nodeName),
    level == "RequestResponse", tostring(log.responseObject.spec.nodeName),
    tostring(split(log.user.username, "system:node:")[1])
)
| where isnotempty(nodeName)
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(verb, "</br>", userAgent, "</br>", nodeName)
| project StartTime, Content, verb, user, nodeName, namespace, name, userAgent
| order by StartTime asc
```

#### check node events

```kusto
//#check node events
//rdosmc.kusto.chinacloudapi.cn/rdos
let StartTime=datetime(2021-07-8 23:00);
let EndTime=datetime(2021-07-12 10:00);
WindowsEventTable
| where NodeId == "12345678-1234-4000-8000-000000000075" and PreciseTimeStamp between (StartTime..EndTime)
//| where Description contains "12345678-1234-4000-8000-000000000076"
| where Description contains "12345678-1234-4000-8000-000000000077"
//| where EventId == "17"
| project PreciseTimeStamp,NodeId, EventId,ProviderName, Description, Level, Cluster
```

#### since we can see that this node was faulted, check more fault …

```kusto
//# since we can see that this node was faulted, check more fault RCA level.
//vmainsight.kusto.windows.net/vmadb
//node fault RCA level - vmadb
VMA
| where NodeId == "12345678-1234-4000-8000-000000000075"
| where PreciseTimeStamp  >= datetime(2021-06-22T00:00:00Z)
| where  PreciseTimeStamp <= datetime(2021-07-09T22:00:00Z)
| where RoleInstanceName == "example-roleinstancename-3"
| project PreciseTimeStamp,RoleInstanceName,RCAEngineCategory, RCALevel1,RCALevel2, RCALevel3, RCA_CSS
```

#### node status

```kusto
//node status
TMMgmtNodeEventsEtwTable
| wherePreciseTimeStamp> datetime(2021-07-09 09:25)
| wherePreciseTimeStamp< datetime(2021-07-09 10:30)
| whereNodeId== "12345678-1234-4000-8000-000000000075"
| whereMessage!contains"AuditEvent"
| whereMessage!contains"Processed notification"
| projectPreciseTimeStamp, Tenant, RoleInstance, Message
| sortbyPreciseTimeStampasc
```

#### BlackboxMonitoringActivity

```kusto
let starttime = datetime(2022-08-29 07:00:20.000);
let endtime = datetime(2022-08-30 23:00:20.000);
BlackboxMonitoringActivity
| where TIMESTAMP > ago(1h)
| where clusterName contains "example-clustername-3"
| where subscriptionID contains "12345678-1234-4000-8000-000000000078"
| project PreciseTimeStamp, subscriptionID, clusterName, region, fqdn,  ccpNamespace, k8sCurrentVersion, agentNodeName, state, reason, pod,  podsState, resourceState, addonPodsState, agentNodeCount, provisioningState, msg, resourceGroupName, resourceName, underlayName
| sort by PreciseTimeStamp desc
```

### Autoscaler and notifications

#### 查autoscaler的日志

```kusto
//============查autoscaler的日志========================
let starttime = datetime(2023-12-07 01:10:00.6812130);
let endtime = datetime(2023-12-07 01:51:00.6812130);
union
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEvents,
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where category contains 'autoscaler'
| where ccpNamespace contains "123454678000000000000002"
| project PreciseTimeStamp, properties
```

#### 查aks autoscaler call CRP的log

```kusto
// 查aks autoscaler call CRP的log
 let starttime = datetime(2022-12-09 08:00:52.7181926);
 let endtime = datetime(2022-12-09 13:30:12.6721662);
 ApiQosEvent
 | where userAgent contains "cluster-autoscaler-aks"
 | where resourceGroupName contains "example-resourcegroupname-2"
 | where resourceName == "example-resourcename-4"
 | join kind = inner(cluster('azcrpmc').database('crp_allmc').VmssQoSEvent
 | where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime) on $left.operationId == $right.operationId
 | project PreciseTimeStamp, operationId,  requestEntity, httpStatusCode, resourceName, e2EDurationInMilliseconds, userAgent, clientApplicationId, region, predominantErrorCode, errorDetails, subscriptionId, vmssName, resourceGroupName
```

#### Azure Notification history for an Azure subscription

```kusto
//Azure Notification history for an Azure subscription
cluster('icmcluster.kusto.windows.net').database('AzNSPROD').AzNSTransmissionsMooncake
//| where SubscriptionId == "12345678-1234-4000-8000-000000000079"
| where SubscriptionId == "12345678-1234-4000-8000-000000000080"
| sort by CreatedTime desc
| project CreatedTime, NotificationState, MechanismType, WebhookHostUrl, FailureReason, AdditionalInfo, AssociatedGroupId
```

---

## Storage

> [!tip]
> Key tables: ==EventServiceEntries==, ==HttpIncomingRequests==, ==StorageAccountStatisticsRecord==, ==AccountTransactionsHourly==, ==DiskRPResourceLifecycleEvent==

### ARM and throttling

#### ARM - Armmcadx - armmc

```kusto
	// ARM - Armmcadx - armmc
	EventServiceEntries
	| where TIMESTAMP between(datetime(2023-08-12 00:00)..datetime(2023-08-14 23:00))
	| where resourceUri contains "auditlogpoc"
	//| where operationName contains "Microsoft.Storage/storageAccounts"
	//| where correlationId contains "12345678-1234-4000-8000-000000000081"
	| project PreciseTimeStamp, operationName, resourceProvider, correlationId, status, subStatus, properties, resourceUri, eventName, operationId, armServiceRequestId, subscriptionId, claims
```

#### ask region //xstore

```kusto
	//ask region //xstore
    StorageAccountStatisticsRecord
    | where Timestamp between(datetime(2023-04-24 00:00)..datetime(2023-04-24 23:00))
    | where SubscriptionId == "12345678-1234-4000-8000-000000000055" and AccountName contains "md-hdd-cdz3vqtqkz2s"
    | project Location, creationTime, primaryStampName, secondaryStampName
```

#### throttling check

```kusto
    // throttling check
    // armmcadx - armmc
    let subid = "12345678-1234-4000-8000-000000000082";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2023-04-18 00:00)..datetime(2023-04-21 23:00))
    | where subscriptionId == subid
    //| where httpStatusCode >= 200
    | summarize count() by bin(TIMESTAMP, 1d), operationName
    | order by count_ desc
    | where operationName contains "delete" and operationName !contains "GET"
    | limit 100
```

#### throttling check

```kusto
    // throttling check
    // armmcadx - armmc
    let subid = "12345678-1234-4000-8000-000000000067";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2022-09-01 00:00)..datetime(2022-09-09 23:00))
    | where subscriptionId == subid
    //| where httpStatusCode >= 200
    //| summarize count() by bin(TIMESTAMP, 1d), operationName
    | order by count_ desc
    | where operationName contains "snapshot"
```

#### ARM or RP throttling check

```kusto
    //ARM or RP throttling check
    let subid = "12345678-1234-4000-8000-000000000083";
    HttpOutgoingRequests
    | where TIMESTAMP between(datetime(2023-02-01 00:00)..datetime(2023-02-03 23:00))
    | where subscriptionId == subid
    | where httpStatusCode == 404
    //| summarize count() by hostName
    //| order by count_ desc
```

#### HttpIncomingRequests

```kusto
cluster('armmcadx.chinaeast2.kusto.chinacloudapi.cn').database('armmc').HttpIncomingRequests
| where subscriptionId == "12345678-1234-4000-8000-000000000084"
|  where PreciseTimeStamp >= ago(1d) //datetime(2022-05-2 17:20:00) and PreciseTimeStamp <= datetime(2022-05-2 17:30:00)
| where targetUri contains "example-targeturi-5"
| where operationName !contains "GET"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp,operationName, httpMethod, correlationId,ActivityId,serviceRequestId, httpStatusCode, targetUri, exceptionMessage
```

### Storage operations and requests

#### HttpIncomingRequests

```kusto
    //List Storage Account Service SAS operations on a resource group, summarized by who/what is doing the operation.
    //This helps us determine if it is a single client (ie. monitoring software) causing the throttling or lots of different clients/users.
    let subid = "12345678-1234-4000-8000-000000000083";
    //let opname = "POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.STORAGE/STORAGEACCOUNTS/cvppprodstorage2019";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2023-02-01 00:00)..datetime(2023-02-03 23:00))
    | where subscriptionId == subid
    | where httpStatusCode  == 404
    //| where operationName == opname
    | summarize count() by clientIpAddress, principalOid, clientApplicationId, userAgent, httpStatusCode
    | order by count_ desc
```

#### HttpOutgoingRequests

```kusto
    //
    HttpOutgoingRequests
    | where (TIMESTAMP >= datetime(2022-09-08 06:00) and TIMESTAMP < datetime(2022-09-08 10:00))
    | where subscriptionId has @'12345678-1234-4000-8000-000000000067'
    //| where httpStatusCode == 529
    | where httpMethod !contains "GET"
```

#### ClientErrors

```kusto
    //
    ClientErrors
    | where TIMESTAMP between(datetime(2022-06-01 00:00)..datetime(2022-06-01 23:00))
    | where subscriptionId contains "12345678-1234-4000-8000-000000000085"
```

#### ClientRequests

```kusto
    ClientRequests
    | where TIMESTAMP between(datetime(2022-09-08 06:00)..datetime(2022-09-08 10:00))
    | where subscriptionId contains "12345678-1234-4000-8000-000000000067"
```

#### Check if disk is soft deleted

```kusto
//cluster('disksmc.chinaeast2.kusto.chinacloudapi.cn').database('Disks').
//Check if disk is soft deleted
DiskRPResourceLifecycleEvent
| where PreciseTimeStamp between(datetime(04/28/2023 00:00:00)..datetime(04/28/2023 23:39:41))//Choose a time shortly before the disk deletion
| where subscriptionId =~ '12345678-1234-4000-8000-000000000086'
| where resourceName has 'os' //or resourceName has 'CAAPMSVMPRD02_OSDISK_1_4067C60C0CE849D8929C4C7C911C1277'
//| where resourceGroupName has 'example-resourcegroupname-3'
//| where diskEvent has 'softdelete'
| summarize max( bin(PreciseTimeStamp,1d)) by subscriptionId,resourceGroupName, resourceName
, blobUrl, diskEvent, RPTenant,MonitoringApplication
| order by max_PreciseTimeStamp asc
```

#### HttpIncomingRequests

```kusto
HttpIncomingRequests
| where subscriptionId contains "12345678-1234-4000-8000-000000000087"
| where PreciseTimeStamp >= datetime(2022-09-01 00:00:00) and PreciseTimeStamp <= datetime(2022-09-09 23:00:00)
//| where correlationId contains "12345678-1234-4000-8000-000000000088"
| where targetUri contains "example-targeturi-6"
// | where status notcontains "Accepted"
| where operationName contains "delete"
| where httpMethod != "GET"
```

#### HttpIncomingRequests

```kusto
let subid = "12345678-1234-4000-8000-000000000089";
HttpIncomingRequests
| where TIMESTAMP >= now(-30d)
| where subscriptionId == subid
| where httpStatusCode == 429
| summarize count() by bin(TIMESTAMP, 1d), operationName
| order by count_ desc
```

#### Check operations

```kusto
//Check operations
//https://armmcadx.chinaeast2.kusto.chinacloudapi.cn/armmc
ShoeboxEntries
| where resourceId endswith "/auditlogpoc"
| where TIMESTAMP > ago(1d) and resultSignature contains "Failed"
| project PreciseTimeStamp , resourceId , operationName , resultSignature , properties, correlationId
```

### Disk and account diagnostics

#### 查VM的非托管磁盘

```kusto
//查VM的非托管磁盘
cluster('https://rdosmc.kusto.chinacloudapi.cn').database('rdos').OsConfigTable
| where TIMESTAMP >= ago(10d)
| where ConfigValue contains "T-123-45-008-08"
// | where ConfigValue contains "12345678-1234-4000-8000-000000000090"//
| where ConfigValue contains "t-maa3-hpc-06"| extend DiskPathCN = tostring(substring(ConfigName, indexof(ConfigName, '/') + 1))
//| where DiskPathCN startswith "md-fz1btkmfgqfn"| extend StorageCluster = extractjson('$.storagecluster', ConfigValue , typeof(string))
| extend _blobproperties = extractjson('$.blobproperties', ConfigValue , typeof(dynamic ))
| extend diskUri=_blobproperties['x-ms-disk-resource-uri']// | summarize arg_max(PreciseTimeStamp ) by ConfigName, DiskPathCN,StorageCluster,diskUri
| summarize arg_max(PreciseTimeStamp, DiskPathCN) by tostring(diskUri)
```

#### 查存储账户的tenant信息

```kusto
// 查存储账户的tenant信息
cluster('xstore.kusto.windows.net').database('xdataanalytics').XStoreAccountPropertiesHourly
| where TimePeriod >= ago(24d)
| where Account has 'example-account-1'
//| where Subscription has 'xx'
| project TimePeriod, Tenant, Account
```

#### AccountTransactionsHourly

```kusto
//https://xstore.kusto.windows.net/xstore
AccountTransactionsHourly
| where TimePeriod between(datetime(2023-09-12T00:00)..datetime(2023-12-12T23:00))
and BilledSubscription =~ "12345678-1234-4000-8000-000000000091"
| where AccountName contains "example-accountname-1"
//| where (RequestType contains "cool" and RequestType contains "Put")
| where RequestType contains "Total"
| project TimePeriod, AccountName, RequestType, AccessTier, TransactionType, TransactionCount, BillableTransactionCount, TotalIngress, TotalEgress ,BillableIngress, BillableEgress
```

#### AccountTransactionsDaily

```kusto
//https://xstore.kusto.windows.net/xstore
AccountTransactionsDaily
| where TimePeriod between(datetime(2023-10-12T00:00)..datetime(2023-12-12T00:00))
| where BilledSubscription contains "12345678-1234-4000-8000-000000000091"
| where AccountName contains "example-accountname-1"
| project TimePeriod, RequestType, AccessTier, TransactionType, TransactionCount, BillableTransactionCount
```

---

## ACR

> [!tip]
> Key tables: ==RegistryActivity==, ==WorkerServiceActivity==, ==ContainerVA_ImageScanLifeCycleEvents==

### Registry activity and manifests

#### RegistryActivity

```kusto
//Acrmc2
RegistryActivity
| where PreciseTimeStamp > ago(5h) //and PreciseTimeStamp < ago(d)
//| where level != "info"
| where http_request_host == "example-registry-1.azurecr.cn"
| where correlationid == "12345678-1234-4000-8000-000000000092"
```

#### RegistryActivity

```kusto
RegistryActivity
| where PreciseTimeStamp > ago(1d) //and PreciseTimeStamp < ago(d)
//| where level != "info"
| where http_request_host == "example-registry-2.azurecr.cn"
//| where correlationid == "12345678-1234-4000-8000-000000000093"
```

#### Unique Manifests (with or without tag) the Registry has

```kusto
//Unique Manifests (with or without tag) the Registry has
//Acrmc2
WorkerServiceActivity
| where env_time > ago(14d)
//| where OperationName == "ACR.Layer: AddManifestRefAsync-Succeed"
| where RegistryLoginUri == "example-registry-1.azurecr.cn"
//| where Repository contains "dataplatformworkflow"
//| summarize count() by Repository, Tag, Digest
| project TimeStamp, Repository, Tag, Digest
```

#### we can look for a specific type of image

```kusto
WorkerServiceActivity
| where env_time > ago(30d)
| where OperationName == "ACR.Layer: ExecuteOperationOnListManifestsAsync"
| where RegistryLoginUri == "example-registry-2.azurecr.cn"
// we can look for a specific type of image
//| where ImageType == "Docker"
| extend numManifests = toint(substring(Message, 52, strlen(Message) - 11 - 52))
| summarize numManifests = sum(numManifests) by bin(env_time, 1d), RegistryId, RegistryLoginUri, ImageType
```

#### union

```kusto
union
cluster('romeeus.kusto.windows.net').database('ProdRawEvents').ContainerVA_ImageScanLifeCycleEvents,
cluster('romeuksouth.uksouth.kusto.windows.net').database('ProdRawEvents').ContainerVA_ImageScanLifeCycleEvents
//| where GeneratedTimestamp > ago(10d)
| where SubscriptionId == "12345678-1234-4000-8000-000000000094"
//| where * contains "sha256:d2ef748ca082fc80237f1da20673fe4d0b57486317bbfe5633586c845c346ee7"
| extend TriggerType = parse_json(tostring(parse_json(AdditionalData).["TriggerType"]))
| extend ScanResultToHandle = parse_json(tostring(parse_json(AdditionalData).["ScanResultToHandle"]))
| extend RequestId = parse_json(tostring(parse_json(ScanResultToHandle).["RequestId"]))
| extend errorReason = tostring(AdditionalData.ScanResultToHandle.ScanErrorReason)
| extend IsTransient = tostring(AdditionalData.ScanResultToHandle.IsScanErrorTransient)
| extend ExternalErrorData = tostring(AdditionalData.ScanResultToHandle.ScanErrorExtraInformation)
| order by GeneratedTimestamp desc
```

#### 看ACR的push操作记录

```kusto
//看ACR的push操作记录
ContainerVA_RegistryImageEvents
| where SubscriptionId == '12345678-1234-4000-8000-000000000095'
```

### ACI

#### HttpIncomingRequests

```kusto
//=========ACI===================
let starttime = datetime(2023-09-11 22:00:00);
let endtime = datetime(2022-09-12 10:10:00);
cluster('acimooncake.chinaeast2.kusto.chinacloudapi.cn').database('acimooncake').HttpIncomingRequests
| where PreciseTimeStamp >= ago(8h)
| where subscriptionId == "12345678-1234-4000-8000-000000000096"
//| where targetUri contains "qi"
| where correlationId == "12345678-1234-4000-8000-000000000097"
//| where httpMethod == "PUT"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp, TaskName, durationInMilliseconds, errorMessage, errorCode, httpMethod, operationName, serviceRequestId, httpStatusCode, subscriptionId, ActivityId, targetUri, correlationId, exceptionMessage, clientIpAddress
```

---

## MDC

> [!tip]
> Key tables: ==ServiceFabricIfxTraceEvent==, ==AssessmentsNonAggregatedStatusSnapshot==, ==SubscriptionActivityQueryOE==

### Exemptions and subscription activity

#### List successfully created exemptions

```kusto
//List successfully created exemptions
cluster('rometelemetrydata.kusto.windows.net').database('RomeTelemetryProd').GetRomeClientTelemetry()
| where timestamp  > ago(5d)
| where event_Name == "Exemption created successfully on recommendation"
| extend customObject = parse_json(customDimensions)
| extend SubscriptionsId = customDimensions.selectedSubscriptions
| extend ExemptionName = customDimensions.ExemptionName
| extend ResourceId = customDimensions.resourceId
| extend ResourceName =  split(ResourceId, "/")[-1], ResourceType = split(ResourceId, "/")[-2]
| extend AssessmentKey = customDimensions.assessmentKey
| extend ExemptionReason = customDimensions.category
| where SubscriptionsId has "{subscriptionId}"
| project timestamp, event_Name, operation_Name, ExemptionName, ExemptionReason, SubscriptionsId, ResourceName, ResourceType, AssessmentKey, ResourceId
```

#### ServiceFabricIfxTraceEvent

```kusto
//#connect "https://romelogsmc.kusto.chinacloudapi.cn/Prod"
let subscriptionId = "12345678-1234-4000-8000-000000000098";
let startTime = datetime(2022-09-06 00:50:00);
ServiceFabricIfxTraceEvent
| where env_time between (startTime .. (startTime +24h))
//| where message contains subscriptionId// and message contains " MFA "// and message contains userOid
| where message contains "recommendation" and message contains "Log Analytics"
| project env_time, message
```

#### romelogsmc

```kusto
//romelogsmc
let subscriptionId = "12345678-1234-4000-8000-000000000099";
SubscriptionActivityQueryOE
| where env_time > ago(30d)
| where SubscriptionId == subscriptionId
| summarize arg_max(env_time, *) by ActivityStatus
| project env_time, ActivityStatus
```

#### DynamicWithSubscriptionOE

```kusto
let subscriptionId = "12345678-1234-4000-8000-000000000099";
DynamicWithSubscriptionOE
| where env_time > ago(2d)
| where SubscriptionId == subscriptionId and operationName == 'IdentityScanner'
| project env_time, customData, rootOperationId
| sort by env_time desc
```

### Assessment traces

#### TraceEvent

```kusto
let rootOperationId = "{rootOperationId}";
TraceEvent
| where env_time > ago(2d)
| where env_cv has rootOperationId
| where tagId has "IdentityScanner" or tagId has "IdentityUtils" or tagId has "IdentityDesignateMoreThanOneOwner" or tagId has "IdentityDesignateLessThanXOwners" or tagId has "IdentityRemoveDeprecatedAccounts" or tagId has "IdentityRemoveExternalAccountsWithPermissions" or tagId has "IdentityEnableMFAForAccountsWithPermissions"
| project env_time, message
```

#### DynamicOE

```kusto
//continue to validate that the assessments were correctly sent to the ingestion platform
let assessmentKey = "12345678-1234-4000-8000-000000000100";
let subscriptionId = "12345678-1234-4000-8000-000000000099";
DynamicOE
| where env_time > ago(30d)
| where operationName == "SendSubAssessmentsAsync"
| where customData has subscriptionId
| where customData has assessmentKey
| project env_time, customData
```

#### AssessmentsNonAggregatedStatusSnapshot

```kusto
//
AssessmentsNonAggregatedStatusSnapshot
| where SubscriptionId == "{subscriptionId}"
| extend  AssessedResourceName = split(AssessedResourceId, "/")[-1], AssessedResourceType = split(AssessedResourceId, "/")[-2]
| summarize arg_max(Timestamp, *) by AssessedResourceId
| project Timestamp, AssessmentKey, AssessmentsDisplayName, ReleaseState, AssessedResourceName, AssessedResourceType, StatusCode, StatusCause, StatusDescription, StatusChangeDate, FirstEvaluationDate , AssessedResourceId
```

#### RecommendationsData(31d,0d)

```kusto
RecommendationsData(31d,0d)
 | where AssessmentDisplayName has "Cognitive Services accounts should enable data encryption with a customer-managed key (CMK)"
```

---

## CRP

> [!tip]
> Key tables: ==ApiQosEvent==, ==ContextActivity==, ==VMApiQosEvent==, ==DCMNMAgentProgrammingDurationEtwTable==

### VM operations

#### CRP operation

```kusto

//----------------CRP operation---------------------------------------------------
// Check VM deployment time
//Execute: [Web] [Desktop] [Web (Lens)] [Desktop (SAW)] https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc
ApiQosEvent_nonGet
| where subscriptionId == "12345678-1234-4000-8000-000000000055"
| where PreciseTimeStamp >=  datetime(2023-04-20)
| where resourceName in ( "9d3574460a204df395cb56a37858a09b")
| where operationName == "VirtualMachines.ResourceOperation.PUT"
| project PreciseTimeStamp, resourceGroupName, resourceName, e2EDurationInMilliseconds
| order by PreciseTimeStamp asc
```

#### Check VM start timeout

```kusto
//Check VM start timeout
VMApiQosEvent
| where TIMESTAMP >= datetime(2022-04-12T00:00:00.0000000Z) and TIMESTAMP <= datetime(2022-12-31T16:00:00.0000000Z)
| where ((* has @'12345678-1234-4000-8000-000000000101' and * has @'wps1_') ) and errorDetails contains "VMStartTimedOut" //|and * has @'exception')
| extend error = parse_json(errorDetails)
//| project TIMESTAMP,resourceName, correlationId,operationName,errorDetails
| project PreciseTimeStamp, operationId, correlationId, operationName, resultCode, resourceName, errorDetails, subscriptionId, RPTenant
```

#### ApiQosEvent

```kusto
cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ApiQosEvent
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
//| where resourceGroupName contains "example-resourcegroupname-4"
//| where resourceName contains "example-resourcename-5"
//| where operationName contains "Disk"
//| where resultCode contains "ProvisioningError"
| where correlationId == "12345678-1234-4000-8000-000000000015"
| extend error = parse_json(errorDetails)
| project PreciseTimeStamp, operationId, correlationId, operationName, resultCode, resourceName, resourceGroupName, errorDetails, userAgent, requestEntity, subscriptionId, region, RPTenant, msg=tostring(error.message)
```

### Operation detail and guest events

#### Check the detailed process of an operation

```kusto
//--------------------Check the detailed process of an operation---------------------------------------
//--------------activityID = Operation ID got from ApiQosEvent ------------------------------------
cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity
| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:00:00)
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
| where activityId == "12345678-1234-4000-8000-000000000102"
//| where message contains "fail"
| project PreciseTimeStamp, activityId, message, traceCode, subscriptionId, goalStateResourceId
```

#### ContextActivity

```kusto
cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where subscriptionId == "12345678-1234-4000-8000-000000000013"
| where activityId == "12345678-1234-4000-8000-000000000103"
| project PreciseTimeStamp, activityId, message, traceCode, subscriptionId, goalStateResourceId
```

#### DCMNMAgentProgrammingDurationEtwTable

```kusto
let queryFrom = datetime("2022-12-19T00:40:31.000Z");
let queryTo = datetime("2022-12-19T01:23:00.000Z");
let queryContainerId = "12345678-1234-4000-8000-000000000023";
let queryNodeId = "12345678-1234-4000-8000-000000000018";
cluster("https://azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| where interfaceId contains queryContainerId
| project PreciseTimeStamp, nodeId, interfaceId, message
| order by PreciseTimeStamp asc
```

---

## Backup + ASR

> [!tip]
> Key tables: ==BMSProtectionStats==, ==SRSShoeboxEvent==, ==SRSOperationEvent==, ==HvrDsTelemetryStats==

### Backup

#### backup

```kusto
//=======backup=================
let _resId="/subscriptions/12345678-1234-4000-8000-000000000104/resourceGroups/Backup/providers/Microsoft.RecoveryServices/vaults/AzureCloudBackup";
union cluster('mabprod1').database('MABKustoProd1').BMSProtectionStats,
 cluster('mabprodweu').database('MABKustoProd').BMSProtectionStats,
 cluster('mabprodwus').database('MABKustoProd').BMSProtectionStats
| where ResourceId  == _resId
//| where OperationName == "BackupManagementSoftDelete"
| project StartTime,DataSourceId,DataSourceType,ContainerType,ContainerUniqueName,SubscriptionId,RequestId,TaskId,OperationName
```

#### EventLog

```kusto
// https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
EventLog
| where PreciseTimeStamp >= datetime(2023-06-29 04:00:00) and PreciseTimeStamp <= datetime(2023-07-07 06:00:00)
| where DataSourceId contains "1234546780000000001"
| where RequestId contains "12345678-1234-4000-8000-000000000105"
```

#### DatasourceSummaryStats

```kusto
// https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
DatasourceSummaryStats
| where PreciseTimeStamp >= datetime(2023-06-20 04:00:00) and PreciseTimeStamp <= datetime(2023-07-7 06:00:00)
| where DataSourceId == "1234546780000000001"
```

#### SubscriptionDetailsStats

```kusto
SubscriptionDetailsStats
| where SubscriptionId contains "12345678-1234-4000-8000-000000000104"
```

#### CBPRecoveryStatsTelemetry

```kusto
CBPRecoveryStatsTelemetry
| where DatasourceId == "1234546780000000001"
```

#### TraceLogMessage

```kusto
TraceLogMessage
| where PreciseTimeStamp >= datetime(2023-06-30 00:00:00) and PreciseTimeStamp <= datetime(2023-07-01 06:00:00)
| where DeploymentName contains "bjb-pod01"
| where DataSourceId == "1234546780000000001"
| where RequestId contains "12345678-1234-4000-8000-000000000105"
```

#### AzureBackupReportingData

```kusto
//let _resId="/subscriptions/12345678-1234-4000-8000-000000000106/resourceGroups/Halo_DEV/providers/Microsoft.KeyVault/vaults/HALODEV";
let _subId="12345678-1234-4000-8000-000000000104";
let subFilter=strcat("/subscriptions/",_subId,"/");
AzureBackupReportingData
| where PreciseTimeStamp >= datetime(2023-06-20 00:00:00) and PreciseTimeStamp <= datetime(2023-06-30 23:30:00)
| where resourceId startswith subFilter
| extend Data = parse_json(properties), telData = parse_json(TelemetryProperties)
//| where operationName == "BackupItem"
//| where tostring(Data.BackupManagementType) in ("IaaSVM","AzureWorkload")
// | where tostring(telData.ResourceId) == _resId
//| where tostring(telData.IsScheduledForDeferredDelete) == "True"
| project ResourceId = tostring(telData.ResourceId),ContainerUniqueName = tostring(Data.BackupItemName), ContainerType = strcat(tostring(Data.BackupManagementType),"Container"),
DsType = tostring(Data.BackupItemType),dsId = tostring(telData.Id), ProtectionState = tostring(Data.ProtectionState),IsScheduledForDeferredDelete = tostring(telData.IsScheduledForDeferredDelete),TimeWhenDeleteWasTrigerred = tostring(telData.DeferredDeleteSyncTimeInUTC),
TimeRemainingForFinalPurge = tostring(telData.deferredDeleteTimeRemaining),
HasWarningPeriodCrossed = tostring(telData.isDeferredDeleteScheduleUpcoming),
HasSoftDeletedPeriodCrossed = tostring(telData.hasCrossedDeferredDeleteRetentionPeriod),PreciseTimeStamp//,resourceId
| summarize arg_max(PreciseTimeStamp, *) by dsId,TimeWhenDeleteWasTrigerred
```

#### **context

```kusto
//**context
//armmcadx - armmc
EventServiceEntries
| where TIMESTAMP >ago(30d)
| where subscriptionId contains "12345678-1234-4000-8000-000000000104"
| where operationName contains "Microsoft.RecoveryServices"
//| where status == "Failed"
| project PreciseTimeStamp, status,subscriptionId, operationName , resourceUri, RoleLocation//, correlationId ,properties
//| order by
```

#### union cluster('mabprod1').database('MABKustoProd1').BCM

```kusto
union cluster('mabprod1').database('MABKustoProd1').BCMBackupStats,
union cluster('mabprodwus').database('MABKustoProd').BCMBackupStats,
cluster('mabprodweu').database('MABKustoProd').BCMBackupStats
| where SubscriptionId == "12345678-1234-4000-8000-000000000104"
| where VMName == "AzureCloudBackup"
| where PreciseTimeStamp >= datetime(2023-06-12 00:00:00) and PreciseTimeStamp <= datetime(2023-06-30 23:30:00)
| project TIMESTAMP, VMName , DeploymentName, IsInstantRPEnabled , IsScheduledBackup , RPExpiryTime , DataSourceId , ResourceId , ContainerId , ContainerName, RecoveryPointId , TaskId
```

### ASR process server and replication

#### CFG/ProcessServer Information

```kusto
//====================ASR================================
//#connect "https://asradxclusmc.chinanorth2.kusto.chinacloudapi.cn/ASRKustoDB"
// CFG/ProcessServer Information
let SubscriptionId="12345678-1234-4000-8000-000000000107";
SRSShoeboxEvent
| where PreciseTimeStamp >= ago(7d)
| where category == "AzureSiteRecoveryFabric"
| parse resourceId with *'/SUBSCRIPTIONS/'SubscriptionId'/RESOURCEGROUPS'*
| extend SubscriptionId = tolower(SubscriptionId)
| where SubscriptionId == SubscriptionId
| extend x = parse_json(properties)
//| project PreciseTimeStamp, level, x
| extend configServerName=tostring(x.name),
         configServerNameLastHeartbeat=todatetime(x.lastHeartbeat),
         processServerCount=tolong(x.processServerCount),
         CSHostId=tostring(x.id),
         CSIpAddr=tostring(x.ipAddress),
         CSProtectedServers=tolong(x.protectedServers)
| mv-expand processServer=x.processServers
| extend processServerName=tostring(processServer.name),
         processServerLastHeartbeat=todatetime(processServer.lastHeartbeat),
         PSHostId=tostring(processServer.hostId),
         PSIpAddr=tostring(processServer.ipAddress),
         PSProtectedServerCount=tolong(processServer.serverCount),
         PSReplicationPairCount=tolong(processServer.replicationPairCount)
| project PreciseTimeStamp, level, configServerName, CSIpAddr, CSHostId, configServerNameLastHeartbeat, CSProtectedServers, processServerCount,
processServerName,PSIpAddr, PSHostId, processServerLastHeartbeat, PSProtectedServerCount, PSReplicationPairCount //, processServer
| summarize max(processServerLastHeartbeat), max(configServerNameLastHeartbeat) by configServerName, CSIpAddr, CSHostId, CSProtectedServers,
processServerName, PSIpAddr, PSHostId, PSProtectedServerCount, PSReplicationPairCount
//| where processServerName contains "example-processservername-1" or processServerName contains "AVTA"
//| where configServerName contains "example-configservername-1"
```

#### Process Server Heartbeat in SRS Telemetry

```kusto
//Process Server Heartbeat in SRS Telemetry
let SubscriptionId="12345678-1234-4000-8000-000000000108";
SRSShoeboxEvent
| where PreciseTimeStamp > datetime(2021-08-14 13:30) and PreciseTimeStamp < datetime(2021-08-14 23:30)
| where category == "AzureSiteRecoveryFabric"
| parse resourceId with *'/SUBSCRIPTIONS/'SubscriptionId'/RESOURCEGROUPS'*
// | extend SubscriptionId = tolower(SubscriptionId)
| where SubscriptionId == SubscriptionId
| extend x = parse_json(properties)
//| project PreciseTimeStamp, level, x
| extend configServerName=tostring(x.name),
         configServerNameLastHeartbeat=todatetime(x.lastHeartbeat),
         processServerCount=tolong(x.processServerCount)
| mv-expand processServer=x.processServers
| extend processServerName=tostring(processServer.name),
         processServerLastHeartbeat=todatetime(processServer.lastHeartbeat)
//| where properties contains "ServerHealth" and properties contains "Process Server"
| project PreciseTimeStamp, level, configServerName, configServerNameLastHeartbeat, processServerCount, processServerName, processServerLastHeartbeat //, processServer
// | summarize max(processServerLastHeartbeat), max(configServerNameLastHeartbeat) by configServerName, processServerName
| where processServerName  contains "example-processservername-2"
```

#### PS Register disappear INFO

```kusto
//PS Register disappear INFO
//Execute: [Web] [Desktop] [Web (Lens)] [Desktop (SAW)] https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
database('MABKustoProd').InMageAdminLogV2
| where MachineId == "12345678-1234-4000-8000-000000000137" //or MachineId == "12345678-1234-4000-8000-000000000138"
| where PreciseTimeStamp > datetime(2021-08-14 13:30) and PreciseTimeStamp < datetime(2021-08-14 23:30)
//|where PreciseTimeStamp >datetime(2021-09-01 07:20:20.8560085)
| where Message contains "ProcessServer Registration"
| where SubComponent contains "PSCore/TaskMgr"
 | project PreciseTimeStamp, AgentTimeStamp, MachineId, SubComponent, AgentPid, AgentLogLevel, Message
| sort by PreciseTimeStamp desc nulls last
```

#### 查看复制的项的健康状态

```kusto
//查看复制的项的健康状态
SRSShoeboxEvent
| where PreciseTimeStamp between (ago(24h) .. now())
| where category == "AzureSiteRecoveryReplicatedItems"
| extend parsedProperties = parsejson(properties)
| parse resourceId with *'/SUBSCRIPTIONS/'SubscriptionId'/RESOURCEGROUPS'*
| extend SubscriptionId = tolower(SubscriptionId)
| where SubscriptionId == "12345678-1234-4000-8000-000000000109"
| extend HostId=tostring(parsedProperties.id)
| extend SourceVmName=tostring(parsedProperties.name)
| extend ReplicationHealth=tostring(parsedProperties.replicationHealth)
//| where ReplicationHealth == "Critical/Warning/Normal"
//| where SourceVmName contains "<HostName>"
//| where HostId == "<HostId>"
| summarize arg_max(PreciseTimeStamp, *) by tostring(parsedProperties.correlationId)
| project PreciseTimeStamp, ProtectedItemName=tostring(parsedProperties.name), ProtectionState=tostring(parsedProperties.protectionState), ReplicationHealth=tostring(parsedProperties.replicationHealth),OS=tostring(parsedProperties.osFamily), PS = tostring(parsedProperties.primaryFabricName), Provider = tostring(parsedProperties.primaryFabricType),ReplicationhealthErrors=parsedProperties.replicationHealthErrors, AgentLastHeartbeat=parsedProperties.lastHeartbeat,StorageAccount = tostring(parsedProperties.targetStorageAccountName), AgentVersion = tostring(parsedProperties.agentVersion)
```

#### InMageTelemetryPSV2

```kusto
InMageTelemetryPSV2
| where HostId == "12345678-1234-4000-8000-000000000110"
| summarize max(PreciseTimeStamp) by PSHostId, HostId , DiskId
```

#### SRSOperationEvent

```kusto
SRSOperationEvent
| where SubscriptionId== "12345678-1234-4000-8000-000000000107"
//| where WorkflowName contains"cert"
| where ObjectName contains "example-objectname-1"
//| where State contains "Failed"
| where TIMESTAMP between( datetime(2023-07-11 00:00:00)..datetime(2023-07-13 23:00:30))
//| project TIMESTAMP,StampName,ClientRequestId,State,WorkflowName,ObjectType,ObjectName, EventMessage
```

### Backlog and RPO

#### check backlog

```kusto
// check backlog
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(3h)
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1234546780000000002") //projectstorage01
//|where DataSourceId in ( "1234546780000000002", "1234546780000000003", "1234546780000000004")
//|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState//| sort by RPOtime desc
| where DiskId == "DATADISK19"
| project PreciseTimeStamp, VmName, BacklogSessionCount, RPOMins, DiskId
```

#### check RPO

```kusto
//check RPO
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(2h)
//|where LatestRpMarkerId != 'null'
| where DataSourceId in ( "1234546780000000002", "1234546780000000003", "1234546780000000004")
| summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState, DataSourceId
| sort by RPOtime desc//| project VmName, DiskId, VhdReplicationState, PreciseTimeStamp
```

#### check RPO

```kusto
//check RPO
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(4h)
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1234546780000000002", "1234546780000000003", "1234546780000000004")
|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState, DataSourceId
| sort by RPOtime desc
//| project VmName, DiskId, VhdReplicationState, PreciseTimeStamp
```

#### disk7 的backlog增减

```kusto
//disk7 的backlog增减
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(13h)
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1234546780000000003")
//|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState//| sort by RPOtime desc
| where DiskId == "DATADISK7"
| project PreciseTimeStamp, VmName, BacklogSessionCount, RPOMins, DiskId
```

#### check errors

```kusto
// check errors
let enumToCodeTable = cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SrsErrorEnumToCode();
SRSShoeboxEvent
| where PreciseTimeStamp > ago(48h)
| extend VmDay=bin(PreciseTimeStamp, 24h)
| where category == "AzureSiteRecoveryReplicatedItems"
| parse resourceId with *'/SUBSCRIPTIONS/'SubId'/RESOURCEGROUPS'*
//| parse resourceId with *'/SUBSCRIPTIONS/12345678-1234-4000-8000-000000000111/RESOURCEGROUPS'*
| extend SubscriptionId = tolower("12345678-1234-4000-8000-000000000107")
| where SubscriptionId == "12345678-1234-4000-8000-000000000107"
| extend x = parse_json(properties)
| extend ReplicationProvider = tostring(x.replicationProviderName)
//| where ReplicationProvider == "V2A"
| extend ProtectionState=tostring(x.protectionState)
//| where ProtectionState == "Protected"
| extend ReplicationHealth=tostring(x.replicationHealth)
//| where ReplicationHealth == "Critical"
//| project x | take 1
| extend HostId=tostring(x.id)
| extend SourceAgentVersion=tostring(x.agentVersion)
| extend SourceVmName=tostring(x.name)
| where SourceVmName contains "example-objectname-1"
| extend OsFamily=tostring(x.osFamily)
| extend PSHostId=tostring(x.processServerName)
| extend LastHeartBeat=tostring(x.lastHeartbeat)
| extend RpoInSecs=tostring(x.rpoInSeconds)
| extend HealthIssues = x.replicationHealthErrors
| mvexpand HealthIssues
| extend ErrorCode = tolong(HealthIssues.errorCode)
| extend ErrorCreationTime = todatetime(HealthIssues.creationTime)
//| where ErrorCreationTime > ago(1h)
| join kind=leftouter enumToCodeTable on ErrorCode
//| project PreciseTimeStamp , HostId, HealthIssues
//| summarize dcount(HostId) by PSHostId, EveryHalfHour
//| render timechart
| summarize makeset(ErrorCodeEnum), makeset(ErrorCode) by TIMESTAMP, SubscriptionId, SourceVmName, HostId, PSHostId , SourceAgentVersion, ProtectionState, ReplicationHealth //, RpoInSecs  //, ErrorCodeEnum
//| summarize StartTime=min(ErrorCreationTime), EndTime=max(PreciseTimeStamp) by SubscriptionId, SourceVmName, HostId , SourceAgentVersion, ProtectionState, ErrorCode , ErrorCodeEnum
```

#### SRSDataEvent

```kusto
SRSDataEvent
| where SubscriptionId == "12345678-1234-4000-8000-000000000107"
| where ClientRequestId == "12345678-1234-4000-8000-000000000112"
| where TIMESTAMP between ( datetime(2023-07-12 00:00:00)..datetime(2023-07-12 23:00:30))
| project PreciseTimeStamp, LogLevel, Message
```

### Enable protection failures

#### get all replication jobs in subscription

```kusto
// get all replication jobs in subscription
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSOperationEvent
| where SubscriptionId == "12345678-1234-4000-8000-000000000113"
| where PreciseTimeStamp >= datetime(2023-03-06 08:00:00) and PreciseTimeStamp < datetime(2023-03-08 10:50:00)
| sort by PreciseTimeStamp asc
| project PreciseTimeStamp, ServiceName, ClientRequestId, SRSOperationName, State,  ObjectType, ObjectName, Region, ContainerId , ResourceId  , TimeTaken
```

#### check job details using job id.

```kusto
 // check job details using job id.
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent
| where ClientRequestId == "12345678-1234-4000-8000-000000000114"  // job id
//| where Level <= 3
| project PreciseTimeStamp,Message, Level
```

#### **** Check SRS all operation flow

```kusto
// **** Check SRS all operation flow
// **** A2AEnableProtectionTargetWorkflow
// **** A2AInstallMobolitrServiceWorkFlow
// **** A2ACreateProtectionTargetWorkflow
// **** A2AStartInitialReplicationWorkflow
// **** CompleteInitialReplicationWorkflow * 2
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent
| where ClientRequestId == "12345678-1234-4000-8000-000000000114" // projectstorage01
| where Message contains "SRS operation Started. | Params: {Operation = "  or  Message contains "SRS operation Completed. | Params: {Operation = "
| project  PreciseTimeStamp, Message, Level
| sort by PreciseTimeStamp asc
```

#### ***** Get Extension Install log

```kusto
// ***** Get Extension Install log
// ***** /var/log/azure/Microsoft.Azure.RecoveryServices.SiteRecovery.xxx
// ***** (Key Words: Logging extensionlog with continuation id: xxxx )
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent
| where ClientRequestId == "12345678-1234-4000-8000-000000000114" // projectstorage01
| where Message contains "Logging extensionlog with continuation id"
//| where Message contains "12345678-1234-4000-8000-000000000115"  //continuation id of above query
| project  PreciseTimeStamp, Message, Level
| sort by PreciseTimeStamp asc
```

---

## Monitor + Automation

> [!tip]
> Key tables: ==LogContainerSnapshot==, ==WindowsEventTable==, ==TMMgmtNodeTraceEtwTable==, ==ControlPlaneEvents==, ==ApiQosEvent_nonGet==

### Node and disk monitoring

#### Query all kind of IDs

```kusto
//---------------------- Query all kind of IDs -------------------------------------------------------
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2022-10-30 00:00:00.0000000) and PreciseTimeStamp <= datetime(2022-11-01 06:40:00.0000000)
| where subscriptionId == "12345678-1234-4000-8000-000000000001" //and roleInstanceName contains "cn2-prd-commerce-elasticsearch-catalog-tr1-elkdata_126"
| where availabilitySetName == ""
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName
```

#### different WindowsEventTable

```kusto
//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
| where PreciseTimeStamp > ago(3d)
| where NodeId in~ ('12345678-1234-4000-8000-000000000116')
| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170',155,15)
| where ProviderName contains "UpdateNotification" or ProviderName contains "OSHostPlugin"
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId
```

#### Check update end time

```kusto
//Check update end time
TMMgmtNodeTraceEtwTable
| where PreciseTimeStamp >= datetime(10/31/2022 07:00:00) and PreciseTimeStamp <= datetime(2022-10-31 09:59:06)
| where BladeID == "12345678-1234-4000-8000-000000000116"
| where Message contains "VmphuPF"
//| where Message contains "20221013_pf2_win_ah2021_497_144_0_10_509"
| project TIMESTAMP, Tenant, BladeID, Message
| sort by TIMESTAMP  asc nulls last
```

#### Check update accurate timeline

```kusto
//Check update accurate timeline
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(10/31/2022 07:00:00) and PreciseTimeStamp <= datetime(2022-10-31 08:48:00)
| where NodeId == "12345678-1234-4000-8000-000000000117"
//| where Message contains "ImageName"
//| where Message contains "OSHP Deployment Team"
| where Message contains "phu"
//| where Message contains "12345678-1234-4000-8000-000000000118"
| summarize arg_min(PreciseTimeStamp, *) by NodeId
| project PreciseTimeStamp , Tenant, NodeId , Message
```

#### DiskRPResourceLifecycleEvent

```kusto
DiskRPResourceLifecycleEvent
| where MonitoringApplication == "DiskRP-chinanorth_Monitoring" //-- Set the Region <DiskRP-<Region>_Monitoring>
| where subscriptionId == "12345678-1234-4000-8000-000000000119" //-- Select the Subscription ID
| where resourceName contains "example-resourcename-6" or resourceName contains "DB" or resourceName contains "PRD"  //-- <Name of the disk. If you don"t have the name of the disk, you could skip this line.>
| where diskEvent contains "SoftDelete"
| where PreciseTimeStamp >= (datetime(2022-11-06)) //-- Choose a time shortly before the disk deletion
| project PreciseTimeStamp, resourceGroupName, resourceName, pseudosubscriptionId, blobUrl, diskEvent, RPTenant
```

#### LogContainerSnapshot

```kusto
LogContainerSnapshot
| where PreciseTimeStamp > datetime(2023-04-16 01:00:00) and PreciseTimeStamp < datetime(2023-04-21 09:00:00)
| where subscriptionId == "12345678-1234-4000-8000-000000000120" and availabilitySetName == "EC2PRDDLBDB-AS"//and roleInstanceName contains "CNCORPAZPDGTM1"
| summarize by roleInstanceName
//| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId
```

#### LogContainerHealthSnapshot

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp > datetime(2023-04-16 01:00:00) and PreciseTimeStamp < datetime(2023-04-21 09:00:00)
| limit 10
```

### AKS resource and control plane traces

#### StartTime = PreciseTimeStamp, Content = strcat(allocati

```kusto
let querySubscriptionId = "12345678-1234-4000-8000-000000000121";
let queryResourceGroupName = "example-resourcegroupname-5";
let queryCreated = datetime("2022-03-11T02:45:53.000Z");
let queryLastSeen = datetime("2023-05-05T20:27:12.000Z");
let queryFrom = datetime("2023-05-05T10:00:00.000Z");
let queryTo = datetime("2023-05-05T23:28:21.000Z");
let crp_operations = VMApiQosEvent
| where PreciseTimeStamp between(max_of(queryFrom, queryCreated) .. min_of(queryTo, queryLastSeen))
| where subscriptionId == querySubscriptionId  and resourceGroupName =~ queryResourceGroupName
| where allocationAction != "None" or operationName contains "restart"
| extend allocationAction = iff(allocationAction != "None", allocationAction, operationName)
| where queryResourceGroupName startswith "hcp-underlay" or resourceName startswith 'aks'
| project
    StartTime = PreciseTimeStamp, Content = strcat(allocationAction, " - ", resourceName), operationId, correlationId,
    allocationAction, resultCode, resultType, resourceName, operationName, durationInMilliseconds, errorDetails
| extend Tooltip = strcat(Content, "<br />CRP OperationId: ", operationId)
| extend Tooltip = strcat(Tooltip, "<br />CRP Correlation ID: ", correlationId)
| order by StartTime asc
| take 1500;
let correlations = crp_operations | distinct correlationId;
crp_operations
| join kind=leftouter (
    cluster("akscn.kusto.chinacloudapi.cn").database("AKSprod").OutgoingRequestTrace
    | where PreciseTimeStamp between(max_of(queryFrom, queryCreated) .. min_of(queryTo, queryLastSeen))
    | where subscriptionID == querySubscriptionId and isnotempty(correlationID)
    | distinct correlationID, operationID
    | project correlationId = correlationID, aks_operation = operationID
) on correlationId
| extend Tooltip = strcat(Tooltip, "<br />AKS Operation ID: ", iff(isnotempty(aks_operation), aks_operation, 'Unknown'))
| project
    StartTime, Content, Tooltip, operationName, aks_operation, operationId, correlationId, resourceName,
    allocationAction, resultCode, durationInMilliseconds, errorDetails
```

#### union ControlPlaneEvents, ControlPlaneEventsNonShoebox

```kusto
let queryClusterVersion = "123454678000000000000004";
let global_startTime = datetime("2023-05-05T14:00:00.000Z");
let global_endTime = datetime("2023-05-05T20:28:21.000Z");
union ControlPlaneEvents, ControlPlaneEventsNonShoebox
| where PreciseTimeStamp >= global_startTime and PreciseTimeStamp < global_endTime
| where ccpNamespace == queryClusterVersion
| where category == 'kube-audit'
//| where properties has 'terminated'
| extend log=parse_json(tostring(parse_json(properties).log))
| extend cs=log.requestObject.status.containerStatuses[0]
| where cs.lastState.terminated.reason !in ('', 'Completed')
| project
    PreciseTimeStamp,
    reason = cs.lastState.terminated.reason,
    exitCode = cs.lastState.terminated.exitCode,
    image = cs.image,
    container = cs.containerID,
    pod = tostring(log.objectRef.name),
    ns = log.objectRef.namespace,
    restartCount = cs.restartCount,
    startedAt = todatetime(cs.lastState.terminated.startedAt),
    finishedAt = todatetime(cs.lastState.terminated.finishedAt),
    cs.lastState.terminated.message,
    log.user.username,
    log.userAgent,
    log.requestUri,
    log.verb
| summarize PreciseTimeStamp = arg_max(PreciseTimeStamp, reason, finishedAt) by pod
| order by finishedAt desc
| extend Tooltip = strcat(reason, " - ", pod)
| extend Content = Tooltip
| project StartTime = PreciseTimeStamp, Content, Tooltip
| take 1500
```

#### ApiQosEvent_nonGet

```kusto
let queryFrom = datetime("2023-05-05T17:00:00.000Z");
let queryTo = datetime("2023-05-05T20:28:21.000Z");
let querySubscription = "12345678-1234-4000-8000-000000000121";
let queryManagedRg = "example-resourcegroupname-5";
let queryFilter = "";
ApiQosEvent_nonGet
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId == querySubscription
| where resourceGroupName =~ queryManagedRg
| where not(queryFilter == 'errors') or isnotempty(errorDetails)
| extend level = case(
    httpStatusCode >= 400 or isnotempty(errorDetails), "warning",
    "info"
)
| extend labelsJSON = parse_json(tostring(labels))
| extend requestJSON = parse_json(tostring(requestEntity))
| extend resourceInstanceId = tostring(split(resourceName, "/")[1])
| extend instanceIds = coalesce(
    array_strcat(requestJSON.instanceIds, ", "),
    tostring(split(split(requestEntity, '"instanceId": "')[1], '"')[0]),
    resourceInstanceId
)
| extend e2EDurationInSeconds = round(e2EDurationInMilliseconds / 1000)
| extend isPortal = userAgent has "Chrome/" or userAgent has "Mozilla/" or userAgent has "AppleWebKit/"
| extend dataDisks = requestJSON.properties.storageProfile.dataDisks
| mv-apply diskAction = dataDisks on (
    extend action = diskAction.createOption
    | summarize actions = strcat_array(make_set(action), ",")
 )
| extend diskAction = case(actions has "Attach", "Attach Disk (CSI)", "Detach Disk (CSI)")
| extend source = case(
    isPortal, "Portal",
    userAgent == "123-45-012", "Geneva Action",
    userAgent has "microsoft.com/aks-remediator", "Remediator",
    userAgent has "disk.csi.azure.com/", diskAction,
    userAgent has "AKS-VMSS-Client", "AKS-VMSS-Client",
    userAgent has "azure-resource-manager/" and operationName has "Deployments.Preflight.POST", "ARM Deployment",
    ""
)
| project PreciseTimeStamp, source, resourceName, correlationId, operationId, userAgent, operationName,
    errorDetails, e2EDurationInSeconds, durationInMilliseconds, httpStatusCode,
    resultCode, clientApplicationId, requestJSON, instanceIds, level, exceptionType,
    labelsJSON
| order by PreciseTimeStamp desc
```

### Host storage diagnostics

#### OsFileVersionTable

```kusto
OsFileVersionTable
| where Cluster == "example-cluster-2" and PreciseTimeStamp >= ago(30d) and NodeId  == "12345678-1234-4000-8000-000000000122"
| where FileName contains "blobcache.sys"
| summarize dcount(NodeId) by FileName, FileVersion
```

#### OsFileVersionTable

```kusto
OsFileVersionTable
| where Cluster == "example-cluster-3" and PreciseTimeStamp >= ago(30d)
| where FileName contains "blobcache.sys"
| summarize dcount(NodeId) by FileName, FileVersion// between (datetime(2023-04-25 00:00:00) ..12h)
//| project PreciseTimeStamp, OsDiagDurationInSec
```

#### HyperVStorageStackTable

```kusto
//rdos
let StartTime = datetime(2023-04-24 01:00:00);
let endTime = datetime(2023-04-24 03:00:00);
HyperVStorageStackTable
| where PreciseTimeStamp > StartTime and PreciseTimeStamp < endTime
| where NodeId == '12345678-1234-4000-8000-000000000123'
| where EventMessage contains '12345678-1234-4000-8000-000000000124' //container id
| where EventId == 9
| project PreciseTimeStamp, NodeId, EventId, EventMessage, Message
```

#### OsRDSSDSurfaceCounterTable

```kusto
let startTime = datetime("2023-04-24T01:00:00.000Z");
let endTime = datetime("2023-04-24T03:00:00.000Z");
let nodeId = "12345678-1234-4000-8000-000000000123";
OsRDSSDSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where SurfaceName contains "12345678-1234-4000-8000-000000000124"
| project PreciseTimeStamp, BlobPath, SurfaceName, HighIOLatInms, CurIOLatInms
```

#### VhdDiskEtwEventTable

```kusto
let startTime = datetime("2023-04-24T01:00:00.000Z");
let endTime = datetime("2023-04-24T03:00:00.000Z");
let nodeId = "12345678-1234-4000-8000-000000000123";
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and EventId  == 13 and EventMessage contains "dcf40vfhwsn5"
| project PreciseTimeStamp, EventId, EventMessage
```

#### StorPort 504/505 错误汇总

```kusto
let queryFrom = datetime("2023-04-24T01:30:00.000Z");
let queryTo = datetime("2023-04-24T02:30:45.000Z");
let queryNodeId = "12345678-1234-4000-8000-000000000123";
let event504 = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "There were " Errors:long "total errors" *
| where Errors > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId,DiskDeviceGuid, Errors, Description;
let event504unqiue = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| where Description contains "few unique errors"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" *
| extend Errors = 1
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId,DiskDeviceGuid, Errors, Description;
let event505 = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 505 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "The IO failed counts are" bucket1:long "," bucket2:long "," bucket3:long "," bucket4:long "," bucket5:long
    "," bucket6:long "," bucket7:long "," bucket8:long "," bucket9:long "," bucket10:long
    "," bucket11:long "," bucket12:long "," bucket13:long "," bucket14:long *
| extend  Errors =   bucket1 + bucket2 + bucket3 + bucket3 + bucket4 + bucket5 + bucket6 + bucket7 + bucket8 + bucket9 + bucket10 + bucket11 + bucket12  +  bucket13  +  bucket14
| where Errors > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, DiskDeviceGuid, Errors, Description;
union event504, event505, event504unqiue
| order by TimeCreated asc
```

### Pod and ARM events

#### union

```kusto
let queryCcpNamespace = "123454678000000000000004";
let querynode = "example-node-1";
union
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEvents,
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp >= datetime(2023-05-05 00:30:00) and PreciseTimeStamp <= datetime(2023-05-05 23:30:00)
| where ccpNamespace == queryCcpNamespace and properties has querynode
| where category == 'kube-audit'
| extend log = parse_json(tostring(parse_json(properties).log))
| where log.objectRef.resource == 'pods' and log.stage == "ResponseComplete"
| extend level = tostring(log.level)
| extend verb = tostring(log.verb)
| extend user = tostring(log.user.username)
| extend namespace = tostring(log.objectRef.namespace)
| extend name = tostring(log.objectRef.name)
| extend userAgent = tostring(log.userAgent)
| extend nodeName = case(
  verb == "create", tostring(log.reauestObject.target.name),
  level == "RequestResponse" and verb != "create", tostring(log.responseObject.spec.nodeName),
  level == "RequestResponse", tostring(log.responseObject.spec.nodeName),
  tostring(split(log.user.username, "system:node:")[1]))
 | where isnotempty(nodeName)
 | where namespace contains "kube-system" //and name contains "corends"
 | extend StartTime = PreciseTimeStamp
 | extend Content = strcat(verb, "</br>", userAgent, "</br>", nodeName)
 | project StartTime, Content, verb, user, nodeName, namespace, name, userAgent
 | order by StartTime asc
```

#### EventServiceEntries

```kusto
 EventServiceEntries
| where subscriptionId == "12345678-1234-4000-8000-000000000121"
| where PreciseTimeStamp >= datetime(2023-05-05 17:00:00) and PreciseTimeStamp <= datetime(2023-05-05 19:00:00)
| where resourceUri contains "aks-nodepool3-123454678"//"example-node-1"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp, operationName, resourceProvider, correlationId, status, subStatus, properties, resourceUri, eventName, operationId, armServiceRequestId, subscriptionId, claims
```

#### CN3 NO IP

```kusto
//=====CN3 NO IP=========
 //#connect "https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc"
let uri="/subscriptions/12345678-1234-4000-8000-000000000125/resourceGroups/123-45-013-BPMS-RG-000/providers/Microsoft.Compute/virtualMachines/ucncn3aapp003";
ApiQosEvent
| where TIMESTAMP >= datetime('2023-5-16 00:00:00') and TIMESTAMP <= datetime('2023-5-16 03:05:53')
 | where subscriptionId == split(uri,"/")[2]  and resourceName contains split(uri,"/")[8]
 | where resultCode contains "OSProvisioningTimedOut"
 | order by PreciseTimeStamp asc
 | extend startTime=PreciseTimeStamp-e2EDurationInMilliseconds*1ms
 | extend OperationDuration=e2EDurationInMilliseconds*1ms
 | order by startTime asc
 | project startTime, PreciseTimeStamp, OperationDuration, resourceGroupName, resourceName, operationName,  resultCode, httpStatusCode, operationId,correlationId,
 region, requestEntity, errorDetails
```

#### DCMNMAgentProgrammingDurationEtwTable

```kusto
 //#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
DCMNMAgentProgrammingDurationEtwTable
| where TIMESTAMP >= datetime('2023-5-16 00:00:00') and TIMESTAMP <= datetime('2023-5-16 03:05:53')
| where Tenant  == "example-tenant-3"
| where * contains "12345678-1234-4000-8000-000000000126" //VM ContainerID
| project PreciseTimeStamp,message,interfaceId,programmingDelayInSeconds
```

#### ApiQosEvent

```kusto
ApiQosEvent
| where PreciseTimeStamp between (datetime(2023-05-24T06:00) .. datetime(2023-05-24T07:50))
| where subscriptionId has '12345678-1234-4000-8000-000000000080'
| where resourceName has 'example-resourcename-7'
| where operationName  == "VMScaleSetVMs.VMScaleSetVMsOperation.PUT"
//| where requestEntity has "kubernetes-internal"
| project PreciseTimeStamp,operationName,correlationId, userAgent,requestEntity
```

#### union ControlPlaneEvents, ControlPlaneEventsNonShoebox

```kusto
union ControlPlaneEvents, ControlPlaneEventsNonShoebox
//union cluster('aks.kusto.windows.net').database('AKSccplogs').ControlPlaneEventsNonShoeboxOld,cluster('aks.kusto.windows.net').database('AKSccplogs').ControlPlaneEventsOl
| where PreciseTimeStamp >= datetime(2023-05-24 06:00:00) and PreciseTimeStamp <= datetime(2023-05-24 07:30:30)
| where resourceId has "/subscriptions/12345678-1234-4000-8000-000000000080/resourceGroups/mkvcrmqarg/providers/Microsoft.ContainerService/managedClusters/QAAKSCluster" //or ccpNamespace contains "123454678000000000000005"
| where category has "cloud-controller-manager"
//| where properties has "found unwanted node"
| extend pod = extractjson('$.pod', properties , typeof(string))
| extend logs = extractjson('$.log', properties , typeof(string))
| extend jlogs = parse_json(logs)
//| extend stage = jlogs.stage
//| extend Timestamp = jlogs.requestReceivedTimestamp
| extend RequestURI = jlogs.requestURI
| extend Action = jlogs.verb
//| extend User = jlogs.user.username
| extend UserAgent = jlogs.userAgent
| extend response_code = jlogs.responseStatus.code
| where Action != "watch"
| project PreciseTimeStamp, category, logs
//| take 1000
```

#### WheaXPFMCAFull

```kusto
cluster("sparkle.eastus").database("defaultdb").WheaXPFMCAFull
| limit 10
```

---

## AAD

> [!tip]
> Key tables: ==EventServiceEntries==, ==PerRequestTableIfx==, ==IfxUlsEvents==, ==IfxBECAuthorizationManager==

### Role assignments and tenant events

#### Role assignment creation or deletions

```kusto

// Connection = https://armmcadx.chinaeast2.kusto.chinacloudapi.cn
// Role assignment creation or deletions
EventServiceEntries
| where subscriptionId == "12345678-1234-4000-8000-000000000067"
| where TIMESTAMP >= ago(30d)
| where operationName has_any ("Microsoft.Authorization/roleAssignments", "Microsoft.Authorization/classicAdministrators")
| project TIMESTAMP, operationName, status, principalOid, principalPuid, subscriptionId, httpRequest, properties, resourceUri, claims
```

#### CertificatesInventory

```kusto
CertificatesInventory
| where TIMESTAMP >= ago(60d)
| where Tenant contains "12345678-1234-4000-8000-000000000127"
```

#### AppHealthEvent

```kusto
AppHealthEvent
| where TIMESTAMP >= ago(60d)
| where Tid == "12345678-1234-4000-8000-000000000127"
```

#### ApplicationEvents

```kusto
ApplicationEvents
| where TIMESTAMP >= ago(60d)
| where Tenant contains "12345678-1234-4000-8000-000000000127"
```

### AAD writes and conditional access

#### 查AAD 写入, 拿到correlation id查details

```kusto
//查AAD 写入, 拿到correlation id查details
//https://msodsmooncake.chinanorth2.kusto.chinacloudapi.cn/MSODS
IfxUlsEvents
| where * has "12345678-1234-4000-8000-000000000128"
| where env_time > datetime(2023-10-25 00:00) and env_time < datetime(2023-10-25 23:00)
//| where message startswith "[Aws::CreateSyncObjectResult]"
| project env_time, message
```

#### 查CA policy

```kusto
//查CA policy
//#connect "https://estscnn2.chinanorth2.kusto.chinacloudapi.cn/ESTS"
let start = datetime(2023-08-07 14:19);
let period = 30min;
PerRequestTableIfx
| where env_time > start - period and env_time < start + period
| where CorrelationId == "12345678-1234-4000-8000-000000000129"
| project env_time, CorrelationId, RequestId, ClientTypeForConditionalAccess, Result, ApplicationId, ResourceId, ErrorCode, ConditionalAccessVerboseData
```

#### Filter with servicePrincipalObjectId or UserObjectId

```kusto
//#connect "https://msodsmooncake.chinanorth2.kusto.chinacloudapi.cn/MSODS"
IfxBECAuthorizationManager
//Filter with servicePrincipalObjectId or UserObjectId
//| where servicePrincipalObjectId == "12345678-1234-4000-8000-000000000130"
//| where tenantName contains "example-tenantname-2"
| where userObjectId contains "12345678-1234-4000-8000-000000000131"
| where env_time > datetime(2023-10-19 00:30) and env_time < datetime(2023-10-20 02:56)
| project env_time, internalCorrelationId, result, parameters, task, scopeClaim, userObjectId, servicePrincipalObjectId, isAppGrantedAccess
```

---

## Health Event

> [!tip]
> Key tables: ==ServiceHealthPublisherCommunications==, ==ServiceHealthTargets==

### Service health lookup

#### Check ServiceHealth

```kusto
// Check ServiceHealth
// https://icmcluster.kusto.windows.net | database("ACM.Publisher")
ServiceHealthPublisherCommunications | where TrackingId == '123-45-014'
```

#### Check ServiceHealth affected subid

```kusto
// Check ServiceHealth affected subid
// need CommunicationId obtained from above
// https://icmcluster.kusto.windows.net | database("ACM.Publisher")
ServiceHealthTargets
|  where CommunicationId == '123454678'
```

---

## AH2021 Patch

> [!tip]
> Key tables: ==OsConfigTable==, ==WindowsEventTable==, ==TMMgmtNodeEventsEtwTable==, ==IridiasTargets==

### Node inventory and patch state

#### 看node和container id

```kusto
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp > datetime(2023-05-14 07:00:00) and PreciseTimeStamp < datetime(2023-05-14 09:00:00)
| where subscriptionId == "12345678-1234-4000-8000-000000000022" and roleInstanceName contains "CNCORPAZPDLDW8"
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId
```

#### 查node是否已经被打上了补丁

```kusto
// 查node是否已经被打上了补丁
let NodeList = datatable(NodeId:string)
[
"12345678-1234-4000-8000-000000000132",
"12345678-1234-4000-8000-000000000133",
"12345678-1234-4000-8000-000000000134",
];
cluster('rdosmc.kusto.chinacloudapi.cn').database('rdos').OsConfigTable
| where TIMESTAMP >= ago(12h)
| where Component == 'cloudcore' and ConfigName == 'buildex'
| where NodeId in (NodeList)
| summarize arg_max(PreciseTimeStamp, *) by ConfigName, NodeId
| extend OSBuild= ConfigValue
| extend Release= case(
    OSBuild startswith "18362.1", '1.8',
    OSBuild startswith "18362.2", '1.85',
    OSBuild startswith "18362.3", '1.86',
    OSBuild startswith "19041", 'AH2020',
    OSBuild startswith "20348.1075", 'AH2021',
    OSBuild startswith "22477.1088", 'AH2022',
    strcat('other', OSBuild))
| project PreciseTimeStamp,Region, Cluster, NodeId, OSBuild, Release
```

### Windows events and node traces

#### different WindowsEventTable

```kusto
//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
| where PreciseTimeStamp >= datetime(2023-11-01 03:20:00) and PreciseTimeStamp <= datetime(2023-11-01 04:00:00)
| where NodeId in~ ('12345678-1234-4000-8000-000000000019')
//| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170','155','15')
//| where EventId == 1
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId
```

#### WindowsEventTable()

```kusto
let queryFrom = datetime("2023-03-12T00:00:11.000Z");
let queryTo = datetime("2023-03-12T06:42:17.000Z");
let queryNodeId = "12345678-1234-4000-8000-000000000135";
//let queryNodeId = "12345678-1234-4000-8000-000000000133";
//let queryNodeId = "12345678-1234-4000-8000-000000000134";
cluster("rdosmc.kusto.chinacloudapi.cn").database("rdos").WindowsEventTable()
| where PreciseTimeStamp  between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where not (ProviderName contains "Kernel-Processor" and EventId == 37) // eliminating periodical processor report event every day.
| where not (ProviderName == "Microsoft-Windows-Kernel-PnP") // eliminating PnP messages
// | where not (ProviderName contains "PnP" and EventId == 1010) // eliminating PnP errors.
| where ProviderName in ("OSHostPlugin", "UpdateNotification", "NMAgent", "Microsoft-Windows-UserModePowerService", "EventLog") or
    ProviderName contains "Microsoft-Windows-Kernel" or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: AfterInstall") or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: BeforeInstall") or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "FPGA driver install") or
    (ProviderName contains "vfpext" and EventId == 7036)
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend level = case (Level == 1, "critical",
    Level == 2, "error",
    Level == 3, "warning",
    "info")
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, Content = strcat(ProviderName, " - ", EventId)
| extend Health = case (Level <= 2, "Unhealthy", Level == 3, "Degraded", "Healthy")
```

#### Check state of nodes, detailed version

```kusto
//Check state of nodes, detailed version
//Azurecm - azurecm
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp > datetime(2023-03-12 02:00:00.000) and PreciseTimeStamp < datetime(2023-03-12 06:00:00.000)
| where NodeId =~ "12345678-1234-4000-8000-000000000132"
| project PreciseTimeStamp, Message
```

#### IridiasTargets

```kusto
cluster('icmcluster.kusto.windows.net').database("ACM.Publisher").
IridiasTargets
| where TrackingId contains "123-45-015"
| where Subscriptions contains "12345678-1234-4000-8000-000000000022"
```
