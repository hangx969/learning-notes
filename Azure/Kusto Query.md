# VM ID and Nodes

~~~sh
//---------------------- Query all kind of IDs -------------------------------------------------------
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2023-12-01 00:00:00) and PreciseTimeStamp <= datetime(2023-12-12 23:00:00)
//| where nodeId == "a82e1173-fdb0-4f72-a553-f2ccc2f314a2"
| where subscriptionId == "e7061e30-4c81-41d1-81ac-e8c9f4a80513"
| where roleInstanceName contains "IVP-CICD-VM-CCN2-DEV"
//| where availabilitySetName contains "CNC_PREPROD_WEB_AS"
//| where containerId contains "48fc0a4b-2197-499d-bb1b-da1a397f09a0"
//| where virtualMachineUniqueId contains "ad881b"
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId, subscriptionId
| order by creationTime desc

//看区域日志最近的产生时间
//Azurecm - azurecm
LogContainerSnapshot | summarize max(ingestion_time()) by Region

//---------------- container health - up/down-------------------------------------
//Azurecm - azurecm
LogContainerHealthSnapshot
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where containerId contains "e0ffd283-4566-454f-8e27-440a5924019e"
| project PreciseTimeStamp, actualOperationalState, containerLifecycleState, containerState, containerOsState,nodeId, containerId, faultInfo

//----------------------- Node Status --------------------------------------
//Check state of nodes, simplified version
//Azurecm - azurecm
LogNodeSnapshot
| where nodeId == "840e1f20-813c-3936-3d0c-523502ed26d3"
| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 03:20:00)
| project PreciseTimeStamp, Tenant,nodeId,nodeState,nodeAvailabilityState, faultInfo, Region, containerCount,diskConfiguration,healthSignals

//Check state of nodes, detailed version
cluster('Azurecm').database('AzureCM').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(2023-10-26 07:00:00) and PreciseTimeStamp <= datetime(2023-10-26 08:00:00)
| where NodeId == "9235964f-15da-4295-b2b6-6a00954d0356"
| project PreciseTimeStamp, Message

//Check state of tenant, detailed version
cluster('Azurecm').database('AzureCM').TMMgmtTenantEventsEtwTable
| where TenantName == "c4eb3be8-847b-467c-8e5e-351895d74a47"
| where PreciseTimeStamp >= datetime(2023-06-07 00:20:00) and PreciseTimeStamp <= datetime(2023-06-07 19:30:00)
| where Message !contains "[AuditEvent]"
| project PreciseTimeStamp, Message

