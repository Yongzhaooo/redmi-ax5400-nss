# 版本来源 / Provenance

| Item | Value |
| --- | --- |
| Release | `v2026.10.23-ath11k` (previous: `v2026.09.14-dual`) |
| Upstream source | https://github.com/kuncy7/openwrt-nss-edma |
| Upstream base | `a7cc5b9d6b6ea31dcae6a6588111417e71f44011` (`ipq50xx-rebase`) |
| Target / board | `qualcommax/ipq50xx` / `xiaomi,redmi-ax5400` |
| Kernel | `6.18.44` |
| Image revision string | `r3-3d76691d96` (2026-10-23 source commit; `v2026.09.14-dual` showed `r0-a7cc5b9`) |
| QCA8337 package release | `r2` |
| NSS tools package release | `r3` (dual-link defaults added) |
| Added on 2026-10-23 | ath11k `999-960`, PHY `0092`/`0093`, `CONFIG_KERNEL_SLUB_DEBUG=y` |
| Integrated image bytes | `18913557` (`v2026.09.14-dual`: `18893074`) |
| Integrated image SHA256 | `0ebadc57b83c13dcac34b924b2894d938c9617dfc8a86658aade6d06de4f4f2a` (`v2026.09.14-dual`: `e60a0c27…`) |
| Daily v2 image compared against | `90d85a603212db522db3c63614497b79acb641112e06499023cf26916bcac87b` (private) |
| Original daily image SHA256 | `b5f600f2d87ac752c1fb58f59135aeda3246fc70927662a93026c830ed4bbfb0` |

## 中文

本仓库建立独立的完整主源码快照，保留上游许可证和归属，不复制整个历史。原实测构建的五文件差异保存在 [source.patch](source.patch)：QCA8337 失败处理/回读与包版本、NSS 启动失败处理/SDRAM 与包版本，以及关闭额外内核调试选项。

在原差异之上，本次将 `nss-tools` 从 r2 升到 r3，并修改 `nss-dwmac.defaults`：RA74 默认启用 CPU5/GMAC0 WAN 和 CPU6/GMAC1 LAN、唤醒 PHY4、设置双 VLAN、关闭 Wi-Fi NSS 卸载，并保留 WAN 设备 MAC/MTU。已有 topology 标记的配置仍保持不变；迁移见安装指南。`check_defaults.py` 覆盖新增行为。

[build.config](build.config) 是本次整合构建的配置；[feeds.conf](feeds.conf) 和 [feed-revisions.txt](feed-revisions.txt) 固定依赖来源。[版本目录](releases/2026.09.14) 保存包清单、校验清单与构建元数据。固件二进制通过 Release 交付，不放进 Git 历史。

本次以原缓存完整构建，移除了未部署的 DAC 候选参与构建的可能；构建完成后原实验源码及候选均已恢复保存。新镜像内核和两项驱动模块与旧日常镜像逐字节相同。没有重新刷路由器、改变当前网络或发布个人配置。

### 2026-10-23 更新

在上述源码之上加入三处内核修改，对应现网日用固件 v2 的内核：

- `package/kernel/mac80211/patches/nss/ath11k/999-960-…`：`244-ath11k-dp-tx-perf` 的 `ath11k_dp_tx_completion_valid()` 把字节偏移加在结构体指针上，读到描述符后 128 字节处，部分固件释放的回执被当作 MEC 通知跳过，skb 一直挂在 tx idr 表里。补丁改用字节运算，把一处未初始化的 `msdu` 置为 NULL，并在 `soc_dp_stats` 增加两行计数。
- `target/linux/qualcommax/patches-6.18/0092-…`：DAC 位域修复，回移植自 net `20f3599d85b4`（已在 6.18.56）。
- `0093-…`：probe 时就写入 IPQ5018 内部 PHY 的模拟参数并重启协商，回移植自 net-next `17baf30a0e64`，保留本树的 RX/TX 时钟管理。
- `build.config`：`CONFIG_KERNEL_SLUB_DEBUG=y`，`SLUB_DEBUG_ON` 关闭。

