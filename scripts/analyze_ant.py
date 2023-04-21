import sys

counter = 0

subnets = set()

max_lines = 4000000000

print(sys.argv[1])

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

for line in sys.stdin:
    if line.startswith("#"):
        continue

    counter += 1
    if counter % 1000000 == 0:
        printProgressBar(min(counter, max_lines), max_lines)

    line = line.split()

    ip = ""
    if line[4] != "--------":
        ip = line[4]
    
    if ip == "" or line[0] != "0x0000":
        continue

    # print(line)

    ip = ".".join(ip.split(".")[0:3]) + ".0"

    subnets.add(ip)


with open(sys.argv[1], "w") as f:
    for slash_24_subnet in subnets:
        f.write(slash_24_subnet + "\n")