//Check node lifecycle status
//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
cluster("Azuredcmmc").database("AzureDcmDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-07-09 07:00:00) and PreciseTimeStamp <= datetime(2023-07-09 09:30:00)
| where ResourceId == "379185b1-c6d6-4a66-8e2b-642d4e21fa70"
| project-reorder PreciseTimeStamp, ResourceId, LifecycleState, FaultCode, FaultDescription, RepairFaultDetails, RepairResolutionDetails
| sort by PreciseTimeStamp desc
| take 100

//check containers list on the node
let starttime = datetime("2023-06-25T03:48:29.415Z");
let endtime = datetime("2023-06-27T03:48:32.933Z");
let nodeid = "1f6fd17b-1f84-76f5-c062-70c753bbf9e1";
//let nodeid = "a7bd5f16-0995-1568-ff6b-50977d53488a";
cluster("azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").LogContainerSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeId == nodeid
| distinct creationTime, roleInstanceName, subscriptionId, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId, tenantOwners, containerType, Region, AvailabilityZone
| order by creationTime

let queryFrom = datetime("2023-06-12T19:40:00.000Z");
let queryTo = datetime("2023-06-12T20:30:00.000Z");
let queryNodeId = "00cf74d4-ef50-45dd-9702-7fac2a6fbd3a";
let queryContainerId = "512d2229-6782-4a4f-81e8-e4ede24a759f";
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

cluster("azuredcmmc.kusto.chinacloudapi.cn").database("AzureDCMDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-06-25 19:30:00) and PreciseTimeStamp <= datetime(2023-06-26 23:30:00)
| where ResourceId == "a7bd5f16-0995-1568-ff6b-50977d53488a" //Node id
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

//------------------ ARM operation----------------------------------------------
// ARM operation
//armmcadx - armmc
EventServiceEntries 
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
//| where correlationId contains "e7cc22cf-5e80-4421-ac94-27bb0170d479"
| where resourceUri contains "aks-d8sv401-33162318-vmss"
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

//armmcadx - armmc
HttpIncomingRequests
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where correlationId ==  "5256b6e1-7831-45b2-bd9f-df20a393f0d3"
//| where targetUri contains "XC-S-ZL18159"
// | where status notcontains "Accepted"
| where httpMethod != "GET"

//ASC - operation 拿到correlation id 来这里查具体出错细节
//https://armmcadx.chinaeast2.kusto.chinacloudapi.cn
let starttime = datetime(2023-12-07 01:00:00);
let endtime = datetime(2023-12-07 02:30:59);
JobTraces
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
| where correlationId ==  "2c954ffb-dbba-4889-abfd-80574874f316"
| project TIMESTAMP, subscriptionId, correlationId, ActivityId, message, exception

//-------------------------VMA Related--------------------------------------------------------
//查node的windows事件
cluster('vmainsight.kusto.windows.net').database('vmadb').WindowsEventTable
| where PreciseTimeStamp >= datetime(2023-08-07 07:00:00) and PreciseTimeStamp <= datetime(2023-08-07 08:50:00)
| where NodeId == "50af6eee-cf30-b85b-0d0e-285d0bfa54d9"
| where Cluster == "ZQZ22PrdApp10"
| where Description contains "PCI"
| project TIMESTAMP, ProviderName, EventId, Description, Cluster, NodeId
| sort by TIMESTAMP asc
//| distinct NodeId

cluster('vmainsight.kusto.windows.net').database('vmadb').WindowsEventTable 
| where PreciseTimeStamp >= datetime(2023-11-01 00:00:00) and PreciseTimeStamp <= datetime(2023-11-01 05:30:00)
//| where Description contains "fa00fc2e-b57a-3402-b118-c53d8d943f2a" and (Description contains "Ethernet" or Description contains "started successfully")
| where NodeId == "76f06633-6b84-49fa-914c-baecbdc5a96c"
| project PreciseTimeStamp, EventId, Channel , Description
| sort by PreciseTimeStamp asc

let queryFrom = datetime('2023-07-22T21:30:28.000Z');
let queryTo = datetime('2023-07-23T01:30:28.000Z');
let queryNodeId = 'd224b764-1fe1-47bd-bf82-e84cb9b33bcf';
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

//Check RCA level2
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp >= datetime(2023-08-18 06:00:00) and PreciseTimeStamp <= datetime(2023-08-18 07:00:00)
| where NodeId == "0a6f9657-6a2d-4177-8047-dbb1fdd07798" and RoleInstanceName has "CNCORPRSOPAPP1A" //and RCAEngineCategory !contains "Customer"
| distinct bin(StartTime,2m), bin(EndTime,2m), Cluster, RoleInstanceName,  RCALevel1, RCALevel2, Watson_CrashDumpLink,Hardware_Generation

cluster("Vmainsight").database("vmadb").VMA 
| where PreciseTimeStamp >= datetime(2023-06-28 16:00:00) and PreciseTimeStamp <= datetime(2023-06-28 18:30:00)
//| where ResourceId == "/subscriptions/0050641c-cefb-4119-b748-c6cc4556a027/resourceGroups/EC2PRDDLRG01/providers/Microsoft.Compute/virtualMachines/CNCORPAZPDLDW8"
| where RoleInstanceName has "nacos102-service.loreal-nacos.svc.cluster.local"
| project StartTime, EndTime, RoleInstanceName, Cluster, RCALevel1, RCALevel2

AirNMAgentUpdateEvents
| where EventTime >= datetime(2022-12-18 00:00:00) and EventTime <= datetime(2022-12-19 03:00:00)
| where NodeId == "fa00fc2e-b57a-3402-b118-c53d8d943f2a" //and ContainerId == "55ee0b4a-ceb4-41cc-b336-bd170551fe78"// and MACAddress == "0017FA03196A"

//https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm
RnmOperationEvents 
| where PreciseTimeStamp >= datetime(2023-07-07 02:00:00) and PreciseTimeStamp <= datetime(2023-07-07 02:15:00) and tenantName == "7e32de2a-8b1d-469e-97f6-a5c617ec60e4" 
| project PreciseTimeStamp, Cluster, EventMessage, status

let queryFrom = datetime("2023-07-07T02:00:00.000Z");
let queryTo = datetime("2023-07-07T02:30:00.000Z");
let queryVMId = "8c0ab1a3-b98f-48db-b5af-a949bb29f618";
let queryContainerId = "119676cc-78e5-4fff-981b-6182c1a5cf1f";
RhcAnnotationReportsEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where (isnotempty(queryVMId) and VmId == queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VmId, ContainerId, Annotation
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = Annotation, VmId, ContainerId, Annotation

//check host OS update
//https://vmainsight.kusto.windows.net/Air
database("Air").AirManagedEvents
| where EventTime >= datetime(2023-07-07 01:00:00) and EventTime <= datetime(2023-07-07 03:00:00)
| where NodeId contains "379185b1-c6d6-4a66-8e2b-642d4e21fa70" and RoleInstanceName contains "T-BJCA3-SQL-02"
| distinct EventTime,Cluster, NodeId, RoleInstanceName, EventType, EventSource

//https://vmainsight.kusto.windows.net/Air
aznwsdn_aznwmds().InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP >= datetime(2022-12-19 00:00:00) and TIMESTAMP <= datetime(2022-12-19 03:00:00)
| where NodeId == "fa00fc2e-b57a-3402-b118-c53d8d943f2a" and ContainerId == "55ee0b4a-ceb4-41cc-b336-bd170551fe78"// and MACAddress == "0017FA03196A"
| project FirstTimeStamp,Detail,StateVersion,FirstTimeProgramming

//------------------------RDOS related-----------------------------------------------------------------------
cluster('rdos.kusto.windows.net').database('rdos').HyperVAnalyticEvents
| where PreciseTimeStamp >= datetime(2023-11-01 03:00:00) and PreciseTimeStamp <= datetime(2023-11-01 04:10:00)
| where NodeId contains '76f06633-6b84-49fa-914c-baecbdc5a96c'
| project PreciseTimeStamp, Cluster, Level, ProviderName, EventId, OpcodeName, TaskName, EventMessage, Message

//vmagent log
//rdosmc
GuestAgentGenericLogs
| where PreciseTimeStamp >= datetime(2023-07-09 08:00:00) and PreciseTimeStamp <= datetime(2023-07-09 08:30:00)
| where ContainerId == '119676cc-78e5-4fff-981b-6182c1a5cf1f'
//| where CapabilityUsed contains "Error"
| project PreciseTimeStamp, Cluster, Level, RoleInstanceName, GAVersion, EventName, CapabilityUsed, Context1, Context2, Context3, OSVersion, ExecutionMode, RAM

//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
//| where PreciseTimeStamp > ago(24h)
| where PreciseTimeStamp >= datetime(2023-11-01 03:00:00) and PreciseTimeStamp <= datetime(2023-11-01 04:50:00)
| where NodeId in~ ('76f06633-6b84-49fa-914c-baecbdc5a96c')
//| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170','155','15')
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId
 
//check Guest OS extension heartbeat
let queryContainerId = "e12637d6-aa46-4866-8c22-3a1d7711fe23";
cluster("rdosmc.kusto.chinacloudapi.cn").database("rdos").GuestAgentExtensionEvents
| where PreciseTimeStamp >= datetime(2023-06-21 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where ContainerId == queryContainerId
| project PreciseTimeStamp, Level, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message
| order by PreciseTimeStamp asc
 
// https://rdosmc.kusto.chinacloudapi.cn/rdos
VmHealthRawStateEtwTable
| where NodeId == "e12637d6-aa46-4866-8c22-3a1d7711fe23"
| where PreciseTimeStamp >= datetime(2023-06-21 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where ContainerId contains "038a11ee-9bcc-37e7-fdf5-cdd5d501d8a1"
| project PreciseTimeStamp,  VmHyperVIcHeartbeat, IsVscStateOperational, VmPowerState, Context

WindowsEventTable
| where NodeId in ("e12637d6-aa46-4866-8c22-3a1d7711fe23")   
| where PreciseTimeStamp >= datetime(2023-06-20 07:00:00) and PreciseTimeStamp <= datetime(2023-06-21 08:50:00)
| where EventId !in ("3095")
| where Description !contains "GetBoardModel" and Description !contains "IO latency summary" and Description !contains "summary for Storport" and Description !contains "Summary of disk space usage"
| project TimeCreated, Cluster,EventId, ProviderName, Description,Level
| order by TimeCreated asc

//===============identify deeper RCA==================================
//check node lifecycle state
cluster("Azuredcmmc").database("AzureDcmDb").RdmResourceSnapshot
| where PreciseTimeStamp >= datetime(2023-07-06 06:00:00) and PreciseTimeStamp <= datetime(2023-07-06 08:30:00)
| where ResourceId == "38d14f12-99b4-4f07-b182-11802aadcfff" //node id
| project PreciseTimeStamp, ResourceId, LifecycleState, FaultCode, FaultDescription, RepairFaultDetails, RepairResolutionDetails
| sort by PreciseTimeStamp desc
| take 100

let starttime = datetime("2023-07-07T02:00:00.000Z");
let endtime = datetime("2023-07-07T02:15:00.000Z");
let nodeid = "379185b1-c6d6-4a66-8e2b-642d4e21fa70";
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

//#connect "https://azuredcm.kusto.windows.net/AzureDCMDb"
//To collect details about Fault codes
cluster("Azuredcm"). database("AzureDCMDb").FaultCodeTeamMapping
| where FaultCode == "10038"
| project FaultCode, FaultReason

cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where ResourceId == "38d14f12-99b4-4f07-b182-11802aadcfff" //node id
| where PreciseTimeStamp >= datetime(2023-07-06 06:00:00) and PreciseTimeStamp <= datetime(2023-07-06 08:30:00)
| project PreciseTimeStamp, LifecycleState, NeedFlags, FaultCode, FaultDescription, Tenant, ResourceId

let filterValue = "";
let queryNodeId = "0a6f9657-6a2d-4177-8047-dbb1fdd07798";
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

//----------//查当前cluster的容量上限以及支持虚拟机类型的--------------------------------------------------
LogAllocatableVmCountMetric
| where Tenant == "ZQZ20PrdApp03"//"BJBPrdApp03"//"SH3PrdApp02"//"BJBPrdApp13"
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

//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
// 查看特定机型的capacity
LogAllocatableVmCountMetric 
//| where Region == "chinan3" and Tenant contains "PrdApp" and 
| where TIMESTAMP > ago(1h) 
//| where AvailabilityZone == "chinan3-AZ01"
| where Tenant contains "SHA20PrdApp07"
| where vmType contains "D2s" //or vmType contains "M64ls"
| where limitType in ("NewDeployment","Upgrade","ServiceHealing")
| summarize max(PreciseTimeStamp) by Tenant, vmType, vmCount, limitType

LogAllocatableVmCountMetric
| where Tenant contains "SHA20PrdApp07"//"BJBPrdApp03"//"SH3PrdApp02"//"BJBPrdApp13"
//| where Region == "chinan3"
//| distinct Tenant

//https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm
// to check capacity of specific cluster
cluster('azurecm.chinanorth2.kusto.chinacloudapi.cn').database('azurecm').LogClusterCapacity
| where Tenant == "SHA20PrdApp07" //or Tenant == "ZQZ20PrdApp03"
| where PreciseTimeStamp >= ago(1h)//(15min)
| project PreciseTimeStamp, Tenant, allocatableNodes, totalHen, totalCores, usedCores, newDeploymentEmptyNodesLimitForAllocation, upgradeEmptyNodesLimitForAllocation
| sort by PreciseTimeStamp desc

AllocableVmCount
| where TIMESTAMP > ago(1h)
| where deploymentType in ("NewDeployment" "Upgrade")
//| where AvailabilityZone contains "chinan3-Az01"
//| where Region contains "chinan3"
| where Tenant contains "SHA20PrdApp07"
//| where vmType contains "M32"
|summarize by Tenant, vmType, vmCount, Region, deploymentType
// I distinct Tenant
// I distinct vmType
// I sort by Tenant asc

//cluster("https://azurecm.chinanorth2.kusto.chinacloudapi.cn/").database("azurecm");
let starttime = datetime('2023-08-09T00:00:00.000Z');
let endtime = datetime('2023-08-09T23:00:00.000Z');
let cluster = 'SHA20PrdApp07';
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


ResourceDeletions
| where subscriptionId contains "68cbae8a-0ad0-4f1d-ad06-b5b759a3866e"
| where resourceGroupName contains "3"
| where TIMESTAMP > ago(3d)
| project providerNamespace, resourceType, resourceName
//use the summarize to remove duplicate results
//| summarize by providerNamespace, resourceGroupLocation, resourceLocation, resourceType, resourceName

//根据node的TOR来查node id
//find all nodes under the ToR
//https://azdhmc.chinaeast2.kusto.chinacloudapi.cn/azdhmds
cluster('azdhmc.chinaeast2.kusto.chinacloudapi.cn').database('azdhmds').DeviceInterfaceLinks
| where LinkType =~ 'DeviceInterfaceLink' and EndDevice =~ 'BJS20-0101-0503-20T0'
| summarize by DeviceName = StartDevice
| join kind = inner
    (
        Servers
        | where DeviceName =~ DeviceName
    ) on DeviceName
    | project NodeId

//list哪些VM在node list里面
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2023-07-01T00:00:00) and PreciseTimeStamp <= datetime(2023-07-07T23:00)
| where nodeId in (
'61154054-abc0-4d17-8694-eae22b2a60d0',
'b16bdc66-e1b7-4247-a1e5-658359775bb8',
'f04173b3-d782-4ec8-87a8-3ecea04b5d00',
'00f3ebb2-e8e5-4382-9296-e60c0f237fba',
'a6e1d10e-ef3b-46ce-8321-59f90055cef3',
'794b1c9c-0225-4bca-b4d1-cf7221f4f612',
'872d397b-79a5-4cfe-b64b-84d3a29fd5d6',
'ef426fdd-0f28-4056-8f48-21b23ab99267',
'39eba69f-23ac-47eb-9243-55a7a73bb238',
'239e9a51-6787-4826-b9a8-de4e5e747008',
'25dd1c1b-1c01-46ca-a767-6d4d5e19b7a0',
'ea84c03b-4e15-43f4-be0a-46a4856a6248',
'd295db81-c627-4661-a14b-e3d5f9819136',
'ed66b800-afdc-4e3d-994d-bd5224f7f10c',
'0269c307-7d15-4a1b-8d2c-293a8ee583ac',
'272838dc-f8da-4890-9f63-0644eda31a26',
'8ed6cdaf-9aa2-40a3-8f62-01cc2e2dee02',
'a15e7a21-60d3-476f-ab7c-e0ee55e23c09',
'c56d926b-ee89-4476-bb6c-ef3dbcfd12c0',
'acd3e6d5-4e2e-47f0-94ad-efafc0c37151',
'b155818e-bc67-497b-a61c-e9fbf35e04b4',
'c0949e62-ac51-4042-b359-2191a809dc9e',
'd2f57aab-7ccd-4be6-bffe-3da486c6aa72',
'ebd0f106-32ed-4085-9bbb-82d4e092fc4a'
)
| where subscriptionId in (
'0c51d0a1-bd08-43af-b21f-af793d7438ce'
)
//| project PreciseTimeStamp,roleInstanceName,nodeId,subscriptionId
| distinct roleInstanceName,subscriptionId,nodeId

LogNodeSnapshot
| where nodeId in (
'61154054-abc0-4d17-8694-eae22b2a60d0',
'b16bdc66-e1b7-4247-a1e5-658359775bb8',
'f04173b3-d782-4ec8-87a8-3ecea04b5d00',
'00f3ebb2-e8e5-4382-9296-e60c0f237fba',
'a6e1d10e-ef3b-46ce-8321-59f90055cef3',
'794b1c9c-0225-4bca-b4d1-cf7221f4f612',
'872d397b-79a5-4cfe-b64b-84d3a29fd5d6',
'ef426fdd-0f28-4056-8f48-21b23ab99267',
'39eba69f-23ac-47eb-9243-55a7a73bb238',
'239e9a51-6787-4826-b9a8-de4e5e747008',
'25dd1c1b-1c01-46ca-a767-6d4d5e19b7a0',
'ea84c03b-4e15-43f4-be0a-46a4856a6248',
'd295db81-c627-4661-a14b-e3d5f9819136',
'ed66b800-afdc-4e3d-994d-bd5224f7f10c',
'0269c307-7d15-4a1b-8d2c-293a8ee583ac',
'272838dc-f8da-4890-9f63-0644eda31a26',
'8ed6cdaf-9aa2-40a3-8f62-01cc2e2dee02',
'a15e7a21-60d3-476f-ab7c-e0ee55e23c09',
'c56d926b-ee89-4476-bb6c-ef3dbcfd12c0',
'acd3e6d5-4e2e-47f0-94ad-efafc0c37151',
'b155818e-bc67-497b-a61c-e9fbf35e04b4',
'c0949e62-ac51-4042-b359-2191a809dc9e',
'd2f57aab-7ccd-4be6-bffe-3da486c6aa72',
'ebd0f106-32ed-4085-9bbb-82d4e092fc4a'
)
| where PreciseTimeStamp >= datetime(2023-07-06 16:00:00) and PreciseTimeStamp <= datetime(2023-07-07 18:30:00)
//| project PreciseTimeStamp, Tenant, nodeId, nodeState, nodeAvailabilityState, faultInfo, Region, containerCount
| distinct nodeId,faultInfo

LiveMigrationSessionCompleteLog
| where vmUniqueId == "fd02e94b-13a5-4e4e-938a-16a457286d12"
| project PreciseTimeStamp, sourceNodeId, sourceContainerId, destinationContainerId, destinationNodeId, tenantName, triggerType, status, Role, RoleInstance, resourceId
~~~

# AKS

~~~sh
//rp service分前后端，前端是frontend* 后端是async*
//frontendqos是 用户发来的request； asyncqos是前段发给后端的request，是内部实现用的
//blackbox不是rp的组件，是monitoring的组件，会不停扫描用户的master pod状态， blackbox跟用户的请求没有直接关系
//ServiceRequestId in ARM EventServices == OperationID in AKS RP QOS tables
//OperationID in AKS RP QOS tables  == OperationID in ContextActivity

	//AKS operations
	//cluster创建失败：get operation id by filter failed!!!，cluster级别的一些操作升级也可以，看AKS RP收到的request
	//获取 operation ID
	union 
	cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').FrontEndQoSEvents,
	cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncQoSEvents
	| where PreciseTimeStamp >= datetime(2023-12-04 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-12-06 23:00:00.0000000)
	//| where PreciseTimeStamp  > ago(4d)
	| where subscriptionID == "3d0a450f-1ff1-492c-a1ff-efdc89cf8ee6" and resourceName contains "aks-tap-cn3-prd"
	| where operationName !contains "get" and operationName !contains "list"
	| extend Count = parse_json(tostring(parse_json(propertiesBag).LinuxAgentsCount)) 
	| project PreciseTimeStamp,correlationID, operationID, Count, operationName, suboperationName, result,resultSubCode,resultCode,errorDetails
    //|project PreciseTimeStamp,correlationID, operationID, operationName, suboperationName, result,resultSubCode,resultCode,errorDetails
	
    union
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').FrontEndQoSEvents,
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncQoSEvents
	| where PreciseTimeStamp >= datetime(2023-10-12 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-10-12 23:00:00.0000000)
	| where subscriptionID == "bba42d85-0cbe-4099-8b4c-186679403e72" and resourceName contains "CE2-CNFSC-AKS-NP-SMTR"
    //| where resourceName contains "JoyLearning_Prod"
    //| where operationID == "d626cd2a-479b-4bc5-b071-f1d9fba5d0b9"
    //and resourceGroupName == "cn-devcne2-rtm2-k8s-rg"
    //| where operationName == "PutManagedClusterHandler.PUT"
    | where operationName notcontains "GET"
    | where operationName notcontains "ListManagedCluster"
	
	//RP
	//error detail，用前面的operation id来查具体的出错信息
    cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').AsyncContextActivity
	//cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').HcpAsyncContextActivity
	| where PreciseTimeStamp >= datetime(2023-12-01 00:00:00.0000000) and PreciseTimeStamp <= datetime(2023-12-06 23:00:00.0000000)
	| where operationID == "41b1d21e-08af-4a53-8177-cc185a02a107"
	| where level !="info"
    | project PreciseTimeStamp, level, msg, fileName, lineNumber,operationID
	
//=============================================================================================	
	//拿到subid，vmss name，来查cm和crp
    let starttime = datetime(2022-08-21 00:10);
	let endtime = datetime(2022-08-21 23:30);
	cluster('azurecm.chinanorth2.kusto.chinacloudapi.cn').database('azurecm').LogContainerSnapshot 
	| where TIMESTAMP >= starttime and TIMESTAMP <=endtime
	| where subscriptionId == "f99c3d28-250e-4c4a-b0b6-92edb0849788c" and roleInstanceName contains ""
	//"aks-nodepool1-32471634-7"
	//|where availabilitySetName == "BEIHQERPAPP2"
	//| where roleInstanceName contains "BEIHQERPAPP2"
	//| where containerId contains "2a3a119c-13f1-4ddd-9dac-77cd8eb7d2f8"
	| project TIMESTAMP, Tenant, tenantName, containerId, nodeId, roleInstanceName, availabilitySetName, updateDomain,subscriptionId,RoleInstance
    | sort by TIMESTAMP asc nulls last

//================================================================================================

    //rdosmc - rdos
    //拿到container id，去查vm agent和extension信息
    GuestAgentExtensionEvents
	| where PreciseTimeStamp > datetime(2022-08-10 00:10) and PreciseTimeStamp < datetime(2022-08-10 23:30)
	| where ContainerId == "8d523633-987b-45bd-89c5-4caa1c865dda"
	//"477c9e8e-84d3-4f80-9848-db533c46eb66"
	| where Operation !in ('HeartBeat', 'HttpErrors')
	| where isnotempty(Message)
    | project PreciseTimeStamp, ContainerId, Level, GAVersion, Version, Operation,Message,Duration
    
    // AKS RP outgoing，akscn - aksprod
    // RP的operation会对应好多个crp的operation和correlation id，要在crp中找到具体哪一个
    // 拿correlation id
    OutgoingRequestTrace
	| where TIMESTAMP > datetime(2022-08-10 00:00) and TIMESTAMP < datetime(2022-08-10 23:00)
	| where operationID == "0f150b5d-56d4-4ef4-845d-0a30cc31a52b"
	| where targetURI contains "aksTest"
    | project TIMESTAMP,correlationID, clientRequestID, operationID,msg, operationName, statusCode, level, Environment,targetURI

    //#connect "https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc"
    // 拿到correlation id，去crp查，获取operation id
    ApiQosEvent
	| where TIMESTAMP > datetime(2021-06-21 23:00) and TIMESTAMP < datetime(2021-06-24 01:00)
	| where correlationId == "2340d7cf-f280-4248-b144-cecf49fbe5ab"
	| where operationName !contains "GET"
    | project  resourceGroupName, resourceName, goalSeekingActivityId, operationId

    //拿这个operation id = activity id到CRP里再去查#
	cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity
	| where TIMESTAMP > datetime(2023-07-20 16:00) and TIMESTAMP < datetime(2021-06-24 01:00)
    | where activityId == "396932d1-2ed6-454d-b75c-8deec1c9e5b6"

//===========================================================================================
//--------------------------------------------------------------------------
	//get operation ID
	// Akscn - AKSprod
	FrontEndQoSEvents
    | where PreciseTimeStamp >= datetime(2022-07-15 06:00:00.0000000) and PreciseTimeStamp <= datetime(2022-07-15 10:00:00.0000000)
    | where subscriptionID == "f99c3d28-250e-4c4a-b0b6-92edb0849788" and resourceGroupName == "aksTest" and resourceName == "aksTest"
    //| where operationName == "PutManagedClusterHandler.PUT"
    | project TIMESTAMP, operationID, operationName
    | take 20
	
    //check cluster error
    union FrontEndQoSEvents, AsyncQoSEvents
    | where PreciseTimeStamp >= datetime(2023-07-20 16:00:00) and PreciseTimeStamp <= datetime(2023-07-20 19:59:59) 
    | where subscriptionID == "d07c204e-68de-4e1f-83f6-7cfa5f6afc0d"
    | where resourceName contains "btccnprd-kub-s00"
    //| where operationName !contains"get" | where operationName !contains"list"

    //ARM
    //cluster failed
    //cluster("Armmcadx.chinaeast2.kusto.chinacloudapi.cn").database("armmc").EventServiceEntries
    EventServiceEntries
    | where PreciseTimeStamp >= datetime(2023-11-15 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:59:59) 
    | where subscriptionId == "3d0a450f-1ff1-492c-a1ff-efdc89cf8ee6"
    | where resourceUri contains "aks-tap-cn3-prd"
    //| where status == "Failed"
    //| where TIMESTAMP > ago(2d)
    //| where operationName contains "cluster"
    | project PreciseTimeStamp, status, operationName , correlationId ,properties

    //ARM https://akscn.kusto.chinacloudapi.cn/AKSprod
    OutgoingRequestTrace
    | where TIMESTAMP > datetime(2022-10-26 00:00) and TIMESTAMP < datetime(2022-10-31 23:00)
    | where operationID == "b0288f7e-4dc0-4a72-a1de-e95b76e43612"
    | where targetURI contains "aks-nodepool1-32471634-5"
    | project TIMESTAMP,correlationID, clientRequestID, operationID, msg, operationName, statusCode, level, Environment, targetURI

    //armmcadx - armmc
    HttpIncomingRequests
    | where TIMESTAMP > datetime(2022-09-04 11:00) and TIMESTAMP < datetime(2022-09-04 15:00)
    | where subscriptionId contains "b84f0f78-ecaf-43b1-bf51-a0d1b098c413"
    | where operationName !contains "METRICBATCH"
    | where httpStatusCode == "202"
    | where httpMethod != "GET"
    | where userAgent contains "Remediator"
    | where operationName contains "RESTART"

    //query by operation ID
    union FrontEndContextActivity,AsyncContextActivity,HcpAsyncContextActivity
    //union HcpAsyncContextActivity,HcpSyncContextActivity
    | where PreciseTimeStamp > ago (1d)
    | where operationID == ""
    //| where level!="info"
    | project PreciseTimeStamp, level, msg, fileName, lineNumber

//akscn - AKSprod
RemediatorEvent 
| where PreciseTimeStamp >= datetime(2023-06-07 00:20:00) and PreciseTimeStamp <= datetime(2023-06-07 19:30:00)
| where ccpNamespace contains "6165019ea740de000172b2d5" 
//| where reason contains "CustomerLinuxNodesNotReady"
//| where msg contains "failed"
| project PreciseTimeStamp, reason, msg, correlationID, hostMachine

//Here is the autoupgrader
AutoUpgraderEvents
| where PreciseTimeStamp >= datetime(2023-12-01 00:20:00) and PreciseTimeStamp <= datetime(2023-12-08 19:30:00)
| where subscriptionID contains 'a3846e58-767e-462b-824b-a6a769161ae9'
//| where resourceGroupName has "echopprodgreen-kaas"
| where resourceName contains "echopprodgreen-cluster"//clustername
//| where msg contains "Upgrade node image"
//| where msg contains "Autoupgrade not enabled"
| project PreciseTimeStamp,level,msg

//Autoupgrade related
//database->looper->autoupgrader
//Here is the looper to get enquene
RegionalLooperEvents
| where PreciseTimeStamp > ago(1d)
//| where fileName contains 'upgrade'
| where msg contains "Enqueuing message" and msg has "/subscriptions/a3846e58-767e-462b-824b-a6a769161ae9/resourceGroups/echopprodgreen-kaas/providers/Microsoft.ContainerService/managedClusters/echopprodgreen-cluster" //resourceURI in format /managedClusters/myAKS
| project PreciseTimeStamp,msg,error,Environment, fileName, api

//============cluster 状态 BBM==============================================
//=================akscn - AKSprod=========================================================
    //BBM只是一个general的信息，不一定展示出全部的错误。是靠外部监控组件来的，不是直接从后台组件抓出来的。
    let starttime = datetime(2023-12-07 01:00:00);
    let endtime = datetime(2023-12-07 02:00:00);
    BlackboxMonitoringActivity 
    | where TIMESTAMP >= starttime and TIMESTAMP <= endtime 
    | where subscriptionID == "a3846e58-767e-462b-824b-a6a769161ae9"
    | where clusterName contains "echopprodgreen-cluster"
    //| where agentNodeName contains "aks"
    | where state != "Healthy"
    | project clusterName, PreciseTimeStamp, fqdn, ccpNamespace, agentNodeName, state, reason, podsState, resourceState, addonPodsState, agentNodeCount, provisioningState, msg, resourceGroupName, resourceName, underlayName
    
    let starttime = datetime(2023-05-04 16:00:00.3320075);
    let endtime = datetime(2023-05-06 19:30:00.3320075);
    BlackboxMonitoringActivity
    | where TIMESTAMP >= starttime and TIMESTAMP <= endtime 
    | where fqdn == "aze2-aks01-aze2-rgec-p-725316-8102a0d8.hcp.chinaeast2.cx.prod.service.azk8s.cn"
    | where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
    | project PreciseTimeStamp, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP 
    
    BlackboxMonitoringActivity
    | where TIMESTAMP > datetime(2019-08-22) and fqdn contains "aks-dev-cluster-0-dns-de2b4978.hcp.chinanorth2.cx.prod.service.azk8s.cn"
    | project PreciseTimeStamp, state, reason
    | summarize count() by bin(PreciseTimeStamp, 30m), state
    | render timechart

    // 查看aks 自动修复是否进行了
	BlackboxMonitoringActivity
	| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:59:59)
	| where fqdn == "echopprodgreen-k8s-lmx1xbti.hcp.chinanorth2.cx.prod.service.azk8s.cn"
	| where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
	| project PreciseTimeStamp, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP
	
cluster('akscn.kusto.chinacloudapi.cn').database('AKSprod').BlackboxMonitoringActivity
| where PreciseTimeStamp >= datetime(2023-11-27 11:00:00) and PreciseTimeStamp <= datetime(2023-11-27 12:00:00)
//| where fqdn == "private-cluster-dns-4839aff4.57ac0247-e4c9-457d-8555-3e29cae982d9.privatelink.chinanorth2.cx.prod.service.azk8s.cn"
| where subscriptionID == "08ab17d7-5c57-4e90-aa8d-44b11ca5dc5c"
//| where fqdn == "sh2dmprdak-sh2prdrg-08ab17-b9b6587e.hcp.chinaeast2.cx.prod.service.azk8s.cn"
//| where clusterName contains "PepsiBevBusiDeptSmartFridge2_AKS"
| where clusterName == "sh2dmprdaks"
| where state != "Healthy"
//| where (["state"] != "Healthy" or podsState != "Healthy" or resourceState != "Healthy" or addonPodsState != "Healthy")
| project PreciseTimeStamp, clusterName, isCCPPoolingEnabled, isPrivateCluster, ['reason'], Underlay, msg, ccpNamespace, tunnelVersion, ccpIP, apiserverCPU, apiserverLatency, coreDNSConfig, etcdCPU, etcdMemory,fqdn
	
//查看集群kubesystem信息
KubeSystemEvents
| where PreciseTimeStamp >= datetime(2023-11-27 11:00:00) and PreciseTimeStamp <= datetime(2023-11-27 12:00:00)
| where (((* has @'08ab17d7-5c57-4e90-aa8d-44b11ca5dc5c' and * has @'sh2dmprdaks'))) //and * has @'error') )
| limit 100
//==============================================================================================================

    //AKS RP outgoing
    OutgoingRequestTrace
	| where TIMESTAMP > datetime(2023-12-07 01:00) and TIMESTAMP < datetime(2023-12-07 02:00)
	//| where operationID == "48adb623-a524-4977-a832-fd218d9389c0"
	| where targetURI contains "aks-d8sv401-33162318-vmss"
    | project TIMESTAMP,correlationID, clientRequestID, operationID,msg, operationName, statusCode, level, Environment,targetURI
    
    //rdosmc - rdos
    GuestAgentExtensionEvents
	| where PreciseTimeStamp > datetime(2021-06-22 00:10) and PreciseTimeStamp < datetime(2021-06-24 14:30)
	| where ContainerId == 
	"b379bad6-bd55-4755-bb92-106f019b2159"
	//"477c9e8e-84d3-4f80-9848-db533c46eb66"
	| where Operation !in ('HeartBeat', 'HttpErrors')
	| where isnotempty(Message)
    | project PreciseTimeStamp, ContainerId, Level, GAVersion, Version, Operation,Message,Duration
    
	// 查看aks 自动修复是否进行了 
	RemediatorEvent 
	| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:00:59) 
	| where ccpNamespace == "64c7b46533257c0001a32f35" 
	//| where reason contains "CustomerLinuxNodesNotReady"
    | project PreciseTimeStamp, reason, msg, correlationID
       
// check node pod deployment scale endpoints
// Akscn - AKSprod    
//pod, node, service, scaler, API等control panel的改变
ControlPlaneEvents //NonShoebox    <-- depend on whether customer enable insights
| where ccpNamespace == '6165019ea740de000172b2d5'  //在BBM的表里能查出来
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
// or properties contains 'extractor-654dd85bb6-d8fhj'
// or properties contains 'extractor-654dd85bb6-kfvns'
// or properties contains 'change-7bcfbdd899-mdqgk'
// or properties contains 'change-7bcfbdd899-8cdn5'
// or properties contains 'change-7bcfbdd899-8cdn5'
// or properties contains 'change-7bcfbdd899-c6qcm'
// or properties contains 'inf-reportcron-1583265600-sg245'
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
//| where properties contains 'chargingservice-deploy-7d59487c4d-mh7ph'
// | where properties contains 'webservicesdrugdata-7c58df5c58-j7hb5'
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

//control plane的记录
//可以查POD，node，service、API等control plane上的life cycle改变
let queryCcpNamespace = "6502b76478b21b0001002640";
let query = "konnectivity-agent-f79ffc68c";
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

//======check pod creation================
let queryFrom = datetime("2023-11-05T00:00:00.000Z");
let queryTo = datetime("2023-12-10T12:30:00.000Z");
let queryCcpNamespace = "6502b76478b21b0001002640";
let queryPod = "konnectivity-agent-f79ffc68c-m2pm6";
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

//#check node events
//rdosmc.kusto.chinacloudapi.cn/rdos
let StartTime=datetime(2021-07-8 23:00);
let EndTime=datetime(2021-07-12 10:00);
WindowsEventTable
| where NodeId == "16cd52b5-1920-444e-a060-b32340651294" and PreciseTimeStamp between (StartTime..EndTime)
//| where Description contains "c54d41f6-0e59-4521-bf37-7eba85d8ed26"
| where Description contains "ecc1701f-8b4c-48b1-ab16-f96a0076fbf0"
//| where EventId == "17"
| project PreciseTimeStamp,NodeId, EventId,ProviderName, Description, Level, Cluster

//# since we can see that this node was faulted, check more fault RCA level.
//vmainsight.kusto.windows.net/vmadb
//node fault RCA level - vmadb
VMA
| where NodeId == "16cd52b5-1920-444e-a060-b32340651294"
| where PreciseTimeStamp  >= datetime(2021-06-22T00:00:00Z)
| where  PreciseTimeStamp <= datetime(2021-07-09T22:00:00Z)
| where RoleInstanceName == "_aks-nodepool1-32471634-5"
| project PreciseTimeStamp,RoleInstanceName,RCAEngineCategory, RCALevel1,RCALevel2, RCALevel3, RCA_CSS


//node status
TMMgmtNodeEventsEtwTable
| wherePreciseTimeStamp> datetime(2021-07-09 09:25)
| wherePreciseTimeStamp< datetime(2021-07-09 10:30)
| whereNodeId== "16cd52b5-1920-444e-a060-b32340651294"
| whereMessage!contains"AuditEvent"
| whereMessage!contains"Processed notification"
| projectPreciseTimeStamp, Tenant, RoleInstance, Message
| sortbyPreciseTimeStampasc

let starttime = datetime(2022-08-29 07:00:20.000);
let endtime = datetime(2022-08-30 23:00:20.000);
BlackboxMonitoringActivity
| where TIMESTAMP > ago(1h)
| where clusterName contains "cn-prdcne2-mfs-k8s"
| where subscriptionID contains "ead66674-258a-4465-bae1-05e099d9c709"
| project PreciseTimeStamp, subscriptionID, clusterName, region, fqdn,  ccpNamespace, k8sCurrentVersion, agentNodeName, state, reason, pod,  podsState, resourceState, addonPodsState, agentNodeCount, provisioningState, msg, resourceGroupName, resourceName, underlayName
| sort by PreciseTimeStamp desc

//============查autoscaler的日志========================
let starttime = datetime(2023-12-07 01:10:00.6812130);
let endtime = datetime(2023-12-07 01:51:00.6812130);
union 
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEvents,
cluster('akscn.kusto.chinacloudapi.cn').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where category contains 'autoscaler'
| where ccpNamespace contains "64c7b46533257c0001a32f35"
| project PreciseTimeStamp, properties

// 查aks autoscaler call CRP的log
 let starttime = datetime(2022-12-09 08:00:52.7181926);
 let endtime = datetime(2022-12-09 13:30:12.6721662);
 ApiQosEvent
 | where userAgent contains "cluster-autoscaler-aks"
 | where resourceGroupName contains "MC_ITSM_CN_aks-itsm-prod_chinanorth2"
 | where resourceName == "aks-nodepool-26775597-vmss"
 | join kind = inner(cluster('azcrpmc').database('crp_allmc').VmssQoSEvent
 | where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime) on $left.operationId == $right.operationId
 | project PreciseTimeStamp, operationId,  requestEntity, httpStatusCode, resourceName, e2EDurationInMilliseconds, userAgent, clientApplicationId, region, predominantErrorCode, errorDetails, subscriptionId, vmssName, resourceGroupName

//Azure Notification history for an Azure subscription
cluster('icmcluster.kusto.windows.net').database('AzNSPROD').AzNSTransmissionsMooncake
//| where SubscriptionId == "21d04625-57f4-4dc7-899a-a1b96e81f31d"
| where SubscriptionId == "db543b1a-3be0-4754-88ef-03578fd4013c"
| sort by CreatedTime desc
| project CreatedTime, NotificationState, MechanismType, WebhookHostUrl, FailureReason, AdditionalInfo, AssociatedGroupId
~~~

# Storage

~~~sh
	// ARM - Armmcadx - armmc
	EventServiceEntries
	| where TIMESTAMP between(datetime(2023-08-12 00:00)..datetime(2023-08-14 23:00))
	| where resourceUri contains "auditlogpoc"
	//| where operationName contains "Microsoft.Storage/storageAccounts"
	//| where correlationId contains "36242b30-42c0-473c-89e6-8058561ef6cf"
	| project PreciseTimeStamp, operationName, resourceProvider, correlationId, status, subStatus, properties, resourceUri, eventName, operationId, armServiceRequestId, subscriptionId, claims
	
	//ask region //xstore
    StorageAccountStatisticsRecord
    | where Timestamp between(datetime(2023-04-24 00:00)..datetime(2023-04-24 23:00))
    | where SubscriptionId == "0c51d0a1-bd08-43af-b21f-af793d7438ce" and AccountName contains "md-hdd-cdz3vqtqkz2s"
    | project Location, creationTime, primaryStampName, secondaryStampName
    
    // throttling check
    // armmcadx - armmc
    let subid = "263f665e-adc2-4a3e-91d7-74c3c7653141";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2023-04-18 00:00)..datetime(2023-04-21 23:00))
    | where subscriptionId == subid
    //| where httpStatusCode >= 200
    | summarize count() by bin(TIMESTAMP, 1d), operationName
    | order by count_ desc
    | where operationName contains "delete" and operationName !contains "GET"
    | limit 100
    
    // throttling check
    // armmcadx - armmc
    let subid = "f99c3d28-250e-4c4a-b0b6-92edb0849788";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2022-09-01 00:00)..datetime(2022-09-09 23:00))
    | where subscriptionId == subid
    //| where httpStatusCode >= 200
    //| summarize count() by bin(TIMESTAMP, 1d), operationName
    | order by count_ desc
    | where operationName contains "snapshot"
    
    
    //ARM or RP throttling check
    let subid = "3646fa3c-3957-4bc2-98ac-62cb7bd8374c";
    HttpOutgoingRequests
    | where TIMESTAMP between(datetime(2023-02-01 00:00)..datetime(2023-02-03 23:00))
    | where subscriptionId == subid
    | where httpStatusCode == 404
    //| summarize count() by hostName
    //| order by count_ desc

