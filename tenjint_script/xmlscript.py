import xml.etree.ElementTree as ET
import uuid
import libvirt
import sys
import os
import shutil
from config import api_configuration
from core.compatible import generate_token
import threading
import time

api_config = api_configuration()
tenjint_path = api_config["tenjint_config_path"]
emulator_path = api_config["emulator_path"]
origPath = os.getcwd()
eventLoopThread = None
libvirt.virEventRegisterDefaultImpl()

def virEventLoopNativeStart():
    global eventLoopThread
    eventLoopThread = threading.Thread(target=virEventLoopNativeRun, name="libvirtEventLoop")
    eventLoopThread.setDaemon(True)
    eventLoopThread.start()

def myDomainEventCallback(conn, dom, event, detail, opaque):
    print("myDomainEventCallback%s EVENT: Domain %s(%s)" % (opaque, dom.name(), dom.ID()))
    if (conn.lookupByName(dom.name()).info()[0] !=1) and dom.ID()!=-1:
           # save json report in DB
        time.sleep(10)
        if conn.lookupByName(dom.name()).info()[0] != 5:
            conn.lookupByName(dom.name()).destroy()
       
def myDomainTimeoutCalllback(timer, opaque):
    print("Timeout %s" % (opaque))
    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    # save json report in DB
    if conn.lookupByName(opaque).info()[0] == libvirt.VIR_DOMAIN_RUNNING:
        conn.lookupByName(opaque).shutdown()
        time.sleep(10)
        if conn.lookupByName(opaque).info()[0] == libvirt.VIR_DOMAIN_RUNNING:
            conn.lookupByName(opaque).destroy()
    libvirt.virEventRemoveTimeout(timer)


def virEventLoopNativeRun():
    while True:
        libvirt.virEventRunDefaultImpl()

virEventLoopNativeStart()
conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)
conn.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE, myDomainEventCallback, 2)
conn.setKeepAlive(5, 3)
    

def startVM(VMName, runTime):
    disk_snapshot = api_config["VM"][VMName]["disk-snap"]
    destFile = generate_token()
    destPath = os.getcwd() + '/tenjint_script/VM/' + destFile + '.qcow2'
    shutil.copyfile(disk_snapshot, destPath)
    snapshot_name = api_config["VM"][VMName]["snapshot"]
    domain_uuid = uuid.uuid4()
    xmlPath = os.getcwd() + '/tenjint_script/template.xml'
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    root.set('vmi-configs', tenjint_path)
    root[0].text = destFile
    root[1].text = str(domain_uuid)
    root[10][0].text = emulator_path
    root[10][1][1].set('file', destPath)
    root[11][3].set('value', snapshot_name)
    tree.write(xmlPath)
    xmlstr = ET.tostring(root, method='xml')
    xmlstr = str(xmlstr, 'utf-8')
    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)

    dom = conn.defineXML(xmlstr)
    if dom == None:
        print('Failed to define a domain from an XML definition.', file=sys.stderr)
        exit(1)

    if dom.create() < 0:
        print('Can not boot guest domain.', file=sys.stderr)
        exit(1)
    
    libvirt.virEventAddTimeout(runTime,myDomainTimeoutCalllback,destFile)
    
    