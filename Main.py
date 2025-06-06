from NetworkCheck import check_network, can_connect, get_default_gateway
from Pi_Control import pin_setup, sendsignal, cleanup
from ASUSReboot import load_config, reboot_router
import time
import os

#Console logging
import logging

#=============================================================================================
def main():
    # Get the default gateway
    gw = get_default_gateway()
    print(f"Default gateway: {gw}")
    
    #Initialize logging
    log_file = 'network_check.log'
    if os.path.exists(log_file):
        os.remove(log_file)
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    # Set up the GPIO pin
    pin_setup()
    
    router_info = load_config('config.json')
    
    
    try:
        while True:
            # Check every x seconds to avoid flooding the network
            time.sleep(60)
            # Check the network status  
            lan_ok, internet_ok = check_network(gw)
            
            curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logging.info(f"Current time: {curtime}")
            
            if lan_ok and internet_ok:
                logging.info("Both LAN and Internet are reachable.")
                #print("✅ Both LAN and Internet are reachable.")
                #pass
                
            elif lan_ok and not internet_ok:
                #print("LAN is up, but Internet is down.")
                logging.info("LAN is up, but Internet is down.")
                
                # Send signal to GPIO pin to drop power
                sendsignal()
                time.sleep(4)  # Wait for 7 seconds before rebooting
                # Reboot the router
                logging.info("Rebooting router...")
                reboot_router(router_info)
                
                # If you perform the check immediately after sending the signal,
                # you may get a false positive because the network may not be back up yet.
                # So, wait for a few minutes before checking again.
                while True:
                    time.sleep(60*2) # Wait for 2 minutes before checking again 
                    lan_ok_recheck, internet_ok_recheck = check_network(gw)
                    if internet_ok_recheck and lan_ok_recheck:
                        logging.info("Internet is back up.")
                        break
                    print("❌ Internet is still down.")           
                    
            elif not lan_ok:
                logging.info("Cannot reach LAN gateway; you may be offline entirely.")
                
            else:
                # Should not reach here because this would imply that
                # the LAN is down but the Internet is up, which is not possible
                # in a typical home network setup.  But let's log it just in case.
                logging.info("Unexpected network state.")
                
            #Clear the log file if it gets too large
            max_size = 1024 * 1024 * 500  # 500 MB
            if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
                with open(log_file, 'w') as f:
                    f.write('')  # Clear the log file
                    logging.info("Log file cleared.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    except KeyboardInterrupt:
        logging.info("Exiting program.")
        
    cleanup()
        
#=============================================================================================
if __name__ == "__main__":
    main()