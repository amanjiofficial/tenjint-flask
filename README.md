# Tenjint Flask API

[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs)
[![Top Language](https://img.shields.io/github/languages/top/amanjiofficial/tenjint-flask)]()
[![Github Issues](https://img.shields.io/github/issues/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/issues)
[![Github License](https://img.shields.io/github/license/amanjiofficial/tenjint-flask)](https://github.com/amanjiofficial/tenjint-flask/blob/master/LICENSE)

Flask Web API for Tenjint Project

The Tenjint Flask API project provides a web API where the user can send samples to analyze in VM and query for output of the tenjint run.

For Documentation and Design Architecture visit https://github.com/amanjiofficial/tenjint-flask/tree/master/Docs

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

# Maintainers

[Aman Ahuja](https://github.com/amanjiofficial)  - amanjiofficial@gmail.com