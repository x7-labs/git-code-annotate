Code annotation report
**********************

Code annotation report
    
Summary
=======

+----------------+-+
|Annotation count|1|
+----------------+-+
|Warning count   |0|
+----------------+-+
|Issue count     |1|
+----------------+-+

Annotations (Medium and High)
=============================

+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|url  | `src <https://github.com/x7-labs/git-code-annotate-tutorial/blob/master/vuln.c#L10>`__ | `annotated <https://github.com/x7-labs/git-code-annotate-tutorial/annotation_demo/blob/vuln.c#L10>`__|
+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|Issue|unsafe use of strcmp The code listed here uses the strcmp function on a user provided input. Using strmp is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_               |
+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


.. code-block:: c

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

