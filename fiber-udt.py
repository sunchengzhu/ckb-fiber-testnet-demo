import random
import time

import requests

import json

NODE1_RPC_URL = "http://127.0.0.1:8227"
NODE1_PEERID = "QmY8dEogQ4GK2KwZLmrtnJLULAuWuE8yPDqzegMjD7LmM7"
NODE1_ADDR = "/ip4/127.0.0.1/tcp/8228/p2p/QmY8dEogQ4GK2KwZLmrtnJLULAuWuE8yPDqzegMjD7LmM7"
NODE1_WALLET_ARG = "0x4d4ae843f62f05bf1ac601b3dbd43b5b4f9a006a"

NODE2_RPC_URL = "http://127.0.0.1:8230"
NODE2_PEERID = "QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"
NODE2_ADDR = "/ip4/127.0.0.1/tcp/8229/p2p/QmS8y8sAoF7DH89st7fquUVW9Y1W3cgcnPgWjPe6tcm1dw"

NODE2_WALLET_ARG = "0xf3afdc1c46caade6bf503b4076855d1dc5a8f735"

NODE3_RPC_URL = "http://127.0.0.1:8232"
NODE3_PEERID = "QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX"
NODE3_ADDR = "/ip4/127.0.0.1/tcp/8231/p2p/QmZP1m2KK59TB5RBe6YDG1MAnA4TFxUPPojqcCH8Edt1CX"

NODE3_WALLET_ARG = "0x6a22298591942ba030594dd46a396adec1ecd913"

RUSD_TYPE_CODE_HASH = "0x1142755a044bf2ee358cba9f2da187ce928c91cd4dc8692ded0337efa677d21a"
RUSD_HASH_TYPE = "type"
RUSD_ARGS = "0x878fcc6f1f08d48e87bb1c3b3d5083f23f8a39c5d5c764f253b55b998526439b"

HASH_ALGORITHM = "sha256"


# "funding_udt_type_script": {
#             "code_hash": "{{UDT_CODE_HASH}}",
#             "hash_type": "data1",
#             "args": "0x32e555f3ff8e135cece1351a6a2971518392c1e30375c1e006ad0ce8eac0794a"
#           }


class FiberRPCClient:
    def __init__(self, url):
        self.url = url

    def send_btc(self, btc_pay_req):
        return self.call("send_btc", [btc_pay_req])

    def open_channel(self, param):
        return self.call("open_channel", [param])

    def list_channels(self, param):
        return self.call("list_channels", [param])

    def accept_channel(self, param):
        return self.call("accept_channel", [param])

    def add_tlc(self, param):
        return self.call("add_tlc", [param])

    def remove_tlc(self, param):
        return self.call("remove_tlc", [param])

    def shutdown_channel(self, param):
        return self.call("shutdown_channel", [param])

    def new_invoice(self, param):
        return self.call("new_invoice", [param])

    def parse_invoice(self, param):
        return self.call("parse_invoice", [param])

    def connect_peer(self, param):
        return self.call("connect_peer", [param])

    def disconnect_peer(self, param):
        return self.call("disconnect_peer", [param])

    def send_payment(self, param):
        return self.call("send_payment", [param])

    def call(self, method, params):
        headers = {"content-type": "application/json"}
        data = {"id": 42, "jsonrpc": "2.0", "method": method, "params": params}
        print(
            "curl --location '{url}' --header 'Content-Type: application/json' --data '{data}'".format(
                url=self.url, data=json.dumps(data, indent=4)
            )
        )
        for i in range(100):
            try:
                response = requests.post(
                    self.url, data=json.dumps(data), headers=headers
                ).json()
                print("response:\n{response}".format(response=json.dumps(response)))
                if "error" in response.keys():
                    error_message = response["error"].get("message", "Unknown error")
                    raise Exception(f"Error: {error_message}")

                return response.get("result", None)
            except requests.exceptions.ConnectionError as e:
                print(e)
                print("request too quickly, wait 2s")
                time.sleep(2)
                continue
        raise Exception("request time out")


def generate_random_preimage():
    hash_str = '0x'
    for _ in range(64):
        hash_str += hex(random.randint(0, 15))[2:]
    return hash_str


def wait_for_channel_state(client, peer_id, expected_state, timeout=120):
    """Wait for a channel to reach a specific state."""
    for _ in range(timeout):
        channels = client.list_channels({"peer_id": peer_id})
        if channels['channels'][0]['state']['state_name'] == expected_state:
            print(f"Channel reached expected state: {expected_state}")
            return channels['channels'][0]['channel_id']
        print(
            f"Waiting for channel state: {expected_state}, current state: {channels['channels'][0]['state']['state_name']}")
        time.sleep(1)
    raise TimeoutError(f"Channel did not reach state {expected_state} within timeout period.")


