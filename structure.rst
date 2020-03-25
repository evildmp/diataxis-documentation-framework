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

Some projects do adopt it fully, including `Django <https://docs.djangoproject.com/en/3.0/#how-the-documentation-is-organized>`_, and `django CMS <http://docs.django-cms.org>`_. It has proved its worth in both projects.


About the analysis
------------------

The analysis of documentation in this article is based on several years of experience writing and maintaining documentation, and much time spent considering how to improve it.

It’s also based on sound principles that come from a variety of disciplines. For example, its conception of tutorials has a pedagogical basis; it posits a tutor and a learner, and considers using software to be a craft in which abstract understanding of general principles follows from concrete steps that deal with particulars.


Making documentation work
-------------------------

One of the biggest headaches that documentation maintainers have to deal with is not having a clear picture of what they should be doing. They write and rewrite, but find it hard to make it fit together in satisfactory ways.

This structure resolves those questions by making clear distinctions and separations. They make documentation that is easier to write and maintain, that’s easier to use and to find one's way around in.

The documentation doesn’t write itself - but it’s now possible to write it without alsohaving to wrestle with poor fit, or unclear scope or doubt about what should be included or what style to adopt. It becomes much clearer what to write, how to write it, and where to put it.

It serves users better, because for all the different phases in the cycle of their interaction with the software they will find the right kind of documentation, that serves the needs of that moment.

Writing documentation that explicitly and distinctly addresses each of the four quadrants helps the software attract and keep more users, who will use it more effectively - and that is one of the things the creators of software want most of all.
