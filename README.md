# ckb-fiber-testnet-demo

- Compilation project
- Configure three fiber nodes
- Create a 1000 CKB channel for node1(1000ckb) -> node2(0)
- Create a 1000 CKB channel for node2(1000ckb) -> node3(0)
- Node 1 transfers 100ckb to node 3 via the channel
- Close Channel



###  compile project

```
git clone https://github.com/nervosnetwork/fiber.git
cd fiber
cargo build --release

# https://github.com/nervosnetwork/ckb/releases/tag/v0.117.0
wget https://github.com/nervosnetwork/ckb/releases/download/v0.117.0/ckb_v0.117.0_aarch64-apple-darwin-portable.zip

unzip ckb_v0.117.0_aarch64-apple-darwin-portable.zip
mkdir tmp 
cp target/release/fnn tmp
cp ckb_v0.117.0_aarch64-apple-darwin-portable/ckb-cli tmp
```

### Configure 3 fiber nodes

node1


```
cd tmp
mkdir -p testnet-fnn/node1/ckb
cp ../config/testnet/config.yml testnet-fnn/node1
./ckb-cli account new  
./ckb-cli account export  --lock-arg 0x30c54eb6b4ddb48b9335420abe0813e3e67f46e1 --extended-privkey-path exported-key
head -n 1 ./exported-key > testnet-fnn/node1/ckb/key
ckb-cli util key-info  --privkey-path testnet-fnn/node1/ckb/key
# https://faucet.nervos.org/

```

node2

```
cd tmp
mkdir -p testnet-fnn/node2/ckb
cp ../config/testnet/config.yml testnet-fnn/node2
# Set ports: fiber.listening_addr to 8229, rpc.listening_addr to 8230
vi testnet-fnn/node2/config.yml 
./ckb-cli account new  
./ckb-cli account export  --lock-arg 0x30c54eb6b4ddb48b9335420abe0813e3e67f46e1 --extended-privkey-path exported-key2
head -n 1 exported-key2 > testnet-fnn/node2/ckb/key
ckb-cli util key-info  --privkey-path testnet-fnn/node2/ckb/key
```

node3

```
cd tmp
mkdir -p testnet-fnn/node3/ckb
cp ../config/testnet/config.yml testnet-fnn/node3
# Set ports: fiber.listening_addr to 8231, rpc.listening_addr to 8232
vi testnet-fnn/node3/config.yml 
./ckb-cli account new  
./ckb-cli account export  --lock-arg 0x6a22298591942ba030594dd46a396adec1ecd913 --extended-privkey-path exported-key3
head -n 1 exported-key3 > testnet-fnn/node3/ckb/key
ckb-cli util key-info  --privkey-path testnet-fnn/node3/ckb/key
```

start nodes

```shell

RUST_LOG=info ./fnn -c testnet-fnn/node1/config.yml -d testnet-fnn/node1

RUST_LOG=info ./fnn -c testnet-fnn/node2/config.yml -d testnet-fnn/node2

RUST_LOG=debug ./fnn -c testnet-fnn/node3/config.yml -d testnet-fnn/node3

```


### Create a 1000 CKB channel for node1(1000ckb) -> node2(0)

Connect node 1 and node 2

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "connect_peer",
    "params": [
        {
            "address": "/ip4/127.0.0.1/tcp/8229/p2p/QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"
        }
    ]
}'
{"jsonrpc": "2.0", "result": null, "id": 42}
```

Connect node 2 and node 3
```shell
curl --location 'http://127.0.0.1:8230' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "connect_peer",
    "params": [
        {
            "address": "/ip4/127.0.0.1/tcp/8231/p2p/QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX"
        }
    ]
}'
{"jsonrpc": "2.0", "result": null, "id": 42}
```




open Channel

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "open_channel",
    "params": [
        {
            "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw",
            "funding_amount": "0x174876e800",
            "public": true
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"temporary_channel_id": "0x284a31f9591e79669d1b4118fe3f5da5050a9a746d83e8a65d02605d6f22d16c"}, "id": 42}

```

Call list_channels and wait until state equals CHANNEL_READY.


```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "list_channels",
    "params": [
        {
            "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x60801abda61fc16597efdc181b132a28ed83e90e5e387763f1e7f6270e255bf8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": null, "state": {"state_name": "AWAITING_CHANNEL_READY", "state_flags": "OUR_CHANNEL_READY"}, "local_balance": "0x15d6ea6a00", "offered_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378f8a6a46a"}, {"channel_id": "0x11c3e6699b13989920203feb6cf2679a3d575b501977411f37a7c70b907674b8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": {"code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a", "hash_type": "type", "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, "state": {"state_name": "SHUTTING_DOWN", "state_flags": "OUR_SHUTDOWN_SENT | THEIR_SHUTDOWN_SENT"}, "local_balance": "0x3b9aca00", "offered_tlc_balance": "0xbeecf9f", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378cda3888e"}]}, "id": 42}

curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "list_channels",
    "params": [
        {
            "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x60801abda61fc16597efdc181b132a28ed83e90e5e387763f1e7f6270e255bf8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": null, "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x15d6ea6a00", "offered_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378f8a6a46a"}, {"channel_id": "0x11c3e6699b13989920203feb6cf2679a3d575b501977411f37a7c70b907674b8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": {"code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a", "hash_type": "type", "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, "state": {"state_name": "SHUTTING_DOWN", "state_flags": "OUR_SHUTDOWN_SENT | THEIR_SHUTDOWN_SENT"}, "local_balance": "0x3b9aca00", "offered_tlc_balance": "0xbeecf9f", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378cda3888e"}]}, "id": 42}

```

### Create a 1000 CKB channel for node2(1000ckb) -> node3(0)

