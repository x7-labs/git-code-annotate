Documentation for the annotation tool
-------------------------------------

The annotation tool allows to annotate code stored in a git repository.
The basic concept for the tool is to branch of the code that need to be reviewed and add review comments inside the source code of that branch. The differences between the branches are the annotations.


.. code-block::

    master branch
       \___annotation  <-- here go te anntations into commits -->



Annotation syntax
=================

All additions to the code are seen as annotations and the annotation tool will provide some contents. That said some preprosessing on the annotations is performed

* Annotations may start with an enpty comment line
* Lines may start with # , //, */ or /*. These comment markers and the white spaces that before those markers will be removed.
* Annotation will contain tag:value pairs
* Annotation may span multiple lines in such events multi line annotation will start with at least 2 whitespaces

.. code-block:: c

        /*
        Reviewer: keesj
        Issue: the posix standard demands that main has a return value
        */
        void main(int argc, char** argv){
        ...


Tutorial
========

First we need to install the tool using pip3

.. code-block:: sh

    pip3 install --user git+https://github.com/x7-labs/git-code-annotate


For this tutorial we created a git repository containing some vulnerable code and we are going to review this code. We start by cloning the repository

.. code-block:: sh

 git clone https://github.com/x7-labs/git-code-annotate-tutorial.git

This tutorial repository contains a file called vuln.c that has the following contents.

.. code-block:: c

        #include <stdio.h>
        #include <string.h>
        #include <stdlib.h>
        #include <unistd.h>

        #define BUF_SIZE    1024
        #define TEST_STR    "test"

        void parse(char *buf) {
            if (strcmp(buf, TEST_STR))
                printf("parsed test\n");
        }

        int main() {
            void *buf = malloc(BUF_SIZE);
            read(0, buf, BUF_SIZE);
            parse((char *)buf);
            return 0;
        }


To integrate our annotation tool and keep the original code intact (and compiling) we are going to create a branch where we are going to store the annotation tool and annotations.

.. code-block:: sh

    cd git-code-annotate-tutorial
    git branch annotation
    git checkout annotation


We are ready for the first run. As we did not add any annotation the output of the following should be empty

.. code-block:: sh

    git-code-annotate

The reviewer now wants to mark that a vulnerability was found in the parse funtion. For that purpose he will edit the vuln.c file, add his formatted comments in there.
Modify vuln.c to add an annotation, save it  and run git-code-annotate.

.. code-block:: c

    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <unistd.h>

    #define BUF_SIZE        1024
    #define TEST_STR        "test"


    void parse(char *buf) {
             /*Issue: unsafe use of strcmp
             *    The code listed here uses the strcmp function on a user provided input. Using strmp
             *    is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
             */
            if (strcmp(buf, TEST_STR))
                    printf("parsed test\n");
    }

    int main() {
            void *buf = malloc(BUF_SIZE);
            read(0, buf, BUF_SIZE);
            parse((char *)buf);
            return 0;
    }


After making the modification run git-code-annotate

.. code-block:: sh

    	git-code-annotate


Sample outout

.. code-block:: sh

    Looking at file vuln.c:10 :
        7 : #define TEST_STR	"test"
        8 : 
        9 : void parse(char *buf) {
    A   10 : 
    A   11 :  Issue: unsafe use of strcmp
    A   12 :     The code listed here uses the strcmp function on a user provided input. Using strmp
    A   13 :     is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
    A   14 : 
        15 : 	if (strcmp(buf, TEST_STR))
        16 : 		printf("parsed test\n");
        17 : }
        18 : 
        19 : int main() {
        20 : 	void *buf = malloc(BUF_SIZE);
        21 : 	read(0, buf, BUF_SIZE);
        22 : 	parse((char *)buf);
        23 : 	return 0;
        24 : }


The reviewer made sure that the code would still compile after adding the comments by putting
the review inside a comment block but this is not stricly needed.

When you are happy with the changes you are free to commit the change into the annotation branch.

.. code-block:: c

    git add vuln.c
    git commit -m "vuln.c review"




Configuration
=============

The annotation tool creates text formated in the form of filename.c:linenumber. This is recognized by tools  (like vs code) and clicking on them will open the file under review
at the correct location.

The tool can also generate links to the original (non annotated code). For that to work the configuration need to be adapted.

Generate the initial configuration

.. code-block:: sh

        git-code-annotate --generate_config

modify the configuration according to https://github.com/x7-labs/git-code-annotate-tutorial/blob/annotation_config/.git-code-annotate.yml

If you want to add the configuration to the repository this might create problems because the configuration will be viewed as an annotation. There are several ways around this. you can add the configuration
to the git repository *before* creating the annotation branch. Therefore the differences between the master branch and the annotation branch will only contain the differences. 


Generating a report
===================

.. code-block:: sh

    git-code-annoate --save
    git-code-report > demo_report.rst