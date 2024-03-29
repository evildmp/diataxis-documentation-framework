.. meta::
   :description:
       The Diátaxis framework solves a problem of quality in technical documentation, describing an
       information architecture that makes it easier to create, maintain and use.
   :keywords: documentation, four, kinds, architecture

.. _diataxis:

Diátaxis
========================================================

.. toctree::
   :maxdepth: 1
   :hidden:
   :titlesonly:

   Home <self>

..  rubric:: A systematic approach to technical documentation authoring.

----------

Diátaxis is a way of thinking about and doing documentation. 

It prescribes approaches to content, architecture and form that emerge from a systematic approach to understanding the needs of documentation users.

..  sidebar::

    *Diátaxis*, from the Ancient Greek δῐᾰ́τᾰξῐς: *dia* ("across") and *taxis* ("arrangement").

Diátaxis identifies four distinct needs, and four corresponding forms of documentation - *tutorials*, *how-to guides*, *technical reference* and *explanation*. It places them in a systematic relationship, and proposes that documentation should itself be organised around the structures of those needs.

.. image:: /images/diataxis.png
   :alt: Diátaxis

Diátaxis solves problems related to documentation *content* (what to write), *style* (how to write it) and *architecture* (how to organise it). 

As well as serving the users of documentation, Diátaxis has value for documentation creators and maintainers. It is light-weight, easy to grasp and straightforward to apply. It doesn't impose implementation constraints. It brings an active principle of quality to documentation that helps maintainers think effectively about their own work.

------

Contents
--------

This website is divided into two main sections, to help apply and understand Diátaxis.

..  grid:: 1 2 2 2
    :padding: 0
    :margin: 0 
    :gutter: 3

    ..  grid-item::

        *Start here.* These pages will help make immediate, concrete sense of the approach. 
        
    ..  grid-item::

        ..  rst-class:: toc-with-header
            
        ..  toctree::
            :maxdepth: 1
            :titlesonly:

            application
            Tutorials <tutorials>
            How-to guides <how-to-guides>
            Reference <reference>
            Explanation <explanation>
            compass
            Workflow <how-to-use-diataxis>

    ..  grid-item::

        This section explores the theory and principles of Diátaxis more deeply, and sets forth the understanding of needs that underpin it.

    ..  grid-item::

        ..  rst-class:: toc-with-header

        ..  toctree::
            :maxdepth: 1
            :titlesonly:

            theory
            foundations
            map
            Quality <quality>
            Tutorials and how-to guides <tutorials-how-to>
            Reference and explanation <reference-explanation>
            Complex hierarchies <complex-hierarchies>

--------

Diátaxis is proven in practice. Its principles have been adopted successfully in hundreds of documentation projects.


..  epigraph::

    At Gatsby we recently reorganized our open-source documentation, and the Diátaxis framework was our go-to resource
    throughout the project. The four quadrants helped us prioritize the user’s goal for each type of documentation. By
    restructuring our documentation around the Diátaxis framework, we made it easier for users to discover the
    resources that they need when they need them.

    -- `Megan Sullivan <https://hachyderm.io/@meganesulli>`_


..  epigraph::

    While redesigning the `Cloudflare developer docs <https://developers.cloudflare.com>`_, Diátaxis became our north star for information architecture. When we weren't sure where a new piece of content should fit in, we'd consult the framework. Our documentation is now clearer than it's ever been, both for readers and contributors.

    -- `Adam Schwartz <https://github.com/adamschwartz>`_






.. toctree::
   :maxdepth: 1
   :hidden:
   :titlesonly:

   colophon 
