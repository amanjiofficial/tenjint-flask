def api_configuration():
    """
    API Config (to be modified by user)
    Returns:
        JSON with API configuration
    """
    return {  # Default Configuration
        "api_host": "127.0.0.1",
        "api_port": 5000,
        "api_debug_mode": True,
        "api_admin_token": "foo",
        "api_database": "mongodb://127.0.0.1:27018/",
        "api_database_name": "tenjint",
        "max_vm_count": 1,
        "max_tenjint_run_time": 3600000,
        "min_tenjint_run_time": 100000,
        "tenjint_config_path": "/home/dell/Downloads/tenjint_config.yml",
        "VM_folder_name": "/home/dell/Documents/opensource/tenjint/vm_folder/",
        "plugin_dir": "/home/dell/Documents/opensource/tenjint/tenjint-flask/plugins/",
        "samples_store": "/home/dell/Documents/opensource/tenjint/tenjint-flask/shared_samples",
        "VM": {
            "ubuntu-18-x86_64": {
                "disk-snap": "/home/dell/Documents/opensource/tenjint/vm_folder/ubuntu18_clone.qcow2",
                "snapshot": "memsnap",
                "disk-snap-name": "ubuntu18.04_clone"
            }
        }
    }
