import sys
import re
import socket
import subprocess

def get_default_gateway():
    """
    Return the default gateway IP by shelling out:
      - Linux:   `ip route`
      - macOS:   `route -n get default`
      - Windows: `route print -4`
    Raises RuntimeError if it can’t parse one of those.
    """
    plat = sys.platform
    if plat.startswith("linux"):
        # e.g. “default via 192.168.1.1 dev wlan0 proto dhcp …”
        out = subprocess.check_output(["ip", "route"], text=True)
        m = re.search(r"^default via ([0-9\.]+)", out, re.M)
    elif plat == "darwin":
        # e.g. “gateway: 192.168.1.1”
        out = subprocess.check_output(["route", "-n", "get", "default"], text=True)
        m = re.search(r"gateway: ([0-9\.]+)", out)
    elif plat.startswith("win"):
        # look for the 0.0.0.0 route in the IPv4 table
        out = subprocess.check_output(["route", "print", "-4"], text=True)
        # this line has something like “0.0.0.0          0.0.0.0     192.168.1.1    192.168.1.100    …”
        m = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+([0-9\.]+)\s+", out)
    else:
        raise RuntimeError(f"Unsupported platform: {plat!r}")

    if not m:
        raise RuntimeError("Could not parse default gateway")
    return m.group(1)


def can_connect(host: str, port: int, timeout: float = 1.0) -> bool:
    """Try opening a TCP socket to (host, port)."""
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def check_network(gw):


    lan_ok = can_connect(gw, 80)           # HTTP port on your router
    internet_ok = can_connect("8.8.8.8", 53)  # DNS port on Google’s public DNS

    #if lan_ok and not internet_ok:
    #    print("✅ LAN is up, but Internet is down.")
    #elif lan_ok and internet_ok:
    #    print("✅ Both LAN and Internet are reachable.")
    #elif not lan_ok:
    #    print("❌ Cannot reach LAN gateway; you may be offline entirely.")
    #else:
    #    print("❓ Unexpected network state.")
    return lan_ok, internet_ok

if __name__ == "__main__":
    check_network(get_default_gateway())