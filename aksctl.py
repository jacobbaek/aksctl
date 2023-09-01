#!/usr/env/python
# https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/containerservice/azure-mgmt-containerservice
# https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/containerservice/manage_managed_clusters.py

from subprocess import Popen, PIPE
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
import argparse

def get_credentials(client, rgname, clustername):
    response = client.managed_clusters.list_cluster_admin_credentials(
        resource_group_name=rgname,
        resource_name=clustername,
    )
    print(response.kubeconfigs)

def aks_list(client):
    response = client.managed_clusters.list()
    akslst=[]
    i = 0

    for cluster in response:
        i = i + 1
        print("[" + str(i) + "] " + cluster.name + "(" + cluster.power_state.code + ") : running k8s " \
               + cluster.kubernetes_version + " cluster on " + cluster.location)
        splitinfo = str(cluster.id).split("/")
        akslst.append({"num":str(i), "rgname":splitinfo[4], "clustername":splitinfo[8]})
    return akslst

def aks_startandstop(client, rgname, clustername, op):
    if op == "start":
        res = client.managed_clusters.begin_start(
            resource_group_name=rgname,
            resource_name=clustername,
            polling_interval=1,
        )
    else:
        res = client.managed_clusters.begin_stop(
            resource_group_name=rgname,
            resource_name=clustername,
            polling_interval=1,
        )
    
# az account show --query id -o tsv
def get_subscription():
    proc = Popen(["az","account","show","--query","id","-o","tsv"], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    if str(err, "utf-8") != "":
        return None
    return str(out, "utf-8").rstrip()

def main():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('-g', '--getcredentials',
                    help='Get credentials for specific AKS cluster')
    parser.add_argument('-s', '--start',
                    help='Start specific AKS cluster')
    parser.add_argument('-p', '--stop',
                    help='Start specific AKS cluster')

    subid = get_subscription()
    if subid == None:
        print("Not found subscription ID")
        exit(1)

    client = ContainerServiceClient(
        credential=DefaultAzureCredential(),
        subscription_id=subid,
    )

    akslst = aks_list(client)

    selectnum = input(" >> press the number : ")
    selectcluster = akslst[int(selectnum)-1]

    aks_startandstop(client, selectcluster["rgname"], selectcluster["clustername"], "start")
    get_credentials(client, selectcluster["rgname"], selectcluster["clustername"])

if __name__ == "__main__":
    main()
