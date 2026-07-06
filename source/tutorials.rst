.. _tutorials:

Tutorials
=========

..  rubric:: A tutorial is an **experience** that takes place under the guidance of a tutor. A tutorial is always **learning-oriented**. 

===========

A tutorial is a *practical activity*, in which the student learns by doing something meaningful, towards some achievable goal. 

A tutorial serves the user's *acquisition* of skills and knowledge - their study. Its purpose is not to help the user get something done, but to help them learn. 

..  image:: /images/overview-tutorials.png
    :alt: Tutorials - learning-oriented guides that describe practical steps and are intended to serve our study.
    :class: sidebar

A tutorial in other words is a lesson. 

It's important to understand that while a student will learn by doing, what the student *does* is not necessarily what they *learn*. Through doing, they will acquire theoretical knowledge (i.e. facts), understanding, familiarity. They will learn how things relate to each other and interact, and how to interact with them. They will learn the names of things, the use of tools, workflows, concepts, commands. And so on.


=================


The tutorial as a lesson
------------------------

A lesson entails a relationship between a teacher and a pupil. In all learning of this kind, *learning takes place as the pupil applies themself to tasks under the instructor's guidance*.

A lesson is a *learning experience*. In a learning experience, what matters is what the learner does and what happens. By contrast, the teacher's explanations and recitations of fact are far less important.

A good lesson gives the learner confidence, by showing them that they can be successful in a certain skill or with a certain product.


Obligations of the teacher
~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  sidebar::

    It's not easy being a teacher.

A lesson is a kind of contract between teacher and student, in which nearly all the responsibility falls upon the teacher. The teacher has responsibility for what the pupil is to learn, what the pupil will do in order to learn it, and for the pupil's success. Meanwhile, the only responsibility of the pupil in this contract is to be attentive and to follow the teacher's directions as closely as they can. There is no responsibility on the pupil to learn, understand or remember.

At the same time, the exercise you put your pupils through must be:

* *meaningful* - the pupil needs to have a sense of achievement
* *successful* - the pupil needs to be able to complete it
* *logical* - the path that the pupil takes through it needs to make sense
* *usefully complete* - the pupil must have an encounter with all of the actions, concepts and tools they need to become familiar with


The problem of tutorials
~~~~~~~~~~~~~~~~~~~~~~~~

In general, tutorials are rarely done well, partly because they are genuinely difficult to do well, and partly because they are not well understood. In software, many products lack good tutorials, or lack tutorials completely; tutorials are often conflated with how-to guides.

In an ideal lesson, the teacher is present and interacts with and responds to the student, correcting their mistakes and checking their learning. In documentation, none of this is possible.

..  sidebar::

    Writing and maintaining tutorials can consume a remarkable amount of effort and time.

It's hard enough to put together a learning experience that meets all the standards described above; in many contexts the product itself evolves rapidly, meaning that all that work needs to be done again to ensure that the tutorial still performs its required functions.

You will also often find that no other part of your documentation is subject to revisions the way your tutorials are. Elsewhere in documentation, changes and improvements can generally be made discretely; in tutorials, where the end-to-end learning journey must make sense, they often cascade through the entire story. 

Finally, tutorials contain the additional complication of the distinction between *what is to be learned* and *what is to be done*. Not only must the creator of a tutorial have a good sense of what the user must learn, and when, they must also devise a meaningful learning journey that somehow delivers all that.


=================

Key principles
--------------

A tutorial is a pedagogical problem. 

It's not an easy problem, but neither is it a mystery. The principles outlined below - repetition, action, small steps, results early and often, concreteness and so on - are not secrets, but they are not always well understood.

Still, there are straightforward, effective ways to address the problems of pedagogy in practice.

..  sidebar:: Anti-pedagogical temptations

    * abstraction, generalisation
    * explanation
    * choices
    * information

The first rule of teaching is simply: **don't try to teach**. Your job, as a teacher, is to provide the learner with an experience that will allow them to learn. A teacher inevitably feels a kind of anxiety to impart knowledge and understanding, but if you give into it and try to teach by telling and explaining, you will jeopardise the learning experience. 

Instead, *allow learning to take place*, and trust that it will. Give your learner things to *do*, through which they can learn. Only your pupil can learn. Sadly, however much you desire it, you will not be able to learn for your pupil. You cannot make them learn. All you can do is make it so *they* can learn.


