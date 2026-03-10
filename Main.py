from NetworkCheck import check_network, can_connect, get_default_gateway
from Pi_Control import pin_setup, sendsignal, cleanup
from ASUSReboot import load_config, reboot_router
import time
import os
from datetime import datetime, timezone, timedelta

#Console logging
import logging

# Fixed PST offset (UTC-8). Does not adjust for daylight saving time.
PST = timezone(timedelta(hours=-8))
DAILY_REBOOT_HOUR = 4  # 4 AM PST

#=============================================================================================
def is_daily_reboot_due(last_reboot_date):
    """Return True if we've passed the reboot hour today (PST) and haven't rebooted yet."""
    now_pst = datetime.now(PST)
    return now_pst.hour >= DAILY_REBOOT_HOUR and last_reboot_date != now_pst.date()

def reboot_and_wait_for_recovery(router_info, gw, reason):
    """Drop power via GPIO, reboot the router, and block until connectivity is restored."""
    logging.info(f"Initiating reboot sequence — reason: {reason}")
    sendsignal()
    time.sleep(4)
    logging.info("Rebooting router...")
    reboot_router(router_info)

    while True:
        time.sleep(60 * 2)
        lan_ok, internet_ok = check_network(gw)
        if lan_ok and internet_ok:
            logging.info(f"Internet is back up after reboot ({reason}).")
            return
        logging.info(f"Internet still down after reboot ({reason}), waiting...")

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

    # Seed last_reboot_date so we don't fire immediately on startup if it's
    # already past the reboot hour. The first real daily reboot will happen
    # the *next* time the reboot hour arrives (or tomorrow if already past).
    now_pst = datetime.now(PST)
    last_reboot_date = now_pst.date() if now_pst.hour >= DAILY_REBOOT_HOUR else None

    try:
        while True:
            # Check every x seconds to avoid flooding the network
            time.sleep(60)

            # --- Scheduled daily reboot (buffered) ---
            # Checked every iteration so that if we were stuck in a recovery
            # loop when the reboot hour passed, it fires as soon as we return.
            if is_daily_reboot_due(last_reboot_date):
                reboot_and_wait_for_recovery(router_info, gw, "scheduled daily reboot")
                last_reboot_date = datetime.now(PST).date()
                continue  # re-enter the loop for a fresh network check

            # Check the network status  
            lan_ok, internet_ok = check_network(gw)
            
            curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logging.info(f"Current time: {curtime}")
            
            if lan_ok and internet_ok:
                logging.info("Both LAN and Internet are reachable.")
                
            elif lan_ok and not internet_ok:
                logging.info("LAN is up, but Internet is down.")
                reboot_and_wait_for_recovery(router_info, gw, "internet outage detected")
                    
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