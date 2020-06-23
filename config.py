def api_configuration():
    """
    API Config (to be modified by user)
    Returns:
        JSON with API configuration
    """
    return {  # Default Configuration
        "api_host": "127.0.0.1",
        "api_port": 5000,
        "api_debug_mode": False,
        "api_admin_token": "foo",
        "api_database": "mongodb://127.0.0.1:27017/",
        "api_database_name": "tenjint",
        "max_vm_count": 5,
        "max_tenjint_run_time": 1800,
        "min_tenjint_run_time": 20,
    }