Show the learner where they'll be going
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's important to allow the learner to form an idea of what they will achieve right from the start. As well as helping to set expectations, it allows them to see themselves building towards the completed goal as they work. 

Providing the picture the learner needs in a tutorial can be as simple as informing them at the outset: *In this tutorial we will create and deploy a scalable web application. Along the way we will encounter containerisation tools and services.*

This is not the same as saying: *In this tutorial you will learn...* - which is presumptuous and a very poor pattern. 


Deliver visible results early and often
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your learner is probably doing new and strange things that they don't fully understand. Understanding comes from being able to make connections between causes and effects, so let them see the results and make the connections rapidly and repeatedly. Each one of those results should be something that the user can see as meaningful.

Every step the learner follows should produce a comprehensible result, however small.


Maintain a narrative of the expected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At every step of a tutorial, the user experiences a moment of anxiety: will this action produce the correct result? Part of the work of a successful tutorial is to keep providing feedback to the learner that they are indeed on the right path.

Keep up a narrative of expectations: "You will notice that ..."; "After a few moments, the server responds with ...". Show the user actual example output, or even the exact expected output.

If you know know in advance what the likely signs of going wrong are, consider flagging them: "If the output doesn't show ..., you have probably forgotten to ...".

It's helpful to prepare the user for possibly surprising actions: "The command will probably return several hundred lines of logs in your terminal."


Point out what the learner should notice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Learning requires reflection. This happens at multiple levels and depths, but one of the first is when the learner  observes the signs in their environment. In a lesson, a learner is typically too focused on what they are doing to notice them, unless they are prompted by the teacher.

Your job as teacher is to close the loops of learning by pointing things out, in passing, as the lesson moves along. This can be as simple as pointing out how a command line prompt changes, for example.

Observing is an active part of a craft, not a merely passive one. It means paying attention to the environment, a skill in itself. It's often neglected.


Target *the feeling of doing*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In all skill or craft, the accomplished practitioner experiences a *feeling of doing*, a joined-up purpose, action, thinking and result. 

As skill develops, it flows in a confident rhythm and becomes a kind of pleasure. It's the pleasure of walking, for example.

..  sidebar::

    Pay attention to your own *feeling of doing* in your work. What is it like to perform a particular operation?

Your learner's skill depends upon their discovering this feeling, and its becoming a pleasure. 

Your challenge as the creator of a tutorial is to ensure that its tasks tie together purpose and action so they become a cradle for this feeling.


Encourage and permit repetition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Learners will return to and repeat an exercise that gives them success, for the pleasure they find in getting the expected result. Doing so reaffirms to them that they can do it, and that it works. 

Repetition is a key to establishing the feeling to doing; being at home with that feeling is a foundational layer of learning.

..  sidebar::

    Repetition is not the best teacher - sometimes it's the *only* teacher.

In your tutorial, try to make it possible for a particular step and result to be repeated. This can be difficult, for example in operations that are not reversible (making it hard to go back to a previous step) - but seek it wherever you can. Watching a user follow a tutorial, you may often be amazed to see how often they choose to repeat a step. They are doing it just to see that the same thing really does happen again.


Ruthlessly minimise explanation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*A tutorial is not the place for explanation.* In a tutorial, the user is focused on correctly following your directions and getting the expected results. *Later*, when they are ready, they will seek explanation, but right now they are concerned with *doing*. Explanation distracts their attention from that, and blocks their learning.

For example, it's quite enough to say something like: *We're using HTTPS because it's more secure.* There is a place for extended discussion and explanation of HTTPS, but not now. Instead, provide a link or reference to that explanation, so that it's available, but doesn't get in the way.

..  sidebar::

    Explanation is only pertinent at the moment the *user* wants it. It is not for the documentation author to decide. 

Explanation is one of the hardest temptations for a teacher to resist; even experienced teachers find it difficult to accept that their students' learning does not depend on explanation. This is perfectly natural. Once we have grasped something, we rely on the power of abstraction to frame it to ourselves - and that's how we want to frame it to others. Understanding means grasping general ideas, and abstraction is the logical form of understanding - but these are not what we need in a tutorial, and it's not how successful learning or teaching works.

