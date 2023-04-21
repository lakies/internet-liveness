import sys, ipaddress, json

in_csv = sys.argv[1]
in_as = sys.argv[2]
out_filename = sys.argv[3]

responded_subnets = []

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

count = 0

autonomous_systems = {}

print("Reading subnets from csv")

with open(in_csv, "r") as f:
    responded_subnets = [x.strip() for x in f.readlines()]

total = len(responded_subnets)

as_count = 0


print("Building AS subnet tree")

with open(in_as, "r") as f:
    for line in f.readlines():
        as_count += 1
        line = line.strip()
        ip, subnet_mask, as_code = line.split()

        ip = ipaddress.ip_address(ip)

        s = bin(int.from_bytes(ip.packed, byteorder="big"))[2::]
        s = s.rjust(32, "0")

        tree = autonomous_systems
        subnet_mask = int(subnet_mask)

        if subnet_mask > 24:
            continue

        for i in range(subnet_mask):
            bit = s[i]
            if bit not in tree:
                tree[bit] = {}
            
            tree = tree[bit]
        
        if "sys" not in tree:
            tree["sys"] = {
                "subnet": subnet_mask,
                "as": as_code,
                "count": 0
            }

unmapped_subnets = []

incremented = 0

print("Analyzing subnets")

for subnet in responded_subnets:

    count += 1

    if count % 10000 == 0:
        printProgressBar(count, total)

    ip = ipaddress.ip_address(subnet)

    s = bin(int.from_bytes(ip.packed, byteorder="big"))[2::]
    s = s.rjust(32, "0")

    tree = autonomous_systems
    for i in range(25):

        if "sys" in tree:
            a_sys = tree["sys"]
            incremented += 1
            a_sys["count"] += 1

            break
        
        if i == 24:
            unmapped_subnets.append(subnet)
            break
        
        bit = s[i]
        if bit in tree:
            tree = tree[bit]
        else:
            unmapped_subnets.append(subnet)
            break

as_responses = {
}
    
print()

print("Collecting AS responsiveness data from tree")

def count_as(tree):
    if "sys" in tree:
        res = tree["sys"]

        as_code = res["as"]
        if as_code not in as_responses:
            as_responses[res["as"]] = {
                "responsive": 0,
                "total": 0
            }

        
        as_responses[as_code]["responsive"] += res["count"]
        as_responses[as_code]["total"] += 2 ** (24 - int(res["subnet"]))

    if "0" in tree:
        count_as(tree["0"])

    if "1" in tree:
        count_as(tree["1"])

count_as(autonomous_systems)

# print("AS Count:" + str(as_count))
print("Unmapped: " + str(len(unmapped_subnets)))

# print("Total:" + str(as_count + len(unmapped_subnets)))

# print(as_responses)


print(len(as_responses.keys()))

as_list = []

count = 0

for as_code in as_responses:
    as_res = as_responses[as_code]
    as_res["ratio"] = as_res["responsive"] / as_res["total"]
    as_res["code"] = as_code
    as_list.append(as_res)

    

as_responses_by_ratio = sorted(as_list, key=lambda d: d['responsive'], reverse=True)

with open(out_filename, "w") as f:
    for as_ in as_responses_by_ratio:
        f.write(json.dumps(as_) + "\n")