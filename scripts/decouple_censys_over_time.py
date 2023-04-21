import os, pandas   as pd
from os.path    import dirname, exists
from base64     import b64decode
from ipaddress  import IPv4Address
from argparse       import ArgumentParser


dir         = dirname(__file__)
parent_dir  = dirname(dir)
data_dir    = f"{parent_dir}/data"







parser = ArgumentParser()
parser.add_argument("input_file",                                                                       help="Input csv file from censys (inside data/datasets/)")
parser.add_argument("output_dir",                                                                       help="Directory in which the split subnets should be stored (inside data/split/)")
parser.add_argument("--title-subnets",      default="_f0",              metavar="Subnet column name",   help="Title of the subnets column in the input file")
parser.add_argument("--title-date",         default="snapshot_date",    metavar="Date column name",     help="Title of the snapshot date column in the input file")

args = parser.parse_args()

# file_to_convert = "HE_TCP_443_overtime_HE.csv"
# output_folder   = f"{data_dir}/split/censys_HE_443_overtime"


file_to_convert = args.input_file
output_folder   = f"{data_dir}/split/{args.output_dir}"
subnet_title    = args.title_subnets
date_title      = args.title_date



print(f"Loading file {file_to_convert}")
df = pd.read_csv(f"{data_dir}/datasets/{file_to_convert}")


snapshots = df[date_title].unique()

print(snapshots)

for i, ((snapshot_date), grouped_df) in enumerate(df.groupby(date_title)):
    print(f"Saving {snapshot_date} ({i + 1}/{len(snapshots)})")

    if not exists(output_folder):
        os.makedirs(output_folder)

    snapshot_date   = snapshot_date.split()[0]
    output_file     = f"{output_folder}/{snapshot_date}.csv"

    if exists(output_file):
        continue

    # Convert b64 subnets to decimal
    grouped_df[subnet_title] = grouped_df[subnet_title].apply(lambda x: IPv4Address(b64decode(x)).compressed)


    with open(output_file, "w") as f:
        sorted_subnets = grouped_df[subnet_title].sort_values()

        f.write("\n".join(sorted_subnets.values))