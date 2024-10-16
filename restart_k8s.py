from kubernetes import client, config 
import pandas as pd
from datetime import datetime

#Load Kubernetes configuration (assume access to kubeconfig)
config.load_kube_config()

#create Kubernetes API Client
v1 = client.CoreV1Api()

#Fetch all pods across all namespaces 
pods = v1.list_pod_for_all_namespaces(watch=False)

# List to hold pod restart information 
data = []

#Iterate through the pods and containers to gather restart counts
for pod in pods.items:
    namespace = pod.metadata.namespace
    pod_name = pod.metadata.name
    for container_status in pod.status.container_statuses or []:
        container_name = container_status.name 
        restart_count = container_status.restart_count
        if restart_count > 0:
            # Collect timestamp of the latest restart event 
            #restart_time = container_status.state.last_terminated.finished_at if container_status.state and container_status.state.last_terminated else None 
            restart_time = container_status.state._terminated.finished_at if container_status.state and container_status.state._terminated else None
            # Format the data for the Execel sheet
            data.append({
                "Namespace": namespace,
                "Pod Name": pod_name,
                "Container Name": container_name,
                "Restart Count": restart_count,
                "Last Restart Time": restart_time.strftime('%Y-%M-%D %H:%M:%S') if restart_time else "N/A"
            })

#Create a DataFrame and export to Excel 
df = pd.DataFrame(data)
output_filename ="container_restarts.xlsx"
df.to_excel(output_filename, index=False)
print(f"Data exported successfully to {output_filename}")
