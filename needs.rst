.. _needs:

The map of needs
=============================

*How to organise my documentation?* In the absence of a clear, generalised
documentation architecture, documentation creators will usually try to
structure their work around characteristics or features of the product its
intended to serve.

This is rarely successful, even in a single instance. In a portfolio of
documentation instances, the results are wild inconsistency. Much better is
the adoption of a scheme that tries to provide an answer to the
question: how to arrange documentation *in general?*

In fact any orderly attempt to organise documentation into clear content
categories will help improve it (for authors as well as users), by providing
lists of content types.

Even so, authors often find themselves needing to write particular
documentation content that fails to fit well within the categories put
forward by a scheme, or struggling to rewrite existing material. Often,
there is a sense of arbitrariness about the structure that they find
themselves working with - why this particular list of content types
rather than another? And if another competing list is proposed, which to
adopt?

.. _map:

The Diátaxis map
----------------------------------------------------

The most immediately striking feature of Diátaxis is its map:

.. image:: /images/diataxis.png
   :alt:
   :class: wider

It's a memorable and approachable idea.

One reason it is effective as a guide to organising documentation is
that it describes a **two-dimensional structure**, rather than a *list*. It
specifies its types of documentation in such a way that the structure
naturally helps guide and shape the material it contains.

As a map, it places the different forms of documentation into relationship
with each other. Each one occupies a space in the mental territory it outlines,
and the boundaries between them highlight their distinctions.

The result is documentation that is not only better, but takes less effort to
create and maintain - but that is only possible because the Diátaxis map is a
map of *needs*.


Needs
-----

A map is only useful if it adequately describes a reality. Diátaxis is
underpinned by a systematic description and analysis of generalised **user
needs**.

The user whose needs Diátaxis serves is *the practitioner in a domain of
skill*. A domain of skill is defined by a craft - the use of a tool
or product is a craft. So is an entire discipline or profession. Using a
programming language is a craft, as is flying a particular aircraft, or even
being a pilot in general.

The successful engagement in any such craft or skill involves
both *theoretical grasp* (knowledge and understanding), and an ability to
apply that *in practice*, to work with the tools and materials of the craft.
Documentation serving the practitioner must therefore meet the needs both
of **theory** and its **practical application**.

And at any moment in their craft, a practitioner is either *acquiring* their
skill, or *applying* it to actual work. That is, a practitioner is either in
the mode of **study** (learning, acquiring, building up their skill) or the
mode of **work** (applying, using, exercising it). And this gives
documentation two more needs to meet.


Axes of knowledge
--------------------------

Diátaxis uses this analysis to divide documentation across two axes of
knowledge: *theory/practice*, and *acquisition/application*.

Documentation therefore either *contains theoretical (i.e. propositional)
knowledge* or *describes practical actions*, and is concerned either with
serving *our acquisition* or *our application* of knowledge. Hence the map,
across which the four forms of documentation are laid out.



Characteristics of documentation
----------------------------------------------------

A clear advantage of organising material this way is that it provides both
clear *expectations* (to the reader) and
*guidance* (to the author). It's clear what the purpose of any particular
piece of content is, it specifies how it should be written and it shows
where it should be placed.

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
  guidance of a teacher, if we're lucky.
* *task-oriented phase*: Next we want to put the skill to work.
* *information-oriented phase*: As soon as our work calls upon knowledge that we don't already have in our head, it
  requires us to consult technical reference.
* *explanation-oriented phase*: Finally, away from the work, we reflect on our practice and knowledge to understand the
  whole.

And then it's back to the beginning, perhaps for a new thing to grasp, or to penetrate deeper.
