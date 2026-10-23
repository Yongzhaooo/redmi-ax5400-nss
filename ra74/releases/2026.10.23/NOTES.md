# RA74 NSS + ath11k completion fix — 2026.10.23

## 中文

在 `v2026.09.14-dual` 的基础上加入三处内核修改，其余配置和软件包不变：

- **ath11k 回执泄漏修复**：NSS 补丁 `244-ath11k-dp-tx-perf` 读错了 HTT 回执状态的位置，一部分固件释放的帧（主要是组播和广播）的回执被当成 MEC 通知跳过，skb 永远不释放，路由器几天后内存耗尽。`soc_dp_stats` 新增两行：`TX Completions Skipped (MEC notify)` 和每个频段的 `TX Pending (host path)`。
- **IPQ5018 内部 PHY**：DAC 位域修复（已进 6.18.56）和 probe 时就写入模拟参数（已进 net-next）。
- **`SLUB_DEBUG`**：提供 `/proc/slabinfo`，运行时调试关闭。

旧版本开着 Wi-Fi 时会慢慢漏内存，建议升级。

验证情况：

- 这些内核修改在我的 RA74 日用固件里自 2026-10-22 起运行。24 小时内没有重启或 OOM，两个频段的待完成帧保持在 0–4，被跳过的回执为 0。修复前待完成帧涨到 1384（5 GHz）和 322（2.4 GHz）。
- 本镜像从干净源码树完整编译。内核代码段、设备树，以及 ath11k、mac80211、QCA8337 和 NSS 等模块，都与日用固件逐字节相同。日用固件另外装了个人监控组件，并保留了旧配置。
- **这份镜像本身尚未单独刷机**，作为预发布提供。保留配置升级不会改写已有设置。

不适用于电竞版、其他 AX5400 或未经确认的分区布局。不含个人配置、密钥或监控组件。

## English

Three kernel changes on top of `v2026.09.14-dual`; the configuration and package set are otherwise unchanged:

- **ath11k completion leak fix:** the NSS patch `244-ath11k-dp-tx-perf` read the HTT completion status from the wrong place. Some firmware-released frames, mostly multicast and broadcast, had their completion skipped as a MEC notification, the skbs were never freed and the router ran out of memory after a few days. `soc_dp_stats` gains `TX Completions Skipped (MEC notify)` and a per-radio `TX Pending (host path)`.
- **IPQ5018 internal PHY:** the DAC field fix (in 6.18.56) and writing the analog settings at probe (in net-next).
- **`SLUB_DEBUG`** for `/proc/slabinfo`; runtime debugging stays off.

The previous release slowly leaks memory while Wi-Fi is in use; upgrading is recommended.

Validation:

- These kernel changes have run in my daily RA74 firmware since 2026-10-22. Over 24 hours there was no reboot or OOM, pending frames stayed at 0–4 on both radios and no completion was skipped. Before the fix, pending frames reached 1384 (5 GHz) and 322 (2.4 GHz).
- This image was built from a clean tree. Its kernel code, device tree and the ath11k, mac80211, QCA8337 and NSS modules are byte-identical to the daily firmware, which additionally carries personal monitoring packages and retained settings.
- **This image itself has not separately been flashed**; it is offered as a prerelease. Upgrades retaining settings keep existing configuration.

Not for the Gaming Edition, other AX5400 devices or unverified partition layouts. No personal settings, keys or monitoring packages are included.

```text
File:   openwrt-qualcommax-ipq50xx-xiaomi_redmi-ax5400-squashfs-sysupgrade.bin
Bytes:  18913557
SHA256: 0ebadc57b83c13dcac34b924b2894d938c9617dfc8a86658aade6d06de4f4f2a
Board:  xiaomi,redmi-ax5400
Kernel: 6.18.44
```
