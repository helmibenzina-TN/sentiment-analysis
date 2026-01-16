#!/bin/sh
set -e

# Replace ONLY the ${BACKEND_URL} variable in the template.
# This prevents envsubst from deleting standard Nginx variables like $host and $remote_addr.
envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the CMD (nginx)
exec "$@"