def wait_for_channel_removal(fiberClient1, NODE_PEERID, timeout=120):
    """Waits for a channel to be removed between the given peer IDs.

    Args:
        fiberClient1 (FiberClient): The FiberClient instance.
        NODE_PEERID (str): The peer ID of the other node.
        timeout (int, optional): The maximum number of seconds to wait. Defaults to 120.

    Returns:
        bool: True if the channel was removed successfully, False otherwise.
    """

    start_time = time.time()
    channels = fiberClient1.list_channels({"peer_id": NODE_PEERID})
    channels_length = len(channels['channels'])
    while time.time() - start_time < timeout:
        channels = fiberClient1.list_channels({"peer_id": NODE_PEERID})
        if len(channels['channels']) == 0:
            return True
        if len(channels['channels']) == channels_length - 1:
            return True
        print(
            f"channel id:{channels['channels'][0]['channel_id']}, state:{channels['channels'][0]['state']['state_name']}, wait channel remove")
        time.sleep(1)

    raise TimeoutError("Channel removal timed out")


if __name__ == '__main__':
    fiberClient1 = FiberRPCClient(NODE1_RPC_URL)
    fiberClient2 = FiberRPCClient(NODE2_RPC_URL)
    fiberClient3 = FiberRPCClient(NODE3_RPC_URL)
    # connected node1 and node2
    fiberClient1.connect_peer({"address": NODE2_ADDR})
    fiberClient2.connect_peer({"address": NODE3_ADDR})

    time.sleep(3)

    # open channel node1 < - > node2  10rusd
    temporary_channel_id = fiberClient1.open_channel({
        "peer_id": NODE2_PEERID,
        "funding_amount": hex(10 * 100000000),
        "public": True,
        # "tlc_fee_proportional_millionths": "0x4B0",
        "funding_udt_type_script": {
            "code_hash": RUSD_TYPE_CODE_HASH,
            "hash_type": RUSD_HASH_TYPE,
            "args": RUSD_ARGS
        }
    })
    time.sleep(15)
    #     fiberClient2.accept_channel({
    #         "temporary_channel_id": temporary_channel_id['temporary_channel_id'],
    #         "funding_amount":  '0x0',
    #     })
    time.sleep(5)
    # wait channel open successful : channel statue: wait
    wait_for_channel_state(fiberClient1, NODE2_PEERID, "CHANNEL_READY", 120)
    channels = fiberClient1.list_channels({"peer_id": NODE2_PEERID})
    N1N2_CHANNEL_ID = channels['channels'][0]['channel_id']

    # open channel node2 < - > node3  10 rusd
    temporary_channel_id = fiberClient2.open_channel({
        "peer_id": NODE3_PEERID,
        "funding_amount": hex(10 * 100000000),
        "public": True,
        # "tlc_fee_proportional_millionths": "0x4B0",
        "funding_udt_type_script": {
            "code_hash": RUSD_TYPE_CODE_HASH,
            "hash_type": RUSD_HASH_TYPE,
            "args": RUSD_ARGS
        }
    })
    time.sleep(5)
    # fiberClient3.accept_channel({
    #     "temporary_channel_id": temporary_channel_id['temporary_channel_id'],
    #     "funding_amount": '0x0',
    # })
    # time.sleep(15)
    # wait channel open successful : channel statue: wait
    wait_for_channel_state(fiberClient2, NODE3_PEERID, "CHANNEL_READY", 120)

    channels = fiberClient3.list_channels({"peer_id": NODE2_PEERID})
    N2N3_CHANNEL_ID = channels['channels'][0]['channel_id']

    # before new pay balance
    before_channels = fiberClient1.list_channels({"peer_id": NODE2_PEERID})
    # time.sleep(20)
    # create new pay 0.1 usd
    payment_preimage = generate_random_preimage()

    invoice = fiberClient3.new_invoice(
        {
            "amount": hex(1 * 100000000),
            "currency": "Fibb",
            "description": "test invoice generated by node2",
            "expiry": "0xe10",
            "final_cltv": "0x28",
            "payment_preimage": payment_preimage,
            "hash_algorithm": HASH_ALGORITHM,
            "udt_type_script": {
                "code_hash": RUSD_TYPE_CODE_HASH,
                "hash_type": RUSD_HASH_TYPE,
                "args": RUSD_ARGS
            }
        }
    )
    payment_hash = invoice['invoice']['data']['payment_hash']
    payment_amount = invoice['invoice']['amount']
    invoice_address = invoice['invoice_address']
    time.sleep(10)
    # # cost pay
    tlc = fiberClient1.send_payment({
        "invoice": invoice_address,
        # "amount": payment_amount,
        # "payment_hash": payment_hash
    })

    time.sleep(10)
    # after  pay balance
    after_channelsN1N2 = fiberClient1.list_channels({"peer_id": NODE2_PEERID})
    print("before:", before_channels)
    print("after:", after_channelsN1N2)
    after_channelsN2N3 = fiberClient2.list_channels({"peer_id": NODE3_PEERID})
    print("after n2-n3:", after_channelsN2N3)

    # close channel
    fiberClient1.shutdown_channel(
        {
            "channel_id": N1N2_CHANNEL_ID,
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": NODE1_WALLET_ARG
            },
            "fee_rate": "0x3FC"
        }
    )
    #
    fiberClient2.shutdown_channel(
        {
            "channel_id": N2N3_CHANNEL_ID,
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": NODE2_WALLET_ARG
            },
            "fee_rate": "0x3FC"
        }
    )
