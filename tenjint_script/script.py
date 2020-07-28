import xml.etree.ElementTree as ET
from flask import abort
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

def check_path(key):
    try:
        if api_config[key]:
            if os.path.exists(api_config[key]):
                return api_config[key]
            else:
                return abort(404, "{} is invalid.".format(key))  
    except KeyError:
        abort(404, "{} is not present.".format(key))

def check_disk_snapshot(VMName):
    try:
        if api_config["VM"][VMName]["disk-snap"]:
            if os.path.exists(api_config["VM"][VMName]["disk-snap"]):
                return api_config["VM"][VMName]["disk-snap"]
            else:
                return abort(404, "Disk Snapshot Path is invalid.")
    except KeyError:
        abort(404, "Disk Snapshot path not present.")

eventLoopThread = None
libvirt.virEventRegisterDefaultImpl()

def virEventLoopNativeStart():
    global eventLoopThread
    eventLoopThread = threading.Thread(target=virEventLoopNativeRun, name="libvirtEventLoop")
    eventLoopThread.setDaemon(True)
    eventLoopThread.start()

def myDomainEventCallback(conn, dom, event, detail, opaque):
    print("myDomainEventCallback%s EVENT: Domain %s(%s)" % (opaque, dom.name(), dom.ID()))
    if (conn.lookupByName(dom.name()).info()[0] !=libvirt.VIR_DOMAIN_RUNNING) and dom.ID()!=-1:
           # save json report in DB
        time.sleep(10)
        if conn.lookupByName(dom.name()).info()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
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
    try:
        if api_config["VM"][VMName]["snapshot"]:
            snapshot_name = api_config["VM"][VMName]["snapshot"]
    except KeyError:
        return abort(404, "Internal memory snapshot not present.")

    tenjint_path = check_path("tenjint_config_path")
    emulator_path = check_path("emulator_path")
    VM_folder = check_path("VM_folder_name")
    disk_snapshot = check_disk_snapshot(VMName)
    destFile = generate_token()
    destPath = VM_folder + '/' + destFile + '.qcow2'
    shutil.copyfile(disk_snapshot, destPath)
    domain_uuid = uuid.uuid4()
    xmlPath = os.getcwd() + '/template.xml'
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
    try: 
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
    except libvirt.libvirtError:
        abort(404, "Libvirt could not be configured")
    