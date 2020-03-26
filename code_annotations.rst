Annotation report
*****************



.. note::
		Annotation contains uncommited changes



Source: `annotate/generate_code_annotation.py line 2 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L2>`_


import os.path

Source: `annotate/generate_code_annotation.py line 5 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L5>`_


import sys



default_configuration ="""

 Configuration for the git-code-annoate tool

config:
 When doing annotations the "untouched" code is normally on a different branch
 e.g. the master branch and the annotation tool is being run on an annotation branch
 that is expected to be the currently checked out branch. All changes on the
 annotation branch are considered annotations.. unless the commit message starts the word
 "dev". This allows to commit changes to this script or the outout of this script
 into the annotation branch
    branch_under_review: master

 When generating rst code links are greated to the original source code that is expected
 to be hosted somewhere. base_url gets concatnated with the modified file
    base_url: "https://gitlab.com/myuser/annotation-tool/-/blob/master/"
"""

Source: `annotate/generate_code_annotation.py line 8 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L8>`_


def do_run(branch_under_review,base_url):
    f1=open('code_annotations.rst', 'w')

Source: `annotate/generate_code_annotation.py line 127 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L127>`_


    # add some rst to force the heading order
    f1.write ("Annotation report\n")
    f1.write ("*****************\n\n")

Source: `annotate/generate_code_annotation.py line 129 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L129>`_


    #
    # Special handing for uncommited changes do a diff and produce the output
    #
    data  = subprocess.getoutput("git diff  -U0")
    if len(data) >0:
        f1.write ("\n\n")
        f1.write (".. note::\n\t\tAnnotation contains uncommited changes\n")

Source: `annotate/generate_code_annotation.py line 132 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L132>`_




Source: `annotate/generate_code_annotation.py line 142 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L142>`_




Source: `annotate/generate_code_annotation.py line 144 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L144>`_


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

Source: `annotate/generate_code_annotation.py line 148 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L148>`_


        id,message = commit_regex.match(commit).groups()

Source: `annotate/generate_code_annotation.py line 155 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L155>`_


        if message.startswith("dev"):
            print("Base commit is %s" % commit)
            diff_commit=id
            break

Source: `annotate/generate_code_annotation.py line 156 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L156>`_


    data  = subprocess.getoutput("git diff  -U0 %s" % base_commit)
    annotations = create_annotations_from_patch(data)
    for a in annotations:
        f1.write ("\n")
        f1.write(convert_annotation_to_rst(a,base_url))
        do_verbatim_include(a,branch_under_review)

Source: `annotate/generate_code_annotation.py line 158 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L158>`_


    f1.close()

Source: `annotate/generate_code_annotation.py line 161 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L161>`_




Source: `annotate/generate_code_annotation.py line 170 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L170>`_




Source: `annotate/generate_code_annotation.py line 172 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L172>`_




Source: `annotate/generate_code_annotation.py line 177 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L177>`_


def main():
    p = subprocess.run("git rev-parse --show-toplevel", capture_output=True, shell=True, text=True)
    if p.returncode != 0:
        print("git-code-annotate: failed to determine git top level directory")
        sys.exit(2)

    top_level = p.stdout.strip()
    config_file= os.path.join(top_level,"git-code-annoate.yml")

    if os.path.isfile(config_file):
        with open(config_file, 'r') as ymlfile:
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

    do_run(branch_under_review,base_url)

Source: `annotate/generate_code_annotation.py line 184 <https://gitlab.com/myuser/annotation-tool/-/blob/master/annotate/generate_code_annotation.py#L184>`_

