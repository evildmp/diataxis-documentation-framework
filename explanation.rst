.. _explanation:

Explanation
=================

Explanation, or discussions, *clarify and illuminate a particular topic*. They broaden the documentation’s coverage of a topic.

They are **understanding-oriented**.

Explanations can equally well be described as *discussions*; they are discursive in nature. They are a chance for the documentation to relax and step back from the software, taking a wider view, illuminating it from a higher level or even from different perspectives. You might imagine a discussion document being read at leisure, rather than over the code.

This section of documentation is rarely explicitly created, and instead, snippets of explanation are scattered amongst other sections. Sometimes, the section exists, but has a name such as *Background* or *Other notes* or *Key topics* - these names are not always useful.

Discussions are less easy to create than it might seem - things that are straightforward to explain when you have the starting-point of someone’s question are less easy when you have a blank page and and have to write down something about it.

A topic isn’t defined by a specific task you want to achieve, like a how-to guide, or what you want the user to learn, like a tutorial. It’s not defined by a piece of the machinery, like reference material. It’s defined by what **you** think is a reasonable area to try to cover at one time, so the division of topics for discussion can sometimes be a little arbitrary.

Analogy from cooking
--------------------

.. image:: /images/mcgee.jpg
   :alt: 'a child cooking'
   :align: right
   :width: 379

Think about a work that discusses food and cooking in the context of history, science and technology. It's *about*
cooking and the kitchen.

It doesn't teach, it's not a collection of recipes, and it doesn't just describe.

Instead, it analyses, considers things from multiple perspectives. It might explain why it is we now do things the way we do, or
even describe bad ways of doing things, or obscure alternatives.

It deepens our knowledge and makes it richer, even if it isn't knowledge we can actually apply in any practical sense - but it doesn't need to be, in order to be valuable.

It's something we might read at our leisure, away from the kitchen itself, when we want
to think about cooking at a higher level, and to understand more about the subject.


How to write good explanation
----------------------------------

Provide context
~~~~~~~~~~~~~~~

**Explanations are the place for background and context** - for example, *Web forms and how they are handled in Django*, or *Search in django CMS*.

They can also explain *why* things are so - design decisions, historical reasons, technical constraints.


Discuss alternatives and opinions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Explanation can consider alternatives**, or multiple different approaches to the same question. For example, in an article on Django deployment, it would be appropriate to consider and evaluate different web server options,

Discussions can even consider and weigh up contrary *opinions* - for example, whether test modules should be in a package directory, or not.


Don't instruct, or provide technical reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Eplanation should do things that the other parts of the documentation do not.** It’s not the place of an explanation to instruct the user in how to do something. Nor should it provide technical descriptions. These functions of documentation are already taken care of in other sections.