cluster('armmcadx.chinaeast2.kusto.chinacloudapi.cn').database('armmc').HttpIncomingRequests
| where subscriptionId == "3e600e64-be35-4347-93d5-2fb9f421a441"
|  where PreciseTimeStamp >= ago(1d) //datetime(2022-05-2 17:20:00) and PreciseTimeStamp <= datetime(2022-05-2 17:30:00)
| where targetUri contains "/subscriptions/3e600e64-be35-4347-93d5-2fb9f421a441/resourceGroups/Audit_Log_POC/providers/Microsoft.Storage/storageAccounts/auditlogpoc"
| where operationName !contains "GET"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp,operationName, httpMethod, correlationId,ActivityId,serviceRequestId, httpStatusCode, targetUri, exceptionMessage
    
    //List Storage Account Service SAS operations on a resource group, summarized by who/what is doing the operation.  
    //This helps us determine if it is a single client (ie. monitoring software) causing the throttling or lots of different clients/users.
    let subid = "3646fa3c-3957-4bc2-98ac-62cb7bd8374c";
    //let opname = "POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.STORAGE/STORAGEACCOUNTS/cvppprodstorage2019";
    HttpIncomingRequests
    | where TIMESTAMP between(datetime(2023-02-01 00:00)..datetime(2023-02-03 23:00))
    | where subscriptionId == subid
    | where httpStatusCode  == 404
    //| where operationName == opname 
    | summarize count() by clientIpAddress, principalOid, clientApplicationId, userAgent, httpStatusCode
    | order by count_ desc
    
    
    //
    HttpOutgoingRequests
    | where (TIMESTAMP >= datetime(2022-09-08 06:00) and TIMESTAMP < datetime(2022-09-08 10:00))
    | where subscriptionId has @'f99c3d28-250e-4c4a-b0b6-92edb0849788' 
    //| where httpStatusCode == 529
    | where httpMethod !contains "GET"
    
    //
    ClientErrors 
    | where TIMESTAMP between(datetime(2022-06-01 00:00)..datetime(2022-06-01 23:00))
    | where subscriptionId contains "1a24575f-4b4c-4a71-8204-1d9acfab1876"
    
    ClientRequests 
    | where TIMESTAMP between(datetime(2022-09-08 06:00)..datetime(2022-09-08 10:00))
    | where subscriptionId contains "f99c3d28-250e-4c4a-b0b6-92edb0849788"
    
