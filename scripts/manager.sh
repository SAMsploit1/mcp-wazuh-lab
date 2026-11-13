#!/bin/sh
set -eu
# Restore the packaged defaults normally populated by the full image init.
cp /var/ossec/data_tmp/exclusion/var/ossec/etc/internal_options.conf /var/ossec/etc/internal_options.conf
chown root:wazuh /var/ossec/etc/internal_options.conf
chmod 640 /var/ossec/etc/internal_options.conf
cp -a /var/ossec/data_tmp/exclusion/var/ossec/etc/lists/. /var/ossec/etc/lists/
chown -R wazuh:wazuh /var/ossec/etc/lists
mkdir -p /var/ossec/queue/sockets
chown wazuh:wazuh /var/ossec/queue/sockets
/var/ossec/bin/wazuh-db
exec /var/ossec/bin/wazuh-analysisd -f
