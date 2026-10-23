# 验证记录 / Validation record

## 中文

### 2026-10-23：ath11k 回执修复与 PHY 修复

内核修改在我的 RA74 日用固件里运行（10/22 15:53 UTC 刷入，保留配置）。以下是之后约 24 小时的 Prometheus 记录：

- 没有重启，OOM 次数为 0，没有内核崩溃记录。
- 两个频段的 `TX Pending (host path)` 按小时最大值在 0–4；`TX Completions Skipped (MEC notify)` 始终为 0。修复前同一指标涨到 1384（5 GHz）和 322（2.4 GHz），最终内存耗尽。
- SUnreclaim 保持在 61–62 MiB。MemAvailable 在 42–146 MiB 间随流量波动，没有下降趋势；低点时只有空闲页变化，缓存和 slab 不变。
- 两个频段都有客户端在用，DNS、HTTPS 和每分钟 TCP 探测正常。

发布镜像从干净源码树编译（`make -j20 V=s` 退出 0），三项离线测试通过。它与日用固件的内核代码段、设备树和 ath11k、mac80211、QCA8337、NSS 等模块逐字节相同，软件包集合与 `v2026.09.14-dual` 相同。这份镜像本身没有单独刷机。本节没有重新测吞吐，也没有做 NSS 隔离或生命周期试验。

### 2026-09-14：双链路

以下硬件结果来自 2026-09-14 的 RA74 日常系统：基线 `a7cc5b9`，QCA8337 r2、GMAC1 SDRAM 修复，关闭 Wi-Fi NSS 卸载。双链路通过配置修改和一次重启启用，没有刷入 DAC 候选。

两条链路均 1000/full，两路 NSS `started`、RX 增长。有线 HTTPS 成功；WAN 端口 1 仅到 CPU5，LAN 端口 2–4 到 CPU6，VLAN 成员掩码分别为 `0x22`/`0x5c`。GMAC0 默认 SDRAM，GMAC1 显式 SDRAM。

| 测试 | 下载 Mbps | 上传 Mbps | 丢包报告 | 平均路由器 CPU |
| --- | ---: | ---: | ---: | ---: |
| Ookla / Telia 45936 | 913.96 | 856.39 | 0% | 7.33% |
| Ookla / Bredband2 40277 | 920.73 | 887.91 | 0% | 15.31% |
| 两个并发 speedtest-go 客户端，约 10 秒 | 864.77 | 670.05 | 未测 | 未测 |

Ookla 的下载/上传分开运行。并发试验中另取 5.151 秒的网卡计数窗口，得到接收 914.74 + 发送 756.69 = **1671.43 Mbps 合计**；这是选定重叠窗口，不是完整应用测试平均值。电脑测试绑定以太网，手机 USB 没有承载主要测速流量。

运营商在重连时改变了 DHCP 租约/路径，不能把昨天和今天的全部速率差异归因于补丁。没有证明双向同时持续 1 Gbps、长期稳定或任何网络环境下都达到同样速率。本轮双链路做了交换机回读和离线故障注入，未重新做实物 WAN 侧负向隔离试验；此前单链路 NSS 阶段的物理隔离测试通过。

### 2026-09-14 断流监控

日常**单链路**配置的 9 月 13 日 23:40 至 14 日 18:01 CEST，共 18 小时 21 分钟，每分钟向三个目标的 TCP 443 各探测一次：

| 目标 | 成功 / 总数 | 中位建连耗时 | 最长耗时 |
| --- | ---: | ---: | ---: |
| Cloudflare 1.1.1.1 | 1102 / 1102 | 20 ms | 30 ms |
| Google 8.8.8.8 | 1102 / 1102 | 20 ms | 60 ms |
| 个人 VPS（地址不公开） | 1102 / 1102 | 60 ms | 80 ms |

该窗口 **3306 次全部成功，无超时、失败或超过 1 秒的连接**。更早的 13 日 22:46 CEST 有一次到 Cloudflare 的 1.07 秒慢连接，但成功，次分钟恢复正常。离线设置和主动拔 WAN 期间的失败单独归类。每分钟探测可能漏掉短暂中断，也不是丢包测试。这不是双链路的长期结果。原始日志和 NAS 历史已私有备份；双链路启用后，三个新探测目标及监控采集恢复检查通过。

### 2026-09-14 镜像的发布检查

- 完整 `make -j16 V=s` 退出 0；设备元数据、包清单、内核配置检查通过。
- 新镜像内的内核及 `qca8337-nss.ko`、`qca-dwmac-nss.ko` 与已使用的旧镜像逐字节一致；NSS 启动脚本、双链路默认脚本与发布源码一致。
- `check_dma.py`：RA74 默认、显式覆盖、其他设备、参数失败后的 Wi-Fi 恢复通过。
- `check_switch.py --dual-link`：391 个总线/PHY 故障点、2 个分配失败、5 个表/寄存器故障及 4 个错误映射通过，使用 ASan/UBSan。
- `check_defaults.py`：首次启动双链路、关闭 Wi-Fi 卸载、MAC/MTU 保留、重复启动、旧配置保留、无 WAN6 和其他板型控制通过。
- 镜像私人配置/密钥检查通过；新镜像尚未单独刷机，不将离线测试当成实机验收。

