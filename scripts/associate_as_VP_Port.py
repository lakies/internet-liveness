import pandas       as pd
from associate_as   import AS_Tree, convert_asn
from os.path        import dirname, basename
from glob           import glob
from argparse       import ArgumentParser


dir         = dirname(__file__)
parent_dir  = dirname(dir)
data_dir    = f"{parent_dir}/data"




parser = ArgumentParser()
parser.add_argument("input_dir",                                                                        help="Directory name with all subnets split into files by date (inside data/split/)")
parser.add_argument("routeview_file",                                                                   help="Filename of the CAIDA routeview that the script should use to analyze subnets (inside data/routeviews/)")
parser.add_argument("output_file",                                                                      help="Filename where the output of this script should be stored (inside data/results/)")
parser.add_argument("-np", "--no-pickle",   action="store_true",                                        help="Whether the script should load and save the routeviews using pickle (Uses less storage, takes more time)")
parser.add_argument("--target-asn",         default=None,           metavar="Specific AS to analyse",   help="The ASN of a specific Autonomous System that we want to analyze")

args = parser.parse_args()



csv_dir     = f"{data_dir}/split/{args.input_dir}"
in_as       = f"{data_dir}/routeviews/{args.routeview_file}"
output_file = f"{data_dir}/results/{args.output_file}"


target_asn = args.target_asn
if target_asn != None:
    
    if target_asn.startswith("ASN"):
        target_asn = target_asn[3:]
    
    elif target_asn.startswith("AS"):
        target_asn = target_asn[2:]




seperator   = "\n-----------------------------------------------\n\n"

tree        = AS_Tree(in_as)

matching_files  = glob(f"{csv_dir}/*.csv")
entries         = []

# Subnets in the dataset that are not related to target_asn according to CAIDA data
false_subnets   = []

unmapped_subnets = []

for i, filepath in enumerate(matching_files):
    filename = basename(filepath).split(".")[0]

    port, vp = filename.split("_")

    print(f"Working on {filename} ({i+1}/{len(matching_files)})")


    with open(filepath, "r") as f:
        responded_subnets = [x.strip() for x in f.readlines()]
        
    tree.count_subnet_occurence(responded_subnets)
    as_responses = tree.count_as()


    if target_asn != None:
        entry       = as_responses[target_asn]

        responsive  = entry["responsive"]
        total       = entry["total"]
        ratio       = responsive / total
    
    else:
        responsive, total, ratio = tree.calc_overall_ratio()

    to_enter = {
        "vp" :          vp,
        "port" :        port,
        "responsive" :  responsive,
        "total" :       total,
        "ratio" :       ratio
    }

    entries.append(to_enter)

    if target_asn != None:
        n_false_subnets = 0
        for ip_s, asn in tree.multiple_as.items():
            asns = convert_asn(asn)

            if target_asn not in asns:
                n_false_subnets += 1
        
        false_subnets.append({
            "port":             port,
            "vp" :              vp,
            "n_false_subnets" : n_false_subnets
        })
    
    unmapped_subnets.append({
        "port" :        port,
        "vp" :          vp,
        "n_unmapped" :  len(tree.unmapped_subnets)
    })

    tree.reset()

def to_df(l):
    return pd.DataFrame(l).sort_values(["port", "vp"])


entries = to_df(entries)

cols    = entries.columns.tolist()
cols    = [cols[-1], cols[-2], *cols[:-2]]

entries[cols].to_csv(output_file, index=False)

with open(output_file, "wt") as file:
    file.write(entries.to_csv(index=False))
    file.write(seperator)

    if target_asn != None:
        file.write("Number of responsive subnets that do not belong to AS3320 accoring to CAIDA data:\n")
        file.write(to_df(false_subnets).to_csv(index=False))
        file.write(seperator)

    file.write("Unmapped Subnets:\n")
    file.write(to_df(unmapped_subnets).to_csv(index=False))