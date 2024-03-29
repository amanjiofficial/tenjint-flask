import xml.etree.ElementTree as ET
from flask import abort
import uuid
import libvirt
import sys
import os
import pickle
import json
import shutil
from config import api_configuration
from core.compatible import generate_token
import threading
import time
from collections import deque
from api.db import db

running = []
waiting = deque()
api_config = api_configuration()
maxvm = api_config["max_vm_count"]


def newSample(sample):
    if len(running) < maxvm and len(waiting) == 0:
        running.append(sample)
        startVM(sample)
    else:
        waiting.append(sample)


def check_path(key):
    try:
        if api_config[key]:
            if os.path.exists(api_config[key]):
                return api_config[key]
            else:
                return abort(404, "{} is invalid.".format(key))
    except KeyError:
        abort(404, "{} is not present.".format(key))

def check_snapshot(VMName, type):
    try:
        if api_config["VM"][VMName][type]:
            return api_config["VM"][VMName][type]
    except KeyError:
        abort(404, "Snapshot not present.")

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
    eventLoopThread = threading.Thread(
        target=virEventLoopNativeRun, name="libvirtEventLoop")
    eventLoopThread.setDaemon(True)
    eventLoopThread.start()


def myDomainEventCallback(conn, dom, event, detail, opaque):
    if (not (conn.lookupByName(dom.name()).info()[0] == libvirt.VIR_DOMAIN_PAUSED) and dom.ID() == -1):
        if conn.lookupByName(dom.name()).info()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            sample_path = db.submission.started.find_one(
                {"domain": dom.name()}, {"submission_file": 1})
            plugin_dir = check_path("plugin_dir")
            db_json = {
                "domain": dom.name()
            }
            try:
                with open(plugin_dir + sample_path["submission_file"], 'rb') as openfile:
                    output_list = pickle.load(openfile)
                    db_json["output"] = output_list
                    os.remove(plugin_dir + sample_path["submission_file"])
            except FileNotFoundError:
                db_json["output"] = "No output collected. Submit sample again"
            if not db.output.output.find_one({"domain": dom.name()}):
                db.output.output.insert_one(db_json)
            db.submission.started.update_one({"domain": dom.name()}, {
                                             "$set": {"status": "completed"}})
            if len(running) > 0:
                flag = 0
                for i in range(0, len(running)):
                    if running[i]["domain"] == dom.name():
                        running.pop(i)
                        flag = 1
                        break
                if len(waiting) > 0 and flag == 1:
                    currSample = waiting[0]
                    waiting.popleft()
                    running.append(currSample)
                    startVM(currSample)
        else:
            if conn.lookupByName(dom.name()).info()[0] == libvirt.VIR_DOMAIN_RUNNING:
                conn.lookupByName(dom.name()).destroy()


def myDomainTimeoutCalllback(timer, opaque):
    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
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
conn.domainEventRegister(myDomainEventCallback, None)
conn.setKeepAlive(5, 3)

def VMTemplate(disk_snapshot_name, VMName, VMPath, tenjint_path, snapshot, sharedFolder):
    dom = conn.lookupByName(disk_snapshot_name)
    xmlstring = dom.XMLDesc(flags=0)
    root = ET.fromstring(xmlstring)
    for n in root.iter('domain'):
        n.set('xmnls:ns0','http://libvirt.org/schemas/domain/qemu/1.0')
    for n in root.iter('name'):
        n.text = VMName
    for n in root.iter('uuid'):
        n.text = str(uuid.uuid4())
    for n in root.iter('disk'):
        for m in n.iter('source'):
            m.set('file', VMPath)
    for n in root.iter('filesystem'):
        for m in n.iter('source'):
            m.set('dir', sharedFolder)
    args = ET.SubElement(root, 'ns0:commandline')
    argTag = ET.SubElement(args, 'ns0:arg')
    argTag.set('value', 'vmi=on,vmi-configs=' + tenjint_path)
    argTag = ET.SubElement(args, 'ns0:arg')
    argTag.set('value', '-loadvm')
    argTag = ET.SubElement(args, 'ns0:arg')
    argTag.set('value', snapshot)
    return ET.tostring(root, method='xml')

def startVM(sample):
    VMName = sample["guest_image"]
    runTime = sample["time_to_run"]
    sample_file = sample["submission_file"]
    tenjint_path = check_path("tenjint_config_path")
    VM_folder = check_path("VM_folder_name")
    samples_folder = check_path("samples_store")
    disk_snapshot = check_disk_snapshot(VMName)
    disk_snapshot_name = check_snapshot(VMName, "disk-snap-name")
    snapshot_name = check_snapshot(VMName, "snapshot")
    destFile = generate_token(32)
    destPath = VM_folder + destFile + '.qcow2'
    sample["domain"] = destFile
    sample["status"] = "running"
    shutil.copyfile(disk_snapshot, destPath)
    xmlstr = VMTemplate(disk_snapshot_name, destFile, destPath, tenjint_path, snapshot_name, samples_folder)
    xmlstr = str(xmlstr, 'utf-8')
    plugin_dir = check_path("plugin_dir")
    with open(plugin_dir + "sample.json", "w") as outfile:
        json.dump({"file": sample_file}, outfile)
    db.submission.started.insert_one(sample)
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
        libvirt.virEventAddTimeout(runTime, myDomainTimeoutCalllback, destFile)
    except libvirt.libvirtError:
        abort(404, "Libvirt could not be configured")
