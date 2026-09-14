# 安装、配置与恢复 / Installation, configuration and recovery

## 中文

本 Release 是 **RA74 sysupgrade 镜像**，不是小米原厂一键安装包。整合源码默认使用双链路；**新镜像尚未单独实刷**，实机证据来自相同驱动加相同双链路配置的日常系统。原厂解锁、首次安装和其他分区布局不在本次验证范围内。

1. 用 `ubus call system board` 核实设备标识 `xiaomi,redmi-ax5400`。保存可用旧镜像及其配置：`sysupgrade -b /tmp/pre-upgrade.tar.gz`，将归档下载到电脑；其中可能含密钥，不要公开上传。
2. 准备 LAN 管理和设备对应的救援方式。首次使用或迁移时，拔掉 ISP WAN，电脑接 LAN，另留手机 USB 网络。备份归档不能代替无法启动时的救援。
3. 下载 Release 的 `.bin` 和 `SHA256SUMS`。Linux 运行 `sha256sum -c SHA256SUMS`；PowerShell 用 `Get-FileHash -Algorithm SHA256` 对照清单。
4. **已使用本套兼容 NSS 固件时**，上传镜像为 `/tmp/ra74.bin`，先运行 `sysupgrade -T /tmp/ra74.bin`。通过后可在 LuCI 保留配置升级，或主动运行 `sysupgrade /tmp/ra74.bin`；后者立即刷写并重启。拒绝时不要用 `-F` 强刷。
5. **保留配置的行为**：已有双链路配置保持原样；旧单链路配置也会保留，需要按下方迁移。原首次启动脚本用 `nss.general.topology` 判断是否已迁移，不会覆盖已有自定义设置。从官方 DSA 迁移不能盲目保留配置；旧 `wan`/`lan*` 接口与 NSS VLAN 布局不同，需要先准备匹配的配置。
6. 新配置应为 `br-lan` 包含 `eth1.1`，WAN/WAN6=`eth0.2`，NSS mask=`0x3`、extra_ports=`0:eth0`、Wi-Fi 卸载=`0`。先确认本地管理、密码、防火墙及 WAN/LAN 隔离，再接回 WAN，验证有线外网及个人监控。

实测使用外部不带 VLAN 标签的 DHCP WAN。PPPoE、ISP 自定义 VLAN、访客网络和自定义桥需分别验证。此处 VLAN 1/2 是内部标记，不能直接当成运营商 VLAN。

## English

This release is a **RA74 sysupgrade image**, not a one-click Xiaomi stock installer. Source defaults use both CPU links. **The newly packaged image has not separately been flashed**; hardware evidence comes from the daily system using the same drivers and dual-link settings. Stock unlocking, first installation and other partition layouts are outside this validation.

1. Verify `xiaomi,redmi-ax5400` with `ubus call system board`. Save a working old image and its configuration: `sysupgrade -b /tmp/pre-upgrade.tar.gz`, then download the archive. It may contain secrets; do not publish it.
2. Prepare LAN management and device-specific recovery. For first use/migration, disconnect ISP WAN, keep a computer on LAN and retain an independent Internet connection. A configuration archive does not replace recovery for a device that cannot boot.
3. Download the `.bin` and `SHA256SUMS`. On Linux run `sha256sum -c SHA256SUMS`; on PowerShell compare `Get-FileHash -Algorithm SHA256` with the list.
4. **From this compatible NSS setup**, upload the image as `/tmp/ra74.bin` and run `sysupgrade -T /tmp/ra74.bin`. If it passes, use LuCI to upgrade while keeping settings, or deliberately run `sysupgrade /tmp/ra74.bin`, which immediately flashes and reboots. Do not bypass rejection with `-F`.
5. **Retained settings:** existing dual-link settings remain; old single-link settings also remain and need the migration below. The first-boot script checks `nss.general.topology` and preserves already migrated/custom configurations. Do not blindly retain official DSA settings: `wan`/`lan*` devices and NSS VLAN interfaces are different layouts. Prepare matching configuration before migration.
6. Check `eth1.1` in `br-lan`, WAN/WAN6=`eth0.2`, NSS mask=`0x3`, extra_ports=`0:eth0`, and Wi-Fi offload=`0`. Confirm local management, passwords, firewall and WAN/LAN separation before reconnecting WAN; then verify wired Internet and personal monitoring.

