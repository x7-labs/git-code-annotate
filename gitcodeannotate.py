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
import pickle

current_version = 7

default_configuration ="""#
# Configuration for the git-code-annoate tool
# https://github.com/x7-labs/git-code-annotate
#
config:
    version: {}
# When doing annotations the "untouched" code is normally on a different branch
# e.g. the master branch and the annotation tool is being run on an annotation branch
# that is expected to be the currently checked out branch.
    branch_under_review: origin/master

# When generating code links are greated to the original source code that is expected
# to be hosted somewhere. base_url gets concatnated with the name of the modified file
    base_url: "https://gitlab.com/myuser/annotation-tool/-/blob/master/"

# if tags_only is set to true only accept tag:value contents (no free form)
    tags_only: True
""".format(current_version)

default_configuration_file_name =".git-code-annotate.yml"

class Options:
    def __init__(self):
        self.base_url = ""
        self.branch_under_review = None
        self.tags_only = False
        self.pre_lines = 3

options = Options()
warnings= list()

def warn(message):
    global warnings
    warnings.append(message)
    print(message)

def warn_exit(message):
    warn(message)
    sys.exit(2)

class Annotation:
    def __init__(self, f_name, source_start, target_start):
        self.std_tags = [ 'issues','reviewer','verifier','warnings','issue','warning','include','review','note','notes','todo','fix','question','suspicious','summary']
        self.tags = list()
        self.context = list()
        self.file = f_name                # file where the annotation applies
        self.target_start  = target_start # diff target start
        self.source_start  = source_start # diff source start
        self.a_start = None               # start of the acutal annotation
        self.a_end = 0                    #not set to None for start_new_annotation
        self.is_inline_comment = False    # inline annotation get a different treatment

    def start_new_annotation(self):
        # it happens that within a single chunk you have multiple annotations
        # this code detect this so we can do a new annotation
        if len(self.context) > self.a_end and self.a_start:
            return True
        return False

    def addContext(self, context,is_annotation=False):
        # handle start of annotation
        if not self.a_start and is_annotation:
            self.a_start = len(self.context)

        self.context.append(context)

        # make sure we always have a valid end to the annotation
        if is_annotation:
            self.a_end = len(self.context)

def shell(cmd,err_message):
    p = subprocess.run(cmd, capture_output=True, shell=True, text=True)
    if p.returncode != 0:
        warn_exit("%s Problem executing command %s\nreturn code: %d\nstdout:%s\n\nstderr:\n%s\n\n" %(err_message,cmd, p.returncode, p.stdout , p.stderr))
    return p

def convert_annotation_to_txt(a):
    start = a.a_start - options.pre_lines
    if not a.is_inline_comment:
        start += options.pre_lines
    start = max(start,0)

    # Who said python code has to be redable?
    return "Looking at file {}:{} :\n".format(a.file,a.context[a.a_start][0]) + "\n".join([ "{} {:4d} : {}".format("A" if (i >= a.a_start and i < a.a_end)  else " ", a.context[i][0],a.context[i][1]) for i in range(start,len(a.context)) ])

def _post_process_annotation(a):
    """ Process the annotation and do some magic parsing on the contents """

    # matches /* and */
    empty_comment = re.compile('^\W*/\*\W*$|^\W*\*\/\W*$')

    # matches comment markers and return the remainder
    patterns = [
        "^\W*#(.*)$",     # matches #
        "^\W*//(.*)$",    # matches //
        "^\W*\*(.*)\*/$", # mathces /* content */
        "^\W*/\*(.*)$",   # matches /* (start of comment)
        "^\W*(.*)\*/$",   # matches */ (end of comment)
        "^\W*\*(.*)$",    # matches  * (like javadoc style multiline)
    ]
    line_start_by_comment = re.compile("|".join(patterns))

    line_start_by_space = re.compile('^\W{1,2}')
    line_start_by_indent = re.compile('^\W{4,}|^\t')

    # it is encouraged to embed tags in the annotations. The format is
    # key:value if those this regex finds these items
    tags_re = re.compile('^\W{0,2}(\w+):(.*)')

    # Check if the first line of the annotation is indented if so assume an inline comment
    if line_start_by_indent.match(a.context[a.a_start][1]):
            a.is_inline_comment = True

    # Clean first / last line of annotation (may be an empty comment)
    for i in [a.a_start, a.a_end-1]:
        if empty_comment.match(a.context[i][1]):
            a.context[i][1] = ""

    # Remove leading # or /* and * // and also c** style /* */ comments
    for i in range(a.a_start, a.a_end):
        c = a.context[i][1]
        if line_start_by_comment.match(c):
            # because python regexp returns a list of groups when the *or* operator is used
            remainder = next((rem for rem in line_start_by_comment.match(c).groups() if not rem is None),"")
            #print("{} -> {}".format(c,remainder))
            a.context[i][1] = remainder

    # parse for tags
    in_tag = False
    last_tag = None
    for i in range(a.a_start, a.a_end):
        c = a.context[i][1]
        #print("YP {}".format(c))
        if tags_re.match(c):
            in_tag = True
            command,value = tags_re.match(c).groups()
            a.tags.append([command.lower(),value])
            if command.lower() not in a.std_tags:
                warn("Unknown tag {} in {}:{}".format(command,a.file,a.context[i][0]))
            last_tag = command
            continue

        if in_tag and line_start_by_indent.match(c):
            a.tags[len(a.tags)-1][1]=  a.tags[len(a.tags)-1][1]  +"\n" + value
            #print("Multline tag %s -%s-" % (last_tag,c))
            continue

        if options.tags_only and len(c) > 0:
            warn("Warning non tag line in {}:{} -{}-".format(a.file,a.context[i][0],c))
        in_tag = False
    return a