## English

### 2026-10-23: ath11k completion fix and PHY fixes

The kernel changes run in my daily RA74 firmware (flashed 2026-10-22 15:53 UTC, settings retained). Prometheus records over the following ~24 hours:

- No reboot, zero OOM kills and no kernel crash archive.
- Hourly maxima of `TX Pending (host path)` stayed at 0–4 on both radios; `TX Completions Skipped (MEC notify)` stayed at 0. Before the fix the same counts reached 1384 (5 GHz) and 322 (2.4 GHz) and memory eventually ran out.
- SUnreclaim stayed at 61–62 MiB. MemAvailable moved between 42 and 146 MiB with traffic and showed no downward trend; at the lows only free pages changed, not cache or slab.
- Clients used both radios; DNS, HTTPS and the per-minute TCP probes worked.

The release image was built from a clean tree (`make -j20 V=s` exited 0) and passed the three offline checks. Its kernel code, device tree and the ath11k, mac80211, QCA8337 and NSS modules are byte-identical to the daily firmware, and its package set equals `v2026.09.14-dual`. This image itself has not separately been flashed. Throughput, NSS isolation and lifecycle tests were not repeated for this section.

### 2026-09-14: dual links

Hardware results below were collected on 2026-09-14 using the daily RA74 system: base `a7cc5b9`, QCA8337 r2, GMAC1 SDRAM fix, and Wi-Fi NSS offload disabled. Dual links were enabled through configuration and one reboot; no DAC candidate was flashed.

Both links reported 1000/full, both NSS interfaces were started with increasing RX, and wired HTTPS worked. WAN port 1 reaches CPU5; LAN ports 2–4 reach CPU6, with VLAN member masks `0x22`/`0x5c`. GMAC0 used default SDRAM; GMAC1 retained explicit SDRAM overrides.

Official Ookla tests measured **913.96/856.39** and **920.73/887.91 Mbps down/up**, each reporting zero loss, with mean router CPU of **7.33%** and **15.31%**. Those download/upload phases were sequential. Two simultaneous speedtest-go clients measured **864.77 down + 670.05 up Mbps** over roughly 10 seconds each. A selected 5.151-second Ethernet counter window averaged **914.74 RX + 756.69 TX = 1671.43 Mbps combined**; it is not the whole-test application average. Clients were bound to Ethernet; USB tethering did not carry the bulk transfer.

The ISP changed the lease/path on reconnection, so cross-day speed differences are not an isolated patch comparison. Sustained simultaneous 1 Gbps each way and long-term stability remain unproven. This dual-link trial included switch readback and offline fault injection, but no new physical WAN-side negative isolation test. Earlier physical isolation tests passed on the single-link NSS setup.

### 2026-09-14 connectivity monitoring

On the earlier daily **single-link** setup, from **13 September 23:40 to 14 September 18:01 CEST** (18 hours 21 minutes), three targets received one TCP/443 probe per minute. Each had **1102/1102 successes**: Cloudflare median/max **20/30 ms**, Google **20/60 ms**, and a private VPS **60/80 ms**. The window contains **3306 successes and no failures, timeouts or connections exceeding one second**.

Earlier at 22:46 CEST on 13 September, one Cloudflare connection took **1.07 seconds** but succeeded; the next minute was normal. Failures during offline setup and deliberate WAN disconnection were separated from normal use. Minute-level probes can miss short interruptions and are not packet-loss tests. These are not long-term dual-link results. Raw logs and NAS history were privately archived; all three fresh probes and monitoring collection passed after enabling dual links.

### 2026-09-14 image release checks

The full `make -j16 V=s` exited zero. Board metadata, package manifest and kernel settings passed inspection. The kernel and both QCA8337/NSS glue modules are byte-identical to the earlier daily image, and embedded NSS startup/dual-link defaults match the published source.

`check_dma.py`, `check_switch.py --dual-link` and `check_defaults.py` passed. Coverage includes descriptor defaults/overrides/failure recovery; 391 bus/PHY fault points, allocation/table faults and malformed VLAN maps with ASan/UBSan; fresh dual-link defaults, host Wi-Fi, MAC/MTU retention, repeat boot, retained settings, absent WAN6 and other-board controls. Image checks found no private network configuration or keys. **The newly packaged image has not separately been flashed; offline checks are not hardware acceptance.**

Public hardware evidence: [dual-link results](https://github.com/kuncy7/openwrt-nss-edma/pull/1#issuecomment-5667765035), [clean-image and monitoring follow-up](https://github.com/kuncy7/openwrt-nss-edma/pull/1#issuecomment-5667148365).
