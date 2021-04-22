.. _tutorials:

About tutorials
===============

..  rubric:: Tutorials are **lessons** that take the reader by the hand through a series of steps to complete a project of some kind. Tutorials are **learning-oriented**.

===========

Tutorials are what your project needs in order to show a beginner that they can achieve something with it.

They are wholly learning-oriented, and specifically, they are oriented towards *learning how* rather than *learning that*.

.. image:: /images/overview-tutorials.png
   :alt: 'Tutorials - learning oriented, practical steps, that serve our study'
   :align: right
   :width: 50%

**You are the teacher**, and you are **responsible** for what the student will do. Under **your** instruction, the student will execute a series of actions to achieve some **end**.

The end and the actions are up to you, but deciding what they should be can be hard work. The end has to be *meaningful*, but also *achievable* for a complete beginner.

The important thing is that having done the tutorial, the learner is in a position to make sense of the rest of the documentation, and the software itself.

Most software projects have really bad - or non-existent - tutorials. Tutorials are what will turn your learners into users. **A bad or missing tutorial will prevent your project from acquiring new users.**

Of the sections describing the four kinds of documentation, this is by far the longest - that's because tutorials are the most
misunderstood and most difficult to do well. The best way of teaching is to have a teacher present, interacting with the
student. That's rarely possible, and our written tutorials will be at best a far-from-perfect substitute. That's all the more
reason to pay special attention to them.

Tutorials need to be useful for the beginner, easy to follow, meaningful and extremely robust, and kept up-to-date. You
might well find that writing and maintaining your tutorials can occupy as much time and energy as the the other three
parts put together.

===============

Analogy from cooking
--------------------

.. image:: /images/anselmo.jpg
   :alt: 'a child cooking'
   :align: right
   :width: 379

Consider an analogy of teaching a child to cook.

*What* you teach the child to cook isn’t really important. What’s important is that the child finds it enjoyable, and gains confidence, and wants to do it again.

*Through* the things the child does, it will learn important things about cooking. It will learn what it is like to be in the kitchen, to use the utensils, to handle the food.


This is because using **software, like cooking, is a matter of craft**. It’s knowledge - but it is *practical* knowledge, not *theoretical* knowledge.

When we learn a new craft or skill, we always begin learning it by doing.

=================

How to write good tutorials
---------------------------

..  sidebar:: Non-didactic temptations

    * abstraction, generalisation
    * explanation
    * choices
    * information


Allow the user to learn by doing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**In the beginning, we only learn anything by doing** - it’s how we learn to talk, or walk.

In your software tutorial, your learner needs to *do* things. The different things that they do while following your tutorial need to cover a wide range of tools and operations, building up from the simplest ones at the start to more complex ones.


Get the user started
~~~~~~~~~~~~~~~~~~~~

It’s perfectly acceptable if your beginner’s first steps are hand-held baby steps. It’s also perfectly acceptable if what you get the beginner to do is not the way an experienced person would, or even if it’s not the ‘correct’ way - a tutorial for beginners is not the same thing as a manual for best practice.

The point of a tutorial is to get your learner **started on their journey**, not to get them to a final destination.


Make sure that your tutorial works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of your jobs as a tutor is to inspire the beginner’s confidence: in the software, in the tutorial, in the tutor and, of course, in their own ability to achieve what’s being asked of them.

There are many things that contribute to this. A friendly tone helps, as does consistent use of language, and a logical progression through the material. But the single most important thing is that **what you ask the beginner to do must work**. The learner needs to see that the actions you ask them to take have the effect you say they will have.

If the learner's actions produce an error or unexpected results, your tutorial has failed - even if it’s not your fault. When your students are there with you, you can rescue them; if they’re reading your documentation on their own you can’t - so you have to prevent that from happening in advance. This is without doubt easier said than done.


Ensure the user sees results immediately
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Everything the learner does should accomplish something comprehensible, however small.** If your student has to do strange and incomprehensible things for two pages before they even see a result, that’s much too long. The effect of every action should be visible and evident as soon as possible, and the connection to the action should be clear.

The conclusion of each section of a tutorial, or the tutorial as a whole, must be a meaningful accomplishment.


Make your tutorial repeatable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Your tutorial must be reliably repeatable.** This not easy to achieve: people will be coming to it with different operating systems, levels of experience and tools. What’s more, any software or resources they use are quite likely themselves to change in the meantime.

The tutorial has to work for all of them, every time.

Tutorials unfortunately need regular and detailed testing to make sure that they still work.


Focus on concrete steps, not abstract concepts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Tutorials need to be concrete**, built around specific, particular actions and outcomes.

The temptation to introduce abstraction is huge; it is after all how most computing derives its power. But all learning proceeds from the particular and concrete to the general and abstract, and asking the learner to appreciate levels of abstraction before they have even had a chance to grasp the concrete is poor teaching.


Provide the minimum necessary explanation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Don’t explain anything the learner doesn’t need to know in order to complete the tutorial.** Extended discussion is important - just not in a tutorial. In a tutorial, it is an obstruction and a distraction. Only the bare minimum is appropriate. Instead, link to explanations elsewhere in the documentation.


Focus only on the steps the user needs to take
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Your tutorial needs to be focused on the task in hand.** Maybe the command you’re introducing has many other options, or maybe there are different ways to access a certain API. It doesn’t matter: right now, your learner does not need to know about those in order to make progress.

==============

The language of tutorials
-------------------------

*In this tutorial, you will...*
    Describe what the learner will accomplish (note - not: "you will learn...").
*First, do x. Now, do y. Now that you have done y, do z.*
    No room for ambiguity or doubt.
*We must always do x before we do y because... (see Explanation for more details).*
    Provide minimal explanation of actions in the most basic language possible. Link to more detailed explanation.
*The output should look something like this...*
    Give your learner clear expectations.
*Notice that... Remember that...*
    Give your learner plenty of clues to help confirm they are on the right track and orient themselves.
*You have built a secure, three-layer hylomorphic stasis engine...*
    Describe (and admire, in a mild way) what your learner has accomplished (note - not: "you have learned...")

=================

Example from Divio's documentation
----------------------------------

Have a look at `our tutorials <https://docs.divio.com/en/latest/introduction>`_.

.. image:: /images/django-tutorial-example.png
   :alt: 'Django tutorial example'
   :align: right
   :width: 379

In particular, see the tutorial for Django. The promise that the tutorial makes is: if you have the basic knowledge
required to follow this tutorial, and you follow its directions, you will end up with with a working Django web
application, complete with Postgres database, S3 media storage, and so on. In order to work as a tutorial, it has to
fulfil that promise.

Note that it doesn’t tell you what you will *learn*, just what you will *do*. The learning comes out of that doing. The
tutorial takes full responsibility for what you will do and the order in which you will do it.
