.. _needs:

Understanding users' needs
=============================

Diátaxis isn't just a system for structuring documentation, it's a framework for understanding it, guiding the
work of documentation authors, and assessing the quality of documentation. However its most obvious implication
is for documentation structure.


The problem of structure
--------------------------

Of all the problems that bedevil authors and maintainers of documentation, the problem of *structure* is one that
accounts for a significant proportion of the grief they suffer. Multiple different documentation architectures exist
that try to provide a solution to this problem. Any orderly attempt to organise documentation into clear content
categories will help improve it (for authors as well as users).

However, even when armed with a helpful structure, authors often find themselves needing to write particular
documentation content that seems to falls outside the scheme it provides, or across its internal boundaries.

The map
--------

Diátaxis aims to solve this problem by providing a scheme that prescribes documentation structure based on a systematic
description and analysis of **user needs** (and not upon the characteristics of the product that the documentation is
intended to serve, or around the different kinds of things that the documentation creator feels need to be said about
the product).

Diátaxis provides a *map* of distinct documentation types rather than a mere list, and specifies these types in such a
way that the structure always naturally helps shape the content into an appropriate form.

The result is documentation that is not only better, but takes less effort to create and maintain.


Axes of knowledge
--------------------------

It's important to understand that Diátaxis is intended to apply to documentation pertaining to a *practical craft*, a
*technical skill* - such as the use of a product. Successful exercise of any such craft or skill involves both
theoretical grasp (knowledge and understanding), and an ability to apply that in practice, to work with the tools and
materials of the craft.

Diátaxis divides documentation across two axes of knowledge: *theory/practice*, and *acquisition/application*.

Documentation therefore either *contains theoretical knowledge* or *describes practical actions*, and is concerned
either with serving *our acquisition* or *our application* of knowledge. Hence the map, across which the four forms
of documentation are laid out:

.. image:: /images/diataxis.png
   :alt:
   :class: wider



Characteristics of documentation
----------------------------------------------------

A clear advantage of organising material this way is that it provides both clear *expectations* (to the reader) and
*guidance* (to the author). It's clear what the purpose of any particular piece of content is, it specifies how it
should be written and it shows where it should be placed.

.. list-table::
   :widths: 16 21 21 21 21
   :header-rows: 1
   :stub-columns: 1
   :class: wider

   * - \
     - :ref:`Tutorials <tutorials>`
     - :ref:`How-to guides <how-to>`
     - :ref:`Reference <reference>`
     - :ref:`Explanation <explanation>`
   * - what they do
     - introduce, educate, lead
     - guide, demonstrate
     - state, describe, inform
     - explain, clarify, discuss
   * - answers the question
     - "Can you teach me to...?"
     - "How do I...?"
     - "What is...?"
     - "Why...?"
   * - oriented to
     - learning
     - tasks
     - information
     - understanding
   * - purpose
     - to allow the newcomer to get started
     - to show how to solve a specific problem
     - to describe the machinery
     - to explain
   * - form
     - a lesson
     - a series of steps
     - dry description
     - discursive explanation
   * - analogy
     - teaching a child how to cook
     - a recipe in a cookery book
     - a reference encyclopaedia article
     - an article on culinary social history

Each piece of content is of a kind that not only has one particular job to do, that job is also clearly distinguished
from and contrasted with the other functions of documentation.


Collapse of the structure
--------------------------

Most documentation systems and authors recognise at least some of these distinctions and try to observe them in
practice. However, there is a kind of natural affinity between each of the different forms of documentation and its
neighbours on the map, and a natural tendency to blur the distinctions (that can be seen repeatedly in examples of
documentation).

* *tutorials and how-to guides* both describe *practical steps*
* *how-to guides and technical reference* are both concerned with the *application of knowledge*
* *reference and explanation* both contain *theoretical knowledge*
* *tutorials and explanation* are both concerned with the *acquisition of knowledge*

..  image:: /images/total-collapse.png
    :alt: The structure of documemntation can collapse.
    :class: sidebar

Allowing these distinctions to blur is what brings about structural problems. The most common is a complete or partial
collapse of tutorials and how-to guides into each other, while explanation spills over into both tutorials and
reference material.


-------------

The cycle of interaction
--------------------------

Diátaxis is intended to help documentation better serve users in their *cycle of interaction* with a product.

This phrase should not be understood too literally. It is not the case that a user must encounter the different kinds
of documentation in the order *tutorials* > *how-to guides* > *technical reference* > *explanation*. In practice,
an actual user may enter the documentation anywhere in search of guidance on some particular subject, and what they
want to read will change from moment to moment as they use your documentation.

However, the idea of a cycle of documentation needs, that proceeds through different phases, is sound and corresponds
to the way that people actually do become expert in a craft. There is a sense and meaning to this ordering.

* *learning-oriented phase*: We begin by learning, and learning a skill means diving straight in to do it - under the
  guidance of a teacher, if we're lucky
* *task-oriented phase*: Next we want to put the skill to work.
* *information-oriented phase*: As soon as our work calls upon knowledge that we don't already have in our head, it
  requires us to consult technical reference.
* *explanation-oriented phase*: Finally, away from the work, we reflect on our practice and knowledge to understand the
  whole.

And then it's back to the beginning, perhaps for a new thing to grasp, or to penetrate deeper.
