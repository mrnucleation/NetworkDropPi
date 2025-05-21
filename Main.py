from NetworkCheck import check_network, can_connect, get_default_gateway
from Pi_Control import pin_setup, sendsignal, cleanup
import time
import os

#Console logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#==========================
def main():
    # Get the default gateway
    gw = get_default_gateway()
    print(f"Default gateway: {gw}")
    
    # Set up the GPIO pin
    pin_setup()
    
    
    try:
        while True:
            # Check every x seconds to avoid flooding the network
            time.sleep(30)
            # Check the network status  
            lan_ok, internet_ok = check_network(gw)
            
            curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logging.info(f"Current time: {curtime}")
            
            if lan_ok and internet_ok:
                logging.info("Both LAN and Internet are reachable.")
                #print("✅ Both LAN and Internet are reachable.")
                
            elif lan_ok and not internet_ok:
                #print("LAN is up, but Internet is down.")
                logging.info("LAN is up, but Internet is down.")
                
                # Send signal to GPIO pin to drop power
                sendsignal()
                time.sleep(60*3) # Wait for 3 minutes before checking again
                _, internet_ok_recheck = check_network(gw)
                if internet_ok_recheck:
                    print("✅ Internet is back up.")
                else:
                    print("❌ Internet is still down.")           
            elif not lan_ok:
                #print("❌ Cannot reach LAN gateway; you may be offline entirely.")
                logging.info("Cannot reach LAN gateway; you may be offline entirely.")
            else:
                # Should not reach here because this would imply that
                # the LAN is down but the Internet is up, which is not possible
                # in a typical home network setup.  But let's log it just in case.
                logging.info("Unexpected network state.")
            #Clear the log file if it gets too large
            log_file = 'network_check.log'
            max_size = 1024 * 1024 * 5  # 5 MB
            if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
                with open(log_file, 'w') as f:
                    f.write('')  # Clear the log file
                    logging.info("Log file cleared.")
    except Exception as e:
        cleanup()
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
    except KeyboardInterrupt:
        # Cleanup GPIO on exit
        cleanup()
        logging.info("Exiting program.")
        #print("Exiting program.")
        pass
        
#===========================
if __name__ == "__main__":
    main()