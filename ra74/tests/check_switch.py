#!/usr/bin/env python3
"""Host fault-injection check of the actual patched driver (not a hardware test).

Usage: python3 check_switch.py /path/to/openwrt [--dual-link]
Requires a native C compiler. Temporary files stay outside the source tree.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

shim = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;
typedef uint16_t u16;
typedef uint8_t u8;
#define BIT(n) (1U << (n))
#define GENMASK(h,l) ((~0U << (l)) & (~0U >> (31-(h))))
#define FIELD_PREP(mask,val) (((u32)(val) << __builtin_ctz(mask)) & (mask))
#define module_param(...)
#define MODULE_PARM_DESC(...)
#define MODULE_LICENSE(...)
#define MODULE_DESCRIPTION(...)
#define module_init(...)
#define module_exit(...)
#define __init
#define __exit
#define GFP_KERNEL 0
#define pr_info(...) ((void)0)
#define pr_warn(...) ((void)0)
#define pr_err(...) ((void)0)
#define usleep_range(...) ((void)0)
#define MII_BMCR 0
#define BMCR_PDOWN BIT(11)
#define BMCR_ANENABLE BIT(12)
#define BMCR_ANRESTART BIT(9)
struct mii_bus { int unused; };
struct device { int unused; };
struct phy_device { struct { struct mii_bus *bus; } mdio; };
static struct mii_bus fake_bus;
static struct device fake_device;
static struct phy_device fake_phy = { .mdio = { .bus = &fake_bus } };
static int mdio_bus_type;
static int fail_at, operations, alloc_fail, allocations, unsafe_enable;
static int stuck_vtu, full_vtu, stuck_atu, drop_lookup, drop_vtu;
static u16 words[4096], page;
static u32 vtu[4096];
static u32 reg32(unsigned reg) { return words[reg/2] | ((u32)words[reg/2+1]<<16); }
static void set32(unsigned reg,u32 value) { words[reg/2]=value; words[reg/2+1]=value>>16; }
static int fault(void) { return ++operations == fail_at; }
static bool policy_ready(void) {
    const unsigned expected[7]={0,0x140340,0x140358,0x140354,0x14034c,0,0x14031e};
    for(int p=0;p<7;p++) if(reg32(0x660+p*12)!=expected[p]) return false;
    if(!(vtu[1] & BIT(20)) || !(vtu[2] & BIT(20))) return false;
    for(int p=1;p<=4;p++) if((reg32(0x420+p*8)&4095)!=(p==1?2:1)) return false;
    for(int p=0;p<7;p++) {
        unsigned a=(vtu[1]>>(4+2*p))&3, b=(vtu[2]>>(4+2*p))&3;
        if(a!=(p==6?2:(p>=2&&p<=4?1:3))) return false;
        if(b!=(p==6?2:(p==1?1:3))) return false;
    }
    return true;
}
static int mdiobus_write(struct mii_bus *bus,int phy,int r,u16 value) {
    (void)bus;
    if(fault()) return -EIO;
    if(phy==0x18 && r==0) { page=value; return 0; }
    unsigned addr=((unsigned)page<<9)|((phy&7)<<6)|(r<<1);
    if(drop_lookup && addr==0x66c && (value&0x7f)) return 0;
    assert(addr/2<4096); words[addr/2]=value;
    if(addr>=0x7c && addr<=0x94 && (addr-0x7c)%4==0 && (value&12))
        if(!policy_ready()) unsafe_enable++;
    /* Automatic link state can clear RX/TX on an unplugged external port. */
    if(addr>=0x7c && addr<=0x94 && (addr-0x7c)%4==0 && (value&BIT(9)))
        words[addr/2]&=~12;
    if(addr==0x616 && (reg32(0x614)&BIT(31))) {
        u32 command=reg32(0x614);
        unsigned vid=(command>>16)&4095;
        if((command&7)==2) {
            if(!drop_vtu) vtu[vid]=reg32(0x610);
            set32(0x610,0);
        } else if((command&7)==6) set32(0x610,vtu[vid]);
        if(!stuck_vtu) set32(0x614,(command&~BIT(31))|(full_vtu?BIT(4):0));
    }
    if(addr==0x60e && !stuck_atu) set32(0x60c,reg32(0x60c)&~BIT(31));
    return 0;
}
static int mdiobus_read(struct mii_bus *bus,int phy,int r) {
    (void)bus;
    if(fault()) return -EIO;
    unsigned addr=((unsigned)page<<9)|((phy&7)<<6)|(r<<1);
    assert(addr/2<4096); return words[addr/2];
}
static struct device *bus_find_device_by_name(void *a,void *b,const char *c) {
    (void)a;(void)b;(void)c;return &fake_device;
}
static struct phy_device *to_phy_device(struct device *d) { (void)d;return &fake_phy; }
static void put_device(struct device *d) { (void)d; }
static int phy_read(struct phy_device *p,int reg) { (void)p;(void)reg;return fault()?-EIO:0; }
static int phy_write(struct phy_device *p,int reg,int val) { (void)p;(void)reg;(void)val;return fault()?-EIO:0; }
static char *kstrdup(const char *s,int flags) { (void)flags;return ++allocations==alloc_fail?NULL:strdup(s); }
#define kfree free
static int kstrtouint(const char *s,unsigned base,unsigned *result) {
    char *end;errno=0;unsigned long value=strtoul(s,&end,base);
    if(errno || end==s || *end || value>UINT32_MAX) return -EINVAL;
    *result=value;return 0;
}
'''

test = r'''
static void reset(void) {
    memset(words,0,sizeof(words));memset(vtu,0,sizeof(vtu));
    fail_at=operations=alloc_fail=allocations=unsafe_enable=g8_error=page=0;
    stuck_vtu=full_vtu=stuck_atu=drop_lookup=drop_vtu=0;
    ports=0x5e;cpu_port=6;switch_fixup=true;
    vlans="1:6t,2u,3u,4u;2:6t,1u";
    wake_phys="90000.mdio-1:00,90000.mdio-1:01,90000.mdio-1:02,90000.mdio-1:03";
}
static void assert_blocked(void) {
    for(int p=0;p<7;p++) {
        assert(!(reg32(G8_PORT_STATUS(p))&(12|BIT(9))));
        assert(!(reg32(G8_PORT_LOOKUP(p))&0x7007f));
    }
}
int main(void) {
    reset();assert(qca8337_nss_init()==0);assert(policy_ready());assert(!unsafe_enable);
    int count=operations;
    assert(!(reg32(G8_PORT_STATUS(0))&12));assert(!(reg32(G8_PORT_STATUS(5))&12));
    for(int n=1;n<=count;n++) {
        reset();fail_at=n;
        assert(qca8337_nss_init()<0);assert(!unsafe_enable);assert_blocked();
    }
    for(int n=1;n<=2;n++) {
        reset();alloc_fail=n;assert(qca8337_nss_init()<0);assert(!unsafe_enable);assert_blocked();
    }
    int *hardware_faults[]={&stuck_vtu,&full_vtu,&stuck_atu,&drop_lookup,&drop_vtu};
    for(unsigned n=0;n<sizeof(hardware_faults)/sizeof(hardware_faults[0]);n++) {
        reset();*hardware_faults[n]=1;
        assert(qca8337_nss_init()<0);assert(!unsafe_enable);assert_blocked();
    }
    const char *bad[]={"","1:6t,2u","1:6t,2u,3u,4u;2:6t,7u","4095:6t,1u"};
    for(unsigned n=0;n<sizeof(bad)/sizeof(bad[0]);n++) {
        reset();vlans=(char *)bad[n];assert(qca8337_nss_init()<0);assert(!unsafe_enable);assert_blocked();
    }
    printf("PASS: RA74 map with unplugged ports, disabled ports, %d single MDIO/PHY faults, 2 allocation failures, 5 table/register faults, 4 malformed maps\n",count);
    return 0;
}
'''

tree = Path(sys.argv[1]).resolve()
dual = '--dual-link' in sys.argv[2:]
if dual:
    shim = shim.replace(
        '{0,0x140340,0x140358,0x140354,0x14034c,0,0x14031e}',
        '{0,0x140320,0x140358,0x140354,0x14034c,0x140302,0x14031c}')
    shim = shim.replace('if(b!=(p==6?2:', 'if(b!=(p==5?2:')
    test = test.replace('ports=0x5e;', 'ports=0x7e;')
    test = test.replace(';2:6t,1u', ';2:5t,1u')
    test = test.replace('90000.mdio-1:03";', '90000.mdio-1:03,90000.mdio-1:04";')
    test = test.replace('assert(!(reg32(G8_PORT_STATUS(5))&12));',
                        'assert(reg32(G8_PORT_STATUS(5))&BIT(9));')
    print('Checking dual link: WAN1↔CPU5, LAN2/3/4↔CPU6', flush=True)
source = (tree/'package/kernel/qca8337-nss/src/qca8337_nss.c').read_text(encoding='utf-8')
source = '\n'.join(line for line in source.splitlines() if not line.startswith('#include <linux/'))
with tempfile.TemporaryDirectory(prefix='ra74-switch-check-') as directory:
    cfile=Path(directory)/'check.c'
    binary=Path(directory)/'check'
    cfile.write_text(shim+'\n'+source+'\n'+test,encoding='utf-8')
    subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-g',str(cfile),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
    init=(tree/'package/nss/nss-tools/files/nss-dwmac.init').read_text(encoding='utf-8')
    init=init.replace('. /lib/functions.sh', ':').replace('. /lib/nss/functions.sh', ':')
    shell_test=r'''
calls="$1"
uci() {
    case "$*" in
        *nss.general.fabric) echo qca8337 ;;
        *nss.general.switch_dev) echo nonexistent-ra74-test-device ;;
        *nss.general.vtu) echo '1:6t,2u,3u,4u;2:6t,1u' ;;
        *nss.general.switch_args) echo 'cpu_port=6 ports=0x5e' ;;
    esac
}
insmod() { printf 'insmod %s\n' "$*" >> "$calls"; return 1; }
modprobe() { echo unexpected-modprobe >> "$calls"; return 1; }
logger() { :; }
wifi_load() { echo "wifi $1" >> "$calls"; }
if start_service; then echo 'ERROR: switch failure was ignored'; exit 1; fi
grep -q 'vlans=1:6t,2u,3u,4u;2:6t,1u cpu_port=6 ports=0x5e' "$calls" || exit 1
grep -qx 'wifi 0' "$calls" || exit 1
if grep -q unexpected-modprobe "$calls"; then exit 1; fi
echo 'PASS: service propagates switch failure, preserves board arguments, no parameter-losing retry'
'''
    subprocess.run(['sh','-s','--',str(Path(directory)/'calls')],input=init+'\n'+shell_test,text=True,check=True)
