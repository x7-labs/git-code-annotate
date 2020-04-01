#!/usr/bin/env python3
from unidiff import PatchSet
import re
import sys
import os.path
import traceback
import subprocess
import yaml
import sys
import argparse

current_version = 2

default_configuration ="""
#
# Configuration for the git-code-annoate tool
# https://github.com/x7-labs/git-code-annotate
#
config:
# When doing annotations the "untouched" code is normally on a different branch
# e.g. the master branch and the annotation tool is being run on an annotation branch
# that is expected to be the currently checked out branch. All changes on the
# annotation branch are considered annotations.. unless the commit message starts the word
# "dev". This allows to commit changes to this script or the outout of this script
# into the annotation branch
    branch_under_review: origin/master

# When generating rst code links are greated to the original source code that is expected
# to be hosted somewhere. base_url gets concatnated with the modified file
    base_url: "https://gitlab.com/myuser/annotation-tool/-/blob/master/"
    version: {}
""".format(current_version)

default_configuration_file_name =".git-code-annotate.yml"

class Annotation:
    def __init__(self, f_name, a_start):
        self.std_tags = [ 'reviewer','issues','warnings','issue','warning','include','review','notes']
        self.std_tags.append("issuses")
        self.tags = list()

        self.context = list()
        self.file = f_name        # file where the annotation applies
        self.start  = a_start      # diff start 
        self.a_start = None
        self.a_end = 0 #not set to None for start_new_annotation

        self.is_inline_comment = False
        self.include_length = 0 # amount of lines to include in the report
        self.include_contents =list()

    def start_new_annotation(self):
        # it happens that within a single chunk you have multiple annotations
        # this code detect this so we can do a new annotation
        #print("context {} . start {}, end {}".format(len(self.context), self.a_start, self.a_end))
        if len(self.context) > self.a_end and self.a_start:
            return True
        return False

    def addContext(self, context,is_annotation=False):
        self.context.append(context)

        if is_annotation:
            self.a_end = len(self.context) 

        if is_annotation and not self.a_start:
            self.a_start = len(self.context) -1

    def setIncludeLength(self, length):
        self.include_length = length

def first_non_none(list):
    for i in list:
        if i:
            return i
    return ""

def _post_process_annotation(a):
    """ Process the annotation and do some magic parsing on the rst contents """

    #print("context:{} start:{} end:{} ".format(len(a.context), a.a_start, a.a_end))
    #print("Looking at file {}:{} :\n".format(a.file,a.context[a.a_start][0]) + "\n".join([ "{} {:4d} :{}".format("A" if (i >= a.a_start and i < a.a_end)  else " ", a.context[i][0],a.context[i][1]) for i in range(len(a.context)) ]))
    # matches /* and */
    empty_comment = re.compile('^\W*/\*\W*$|^\W*\*\/\W*$')

    # matches comment markers return the remainder
    patterns = [
        "^\W*#(.*)$",     # matches #
        "^\W*//(.*)$",    # matches //
        "^\W*\*(.*)\*/$", # mathces /* content */
        "^\W*/\*(.*)$",   # matches /* (start of comment)
        "^\W*\*/(.*)$",   # matches */ (end of comment)
        "^\W*\*(.*)$",    # matches  * (like javadoc style multiline)
     
    ]
    line_start_by_comment = re.compile("|".join(patterns))

    line_start_by_space = re.compile('^\W{1,2}')
    line_start_by_indent = re.compile('^\W{2,}')

    # it is allowed to embed commands in the rst content the format is
    # key:value if those this regex finds these items
    tags_re = re.compile('(\w+):(.*)')

    # Remove empty or last comment line if empty
    for i in [a.a_start, a.a_end]:
        if empty_comment.match(a.context[i][1]):
            a.context[i][1] =""

    # Check if the first line of the annotation is indented if so..
    # Assume an inline comment (we will by default show more context)
    if line_start_by_indent.match(a.context[a.a_start][1]):
            a.is_inline_comment = True

    # Remove leading # or /* and * // and also c** style /* */ comments
    for i in range(a.a_start,a.a_end):
        c = a.context[i][1]
        if line_start_by_comment.match(c):
            remainder = first_non_none(line_start_by_comment.match(c).groups())
            a.context[i][1] = remainder
    
    # parse for tags
    in_tag = False
    last_tag = None
    for i in range(a.a_start, a.a_end):
        c = a.context[i][1]
        #print("YP {}".format(c))
        # bug??
        if c is None:
            print("WOT C NONE {} {}".format(i,len(a.rst)))
        if tags_re.match(c):
            in_tag = True
            command,value = tags_re.match(c).groups()
            a.tags.append([command.lower(),value])
            if command.lower() not in a.std_tags:
                print("Unknown tag %s" % command)
            last_tag = command
            continue

        if in_tag and line_start_by_space.match(c):
                a.tags[len(a.tags)-1][1]=  a.tags[len(a.tags)-1][1]  +"\n" + value
                print("Multline tag %s -- %s" % (last_tag,c))
                continue

        in_tag = False
    pre_lines = 3

    start = a.a_start - pre_lines 
    if not a.is_inline_comment:
        start += pre_lines

    print("Looking at file {}:{} :\n".format(a.file,a.context[a.a_start][0]) + "\n".join([ "{} {:4d} :{}".format("A" if (i >= a.a_start and i < a.a_end)  else " ", a.context[i][0],a.context[i][1]) for i in range(start,len(a.context)) ]))
    print("")
    return a

