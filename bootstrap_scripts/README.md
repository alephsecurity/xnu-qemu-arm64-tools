# iOS Kernel Bootstrap Scripts

Those scripts are used to exctract, decode, decompress the needed files to load the iOS kernel on QEMU.

---
- asn1dtredecode.py - *extract the ASN1 encoded device tree:*
```
$ python asn1dtredecode.py encoded_device_tree_input_filename device_tree_output_filename
```
---
- asn1kerneldecode.py - *extract the ASN1 encoded kernel image:*
```
$ python asn1kerneldecode.py encoded_kernel_image_input_filename kernel_image_output_filename
```
---
- decompress_lzss.py - *decompress the ASN1 decoded kernel image:*
```
$ python decompress_lzss.py compressed_decoded_kernel_image_filename kernel_image_output_filename
```
---
- asn1rdskdecode.py - *extract the ASN1 encoded ramdisk image:*
```
$ python asn1rdskdecode.py ramdisk_image_input_filename ramdisk_image_output_filename
```
---
- create_trustcache.py - *given a list of hashes (each of which represents a signed executable),
separated by a new line, create a static trust cache file (binary):*
```
$ python create_trustcache.py list_of_hashes_filename output_tc_filename 
```
---
- kernelcompressedextractmonitor.py - *extract the secure monitor from the compressed kernel image:*
```
$ python kernelcompressedextractmonitor.py compressed_decoded_kernel_image_filename secure_monitor_output_filename
```
