import csv


sets = []
fileNames1 = ["it.98.1.pinger-g1.csv", "it.98.2.pinger-g1.csv"]
fileNames2 = [ "it.98.pinger-c1.bz2.csv", "it.98.pinger-e1.bz2.csv", "it.98.pinger-n1.bz2.csv", "it.98.pinger-w1.bz2.csv"]

data = set()
for name in fileNames1:
    with open(name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data.add(line.strip('\n'))
sets.append(data)

for name in fileNames2:
    with open(name, 'r') as f:
        data = set()
        lines = f.readlines()
        for line in lines:
            data.add(line.strip('\n'))
        sets.append(set(data))

print(len(sets))
#print(sets)

intersection = set.intersection(*sets)
f = open("intersection.txt", 'w')
f.write('\n'.join(i for i in intersection))
f.close()

union = set.union(*sets)
f = open("union.txt", 'w')
f.write('\n'.join(u for u in union))
f.close()

#TODO: Add the vantage point to the file, so we know where it was found
result = set()
for _ in sets:
    result |= sets[0] - set.union(*sets[1:])
    sets = sets[1:] + sets[:-1]
f = open("uniqueElements.txt", 'w')
f.write('\n'.join(r for r in result))
f.close()
