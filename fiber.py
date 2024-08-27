import random
import time

import requests

import json
NODE1_RPC_URL = "http://127.0.0.1:8227"
NODE1_PEERID = "Qmf15i3L9mibJCuYgvsPqZcjTsiQ237M4MSE4nCMdgYGia"
NODE1_ADDR = "/ip4/127.0.0.1/tcp/8228/p2p/Qmf15i3L9mibJCuYgvsPqZcjTsiQ237M4MSE4nCMdgYGia"

NODE1_WALLET_ARG = "0x88aa0c0a97d9cf7019a047c66ba78414a911e8c6"

NODE2_RPC_URL = "http://127.0.0.1:8230"
NODE2_PEERID = "QmSC11fpwr3PZb4bZdRyMq9rYTBcAGQ42UK9sSDraAycTZ"
NODE2_ADDR = "/ip4/127.0.0.1/tcp/8229/p2p/QmSC11fpwr3PZb4bZdRyMq9rYTBcAGQ42UK9sSDraAycTZ"

NODE2_WALLET_ARG = "0xb846777110d02f110655ef96d2def865deb9beb6"

HASH_ALGORITHM = "sha256"


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

    # connected node1 and node2
    fiberClient1.connect_peer({"address": NODE2_ADDR})
    time.sleep(10)
    
    # open channel node1 < - > node2
    fiberClient1.open_channel({
        "peer_id": NODE2_PEERID,
        "funding_amount": hex(2000 * 100000000)
    })

    # wait channel open successful : channel statue: wait
    wait_for_channel_state(fiberClient1, NODE2_PEERID, "CHANNEL_READY", 120)
    channels = fiberClient1.list_channels({"peer_id": NODE2_PEERID})
    N1N2_CHANNEL_ID = channels['channels'][0]['channel_id']

    # before new pay balance
    before_channels = fiberClient1.list_channels({"peer_id": NODE2_PEERID})

    # create new pay
    payment_preimage = generate_random_preimage()
    invoice = fiberClient2.new_invoice(
        {
            "amount": hex(20000000000),
            "currency": "Fibb",
            "description": "test invoice generated by node2",
            "expiry": "0xe10",
            "final_cltv": "0x28",
            "payment_preimage": payment_preimage,
            "hash_algorithm": HASH_ALGORITHM
        }
    )
    payment_hash = invoice['invoice']['data']['payment_hash']
    payment_amount = invoice['invoice']['amount']
    # cost pay
    tlc = fiberClient1.add_tlc(
        {
            "channel_id": N1N2_CHANNEL_ID,
            "amount": payment_amount,
            "payment_hash": payment_hash,
            "expiry": 40,
            "hash_algorithm": HASH_ALGORITHM
        }
    )
    N1N2_TLC_ID1 = tlc['tlc_id']
    fiberClient2.remove_tlc({
        "channel_id": N1N2_CHANNEL_ID,
        "tlc_id": N1N2_TLC_ID1,
        "reason": {
            "payment_preimage": payment_preimage
        }
    })
    time.sleep(10)
    # after  pay balance
    after_channels = fiberClient1.list_channels({"peer_id": NODE2_PEERID})
    print("before:", before_channels)
    print("after:", after_channels)

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

    fiberClient2.shutdown_channel(
        {
            "channel_id": N1N2_CHANNEL_ID,
            "close_script": {
                "code_hash": "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8",
                "hash_type": "type",
                "args": NODE2_WALLET_ARG
            },
            "fee_rate": "0x3FC"
        }
    )

    # wait channel remove
    wait_for_channel_removal(fiberClient1, NODE2_PEERID, 120)
