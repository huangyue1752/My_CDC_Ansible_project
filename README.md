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

# check if connection to eventhub is successful(run in in vm)
sudo systemctl status cdc-bridge
# check if evenyhub consumer is receiving message
docker exec -it kafka_demo bash -lc \
'kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group bridge-to-eventhub'




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
"ansible-playbook -i hosts.yml deploy.yml --ask-pass --ask-become-pass --ask-vault-pass
s"

# Final Verification on the VM
cat /home/datastream/my_cdc_project/debezium-connector-config.json


# question to clear after adding the bridge to connect kafka to event hub
1️⃣ Is kafka-consumer-groups the same as a topic?
A topic is where messages are stored.
A consumer group is who reads from the topic.
Example:bridge-to-eventhub

in debezium-mysql-source-connector-demo.yml
ports:
  - "29092:29092"
  That means:
Left side = host port
Right side = container port
So:Host:29092 → Container:29092
If that mapping does not exist,
your VM cannot talk to Kafka.

🔹 9092 = INTERNAL Docker Network
Used when:
Container talks to container
Kafka container talks to Debezium
You exec inside container

🔹 29092 = EXTERNAL Host Port( because bridge_kafka_to_eventhub.py was created in the VM not in the container, so its the communication between vm(py file) and container(kafka))
Used when:
VM host talks to container
Your systemd bridge runs outside Docker
Anything outside container connects

Docker Network
------------------------------------------------
|                                              |
|  Debezium ----> kafka:9092 <---- zookeeper  |
|                                              |
------------------------------------------------
               ↑
               |
VM host connects via 192.168.65.5:29092
               |
         systemd bridge


🔵 1️⃣ KAFKA_LISTENERS
KAFKA_LISTENERS:
  INTERNAL://0.0.0.0:9092,
  EXTERNAL://0.0.0.0:29092
This means:
"Kafka, open these ports and listen for connections."
Think of it like:
Opening doors on a building.
What does 0.0.0.0 mean?
It means:
Listen on ALL network interfaces.
So Kafka is saying:
I will accept connections on port 9092
I will accept connections on port 29092
But this does NOT tell clients how to reach Kafka.
It only tells Kafka what ports to open

🟢 2️⃣ KAFKA_ADVERTISED_LISTENERS
KAFKA_ADVERTISED_LISTENERS:
  INTERNAL://kafka:9092,
  EXTERNAL://192.168.65.5:29092

This means:
"When clients ask for cluster metadata, tell them to use THESE addresses."
This is not about opening ports.
This is about what Kafka tells clients to use.




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

 # ! WHEN YOU ignoregit you need to run blow code and verify
 git rm --cached group_vars/all.yml
 git ls-files | grep all.yml
 (you need to make you the ignroed file cannot be seen)

 # check what's been committed
 git ls-files | grep .gitignore
 git show HEAD:.gitignore

# when your remote dev branch has commits you don’t have locally, so Git won’t let you push (to avoid overwriting).
git pull --rebase origin dev
git push origin dev

✅ Option 1 — Completely Reset dev to Match main (Most Common)
Step 1 — Make sure main is updated
git checkout main
git pull origin main
Step 2 — Go back to dev
git checkout dev
git reset --hard main

how do I check the latest version of main
✅ 1️⃣ Check Your Local main Version
git checkout main
git log -1
✅ 2️⃣ Check Remote main (Very Important)
git fetch origin
git log origin/main -1