//cluster('disksmc.chinaeast2.kusto.chinacloudapi.cn').database('Disks').
//Check if disk is soft deleted
DiskRPResourceLifecycleEvent
| where PreciseTimeStamp between(datetime(04/28/2023 00:00:00)..datetime(04/28/2023 23:39:41))//Choose a time shortly before the disk deletion
| where subscriptionId =~ '8650d1cb-b941-40a4-a1ba-8a9c72db9b3d'
| where resourceName has 'os' //or resourceName has 'CAAPMSVMPRD02_OSDISK_1_4067C60C0CE849D8929C4C7C911C1277'
//| where resourceGroupName has 'CAA-PMS-RG-PRD'
//| where diskEvent has 'softdelete'
| summarize max( bin(PreciseTimeStamp,1d)) by subscriptionId,resourceGroupName, resourceName
, blobUrl, diskEvent, RPTenant,MonitoringApplication
| order by max_PreciseTimeStamp asc
		 

HttpIncomingRequests
| where subscriptionId contains "38db9c2d-0b36-415a-8112-a00c1006fdf9"
| where PreciseTimeStamp >= datetime(2022-09-01 00:00:00) and PreciseTimeStamp <= datetime(2022-09-09 23:00:00)
//| where correlationId contains "8c45b856-eda2-4469-9c96-726793714ab7"
| where targetUri contains "dmpstorageaccountprddrg1"
// | where status notcontains "Accepted"
| where operationName contains "delete"
| where httpMethod != "GET"

