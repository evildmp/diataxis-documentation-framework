.. raw:: html

    <style>
        table.docutils { width: 100%; table-layout: fixed;}
        table.docutils th, table.docutils td { white-space: normal }
    </style>


About the structure
===================

Why isn't this obvious?
-----------------------

This structure is clear, and it works, but there is a reason why it's not so obvious, and that is the way the characteristics of each quadrant of the documentation overlap with those of its neighbours in the scheme.

.. image:: /images/overview.png
   :alt: 'overview of the documentation system'

Each of the quadrants is similar to its two neighbours:

* *tutorials and how-to guides* are both concerned with **describing practical steps**
* *how-to guides and technical reference* are both **what we need when we are at work, coding**
* *reference guides and explanation* are both concerned with **theoretical knowledge**
* *tutorials and explanation* are both **most useful when we are studying**, rather than actually working


The tendency to collapse
~~~~~~~~~~~~~~~~~~~~~~~~~

Given these overlaps, it's not surprising that the different kinds of documentation become confused and mixed in with each other. In fact, there is a natural gravitational pull of these distinct types of documentation to each other, and it is hard to resist. Its effect is to collapse the structure, and that is why so much documentation looks like this:

.. image:: /images/collapse.png
   :alt: 'collapse of the documentation structure'


Adoption of the system
-----------------------


Though it's rare to find it clear examples of it used fully, a great deal of documentation recognises, in different ways, each of these four functions.

Good examples of the scheme in substantial projects include:

* the `Divio Developer Handbook <https://docs.divio.com>`_
* `Django's documentation <https://docs.djangoproject.com/en/3.0/#how-the-documentation-is-organized>`_
* `django CMS's documentation <http://docs.django-cms.org>`_

It's possible to use the system even in very minimal documentation, for example `CoReport (an open-source COVID-19 reporting
project) <https://docs.coreport.ch>`_. Here, applying the system creates a framework for future documentation, helping ensure that
new material will conform.

Sometimes the documentation is so minimal that not all quadrants are ready to be represented, as in the case of `Getting started
with Java and Spring-boot <https://github.com/flavours/getting-started-with-spring-boot/blob/master/README.md>`_, which includes
only a tutorial, how-to and reference material.

`But I never wanted to do DevOps! <https://workshop.no-devops.work/en/latest/explanation/index.html>`_ is the written material
that accompanies a popular workshop. The documentation strictly separate the `tutorial
<https://workshop.no-devops.work/en/latest/the-workshop/index.html>`_, the steps learners are to follow, from the *explanation*
(`Further reading <https://workshop.no-devops.work/en/latest/explanation/index.html>`_). Both belong to the *most useful when we
are studying* side of the system, so it's natural to include them in a workshop.

In each case though, however minimal or even incomplete, the system is respected and the clear distinction between sections and
their purposes will benefit the author and user right away, and help guide the expansion of the material as it develops in the
future.


About the analysis and its application
---------------------------------------

The analysis of documentation in this article is based on several years of experience writing and maintaining documentation, and much time spent considering how to improve it.

It’s also based on sound principles that come from a variety of disciplines. For example, its conception of tutorials has a pedagogical basis; it posits a tutor and a learner, and considers using software to be a craft in which abstract understanding of general principles follows from concrete steps that deal with particulars.

The system is presented regularly at talks and interactive workshops. The analysis has been applied to numerous projects, including large internal documentation sets, and has repeatedly procured
benefits of usability and maintainability, across a very wide range of technical subject matter.