One must see it for oneself, to see the focused attention of a student dissolve into air, when a teacher's well-intentioned explanation breaks the magic spell of learning.


... and focus on the concrete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a learning situation, your student is in the moment, a moment composed of concrete things. You are responsible for setting up and maintaining the student's flow, from one concrete action and result to another.

Focus on *this* problem, *this* action, *this* result, in such a way that you lead the learner from step to concrete step. 

It might seem that by maintaining focus on the concrete and particular that you deny the student the opportunity to see or grasp the larger general patterns, but the contrary is true. The one thing our minds do spectacularly well is to perceive general patterns from concrete examples. All learning moves in one direction: from the concrete and particular, towards the general and abstract. The latter *will* emerge from the former.


Ignore options and alternatives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your job is to guide the learner to a successful conclusion. There may be many interesting diversions along the way (different options for the command you're using, different ways to use the API, different approaches to the task you're describing) - ignore them. *Your guidance needs to remain focused on what's required to reach the conclusion*, and everything else can be left for another time.

Doing this helps keep your tutorial shorter and crisper, and saves both you and the reader from having to do extra cognitive work.


Aspire to perfect reliability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the above are general principles of pedagogy, but there is a special burden on the creator of a tutorial. 

A tutorial must inspire confidence. Confidence can only be built up layer by layer, and is easily shaken. At every stage, when you ask your student to do something, they must see the result you promise. A learner who follows your directions and doesn't get the expected results will quickly lose confidence, in the tutorial, the tutor and themselves.

..  sidebar::

    You are required to be present, but condemned to be absent. 

A teacher who's there with the learner can rescue them when things go wrong. In a tutorial, you can't do that. Your tutorial ought to be so well constructed that things *can't* go wrong, that your tutorial works for every user, every time.

It's hard work to create a reliable experience, but that is what you must aspire to in creating a tutorial.

Your tutorial will have flaws and gaps, however carefully it is written. You won't discover them all by yourself, you will have to rely on users to discover them for you. The only way to learn what they are is by finding out what actually happens when users do the tutorial, through extensive testing and observation.


==============

The language of tutorials
-------------------------

We ...
    The first-person plural affirms the relationship between tutor and learner: you are not alone; we are in this together. 
In this tutorial, we will ...
    Describe what the learner will accomplish.
First, do x. Now, do y. Now that you have done y, do z.
    No room for ambiguity or doubt.
We must always do x before we do y because... (see Explanation for more details).
    Provide minimal explanation of actions in the most basic language possible. Link to more detailed explanation.
The output should look something like ...
    Give your learner clear expectations.
Notice that ... Remember that ... Let's check ...
    Give your learner plenty of clues to help confirm they are on the right track and orient themselves.
You have built a secure, three-layer hylomorphic stasis engine...
    Describe (and admire, in a mild way) what your learner has accomplished.


===============

Applied to food and cooking
---------------------------

..  image:: /images/anselmo.jpg
    :alt: A child proudly showing a dish he has helped prepare

Someone who has had the experience of teaching a child to cook will understand what matters in a tutorial, and just as importantly, the things that don't matter at all.

It really doesn't matter what the child makes, or how correctly they do it. The value of a lesson lies in what the child gains, not what they produce.

Success in a cooking lesson with a child is not the culinary outcome, or whether the child can now repeat the processes on their own. Success is when the child acquires the knowledge and skills you were hoping to impart. 

It's a crucial condition of this that the child discovers pleasure in the experience of being in the kitchen with you, and wants to return to it. Learning a skill is never a once and for all matter. Repetition is always required. 

Meanwhile, the cooking lesson might be framed around the idea of learning how to prepare a particular dish, but what we actually need the child to learn might be things like: *that we wash our hands before handling food*; *how to hold a knife*; *why the oil must be hot*; *what this utensil is called*, *how to time and measure things*. 

The child learns all this by working alongside you in the kitchen; in its own time, at its own pace, **through the activities** you do together, and not from the things you say or show.

With a young child, you will often find that the lesson suddenly has to end before you'd completed what you set out to do. This is normal and expected; children have short attention spans. But as long as the child managed to achieve something - however small - and enjoyed doing it, it will have laid down something in the construction of its technical expertise, that can be returned to and built upon next time.
