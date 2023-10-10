#!/bin/sh

# Entrypoint script which runs API and also enables SSH on Azure
# https://learn.microsoft.com/en-us/azure/app-service/configure-custom-container?tabs=debian&pivots=container-linux#enable-ssh

set -e
service ssh start
exec uvicorn main:app --host 0.0.0.0 --port 80
