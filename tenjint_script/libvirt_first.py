from __future__ import print_function
import sys
import libvirt
from datetime import datetime
import uuid
import subprocess


vmi_config_path = sys.argv[1]
domain_name = sys.argv[2]
unique_snapshot_path = sys.argv[3]
#unique_snapshot_name = sys.argv[7]
domain_uuid = uuid.uuid4()
emulator_path = sys.argv[4]
source_file_qcow2 = sys.argv[5]

process = subprocess.Popen(['qemu-img', 'create', '-f', 'qcow2', '-b', source_file_qcow2, unique_snapshot_path],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
print(stdout)

xmlconfig = "<domain type='kvm' vmi='on' vmi_configs='{}' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'> <name>{}</name>  <uuid>{}</uuid>  <memory>5000000</memory> <vcpu>1</vcpu> <os><type arch='x86_64' machine ='pc-i440fx-4.2'>hvm</type></os><clock offset='utc'/>  <on_poweroff>destroy</on_poweroff>  <on_reboot>restart</on_reboot>  <on_crash>destroy</on_crash>  <devices><emulator>{}</emulator><disk type='file' device='disk'><driver name='qemu' type='qcow2'/><source file='{}'/><backingStore type='file'><format type='qcow2'/><source file='{}'/></backingStore><target dev='hda'/></disk><input type='mouse' bus='ps2'/><graphics type='vnc' port='-1'/></devices> <qemu:commandline><qemu:arg value='-L' /><qemu:arg value='/usr/share/seabios' /></qemu:commandline></domain>".format(vmi_config_path, domain_name, domain_uuid, emulator_path, unique_snapshot_path, source_file_qcow2)

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

timetorun = float(sys.argv[6])
starttime = datetime.now()
starttime = datetime.timestamp(starttime)
print(starttime)
while datetime.timestamp(datetime.now()) <= starttime + timetorun:
    continue
conn = libvirt.open('qemu:///system')
conn.lookupByName(domain_name).destroy()
conn.lookupByName(domain_name).undefine()