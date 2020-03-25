.. raw:: html

    <style>
        table.docutils { width: 100%; table-layout: fixed;}
        table.docutils th, table.docutils td { white-space: normal }
    </style>


Introduction
============

The problem and the solution
------------------------------

The problem it solves
~~~~~~~~~~~~~~~~~~~~~

It doesn’t matter how good your product is, because **if its documentation is not good enough, people will not use it**. Even if  they have to use it because they have no choice, without good documentation, they won’t use it effectively or the way
you’d like them to.

Nearly everyone understands this. Nearly everyone knows that that they need good documentation, and **most people try to create good documentation**. And **most people fail**.

Usually, it’s not because they don’t try hard enough. Usually, it’s because they are not doing it the right way.

This system is a way to make your documentation better, not by working harder at it, but by doing it the right way. **The right way is the easier way** - easier to write, and easier to maintain.


The 'secret'
~~~~~~~~~~~~

It's not really a secret: documentation needs to include and be structured around its **four different functions**: *tutorials*, *how-to guides*, *technical reference* and *explanation*. Each of them **requires a distinct mode of writing**. People working with software need these four different kinds of documentation at different times, in different circumstances - so software usually needs them all.

And documentation needs to be explicitly structured around them, and they all must be kept separate and distinct from each other.

.. list-table::
   :widths: 16 21 21 21 21
   :header-rows: 1

   * - \
     - Tutorials
     - How-to guides
     - Reference
     - Explanation
   * - *oriented to*
     - learning
     - a goal
     - information
     - understanding
   * - *must*
     - allow the newcomer to get started
     - show how to solve a specific problem
     - describe the machinery
     - explain
   * - *its form*
     - a lesson
     - a series of steps
     - dry description
     - discursive explanation
   * - *analogy*
     - teaching a small child how to cook
     - a recipe in a cookery book
     - a reference encyclopaedia article
     - an article on culinary social history

This division makes it obvious to both author and reader what information goes where. It tells the author how to write, and what to write, and where to write it. It saves the author from wasting a great deal of time trying to wrestle the information they want to impart into a shape that makes sense, because **each of these kinds of documentation has only one job**.

In fact, it’s extremely hard to maintain good documentation that doesn’t implicitly or explicitly recognise the quadrants of this scheme. The demands of each kind are different from those of the others, so **any attempt at documentation that fails to maintain this structure suffers**, as it’s pulled in different directions at once.

Once you understand the structure, it becomes a very useful tool for analysing existing documentation, and understanding what needs to be done to improve it.


What about project (rather than product) documentation?
-------------------------------------------------------

You may well ask: where do things like changelogs, contribution policies, and other information about the project fit into this scheme? The answer is that they do not - because they are, strictly speaking, project documentation rather than documentation of the producr itself,

They can simply be kept in appropriately-named sections alongside the other material - as long as they are not mixed up *in* it.

With that in mind, let's explore each of the four key functions.