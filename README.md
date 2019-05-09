[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg)](code-of-conduct.md) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Xbypass #
# A tool to facilitate ROP Chain Development for XML Character Sanitization #

## Authors 
Douglas McKee: [@fulmetalpackets](https://twitter.com/fulmetalpackets)</br>
Charles McFarland: [@CGMcFarland](https://twitter.com/CGMcFarland)


## Table of Contents

* [Xbypass](#xbypass)
* [Why is McAfe Releasing this Tool?](#why-is-mcafee-releasing-this-tool)
* [Quick Start](#quick-start)
* [Output](#output)
* [FAQ](#faq)
* [Acknowledgements](#acknowledgements)
* [License](#license)

## System Requirements

* Python 2.7
* The Python module, [Ropper](https://github.com/sashs/Ropper)

## Xbypass

Xbypass is a vulnerability research tool that assists in discovering ROP gadgets and valid byte address combinations to bypass XML character input constraints. The tool was developed to automate portions of ROP-chain creation to facilitate the bypass of XML sanitization, where gadgets supplied must not contain any non-printable bytes. The user supplies a target address and list of binaries with associated address ranges. A target address is an address of a function which an attacker would like to execute. For example, it is common for exploit writers to want to execute "system" within "libc", therefore the target address would be the location of "system" within "libc". The address ranges represent executable memory for each shared library loaded into memory. Gadgets are instructions, of an arbitrary starting location, that typically end in a jump or return instruction. If the researcher controls a resource such as the stack, they can use the instructions in a gadget to direct execution to an address of their choosing. Specifically, Xbypass finds addition and subtraction instructions as these are very common and enable addresses that will pass XML input sanitization checks. If the target address includes a bad byte, (a byte that is not allowed by the XML filter), we can submit two addresses, which are subsequently added or subtracted to the target address and can get through the character filter. Xbypass will output these addition and subtraction gadgets, discovered in the supplied binaries, as well as operand pairs that can be used to reach a target address. These operand pairs will only consist of valid bytes that can pass through common XML filters.

This tool has two main contributions to the research community.

* Multi architecture support including MIPS, ARM and x86. 
* Whitelist approach to Bad Byte handling to specifically account for common XML sanitization.

## Why is McAfee Releasing this tool

McAfee Advanced Threat Research (ATR) wants to empower software developers to build and deliver products with minimal exploitable vulnerabilities.  The release of this tool will make it easier for software developers to identify and validate exploitability of XML sanitized vulnerabilities prior to release of their products, software or technologies. Additionally, this tool can be utilized by security researchers to identify, assess and automate the process of vulnerability discovery and exploitation, with the ultimate goal of bringing awareness and visibility to the importance and impact of secure development processes. This will effectively raise the bar on security standards for the industry and dramatically reduce the effectiveness of bad actors.

## Quick Start

For difficulties installing Ropper see the related [Ropper question](#why-is-ropper-failing-to-install) in the FAQ

### Installation

Xbypass does not require installation. Simply clone the directory to your desired location and run Xbypass from the <b>xbypass/tools</b> folder

```console
$ git clone https://github.com/advanced-threat-research/xbypass
$ cd xbypass/tools
```

It is highly recommended to use a virtual environment such as virtualenv, especially if the normal pip installation for Ropper breaks.

To create a virtual environment for Xbypass run the following in the <b>xbypass/</b> folder:

```console
$ pip install virutalenv
$ virtualenv -p python xbypass_venv
$ source xbypass_venv/bin/activate
```

To deactivate the virtual environment run the following:

```console
$ deactivate
```

### Running Unit Tests

Unit tests cover the functionality of operand calculations.  All unit testing can be executed with a single Python command.  The tests can be found in the <b>test/</b> folder which allows for automated discovery of the tests from the <b>xbypass/</b> folder.

From the <b>xbypass</b> folder:

```console
 $ python -m unittest discover -v  
 ```

### Prerequisite Information

The researcher needs the following information to be identified before using Xbypass:

* Which binaries to scan
* What is the architecture of the binaries
* What is the memory address range of each library loaded (start/end address)
* The target address of the function to execute with the exploit


### Binary Files

Ensure you have your binary file directories accessible to the Xbypass project. The examples shown here were run from the <b>lib/</b> folder in the Xbypass project.

### Creating a Config File

Use __example.config__ to help create your own config file. A config file is a JSON formatted file that has the following:

* Target Address - The target address you wish to redirect execution to, such as an address of "system" in libc.
* List of executable memory locations - Contains a list of libraries to search in for gadgets


### Example Config File
```console
{
    "targetAddress": ["0x2AD1e4F4"],
    "executableMemory" : [
        {
            "name":"libpthread-0.9.33.2.so",
            "path": "libs/libpthread-0.9.33.2.so",
            "baseAddress": "0x2ad14000",
            "endAddress": "0x2ad27000",
            "arch":"MIPS"
        }
   ]

}
```

### Running Xbypass

If you have your binaries in place and the config file properly created, running Xbypass is a single Python command with one parameter.

```console
$ python Xbypass.py [config file]   
 ```

## Output

You can view within the console the number of usable gadgets found by Xbypass. Details of the discoveries are provided in the <b>output/</b> folder. There may be three files per binary listed in the config file.

* [name]\_Xbypass.txt - Includes a list of all gadgets
* [name]\_sub_gadgets.txt - Includes a list of subtraction gadgets
* [name]\_add_gadgets.txt - Includes a list of addition gadgets
* [address]\_operands.txt - This will include addresses with valid bytes that add or subtract to the target address

### Example output

#### binary\_Xbypass.txt
```console
Usable Gadgets: 101
----------------
----------------
0x2a0a5667: addiu $a0, $a0, -0x3e10
0x2a0a566b: move $a1, $s1
0x2a0a5669: jalr $t9
0x2a0a5673: addiu $a2, $zero, 0x14

----------------------------------
0x2a0d4d3b: jalr $t9
0x2a0d4d39: subu $a2, $v0, $s2

.
.
.
```

#### binary\_xbypass\_add\_gadgets.txt
```console
Usable Gadgets: 42
----------------
----------------
0x2a0a5667: addiu $a0, $a0, -0x3e10
0x2a0a566b: move $a1, $s1
0x2a0a5669: jalr $t9
0x2a0a5673: addiu $a2, $zero, 0x14

----------------------------------
0x2b096378: addiu $a0, $a0, 1
0x2b09637c: lw $t9, -0x76d8($gp)
0x2b096380: jalr $t9
0x2b096384: lw $a0, 0x24($sp)
.
.
.
```

#### binary\_xbypass\_sub\_gadgets.txt
```console
Usable Gadgets: 7
----------------
----------------
0x2a0d4d37: addiu $a1, $zero, 0x3d
0x2a0d4d3b: jalr $t9
0x2a0d4d39: subu $a2, $v0, $s2

----------------------------------
0x2a0d4d3b: jalr $t9
0x2a0d4d39: subu $a2, $v0, $s2

.
.
.
```

#### 0x2ad1e4f4\_operands.txt
```console
Target Name: 
Target Address: 0x2ad1e4f4
Addition operands:
0x09526575 0x217f7f7f
Subtraction operands:
0x34090920 0x0937242c
```


## FAQ

* [How do I install Xbypass?](#how-do-i-install-xbypass)
* [Which architectures does Xbypass support?](#which-architectures-does-xbypass-support)
* [Where do I find the usable gadgets after running Xbypass?](#where-do-i-find-the-usable-gadgets-after-running-xbypass)
* [Where do I find the usable operands after running Xbypass?](#where-do-i-find-the-usable-operands-after-running-xbypass)
* [What if Xbypass does not return any gadgets?](#what-if-xbypass-does-not-return-any-gadgets)
* [What if Xbypass does not return an operands file?](#what-if-xbypass-does-not-return-an-operands-file)
* [What are the bytes that are assumed to be valid?](#what-are-the-bytes-that-are-assumed-to-be-valid)
* [What do I do after Xbypass returns usable operands?](#what-do-i-do-after-xbypass-returns-usable-operands)
* [Why is Ropper failing to install?](#why-is-ropper-failing-to-install)


### How do I install Xbypass

<p style=margin-left:5em;>Xbypass does not need to be installed. You simply need to meet the prerequisites including having the Ropper module installed. Once you download Xbypass you can run it from the <b>Xbypass/tools</b> folder.</p>

### Which architectures does Xbypass support

<p style=margin-left:5em;>Xbypass works with the following architectures:</p>
<p style=margin-left:5em;>x86, x86_64, MIPS, MIPS64, ARM, ARMTHUMB, ARM64, PPC, PPC64</p>

### Where do I find the usable gadgets after running Xbypass

<p style=margin-left:5em;>The ouput of Xbypass can be found in <b>tools/output</b>. You will have 3 files that include gadget information: <i>[binary name]</i>_Xbypass.txt, <i>[binary name]</i>_sub_gadgets.txt, <i>[binary_name]</i>_add_gadgets.txt.</br><br>
These will include all gadgets as well as the subset of subtraction gadgets and addition gadgets. 
</p>

### Where do I find the usable operands after running Xbypass

<p style=margin-left:5em;>The ouput of Xbypass can be found in <b>tools/output</b>. You will have 1 file that includes both the add and sub operands, if they exists, to use for the target address: <i>[target address]</i>_operands.txt</p>

### What if Xbypass does not return any gadgets

<p style=margin-left:5em;>This means there are no gadgets in the address range specified. Ensure that you have specified a valid range of executable memory. If you have, then consider moving to other exploitation techniques besides ROP.
</p>

### What if Xbypass does not return an operands file

<p style=margin-left:5em;>Unfortunately, that means the tool was unable to locate an add or sub operand pair that results in the target address. This could be due to a single bit difference in the target address or the target falling into an address space that is unreachable given an XML filter. The search is exhaustive. If you have flexibility, consider using a different target address.</p>

### What are the bytes that are assumed to be valid

<p style=margin-left:5em;>The list of good bytes assumed to pass through XML sanitization can be found in <b>xmlChecker_out.xml</b>. These are the bytes commonly found in XML filter packages.</p>

### What do I do after Xbypass returns usable operands

<p style=margin-left:5em;>You can use these operands as part of a ROP chain. It's up to the researcher to construct the ROP chain from the gadgets found by Xbypass and use either an add or subtract gadget to utilize the operands.</p>

### Why is Ropper failing to install  
```console 
ERROR: Command "python setup.py egg_info" failed with error code 1 in [path]/filebytes/
```

<p style=margin-left:5em;>One of the dependencies of Ropper may not install with the normal Pip installation process. Either Ropper or that dependency will need to be addressed. In the meantime, the following installation steps should work around the issue. It is highly recommended to use a virtual environment.</p>

<p style=margin-left:5em;>Using your Xbypass virtual environment:<p>

```console
$ pip install pathlib
$ git clone https://github.com/sashs/filebytes
$ cd filebytes
$ pip install ropper 
```

<p style=margin-left:5em;>At this point you need to edit <b>setup.py</b> to remove the offending code. We can resolve the issue by hardcoding the version number of filebytes into its <b>setup.py</b> file. You can find the current version number on the last line of <b>filebytes/__init__.py.</b> Copy this version and replace the current variable assignment with the hardcoded number.</p>

<b>setup.py</b>

<p style=margin-left:5em;>Remove: version = extractMetaInfo((currentDir / "filebytes" / "__init__.py").read_text())["VERSION"]</br>
Replace with: version = '0.9.20'</p>

```python
#version = extractMetaInfo((currentDir / "filebytes" / "__init__.py").read_text())["VERSION"]
version = '0.9.20'
```

<p style=margin-left:5em;>Now install filebytes by running <b>setup.py</b> followed by a pip install of Ropper.</p>

```console
$ python setup.py install
$ pip install ropper 
```
## Code of Conduct

In an effort to maintain a healthy environment for the community we have assumed the Contributor Covenant Code of Conduct 1.4.1. All contributors are expected to evaluate their actions against our Code of Conduct. The Code of Conduct can be found in the [code-of-conduct.md](code-of-conduct.md) file of this project.

## Acknowledgements

### Ropper

Ropper, is an open source tool found at https://github.com/sashs/Ropper. It was created by the user Sascha Schirra who, at the time of this writing, released the tool under the BSD-3-Clause License found at https://github.com/sashs/Ropper/blob/master/COPYING. 

### Filebytes

Filebytes is a dependency of Ropper. It is an open source tool found at https://github.com/sashs/filebytes. It was created by the user Sascha Schirra who, at the time of this writing, released to tool under the BSD-3-Clause License found at https://github.com/sashs/filebytes/blob/master/COPYING.

## License

Copyright 2019 McAfee, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.