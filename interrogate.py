from scapy.all import rdpcap, Raw, IP

# 1. Open the jail cell
try:
    prisoners = rdpcap("blackhole_jail.pcap")
except FileNotFoundError:
    print("No prisoners currently in jail.")
    exit()

# 2. Count how many packets are locked inside
print(f"Total Attackers Locked Up: {len(prisoners)}")

# 3. Force all attackers to reveal their payloads
print("\n--- ATTACKER PAYLOADS ---")
for i, packet in enumerate(prisoners):
    if packet.haslayer(IP) and packet.haslayer(Raw):
        ip_src = packet[IP].src
        payload = packet[Raw].load.decode('latin-1', errors='ignore')
        print(f"\n[Prisoner #{i+1}] Source IP: {ip_src}")
        print(f"Evidence:\n{payload.strip()}")
