import pandas   as pd

from os.path    import dirname, basename
from glob       import glob
from itertools  import combinations
from typing     import Dict, List, Tuple


dir         = dirname(__file__)
parent_dir  = dirname(dir)
data_dir    = f"{parent_dir}/data"

csv_dir     = f"{data_dir}/split/censys_2022_03"
output_file = f"{data_dir}/results/2022_03_intersection.txt"




seperator   = "\n-----------------------------------------------\n\n"

def merge_dataframes(dataframes, how):
    df = dataframes[0]

    for new_df in dataframes[1:]:
        df = pd.merge(df, new_df, how=how)
    
    return df


def run_combination(vps : Dict[str, pd.DataFrame], combination : List[Tuple[str]]):
    dataframes = [vps[vp] for vp in combination]

    inter = merge_dataframes(dataframes, "inner")
    union = merge_dataframes(dataframes, "outer")

    return len(inter["subnet"]), len(union["subnet"])

    



def vp_responsiveness_intersection(port):
    """
    calculates the intersection of responsive subnets per vantage point given a port
    """

    # load vantage points
    vps     = {}

    for filepath in glob(f"{csv_dir}/{port}_*.csv"):
        filename    = basename(filepath).split(".")[0]

        vp          = filename.split("_")[1]
        vps[vp]     = pd.read_csv(filepath, header=None, names=["subnet"])


    # generate combinations
    all_combinations = []

    for i in range(2, len(vps) + 1):
        all_combinations += combinations(vps, i)
    
    results = [
        f"Port {port}" + ","*len(vps) + "inter,union,ratio"
        ]


    for i, combination in enumerate(all_combinations):
        print(f"\tWorking on combination {combination} ({i+1}/{len(all_combinations)})")
        
        inter, union = run_combination(vps, combination)

        vps_s = ",".join(combination) + "," * (len(vps) - len(combination))

        results.append(f"{vps_s},{inter},{union},{inter/union}")
    
    print()
    
    return results



ports           = [22, 53, 80]
final_results   = []

for i, port in enumerate(ports):
    print(f"Working on Port {port} ({i+1}/{len(ports)})")

    final_results += vp_responsiveness_intersection(port)
    final_results.append(seperator)


with open(output_file, "wt") as file:
    for line in final_results:
        file.write(line + "\n")