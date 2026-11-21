"""Every mesh of the robot descriptions loads through foxglove_bridge, like in Lichtblick.

    python3 tests/stack/mesh_check.py [ws://localhost:8765]

Needs the stack running (profile sim or real) and the Python package `websockets`. Reads
/georg_full/robot_description and /robot_description through the bridge, then fetches every
package:// URI with the bridge's fetchAsset, exactly as Lichtblick does. Exit code 1 if one
mesh cannot be loaded.
"""
import asyncio
import json
import re
import struct
import sys

import websockets

TOPICS = ['/georg_full/robot_description', '/robot_description']


def _cdr_string(payload):
    # std_msgs/String in CDR: 4 byte encapsulation header, uint32 length, bytes (with \0)
    length = struct.unpack('<I', payload[4:8])[0]
    return payload[8:8 + length - 1].decode('utf-8')


async def main(url):
    async with websockets.connect(url, subprotocols=['foxglove.websocket.v1', 'foxglove.sdk.v1'],
                                  max_size=None) as ws:
        channels, descriptions = {}, {}
        sub_ids = {}
        deadline = asyncio.get_event_loop().time() + 20
        while len(descriptions) < len(TOPICS) and asyncio.get_event_loop().time() < deadline:
            msg = await asyncio.wait_for(ws.recv(), 20)
            if isinstance(msg, str):
                data = json.loads(msg)
                if data.get('op') == 'advertise':
                    for ch in data['channels']:
                        if ch['topic'] in TOPICS and ch['topic'] not in channels:
                            channels[ch['topic']] = ch['id']
                            sub_id = len(sub_ids) + 1
                            sub_ids[sub_id] = ch['topic']
                            await ws.send(json.dumps({'op': 'subscribe', 'subscriptions': [
                                {'id': sub_id, 'channelId': ch['id']}]}))
            elif msg[0] == 0x01:  # message data
                sub_id = struct.unpack('<I', msg[1:5])[0]
                descriptions[sub_ids[sub_id]] = _cdr_string(msg[13:])
        uris = sorted({u for d in descriptions.values()
                       for u in re.findall(r'filename="(package://[^"]+)"', d)})
        print(f'descriptions: {sorted(descriptions)}; {len(uris)} mesh URIs', flush=True)
        for i, uri in enumerate(uris, 1):
            await ws.send(json.dumps({'op': 'fetchAsset', 'uri': uri, 'requestId': i}))
        failed, pending = [], set(range(1, len(uris) + 1))
        while pending:
            msg = await asyncio.wait_for(ws.recv(), 30)
            if isinstance(msg, bytes) and msg[0] == 0x04:
                rid, status, elen = struct.unpack('<IBI', msg[1:10])
                pending.discard(rid)
                if status != 0:
                    failed.append(f'{uris[rid - 1]}: {msg[10:10 + elen].decode()}')
        for line in failed:
            print('FAIL', line, flush=True)
        print(f'{len(uris) - len(failed)}/{len(uris)} meshes load', flush=True)
        return 1 if failed or len(descriptions) < len(TOPICS) else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'ws://localhost:8765')))
