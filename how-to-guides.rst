.. _how-to:

About how-to guides
===================

..  rubric:: How-to guides are **directions** that take the reader through the steps required to solve a real-world
    problem. How-to guides are **goal-oriented**.

===========

How-to guides can be thought of as recipes, directions that guide the reader through the steps to achieve a specific
end.

..  image:: /images/overview-how-to.png
    :alt: How-to guides - task oriented, practical steps, that serve our work
    :class: sidebar

Examples could be: *how to calibrate the radar array*; *how to use fixtures in pytest*; *how to configure
reconnection back-off policies*. On the other hand, *how to build a web application* is not - that's not
addressing a specific goal or problem, it's a vastly open-ended sphere of skill.

How-to guides matter not just because users need to be able to accomplish things: the list of how-to guides in your
documentation helps frame the picture of what your product can actually *do*. A rich list of how-to guides is an
encouraging suggestion of a product's capabilities.

If they're well-written and address the right subjects, you're likely to find that how-to guides are the most-read
sections of your documentation.

===========

Tutorials vs how-to guides
----------------------------

**How-to guides are wholly distinct from tutorials**. They are easily conflated, as both describe a series of practical
steps that lead to the completion of some task. The user-needs that they serve are quite different however, and
conflating them is at the root of many difficulties that afflict documentation.

See :ref:`tutorials-how-to` for an extended discussion of this distinction.


================

Food and cooking
--------------------

Consider a recipe, an excellent model for a how-to guide. A recipe clearly defines what will be achieved by following
it, and **addresses a specific question** (*How do I make...?* or *What can I make with...?*).

..  image:: /images/old-recipe.jpg
    :alt: A recipe contains a list of ingredients and a list of steps.

It's not the responsibility of a recipe to *teach* you how to make something. A professional chef who has made
exactly the same thing multiple times before may still follow a recipe - even if they *created* the recipe
themselves - to ensure that they do it correctly.

Even following a recipe **requires at least basic competence**. Someone who has never cooked before should not be
expected to follow a recipe with success, so a recipe is not a substitute for a cooking lesson.

Someone who expected to be provided with a recipe, and is given instead a cooking lesson, will be disappointed and
annoyed. Similarly, while it's interesting to read about the context or history of a particular dish, the one time you
don't want to be faced with that is while you are in the middle of trying to make it. A good recipe follows a
well-established format, that excludes both teaching and discussion, and focuses only on **how** to make the dish
concerned.

=================

Writing a good how-to guide
---------------------------------------

Describe a sequence of actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like a tutorial, a **how-to guide contains a sequence of actions, that have an order**. Unlike a tutorial, you don't
have to start at the beginning of the whole story and take your reader right to the end. Most likely, your user will also be in the middle of something - so you only need to provide a starting-point that they know how to reach, and a conclusion that actually answers a real question.

..  sidebar:: How-to characteristics

    * focused on tasks or problems
    * assume the user knows what they want to achieve
    * action and only action
    * no digression, explanation, teaching

How-to guides should be reliable, but they don’t need to have the cast-iron repeatability of a tutorial.


Solve a problem
~~~~~~~~~~~~~~~~~~~~

The problem or task is the concern of a how-to guide: **stick to that practical goal**. Anything else that's added
- unnecessary explanation, for example - distracts both you and the user and dilutes the useful power of the guide.


Don't explain concepts
~~~~~~~~~~~~~~~~~~~~~~~

An explanation doesn't show you how to do something - so **a how-to guide should not try to explain things.** Explanation here will simply get in the way of the action. If explanations are important, link to them.


Be flexible
~~~~~~~~~~~~~~~~~~~~~~~~~~

A tutorial needs to be didactic in nature, but **a how-to guide needs to be adaptable to real-world use-cases**. A
how-to guide that is useless for any purpose except *exactly* the narrow one you have addressed is rarely valuable.


Omit the unnecessary
~~~~~~~~~~~~~~~~~~~~~

In how-to guides, **practical usability is more helpful than completeness.** Whereas a tutorial needs to be a complete,
end-to-end guide, a how-to guide does not. It should start and end in some reasonable, meaningful place, and require
the reader to join it up to their own work.


Pay attention to naming
~~~~~~~~~~~~~~~~~~~~~~~~

**Choose titles that say exactly what a how-to guide shows.**

* good: *How to integrate application performance monitoring*
* bad: *Integrating application performance monitoring* (maybe the document is about how to decide whether you should,
  not about how to do it)
* very bad: *Application performance monitoring* (maybe it's about *how* - but maybe it's about *whether*, or even
  just an explanation of *what* it is)

Note that search engines appreciate good titles just as much as humans do.

==============

The language of how-to guides
-----------------------------

*This guide shows you how to...*
    Describe clearly the problem or task that the guide shows the user how to solve.
*If you want x, do y. To achieve w, do z.*
    Use conditional imperatives.
*Refer to the x reference guide for a full list of options.*
    Don't pollute your practical how-to guide with every possible thing the user might do related to x.
