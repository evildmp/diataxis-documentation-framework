.. _tutorials:

About tutorials
===============

..  rubric:: Tutorials are **lessons** that take the reader by the hand through a series of steps to complete a project of some kind. Tutorials are **learning-oriented**.

===========

A tutorial must help a beginner achieve basic competence with a product, so that they can go on to use the product
for their own purposes.

A tutorial also needs to show the learner that they can be successful with the product - by having them do something
both *meaningful* and *attainable*.

..  image:: /images/overview-tutorials.png
    :alt: Tutorials - learning-oriented guides that describe practical steps and are intended to serve our study.
    :class: sidebar

A tutorial in other words is a lesson - a lesson concerned with *learning how* rather than *learning that*, because
it's concerned with *skill*: practical, not theoretical knowledge.

Having completed a tutorial, the learner should be in a position to start to make sense of the rest of the
documentation, and the product itself.

For a product, a tutorial turns new learners into users. An inadequate tutorial can prevent a project from
acquiring new users.

=================


The tutorial as a lesson
-------------------------

A lesson entails a relationship between a teacher and a pupil. In all learning of this kind, **learning takes place
through what the pupil does**.

Any facts and explanations that are presented in teaching are almost irrelevant to what the pupil will learn - what
matters is what the teacher gets the pupil to do.

For our purposes, **a lesson is a learning experience**. If you are not providing your learner with a learning
experience, your tutorial isn't doing the job it needs to.


Obligations of the teacher
~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  sidebar::

    It's not easy being a teacher.

**The teacher has responsibility**: for what the pupil is to learn, what the pupil will do in order to learn it, and
for the pupil's success. The only responsibility of the pupil is to be attentive and to follow the teacher's directions
as closely as they can. **There is no responsibility on the pupil to learn, understand or remember** - the learner's
*only* obligation in this contract is to do things as directed.

At the same time, the exercise you put your pupils through must be:

* *meaningful* - the pupil needs to have a sense of achievement
* *successful* - the pupil needs to be able to complete it
* *logical* - the path that the pupil takes through it needs to make sense
* *usefully complete* - the pupil must have an encounter with all of the actions, concepts and tools they need to become
  familiar with


The problem of tutorials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, tutorials are the weakest part of documentation, the most misunderstood and the most difficult to do well.
Most software projects have poor - or non-existent - tutorials.

In an ideal lesson, the teacher is present and interacts with and responds to the student. A written tutorial is a
far-from-perfect substitute for this.

..  sidebar::

    You can easily find that writing and maintaining your tutorials occupies as much time and energy as all the other
    parts of documentation put together.

The sheer amount of work required to create and maintain tutorials is much more than that required for the
other parts of documentation. It's hard enough to put together a learning experience that meets all the standards
described above; in many contexts the product itself evolves rapidly, meaning that all that work needs to be done
again to ensure that the tutorial still performs its required functions.

Finally, you will find that no other part of your documentation is subject to revisions the way your tutorials are.
You only have to change a reference or how-to guide if something in the product changes, and even then, usually only
part of it needs to change. In the case of a tutorial, you may come to the conclusion that the whole lesson should be
completely rewritten, because you have thought of a better way to produce a learning experience for the pupil.

===============

Food and cooking
--------------------

Perhaps you have had the experience of teaching a child to cook, in which case you'll have encountered most of the main
demands imposed by a tutorial.

..  image:: /images/anselmo.jpg
    :alt:

As you probably realised, if you didn't know it already: the important thing in this experience isn't *what* you
teach the child to cook. The only thing that really matters is that the child should enjoy the experience of working in
the kitchen with you, and gains **confidence**, and wants to do it again.

That needs to be the outcome of each learning experience in the kitchen; if it's not, then even if the child
learned something, the learning journey is at risk of being ended there.

A teacher always feels some natural anxiety that the pupil should learn. There's a temptation to press that too hard -
which is both unnecessary and counter-productive.

The child *will* learn, in its own time, at its own pace, **through the activities** you do together, and not from the
things you say or show.

It will learn important things through *repetition*, over time: how to hold a knife, that it's important to wash hands
before handling food, how to use measuring equipment, how to time things. It will learn what it's like to work in the
kitchen, where to find utensils.

With a young child, you will often find that the lesson suddenly has to end before you'd completed what you set out to
do. This is normal and expected; children have short attention spans. As long as the child managed to achieve something
- however small - and enjoyed doing it, it will have laid down something in the construction of its technical
expertise, that can be returned to and built upon next time.

Cooking is a matter of **craft**. It’s knowledge - but it's *practical* knowledge, not *theoretical* knowledge.
It's the same for any product: using it is a skill, and when we learn a new craft or skill, we always begin learning it
by doing.

=================

Writing a good tutorial
---------------------------------

Don't try to teach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Allow the user to learn. **In the beginning, we only learn anything by doing** - it’s how we learn to talk, or walk.

