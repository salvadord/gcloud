#!/bin/bash

function delete_instances() {
	step=50
	instances_list=("`gcloud compute instances list --format="value(NAME,ZONE)" 2>/dev/null | grep compute`")
	zone=`echo "${instances_list[@]}" | awk '{print $2}' | sort -u`
	
	echo "${instances_list[@]}" | grep -v -w "compute1" | grep -v -w "compute2" | awk '{print $1}' | xargs -n 1000 gcloud compute instances delete -q --zone=$zone
}

function main() {
	while [ -n "`gcloud compute instances list 2>/dev/null | grep compute | grep -v -w "compute1" | grep -v -w "compute2" | awk '{print $1}'`" ]; do
		delete_instances
	done
	
	if [ "$2" != "--instances" ]; then
		echo "Instance deletion complete."
		echo "Deleting firewall rules."
		sleep 15
		
		for i in `gcloud compute firewall-rules list 2>/dev/null | grep slurm-network | awk '{print $1}'`; do 
			gcloud compute firewall-rules delete $i -q &
		done
		while [ `gcloud compute firewall-rules list 2>/dev/null | grep -c slurm-network` -gt 0 ]; do sleep 5; done
		gcloud compute networks delete slurm-network -q
		sleep 10
		gcloud deployment-manager deployments delete $1 -q 
	fi
}

main $@
