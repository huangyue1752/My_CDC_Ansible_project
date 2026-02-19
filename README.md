# this file include debezium project and Ansible deployment
1.debezium project
# My project steps
Before the project you need to install docker and MySQL(9.1.0-arm64). Please be careful about the versions(it makes big difference)

# how to check mySQL version
run "ls /usr" then "open /usr" in your terminal 
click "local" folder and then right click on mysql-9.1.0-macos14-arm64 to select Terminal tap at folder
Create my.cnf file in
/usr/local/mysql-8.0.11-macos10.13-x86_64/my.cnf
"sudo touch my.cnf"
put password
"sudo vi my.cnf"
click "i" to switch to insert mode
paste:
[mysqld]
server-id = 223344
log_bin = mysql-bin
binlog_format = row
binlog_row_image = FULL
gtid_mode = ON
enforce-gtid-consistency = TRUE
require_secure_transport=OFF

esc then ":wq" to save it
"./bin/mysql -u root -p"

"CREATE USER 'devezium'@'%' IDENTIFIED BY '******'

"GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%'"

"FLUSH PRIVILEGES"

Stop MySQL server and then restard( you need to do it in the setting of macbook)

Thenn you need to create the two files :debezium-connector-config.json.j2 and debezium-mysql-source-connector-demo.yml
(Please note you need to beware the image version and the configuration wording version, it works for the current version but you might need to change it later if you have new version)

"docker compose -f devezium-mysql-source-connector-demo.yml up -d" to deploy the images

go back to mysql terminal
"CREATE SCHEMA school;"

"use school;"

"create table students (id integer, name varchar(100));"

"insert into students values (1,'Tyler');

switch to the other terminal 

"cat debezium-connector-config.json" checking the content of the file
"vif debezium-connector-config.json" edit the cotent of the file
"ggDg" delete

# seding the json config file to speak with Kafka connect rest api
"curl -X POST -H "Content-Type:application/json" --data @debezium-connector-config.json http://localhost:8083/connectors"

then you can use the code below to check the connector
curl http://localhost:8083/connectors
or delete the connector 
curl -X DELETE http://localhost:8083/connectors/mysql-connector-v4


# open kafka demo to check if the topics are generated
1."docker exec -it kafka_demo bash"
2."cd /usr/bin/"
# list topics (you need to make sure 1,2 is running before this)
"./kafka-topics --bootstrap-server localhost:9092 --list"
# run consumer (you need to make sure 1,2 is running before this)
"./kafka-console-consumer --bootstrap-server localhost:9092 --topic mysql9_full.school.students --from-beginning"

# codes you need to debug incase it does not work
"docker logs debezium_demo --tail 100"


2.Ansible deployment
# First you need to install VM in your Macbook
check the link below for how to install VM ubuntu in your macbook M1(be careful the version) with UTM
https://www.youtube.com/watch?v=1PL-0-5BNXs

# prepare for the keys. !!!
"nano ~/.zshrc

# 2. Ensure these are on their own lines at the bottom (NO 'source' at the end)
export MAC_IP="your_mac_ip"
export MYSQL_PW="your_password"
export VM_IP="your_vm_ip"

# save and verify
"source ~/.zshrc"
"echo $MYSQL_PW

# Prepare the Template (debezium-connector-config.json.j2)

# The Ansible Playbook (deploy.yml)

# hosts.yml
# Execute this from your Mac terminal:
"ansible-playbook -i hosts.yml deploy.yml --ask-pass --ask-become-pass"

# Final Verification on the VM
cat /home/datastream/my_cdc_project/debezium-connector-config.json

# how to git
git init
git add .
nano .gitignore # if needed
git commit -m "Initial commit: Ansible automation for CDC with secure templates"
git push origin main

# create a new branch
git checkout -b dev

# check which branch 
 git branch