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
* Annotation may contain tag:value pairs

.. code-block:: c

        /*
        Review:
        Reviewer: keesj
        issues: 1
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

        #define BUF_SIZE    1024
        #define TEST_STR    "test"
        
        /*
        Unsafe use of strcmp
        --------------------

        The code listed here uses the strcmp function on a user provided input. Using strmp
        is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
        Issues: 1
        */
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


After making the modification run git-code-annotate

.. code-block:: sh

    	git-code-annotate


Sample outout

.. code-block:: sh

	Looking at file vuln.c:9 :
	A    9 :
	A   10 : Unsafe use of strcmp
	A   11 : --------------------
	A   12 :
	A   13 : The code listed here uses the strcmp function on a user provided input. Using strmp
	A   14 : is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
	A   15 : Issues: 1
	A   16 :
	    17 : void parse(char *buf) {
	    18 :        if (strcmp(buf, TEST_STR))
	    19 :                printf("parsed test\n");
	    20 : }
	    21 :
	    22 : int main() {
	    23 :        void *buf = malloc(BUF_SIZE);
	    24 :        read(0, buf, BUF_SIZE);
	    25 :        parse((char *)buf);
	    26 :        return 0;

While not needed the reviewer also made sure that the code would still compile after adding the comments by putting
the review inside a comment block

It is is also possible to annotate inside code. In such event git-code-annotate will also autmatically include more context on the method. add the text `/* This text will also be seen as an annotation */`
inside the pasr function and run git-code-annotate again.

.. code-block:: c

        #include <stdio.h>
        #include <string.h>
        #include <stdlib.h>
        #include <unistd.h>

        #define BUF_SIZE    1024
        #define TEST_STR    "test"
        
        /*
        Unsafe use of strcmp
        --------------------

        The code listed here uses the strcmp function on a user provided input. Using strmp
        is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
        Issues: 1
        */
        void parse(char *buf) {
            /* This text will also be seen as an annotation */
            if (strcmp(buf, TEST_STR))
                printf("parsed test\n");
        }

        int main() {
            void *buf = malloc(BUF_SIZE);
            read(0, buf, BUF_SIZE);
            parse((char *)buf);
            return 0;
        }

and run git-code-annotate to see the result. This is an iterative process

.. code-block:: sh

    git-code-annoate

When you are happy with the changes you are free to commit the change into the annotation branch.

.. code-block:: c

    git add vuln.c
    git commit -m "vuln.c review"

If you followed this tutorial the output of running git-code-annotate should look like the following


.. code-block:: sh

	Looking at file vuln.c:9 :
	A    9 :
	A   10 : Unsafe use of strcmp
	A   11 : --------------------
	A   12 :
	A   13 : The code listed here uses the strcmp function on a user provided input. Using strmp
	A   14 : is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
	A   15 : Issues: 1
	A   16 :
	    17 : void parse(char *buf) {


	Looking at file vuln.c:18 :
	    15 : Issues: 1
	    16 :
	    17 : void parse(char *buf) {
	A   18 :  This text will also be seen as an annotation
	    19 :        if (strcmp(buf, TEST_STR))
	    20 :                printf("parsed test\n");
	    21 : }
	    22 :
	    23 : int main() {
	    24 :        void *buf = malloc(BUF_SIZE);
	    25 :        read(0, buf, BUF_SIZE);
	    26 :        parse((char *)buf);
	    27 :        return 0;
	    28 : }



Configuration
=============

The annotation tool creates text formated in the form of filename.c:linenumber. This is recognized by tools  (like vs code) and clicking on them will open the file under review
at the correct location.

The tool can also generate links to the original (non annotated code). For that to work the configuration need to be adapted.

Generate the initial configuration

.. code-block:: sh

        git-code-annotate --generate_config

For the tutorial above one needs to modify the base_url to point to github.

.. code-block:: sh

        config:
            branch_under_review: master
            base_url: "https://github.com/x7-labs/git-code-annotate-tutorial/blob/master/"

If you want to add the configuration to the repository this might create problems because the configuration will be viewed as an annotation. There are several ways around this. you can add the configuration
to the git repository *before* creating the annotation branch. Therefore the differences between the master branch and the annotation branch will only contain the differences. The second way to work around this problem is by making the commit in the annotation branch and commiting the message starting with "dev:" and making sure it is the first commit on the branch.

.. code-block:: sh

    git add .git-code-annoation.yml
    git commit -m "dev:modify configuration"
    git rebase -i master
    #edit the commits in such a way that the "dev:" commits are on top and save the file
    