let subid = "51a916f1-8712-489e-aa4a-98635e8aa76f";
HttpIncomingRequests
| where TIMESTAMP >= now(-30d)
| where subscriptionId == subid
| where httpStatusCode == 429
| summarize count() by bin(TIMESTAMP, 1d), operationName
| order by count_ desc

//Check operations
//https://armmcadx.chinaeast2.kusto.chinacloudapi.cn/armmc
ShoeboxEntries 
| where resourceId endswith "/auditlogpoc"
| where TIMESTAMP > ago(1d) and resultSignature contains "Failed" 
| project PreciseTimeStamp , resourceId , operationName , resultSignature , properties, correlationId

//查VM的非托管磁盘
cluster('https://rdosmc.kusto.chinacloudapi.cn').database('rdos').OsConfigTable
| where TIMESTAMP >= ago(10d)
| where ConfigValue contains "T-MAA3-ESBZ1-08"
// | where ConfigValue contains "c01e3e1b-e751-468c-8571-e3d7759a7409"// 
| where ConfigValue contains "t-maa3-hpc-06"| extend DiskPathCN = tostring(substring(ConfigName, indexof(ConfigName, '/') + 1))
//| where DiskPathCN startswith "md-fz1btkmfgqfn"| extend StorageCluster = extractjson('$.storagecluster', ConfigValue , typeof(string))
| extend _blobproperties = extractjson('$.blobproperties', ConfigValue , typeof(dynamic )) 
| extend diskUri=_blobproperties['x-ms-disk-resource-uri']// | summarize arg_max(PreciseTimeStamp ) by ConfigName, DiskPathCN,StorageCluster,diskUri 
| summarize arg_max(PreciseTimeStamp, DiskPathCN) by tostring(diskUri)

// 查存储账户的tenant信息
cluster('xstore.kusto.windows.net').database('xdataanalytics').XStoreAccountPropertiesHourly
| where TimePeriod >= ago(24d)
| where Account has 'md-hdd-5pwrqknld0mh'
//| where Subscription has 'xx'
| project TimePeriod, Tenant, Account

//https://xstore.kusto.windows.net/xstore
AccountTransactionsHourly
| where TimePeriod between(datetime(2023-09-12T00:00)..datetime(2023-12-12T23:00))
and BilledSubscription =~ "0bcf6f7f-0e7a-46e1-8f53-0fc387882f2f" 
| where AccountName contains "ce2cnepbstopdgem1"
//| where (RequestType contains "cool" and RequestType contains "Put")
| where RequestType contains "Total"
| project TimePeriod, AccountName, RequestType, AccessTier, TransactionType, TransactionCount, BillableTransactionCount, TotalIngress, TotalEgress ,BillableIngress, BillableEgress

//https://xstore.kusto.windows.net/xstore
AccountTransactionsDaily
| where TimePeriod between(datetime(2023-10-12T00:00)..datetime(2023-12-12T00:00))
| where BilledSubscription contains "0bcf6f7f-0e7a-46e1-8f53-0fc387882f2f"
| where AccountName contains "ce2cnepbstopdgem1"
| project TimePeriod, RequestType, AccessTier, TransactionType, TransactionCount, BillableTransactionCount  
~~~

# ACR

~~~sh
//Acrmc2
RegistryActivity
| where PreciseTimeStamp > ago(5h) //and PreciseTimeStamp < ago(d)
//| where level != "info"
| where http_request_host == "pubacrshared.azurecr.cn"
| where correlationid == "6d26304a-6d4e-4c66-b523-9416cd0726dd"

RegistryActivity
| where PreciseTimeStamp > ago(1d) //and PreciseTimeStamp < ago(d)
//| where level != "info"
| where http_request_host == "adientsrmdev.azurecr.cn"
//| where correlationid == "a781343a-d82a-4938-a560-0bd1a9470d64"

//Unique Manifests (with or without tag) the Registry has
//Acrmc2
WorkerServiceActivity
| where env_time > ago(14d)
//| where OperationName == "ACR.Layer: AddManifestRefAsync-Succeed"
| where RegistryLoginUri == "adientsrm.azurecr.cn" 
//| where Repository contains "dataplatformworkflow" 
//| summarize count() by Repository, Tag, Digest
| project TimeStamp, Repository, Tag, Digest

WorkerServiceActivity
| where env_time > ago(30d)
| where OperationName == "ACR.Layer: ExecuteOperationOnListManifestsAsync"
| where RegistryLoginUri == "adientsrmdev.azurecr.cn"
// we can look for a specific type of image
//| where ImageType == "Docker"
| extend numManifests = toint(substring(Message, 52, strlen(Message) - 11 - 52))
| summarize numManifests = sum(numManifests) by bin(env_time, 1d), RegistryId, RegistryLoginUri, ImageType  

union 
cluster('romeeus.kusto.windows.net').database('ProdRawEvents').ContainerVA_ImageScanLifeCycleEvents,
cluster('romeuksouth.uksouth.kusto.windows.net').database('ProdRawEvents').ContainerVA_ImageScanLifeCycleEvents 
//| where GeneratedTimestamp > ago(10d)
| where SubscriptionId == "91da4a46-67d2-4043-a218-e5804ef74831"
//| where * contains "sha256:d2ef748ca082fc80237f1da20673fe4d0b57486317bbfe5633586c845c346ee7"
| extend TriggerType = parse_json(tostring(parse_json(AdditionalData).["TriggerType"]))
| extend ScanResultToHandle = parse_json(tostring(parse_json(AdditionalData).["ScanResultToHandle"]))
| extend RequestId = parse_json(tostring(parse_json(ScanResultToHandle).["RequestId"]))
| extend errorReason = tostring(AdditionalData.ScanResultToHandle.ScanErrorReason)
| extend IsTransient = tostring(AdditionalData.ScanResultToHandle.IsScanErrorTransient)
| extend ExternalErrorData = tostring(AdditionalData.ScanResultToHandle.ScanErrorExtraInformation)
| order by GeneratedTimestamp desc


//看ACR的push操作记录
ContainerVA_RegistryImageEvents
| where SubscriptionId == 'fecd2352-d290-4df6-8048-9aa8daccc9f1'


//=========ACI===================
let starttime = datetime(2023-09-11 22:00:00);
let endtime = datetime(2022-09-12 10:10:00);
cluster('acimooncake.chinaeast2.kusto.chinacloudapi.cn').database('acimooncake').HttpIncomingRequests
| where PreciseTimeStamp >= ago(8h)
| where subscriptionId == "c51160af-3d33-4c28-98fa-3d9c350ce597"
//| where targetUri contains "qi"
| where correlationId == "051460b9-d00f-4d84-97d3-6fa4c9a9eac2"
//| where httpMethod == "PUT"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp, TaskName, durationInMilliseconds, errorMessage, errorCode, httpMethod, operationName, serviceRequestId, httpStatusCode, subscriptionId, ActivityId, targetUri, correlationId, exceptionMessage, clientIpAddress

