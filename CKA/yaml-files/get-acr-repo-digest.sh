#!/bin/bash

#the azure container registry name
registry_name="xhacrtest"

repository_list=$(az acr repository list --name $registry_name --output tsv | tr '\n' ' ')

for repository_name in $repository_list
do
  echo "Repository: $repository_name"
  #az acr manifest list-metadata -r $registry_name -n $repository_name --query "[].{digest:digest}" --output table
  az acr repository show-manifests --name $registry_name --repository $repository_name --query "[].{digest:digest, tags:tags}" --output table
done