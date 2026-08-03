.. _how-to:

How-to guides
=============

..  rubric:: How-to guides are **directions** that guide the reader through a problem or towards a result. How-to guides are **goal-oriented**.

===========

A how-to guide helps the user get something done, correctly and safely; it guides the user's *action*. 

It's concerned with *work* - navigating from one side to the other of a real-world problem-field.

..  image:: /images/overview-how-to.png
    :alt: How-to guides - task oriented, practical steps, that serve our work
    :class: sidebar

Examples could be: *how to calibrate the radar array*; *how to use fixtures in pytest*; *how to configure
reconnection back-off policies*. On the other hand, *how to build a web application* is not - that's not
addressing a specific goal or problem, it's a vastly open-ended sphere of skill.

How-to guides matter not just because users need to be able to accomplish things: the list of how-to guides in your
documentation helps frame the picture of what your product can actually *do*. A rich list of how-to guides is an
encouraging suggestion of a product's capabilities.

Well-written how-to guides that address the right questions are likely to be the most-read sections of your documentation.

=================

How-to guides addressed to problems
-----------------------------------

**How-to guides must be written from the perspective of the user, not of the machinery.** A how-to guide represents something that someone needs to get done. It's defined in other words by the needs of a user. Every how-to guide should answer to a human project, in other words. It should show what the human needs to do, with the tools at hand, to obtain the result they need. 

This is in strong contrast to common pattern for how-to guides that often prevails, in which how-to guides are defined by operations that can be performed with a tool or system. The problem with this latter pattern is that it offers little value to the user; it is not addressed to any need the user has. Instead, it's focused on the tool, on taking the machinery through its motions.

This is fundamentally a distinction of *meaningfulness*. Meaning is given by purpose and need. There is no purpose or need in the functionality of a machine. It is merely a series of causes and effects, inputs and outputs. 

Consider:

* "To shut off the flow of water, turn the tap clockwise."
* "To deploy the desired database configuration, select the appropriate options and press **Deploy**."

..  sidebar:: 
    
    We really do not need to be informed that we turn on a device using the power switch, but it is shocking how often how-to guides in software documentation are written at this level.

The examples above *look* like examples of guidance, but they are not. 

They represent mostly useless information that anyone with basic competence - anyone who is working in this domain - should be expected to know. Between them, standardised interfaces and generally-expected knowledge should make it quite clear what effect most actions will have. 

Secondly, they are disconnected from purpose. What the user needs to know might be things like:

* how much water to run, and how vigorously to run it, for a certain purpose
* what database configuration options align with particular real-world needs

..  sidebar:: 
    
    How-to guides are about goals, projects and problems, not about tools. 
    
Tools appear in how-to guides as incidental bit-players, the means to the user's end. Sometimes of course, a particular end is closely aligned with a particular tool or part of the system, and then you will find that a how-to guide indeed concentrates on that. Just as often, a how-to guide will cut across different tools or parts of a system, joining them up together in a series of activities defined by something a human being needs to get done. In either case, it is that project that defines what a how-to guide must cover.


=================

What how-to guides are not
--------------------------

**How-to guides are wholly distinct from tutorials**. They are often confused, but the user needs that they serve are quite different. Conflating them is at the root of many difficulties that afflict documentation. See :ref:`tutorials-how-to` for a discussion of this distinction.

In another confusion, how-to guides are often construed merely as procedural guides. But solving a problem or accomplishing a task cannot always be reduced to a procedure. Real-world problems do not always offer themselves up to linear solutions. The sequences of action in a how-to guide sometimes need to fork and overlap, and they have multiple entry and exit-points. Often, a how-to guide will need the user to rely on their judgement in applying the guidance it can provide.
    

=================

Key principles
---------------------------------------

A how to-guide is concerned with work - a task or problem, with a practical goal. *Maintain focus on that goal*. 

..  sidebar:: How-to characteristics

    * focused on tasks or problems
    * assume the user knows what they want to achieve
    * action and only action
    * no digression, explanation, teaching

Anything else that's added distracts both you and the user and dilutes the useful power of the guide. Typically, the temptations are to explain or to provide reference for completeness. Neither of these are part of guiding the user in their work. They get in the way of the action; if they're important, link to them.