~~~

# MDC

~~~sh
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


//#connect "https://romelogsmc.kusto.chinacloudapi.cn/Prod"
let subscriptionId = "08ba6e07-14eb-4984-9176-9261b8a2781d";
let startTime = datetime(2022-09-06 00:50:00);
ServiceFabricIfxTraceEvent 
| where env_time between (startTime .. (startTime +24h))
//| where message contains subscriptionId// and message contains " MFA "// and message contains userOid
| where message contains "recommendation" and message contains "Log Analytics"
| project env_time, message


//romelogsmc
let subscriptionId = "faa06be4-8418-4b32-96e8-f9823d9e55b1";
SubscriptionActivityQueryOE
| where env_time > ago(30d)
| where SubscriptionId == subscriptionId
| summarize arg_max(env_time, *) by ActivityStatus
| project env_time, ActivityStatus

let subscriptionId = "faa06be4-8418-4b32-96e8-f9823d9e55b1";
DynamicWithSubscriptionOE
| where env_time > ago(2d)
| where SubscriptionId == subscriptionId and operationName == 'IdentityScanner'
| project env_time, customData, rootOperationId 
| sort by env_time desc 

let rootOperationId = "{rootOperationId}";
TraceEvent
| where env_time > ago(2d)
| where env_cv has rootOperationId
| where tagId has "IdentityScanner" or tagId has "IdentityUtils" or tagId has "IdentityDesignateMoreThanOneOwner" or tagId has "IdentityDesignateLessThanXOwners" or tagId has "IdentityRemoveDeprecatedAccounts" or tagId has "IdentityRemoveExternalAccountsWithPermissions" or tagId has "IdentityEnableMFAForAccountsWithPermissions"
| project env_time, message


//continue to validate that the assessments were correctly sent to the ingestion platform
let assessmentKey = "1ff0b4c9-ed56-4de6-be9c-d7ab39645926";
let subscriptionId = "faa06be4-8418-4b32-96e8-f9823d9e55b1";
DynamicOE
| where env_time > ago(30d)
| where operationName == "SendSubAssessmentsAsync"
| where customData has subscriptionId 
| where customData has assessmentKey
| project env_time, customData

//
AssessmentsNonAggregatedStatusSnapshot
| where SubscriptionId == "{subscriptionId}"
| extend  AssessedResourceName = split(AssessedResourceId, "/")[-1], AssessedResourceType = split(AssessedResourceId, "/")[-2]
| summarize arg_max(Timestamp, *) by AssessedResourceId
| project Timestamp, AssessmentKey, AssessmentsDisplayName, ReleaseState, AssessedResourceName, AssessedResourceType, StatusCode, StatusCause, StatusDescription, StatusChangeDate, FirstEvaluationDate , AssessedResourceId

RecommendationsData(31d,0d)
 | where AssessmentDisplayName has "Cognitive Services accounts should enable data encryption with a customer-managed key (CMK)"
~~~

# CRP

~~~sh

//----------------CRP operation---------------------------------------------------
// Check VM deployment time
//Execute: [Web] [Desktop] [Web (Lens)] [Desktop (SAW)] https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc
ApiQosEvent_nonGet
| where subscriptionId == "0c51d0a1-bd08-43af-b21f-af793d7438ce"
| where PreciseTimeStamp >=  datetime(2023-04-20) 
| where resourceName in ( "9d3574460a204df395cb56a37858a09b")
| where operationName == "VirtualMachines.ResourceOperation.PUT"
| project PreciseTimeStamp, resourceGroupName, resourceName, e2EDurationInMilliseconds
| order by PreciseTimeStamp asc 

//Check VM start timeout
VMApiQosEvent
| where TIMESTAMP >= datetime(2022-04-12T00:00:00.0000000Z) and TIMESTAMP <= datetime(2022-12-31T16:00:00.0000000Z)
| where ((* has @'14e2e248-5151-4432-8b87-ddd8722fc6b7' and * has @'wps1_') ) and errorDetails contains "VMStartTimedOut" //|and * has @'exception')
| extend error = parse_json(errorDetails)
//| project TIMESTAMP,resourceName, correlationId,operationName,errorDetails
| project PreciseTimeStamp, operationId, correlationId, operationName, resultCode, resourceName, errorDetails, subscriptionId, RPTenant

cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ApiQosEvent 
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
//| where resourceGroupName contains "databricks-rg-Magellan-EDW-ODS-Databricks-PRD-frurg63i5udpw"
//| where resourceName contains "KAFDV1BUY03"
//| where operationName contains "Disk"
//| where resultCode contains "ProvisioningError"
| where correlationId == "5256b6e1-7831-45b2-bd9f-df20a393f0d3"
| extend error = parse_json(errorDetails)
| project PreciseTimeStamp, operationId, correlationId, operationName, resultCode, resourceName, resourceGroupName, errorDetails, userAgent, requestEntity, subscriptionId, region, RPTenant, msg=tostring(error.message)

//--------------------Check the detailed process of an operation---------------------------------------
//--------------activityID = Operation ID got from ApiQosEvent ------------------------------------
cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity 
| where PreciseTimeStamp >= datetime(2023-12-07 01:00:00) and PreciseTimeStamp <= datetime(2023-12-07 02:00:00)
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
| where activityId == "42d42aa3-4b9f-4c48-8171-731b791059e3"
//| where message contains "fail"
| project PreciseTimeStamp, activityId, message, traceCode, subscriptionId, goalStateResourceId

cluster('azcrpmc.kusto.chinacloudapi.cn').database('crp_allmc').ContextActivity 
| where PreciseTimeStamp >= datetime(2023-12-07 00:00:00) and PreciseTimeStamp <= datetime(2023-12-07 23:00:00)
| where subscriptionId == "a3846e58-767e-462b-824b-a6a769161ae9"
| where activityId == "7ed392d6-7eda-41d8-951d-f46a2efa4155"
| project PreciseTimeStamp, activityId, message, traceCode, subscriptionId, goalStateResourceId

let queryFrom = datetime("2022-12-19T00:40:31.000Z");
let queryTo = datetime("2022-12-19T01:23:00.000Z");
let queryContainerId = "55ee0b4a-ceb4-41cc-b336-bd170551fe78";
let queryNodeId = "fa00fc2e-b57a-3402-b118-c53d8d943f2a";
cluster("https://azurecm.chinanorth2.kusto.chinacloudapi.cn").database("azurecm").DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| where interfaceId contains queryContainerId
| project PreciseTimeStamp, nodeId, interfaceId, message
| order by PreciseTimeStamp asc
~~~

# backup+ASR

~~~sh
//=======backup=================
let _resId="/subscriptions/8fc622eb-ff9b-43a5-834b-da271f8e9b4d/resourceGroups/Backup/providers/Microsoft.RecoveryServices/vaults/AzureCloudBackup";
union cluster('mabprod1').database('MABKustoProd1').BMSProtectionStats, 
 cluster('mabprodweu').database('MABKustoProd').BMSProtectionStats, 
 cluster('mabprodwus').database('MABKustoProd').BMSProtectionStats
| where ResourceId  == _resId
//| where OperationName == "BackupManagementSoftDelete"
| project StartTime,DataSourceId,DataSourceType,ContainerType,ContainerUniqueName,SubscriptionId,RequestId,TaskId,OperationName

// https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
EventLog
| where PreciseTimeStamp >= datetime(2023-06-29 04:00:00) and PreciseTimeStamp <= datetime(2023-07-07 06:00:00)
| where DataSourceId contains "3377805273646306104"
| where RequestId contains "665a847e-1bb4-4860-b104-87a71d4143c6"

// https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
DatasourceSummaryStats 
| where PreciseTimeStamp >= datetime(2023-06-20 04:00:00) and PreciseTimeStamp <= datetime(2023-07-7 06:00:00)
| where DataSourceId == "3377805273646306104"

SubscriptionDetailsStats 
| where SubscriptionId contains "8fc622eb-ff9b-43a5-834b-da271f8e9b4d"

CBPRecoveryStatsTelemetry 
| where DatasourceId == "3377805273646306104"

TraceLogMessage
| where PreciseTimeStamp >= datetime(2023-06-30 00:00:00) and PreciseTimeStamp <= datetime(2023-07-01 06:00:00)
| where DeploymentName contains "bjb-pod01"
| where DataSourceId == "3377805273646306104"
| where RequestId contains "665a847e-1bb4-4860-b104-87a71d4143c6"

//let _resId="/subscriptions/84fc9cb0-2c61-4711-81f3-3c3fe611f9bf/resourceGroups/Halo_DEV/providers/Microsoft.KeyVault/vaults/HALODEV";
let _subId="8fc622eb-ff9b-43a5-834b-da271f8e9b4d";
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

//**context
//armmcadx - armmc
EventServiceEntries
| where TIMESTAMP >ago(30d)
| where subscriptionId contains "8fc622eb-ff9b-43a5-834b-da271f8e9b4d"
| where operationName contains "Microsoft.RecoveryServices"
//| where status == "Failed"
| project PreciseTimeStamp, status,subscriptionId, operationName , resourceUri, RoleLocation//, correlationId ,properties
//| order by 

union cluster('mabprod1').database('MABKustoProd1').BCMBackupStats, 
union cluster('mabprodwus').database('MABKustoProd').BCMBackupStats, 
cluster('mabprodweu').database('MABKustoProd').BCMBackupStats 
| where SubscriptionId == "8fc622eb-ff9b-43a5-834b-da271f8e9b4d" 
| where VMName == "AzureCloudBackup" 
| where PreciseTimeStamp >= datetime(2023-06-12 00:00:00) and PreciseTimeStamp <= datetime(2023-06-30 23:30:00)
| project TIMESTAMP, VMName , DeploymentName, IsInstantRPEnabled , IsScheduledBackup , RPExpiryTime , DataSourceId , ResourceId , ContainerId , ContainerName, RecoveryPointId , TaskId

//====================ASR================================
//#connect "https://asradxclusmc.chinanorth2.kusto.chinacloudapi.cn/ASRKustoDB"
// CFG/ProcessServer Information 
let SubscriptionId="a05d057c-aeda-4fcd-abf2-b42af384bc31";
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
//| where processServerName contains "vtasr" or processServerName contains "AVTA"
//| where configServerName contains "HUZSDRA01"

//Process Server Heartbeat in SRS Telemetry
let SubscriptionId="3082ff43-8592-4859-a831-d8d7aab9421a";
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
| where processServerName  contains "VTASRAP"


//PS Register disappear INFO
//Execute: [Web] [Desktop] [Web (Lens)] [Desktop (SAW)] https://mabprodmcadx.chinaeast2.kusto.chinacloudapi.cn/MABKustoProd
database('MABKustoProd').InMageAdminLogV2
| where MachineId == "6F2ACE5F-60CE-AA40-9401D144FFEDBE84" //or MachineId == "83ED0EA6-0930-4A47-AE4EA9EFC93537E3"
| where PreciseTimeStamp > datetime(2021-08-14 13:30) and PreciseTimeStamp < datetime(2021-08-14 23:30)
//|where PreciseTimeStamp >datetime(2021-09-01 07:20:20.8560085)
| where Message contains "ProcessServer Registration"
| where SubComponent contains "PSCore/TaskMgr"
 | project PreciseTimeStamp, AgentTimeStamp, MachineId, SubComponent, AgentPid, AgentLogLevel, Message
