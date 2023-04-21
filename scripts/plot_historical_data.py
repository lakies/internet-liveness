import json
import matplotlib.pyplot as plt
import matplotlib, numpy as np


dataset_ids = ["79", "84", "89", "93", "98"]

datasets = {}

for id in dataset_ids:
    with open("as_subnet_csvs/it." + id + ".pinger-e1.bz2.csv", "r") as f:
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

for attribute, measurement in [["Announced", totals], ["Responsive", responsive]]:
    offset = width * multiplier
    rects = ax.bar(x + offset + 0.25 / 2, measurement, width, label=attribute)
    # ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel('Number of /24 subnets')
ax.set_xlabel('Dataset number')
ax.set_title('Number of announced and responsive subnets for AS3320\n Vantage Point e1, ICMP')
ax.set_xticks(x + width, dataset_ids)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, max(totals) * 1.25)
ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
fig.savefig('ant_as3320_absolute_icmp_e1.pdf', format="pdf")
# plt.show()

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

for attribute, measurement in [["Announced", announced_totals], ["Responsive", responsive_totals]]:
    offset = width * multiplier
    rects = ax.bar(x + offset + 0.25 / 2, measurement, width, label=attribute)
    # ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel('Number of /24 subnets')
ax.set_xlabel('Dataset number')
ax.set_title('Number of announced and responsive subnets\n Vantage Point e1, ICMP')
ax.set_xticks(x + width, dataset_ids)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, max(announced_totals) * 1.25)
ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.hlines(y=2**24, xmin=0, xmax=5, colors='r', linestyles='--', lw=1, label='Max IPv4 Address Space')
ax.annotate('Max IPv4 Address Space', xy=(4.5, 2**24), xytext=(4.0, 2**24 * 1.02), ha='center', color='r') 

fig.savefig('and_total_absolute_icmp_e1.pdf', format="pdf")
