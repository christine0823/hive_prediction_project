#!/bin/bash

if [ "$1" = "" ]; then
        echo "usage: sh firsh_label.sh IN_FILE"
        exit 0;
fi

dconf="q,d,d,d,q,d,q,d,d,d,d,d,d,q,q,q,q,q,d,d,d,q,q,q,q,q,q,q,q,q,q,q,q,q,q,q,q,d,d,d,q,q,q,q,d"
label="0,1,0,0,0,0,0,1,1,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0"
sed -i 1"i\\$label" $1
sed -i 1"i\\$dconf" $1

sed -i "s/-Xmx//g" $1
sed -i "s/m//g" $1
