import os, pandas   as pd
from os.path        import dirname, exists
from base64         import b64decode
from ipaddress      import IPv4Address
from argparse       import ArgumentParser


dir         = dirname(__file__)
parent_dir  = dirname(dir)
data_dir    = f"{parent_dir}/data"




parser = ArgumentParser()
parser.add_argument("input_file",                                                                           help="Input csv file from censys (inside data/datasets/)")
parser.add_argument("output_dir",                                                                           help="Directory in which the split subnets should be stored (inside data/split/)")
parser.add_argument("--title-subnets",      default="subnet",       metavar="Subnet column name",           help="Title of the subnets column in the input file")
parser.add_argument("--title-vp",           default="perspective",  metavar="Vantage Point column name",    help="Title of the vantage point column in the input file")
parser.add_argument("--title-port",         default="port",         metavar="Port column name",             help="Title of the port column in the input file")


args = parser.parse_args()


# file_to_convert = "subnets_tcp_port22_port80_march2022.csv"
# output_folder   = f"{data_dir}/split/censys_2022_03"


file_to_convert = args.input_file
output_folder   = f"{data_dir}/split/{args.output_dir}"
subnet_title    = args.title_subnets
vp_title        = args.title_vp
port_title      = args.title_port



file_path       = f"{data_dir}/datasets/{file_to_convert}"

print(f"Loading '{file_path}'")

df = pd.read_csv(file_path)

# Convert b64 subnets to decimal
df[subnet_title]    = df[subnet_title].apply(lambda x: IPv4Address(b64decode(x)).compressed)
df                  = df[df[vp_title] != "PERSPECTIVE_UNSPECIFIED"]


grouped_dfs         = df.groupby([vp_title, port_title])

for i, ((vp, port), grouped_df) in enumerate(grouped_dfs):
    if not exists(output_folder):
        os.makedirs(output_folder)
    
    print(f"Saving {port}_{vp} ({i+1}/{len(grouped_dfs)})")

    with open(f"{output_folder}/{port}_{vp}.csv", "w") as f:
        sorted_subnets = grouped_df[subnet_title].sort_values()

        f.write("\n".join(sorted_subnets.values))
