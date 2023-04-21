import ipaddress, pickle

from os.path            import dirname, split, exists
from collections.abc    import Iterable

import pandas           as pd




def ip_to_bin(ip):
    ip  = ipaddress.ip_address(ip)

    s   = bin(int.from_bytes(ip.packed, byteorder="big"))[2::]
    return s.rjust(32, "0")

def convert_asn(asn: str) -> set:
    """
    Takes asn and returns a set of asns. This is done because multiple AS can claim the same subnet
    """
    asns = set()

    for s in asn.split("_"):
        for s in s.split(","):
            asns.add(s)
    
    return asns


class AS_Tree:
    """
    Binary tree which allows for quick lookup of what subnets belong to which AS
    """
    nodes       = {}
    multiple_as = {}

    unmapped_subnets: list
    as_responses: dict
    _pickle_file: str
    _use_pickle: bool

    def __init__(self, as_caida_file, use_pickle=True) -> None:
        filedir, file       = split(as_caida_file)
        filename            = file.split(".")[0]

        self._use_pickle     = use_pickle
        if use_pickle:

            self._pickle_file   = f"{filedir}/{filename}.pickle"

            if exists(self._pickle_file):
                f           = open(self._pickle_file, "rb")
                self.nodes  = pickle.load(f)
                return

        df = pd.read_csv(as_caida_file, sep="\t", names=["subnet", "s_mask", "ASN"], header=None)

        df["s_mask"]    = pd.to_numeric(df["s_mask"])
        df              = df.sort_values("s_mask")
        df              = df[df["s_mask"] <= 24]

        for _, row in df.iterrows():
            ip_s, subnet_mask, asn = row["subnet"], row["s_mask"], row["ASN"]

            ip_bin  = ip_to_bin(ip_s)
            asns    = convert_asn(asn)
            
            if len(asns) > 1:
                self.multiple_as[ip_s] = asn

            tree = self.nodes
            for bit in ip_bin[:subnet_mask]:
                if bit not in tree:
                    tree[bit] = {}
                
                tree = tree[bit]
            
            if "sys" not in tree:
                tree["sys"] = {
                    "s_mask":   subnet_mask,
                    "count":    0,
                    "asn":      asns,
                }
        
        if use_pickle:
            f = open(self._pickle_file, "wb")
            pickle.dump(self.nodes, f)


    def count_subnet_occurence(self, responded_subnets):
        """
        Receives a list of subnets that responded. For ech responded subnet we add 1 to the count of whichever larger subnet that subnet belongs to.
        If the subnet is not claimed by any AS, we add it to the unmapped subnets
        """
        self.unmapped_subnets = []

        for subnet in responded_subnets:
            ip_bin = ip_to_bin(subnet)

            try:
                a_sys = self.walk_path(ip_bin, last_sys=True)
                a_sys["count"] += 1
            
            except (KeyError, TypeError):
                self.unmapped_subnets.append(subnet)
    
    def count_as(self):
        """
        Generates number of subnets that responsed and the total amount of subnets for each AS
        """
        self.as_responses = {}

        for _, node in self:

            for asn in node["asn"]:

                if asn not in self.as_responses:
                    self.as_responses[asn] = {
                        "responsive" : 0,
                        "total" : 0
                    }
                
                self.as_responses[asn]["responsive"] += node["count"]
                self.as_responses[asn]["total"]      += 2 ** (24 - int(node["s_mask"]))
        
        return self.as_responses


    def walk_path(self, path, stop_sys=False, last_sys=False):
        """
        Walks self.nodes along given path and returns result. 
        If stop_sys=True then it returns the first "sys" entry it finds. 
        If last_sys=True then it returns the last "sys" it encounters.
        """
        tree        = self.nodes
        latest_sys  = None

        for bit in path:
            if "sys" in tree:
                if stop_sys:
                    return tree["sys"]
                
                latest_sys = tree["sys"]
            
            if bit not in tree and last_sys:
                return latest_sys
            
            tree = tree[bit]
        
        if last_sys:
            return latest_sys
    
        return tree


    def calc_ratio(self):
        """
        Calculates the ratios for each AS
        """
        as_entries = []

        for asn, as_entry in self.as_responses.items():
            as_entry["ratio"]   = as_entry["responsive"] / as_entry["total"]
            as_entry["asn"]     = asn

            as_entries.append(as_entry)

    
        return sorted(as_entries, key=lambda d: d['responsive'], reverse=True)
    
    def calc_overall_ratio(self):
        responsive  = 0
        total       = 0

        for as_entry in self.as_responses.values():
            responsive  += as_entry["responsive"]
            total       += as_entry["total"]
        
        return responsive, total, responsive / total

    def reset(self):
        """
        Resets all values in the tree
        """
        self.multiple_as = {}

        if self._use_pickle and exists(self._pickle_file):
            f           = open(self._pickle_file, "rb")
            self.nodes  = pickle.load(f)
            return

        for _, entry in self:
            entry["count"] = 0


    def analyze_tree(self, in_csv):
        with open(in_csv, "r") as f:
            responded_subnets = [x.strip() for x in f.readlines()]
        
        self.count_subnet_occurence(responded_subnets)
        self.count_as()

        return self.calc_ratio()


    def __getitem__(self, _key):
        if isinstance(_key, Iterable) and len(_key) != 1:
            return self.walk_path(_key)
    

        return self.nodes[_key]


    def __iter__(self, tree=None, path=""):
        """
        Iterates over each entry in the tree and yields path as well as the node
        """

        if tree == None:
            tree = self.nodes
        
        if "sys" in tree:
            yield path, tree["sys"]

        for branch in ["0", "1"]:
            if branch in tree:
                yield from self.__iter__(tree[branch], path + branch)
    



def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def read_subnet(in_csv):    
    with open(in_csv, "r") as f:
        return [x.strip() for x in f.readlines()]





if __name__ == "__main__":
    raise Exception("This file is not supposed to be run on it's own and only serves to be imported from other files. Consider running other associate_as.py scripts")