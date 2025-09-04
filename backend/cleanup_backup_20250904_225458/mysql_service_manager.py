#!/usr/bin/python3
"""MySQL Service Manager for Windows"""

import subprocess
import sys
import time
import os

class MySQLServiceManager:
    """Manage MySQL service on Windows"""
    
    def __init__(self):
        self.service_name = "mysql"
        self.alternative_names = ["MySQL", "MySQL80", "MySQL90", "MySQL94"]
    
    def check_service_status(self):
        """Check if MySQL service is running"""
        try:
            # Try different possible service names
            for service_name in [self.service_name] + self.alternative_names:
                result = subprocess.run(
                    f'sc query "{service_name}"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    if "running" in output:
                        print(f"SUCCESS: MySQL service '{service_name}' is running")
                        return True, service_name
                    elif "stopped" in output:
                        print(f"WARNING: MySQL service '{service_name}' is stopped")
                        return False, service_name
                    elif "not found" in output or "does not exist" in output:
                        continue
                        
            print("ERROR: No MySQL service found")
            return False, None
            
        except Exception as e:
            print(f"ERROR: Error checking service status: {e}")
            return False, None
    
    def start_service(self, service_name=None):
        """Start MySQL service"""
        if not service_name:
            _, service_name = self.check_service_status()
            if not service_name:
                print("ERROR: No MySQL service found to start")
                return False
        
        try:
            print(f"Starting MySQL service '{service_name}'...")
            result = subprocess.run(
                f'net start "{service_name}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"SUCCESS: MySQL service '{service_name}' started successfully")
                return True
            else:
                print(f"ERROR: Failed to start MySQL service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"ERROR: Error starting service: {e}")
            return False
    
    def stop_service(self, service_name=None):
        """Stop MySQL service"""
        if not service_name:
            _, service_name = self.check_service_status()
            if not service_name:
                print("ERROR: No MySQL service found to stop")
                return False
        
        try:
            print(f"Stopping MySQL service '{service_name}'...")
            result = subprocess.run(
                f'net stop "{service_name}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"SUCCESS: MySQL service '{service_name}' stopped successfully")
                return True
            else:
                print(f"ERROR: Failed to stop MySQL service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"ERROR: Error stopping service: {e}")
            return False
    
    def restart_service(self, service_name=None):
        """Restart MySQL service"""
        if not service_name:
            _, service_name = self.check_service_status()
            if not service_name:
                print("ERROR: No MySQL service found to restart")
                return False
        
        print(f"Restarting MySQL service '{service_name}'...")
        if self.stop_service(service_name):
            time.sleep(2)  # Wait a moment
            return self.start_service(service_name)
        return False
    
    def ensure_service_running(self):
        """Ensure MySQL service is running, start if not"""
        is_running, service_name = self.check_service_status()
        
        if is_running:
            return True
        elif service_name:
            print(f"WARNING: MySQL service is not running. Attempting to start...")
            return self.start_service(service_name)
        else:
            print("ERROR: No MySQL service found. Please install MySQL or check service name.")
            return False

def main():
    """Main function for testing"""
    manager = MySQLServiceManager()
    
    print("Checking MySQL Service Status...")
    print("=" * 50)
    
    # Check current status
    is_running, service_name = manager.check_service_status()
    
    if not is_running and service_name:
        print(f"\nAttempting to start MySQL service...")
        if manager.ensure_service_running():
            print("SUCCESS: MySQL service is now running!")
        else:
            print("ERROR: Failed to start MySQL service")
            print("TIP: You may need to run as Administrator")
    elif not service_name:
        print("ERROR: No MySQL service found")
        print("TIP: Please install MySQL or check if it's running as a different service name")

if __name__ == "__main__":
    main()
