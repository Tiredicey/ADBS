#!/usr/bin/env bash
# Download MongoDB 8.0.4 + mongosh 2.3.8 into ~/bin and start a local server.
set -e
mkdir -p ~/work/mdb ~/bin && cd ~/work
[ -x ~/bin/mongod ] || { curl -sSL -o mongod.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian12-8.0.4.tgz
  tar -xzf mongod.tgz --wildcards '*/bin/mongod' && cp */bin/mongod ~/bin/ && rm -rf mongodb-linux-* mongod.tgz; }
[ -x ~/bin/mongosh ] || { curl -sSL -o mongosh.tgz https://downloads.mongodb.com/compass/mongosh-2.3.8-linux-x64.tgz
  tar -xzf mongosh.tgz && cp mongosh-2.3.8-linux-x64/bin/* ~/bin/ && rm -rf mongosh-2.3.8-linux-x64 mongosh.tgz; }
pgrep -x mongod >/dev/null || ~/bin/mongod --dbpath ~/work/mdb --bind_ip 127.0.0.1 --wiredTigerCacheSizeGB 0.25 --fork --logpath ~/work/mongod.log
echo MONGO_READY