| sort by PreciseTimeStamp desc nulls last

//查看复制的项的健康状态
SRSShoeboxEvent
| where PreciseTimeStamp between (ago(24h) .. now())
| where category == "AzureSiteRecoveryReplicatedItems"
| extend parsedProperties = parsejson(properties)
| parse resourceId with *'/SUBSCRIPTIONS/'SubscriptionId'/RESOURCEGROUPS'*
| extend SubscriptionId = tolower(SubscriptionId)
| where SubscriptionId == "5d24c88a-e104-419a-a9cd-b2563ded04d8"
| extend HostId=tostring(parsedProperties.id)
| extend SourceVmName=tostring(parsedProperties.name)
| extend ReplicationHealth=tostring(parsedProperties.replicationHealth)
//| where ReplicationHealth == "Critical/Warning/Normal"
//| where SourceVmName contains "<HostName>"
//| where HostId == "<HostId>"
| summarize arg_max(PreciseTimeStamp, *) by tostring(parsedProperties.correlationId)
| project PreciseTimeStamp, ProtectedItemName=tostring(parsedProperties.name), ProtectionState=tostring(parsedProperties.protectionState), ReplicationHealth=tostring(parsedProperties.replicationHealth),OS=tostring(parsedProperties.osFamily), PS = tostring(parsedProperties.primaryFabricName), Provider = tostring(parsedProperties.primaryFabricType),ReplicationhealthErrors=parsedProperties.replicationHealthErrors, AgentLastHeartbeat=parsedProperties.lastHeartbeat,StorageAccount = tostring(parsedProperties.targetStorageAccountName), AgentVersion = tostring(parsedProperties.agentVersion)

InMageTelemetryPSV2
| where HostId == "a2c2cd7e-91a8-4e58-bd86-145226c2e02d"
| summarize max(PreciseTimeStamp) by PSHostId, HostId , DiskId

SRSOperationEvent
| where SubscriptionId== "a05d057c-aeda-4fcd-abf2-b42af384bc31"
//| where WorkflowName contains"cert"
| where ObjectName contains "Huzstsls03"
//| where State contains "Failed"
| where TIMESTAMP between( datetime(2023-07-11 00:00:00)..datetime(2023-07-13 23:00:30))
//| project TIMESTAMP,StampName,ClientRequestId,State,WorkflowName,ObjectType,ObjectName, EventMessage

//----------------------------------------------------------------------------------------------

// check backlog 
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(3h) 
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1805978636076306803") //projectstorage01
//|where DataSourceId in ( "1805978636076306803", "1805978637002300982", "1805978635832687323")
//|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState//| sort by RPOtime desc
| where DiskId == "DATADISK19" 
| project PreciseTimeStamp, VmName, BacklogSessionCount, RPOMins, DiskId

//check RPO
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(2h) 
//|where LatestRpMarkerId != 'null'
| where DataSourceId in ( "1805978636076306803", "1805978637002300982", "1805978635832687323")
| summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState, DataSourceId
| sort by RPOtime desc//| project VmName, DiskId, VhdReplicationState, PreciseTimeStamp

//check RPO
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(4h) 
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1805978636076306803", "1805978637002300982", "1805978635832687323")
|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState, DataSourceId
| sort by RPOtime desc
//| project VmName, DiskId, VhdReplicationState, PreciseTimeStamp

//disk7 的backlog增减
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').HvrDsTelemetryStats
|where TIMESTAMP > ago(13h) 
//|where LatestRpMarkerId != 'null'
|where DataSourceId in ( "1805978637002300982")
//|summarize RPOtime = max(LatestRpReplicationTimeUTC) by LatestRpMarkerId, VmName, DiskId, AppConsistentInterval , ReplicationInterval , VhdReplicationState//| sort by RPOtime desc
| where DiskId == "DATADISK7"
| project PreciseTimeStamp, VmName, BacklogSessionCount, RPOMins, DiskId

// check errors
let enumToCodeTable = cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SrsErrorEnumToCode();
SRSShoeboxEvent
| where PreciseTimeStamp > ago(48h)
| extend VmDay=bin(PreciseTimeStamp, 24h)
| where category == "AzureSiteRecoveryReplicatedItems"
| parse resourceId with *'/SUBSCRIPTIONS/'SubId'/RESOURCEGROUPS'*
//| parse resourceId with *'/SUBSCRIPTIONS/6cebbc3f-c68b-47fb-a047-19b23812df2c/RESOURCEGROUPS'*
| extend SubscriptionId = tolower("a05d057c-aeda-4fcd-abf2-b42af384bc31")
| where SubscriptionId == "a05d057c-aeda-4fcd-abf2-b42af384bc31"
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
| where SourceVmName contains "Huzstsls03"
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
 
SRSDataEvent
| where SubscriptionId == "a05d057c-aeda-4fcd-abf2-b42af384bc31"
| where ClientRequestId == "bc69ae27-a349-4045-b7a3-9941d0e4e6eb"
| where TIMESTAMP between ( datetime(2023-07-12 00:00:00)..datetime(2023-07-12 23:00:30))
| project PreciseTimeStamp, LogLevel, Message

//================ASR enable failure===============================

// get all replication jobs in subscription 
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSOperationEvent 
| where SubscriptionId == "7a23a2af-e8b9-4248-b715-230e9758164c" 
| where PreciseTimeStamp >= datetime(2023-03-06 08:00:00) and PreciseTimeStamp < datetime(2023-03-08 10:50:00)
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, ServiceName, ClientRequestId, SRSOperationName, State,  ObjectType, ObjectName, Region, ContainerId , ResourceId  , TimeTaken
 
 // check job details using job id. 
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent 
| where ClientRequestId == "793d436a-a101-427d-8eba-f1c2ad411e2b"  // job id
//| where Level <= 3
| project PreciseTimeStamp,Message, Level

// **** Check SRS all operation flow 
// **** A2AEnableProtectionTargetWorkflow 
// **** A2AInstallMobolitrServiceWorkFlow
// **** A2ACreateProtectionTargetWorkflow 
// **** A2AStartInitialReplicationWorkflow 
// **** CompleteInitialReplicationWorkflow * 2
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent 
| where ClientRequestId == "793d436a-a101-427d-8eba-f1c2ad411e2b" // projectstorage01
| where Message contains "SRS operation Started. | Params: {Operation = "  or  Message contains "SRS operation Completed. | Params: {Operation = "  
| project  PreciseTimeStamp, Message, Level 
| sort by PreciseTimeStamp asc

// ***** Get Extension Install log 
// ***** /var/log/azure/Microsoft.Azure.RecoveryServices.SiteRecovery.xxx
// ***** (Key Words: Logging extensionlog with continuation id: xxxx ) 
cluster('asradxclusmc.chinanorth2.kusto.chinacloudapi.cn').database('ASRKustoDB').SRSDataEvent 
| where ClientRequestId == "793d436a-a101-427d-8eba-f1c2ad411e2b" // projectstorage01
| where Message contains "Logging extensionlog with continuation id"
//| where Message contains "8c44b33c-f9ca-4dc1-a028-e35e7c6a7598"  //continuation id of above query
| project  PreciseTimeStamp, Message, Level 
| sort by PreciseTimeStamp asc
~~~

# Monitor+Automation

~~~sh
//---------------------- Query all kind of IDs -------------------------------------------------------
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp >= datetime(2022-10-30 00:00:00.0000000) and PreciseTimeStamp <= datetime(2022-11-01 06:40:00.0000000)
| where subscriptionId == "a82e1173-fdb0-4f72-a553-f2ccc2f314a2" //and roleInstanceName contains "cn2-prd-commerce-elasticsearch-catalog-tr1-elkdata_126"
| where availabilitySetName == ""
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName

//#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
| where PreciseTimeStamp > ago(3d)
| where NodeId in~ ('6d917393-3f43-f652-6ff8-9d1e0369ab4b')
| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170',155,15)
| where ProviderName contains "UpdateNotification" or ProviderName contains "OSHostPlugin"
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId

//Check update end time
TMMgmtNodeTraceEtwTable
| where PreciseTimeStamp >= datetime(10/31/2022 07:00:00) and PreciseTimeStamp <= datetime(2022-10-31 09:59:06)
| where BladeID == "6d917393-3f43-f652-6ff8-9d1e0369ab4b"
| where Message contains "VmphuPF"
//| where Message contains "20221013_pf2_win_ah2021_497_144_0_10_509"
| project TIMESTAMP, Tenant, BladeID, Message
| sort by TIMESTAMP  asc nulls last

//Check update accurate timeline
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(10/31/2022 07:00:00) and PreciseTimeStamp <= datetime(2022-10-31 08:48:00)
| where NodeId == "d38e55fd-c0dc-4782-abf4-11edd79c0958"
//| where Message contains "ImageName"
//| where Message contains "OSHP Deployment Team"
| where Message contains "phu"
//| where Message contains "37fd4ba2-b55d-4195-8149-9be9a2a06ee6"
| summarize arg_min(PreciseTimeStamp, *) by NodeId
| project PreciseTimeStamp , Tenant, NodeId , Message

DiskRPResourceLifecycleEvent 
| where MonitoringApplication == "DiskRP-chinanorth_Monitoring" //-- Set the Region <DiskRP-<Region>_Monitoring>
| where subscriptionId == "10084850-bc56-47f3-9756-b721f5274e5c" //-- Select the Subscription ID
| where resourceName contains "BPDynamics" or resourceName contains "DB" or resourceName contains "PRD"  //-- <Name of the disk. If you don"t have the name of the disk, you could skip this line.>
| where diskEvent contains "SoftDelete"
| where PreciseTimeStamp >= (datetime(2022-11-06)) //-- Choose a time shortly before the disk deletion
| project PreciseTimeStamp, resourceGroupName, resourceName, pseudosubscriptionId, blobUrl, diskEvent, RPTenant

LogContainerSnapshot
| where PreciseTimeStamp > datetime(2023-04-16 01:00:00) and PreciseTimeStamp < datetime(2023-04-21 09:00:00)
| where subscriptionId == "ce28076b-0a9f-4e33-853b-adfa7cac1f05" and availabilitySetName == "EC2PRDDLBDB-AS"//and roleInstanceName contains "CNCORPAZPDGTM1"
| summarize by roleInstanceName
//| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId

LogContainerHealthSnapshot
| where PreciseTimeStamp > datetime(2023-04-16 01:00:00) and PreciseTimeStamp < datetime(2023-04-21 09:00:00)
| limit 10

let querySubscriptionId = "725316d8-fa91-43a9-ac40-1e607f602e4f";
let queryResourceGroupName = "MC_aze2-rgec-p_aze2-aks01-p_chinaeast2";
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

let queryClusterVersion = "622ab7e2a1c3dc0001f530e5";
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


