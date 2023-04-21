import pandas       as pd
from associate_as   import AS_Tree
from os.path        import dirname, basename
from glob           import glob
from argparse       import ArgumentParser


dir         = dirname(__file__)
parent_dir  = dirname(dir)
data_dir    = f"{parent_dir}/data"


parser = ArgumentParser()
parser.add_argument("input_dir",                                    help="Directory name with all subnets split into files by date (inside data/split/)")
parser.add_argument("output_file",                                  help="Filename where the output of this script should be stored (inside data/results/)")
parser.add_argument("-np", "--no-pickle",   action="store_true",    help="Whether the script should load and save the routeviews using pickle (Uses less storage, takes more time)")

args = parser.parse_args()


csv_dir     = f"{data_dir}/split/{args.input_dir}"
output_file = f"{data_dir}/results/{args.output_file}"
use_pickle  = not args.no_pickle


print(f"Analyzing all files in '{csv_dir}' and saving output to '{output_file}'")


entries = []

matching_files = glob(f"{csv_dir}/*.csv")

for i, filepath in enumerate(matching_files):
    filename = basename(filepath).split(".")[0]
    print(f"Working on {filename} ({i + 1}/{len(matching_files)})")

    year, month, day = filename.split("-")

    routeview = f"{data_dir}/routeviews/routeviews-rv2-{year}{month}{day}-*.pfx2as"

    matching_routeviews = list(glob(routeview))

    while len(matching_routeviews) == 0:
        input(f"Cannot find routeview for {year}-{month}-{day}'. Please download, put it in the folder and then press enter to continue.")
        matching_routeviews = list(glob(routeview))

    if len(matching_routeviews) > 1:
        print("Multiple files matching!", matching_routeviews)
        print()
        print(entries)
        raise Exception()
    
    tree    = AS_Tree(matching_routeviews[0], use_pickle=use_pickle)

    with open(filepath, "r") as f:
        responded_subnets = [x.strip() for x in f.readlines()]
        
    tree.count_subnet_occurence(responded_subnets)
    as_responses = tree.count_as()

    final_entry = {
        "date"          : filename,
        "responsive"    : 0,
        "total"         : 0,
        "n_unmapped"    : len(tree.unmapped_subnets)
    }

    for entry in as_responses.values():
        final_entry["responsive"]   += entry["responsive"]
        final_entry["total"]        += entry["total"]
    
    final_entry["ratio"] = final_entry["responsive"] / final_entry["total"]


    entries.append(final_entry)



entries = pd.DataFrame(entries)

print(entries)

entries = entries.sort_values("date")

# cols    = entries.columns.tolist()
# cols    = [cols[-1], cols[-2], *cols[:-2]]

entries.to_csv(output_file, index=False)