open channel
```shell
curl --location 'http://127.0.0.1:8230' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "open_channel",
    "params": [
        {
            "peer_id": "QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX",
            "funding_amount": "0x174876e800",
            "public": true
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"temporary_channel_id": "0xf31c078fab3ba282fd30298d43e50ea78c36da5fb82b6655135ffd901f249927"}, "id": 42}
```

Call list_channels and wait until state equals CHANNEL_READY.

```shell
curl --location 'http://127.0.0.1:8230' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "list_channels",
    "params": [
        {
            "peer_id": "QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX"
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x2ed137edf63a7c12b42cf6b36e858e69fcf4277e6c9950d01e4c9693ca7df53b", "peer_id": "QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX", "funding_udt_type_script": null, "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x15d6ea6a00", "offered_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378ffe02e30"}]}, "id": 42}

```

### Node 1 transfers 100ckb to node 3 via the channel

Node 3 generates a 100 CKB invoice

```shell
curl --location 'http://127.0.0.1:8232' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "new_invoice",
    "params": [
        {
            "amount": "0x2540be400",
            "currency": "Fibt",
            "description": "test invoice generated by node3",
            "expiry": "0xe10",
            "final_cltv": "0x28",
            "payment_preimage": "0x26b069707aec100fd7153f26abe2bea9e32ed0a6ec1b7e3dcd47aa0e684a146f",
            "hash_algorithm": "sha256"
        }
    ]
}'
{"jsonrpc":"2.0","result":{"invoice_address":"fibt100000000001qms3acfz8kxgfw0pnm6vk29yj7x6zkvqgdefxcr03p9tecaw6gslxq64f4q03gsr5lv3zy4qwvhpzadqfwe5j3mtlm72hllrvcq3rukxs0hwfc6y6g2949uef7ukmw64ajsq2y8sxxn5s6ha2dm9qwuqrgxc44ruv50fv8jnc0t4rwkfdgm8w2rkvp7werh2t7xqzzr96f5k5lxeltywjtxdpjse37w9cl3qmgrrzn5nh90vpvlqqmphf54jnylp9dft6xjzq45djclz8xx3","invoice":{"currency":"Fibb","amount":"0x2540be400","signature":null,"data":{"timestamp":"0x1924c10da27","payment_hash":"0xd1825993e014d7761b0e2ada735f4f632a3cd33e269364d3711370b47aeb7bfc","attrs":[{"Description":"test invoice generated by node3"},{"ExpiryTime":{"secs":3600,"nanos":0}},{"FinalHtlcMinimumCltvExpiry":40},{"HashAlgorithm":"sha256"},{"PayeePublicKey":"03c5627399cd37db17f7281926f7bc514d4687b4f541d4c52643d9d42c9a77ba68"}]}}},"id":42}
```


Node 1 sends a payment

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "send_payment",
    "params": [
        {
            "invoice": "fibt100000000001qms3acfz8kxgfw0pnm6vk29yj7x6zkvqgdefxcr03p9tecaw6gslxq64f4q03gsr5lv3zy4qwvhpzadqfwe5j3mtlm72hllrvcq3rukxs0hwfc6y6g2949uef7ukmw64ajsq2y8sxxn5s6ha2dm9qwuqrgxc44ruv50fv8jnc0t4rwkfdgm8w2rkvp7werh2t7xqzzr96f5k5lxeltywjtxdpjse37w9cl3qmgrrzn5nh90vpvlqqmphf54jnylp9dft6xjzq45djclz8xx3"
        }
    ]
}'
{"jsonrpc":"2.0","result":{"payment_hash":"0xd1825993e014d7761b0e2ada735f4f632a3cd33e269364d3711370b47aeb7bfc"},"id":42}
```

Check balance

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "list_channels",
    "params": [
        {
            "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x60801abda61fc16597efdc181b132a28ed83e90e5e387763f1e7f6270e255bf8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": null, "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x138245ef80", "offered_tlc_balance": "0x0", "remote_balance": "0x254a47a80", "received_tlc_balance": "0x0", "created_at": "0x62378f8a6a46a"}, {"channel_id": "0x11c3e6699b13989920203feb6cf2679a3d575b501977411f37a7c70b907674b8", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": {"code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a", "hash_type": "type", "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, "state": {"state_name": "SHUTTING_DOWN", "state_flags": "OUR_SHUTDOWN_SENT | THEIR_SHUTDOWN_SENT"}, "local_balance": "0x3b9aca00", "offered_tlc_balance": "0xbeecf9f", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378cda3888e"}]}, "id": 42}
```


### close channel

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "shutdown_channel",
    "params": [
        {
            "channel_id": "0x60801abda61fc16597efdc181b132a28ed83e90e5e387763f1e7f6270e255bf8",
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": "0x4d4ae843f62f05bf1ac601b3dbd43b5b4f9a006a"
            },
            "fee_rate": "0x3FC"
        }
    ]
}'
{"jsonrpc": "2.0", "result": null, "id": 42}
curl --location 'http://127.0.0.1:8230' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "shutdown_channel",
    "params": [
        {
            "channel_id": "0x2ed137edf63a7c12b42cf6b36e858e69fcf4277e6c9950d01e4c9693ca7df53b",
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": "0xf3afdc1c46caade6bf503b4076855d1dc5a8f735"
            },
            "fee_rate": "0x3FC"
        }
    ]
}'
{"jsonrpc": "2.0", "result": null, "id": 42}

```



check channel 

```
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "list_channels",
    "params": [
        {
            "peer_id": "QmaQSn11jsAXWLhjHtZ9EVbauD88sCmYzty3GmYcoVWP2j"
        }
    ]
}'
response:
{"jsonrpc": "2.0", "result": {"channels": []}, "id": 42}
```


