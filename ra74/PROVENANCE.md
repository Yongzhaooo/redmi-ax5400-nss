# 版本来源 / Provenance

| Item | Value |
| --- | --- |
| Release | `v2026.09.14-dual` |
| Upstream source | https://github.com/kuncy7/openwrt-nss-edma |
| Upstream base | `a7cc5b9d6b6ea31dcae6a6588111417e71f44011` (`ipq50xx-rebase`) |
| Target / board | `qualcommax/ipq50xx` / `xiaomi,redmi-ax5400` |
| Kernel | `6.18.44` |
| Image revision string | `r0-a7cc5b9` |
| QCA8337 package release | `r2` |
| NSS tools package release | `r3` (dual-link defaults added) |
| Integrated image bytes | `18893074` |
| Integrated image SHA256 | `e60a0c27f50a339ca38fd322a2276f48cbddc4c0efbc7b26ac76ea9972a9026b` |
| Original daily image SHA256 | `b5f600f2d87ac752c1fb58f59135aeda3246fc70927662a93026c830ed4bbfb0` |

## 中文

本仓库建立独立的完整主源码快照，保留上游许可证和归属，不复制整个历史。原实测构建的五文件差异保存在 [source.patch](source.patch)：QCA8337 失败处理/回读与包版本、NSS 启动失败处理/SDRAM 与包版本，以及关闭额外内核调试选项。

在原差异之上，本次将 `nss-tools` 从 r2 升到 r3，并修改 `nss-dwmac.defaults`：RA74 默认启用 CPU5/GMAC0 WAN 和 CPU6/GMAC1 LAN、唤醒 PHY4、设置双 VLAN、关闭 Wi-Fi NSS 卸载，并保留 WAN 设备 MAC/MTU。已有 topology 标记的配置仍保持不变；迁移见安装指南。`check_defaults.py` 覆盖新增行为。

[build.config](build.config) 是本次整合构建的配置；[feeds.conf](feeds.conf) 和 [feed-revisions.txt](feed-revisions.txt) 固定依赖来源。[版本目录](releases/2026.09.14) 保存包清单、校验清单与构建元数据。固件二进制通过 Release 交付，不放进 Git 历史。

本次以原缓存完整构建，移除了未部署的 DAC 候选参与构建的可能；构建完成后原实验源码及候选均已恢复保存。新镜像内核和两项驱动模块与旧日常镜像逐字节相同。没有重新刷路由器、改变当前网络或发布个人配置。

软件包源码由上游 Makefile 的 URL/版本/哈希获取，外部 feeds 以固定提交获取；不是把所有 tarball 或工具链缓存都提交到 Git。独立快照的 Git HEAD 与内置 `r0-a7cc5b9` 字符串不同，Release 标签用于识别本次源码。公开仓库保留上游 GitHub 工作流，但 Actions 关闭，避免把上游自动化误当成本项目已配置的发布服务。

## English

This repository starts an independent full snapshot of the main source tree, retaining upstream attribution and licenses without importing its complete history. [source.patch](source.patch) records the original five-file daily-build delta: QCA8337 failure handling/readback and release bump; NSS startup failure handling/SDRAM override and release bump; and removal of additional kernel debug settings.

On top, this release bumps `nss-tools` from r2 to r3 and updates `nss-dwmac.defaults`: RA74 uses CPU5/GMAC0 for WAN and CPU6/GMAC1 for LAN, wakes PHY4, sets split VLANs, disables Wi-Fi NSS offload and retains the WAN device's MAC/MTU. Configurations already carrying the topology marker remain unchanged; see installation for migration. `check_defaults.py` covers the added behavior.

[build.config](build.config) is the integrated build configuration. [feeds.conf](feeds.conf) and [feed-revisions.txt](feed-revisions.txt) pin dependency sources. The [release directory](releases/2026.09.14) contains package, checksum and build metadata; firmware binaries are Release assets rather than Git history.

The full build reused the original cache with the uninstalled DAC candidate excluded. Original experimental source/configuration and the candidate were restored afterward. The new kernel and both driver modules match the daily image byte for byte. No router flash, current network change or personal configuration publication occurred.

Package sources are fetched through upstream Makefile URLs, versions and hashes; feeds use fixed Git commits. Download tarballs and toolchain caches are not all committed. This snapshot's Git HEAD differs from the embedded `r0-a7cc5b9` string; use the release tag to identify the published source. Inherited workflows remain in the snapshot, but GitHub Actions is disabled rather than presented as configured release infrastructure.
