import tempfile
import subprocess
import json
import os
from icecream import ic

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

    def to_treeview(self):
        return {'text':self.id,'nodes':dict_to_tree(self.infos,keys_to_ignore=["id"])}



