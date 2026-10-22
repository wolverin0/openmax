"""Host C integration. ALL proc/time/stop/priority calls are replaced by fakes.

No target binary, network, real /proc probe, workload or shared service is used.
The disposable compiler/executable live only in a local WSL tempfile directory.
"""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from controller.distributed_compute import simulate_c_worker_kernel

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
#define _XOPEN_SOURCE 600
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static const char *scenario;
static uint64_t ticks;
static int fake_open(const char *p, int flags, ...) {
 (void)flags;
 if (!strcmp(p,"/proc/meminfo")) return 101;
 if (!strcmp(p,"/proc/net/dev")) return 102;
 errno=EPERM; return -1;
}
static ssize_t fake_read(int fd, void *p, size_t n) {
 const char *text;
 char long_mem[2048];
 if ((fd==101 && !strcmp(scenario,"memfail")) ||
     (fd==102 && !strcmp(scenario,"netfail"))) {errno=EIO;return -1;}
 text=fd==101 ? "MemFree: 20000 kB\nBuffers: 0 kB\nCached: 1000 kB\nShmem: 0 kB\n" :
 "Inter-| Receive | Transmit\n face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed\n eth0: 100 1 0 0 0 0 0 0 200 2 0 0 0 0 0 0\n";
 if (fd==102 && !strcmp(scenario,"nointerface")) text=" lo: 100 1 0 0 0 0 0 0 200 1 0 0 0 0 0 0\n";
 if(fd==101 && (!strcmp(scenario,"memlong") || !strcmp(scenario,"memincomplete"))) {
  memset(long_mem,'X',sizeof(long_mem));
  const char *head=!strcmp(scenario,"memlong") ? text :
   "MemFree: 20000 kB\nBuffers: 0 kB\nCached: 1000 kB\n";
  memcpy(long_mem,head,strlen(head));long_mem[sizeof(long_mem)-1]=0;text=long_mem;
 }
 size_t len=strlen(text);if(len>n)len=n;memcpy(p,text,len);return (ssize_t)len;
}
static int fake_close(int fd) {(void)fd;return 0;}
static int fake_access(const char *p,int mode) {(void)p;(void)mode;errno=ENOENT;return -1;}
static int fake_nice(int n) {(void)n;return 0;}
static int fake_clock(clockid_t c,struct timespec *t) {
 (void)c;if(!strcmp(scenario,"clockfail")){errno=EIO;return -1;}
 ticks+=20000;t->tv_sec=ticks/1000000000;t->tv_nsec=ticks%1000000000;return 0;
}
static int fake_sleep(const struct timespec *r,struct timespec *rem) {
 (void)rem;ticks+=(uint64_t)r->tv_sec*1000000000+r->tv_nsec;return 0;
}
#define open fake_open
#define read fake_read
#define close fake_close
#define access fake_access
#define nice fake_nice
#define clock_gettime fake_clock
#define nanosleep fake_sleep
#define main worker_main
#include "WORKER_SOURCE"
#undef main
int main(int argc,char **argv) {
 if(argc<2)return 99;
 scenario=argv[1];
 if(!strcmp(scenario,"kernel")) {
  if(argc!=5)return 98;
  uint32_t op=strtoul(argv[2],0,10),s=strtoul(argv[3],0,10);
  uint32_t a=op==2?2166136261U:0;
  run_kernel_step(op,&s,&a,strtoul(argv[4],0,10));
  printf("{\"rng\":%u,\"accum\":%u}\n",s,a);return 0;
 }
 return worker_main(argc-1,argv+1);
}
'''


@pytest.fixture(scope='module')
def c_results():
    if not shutil.which('wsl.exe'):
        pytest.skip('Local C fixture requires existing WSL/gcc; no install attempted')
    worker = str(ROOT / 'controller/fmx_micro_worker.c')
    worker = '/mnt/' + worker[0].lower() + worker[2:].replace('\\', '/')
    source = HARNESS.replace('WORKER_SOURCE', worker)
    cases = {name: [name, '1', '12345', '1000000', '5', '90', '64']
             for name in ('memfail', 'netfail', 'nointerface', 'clockfail', 'memlong', 'memincomplete')}
    cases.update({
        'junk': ['ok', '1junk', '1', '1', '5', '90', '64'],
        'wrap': ['ok', '1', '4294967297', '1', '5', '90', '64'],
        'ttlzero': ['ok', '1', '1', '1', '5', '0', '64'],
        'dutyzero': ['ok', '1', '1', '1', '0', '90', '64'],
        'negative': ['ok', '1', '-1', '1', '5', '90', '64'],
    })
    # Exact historical shard inputs; comparison below is numeric only.
    cases.update({f'kernel{op}': ['kernel', str(op), str(seed), str(n)]
                  for op, seed, n in [(1, 12345, 400000), (2, 67890, 800000), (3, 77, 4096)]})
    script = f'''
import tempfile,pathlib,subprocess,json
source={source!r}
cases={cases!r}
with tempfile.TemporaryDirectory(prefix="fmx-worker-fixture-") as d:
 p=pathlib.Path(d);(p/'h.c').write_text(source)
 c=subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(p/'h.c'),'-o',str(p/'worker')],capture_output=True,text=True)
 if c.returncode: print(c.stderr);raise SystemExit(c.returncode)
 results={{}}
 for k,args in cases.items():
  r=subprocess.run([str(p/'worker')]+args,capture_output=True,text=True,timeout=5)
  results[k]={{'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}}
 print(json.dumps(results))
'''
    result = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--exec', 'python3', '-'],
                            input=script, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr + result.stdout
    return json.loads(result.stdout)


@pytest.mark.parametrize('case', ['junk', 'wrap', 'ttlzero', 'dutyzero', 'negative'])
def test_c_rejects_malformed_or_out_of_range_cli(c_results, case):
    assert c_results[case]['exit_code'] == 64


@pytest.mark.parametrize('case', ['memfail', 'netfail', 'nointerface', 'clockfail'])
def test_c_missing_safety_telemetry_never_completes_work(c_results, case):
    assert c_results[case]['exit_code'] != 0
    assert '"status":"OK"' not in c_results[case]['stdout']


def test_complete_required_meminfo_prefix_can_exceed_read_buffer(c_results):
    assert c_results['memlong']['exit_code'] == 0
    assert '"status":"OK"' in c_results['memlong']['stdout']
    assert c_results['memincomplete']['exit_code'] != 0


@pytest.mark.parametrize('op,seed,n', [(1, 12345, 400000), (2, 67890, 800000), (3, 77, 4096)])
def test_actual_c_kernels_match_python(c_results, op, seed, n):
    row = c_results[f'kernel{op}']
    assert row['exit_code'] == 0
    output = json.loads(row['stdout'])
    rng, accum = simulate_c_worker_kernel(op, seed, n)
    assert output == {'rng': rng, 'accum': accum}
