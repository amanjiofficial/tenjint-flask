# Tenjint Flask API

[![Top Language](https://img.shields.io/github/languages/top/amanjiofficial/tenjint-flask)]()
[![Github Issues](https://img.shields.io/github/issues/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/issues)
[![Github License](https://img.shields.io/github/license/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/blob/master/LICENSE)

Flask Web API for Tenjint Project

Tenjint is a Python 3 based platform for virtual machine introspection (VMI) on x86 and ARM. It allows developers to write third-party plugins.

To know more about Tenjint visit https://github.com/bedrocksystems/tenjint

The Tenjint Flask API project provides a web API where the user can submit Malware samples to analyze inside VM in tenjint space and query for output of the tenjint run. The web API allows to __scale up Malware Analysis__ Infrastructure. Set up the Tenjint Flask Project on a server and several user can submit the sample files and retrieve the output.

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

# Getting Started

Clone this repository.

    git clone https://github.com/amanjiofficial/tenjint-flask.git

Create a virtualenv and activate.

    python3 -m venv env
    source env/bin/activate

Install requirement packages.

    pip install -r requirements.txt

Start the Flask application on your terminal window.

    python app.py

Application is started at http://localhost:5000/

Instructions For Creating Virtual Machines.

Create a new Virtual Machine and from that create a disk snapshot.

    https://fabianlee.org/2018/09/24/kvm-implementing-linked-clones-with-a-backing-file/

Boot using the disk snapshot and take a memory snapshot.

    virsh snapshot-create-as --domain $DOMAIN $SNAPSHOT_NAME --memspec snapshot=internal

Add the path to disk snapshot and name of memory snapshot in [configuration file](https://github.com/amanjiofficial/tenjint-flask/blob/master/config.py)

# ROADMAP

Upcoming Features:-

* Adding API Trace Plugin.
* Support for Multiple servers in the backend.
* Frontend UI for submission of samples and retrieval of output report.

# Maintainers:-

[Aman Ahuja](https://github.com/amanjiofficial)  - amanjiofficial@gmail.com

This project started as a part of Google Summer Of Code 2020 under the mentors [Jonas Pfoh](https://github.com/pfohjo) and [Sebastian Vogl](https://github.com/voglse). To know more visit [Project Description](https://summerofcode.withgoogle.com/projects/#6463804466003968)
