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
    def __init__(self):
        self.info  = ""
        self.file = None        # file where the annotation applies
        self.rst =list()
        self.start  = None      # diff start 
        self.length = None      # diff length
        self.include_length = 0 # amount of lines to include in the report
        self.include_contents =list()

    def setInfo(self, info):
        self.info = info

    def setFile(self, myfile):
        self.file = myfile

    def addRst(self, rst):
        self.rst.append(rst)

    def setStart(self, start):
        self.start = start

    def setLength(self, length):
        self.length = length

    def setIncludeLength(self, length):
        self.include_length = length


def _post_process_annotation(a):
    """ Process the annotation and do some magic parsing on the rst contents """

    # matches /* and */
    empty_comment = re.compile('^/\*$|^\*/$')

    # matches # and // at start of line return the remainder
    line_start_by_comment = re.compile('^#(.*)|^//(.*)')

    # it is allowed to embed commands in the rst content the format is
    # key:value if those this regex finds these items
    commands = re.compile('([A-Z]+):(.*)')

    # Remove first or last comment line if empty e.g. /*
    if len(a.rst) > 0:
        if empty_comment.match(a.rst[0]):
            a.rst = a.rst[1:]
    if len(a.rst) > 0:
        if empty_comment.match(a.rst[-1]):
            a.rst = a.rst[:-1]

    # remove leading # or //
    for i in range(0,len(a.rst)):
        c = a.rst[i]
        if line_start_by_comment.match(c):
            remainder = line_start_by_comment.match(c).groups()[0]
            a.rst[i] = remainder
    
    # parse for commands
    for i in range(0,len(a.rst)):
        c = a.rst[i]
        if commands.match(c):
            command,value = commands.match(c).groups()
            if command == "INCLUDE":
                a.setIncludeLength(int(value))
                a.rst[i] = ""
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
        for pfile in pset.modified_files:
            # Parse hunks , create annotation 
            for hunk in pfile:
                contents =list()
                a = Annotation()
                a.setFile(pfile.path)
                a.setStart(hunk.source_start)
                a.setLength(hunk.target_length)

                for line in hunk.target:
                    if line[0] == '+':
                        a.addRst(line[1:].rstrip())
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
    return "\n".join(a.rst) + "\n\nSource: `{} <{}>`_".format(file_name ,file_link) + "\n\n"

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
    data  = subprocess.getoutput("git diff  -U0")
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

    data  = subprocess.getoutput("git diff  -U0 %s" % base_commit)
    annotations = create_annotations_from_patch(data)
    for a in annotations:
        f1.write ("\n")
        f1.write(convert_annotation_to_rst(a,base_url))
        do_verbatim_include(f1,a,branch_under_review)

    f1.close()




def main():
    parser = argparse.ArgumentParser(prog='git-code-annotate')
    parser.add_argument('--view', action="store_true")
    parser.add_argument('--generate_config', action="store_true")
    args = parser.parse_args()

    if args.view:
        cmd = "restview git_code_annotations.rst"
        print("Invoking: %s" % cmd)
        p = subprocess.run(cmd, capture_output=True, shell=True, text=True)
        if p.returncode != 0:
            print("git-code-annotate: failed to launch restview")
            print(p.stdout)
            print(p.stderr)
            sys.exit(p.returncode)
        sys.exit(0)


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

    if os.path.isfile(config_file):
        with open(config_file, 'r',encoding='utf-8') as ymlfile:
            cfg = yaml.load(ymlfile,Loader=yaml.BaseLoader)
    else:
        cfg = yaml.load(default_configuration,Loader=yaml.BaseLoader)
    #
    # When doing annotations the "untouched" code is normally on a different branch
    # e.g. the master branch and the annotation tool is being run on an annotation branch
    # that is expected to be the currently checked out branch. All changed on the 
    # annotation branch are considered annotations.. unless the commit message starts the word
    # "dev". This allows to commit changes to this script or the outout of this script 
    # into the annotation branch
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
