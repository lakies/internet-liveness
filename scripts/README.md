# Introduction

This README explains how to use the provided python scripts that were used to process and analyze the data provided to us. 

> **_NOTE:_**  
This zip file does not come with any data. See Data Section.

# Requirements
These scripts were run using Python 3.10 and 3.11, however they should work with Python version 3.6 or above.

Additionally the scripts require third party libraries, which are listed in requirements.txt. These can be installed as follows when in the `scripts/` directory:

```
pip3 install -r requirements.txt
```

# Data
One important detail to note before using these scripts is that the provided data folder does not actually contain any data. It only serves as a guideline for the structure that the scripts rely on. 

The reason we do not provide any data is because of the Data Use Agreement for both ANT and Censys, which prohibits us from sharing their raw data. If someone wishes to execute these scripts they will need to request access to data from ANT or Censys. In the sub-sections below we will explain what to do once access is gained.

## ANT

In this section we talk about how to gain access to ANT data as well as what to do with it once access has been given.

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







## Censys

We sent an email requesting access to the Censys dataset to `research@censys.io` using our TU Delft email addresses. 

We were granted access to part of the censys database using Google BigQuery. In the following subsections we provide the steps to take once access to Censys data has been given.

### Database structure
Censys gave us access to part of their database using the following Query:

```sql
SELECT  *  FROM `censys-io.universal_internet_dataset.universal_internet_dataset`
WHERE  DATE(snapshot_date)  < DATE_SUB(CURRENT_DATE(), INTERVAL 1  QUARTER)
AND EXTRACT(DAYOFWEEK FROM snapshot_date)  =  3
AND EXTRACT(DAY  FROM snapshot_date)  <  7
```

> **_NOTE:_**  
We were supposed to have access to the first Tuesday every month, however due to a mistake in the above query, whenever the first Tuesday of the month is on the 7th, that dataset gets discarded

For more information about the data in and the structure of the database, visit:

* [Universal Internet BigQuery Dataset](https://support.censys.io/hc/en-us/articles/360056063151-Universal-Internet-BigQuery-Dataset)

* [Data Model for the Universal Internet Data Set](https://support.censys.io/hc/en-us/articles/4401974600340)
* [Universal Internet Dataset schema](https://search.censys.io/data/universal-internet-dataset/definitions)
* [BigQuery Introduction](https://support.censys.io/hc/en-us/articles/360038759991-BigQuery-Introduction).

### Queries 
We ran the following queries to receive the data that was then analysed for the paper:

Port 443, Vantage Point HE, variable time
```sql
SELECT ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
FROM  `censys-io.research_1q.universal_internet_dataset`  as ds, unnest(services) as s
where snapshot_date >= '2018-01-01'  and snapshot_date<='2023-01-01'  and s.transport = 'TCP'  and s.port=443  and s.perspective='HE'
group by ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
```

Port 80, Vantage Point HE, variable time
```sql
SELECT ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
FROM  `censys-io.research_1q.universal_internet_dataset`  as ds, unnest(services) as s
where snapshot_date >= '2018-01-01'  and snapshot_date<='2023-01-01'  and s.transport = 'TCP'  and s.port=80  and s.perspective='HE'
group by ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
```

Port 80, Vantage Point TELIA, variable time
```sql
SELECT ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
FROM  `censys-io.research_1q.universal_internet_dataset`  as ds, unnest(services) as s
where snapshot_date >= '2018-01-01'  and snapshot_date<='2023-01-01'  and s.transport = 'TCP'  and s.port=80  and s.perspective='TELIA'
group by ds.snapshot_date, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24)
```

March 2022, ASN3320, variable Vantage Point, Port {22, 53, 80}
```sql
SELECT s.perspective, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24) as subnet, s.transport, s.port
FROM  `censys-io.research_1q.universal_internet_dataset`  as ds, unnest(services) as s
where snapshot_date >= '2022-03-01'  and snapshot_date<'2022-04-01'  and ((s.transport = 'TCP'  and (s.port=22  or s.port=80)) or (s.transport='UDP'  and s.port=53)) and ds.autonomous_system.asn=3320
group by s.perspective, subnet, s.transport, s.port
```

March 2022, variable Vantage Point, variable Port {22, 53, 80}
```sql
SELECT s.perspective, NET.IP_TRUNC(NET.IP_FROM_STRING(ds.host_identifier.ipv4), 24) as subnet, s.transport, s.port
FROM  `censys-io.research_1q.universal_internet_dataset`  as ds, unnest(services) as s
where snapshot_date >= '2022-03-01'  and snapshot_date<'2022-04-01'  and ((s.transport = 'TCP'  and (s.port=22  or s.port=80)) or (s.transport='UDP'  and s.port=53))
group by s.perspective, subnet, s.transport, s.port
```

### Data folder structure

Once data has been acquired, it should be put in the correct directory as the scripts will otherwise not find the data. In the case of censys data, it should be put into `data/datasets/`. Here is the expected structure of the data folder:

```
data/
    datasets/
    results/
    routeviews/
    split/
```

The purpose of these folders is as follows:
* __datasets__: Stores the raw .csv files received from censys
* __results__: Stores the final results of the scripts
* __routeviews__: Stores the unzipped CAIDA prefix2as routeviews. Zipped versions can be downloaded [here](https://publicdata.caida.org/datasets/routing/routeviews-prefix2as/).
* __split__: Stores the raw list of subnets grouped by different categories such as time, Vantage Point and Port. These files are automatically created from the csv files in `datasets/` using one of the 2 `decouple_censys.py` files.

### Raw data to list of subnets 

The data received from one of the queries above comes as a `.csv` file, with columns depending on the goal of that query. The next step is to split the subnets in the big `.csv` into smaller files according to their changing variable. These can be one of the two following:
* Changing over time, in which case `decouple_censys_over_time.py` should be used
* Changing over Vantage Point and Port, in which case `decoupe_censys.py` should be used.

Both of these files take an input `.csv` file obtained from censys, located inside `data/datasets/` as first argument, and a directory where the split subnets will be stored, located inside `data/split/`. They also take an optional argument `--title-subnets` which specifies the title of the subnets row of the input file. A detailed explanation of the arguments can be seen in the Scripts section.


Examples for both files:

```
python3 decouple_censys_over_time.py TELIA_TCP80_subnets_overtime.csv censys_TELIA_80_overtime

python3 decouple_censys.py subnets_tcp_port22_port80_march2022.csv censys_2022_03

python3 decouple_censys.py subnets_tcp_port22_port80_march2022.csv censys_2022_03 --title-subnets subnet --title-vp vantage_point
```

### Autonomous system data from subnet lists

This next step requires routeviews provided by CAIDA [here](https://publicdata.caida.org/datasets/routing/routeviews-prefix2as/), which should be unzipped and put in the `data/routeviews/` folder. 

Once that is done, we can analyse the data either over time or over vantage point and over time. To analyse over time, we can use `associate_as_òvertime.py`, which takes 2 positional arguments, the first being the name of the input directory (inside `data/split/`) which has the split subnet lists/files. The second positional argument is the output file (inside `data/results/`) which stores all the results of the analysis over time. These results can then be imported into a spreadsheet program to generate graphs.

To analyse the data over vantage point and port, we can use `associate_as_VP_Port.py`. This takes 3 positional arguments:
* Input directory inside `data/split/`, which has the split subnet lists/files
* Unzipped CAIDA routeview file inside `data/routeviews/`, which should be the caida routeview file from the day the measurement was taken
* Output filename inside `data/results/`, which stores all the results of the analysis over time.

Here are some example usages of the programs. Both files also have additional arguments which are covered in the scripts sections.
```
python3 associate_as_overtime.py censys_TELIA_80_overtime TELIA_80_overtime.txt

python3 associate_as_overtime.py censys_TELIA_80_overtime TELIA_80_overtime.txt -np

censys_2022_03 routeviews-rv2-20220301-0200.pfx2as 2022_03_VP_Port.txt

censys_2022_03 routeviews-rv2-20220301-0200.pfx2as 2022_03_VP_Port.txt --target-asn 3320
```


## Scripts

decouple_censys.py
```
positional arguments:
  input_file            Input csv file from censys (inside data/datasets/)
  output_dir            Directory in which the split subnets should be stored (inside data/split/)

options:
  -h, --help            show this help message and exit
  --title-subnets Subnet column name
                        Title of the subnets column in the input file
  --title-vp Vantage Point column name
                        Title of the vantage point column in the input file
  --title-port Port column name
                        Title of the port column in the input file
```

decouple_censys_over_time.py
```
positional arguments:
  input_file            Input csv file from censys (inside data/datasets/)
  output_dir            Directory in which the split subnets should be stored (inside data/split/)

options:
  -h, --help            show this help message and exit
  --title-subnets Subnet column name
                        Title of the subnets column in the input file
  --title-date Date column name
                        Title of the snapshot date column in the input file
```

associate_as.py
```
Not meant to be run on it's own, has AS_tree class which is used by all the other associate_as files
```

associate_as_VP_Port.py
```
positional arguments:
  input_dir             Directory name with all subnets split into files by date (inside data/split/)
  routeview_file        Filename of the CAIDA routeview that the script should use to analyze subnets (inside data/routeviews/)
  output_file           Filename where the output of this script should be stored (inside data/results/)

options:
  -h, --help            show this help message and exit
  -np, --no-pickle      Whether the script should load and save the routeviews using pickle (Uses less storage, takes more time)
  --target-asn Specific AS to analyse
                        The ASN of a specific Autonomous System that we want to analyze
```


associate_as_overtime.py
```
positional arguments:
  input_dir         Directory name with all subnets split into files by date (inside data/split/)
  output_file       Filename where the output of this script should be stored (inside data/results/)

options:
  -h, --help        show this help message and exit
  -np, --no-pickle  Whether the script should load and save the routeviews using pickle (Uses less storage, takes more time)
```