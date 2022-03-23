# Data Collection

### Scrapy Crawler

This is a firmware scraper that aims to download firmware images and associated
metadata from supported device vendor websites. The original version is designed by https://github.com/firmadyne/scraper. The spiders are extended and updated.

#### Dependencies

* [psycopg2](http://initd.org/psycopg/)
* [scrapy](http://scrapy.org/)

#### Usage

To run a specific scraper, e.g. `dlink`:

`scrapy crawl dlink`

To run all scrapers with maximum 4 in parallel, using [GNU Parallel](https://www.gnu.org/software/parallel/):

The scriper is not fully tested when running in parallel. 
```parallel -j 4 scrapy crawl ::: `for i in ./firmware/spiders/*.py; do basename ${i%.*}; done` ```



### Metadata

The ```./metadata``` folder contains the meta data of firmware images used in the paper. The ```json``` files include the download links, firmware categories, release time and etc. 

- [360](luyou.360.cn): 	```/metadata/360.json```
- [AVM](download.avm.de):    ```/metadata/avm.json```
- [belkin](belkin.com):   ```/metadata/belkin.json```
- [buffalo](https://www.buffalotech.com):  ```/metadata/buffalo.json```
- [camius](camius.com):  ```/metadata/camius.json```
- [dlink](dlink.com):      ```/metadata/dlink.json```
- [hikvision](hikvisioneurope.com):  ```/metadata/hikvision.json```
- [linksys](linksys.com):     ```/metadata/linksys.json```
- [mercury](mercurycom.com.cn):   ```/metadata/mercury.json```
- [mikrotik](mikrotik.com):   ```/metadata/mikrotik.json```
- [netcore](netcoretec.com):    ```/metadata/netcore.json```
- [netgear](netgear.com):    ```/metadata/netgear.json`
- [openwrt](downloads.openwrt.org):   ```/metadata/openwrt.json```
- [router-tech](routertech.org):  ```/metadata/routertech.json```
- [supermirco](supermicro.com):  ```/metadata/supermirco.json```
- [Tenda](tendacn.com):    ```/metadata/tenda-zh.json```  ```/metadata/tenda-en.json```
- [tenvis](tenvis.com):    ```/metadata/tenvis.json```
- [tomato-shibby](tomato.groov.pl):    ```/metadata/tomato.json```
- [Tp-link](https://www.tp-link.com):     ```/metadata/tplink-en.json```     ```/metadata/tplink-zh.json```
- [Trendnet](trendnet.com):     ```/metadata/trendnet.json```
- [ubiquiti](ubnt.com):     ```/metadata/ubiquiti.json```
- [ublox](u-blox.com):    ```/metadata/ublox.json```
- [zyxel](zyxel.com):    ```/metadata/zyxel.json```





# Analyzer

### ELF Analyzer

The ELF analyzer takes one file as input to check the mitigations adopted by the ELF binary. We use [Binaryninja](https://binary.ninja/) to disassemble statically-linked binary to verify Stack Canary and Fortify Source. We separate this functionality from ```elf_analyzer.py``` since BinaryNinja is a commercial tool unavailable to general public.

#### Dependencies

* [elftools](https://pypi.org/project/pyelftools/)
* [pwntools](https://docs.pwntools.com/en/stable/)
* [Binaryninja](https://binary.ninja/) (optional)

#### Usage

Run with following command:

```python3 elf_analyzer.py file_path```

The output includes the mitigations adopted by the ELF binary

```c
File name: /bin/ls
Arch: amd64-64
Dynamic linked: Yes
PIE/PIC: Yes
Protected with Canary: Yes
Protected with NX: Yes
Protected with full RELRO
Protected with Fortify Source: Yes
```



To accurately verify Stack Canary & Fortify Source in statically-linked binary, run following command with Binaryninja correctly installed:

```python3 stc_stack.py file_path```



### Kernel Analyzer

The kernel analyzer takes ELF format Linux kernel as input to check the Linux kernel version and the existence of kernel attack mitigations. [vmlinux-to-elf](https://github.com/marin-m/vmlinux-to-elf) can be used to transfer raw format Linux kernel to a fully analyzable ELF file.

#### Dependencies:

* [vmlinux-to-elf](https://github.com/marin-m/vmlinux-to-elf)



#### Usage:

The ```kernel_example``` folder contains a raw format Linux kernel its corresponding recovered ELF format Linux kernel. To check the mitigations, run the example with following:

```bash kernel_analyzer.sh -f kernel_example/elf_kernel```

