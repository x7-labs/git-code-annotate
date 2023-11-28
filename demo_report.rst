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
|url  | `src <https://github.com/x7-labs/git-code-annotate-tutorial/blob/master/vuln.c#L10>`__ | `annotated <https://github.com/x7-labs/git-code-annotate-tutorial/blob/annotation_demo/vuln.c#L10>`__|
+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|Issue|unsafe use of strcmp The code listed here uses the strcmp function on a user provided input. Using strmp is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_               |
+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


.. code-block:: c

    File vuln.c:10 :
         7 : #define TEST_STR	"test"
         8 : 
         9 : void parse(char *buf) {
    A   10 : Issue: unsafe use of strcmp
    A   10 :     The code listed here uses the strcmp function on a user provided input. Using strmp
    A   10 :     is generally considered unsafe see `strcmp <http://no.more.strmp.org>`_
    A   10 : 
        10 : 	if (strcmp(buf, TEST_STR))
        11 : 		printf("parsed test\n");
        12 : }
        13 : 
        14 : int main() {
        15 : 	void *buf = malloc(BUF_SIZE);
        16 : 	read(0, buf, BUF_SIZE);
        17 : 	parse((char *)buf);
        18 : 	return 0;
        19 : }

