from __future__ import print_function
import sys
import libvirt

xmlconfig = "<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'> <name>tenjint_firse</name>  <uuid>c7a5fdbd-edaf-9455-926a-d65c16db1809</uuid>  <memory>5000000</memory> <vcpu>1</vcpu> <os><type arch='x86_64' machine ='pc-i440fx-4.2'>hvm</type></os><clock offset='utc'/>  <on_poweroff>destroy</on_poweroff>  <on_reboot>restart</on_reboot>  <on_crash>destroy</on_crash>  <devices>    <emulator>/home/dell/Documents/opensource/tenjint/qemu/x86_64-softmmu/qemu-system-x86_64</emulator>    <disk type='file' device='disk'>      <source file='/home/dell/Downloads/ub.qcow2'/>      <driver name='qemu' type='qcow2'/>      <target dev='hda'/> </disk> <input type='mouse' bus='ps2'/><graphics type='vnc' port='-1'/></devices> <qemu:commandline><qemu:arg value='-L' /><qemu:arg value='/usr/share/seabios' /></qemu:commandline></domain>"

conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

dom = conn.defineXML(xmlconfig)
if dom == None:
    print('Failed to define a domain from an XML definition.', file=sys.stderr)
    exit(1)

if dom.create() < 0:
    print('Can not boot guest domain.', file=sys.stderr)
    exit(1)

print('Guest '+dom.name()+' has booted', file=sys.stderr)

conn.close()
exit(0)