Hardware testing used DHCP on an externally untagged WAN. PPPoE, custom ISP VLANs, guest networks and custom bridges need separate validation. VLANs 1/2 here are internal tags, not automatically the ISP's VLAN IDs.

## 旧单链路迁移 / Migrating retained single-link settings

中文：仅在已迁移到 NSS、`br-lan` 已包含 `eth1.1`、已有 `network.wan` 的普通 RA74 上使用。先备份 `/etc/config/network` 和 `/etc/config/nss`，检查 `uci show network`。命令不改 IP、Wi-Fi 密码或防火墙；运行后需重启，会中断网络。

English: use only on a standard RA74 already migrated to NSS, with `eth1.1` in `br-lan` and an existing `network.wan`. First back up `/etc/config/network` and `/etc/config/nss`, and inspect `uci show network`. These commands leave IP addresses, Wi-Fi passwords and firewall settings alone. A reboot is required and interrupts networking.

```sh
[ "$(cat /tmp/sysinfo/board_name)" = 'xiaomi,redmi-ax5400' ] || exit 1
uci set nss.general.enabled='1'
uci set nss.general.wifi_offload='0'
uci set nss.general.fw_logbuf='256'
uci set nss.general.fw_mask='0x3'
uci set nss.general.trunk='eth1'
uci set nss.general.trunk_if='1'
uci set nss.general.extra_ports='0:eth0'
uci set nss.general.topology='vlan-trunk'
uci set nss.general.switch_args='cpu_port=6 ports=0x7e wake_phys=90000.mdio-1:00,90000.mdio-1:01,90000.mdio-1:02,90000.mdio-1:03,90000.mdio-1:04'
uci set nss.general.vtu='1:6t,2u,3u,4u;2:5t,1u'
uci set nss.general.enable_rps='1'
uci set nss.general.enable_log='1'
uci set network.wan.device='eth0.2'
if uci -q get network.wan6 >/dev/null; then
    uci set network.wan6.device='eth0.2'
fi
```

中文：旧 WAN 的 `config device` 节也需要改名为 `eth0.2`，保留其 MAC/MTU。实测设备节名为 `network.wan_device`；只有你的配置同名时才使用下面第一条。否则用实际节名，不要创建重复设备节。

English: rename the old WAN's `config device` entry to `eth0.2`, retaining its MAC/MTU. The tested unit used `network.wan_device`; use the first command below only if yours does too. Otherwise use the actual section name and avoid duplicate device entries.

```sh
# Only if this is the existing WAN device section:
uci set network.wan_device.name='eth0.2'
uci changes network
uci changes nss
# After reviewing both configurations:
uci commit network
uci commit nss
reboot
```

## 验证与回退 / Verification and rollback

```sh
ethtool eth0
ethtool eth1
cat /sys/kernel/debug/qca-dwmac-nss/status
cat /sys/module/qca_nss_drv/parameters/meminfo_user_config
ubus call network.interface.wan status
logread -e nss
```

中文：两路应为 1000/full、NSS `started`，传输时 RX 增长；GMAC1 描述符应为 SDRAM。电脑强制走以太网测试 HTTPS/速率，避免 USB 或 Wi-Fi 代跑。计数正常不能代替防火墙和隔离测试。

配置回退时，将保存的 `network` 和 `nss` **成对恢复**并重启。固件回退时使用对应旧镜像及其配置，返回官方 DSA 时不保留 NSS VLAN 设置。失去管理时用事先准备的救援入口。`nss.general.enabled=0` 不会自动恢复官方 DSA 拓扑。

English: expect 1000/full, both NSS interfaces `started`, increasing RX during traffic, and SDRAM descriptors for GMAC1. Bind client HTTPS/throughput tests to Ethernet to exclude USB/Wi-Fi. Healthy counters do not replace firewall/isolation checks.

For configuration rollback, restore saved `network` and `nss` files **together** and reboot. Firmware rollback needs the matching old image and its settings; do not retain NSS VLAN settings when returning to official DSA. Use the prepared recovery path if management is lost. `nss.general.enabled=0` does not automatically restore official DSA topology.
