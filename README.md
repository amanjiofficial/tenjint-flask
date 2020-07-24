# Tenjint-flask
Flask Web API for Tenjint Project

The project provides a web API where the user can send samples to analyze it in tenjint sandbox and returns result in JSON format.
To run the project locally

1. Clone this repository.

    git clone https://github.com/amanjiofficial/tenjint-flask.git

2. Create a virtualenv and activate.

    python3 -m venv env
    source env/bin/activate

3. Install requirement packages.

    pip install -r requirements.txt

4. Start the Flask application on your terminal window.

    python app.py

5. Go to http://localhost:5000/

For API documentation visit docs folder.


Instructions For Creating Virtual Machines.

1. Create a new Virtual Machine and from that create a disk snapshot.

    https://fabianlee.org/2018/09/24/kvm-implementing-linked-clones-with-a-backing-file/

2. Boot using the disk snapshot and take a memory snapshot.

    virsh snapshot-create-as --domain $DOMAIN $SNAPSHOT_NAME --memspec snapshot=internal

3. Add the path to disk snapshot and name of memory snapshot in configuration file.

