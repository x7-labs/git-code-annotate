#!/usr/bin/env python3

import gitcodeannotate as ga

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
                sizes[i] = l + 2

    txt("+" + "+".join(["-" * x for x in sizes])+ "+")
    for r in range(0,h):
        fmt = "|" + "|".join(["{:%ds}" % x for x in sizes]) + "|"
        txt(fmt.format(*a[r]))
        txt("+" + "+".join(["-" * x for x in sizes])+ "+")
    txt()


def main():
    ga.read_config()
    print(ga.options.link)
    annotations = ga.create_annotations_from_patch( open("annotations.p").read())

    acceptable_tags =  ['warning','issue','importance','type','note','todo']
    b = []
    for a in annotations:
        # convert tags to a dict
        d = {i[0]:i[1] for i in a.tags}
        keys = d.keys()

        if len(a.tags) == 0 or a.tags[0][0] not in acceptable_tags:
            continue

        if "importance" in keys:
            #print("'{}'".format(d["importance"]))
            if d["importance"] in ["Low"]:
                #print("Skipping annotation (low priotity)")
                continue

        b.append(a)

    t = []
    if len(t) > 0:
        table(t)
    h2("Annotations")

    for a in b:
        t = []
        line = a.source_start + a.a_start - ga.options.pre_lines
        #print(a.source_start)
        #print(a.a_start)
        line_annotated = a.context[a.a_start][0]
        txt()
        base = ga.options.base_url
        annotated = ga.options.annotation_url
        if ga.options.link:
            t.append(['url',' `src <{}{}#L{}>`__ | `annotated <{}{}#L{}>`__'.format(base,a.file,line,annotated,a.file,line_annotated,a.file,line_annotated)])

        for tag in a.tags:
            if tag[0] in acceptable_tags:
                t.append([" " + tag[0].capitalize()," " + tag[1].replace("\n"," ")])
        #print(len(t))
        #print(a.tags)
        table(t)
        print()
        a_name = f"{a.file}:{a.source_start + a.a_start}"
        print(".. code-block:: c")
        if ga.options.sphinx:
            print(f"    :name: {a_name}")
            print(f"    :caption: {a_name}")
            print(f"    :linenos:")
            print(f"    :lineno-start: {line}")
            print(f"    :emphasize-lines: {ga.options.pre_lines +1}")
            print("")
            print("    " + "\n    ".join(ga.convert_annotation_to_sphinx(a).split("\n")))
            print("")
        else:
            print("")
            print("    " + "\n    ".join(ga.convert_annotation_to_rst(a).split("\n")))
            print("")
if __name__ == "__main__":
    main()
