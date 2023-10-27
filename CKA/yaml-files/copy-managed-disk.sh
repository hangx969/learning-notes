#Provide the subscription Id of the subscription where managed disk exists
sourceSubscriptionId="f99c3d28-250e-4c4a-b0b6-92edb0849788"

#Provide the name of your resource group where managed disk exists
sourceResourceGroupName="Hangcentos8-RG"

#Provide the name of the managed disk
managedDiskName="hangentos8_OsDisk_1_67208bc4fec546a2b3586626c1be6949"

#Set the context to the subscription Id where managed disk exists
az account set --subscription $sourceSubscriptionId

#Get the managed disk Id 
managedDiskId=$(az disk show --name $managedDiskName --resource-group $sourceResourceGroupName --query "id" -o tsv)

#If managedDiskId is blank then it means that managed disk does not exist.
echo 'source managed disk Id is: ' $managedDiskId

#Provide the subscription Id of the subscription where managed disk will be copied to
targetSubscriptionId="9ef8a15c-15a2-4ef1-a19b-e31876ab177c"

#Name of the resource group where managed disk will be copied to
targetResourceGroupName="myResourceGroup"

#Set the context to the subscription Id where managed disk will be copied to
az account set --subscription $targetSubscriptionId

#Copy managed disk to different subscription using managed disk Id
az disk create --resource-group $targetResourceGroupName --name $managedDiskName --source $managedDiskId --location chinaeast2