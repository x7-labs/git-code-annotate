#!/usr/bin/env python3
import pickle

from gitcodeannotate import Annotation
from gitcodeannotate import read_config

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
    h1("Code annotation report")
    txt()
    txt("""Code annotation report
    """)
    h2("Summary")
    txt()

    for a in annotations:
        # convert tags to a dict
        d = {i[0]:i[1] for i in a.tags}

#        for tag in a.std_tags:
#            if tag in d.keys():
#                print("{:10s}:{}".format(tag, d[tag]))

        if "issues" in d.keys():
            issue_count += int(d["issues"])

        if "warnings" in d.keys():
            warning_count += int(d["warnings"])

    t = []
    t.append(["Annotation count", "%d" % len(annotations)])
    t.append(["Warnings", "%d" % warning_count])
    t.append(["Issues", "%d" % issue_count])
    table(t)

if __name__ == "__main__":
    main()
