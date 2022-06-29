#!/bin/bash

file_dir=$(dirname $0)
cd $file_dir

docker run --name some-mysql -v `pwd`/mysql_entrypoint:/docker-entrypoint-initdb.d/ -e MYSQL_ROOT_PASSWORD=mypw -d mysql 
