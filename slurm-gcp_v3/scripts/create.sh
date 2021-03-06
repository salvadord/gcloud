#!/bin/bash

# Takes the deployment name as the first arg, the deployment manager YAML as the second arg.

if [ -r $2 ] && [ $1 ]; then
	gcloud deployment-manager deployments create $1 --config $2
else
	echo "Provide a YAML!"
	exit 1
fi