def create_annotations_from_patch(patch):
    # This is where the magic happens, a unified diff formatted patch
    # as for example created by git diff get parsed and gets converted
    # into annotations

    annotations = list()
    try:
        pset = PatchSet(patch)
        for mod_files in pset.modified_files:
            # Parse hunks , create annotation

            for hunk in mod_files:
                a = Annotation(mod_files.path, hunk.source_start, hunk.target_start)
                offset = 0
                for line in hunk.target:
                    if line[0] == '+':
                        if a.start_new_annotation():
                            # A single hunk can contain multiple annotations we create and annotation
                            # object for every section of added content
                            annotations.append(_post_process_annotation(a))
                            b = Annotation(mod_files.path, a.source_start, a.target_start)
                            # copy lines from the previous annotation for context
                            [ b.addContext(item,False) for item in a.context ]
                            a = b
                        a.addContext([hunk.target_start + offset,format(line[1:].rstrip('\n'))],True)
                    elif line[0] not in ['+','-']:
                        a.addContext([hunk.source_start + offset,format(line[1:].rstrip('\n'))],False)
                    #keep track of the offset compared to the hunk
                    if line[0] != '-':
                        offset += 1
                annotations.append(_post_process_annotation(a))
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(2)
    return annotations


def do_run(args):
    #global options
    # By default compare against the master branch
    base_commit=options.branch_under_review

    # List commits on this branch and find the first non "dev:" commit
    # Based on this do a git diff including all the commits
    output  = subprocess.getoutput("git log %s... --oneline" % base_commit)
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

    files=""
    if args.modified:
        cmd_output  = subprocess.getoutput("git diff --name-only")
        file_list = map(str.strip,cmd_output.split("\n"))
        files = "-- " + " ".join(["'"+ i.replace("'","\'") + "'" for i in file_list ])
    elif args.head:
        base_commit = "HEAD"

    diff  = shell("git diff -U10 %s %s" % (base_commit,files),"Create the diff").stdout

    if  args.diff:
        print(diff)
        return

    annotations = create_annotations_from_patch(diff)

    if args.save:
        pickle.dump( annotations, open( "annotations.p", "wb" ) )

    for a in annotations:
        print("\n%s" % convert_annotation_to_txt(a))

def get_top_level_directory():
    # find top level directory
    return shell("git rev-parse --show-toplevel","determine top level directory").stdout.strip()

def get_config_file():
    return os.path.join(get_top_level_directory(),default_configuration_file_name)

def generate_config():
    with open(get_config_file(), 'w', encoding='utf-8') as ymlfile:
        ymlfile.write(default_configuration)
    print("Config file {} generated".format(get_config_file()))

def read_config():
    global options
    # load the default configuration
    cfg = yaml.load(default_configuration,Loader=yaml.BaseLoader)

    if os.path.isfile(get_config_file()):
        with open(get_config_file(), 'r',encoding='utf-8') as ymlfile:
            c = yaml.load(ymlfile,Loader=yaml.BaseLoader)
            cfg['config'].update(c['config'])

    options.branch_under_review = cfg['config']['branch_under_review']
    options.base_url = cfg['config']['base_url']
    options.tags_only = bool(cfg['config']['tags_only'])

    if int(cfg['config']['version']) > current_version:
        warn_exit("ERROR:Detected a more recent version of the configuration. Upgrade git-code-annotate")

def main():
    parser = argparse.ArgumentParser(prog='git-code-annotate')
    parser.add_argument('--generate-config', action="store_true")
    parser.add_argument('--modified', action="store_true", help="Perform normal code annotation but only on modified files")
    parser.add_argument('--head', action="store_true", help="Perform code annotation on uncommited change")
    parser.add_argument('--diff', action="store_true", help="show diff insead of the annotations")
    parser.add_argument('--save', action="store_true", help="Save annotations")
    args = parser.parse_args()

    if args.generate_config:
            generate_config()
            return
    read_config()
    do_run(args)
    if len(warnings) > 0:
        print("\nWARNINGS:\n" + "\n".join(warnings))

if __name__ == "__main__":
    main()