..  sidebar:: Anti-pedagogical temptations

    * abstraction, generalisation
    * explanation
    * choices
    * information

Give your learner things to *do*, through which they can learn. Only your pupil can learn. Sadly, however much you desire
it, you will not be able to learn for your pupil. You cannot make them learn. All you can do is make it so *they* can
learn.

As you lead the pupil through the steps you have devised, have them use the tools and perform the operations they’ll
need to become familiar with, building up from the simplest ones at the start to more complex ones.


Get the user started
~~~~~~~~~~~~~~~~~~~~

Your job is to **get the learner started**, not to turn them into an expert. Don’t ever be embarrassed to start right at
the beginning: a user can skim rapidly over what’s unnecessary, but if they need something and it’s not there, you risk
losing them altogether. It’s also perfectly acceptable if what you get the beginner to do is not the way an experienced
person would, or even if it’s not the ‘correct’ way - a tutorial for beginners is not the same thing as a manual for
best practice.

The point of a tutorial is to help your learner set out safely on their journey, not to get them to a final destination.

The only reason not to lower the threshold is because you decide that you don’t want the responsibility of teaching
beginners at below a certain level, or you judge that a certain level of skill is a reasonable prerequisite for using
the product at all.


Provide a complete picture before they start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It’s important to **allow the learner to form an idea of what they will achieve right from the start**. As well as
helping to set expectations, it allows them to see themselves building towards the completed goal as they work.
Surprising them with the result at the end will diminish, not augment, the value of what they achieve. It’s very
enjoyable to reveal impressive conclusions with a flourish, but you should save that for your magic tricks and novels.

Providing the picture the learner needs in a tutorial can be as simple as informing them at the outset: *In this
tutorial you will build a simple website using Django and deploy it using Docker. Along the way you will use a cloud
storage service for handling media files, and will configure your application to use it.*


Ensure that the tutorial works reliably
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of your jobs as a tutor is to inspire the beginner’s confidence. Confidence can only be built up layer by layer,
but is easily shaken. It helps to maintain a friendly tone, as does consistent use of language, and a logical
progression through the material. However, the single most important requirement is that **what you ask the beginner to
do must work**. The learner needs to see that when they follow your directions, they will attain the results you
promise.

It’s hard work to create a reliable experience, but that is what you must aspire to in creating a tutorial.


Ensure the user sees results immediately
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your learner is probably doing new and strange things that they don't understand. Don't make them do too many before
they see a result from their actions. As far as possible, the effect of every action should be clear to them as soon as
possible. The relation of cause and effect should be evident. Finally, each result should be something that the user
can see as meaningful.

**Every step the learner follows should produce a comprehensible result, however small.**


Make your tutorial repeatable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unless you're very lucky, the users of your tutorial will have different levels of skill and understanding. They might
also be using different tools and operating systems and you can't rely on them having the same resources or
environment.

This makes repeatable reliability extremely hard to achieve, and yet, **your tutorial should work for all users, every
time**.

You have no alternative but to test your tutorials regularly to make sure that they still work as expected.


Describe concrete steps, not abstract concepts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Tutorials are composed of concrete steps**, not abstract discussion. Be specific and particular, about actions and
outcomes.

Resist the temptation to introduce abstraction. All learning proceeds from the particular and concrete to the general
and abstract. It's later, after a beginner has encountered multiple concrete examples that they are ready to see a
pattern in them and seek an abstract account of what is happening - until that time, requiring the learner to handle
levels of abstraction before they have even had a chance to grasp the concrete is confusing and places unnecessary
burdens on them.

It's hard to resist this temptation, because once we have grasped something, we rely on the power of abstraction
to frame it to ourselves - and that's how we want to frame it to others. But it's simply not how learning or
successful teaching works.


Offer only minimum, necessary, explanation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**If the learner doesn't need an explanation in order to complete the tutorial, don't explain.**

For example, it's enough to say something like: *We're using HTTPS because it's more secure.* There is a place
for extended discussion and explanation of HTTPS, but not in a tutorial. Sometimes, even that much explanation is
more than required.

It can seem problematic that we are asking a user to do things, without much explanation why. In practice, for the
learner, it rarely is. The learner is focused on following your directions and getting a result; their time for wanting
to know more about the *why* of what they're doing will come later. By all means include links to further explanatory
material, if you feel it's required, but try to resist the temptation to interrupt the flow of a tutorial by digressing
into explanation.


Ignore options and alternatives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your job is to guide the learner to a successful conclusion. There may be many interesting diversions along the way
(different options for the command you're using, different ways to use the API, different approaches to the task you're
describing) - ignore them. **Your guidance needs to remain focused on what's required to reach the conclusion**, and
everything else can be left for another time.

Doing this helps keep your tutorial shorter and crisper, and saves both you and the reader from having to do extra
cognitive work.

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
