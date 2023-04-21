## Processing ANT data

We used the `Internet address censuses` dataset provided by the ANT research group. The overview of the dataset can be found at [https://ant.isi.edu/datasets/index.html](https://ant.isi.edu/datasets/index.html). Access should be requested directly from them.

### Raw data to list of subnets

ANT provides their ICMP scan data in their custom binary format. For reading this format they provide a binary `print_datafile`, source code for which can be downloaded from [https://ant.isi.edu/software/address_surveys/index.html](https://ant.isi.edu/software/address_surveys/index.html).

Each scan file can be converted into a CSV file of responsive /24 subnets using the `analyze_ant.py` script. It reads the scan results line by line and takes one argument, the file name for the output CSV file.

Example usage: `./print_datafile -f data/it.93.pinger-e1.bz2 | python scripts/analyze_ant.py data/it.93.pinger-e1.csv`

### Autonomous system data from subnet lists

A list of autonomous systems and how many of their subnets are responsive can be created using the `associate_as_ant.py` script. Before running the script, the correct pfx2as file needs to be downloaded from `https://publicdata.caida.org/datasets/routing/routeviews-prefix2as/`. The script takes three arguments: 

1. The list of /24 subnets created using `analyze_ant.py`
2. The pfx2as file for the correct scan date
3. Output file name

The output of this script is a list of JSON objects (in `jsonl` format).

Example usage: `python scripts/associate_as_ant.py data/it.93.pinger-e1.csv routeviews-rv2-20210202-0000.pfx2as data/it.93.pinger-e1.jsonl`

### Plotting the results

Results can be plotted using two additional python scripts: `plot_vantage_point_diff.py` and `plot_historical_data.py`.

Plotting the responsive subnets for each vantage point requires the presence of the files created using `associate_as_ant.py`. The `plot_vantage_point_diff.py` script is currently configured to use data from scan number 98 and vantage points `["c", "e", "g", "n", "w"]`.

Example usage: `python scripts/plot_vantage_point_diff.py`

This will read from files `data/it.98.pinger-{c,e,g,n,w}1.jsonl` and will produce two pdf files: `ant_3320_vantage_point.pdf` and `ant_vantage_point.pdf`.

`plot_historical_data.py` works in a similar manner. In the current configuration it reads the data from vantage point `e` and from scan numbers `["79", "84", "89", "93", "98"]`.

Example usage: `python scripts/plot_historical_data.py`

This will read from files `data/it.{79,84,89,93,98}.pinger-e1.jsonl` and will produce two pdf files: `ant_as3320_absolute_icmp_e1.pdf` and `ant_total_absolute_icmp_e1.pdf`.