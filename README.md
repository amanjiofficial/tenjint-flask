# Tenjint Flask API

[![Top Language](https://img.shields.io/github/languages/top/amanjiofficial/tenjint-flask)]()
[![Github Issues](https://img.shields.io/github/issues/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/issues)
[![Github License](https://img.shields.io/github/license/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/blob/master/LICENSE)

Flask Web API for Tenjint Project

Tenjint is a Python 3 based platform for virtual machine introspection (VMI) on x86 and ARM. It allows developers to write third-party plugins.

To know more about Tenjint visit https://github.com/bedrocksystems/tenjint

The Tenjint Flask API project provides a web API where the user can submit Malware samples to analyze inside VM in tenjint space and query for output of the tenjint run. The web API allows to __scale up Malware Analysis__ Infrastructure. Set up the Tenjint Flask Project on a server and several users can submit the sample files and retrieve the output.

# Features

* Easy to setup Flask Project with customizable configurations.
* User Authentication for submission of sample and output reports.
* Multiple VMs simultaneously allows faster response time.
* Handles waiting queue of API requests if new VM cannot be launched.
* Users can query for the status of their submission at any point of time.
* JSON based output of tenjint run can be retrieved whenever required post tenjint run.
* Easy to add new guest Image category.

# Documentation

[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs)

For openAPI based Specification and Design Architecture visit [docs](https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs)

# Pre-Requisites

## MongoDB
* Follow the Official MongoDB [documentation installation guide](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).
* Add mongoDB to the sources list. 
* Install mongoDB.
````console
sudo apt-get install -y mongodb-org
````
* Enable mongoDB.
````console
systemctl start mongod
````

## Libvirtd
* Ensure Libvirt is installed

* Start the Libvirtd service.
````console
service libvirtd start
````

# Installation

Clone this repository.

    git clone https://github.com/amanjiofficial/tenjint-flask.git

Create a virtualenv and activate.

    python3 -m venv env
    source env/bin/activate

Install requirement packages.

    pip install -r requirements.txt

Install Tenjint and Rekall from Tenjint Repository within virtualenv.

* [Tenjint](https://github.com/bedrocksystems/tenjint)
* [Tenjint-Rekall](https://github.com/bedrocksystems/tenjint-rekall)

Ensure modified QEMU/KVM is installed from [tenjint-qemu](https://github.com/bedrocksystems/tenjint-qemu)

Ensure modified linux kernel is installed from [tenjint-linux](https://github.com/bedrocksystems/tenjint-linux)

Start the Flask application on your terminal window.

    python app.py

Application is started at http://localhost:5000/

# Usage

## Creating Virtual Machines.

* Download the iso file from official sources. 
* Create virsh disk pool for virsh to store VMs.
````console
virsh pool-create-as --name $DISK-POOL-NAME --type dir --target $PATH 
````
* Create a new Virtual Machine using iso file.
````console 
    virt-install --virt-type=kvm --name=$VM_NAME --ram 2048 --vcpus=2 --virt-type=kvm --hvm --cdrom $ISO_FILE_PATH --network network=default --disk pool=$DISK_POOL_NAME,size=20,bus=virtio,format=qcow2 --filesystem $SOURCE,$TARGET
````
* Shutdown the VM.
````console 
virsh shutdown $VM_NAME
````

## Backing File
* Check the location of qcow2 file of the VM created above.
````console
virsh dumpxml $VM_NAME | grep "<source file"
````
* Change to location of qcow2 file.
* Create the new disk with parent backing file 
````console
qemu-img create -f qcow2 -F qcow2 -b $VM_NAME.qcow2 $VM_NAME_CLONE.qcow2 
````
* Create a Folder that will store the VMs generated by the Tenjint Flask and copy files $VM_NAME_CLONE.qcow2 and $VM_NAME.qcow2 and substitute it in `VM_folder_name` in [configuration file](https://github.com/amanjiofficial/tenjint-flask/blob/master/config.py)

## Snapshot
* Generate the XML of VM created in the previous step and save to another file.
````console
virsh dumpxml $VM_NAME > $VM_XML.xml
````

* Undefine the VM.
````console 
virsh undefine $VM_NAME
````

* Edit $VM_NAME.xml file to include `filesystem` block within `devices` block.
````console
<filesystem type='mount' accessmode='passthrough'>
<source dir='/home'/>
<target dir='temp'/>
</filesystem>
```` 

* Edit $VM_NAME.xml and update `source` under `disk` block in `devices` section with the path of $VM_NAME_CLONE.qcow2

* Deploy a new guest OS as a linked clone using $VM_NAME.xml. 
````console
virsh create $VM_NAME.xml
````

* Take a memory snapshot.
````console
virsh snapshot-create-as --domain $VM_NAME $SNAPSHOT_NAME --memspec snapshot=internal
````

* Shutdown the VM.
````console 
virsh shutdown $VM_NAME
````

* Add the path to disk snapshot, name of disk snapshot and name of memory snapshot to [configuration file](https://github.com/amanjiofficial/tenjint-flask/blob/master/config.py)
    * `disk-snap`: disk snapshot qcow2 file path($VM_NAME_CLONE)
    * `snapshot`: memory snapshot($SNAPSHOT)
    * `disk-snap-name`: disk snapshot name($VM_NAME_CLONE)

## Configuration Parameters

The following tables lists the parameters that can be configured and their default values. Configuration is available in [configuration file](https://github.com/amanjiofficial/tenjint-flask/blob/master/config.py)


| Parameter                        | Description                                                                               | Default                                                      |
|----------------------------------|-------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `api_host`           | Host URL for Flask server                                                              | `127.0.0.1`                                                        |
| `api_port`        | Host Port for Flask server                                           | `5000`      |
| `api_debug_mode`                 | Boolean to set debug mode for Flask server                                                              | `True`                                                  |
| `api_admin_token`               |  Token for Admin account authentication                                                                  | `foo`                                             |
| `api_database`                      | Mongo DB Database URL                                                                       | `mongodb://127.0.0.1:27017`                                                 |
| `api_database_name`               | MongoDB database name to be used                                                             | `tenjint`                                                     |
| `max_vm_count`              | Maximum number of VMs that can be run at a particular time                                          | 1       |
| `max_tenjint_run_time`                   |  Maximum allowed duration to run Malware sample in Tenjint                                                                      | 3600000                                                  |
| `min_tenjint_run_time`                   |  Minimum allowed duration to run Malware sample in Tenjint                                                                      | 100000                                                |
| `emulator_path`                   | Path of QEMU Emulator for Tenjint                                                | `/home/dell/Documents/opensource/tenjint/qemu/x86_64-softmmu/qemu-system-x86_64`                                                  |
| `tenjint_config_path`                | Tenjint Configuration Path                                                  | `/home/dell/Downloads/tenjint_config.yml`                                                        |
| `VM_folder_name`                      | Folder path to store VMs for Tenjint  |                               `/home/dell/Documents/opensource/tenjint/VM_Folder/`                                                        |
| `plugin_dir`                | Folder path for Tenjint plugins. It contains necessary plugins to run this Flask Server.                                                  | `/home/dell/Documents/opensource/tenjint/tenjint-flask/plugins/`                                                        |
| `samples_store`                | Folder path to store Malware samples.                                                  | `/home/dell/Documents/opensource/tenjint/tenjint-flask/shared_samples`                                                        |
| `VM`                | List of available VMs.                                                   | Each VM constitutes  `disk-snap`: `disk snapshot qcow2 path`, `snapshot`: `memory snapshot` and `disk-snap-name`: `disk snapshot name`

## Authentication

* Token based authentication.
* Admin token can be configured in `api_admin_token` in  [configuration file](https://github.com/amanjiofficial/tenjint-flask/blob/master/config.py)
* Admin can create users and delete users in the endpoints provided in [docs](https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs/api/openapi.yaml)

when creating a new user, a token is provided as a response of the query. This token is to be used by users to authenticate for submitting Malware Samples.

## Submit Malware Sample

API request example

````console
curl -X POST \
  'http://127.0.0.1:5000/submit?runTime=200000&guestImage=ubuntu-18-x86_64&api_key=5c76f51a419eb213813025ece8bb7ab1' \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F sample=@comment-15.txt
````

Visit [openAPI specification](https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs/api/openapi.yaml) to know more about each parameter. 

# Roadmap

Upcoming Features

* Adding API Trace Plugin.
* Support for Multiple servers in the backend.
* Frontend UI for submission of samples and retrieval of output report.

# Maintainers

[Aman Ahuja](https://github.com/amanjiofficial)  - amanjiofficial@gmail.com

This project started as a part of Google Summer Of Code 2020 under the mentors [Jonas Pfoh](https://github.com/pfohjo) and [Sebastian Vogl](https://github.com/voglse). To know more visit [Project Description](https://summerofcode.withgoogle.com/projects/#6463804466003968)
