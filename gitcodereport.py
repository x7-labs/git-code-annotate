#!/usr/bin/env python3
import pickle

import os
from gitcodeannotate import Annotation
from gitcodeannotate import read_config
from gitcodeannotate import convert_annotation_to_txt
from gitcodeannotate import options
def h(msg,heading):
    print(msg)
    print(heading * len(msg))

headings = {
        "chapter":"*",
        "section":"=",
        "subsection":"*",
        "subsubsection":"*",
}

def h1(msg):
    h(msg,headings['chapter'])

def h2(msg):
    h(msg,headings['section'])

def h3(msg):
    h(msg,headings['subsection'])

def txt(msg=""):
    print(msg)

def table(a):
    w= len(a[0])
    h= len(a)
    sizes=[]
    for i in range(0,w):
        max=0
        sizes.append(0)
        for r in range(0,h):
            l = len(a[r][i])
            if l >= sizes[i]:
                sizes[i] = l

    txt("+" + "+".join(["-" * x for x in sizes])+ "+")
    for r in range(0,h):
        fmt = "|" + "|".join(["{:%ds}" % x for x in sizes]) + "|"
        txt(fmt.format(*a[r]))
        txt("+" + "+".join(["-" * x for x in sizes])+ "+")
    txt()

def main():
    read_config()
    annotations = pickle.load( open("annotations.p","rb"))
    warning_count =0
    issue_count =0
    warnings=0
    issues=0
    h1("Code annotation report")
    txt()
    txt("""Code annotation report
    """)
    h2("Summary")
    txt()

    if os.path.isfile("summary.txt"):
        txt()
        with open('summary.txt', 'r') as file:
            txt(file.read())
    b = []
    types = {}
    for a in annotations:
        # convert tags to a dict
        d = {i[0]:i[1] for i in a.tags}
        keys = d.keys()
#        for tag in a.std_tags:
#            if tag in d.keys():
#                print("{:10s}:{}".format(tag, d[tag]))

        if "importance" in keys:
            #print("'{}'".format(d["importance"]))
            if d["importance"] in ["Low"]:
                #print("Skipping annotation (low priotity)")
                continue

        if "warning" not in keys and "issue" not in keys:
            #print("Skipping annotation (non issue/warning) {}".format(d))
            continue

        if "type" in keys:
            val = d["type"]
            if val in types.keys():
                types[val] += types[val] + 1
            else:
                types[val] = 1

        b.append(a)
        if "issues" in d.keys():
            issue_count += int(d["issues"])

        if "warnings" in d.keys():
            warning_count += int(d["warnings"])

        if "issue" in d.keys():
            issues += 1

        if "warning" in d.keys():
            warnings += 1

    t = []
    t.append(["Annotation count", "%d" % len(b)])
    t.append(["Warning count", "%d" % warnings])
    t.append(["Issue count", "%d" % issues])
    table(t)

    t = []
    for i in types.keys():
        t.append([i,str(types[i])])
    table(t)
    
    h2("Annotations (Medium and High)")

    for a in b:
        t = []
        line = a.source_start + a.a_start
        line_annotated = a.context[a.a_start][0]
        txt()
        base = options.base_url
        annotated =options.annotation_url
        t.append(['url',' `src <{}{}#L{}>`__ | `annotated <{}{}#L{}>`__'.format(base,a.file,line,annotated,a.file,line_annotated,a.file,line_annotated)])

        for tag in a.tags:
            if tag[0] in ['warning','issue','importance','type']:
                t.append([tag[0].capitalize(),tag[1].replace("\n"," ")])
        #print(len(t))
        #print(a.tags)
        table(t)
        print()
        print(".. code-block:: c")
        print("")
        print("    " + "\n    ".join(convert_annotation_to_txt(a).split("\n")))
        print("")
if __name__ == "__main__":
    main()
