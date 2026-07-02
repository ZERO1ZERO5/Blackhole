from scapy.all import sniff, IP, TCP, Raw, wrpcap
from scapy.sessions import TCPSession 
import subprocess
import urllib.parse
import ctypes
import sys
import re 
import os
import platform
import json

MEMORY_FILE = "blocked_ips.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        ALREADY_BLOCKED_IPS = set(json.load(f))
else:
    ALREADY_BLOCKED_IPS = set()

def banish_attacker(ip_address):
    global ALREADY_BLOCKED_IPS
    
    
    if ip_address in ALREADY_BLOCKED_IPS:
        return 
        
    
    ALREADY_BLOCKED_IPS.add(ip_address)
    with open(MEMORY_FILE, "w") as f:
        json.dump(list(ALREADY_BLOCKED_IPS), f)
    
    target_ip = ip_address 
    
    try:
        if platform.system() == "Windows":
            rule_name = f"BlackHole_Block_{target_ip}"
            command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={target_ip}'
        else:
            command = f'iptables -A INPUT -s {target_ip} -j DROP'
            
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\n[X] FIREWALL ACTIVATED: Network connection severed for {target_ip}")
    except Exception as e:
        print(f"[!] Failed to block IP. Are you running as Administrator/Root?")

def devour_check(packet):
    if packet.haslayer(IP):
        ip_src = packet[IP].src
        
        
        if ip_src.startswith("192.168.") or ip_src.startswith("10.") or ip_src == "127.0.0.1":
            return
            
        
        if packet.haslayer(Raw):
            try:
                raw_data = packet[Raw].load.decode('latin-1', errors='ignore')
                decoded_data = urllib.parse.unquote(raw_data)
                payload = decoded_data.upper()
            except:
                return
            
            # --- UPGRADE: Regex Threat Patterns ---
            POISONOUS_PATTERNS = [
                r"DROP\s+TABLE",                  
                r"SELECT\s+\*\s+FROM",            
                r"UNION\s+(/\*.*\*/\s*)?SELECT"   
            ]
            
            # the "Devour" Logic
            for pattern in POISONOUS_PATTERNS:
                if re.search(pattern, payload, re.IGNORECASE):
                    print(f"\n[!!!] BLACK HOLE ALERT [!!!]")
                    print(f"DEVOURING attack from: {ip_src}")
                    print(f"REASON: Matched Threat Pattern '{pattern}'")
                    print(f"DIGESTING EVIDENCE: {payload[:50]}...")
                    
                    # 4. Phase 3: The Jail
                    wrpcap("blackhole_jail.pcap", packet, append=True)
                    print("[*] Evidence safely locked in blackhole_jail.pcap")
                    
                    # 5. Phase 4: The Executioner
                    banish_attacker(ip_src)
                    
                    return

#  SYSTEM CHECK: Verify Administrator Rights 
def is_admin():
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.getuid() == 0
    except:
        return False

if not is_admin():
    print("[!] FATAL ERROR: The Black Hole requires Administrator privileges.")
    print("[*] Please close VS Code, right-click, and select 'Run as Administrator'.")
    sys.exit()

print("|||||||||| BLACK HOLE TASTE BUDS ACTIVE ||||||||||")
# UPGRADE: TCP Stream Reassembly 
sniff(filter="tcp", prn=devour_check, store=0, session=TCPSession)
