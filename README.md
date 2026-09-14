# Redmi AX5400 (RA74) — OpenWrt NSS + dual CPU links

[中文](#中文) · [English](#english) · [下载固件 / Firmware](https://github.com/Yongzhaooo/redmi-ax5400-nss/releases)

## 中文

这是我在 **红米 AX5400 普通版（RA74，全千兆网口）** 上使用的 OpenWrt NSS 方案：修复有线 NSS 收包，并恢复 WAN/LAN 双 CPU 链路。硬件为 IPQ5018 + QCA8337，设备标识 `xiaomi,redmi-ax5400`。**不适用于电竞版或其他 AX5400。**

本仓库集成：

- **NSS 收包修复**：GMAC1 DMA 描述符使用 SDRAM。
- **QCA8337 r2 修复**：先配置并回读 VLAN 隔离，再开放端口；失败时尝试阻断端口并拒绝接管。
- **双链路默认配置**：WAN=`eth0.2`、LAN=`eth1.1`，两路 NSS 都启用，Wi-Fi NSS 卸载默认关闭。

下载 **`v2026.09.14-dual`** 可获得整合镜像。**上述驱动与双链路配置已经在我的 RA74 上实测；新生成镜像通过编译和离线检查，尚未单独刷机验证。** 保留配置升级不会覆盖旧设置；已使用双链路的设备可以继续保留，旧单链路配置按指南迁移。未收录不依赖的 DAC 实验补丁。

| 入口 | 内容 |
| --- | --- |
| [安装、配置与恢复](ra74/INSTALL.md) | 设备范围、升级、双链路检查及旧配置迁移 |
| [编译说明](ra74/BUILD.md) | Linux/WSL、锁定 feeds、测试命令 |
| [实测结果](ra74/VALIDATION.md) | 速率、断流监控和测试范围 |
| [版本来源](ra74/PROVENANCE.md) | 源码、补丁、配置和固件对应关系 |
| [Releases](https://github.com/Yongzhaooo/redmi-ax5400-nss/releases) | 固件、SHA256 与版本说明 |

实测下载 **914–921 Mbps**、上传 **856–888 Mbps**；同时运行下载和上传客户端约 **865 + 670 Mbps**。此前日常单链路配置约 18 小时的 **3,306 次 TCP 探测全部成功**。测试范围及一次较早的慢连接见实测记录，不代表已经证明长期无断流或双向同时跑满千兆。

这是个人 NSS 版本，**不是 OpenWrt 官方固件**。DSA/qca8k 仍负责开机初始化，之后 NSS 接管转发。已合并的 [NSS 收包 PR](https://github.com/kuncy7/openwrt-nss-edma/pull/1) 与官方 [DSA/WAN issue #24696](https://github.com/openwrt/openwrt/issues/24696) 是不同问题；这里不声称修复了官方 DSA，维护范围以这套可用的 NSS 方案为准。

仓库含完整 OpenWrt 主源码快照；外部 feeds 和软件包源码按锁定版本获取。基于 [kuncy7/openwrt-nss-edma](https://github.com/kuncy7/openwrt-nss-edma) 的 `a7cc5b9`，保留上游说明与许可证。未公开个人密码、网络配置备份或监控原始数据；后来安装的监控组件不内置于此镜像。

## English

This is the OpenWrt NSS setup I use on the **standard Redmi AX5400 (RA74, all Gigabit Ethernet ports)**. It restores wired NSS reception and uses both WAN/LAN CPU links. Hardware: IPQ5018 + QCA8337; board ID: `xiaomi,redmi-ax5400`. **Not for the Gaming Edition or other AX5400 models.**

Included in this repository:

- **NSS receive fix:** GMAC1 DMA descriptors in SDRAM.
- **QCA8337 r2 changes:** program and read back VLAN isolation before enabling ports; attempt port blocking and refuse takeover on failure.
- **Dual-link defaults:** WAN on `eth0.2`, LAN on `eth1.1`, both NSS interfaces enabled, Wi-Fi NSS offload disabled by default.

Download **`v2026.09.14-dual`** for the integrated image. **The drivers and dual-link configuration have been tested on my RA74; this newly packaged image has passed build and offline checks but has not separately been flashed.** Upgrades retaining settings preserve those settings: an existing dual-link setup can stay, while an old single-link setup needs the documented migration. The unrelated experimental DAC patch is excluded.

| Guide | Contents |
| --- | --- |
| [Installation, setup and recovery](ra74/INSTALL.md) | Compatibility, upgrades, dual-link checks and migration |
| [Building](ra74/BUILD.md) | Linux/WSL, pinned feeds and tests |
| [Validation](ra74/VALIDATION.md) | Throughput, connectivity monitoring and limits |
| [Provenance](ra74/PROVENANCE.md) | Source, patches, configuration and image identity |
| [Releases](https://github.com/Yongzhaooo/redmi-ax5400-nss/releases) | Firmware, SHA256 and release notes |

Observed speeds: **914–921 Mbps down / 856–888 Mbps up**; simultaneous clients measured about **865 Mbps down + 670 Mbps up**. Earlier monitoring on the daily single-link setup recorded **3,306 successful TCP checks over about 18 hours**. See the validation record for scope and an earlier slow connection; this does not establish long-term interruption-free operation or simultaneous full Gigabit in both directions.

This is a personal NSS build, **not an official OpenWrt release**. DSA/qca8k still initializes the switch at boot before NSS takes over forwarding. The merged [NSS receive fix](https://github.com/kuncy7/openwrt-nss-edma/pull/1) and official [DSA/WAN issue #24696](https://github.com/openwrt/openwrt/issues/24696) are separate problems. This project maintains the working NSS setup and does not claim to fix official DSA.

This is a full snapshot of the main OpenWrt source tree; external feeds and package sources are fetched at pinned revisions. Based on `a7cc5b9` from [kuncy7/openwrt-nss-edma](https://github.com/kuncy7/openwrt-nss-edma). Personal passwords, configuration backups and raw monitoring data are not published. Monitoring components installed later are not bundled in this image.

## 致谢与许可证 / Credits and licenses

Thanks to OpenWrt, kuncy7, the NSS package maintainers and contributors to the IPQ50xx port. Upstream documentation is retained in [README.upstream.md](README.upstream.md) and [README.ipq50xx.md](README.ipq50xx.md); use the RA74 guides above for this release. See [COPYING](COPYING) and [LICENSES](LICENSES). Components retain their individual licenses; included vendor firmware remains subject to its own license.
