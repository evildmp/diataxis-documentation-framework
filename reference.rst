.. _reference:

About reference
======================

..  rubric:: Reference guides are **technical descriptions** of the machinery and how to operate it. Reference material
    is **information-oriented**.

===========

The only purpose of a reference guide is to describe, as succinctly as possible, and in an orderly
way. Whereas the content of tutorials and how-to guides are led by needs of the user, reference
material is led by the product it describes.

..  image:: /images/overview-reference.png
    :alt: Reference - information oriented, theoretical knowledge, that serves our work
    :class: sidebar

In the case of software, reference guides describe the software itself - APIs, classes, functions
and so on - and how to use them.

Your users need reference material because they need truth and certainty - firm platforms on which to stand while
they work. Good technical reference is essential to provide users with the confidence to do their work.

-----------

Reference as description
---------------------------------

Reference material should be **austere and to the point**. One hardly *reads* reference material;
one *consults* it.

There should be no doubt or ambiguity in reference; it should be wholly authoritative.

Reference material is like a map. A map tells you what you need to know about the territory,
without having to go out and check the territory for yourself; a reference guide serves the same
purpose for the product and its internal machinery.

Although reference should not attempt to show how to perform tasks, it can and often needs to
include a description of how something works or the correct way to use it.

..  sidebar::

    Unfortunately, too many software developers think that auto-generated reference material is all the
    documentation required.

Some reference material (such as API documentation) can be generated automatically by the software
it describes, which is a powerful way of ensuring that it remains faithfully accurate to the code.


===============

Food and cooking
--------------------

Perhaps you might consult an encyclopaedia to read about an ingredient (for example, about
liquorice).

..  image:: /images/liquorice.png
    :alt: Wikipedia's entry for liquorice

What you're seeking is information - accurate, up-to-date, comprehensive information. You may want
to know about its properties, its chemical composition, how it interacts with other ingredients,
what other ingredients or plants it is related to, what health implications it might have.

For example: *Liquorice is a flowering plant of the bean family Fabaceae*. Or: *Excessive
consumption of liquorice may result in adverse effects*.

You'll expect to find information about these sorts of things presented in much the same way for
each one.

You will not on the other hand expect to find for example recipes, or suggestions on how to cook with
it - it is not a function of an encyclopaedia article to tell you what to do.

===============


Writing a good reference guide
----------------------------------------

.. _respect-structure:

Respect the structure of the machinery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The way a map corresponds to the territory it represents helps us use the former to find our way
through the latter. It should be the same with documentation: **the structure of the documentation
should mirror the structure of the product**, so that the user can work their way through them
at the same time.

In the case of code, this means arranging the sections of reference documentation to follow the
architecture of the software, where possible.

..  sidebar:: Style and form

    * austere and uncompromising
    * neutrality, objectivity, factuality
    * structured according to the structure of the machinery itself

It doesn't mean forcing the documentation into an unnatural structure. What's important is that the
logical, conceptual arrangement of and relations within the code should help make sense of the
documentation.


Be consistent
~~~~~~~~~~~~~

**Reference material benefits from consistency.** Be consistent, in structure, language,
terminology, tone. There are many opportunities in writing to delight your readers with your
extensive vocabulary and command of multiple styles, but reference material is definitely not
one of them.


Do nothing but describe
~~~~~~~~~~~~~~~~~~~~~~~~

**Technical reference has one job: to describe**, and to do that clearly, accurately and
comprehensively. Doing anything else - explaining, discussing, instructing, speculating -
gets in the way of that job, and makes it harder for the reader to find the information they need.

It can be tempting to introduce instruction and explanation, simply because technical reference can
seem too bare. Instead, link to how-to guides, explanation and introductory tutorials as
appropriate.


Provide examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Examples** are valuable ways of providing illustration that helps readers understand reference,
without becoming distracted from the job of describing. For example, an example of usage of a
command can be a succinct way of illustrating it and its context.

Be accurate
~~~~~~~~~~~

**These descriptions must be accurate and kept up-to-date.** Any discrepancy between the machinery and your description of it will inevitably lead a user astray.

==============

The language of reference guides
--------------------------------

*X is an example of y. W needs to be initialised using z. This option does that.*
    State facts about the machinery and its behaviour.
*Sub-commands are: a, b, c, d, e, f.*
    List commands, options, operations, features, flags, limitations, error messages, etc.
*You must use a. You must not apply b unless c. Never d.*
    Provide warnings where appropriate.
