#!/bin/bash

header=$(cat << EOF
SHELL=/bin/bash 
PATH=/sbin:/bin:/usr/sbin:/usr/bin 
MAILTO=root HOME=/  
EOF
)

{ echo -e "${header}" && echo "" && cat ./cron.txt; } > /etc/cron.d/arbitrade