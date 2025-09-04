#!/usr/bin/python3
"""Quick MySQL Service Checker"""

from mysql_service_manager import MySQLServiceManager

def main():
    """Check and start MySQL service if needed"""
    print("MySQL Service Checker")
    print("=" * 30)
    
    manager = MySQLServiceManager()
    
    # Check current status
    is_running, service_name = manager.check_service_status()
    
    if is_running:
        print("SUCCESS: MySQL service is running!")
        return True
    elif service_name:
        print(f"WARNING: MySQL service '{service_name}' is stopped")
        print("Attempting to start...")
        
        if manager.start_service(service_name):
            print("SUCCESS: MySQL service started successfully!")
            return True
        else:
            print("ERROR: Failed to start MySQL service")
            print("TIP: Try running as Administrator:")
            print(f"   net start \"{service_name}\"")
            return False
    else:
        print("ERROR: No MySQL service found")
        print("TIP: Please check if MySQL is installed")
        return False

if __name__ == "__main__":
    main()
