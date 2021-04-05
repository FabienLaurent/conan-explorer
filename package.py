import tempfile
import subprocess
import json
import os
from icecream import ic
from functools import reduce

def call_conan(*args):
    out = {}
    tmp = tempfile.mktemp()
    subprocess.run(["conan"] + list(args) + ["--json", tmp])
    
    with open(tmp, "r") as f:
        out = json.load(f)
    os.remove(tmp)
    return out


class Reference:
    def __init__(self, infos: dict):
        self.ref = infos['recipe']['id']
        self.get_packages()
        self.infos = call_conan("info","--paths",self.ref)[0]
        
    def get_packages(self):
        infos = call_conan("search", self.ref)
        self.packages = []
        for r in infos['results']:
            for i in r['items']:
                for p in i['packages']:
                    self.packages.append(Package(p))
        common_infos = reduce(lambda x, y: dictdiff(x, y, only_common=True), [p.infos for p in self.packages])
        [p.substract_common_infos(common_infos) for p in self.packages]

    def info_to_tree(self):
        tmp = dict_to_tree(self.infos,keys_to_ignore=["id"])
        return {'text':'infos','backColor':'#77DD77','nodes':tmp}

    def to_treeview(self):
        return {'text':self.ref,'state.expanded':False,'nodes':[self.info_to_tree()] + [p.to_treeview() for p in self.packages]}

def dict_to_tree(info: dict,keys_to_ignore=[]):
    out = []
    for k, v in info.items():
        if k in keys_to_ignore:
            continue
        if not v:
            continue
        if isinstance(v, dict):
            out.append({'text': str(k), 'nodes': dict_to_tree(v)})
        else:
            tmp = {'text': f"{k} = {v}"}
            if k.lower() == "url":
                tmp['href'] = v
            if isinstance(v, str):
                if v.startswith("http"):
                    tmp['href'] = v
                if os.path.isdir(v) or os.path.isfile(v):
                    tmp['href'] = f'http://127.0.0.1:5000/{v}'
                
            out.append(tmp)
    return out

class Package:
    def __init__(self, infos: dict):
        self.id = infos['id']
        self.infos = infos
        self.unique_infos = {}
        self.name = self.id
        assert isinstance(self.infos,dict)

    def to_treeview(self):
        return {'text': self.name, 'nodes': dict_to_tree(self.infos)}
        
    def substract_common_infos(self, common: dict):
        assert isinstance(common,dict)
        _, self.unique_infos, _ = dictdiff(self.infos, common)
        
        def info_to_str(to_analyze: dict):
            name = ""
            for k, v in to_analyze.items():
                if not v or k=='id':
                    continue
                if k in ['requires','options','settings']:
                    name += f"{k[0]}:{v} "
                else:
                    name += f"{k}:{v} "
            return name

        self.name = info_to_str(self.unique_infos)
        if not (self.name):
            self.name = info_to_str(self.infos)
        if not (self.name):
            self.name = self.id

def dictdiff(d1, d2, only_common=False):
    only1 = {}
    only2 = {}
    common = {}
    if not only_common:
        for k in set(d1.keys()) - set(d2.keys()):
            only1[k] = d1[k]
        for k in set(d2.keys()) - set(d1.keys()):
            only2[k] = d2[k]
    for k in set(d1.keys()).intersection(set(d2.keys())):
        if type(d1[k]) != type(d2[k]) and (not only_common):
            only1[k] = d1[k]
            only2[k] = d2[k]
        elif isinstance(d1[k], dict):
            if only_common:
                common[k] = dictdiff(d1[k], d2[k], True)
            else:
                common[k], only1[k], only2[k] = dictdiff(d1[k], d2[k],False)
        elif isinstance(d1[k], list):
            only1[k] = list(set(d1[k]) - set(d2[k]))
            only2[k] = list(set(d2[k]) - set(d1[k]))
            common[k] = list(set(d2[k]).intersection(set(d1[k])))
        elif d1[k] == d2[k]:
            common[k] = d1[k]
        else:
            only1[k] = d1[k]
            only2[k] = d2[k]
    
    if only_common:
        return common
    else:
        return (common,only1,only2)