本次用干净源码树在 Linux ext4 上按 [BUILD.md](BUILD.md) 完整编译，feeds 与 [feeds.conf](feeds.conf) 一致。与日用 v2 镜像对比：内核 `.text` 逐字节相同，`.rodata`/`.data` 只差版本串和日期；设备树相同；ath11k、mac80211、cfg80211、qca8337-nss、qca-dwmac-nss、qca-nss-drv 模块相同。日用 v2 另有个人监控组件和 r2 单链路默认脚本（现网保留旧配置），这些不在本仓库。[版本目录](releases/2026.10.23)保存清单与元数据。

软件包源码由上游 Makefile 的 URL/版本/哈希获取，外部 feeds 以固定提交获取；不是把所有 tarball 或工具链缓存都提交到 Git。独立快照的 Git HEAD 与内置 `r0-a7cc5b9` 字符串不同，Release 标签用于识别本次源码。公开仓库保留上游 GitHub 工作流，但 Actions 关闭，避免把上游自动化误当成本项目已配置的发布服务。

## English

This repository starts an independent full snapshot of the main source tree, retaining upstream attribution and licenses without importing its complete history. [source.patch](source.patch) records the original five-file daily-build delta: QCA8337 failure handling/readback and release bump; NSS startup failure handling/SDRAM override and release bump; and removal of additional kernel debug settings.

On top, this release bumps `nss-tools` from r2 to r3 and updates `nss-dwmac.defaults`: RA74 uses CPU5/GMAC0 for WAN and CPU6/GMAC1 for LAN, wakes PHY4, sets split VLANs, disables Wi-Fi NSS offload and retains the WAN device's MAC/MTU. Configurations already carrying the topology marker remain unchanged; see installation for migration. `check_defaults.py` covers the added behavior.

[build.config](build.config) is the integrated build configuration. [feeds.conf](feeds.conf) and [feed-revisions.txt](feed-revisions.txt) pin dependency sources. The [release directory](releases/2026.09.14) contains package, checksum and build metadata; firmware binaries are Release assets rather than Git history.

The full build reused the original cache with the uninstalled DAC candidate excluded. Original experimental source/configuration and the candidate were restored afterward. The new kernel and both driver modules match the daily image byte for byte. No router flash, current network change or personal configuration publication occurred.

### 2026-10-23 update

Three kernel changes on top, matching the kernel of the daily v2 firmware:

- `package/kernel/mac80211/patches/nss/ath11k/999-960-…`: `ath11k_dp_tx_completion_valid()` in `244-ath11k-dp-tx-perf` added a byte offset to a struct pointer and read 128 bytes past the descriptor, so some firmware-released completions were skipped as MEC notifications and their skbs stayed in the tx idr pool. The patch uses byte arithmetic, initializes `msdu` to NULL in one error path and adds two `soc_dp_stats` counters.
- `target/linux/qualcommax/patches-6.18/0092-…`: the DAC field fix, backported from net `20f3599d85b4` (in 6.18.56).
- `0093-…`: writes the IPQ5018 internal PHY analog settings at probe and restarts autonegotiation, backported from net-next `17baf30a0e64` while keeping this tree's RX/TX clock handling.
- `build.config`: `CONFIG_KERNEL_SLUB_DEBUG=y` with `SLUB_DEBUG_ON` off.

The release was built from a clean tree on Linux ext4 following [BUILD.md](BUILD.md), with feeds matching [feeds.conf](feeds.conf). Against the daily v2 image, the kernel `.text` is byte-identical and `.rodata`/`.data` differ only in version strings and dates; the device tree and the ath11k, mac80211, cfg80211, qca8337-nss, qca-dwmac-nss and qca-nss-drv modules are identical. The daily image also carries personal monitoring packages and the r2 single-link defaults script (its settings are retained); those are not part of this repository. See the [release directory](releases/2026.10.23).

Package sources are fetched through upstream Makefile URLs, versions and hashes; feeds use fixed Git commits. Download tarballs and toolchain caches are not all committed. This snapshot's Git HEAD differs from the embedded `r0-a7cc5b9` string; use the release tag to identify the published source. Inherited workflows remain in the snapshot, but GitHub Actions is disabled rather than presented as configured release infrastructure.
