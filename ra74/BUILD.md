# 编译 / Building

## 中文

使用 Linux 或 WSL2 Ubuntu，**在 Linux ext4 内编译**，例如 `~/src/redmi-ax5400-nss`。不要在 `/mnt/c`、`/mnt/e` 或 NTFS 上编译。Windows 目录可用于阅读和绑定项目；编译时另行 clone，以保留符号链接和执行权限。

下面以 Ubuntu 24.04 为例。依赖安装后，以普通用户运行共享命令；按内存和 CPU 调整 `-j`。这些步骤只下载、编译，不会连接或刷写路由器。

## English

Use Linux or WSL2 Ubuntu, and **build on Linux ext4**, for example `~/src/redmi-ax5400-nss`. Do not build on `/mnt/c`, `/mnt/e` or NTFS. A Windows checkout is useful for browsing/project binding; clone separately inside Linux to preserve symlinks and executable bits.

The example targets Ubuntu 24.04. After installing dependencies, run the shared commands as a regular user and adjust parallelism for your RAM/CPU. These commands download and build; they do not contact or flash the router.

```sh
sudo apt update
sudo apt install build-essential clang flex bison g++ gawk gcc-multilib \
  g++-multilib gettext git libncurses-dev libssl-dev python3 python3-setuptools \
  rsync swig unzip zlib1g-dev file wget curl zstd

mkdir -p ~/src
cd ~/src
git clone --branch v2026.10.23-ath11k https://github.com/Yongzhaooo/redmi-ax5400-nss.git
cd redmi-ax5400-nss
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cp ra74/feeds.conf feeds.conf
./scripts/feeds update -a
./scripts/feeds install -a
# Avoid the known Kconfig cycles in these feed revisions.
./scripts/feeds uninstall librespeed-cli librespeed-cli-rust luci-app-librespeed
cp ra74/build.config .config
make defconfig
python3 ra74/tests/check_dma.py .
python3 ra74/tests/check_switch.py . --dual-link
python3 ra74/tests/check_defaults.py .
make -j"$(nproc)" download
make -j"$(nproc)" V=s
```

## 中文：输出与复现

产物位于 `bin/targets/qualcommax/ipq50xx/`，目标应为 `xiaomi_redmi-ax5400`。保留配置、manifest 和 SHA256。确认 `make defconfig` 无递归依赖错误；可选包缺失警告不能代替检查实际选择的依赖和最终退出码。

[feeds.conf](feeds.conf) 锁定六个 feed 的提交，替代原本本机路径的 NSS `src-link`。[source.patch](source.patch) 是原已实测驱动差异，已包含在主源码中，**不要重复应用**；双链路默认值和 2026-10-23 的 ath11k、PHY 补丁是其上的额外修改，见版本来源。

Release 使用已有 Linux 构建缓存运行完整 `make -j16 V=s`，不含 DAC 候选。空缓存便携流程未再次完整执行。独立仓库版本字符串、时间戳和新生成的签名密钥可能改变二进制，不承诺逐字节复现 Release 哈希。继承的 GitHub Actions 暂未启用，不提供自动更新承诺。

## English: output and reproducibility

Output is under `bin/targets/qualcommax/ipq50xx/`; the device must be `xiaomi_redmi-ax5400`. Retain the configuration, manifest and SHA256. Check for recursive dependency errors in `make defconfig`; warnings about optional packages do not replace checking selected dependencies and the final exit code.

[feeds.conf](feeds.conf) pins all six feeds and replaces the machine-local NSS `src-link`. [source.patch](source.patch) records the original tested driver changes and is **already applied**. Dual-link defaults and the 2026-10-23 ath11k and PHY patches are additional changes on top; see provenance.

The release uses the existing Linux build cache with a full `make -j16 V=s`, excluding the DAC candidate. The portable empty-cache procedure has not been rerun end to end. Repository version strings, timestamps and newly generated signing keys may change binaries, so bit-for-bit reproduction of the release hash is not promised. Inherited GitHub Actions are currently disabled; automatic updates are not provided.

## 中文：默认开启 Wi-Fi NSS 卸载（可选）

发布镜像让 RA74 的 Wi-Fi 走主机路径。开启 Wi-Fi NSS 卸载后，Wi-Fi 与有线之间的吞吐从约 690 Mbps 提高到 900–945 Mbps，代价是约 44 MiB 内存，测试范围见[实测结果](VALIDATION.md)。想让自编镜像首次迁移时就开启，在 `make defconfig` 之后、运行测试之前改两处默认值和一处测试期望：

```sh
D=package/nss/nss-tools/files/nss-dwmac.defaults
sed -i "/xiaomi,redmi-ax5400)/,/;;/ s/wifi_offload='0'/wifi_offload='1'/" "$D"
sed -i "/redmi-ax5400' ] || uci set nss.general.wifi_offload='0'/d" "$D"
sed -i "s/'nss.general.wifi_offload': '0', 'nss.general.topology'/'nss.general.wifi_offload': '1', 'nss.general.topology'/" ra74/tests/check_defaults.py
git diff --stat   # 应只有这两个文件变化
python3 ra74/tests/check_defaults.py .
```

这些默认值只在首次迁移到双链路时写入。保留配置升级时，脚本发现已有 `nss.general.topology` 就直接退出，原有的 `wifi_offload` 不变。已在用的设备不需要重新编译，运行 `uci set nss.general.wifi_offload=1 && uci commit nss && reboot` 即可；改回 0 同样需要重启。

## English: Wi-Fi NSS offload on by default (optional)

The released image keeps RA74 Wi-Fi on the host path. With Wi-Fi NSS offload on, Wi-Fi to wired throughput rose from about 690 Mbps to 900–945 Mbps at a cost of about 44 MiB of memory; see [Validation](VALIDATION.md) for the test scope. To have your own image enable it on first migration, change two defaults and one test expectation after `make defconfig` and before running the tests:

```sh
D=package/nss/nss-tools/files/nss-dwmac.defaults
sed -i "/xiaomi,redmi-ax5400)/,/;;/ s/wifi_offload='0'/wifi_offload='1'/" "$D"
sed -i "/redmi-ax5400' ] || uci set nss.general.wifi_offload='0'/d" "$D"
sed -i "s/'nss.general.wifi_offload': '0', 'nss.general.topology'/'nss.general.wifi_offload': '1', 'nss.general.topology'/" ra74/tests/check_defaults.py
git diff --stat   # only these two files should change
python3 ra74/tests/check_defaults.py .
```

These defaults are written only on the first migration to dual links. On an upgrade that keeps settings, the script exits as soon as it finds `nss.general.topology`, so an existing `wifi_offload` stays as it was. A device already in use needs no rebuild: run `uci set nss.general.wifi_offload=1 && uci commit nss && reboot`. Switching back to 0 also needs a reboot.
