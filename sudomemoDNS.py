from datetime import datetime
from time import sleep

from dnslib import DNSLabel, QTYPE, RD, RR
from dnslib import A, AAAA, CNAME, MX, NS, SOA, TXT
from dnslib.server import DNSServer

import socket
import requests
import json
import sys

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

SUDOMEMODNS_VERSION = "0.1"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

EPOCH = datetime(1970, 1, 1)
SERIAL = int((datetime.utcnow() - EPOCH).total_seconds())
MY_IP = get_ip()

print("+===============================+")
print("|      Sudomemo DNS Server      |")
print("|          Version " + SUDOMEMODNS_VERSION + "          |")
print("+===============================+\n")

print("Hello! This server will allow you to connect to Sudomemo when")
print("your Internet Service Provider does not work with custom DNS.\n")

print("#### How To Use ####\n")
print("The setup process does not differ from what is shown at")
print("https://support.sudomemo.net/setup except for the values")
print("to enter in your custom DNS settings.\n")

print("First, make sure that your Nintendo DSi is connected to the")
print("same network as this computer.")

print("\nHere are the settings you will put in for DNS on your Nintendo DSi:\n")
print("Primary DNS:  ",MY_IP)
print("Secondary DNS: 8.8.8.8")

print("All other settings should match what is shown at the above URL.\n")

print("#### Starting up ####\n")

TYPE_LOOKUP = {
    A: QTYPE.A,
    AAAA: QTYPE.AAAA,
    CNAME: QTYPE.CNAME,
    MX: QTYPE.MX,
    NS: QTYPE.NS,
    SOA: QTYPE.SOA,
    TXT: QTYPE.TXT,
}

# Can't seem to turn off DNSLogger with a None type so let's just null it out with a dummy function

class SudomemoDNSLogger(object):
    def log_recv(self, handler, data):
        pass
    def log_send(self, handler, data):
        pass
    def log_request(self, handler, request):
        print("[INFO] Received DNS request from DSi at " + handler.client_address[0])
    def log_reply(self, handler, reply):
        print("[INFO] Sent response to DSi at " + handler.client_address[0])
    def log_error(self, handler, e):
        logger.error("[INFO] Invalid DNS request from " + handler.client_address[0])
    def log_truncated(self, handler, reply):
        pass
    def log_data(self, dnsobj):
        pass


class Record:
    def __init__(self, rdata_type, *args, rtype=None, rname=None, ttl=None, **kwargs):
        if isinstance(rdata_type, RD):
            # actually an instance, not a type
            self._rtype = TYPE_LOOKUP[rdata_type.__class__]
            rdata = rdata_type
        else:
            self._rtype = TYPE_LOOKUP[rdata_type]
            if rdata_type == SOA and len(args) == 2:
                # add sensible times to SOA
                args += ((
                    SERIAL,  # serial number
                    60 * 60 * 1,  # refresh
                    60 * 60 * 3,  # retry
                    60 * 60 * 24,  # expire
                    60 * 60 * 1,  # minimum
                ),)
            rdata = rdata_type(*args)

        if rtype:
            self._rtype = rtype
        self._rname = rname
        self.kwargs = dict(
            rdata=rdata,
            ttl=self.sensible_ttl() if ttl is None else ttl,
            **kwargs,
        )

    def try_rr(self, q):
        if q.qtype == QTYPE.ANY or q.qtype == self._rtype:
            return self.as_rr(q.qname)

    def as_rr(self, alt_rname):
        return RR(rname=self._rname or alt_rname, rtype=self._rtype, **self.kwargs)

    def sensible_ttl(self):
        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            return 60 * 60 * 24
        else:
            return 300

    @property
    def is_soa(self):
        return self._rtype == QTYPE.SOA

    def __str__(self):
        return '{} {}'.format(QTYPE[self._rtype], self.kwargs)


ZONES = {}

try:
  get_zones = requests.get("https://www.sudomemo.net/api/dns_zones.json", headers={'User-Agent': 'SudomemoDNS/' + SUDOMEMODNS_VERSION + ' (' + get_platform() + ')'})
except requests.exceptions.Timeout:
  print("[ERROR] Couldn't load DNS data: connection to Sudomemo timed out.")
  print("[ERROR] Are you connected to the Internet?")
except requests.exceptions.RequestException as e:
  print("[ERROR] Couldn't load DNS data.")
  print("[ERROR] Exception: ",e)
  sys.exit(1)
try:
  zones = json.loads(get_zones.text)
except ValueError as e:
  print("[ERROR] Couldn't load DNS data: invalid response from server")
  print("[ERROR] Check that you can visit sudomemo.net")

for zone in zones:
  if zone["type"] == "a":
    ZONES[zone["name"]] = [ Record(A, zone["value"]) ]
  elif zone["type"] == "p":
    ZONES[zone["name"]] = [ Record(A, socket.gethostbyname(zone["value"])) ]

print("[INFO] DNS information loaded successfully.")

class Resolver:
    def __init__(self):
        self.zones = {DNSLabel(k): v for k, v in ZONES.items()}

    def resolve(self, request, handler):
        reply = request.reply()
        zone = self.zones.get(request.q.qname)
        if zone is not None:
            for zone_records in zone:
                rr = zone_records.try_rr(request.q)
                rr and reply.add_answer(rr)
        else:
            # no direct zone so look for an SOA record for a higher level zone
            for zone_label, zone_records in self.zones.items():
                if request.q.qname.matchSuffix(zone_label):
                    try:
                        soa_record = next(r for r in zone_records if r.is_soa)
                    except StopIteration:
                        continue
                    else:
                        reply.add_answer(soa_record.as_rr(zone_label))
                        break

        return reply


resolver = Resolver()
dnsLogger = SudomemoDNSLogger()
if get_platform() == 'linux':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'OS X':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'Windows':
  print("[INFO] Please note: On Windows, you will have to run this as Administrator.")
  print("[INFO] Right click on the .exe and select 'Run as administrator' to do so.")
  print("[INFO] If you aren't seeing any requests, make sure you have done so first.")
  print("[INFO] Disregard this message if you have already done so; as the message will always show")


try:
  servers = [
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=True, logger=dnsLogger),
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=False, logger=dnsLogger),
  ]
except PermissionError:
  print("[ERROR] Permission error: check that you are running this as Administrator or root")
  sys.exit(1)


print("[INFO] Starting Sudomemo DNS server.")

print("[INFO] Now waiting for DNS requests from your Nintendo DSi System.")

if __name__ == '__main__':
    for s in servers:
        s.start_thread()

    try:
        while 1:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.stop()
