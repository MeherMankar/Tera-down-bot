import subprocess
import time
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

def start_aria2c():
    """Start aria2c daemon"""
    try:
        # Check if aria2c is already running
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq aria2c.exe'], 
                              capture_output=True, text=True)
        if 'aria2c.exe' in result.stdout:
            logging.info("aria2c is already running")
            return True
            
        # Start aria2c daemon
        logging.info("Starting aria2c daemon...")
        subprocess.Popen([
            'aria2c', 
            '--enable-rpc', 
            '--rpc-listen-all=false', 
            '--rpc-allow-origin-all', 
            '--daemon',
            '--quiet'
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        time.sleep(3)  # Wait for daemon to start
        logging.info("aria2c daemon started successfully")
        return True
        
    except Exception as e:
        logging.error(f"Failed to start aria2c: {e}")
        return False

def main():
    # Start aria2c first
    if start_aria2c():
        logging.info("Starting Terabox bot...")
        # Import and run the main bot
        try:
            import terabox
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Bot error: {e}")
    else:
        logging.error("Failed to start aria2c daemon")
        sys.exit(1)

if __name__ == "__main__":
    main()