def create_annotations_from_patch(patch):
    # This is where the magic happens, a unified diff formatted patch 
    # as for example created by git diff get parsed. To make things easy
    # the patch is created with the -U0 option (no context lines)
    # a patch gets converted into annotations
    # PatchSet does not accept a single string e.g. something goes
    # wrong when a non iterable object gets passed.
    annotations = list()
    try:
        pset = PatchSet(patch)
        for mod_files in pset.modified_files:
            # Parse hunks , create annotation 

            for hunk in mod_files:
                a = Annotation(mod_files.path,hunk.source_start)
                offset = 0
                for line in hunk.target:
                    if line[0] == '+':
                        if a.start_new_annotation():
                            annotations.append(_post_process_annotation(a))
                            b = Annotation(mod_files.path,hunk.source_start)
                            for i in a.context:
                                b.addContext(i)
                            a = b
                        a.addContext([hunk.source_start + offset,format(line[1:].rstrip())],True)
                    #keep track of the offset compared to the hunk
                    elif line[0] not in ['+','-']:
                        a.addContext([hunk.source_start + offset,format(line.rstrip())])
                    if line[0] != '-':
                        offset += 1
                annotations.append(_post_process_annotation(a))
 

    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(2)
    return annotations

#
# the rest of this script is more about .. formating and generating rst for the annotations
#
def convert_annotation_to_rst(a,base_url):
    file_name = "{} line {}".format(a.file, a.start)
    file_link = "{}{}#L{}".format(base_url,a.file,a.start)
    lines =[ i[1] for i in a.context]
    return "\n".join(lines) + "\n\nSource: `{} <{}>`_".format(file_name ,file_link) + "\n\n"

def do_verbatim_include(fh,a,revision):
    if a.include_length >0:
        cmd = "git show {}:{}".format(revision,a.file)
        data = subprocess.getoutput(cmd)
        selection = data.split("\n")[a.start:a.start + a.include_length]
        fh.write("\n.. code-block:: c\n\n    ")
        fh.write("\n    ".join(selection))
        fh.write("\n\n")

def do_run(top_level,branch_under_review,base_url):
    f1=open('git_code_annotations.rst', 'w',encoding='utf-8')

    # add some rst to force the heading order
    f1.write ("Annotation report\n")
    f1.write ("*****************\n\n")

    #
    # Special handing for uncommited changes do a diff and produce the output
    #
    data  = subprocess.getoutput("git diff")
    if len(data) >0:
        f1.write ("\n\n")
        f1.write (".. note::\n\t\tAnnotation contains uncommited changes\n\n")

    # By default compare against the master branch
    base_commit=branch_under_review

    # List commits on this branch and find the first non "dev:" commit
    # Based on this do a git diff including all the commits
    output  = subprocess.getoutput("git log %s... --oneline" % branch_under_review)
    commits = map(str.strip,output.split("\n"))
    for commit in commits:
        commit_regex = re.compile('^([0-9a-f]*) (.*)')
        if not commit_regex.match(commit):
            continue

        id,message = commit_regex.match(commit).groups()

        if message.startswith("dev"):
            print("Base commit is %s" % commit)
            diff_commit=id
            break

    #data  = subprocess.getoutput("git diff %s" % base_commit)
    data  = subprocess.getoutput("git diff  -U10 %s" % base_commit)
    annotations = create_annotations_from_patch(data)
    for a in annotations:
        f1.write ("\n")
        f1.write(convert_annotation_to_rst(a,base_url))
        do_verbatim_include(f1,a,branch_under_review)

    f1.close()

def main():
    parser = argparse.ArgumentParser(prog='git-code-annotate')
    parser.add_argument('--generate_config', action="store_true")
    parser.add_argument('--show_diff', action="store_true")
    args = parser.parse_args()

    p = subprocess.run("git rev-parse --show-toplevel", capture_output=True, shell=True, text=True)
    if p.returncode != 0:
        print("git-code-annotate: failed to determine git top level directory")
        sys.exit(2)

    top_level = p.stdout.strip()
    config_file= os.path.join(top_level,default_configuration_file_name)

    if args.generate_config:
        print("\nCreated a new configuration file: %s. to add it to the git repository and skip it from annocation please commit it using the following message 'dev:add git-code-annotate config' e.g. \n\n git add %s \n git commit -m \"dev:add .git-code-annotate config\" " % (config_file,config_file))
        with open(config_file, 'w', encoding='utf-8') as ymlfile:
            ymlfile.write(default_configuration)
            ymlfile.close()
            return

    if os.path.isfile(config_file):
        with open(config_file, 'r',encoding='utf-8') as ymlfile:
            cfg = yaml.load(ymlfile,Loader=yaml.BaseLoader)
    else:
        cfg = yaml.load(default_configuration,Loader=yaml.BaseLoader)
    #
    # When doing annotations the "untouched" code is normally on a different branch
    # e.g. the master branch and the annotation tool is being run on an annotation branch
    branch_under_review= cfg['config']['branch_under_review']
    base_url= cfg['config']['base_url']
    version = int("1")
    if 'version' in cfg['config']:
        version = int(cfg['config']['version'])

    if version > current_version:
        print("ERROR:Detected a more recent version of the configuration. Upgrade git-code-annotate")
        sys.exit(2)
    
    do_run(top_level,branch_under_review,base_url)

if __name__ == "__main__":
    main()
