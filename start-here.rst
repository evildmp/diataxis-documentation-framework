.. meta::
   :description:
       The best way to get started with Diátaxis is by applying it to documentation problems.

=======================================
Start here - Diátaxis in five minutes
=======================================

..  sidebar::

    Treat this website as a handbook or a toolbox that you make use of when you need it. 

You don't need to read everything on this website to make sense of Diátaxis, or to start using it in practice. In fact I recommend that you don't. **The best way to get started with Diátaxis is by applying it** - to something, however small.

Read this page for a brief primer. Each section contains links to more in-depth material; refer to that when you need it - when you're actually at work, or reflecting on the documentation problems you have encountered.

------------

The four kinds of documentation
===============================

The core idea of Diátaxis is that there are fundamentally four identifiable kinds of documentation, that respond to four different needs. The four kinds are: *tutorials*, *how-to guides*, *reference* and *explanation*. Each has a different purpose, and needs to be written in a different way.


Tutorials
---------

..  sidebar::
   
    * :ref:`Tutorials in more detail <tutorials>`
    * :ref:`Why tutorials are completely different from how-to guides <tutorials-how-to>`

**A tutorial is a lesson**, that takes a student by the hand through a learning experience. A tutorial is always *practical*: the user *does* something, under the guidance of an instructor. A tutorial is designed around an encounter that the learner can make sense of, in which the instructor is responsible for the learner's safety and success.

A driving lesson is a good example of a tutorial. The purpose of the lesson is to develop skills and confidence in the student, not to get from A to B. A software example could be: *Let's create a simple game in Python*.

*The user will learn through what they do* - not because someone has tried to teach them.

In documentation, the special difficulty is that the instructor is condemned to be absent, and is not there to monitor the learner and correct their mistakes. The instructor must somehow find a way to be present through written instruction alone.


How-to guides
-------------

..  sidebar::
   
    * :ref:`How-to guides in more detail <how-to>`

**A how-to guide addresses a real-world goal or problem**, by providing practical directions to help the user who is in that situation. 

A how-to guide always addresses an already-competent user, who is expected to be able to use the guide to help them get their work done. In contrast to a tutorial, a how-to guide is concerned with *work* rather than *study*. 

A how-to guide might be: *How to store cellulose nitrate film* (in motion picture photography) or *How to configure frame profiling* (in software). Or even: *Troubleshooting deployment problems*.


Reference
---------

..  sidebar::
   
    * :ref:`Reference in more detail <reference>`

**Reference guides contain the technical description** - facts - that a user needs in order to do things correctly: accurate, complete, reliable information, free of distraction and interpretation. They contain *propositional or theoretical knowledge*, not guides to action.

Like a how-to guide, reference documentation serves the user who is at *work*, and it's up to the user to be sufficiently competent to interpret and use it correctly.

*Reference material is neutral.* It is not concerned with what the user is doing. A marine chart could be used by a ship's navigator to plot a course, but equally well by a prosecuting magistrate in a legal case.

Where possible, the architecture of reference documentation should reflect the structure or architecture of the thing it's describing - just like a map does. If a method is part of a class that belongs to a certain module, then we should expect to see the same relationship in the documentation too.  


Explanation
-----------

..  sidebar::
   
    * :ref:`Explanation in more detail <explanation>`
    * :ref:`Understanding the difference between reference and explanation <reference-explanation>`


**Explanatory guides provide context and background.** They serve the need to understand and put things in a bigger picture. Explanation joins things together, and helps answer the question *why?*

Explanation often needs to circle around its subject, and approach it from different directions. It can contain opinions and take perspectives.

Like reference, explanation belongs to the realm of propositional knowledge rather than action. However its purpose is to serve the user's study - as tutorials do - and not their work.

Often, writers of tutorials who are anxious that their students should *know* things overload their tutorials with distracting and unhelpful explanation. It would be much more useful to give the learner the most minimal explanation ("Here, we use HTTPS because it's safer") and then link to an in-depth article (*Secure communication using HTTPS encryption*) for when the user is ready for it.


-----------

The Diátaxis map
================

The four kinds of documentation and the relationships between them can be summarised in the Diátaxis map. 

..  sidebar::
   
    * :ref:`The map in more detail <map>`

Diátaxis is not just a list of four different things, but a conceptual arrangement of them. It shows how the four kinds of documentation are related to each other, and distinct from each other.

Crossing or blurring the boundaries described in the map is at the heart of a vast number of problems in documentation. 

.. image:: /images/diataxis.png
   :alt: Diátaxis


-----------

The Diátaxis compass
====================

As you can see from the map:

* tutorials and how-to guides are concerned with what the user *does* (**action**)
* reference and explanation are about what the user *knows* (**cognition**)

On the other hand: 

* tutorials and explanation serve the *acquistion* of skill (the user's **study**)
* how-to guides and reference serve the *application* of skill (the user's **work**)

But a map doesn't tell you what to *do* - it's reference. To guide your action you need a different sort of tool, in this case, a kind of Diátaxis compass.

..  sidebar::
   
    * :ref:`The compass in more detail <compass>`

The compass is useful in two different ways.

When creating documentation, it helps clarify your own intentions, and helps make sure you're actually doing what you think you're doing.

When looking at documentation, it helps understand what's going on in it, and makes problems stand out.

The compass is not nearly as eye-catching as the map, but when you're at work puzzling over a documentation problem it's what will help you move forward.

.. list-table::
   :widths: 33 33 34
   :header-rows: 1
   :stub-columns: 0
   :class: wider

   * - If the content...
     - ...and serves the user's...
     - ...then it must belong to...
   * - informs action
     - acquisition of skill
     - a tutorial
   * - informs action
     - application of skill
     - a how-to guide
   * - informs cognition
     - application of skill
     - reference
   * - informs cognition
     - acquisition of skill
     - explanation



-----------

Working
=======

There is a very simple workflow for Diátaxis.

..  sidebar::
   
    :ref:`how-to-use-diataxis`

1. Consider what you see in the documentation, in front of you right now (which might be literally nothing, if you haven't started yet).

2. Ask: *is there any way in which it could be improved?*

3. Decide on *one* thing you could do to it right now, however small, that would improve it.

4. Do that thing. 

And then repeat. 

That's it. 


-----------

Do what you like
================

You can do what you like with Diátaxis. You don't have to believe in it and there is no exam. It is a wholly pragmatic approach. I think it's *true*, but what matters is that it actually helps people create better documentation. If you find one idea or insight in it that seems to be worthwhile, help yourself to that.

There is an extensively elaborated theory around Diátaxis, but you don't need to subscribe to it, or even read about it. Diátaxis doesn't require a commitment to pursue it to a final end. 

You can do just one thing, right now, and even if you do nothing else ever after, you will at least have made that one improvement. (In practice what you will find is that each thing you do will give you a clue as to the next thing to do - you only need to keep doing them.)


Get started
===========

At this point, you have read everything you need to get started with Diátaxis. 

You can read more if you want, and eventually you probably should, but *you will get the most value from the guidance in this website when you turn to it with a problem or a question*. That's when it comes alive. 
