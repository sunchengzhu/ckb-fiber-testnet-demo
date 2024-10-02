gi t# ckb-fiber-testnet-demo

- Compilation project
- Configure three fiber nodes
- Create a 10USD channel for node1(10USD) -> node2(0USD)
- Create a 10USD channel for node2(10USD) -> node3(0USD)
- Node 1 transfer 1USD to node 3 via the channel use ln-address
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

### Configure two fiber nodes

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
#  https://testnet0815.stablepp.xyz/stablecoin
```

node2

```
cd tmp
mkdir -p testnet-fnn/node2/ckb
cp ../config/testnet/config.yml testnet-fnn/node2
vi testnet-fnn/node2/config.yml 
./ckb-cli account new  
./ckb-cli account export  --lock-arg 0x30c54eb6b4ddb48b9335420abe0813e3e67f46e1 --extended-privkey-path exported-key2
head -n 1 ./ckb/exported-key2 > testnet-fnn/node2/ckb/key
ckb-cli util key-info  --privkey-path testnet-fnn/node2/ckb/key
```

node3

```
cd tmp
mkdir -p testnet-fnn/node3/ckb
cp ../config/testnet/config.yml testnet-fnn/node3
vi testnet-fnn/node3/config.yml 
./ckb-cli account new  
./ckb-cli account export  --lock-arg 0x6a22298591942ba030594dd46a396adec1ecd913 --extended-privkey-path exported-key3
head -n 1 ./ckb/exported-key3 > testnet-fnn/node3/ckb/key
ckb-cli util key-info  --privkey-path testnet-fnn/node3/ckb/key
```

start nodes

```shell

RUST_LOG=info ./fnn -c testnet-fnn/node1/config.yml -d testnet-fnn/node1

RUST_LOG=info ./fnn -c testnet-fnn/node2/config.yml -d testnet-fnn/node2

RUST_LOG=info ./fnn -c testnet-fnn/node3/config.yml -d testnet-fnn/node3

```



### Create a 2000CKB channel for node1 and node2

Connect node 1 and node 2

```shell

curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "connect_peer",
    "params": [
        {
            "address": "/ip4/127.0.0.1/tcp/8230/p2p/QmaQSn11jsAXWLhjHtZ9EVbauD88sCmYzty3GmYcoVWP2j"
        }
    ]
}'
```



Create a 10USD channel for node1(10USD) -> node2(0USD)


```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "open_channel",
    "params": [
        {
            "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw",
            "funding_amount": "0x5f5e100",
            "public": true,
            "funding_udt_type_script": {
                "code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a",
                "hash_type": "type",
                "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"
            }
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"temporary_channel_id": "0xbf1b507e730b08024180ed9cb5bb3655606d3a89e94476033cf34d206d352751"}, "id": 42}

```

Call list_channels and wait until state equals CHANNEL_READY.


```shell
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
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x2329a1ced09d0c9eff46068ac939596bb657a984b1d6385db563f2de837b8879", "peer_id": "QmaQSn11jsAXWLhjHtZ9EVbauD88sCmYzty3GmYcoVWP2j", "state": {"state_name": "NEGOTIATING_FUNDING", "state_flags": "OUR_INIT_SENT | THEIR_INIT_SENT"}, "local_balance": "0x2d1f615200", "sent_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x620a0b7b1676b"}]}, "id": 42}

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
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0x2329a1ced09d0c9eff46068ac939596bb657a984b1d6385db563f2de837b8879", "peer_id": "QmaQSn11jsAXWLhjHtZ9EVbauD88sCmYzty3GmYcoVWP2j", "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x2d1f615200", "sent_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x620a0b7b1676b"}]}, "id": 42}

```

Create a 10USD channel for node2(10USD) -> node3(0USD)

```shell
curl --location 'http://127.0.0.1:8230' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "open_channel",
    "params": [
        {
            "peer_id": "QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX",
            "funding_amount": "0x3b9aca00",
            "public": true,
            "funding_udt_type_script": {
                "code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a",
                "hash_type": "type",
                "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"
            }
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"temporary_channel_id": "0xb2e489b05ef42fcde33950ddf24bc55f7cf990e38eef46e020c5b80cd0b159fb"}, "id": 42}
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
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0xa239009760d9abacf3f1b11947df7bb0e40fc66768864e499ca6f9a9aa567342", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": {"code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a", "hash_type": "type", "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x3b9aca00", "offered_tlc_balance": "0x0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378376b846f"}]}, "id": 42}