A how-to guide serves the work of the already-competent user, whom you can assume to know what they want to do, and to be able to follow your instructions correctly.


Address real-world complexity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A how-to guide needs to be adaptable to real-world use-cases**. One that is useless for any purpose except *exactly* the narrow one you have addressed is rarely valuable. You can't address every possible case, so you must find ways to remain open to the range of possibilities, in such a way that the user can adapt your guidance to their needs.

Omit the unnecessary
~~~~~~~~~~~~~~~~~~~~

In how-to guides, **practical usability is more helpful than completeness.** Whereas a tutorial needs to be a complete,
end-to-end guide, a how-to guide does not. It should start and end in some reasonable, meaningful place, and require
the reader to join it up to their own work.


Provide a set of instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A how-to guide describes an *executable solution* to a real-world problem or task. It's in the form of a contract: if you're facing this situation, then you can work your way through it by taking the steps outlined in this approach. The steps are in the form of *actions*.

"Actions" in this context includes physical acts, but also thinking and judgement - solving a problem involves thinking it through. A how-to guide should address how the user thinks as well as what the user does.


Describe a logical sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The fundamental structure of a how-to guide is a *sequence*. It implies logical ordering in time, that there is a sense and meaning to this particular order.

In many cases, the ordering is simply imposed by the way things must be (step two requires completion of step one, for example). In this case it's obvious what order your directions should take.

Sometimes the need is more subtle - it might be possible to *perform* two operations in either order, but if for example one operation helps set up the user's working environment or even their thinking in a way that benefits the other, that's a good reason for putting it first.


Seek flow
~~~~~~~~~

At all times, try to ground your sequences in the patterns of the *user's* activities and thinking, in such a way that the guide acquires *flow*: smooth progress.  

Achieving flow means successfully understanding the user. Paying attention to sense and meaning in ordering requires paying attention to the way human beings think and act, and the needs of someone following directions. 

Again, this can be somewhat obvious: a workflow that has the user repeatedly switching between contexts and tools is clearly clumsy and inefficient. But you should look more deeply than this. What are you asking the user to think about, and how will their thinking flow from subject to subject during their work? How long do you require the user to hold thoughts open before they can be resolved in action? If you require the user to jump back to earlier concerns, is this necessary or avoidable?

A how-to guide is concerned not just with logical ordering in time, but action taking place in time. Action, and a guide to it, has pace and rhythm. Badly-judged pace or disrupted rhythm are both damaging to flow.

At its best, how-to documentation gives the user flow. There is a distinct experience of encountering a guide that appears to *anticipate* the user - the documentation equivalent of a helper who has the tool you were about to reach for, ready to place it in your hand. 


Pay attention to naming
~~~~~~~~~~~~~~~~~~~~~~~~

**Choose titles that say exactly what a how-to guide shows.**

* good: *How to integrate application performance monitoring*
* bad: *Integrating application performance monitoring* (maybe the document is about how to decide whether you should, not about how to do it)
* very bad: *Application performance monitoring* (maybe it's about *how* - but maybe it's about *whether*, or even just an explanation of *what* it is)

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


================

Applied to food and cooking
---------------------------

Consider a recipe, an excellent model for a how-to guide. A recipe clearly defines what will be achieved by following it, and **addresses a specific question** (*How do I make...?* or *What can I make with...?*).

..  image:: /images/old-recipe.jpg
    :alt: A recipe contains a list of ingredients and a list of steps.

It's not the responsibility of a recipe to *teach* you how to make something. A professional chef who has made exactly the same thing multiple times before may still follow a recipe - even if they *created* the recipe themselves - to ensure that they do it correctly.

Even following a recipe **requires at least basic competence**. Someone who has never cooked before should not be expected to follow a recipe with success, so a recipe is not a substitute for a cooking lesson.

Someone who expected to be provided with a recipe, and is given instead a cooking lesson, will be disappointed and annoyed. Similarly, while it's interesting to read about the context or history of a particular dish, the one time you don't want to be faced with that is while you are in the middle of trying to make it. A good recipe follows a well-established format, that excludes both teaching and discussion, and focuses only on **how** to make the dish concerned.
