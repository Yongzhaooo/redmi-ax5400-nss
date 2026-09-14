#!/usr/bin/env python3
"""Execute the shipped first-boot script against a disposable UCI model."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).resolve()
script = (source / 'package/nss/nss-tools/files/nss-dwmac.defaults').read_text()
shim = r'''#!/usr/bin/env python3
import json, os, sys
path = os.environ['UCI_STATE']
state = json.load(open(path))
args = [arg for arg in sys.argv[1:] if arg != '-q']
op = args[0]
key = args[1] if len(args) > 1 else ''
if op == 'get':
    if key not in state: sys.exit(1)
    print(state[key]); sys.exit(0)
if op == 'set':
    key, value = key.split('=', 1); state[key] = value
elif op == 'delete': state.pop(key, None)
elif op == 'add_list':
    key, value = key.split('=', 1)
    state[key] = (state.get(key, '') + ' ' + value).strip()
elif op != 'commit': raise ValueError(args)
with open(path, 'w') as f: json.dump(state, f)
'''
functions = r'''
board_name() { printf '%s\n' "$TEST_BOARD"; }
logger() { :; }
config_load() { :; }
config_get() { eval "$1=\$(uci -q get network.$2.$3)"; }
config_foreach() { "$1" '@device[0]'; "$1" wan_device; }
'''
base = {
    'network.lan': 'interface', 'network.lan.device': 'br-lan',
    'network.@device[0]': 'device', 'network.@device[0].name': 'br-lan',
    'network.@device[0].ports': 'lan1 lan2 lan3',
    'network.wan': 'interface', 'network.wan.device': 'wan',
    'network.wan6': 'interface', 'network.wan6.device': 'wan',
    'network.wan_device': 'device', 'network.wan_device.name': 'wan',
    'network.wan_device.macaddr': '02:00:00:00:00:01',
    'network.wan_device.mtu': '1500', 'nss.general.wifi_offload': '1',
}
with tempfile.TemporaryDirectory(prefix='ra74-defaults-') as directory:
    tmp = Path(directory)
    tool = tmp / 'uci'
    tool.write_text(shim); tool.chmod(0o755)
    actual = tmp / 'defaults.sh'
    assert script.count('. /lib/functions.sh') == 1
    actual.write_text(script.replace('. /lib/functions.sh', functions))
    subprocess.run(['sh', '-n', str(actual)], check=True)

    def run(board, state):
        state_file = tmp / 'state.json'
        state_file.write_text(json.dumps(state))
        env = dict(os.environ, TEST_BOARD=board, UCI_STATE=str(state_file),
                   PATH=str(tmp) + ':' + os.environ['PATH'])
        subprocess.run(['sh', str(actual)], env=env, check=True)
        return json.loads(state_file.read_text())

    result = run('xiaomi,redmi-ax5400', base)
    expected = {
        'nss.general.fw_mask': '0x3', 'nss.general.trunk': 'eth1',
        'nss.general.trunk_if': '1', 'nss.general.extra_ports': '0:eth0',
        'nss.general.vtu': '1:6t,2u,3u,4u;2:5t,1u',
        'nss.general.wifi_offload': '0', 'nss.general.topology': 'vlan-trunk',
        'network.wan.device': 'eth0.2', 'network.wan6.device': 'eth0.2',
        'network.wan_device.name': 'eth0.2', 'network.@device[0].ports': 'eth1.1',
    }
    for key, value in expected.items(): assert result.get(key) == value, (key, result)
    assert 'ports=0x7e' in result['nss.general.switch_args']
    assert result['nss.general.switch_args'].endswith('90000.mdio-1:04')
    for key in ('network.wan_device.macaddr', 'network.wan_device.mtu', 'network.lan.device'):
        assert result[key] == base[key]
    assert run('xiaomi,redmi-ax5400', result) == result, 'must be idempotent'
    retained = dict(base, **{'nss.general.topology': 'vlan-trunk', 'nss.general.vtu': 'custom'})
    assert run('xiaomi,redmi-ax5400', retained) == retained, 'retained config changed'
    no_v6 = {key: value for key, value in base.items() if not key.startswith('network.wan6')}
    assert 'network.wan6.device' not in run('xiaomi,redmi-ax5400', no_v6)
    other = run('glinet,gl-b3000', base)
    assert other['network.wan.device'] == 'eth0.2'
    assert other['network.@device[0].ports'] == 'eth0.1'
    assert other['nss.general.fw_mask'] == '0x2'
    tagged = dict(base, **{'network.wan.device': 'eth0.35'})
    assert run('glinet,gl-b3000', tagged)['network.wan.device'] == 'eth0.35'
print('PASS: fresh RA74 dual links, host Wi-Fi, MAC/MTU retention, repeat boot, retained settings, absent WAN6, other-board and tagged-WAN controls')
