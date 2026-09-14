# RA74 NSS + dual CPU links — 2026.09.14

## 中文

面向红米 AX5400 普通版 RA74（全千兆）的个人 OpenWrt NSS 镜像：保留 QCA8337 r2 和 NSS SDRAM 收包修复，**默认配置整合 WAN eth0.2 + LAN eth1.1 双链路**，关闭 Wi-Fi NSS 卸载。不含 DAC 实验补丁。

驱动与相同双链路配置已在日常设备实测。**这份新打包镜像通过完整编译、镜像内容检查和三项离线测试，尚未单独实刷，因此作为预发布提供。** 内核及交换机/NSS glue 模块与日常固件逐字节一致。保留配置升级不会改写已有配置，旧单链路用户需按指南迁移。

- 实测速率：下载 914–921 / 上传 856–888 Mbps；并发客户端约 865 + 670 Mbps。
- 此前单链路日常监控：18 小时 21 分钟，3306 次 TCP 探测成功，窗口内无失败或超时；更早有一次成功但耗时 1.07 秒的连接。分钟采样不等于长期无断流。
- 不是官方 DSA 修复，不适用于电竞版、其他 AX5400 或未经确认的分区布局。
- 不含个人配置、密钥、原始监控日志或后来安装的监控组件。

请先阅读[安装与恢复](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/INSTALL.md)、[编译说明](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/BUILD.md)及[实测范围](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/VALIDATION.md)。

## English

A personal OpenWrt NSS image for the standard Redmi AX5400 RA74 (all Gigabit ports). Retains QCA8337 r2 and the NSS SDRAM receive fix, and **integrates dual-link defaults: WAN eth0.2 + LAN eth1.1**, with Wi-Fi NSS offload disabled. The experimental DAC patch is excluded.

The drivers and equivalent dual-link configuration have been tested on the daily device. **This newly packaged image passed the full build, content inspection and three offline checks, but has not separately been flashed; it is offered as a prerelease.** The kernel and switch/NSS glue modules match the daily image byte for byte. Retained settings are not overwritten; old single-link configurations need the documented migration.

- Observed throughput: 914–921 Mbps down / 856–888 Mbps up; simultaneous clients about 865 + 670 Mbps.
- Earlier single-link monitoring: 3306 successful TCP checks over 18 hours 21 minutes, no failures/timeouts in that window; one earlier successful connection took 1.07 seconds. Minute-level sampling is not proof of interruption-free operation.
- Not an official DSA fix, and not for the Gaming Edition, other AX5400 devices or unverified partition layouts.
- No personal settings, keys, raw monitoring logs or monitoring components installed later are included.

Read [installation/recovery](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/INSTALL.md), [building](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/BUILD.md) and [validation scope](https://github.com/Yongzhaooo/redmi-ax5400-nss/blob/main/ra74/VALIDATION.md) first.

```text
File:   openwrt-qualcommax-ipq50xx-xiaomi_redmi-ax5400-squashfs-sysupgrade.bin
Bytes:  18893074
SHA256: e60a0c27f50a339ca38fd322a2276f48cbddc4c0efbc7b26ac76ea9972a9026b
Board:  xiaomi,redmi-ax5400
Kernel: 6.18.44
```
