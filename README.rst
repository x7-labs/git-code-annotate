Documentation for the annotation tool
-------------------------------------

The annotation tool allows to annotate code stored in a git repository.

The basic concept for the tool is to branch of the code that need to be reviewed and add review comments inside the source code of that branch


.. code-block::

    master branch
       \___annotate  <-- here go the changes into commits -->



Annotation syntax
=================

Annotation have to writen in `Restructured Text (reST) <https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_

* The first and last line of review may contain a start and stop of a block coment these will be removed.
* Lines may start with # or // .These comment markers (only the markers) will be removed.
* Definition lists, tables, links are allowed.
* Reviews can be split into commits. every commit is also RST formatted and will be included into the resulting report.
* A special INCLUDE:N directive allows to include the N lines of code bellow the comment.


.. code-block:: c

        /*
        Review title
        ------------

        risk
            low | medium | high

        review comments

        INCLUDE:12
        */
        void main(int argc, char** argv){
        ...

Annotations are grouped together into git commits and the git commits messages themself will be added to the review
comment.

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


We are ready for the first run.

.. code-block:: sh

    git-code-annotate

This will create an file called git-code-annotations.rst in the top directory. Given we did not annotate anything yet it  will not contain annotations.

We use a tool called restview to visualize the annotation in the browser. Now it a good time to see how it works for you. Run  git-code-annotate --view . This will start a webserver that can render rst and opens a browser(or tab) automatically. 

.. code-block:: sh

        git-code-annotate --view

The reviewer now wants to mark that a vulnerability was found in the parse funtion. For that purpose he will edit the vuln.c file, add his rst formatted comments in there.
Modify vuln.c to add an annotation, save it  and run git-code-annoate your browser should self refresh

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
        INCLUDE:4
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

While not needed the reviewer also made sure that the code would still compile after adding the comments by putting
the review inside a comment block

After runnning git-code-annotate the browser will have self refreshed and you should see your first annotation.

Annotating inside code

During review we found that when using the INCLUDE directive we where still sometimes having trouble documenting the code section or wanting to include more comments
in that section. The most elegant way of hanling this is to copy the code and insert it into the annotation section. for vuln.c this looks like this (e.g. adding a .. code-block:: c section and the copy of the code ). So try and remove the INCLUDE directive and copy the function that requires annotation.

.. code-block:: c

        #include <stdio.h>
        #include <string.h>
        #include <stdlib.h>
        #include <unistd.h>

        #define BUF_SIZE	1024
        #define TEST_STR	"test"

        /*
        Unsafe use of strcmp
        --------------------

        The code listed here uses the strcmp function on a user provided input. Using strmp
        is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_

        .. code-block:: c
        
                void parse(char *buf) {
                    if (strcmp(buf, TEST_STR))   <!-- THIS IS BAD -->
                        printf("parsed test\n");
                }
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


and run git-code-annotate to see the result. This is an iterative process

.. code-block:: sh

    git-code-annoate

When you are happy with the changes you are free to commit the change into the annotation branch.
Commit your code (as described in the example section) and push back to our tutotial server. 

.. code-block:: c

    git add vuln.c
    git commit -m "vuln.c review"

If you followed this tutorial you should now have a rst file that will render like `this <https://github.com/x7-labs/git-code-annotate-tutorial/blob/demo/git_code_annotations.rst>`_

Configuration
=============

The annotation tool creates web links to the original hosted source code so that the reader can have able to have context on the annotation. To configure what url to use the annotate directory also read a configuration file stored in the root directory called .git-code-annoation.yml. 

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