let queryFrom = datetime("2023-05-05T17:00:00.000Z");
let queryTo = datetime("2023-05-05T20:28:21.000Z");
let querySubscription = "725316d8-fa91-43a9-ac40-1e607f602e4f";
let queryManagedRg = "MC_aze2-rgec-p_aze2-aks01-p_chinaeast2";
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
    userAgent == "ACIS-CRP", "Geneva Action",
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

OsFileVersionTable
| where Cluster == "BJS20PrdApp01" and PreciseTimeStamp >= ago(30d) and NodeId  == "702629fa-7478-46fe-9ed9-94956ede6f05"
| where FileName contains "blobcache.sys"
| summarize dcount(NodeId) by FileName, FileVersion

OsFileVersionTable
| where Cluster == "BJS20PrdApp06a" and PreciseTimeStamp >= ago(30d)
| where FileName contains "blobcache.sys"
| summarize dcount(NodeId) by FileName, FileVersion// between (datetime(2023-04-25 00:00:00) ..12h)
//| project PreciseTimeStamp, OsDiagDurationInSec


//rdos
let StartTime = datetime(2023-04-24 01:00:00);
let endTime = datetime(2023-04-24 03:00:00);
HyperVStorageStackTable
| where PreciseTimeStamp > StartTime and PreciseTimeStamp < endTime
| where NodeId == 'f8209eab-5350-488e-b26b-41439f79814d'
| where EventMessage contains '3c3adcba-fefa-4852-8bad-b5e578e92e26' //container id
| where EventId == 9
| project PreciseTimeStamp, NodeId, EventId, EventMessage, Message

let startTime = datetime("2023-04-24T01:00:00.000Z");
let endTime = datetime("2023-04-24T03:00:00.000Z");
let nodeId = "f8209eab-5350-488e-b26b-41439f79814d";
OsRDSSDSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where SurfaceName contains "3c3adcba-fefa-4852-8bad-b5e578e92e26"
| project PreciseTimeStamp, BlobPath, SurfaceName, HighIOLatInms, CurIOLatInms


let startTime = datetime("2023-04-24T01:00:00.000Z");
let endTime = datetime("2023-04-24T03:00:00.000Z");
let nodeId = "f8209eab-5350-488e-b26b-41439f79814d";
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and EventId  == 13 and EventMessage contains "dcf40vfhwsn5"
| project PreciseTimeStamp, EventId, EventMessage


let queryFrom = datetime("2023-04-24T01:30:00.000Z");
let queryTo = datetime("2023-04-24T02:30:45.000Z");
let queryNodeId = "f8209eab-5350-488e-b26b-41439f79814d";
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

let queryCcpNamespace = "622ab7e2a1c3dc0001f530e5";
let querynode = "aks-nodepool2-42314929";
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
 
 EventServiceEntries 
| where subscriptionId == "725316d8-fa91-43a9-ac40-1e607f602e4f"
| where PreciseTimeStamp >= datetime(2023-05-05 17:00:00) and PreciseTimeStamp <= datetime(2023-05-05 19:00:00)
| where resourceUri contains "aks-nodepool3-16994892"//"aks-nodepool2-42314929"
| sort by PreciseTimeStamp asc nulls last
| project PreciseTimeStamp, operationName, resourceProvider, correlationId, status, subStatus, properties, resourceUri, eventName, operationId, armServiceRequestId, subscriptionId, claims

//=====CN3 NO IP=========
 //#connect "https://azcrpmc.kusto.chinacloudapi.cn/crp_allmc"
let uri="/subscriptions/b5939b57-f3ef-4cfa-b425-64ce459b0423/resourceGroups/CN3-NPRD-BPMS-RG-000/providers/Microsoft.Compute/virtualMachines/ucncn3aapp003";
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
 
 //#connect "https://azurecm.chinanorth2.kusto.chinacloudapi.cn/azurecm"
DCMNMAgentProgrammingDurationEtwTable 
| where TIMESTAMP >= datetime('2023-5-16 00:00:00') and TIMESTAMP <= datetime('2023-5-16 03:05:53')
| where Tenant  == "ZQZ20PrdApp06"
| where * contains "037c5c6b-88ba-4842-88f4-dcf338d2be76" //VM ContainerID
| project PreciseTimeStamp,message,interfaceId,programmingDelayInSeconds


ApiQosEvent
| where PreciseTimeStamp between (datetime(2023-05-24T06:00) .. datetime(2023-05-24T07:50))
| where subscriptionId has 'db543b1a-3be0-4754-88ef-03578fd4013c'
| where resourceName has 'aks-qaaksnodes1-44962715-vmss'
| where operationName  == "VMScaleSetVMs.VMScaleSetVMsOperation.PUT"
//| where requestEntity has "kubernetes-internal"
| project PreciseTimeStamp,operationName,correlationId, userAgent,requestEntity


union ControlPlaneEvents, ControlPlaneEventsNonShoebox
//union cluster('aks.kusto.windows.net').database('AKSccplogs').ControlPlaneEventsNonShoeboxOld,cluster('aks.kusto.windows.net').database('AKSccplogs').ControlPlaneEventsOl
| where PreciseTimeStamp >= datetime(2023-05-24 06:00:00) and PreciseTimeStamp <= datetime(2023-05-24 07:30:30)
| where resourceId has "/subscriptions/db543b1a-3be0-4754-88ef-03578fd4013c/resourceGroups/mkvcrmqarg/providers/Microsoft.ContainerService/managedClusters/QAAKSCluster" //or ccpNamespace contains "5dfd541f64a4b2000102e6d1"
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

cluster("sparkle.eastus").database("defaultdb").WheaXPFMCAFull
| limit 10
~~~

# AAD

~~~sh

// Connection = https://armmcadx.chinaeast2.kusto.chinacloudapi.cn
// Role assignment creation or deletions
EventServiceEntries
| where subscriptionId == "f99c3d28-250e-4c4a-b0b6-92edb0849788"
| where TIMESTAMP >= ago(30d)
| where operationName has_any ("Microsoft.Authorization/roleAssignments", "Microsoft.Authorization/classicAdministrators")
| project TIMESTAMP, operationName, status, principalOid, principalPuid, subscriptionId, httpRequest, properties, resourceUri, claims

CertificatesInventory
| where TIMESTAMP >= ago(60d)
| where Tenant contains "90aa5e12-60df-4601-aeca-c28cc0f6674a"

AppHealthEvent
| where TIMESTAMP >= ago(60d)
| where Tid == "90aa5e12-60df-4601-aeca-c28cc0f6674a"

ApplicationEvents
| where TIMESTAMP >= ago(60d)
| where Tenant contains "90aa5e12-60df-4601-aeca-c28cc0f6674a"

//查AAD 写入, 拿到correlation id查details
//https://msodsmooncake.chinanorth2.kusto.chinacloudapi.cn/MSODS
IfxUlsEvents
| where * has "01e19238-2074-43e5-848c-bfdb1fc27318"
| where env_time > datetime(2023-10-25 00:00) and env_time < datetime(2023-10-25 23:00)
//| where message startswith "[Aws::CreateSyncObjectResult]"
| project env_time, message

//查CA policy
//#connect "https://estscnn2.chinanorth2.kusto.chinacloudapi.cn/ESTS"
let start = datetime(2023-08-07 14:19);
let period = 30min;
PerRequestTableIfx
| where env_time > start - period and env_time < start + period
| where CorrelationId == "19d02f54-d7f5-4666-9e0a-580dc6e051fb"
| project env_time, CorrelationId, RequestId, ClientTypeForConditionalAccess, Result, ApplicationId, ResourceId, ErrorCode, ConditionalAccessVerboseData

//#connect "https://msodsmooncake.chinanorth2.kusto.chinacloudapi.cn/MSODS"
IfxBECAuthorizationManager
//Filter with servicePrincipalObjectId or UserObjectId
//| where servicePrincipalObjectId == "0777ebf3-ff41-4592-8d41-b99404399fdc"
//| where tenantName contains "CSSMooncake"
| where userObjectId contains "6a3524a8-abcf-4310-b40d-3c3a257c35c1"
| where env_time > datetime(2023-10-19 00:30) and env_time < datetime(2023-10-20 02:56)
| project env_time, internalCorrelationId, result, parameters, task, scopeClaim, userObjectId, servicePrincipalObjectId, isAppGrantedAccess
~~~

# Health Event

~~~sh
// Check ServiceHealth
// https://icmcluster.kusto.windows.net | database("ACM.Publisher")
ServiceHealthPublisherCommunications | where TrackingId == 'NL9G-JP8'

// Check ServiceHealth affected subid
// need CommunicationId obtained from above
// https://icmcluster.kusto.windows.net | database("ACM.Publisher")
ServiceHealthTargets
|  where CommunicationId == '11000098746714'
~~~

# AH2021 patch

~~~sh
//Azurecm - azurecm
//看node和container id
LogContainerSnapshot
| where PreciseTimeStamp > datetime(2023-05-14 07:00:00) and PreciseTimeStamp < datetime(2023-05-14 09:00:00)
| where subscriptionId == "0050641c-cefb-4119-b748-c6cc4556a027" and roleInstanceName contains "CNCORPAZPDLDW8"
| project creationTime, RoleInstance, Tenant, tenantName, nodeId, containerId, containerType, availabilitySetName, roleInstanceName, virtualMachineUniqueId

// 查node是否已经被打上了补丁 
let NodeList = datatable(NodeId:string)
[
"657f6d8d-e051-47c2-9245-d5a2c3ac167b",
"5a665970-7c54-4f31-a72b-5e686da72101",
"c270f9a4-edfb-c32f-1ab9-d52bb085dccb",
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


//different WindowsEventTable
// Check if there's update
cluster('Rdosmc').database('rdos').WindowsEventTable
//| where PreciseTimeStamp between(datetime({starttime})..1d)
| where PreciseTimeStamp >= datetime(2023-11-01 03:20:00) and PreciseTimeStamp <= datetime(2023-11-01 04:00:00)
| where NodeId in~ ('76f06633-6b84-49fa-914c-baecbdc5a96c')
//| where EventId!in('512', '510','511', '504', '505','146', '1004', '1008', '37', '303','300','145', '142','154','4', '3095', '0','31','400','410','170','155','15')
//| where EventId == 1
| project TimeCreated, Cluster, NodeId,  EventId, ProviderName, Description
| order by TimeCreated asc
//| sort by DeviceId

let queryFrom = datetime("2023-03-12T00:00:11.000Z");
let queryTo = datetime("2023-03-12T06:42:17.000Z");
let queryNodeId = "7d51d505-3e7b-44fb-9f08-9fe98828b4b7";
//let queryNodeId = "5a665970-7c54-4f31-a72b-5e686da72101";
//let queryNodeId = "c270f9a4-edfb-c32f-1ab9-d52bb085dccb";
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


//Check state of nodes, detailed version
//Azurecm - azurecm
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp > datetime(2023-03-12 02:00:00.000) and PreciseTimeStamp < datetime(2023-03-12 06:00:00.000)
| where NodeId =~ "657f6d8d-e051-47c2-9245-d5a2c3ac167b"
| project PreciseTimeStamp, Message

cluster('icmcluster.kusto.windows.net').database("ACM.Publisher").
IridiasTargets 
| where TrackingId contains "2K1S-390"
| where Subscriptions contains "0050641c-cefb-4119-b748-c6cc4556a027"
~~~
