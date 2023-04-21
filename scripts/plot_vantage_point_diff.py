import json
import matplotlib.pyplot as plt
import matplotlib, numpy as np


dataset_ids = ["c", "e", "g", "n", "w"]

datasets = {}

for id in dataset_ids:
    with open("data/it.98.pinger-" + id + "1.jsonl", "r") as f:
        datasets[id] = [json.loads(x.strip()) for x in f.readlines()]

as_code = "3320"

ratios = []
totals = []
responsive = []

for id in dataset_ids:
    for as_ in datasets[id]:
        if as_["code"] == as_code:
            ratios.append(as_["ratio"])
            totals.append(as_["total"])
            responsive.append(as_["responsive"])


print(ratios)
print(totals)
print(responsive)


x = np.arange(5)
width = 0.25  
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in [["Responsive", responsive]]:
    offset = width * multiplier
    rects = ax.bar(x + offset + 0.25, measurement, width, label=attribute)
    multiplier += 1

ax.set_ylabel('Number of /24 subnets')
ax.set_xlabel('Vantage point')
ax.set_title('Number of responsive subnets for AS3320\nMarch 2022, ICMP')
ax.set_xticks(x + width, dataset_ids)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, max(responsive) * 1.25)
ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
fig.savefig('ant_3320_vantage_point.pdf', format="pdf")

announced_totals = []
responsive_totals = []
responsive_ratios = []

for id in dataset_ids:
    responsive_total = 0
    announced_total = 0

    for as_ in datasets[id]:
        responsive_total += as_["responsive"]
        announced_total += as_["total"]
    
    announced_totals.append(announced_total)
    responsive_totals.append(responsive_total)
    responsive_ratios.append(responsive_total / announced_total)

fig, ax = plt.subplots(layout='constrained')
multiplier = 0

for attribute, measurement in [["Responsive", responsive_totals]]:
    offset = width * multiplier
    rects = ax.bar(x + offset + 0.25, measurement, width, label=attribute)
    multiplier += 1

ax.set_ylabel('Number of /24 subnets')
ax.set_xlabel('Vantage point')
ax.set_title('Number of responsive subnets\nMarch 2022, ICMP')
ax.set_xticks(x + width, dataset_ids)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, max(announced_totals) * 1.25)
ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.hlines(y=max(announced_totals), xmin=0, xmax=5, colors='r', linestyles='--', lw=1, label='Announced subnets')
ax.annotate('Announced subnets', xy=(4.5, 2**24), xytext=(4.0, 2**24 * 1.02), ha='center', color='r') 

plt.savefig("ant_vantage_point.pdf", format="pdf")