```

### Node 1 transfers 1USD to node 3 via the channel

Node 3 generates a 10 USD invoice

```shell
curl --location 'http://127.0.0.1:8232' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "new_invoice",
    "params": [
        {
            "amount": "0x5f5e100",
            "currency": "Fibb",
            "description": "test invoice generated by node2",
            "expiry": "0xe10",
            "final_cltv": "0x28",
            "payment_preimage": "0xd07d669c758a5c5c0c220e36652011f279ea4bbebf31fa4bfed0d2e84cbfe9de",
            "hash_algorithm": "sha256",
            "udt_type_script": {
                "code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a",
                "hash_type": "type",
                "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"
            }
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"invoice_address": "fibb1000000001qgxlna32kkmczxzat8almqgp23lgsdfjzja4wp7n5mxsld70njckjxdrp80f59yqln8xalfh7stu653qs30mrk720ve9et7fdrat97uvdmj783j7ruw872t60v7pe6hfjutenr4njadjgacmfen0l46au9wfpe5sg5d6dpqmvjlaf88equldr8zlpum8v2twgrsedjfkt8ejq2tdarqmac57rx4mkrxashe6nm0xu59rzaqm9dxv3vzc9jc6890ccfwqlucswsn62p3yafgd7gep5x2p8uda0kxap40mglarrrm0cjcuaq48q07s9qg33kuhudnttfhpg5vy5sndgtk6z9lvtcgquyrv0tk9gykd5r8t8yxh8d40z96ce2uwrcmscakrxhtl2eu7k3ltusk77sy5", "invoice": {"currency": "Fibb", "amount": "0x5f5e100", "signature": null, "data": {"timestamp": "0x1924bd772e4", "payment_hash": "0x8f804fca8b611c43e05c82f23141faee236b6e0b7364c2f8b1b569e4f800b04a", "attrs": [{"Description": "test invoice generated by node2"}, {"ExpiryTime": {"secs": 3600, "nanos": 0}}, {"FinalHtlcMinimumCltvExpiry": 40}, {"UdtScript": "0x550000001000000030000000310000001142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a0120000000878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, {"HashAlgorithm": "sha256"}, {"PayeePublicKey": "03c5627399cd37db17f7281926f7bc514d4687b4f541d4c52643d9d42c9a77ba68"}]}}}, "id": 42}
```
- invoice_address: "fibb1000000001qgxlna32kkmczxzat8almqgp23lgsdfjzja4wp7n5mxsld70njckjxdrp80f59yqln8xalfh7stu653qs30mrk720ve9et7fdrat97uvdmj783j7ruw872t60v7pe6hfjutenr4njadjgacmfen0l46au9wfpe5sg5d6dpqmvjlaf88equldr8zlpum8v2twgrsedjfkt8ejq2tdarqmac57rx4mkrxashe6nm0xu59rzaqm9dxv3vzc9jc6890ccfwqlucswsn62p3yafgd7gep5x2p8uda0kxap40mglarrrm0cjcuaq48q07s9qg33kuhudnttfhpg5vy5sndgtk6z9lvtcgquyrv0tk9gykd5r8t8yxh8d40z96ce2uwrcmscakrxhtl2eu7k3ltusk77sy5"

Node 1 sends a payment

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "send_payment",
    "params": [
        {
            "invoice": "fibb1000000001qgxlna32kkmczxzat8almqgp23lgsdfjzja4wp7n5mxsld70njckjxdrp80f59yqln8xalfh7stu653qs30mrk720ve9et7fdrat97uvdmj783j7ruw872t60v7pe6hfjutenr4njadjgacmfen0l46au9wfpe5sg5d6dpqmvjlaf88equldr8zlpum8v2twgrsedjfkt8ejq2tdarqmac57rx4mkrxashe6nm0xu59rzaqm9dxv3vzc9jc6890ccfwqlucswsn62p3yafgd7gep5x2p8uda0kxap40mglarrrm0cjcuaq48q07s9qg33kuhudnttfhpg5vy5sndgtk6z9lvtcgquyrv0tk9gykd5r8t8yxh8d40z96ce2uwrcmscakrxhtl2eu7k3ltusk77sy5"
        }
    ]
}'
{"jsonrpc": "2.0", "result": {"payment_hash": "0x8f804fca8b611c43e05c82f23141faee236b6e0b7364c2f8b1b569e4f800b04a"}, "id": 42}

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
{"jsonrpc": "2.0", "result": {"channels": [{"channel_id": "0xa239009760d9abacf3f1b11947df7bb0e40fc66768864e499ca6f9a9aa567342", "peer_id": "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw", "funding_udt_type_script": {"code_hash": "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a", "hash_type": "type", "args": "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"}, "state": {"state_name": "CHANNEL_READY", "state_flags": []}, "local_balance": "0x3b9aca00", "offered_tlc_balance": "0x5f767a0", "remote_balance": "0x0", "received_tlc_balance": "0x0", "created_at": "0x62378376b846f"}]}, "id": 42}
```


### close channel

```shell
curl --location 'http://127.0.0.1:8227' --header 'Content-Type: application/json' --data '{
    "id": 42,
    "jsonrpc": "2.0",
    "method": "shutdown_channel",
    "params": [
        {
            "channel_id": "0x2329a1ced09d0c9eff46068ac939596bb657a984b1d6385db563f2de837b8879",
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": "0xe266ef916081dbf19e13f1a485bbbc2206a01dc1"
            },
            "fee_rate": "0x3FC"
        }
    ]
}'
response:
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


