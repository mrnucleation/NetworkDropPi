This is a small set of scripts I used to program a Raspberry Pi Zero to send a signal in the event that my router and modem lost connections to each other.  
This was to fix a problem where the DCHP server would randomly stop talking to the router.  But I needed this to happen when I was not home as the
biggest issue was that I could not connect to my computer remotely when this happened. 

So the goal of this script is to check for network connection periodically and if it detects that the router is still reachable, but the internet is not to send
a signal to a 120V controllable plug (https://www.adafruit.com/product/2935) and have it drop the power for 2 seconds then come back up.   This would usually solve the issue.
It's kind of a duct tape approach, but it does work. 
