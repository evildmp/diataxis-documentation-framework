.. _complex-documentation:

Diátaxis in complex hierarchies
==================================

.. _basic-structure:

The basics
----------

The application of Diátaxis to most documentation is fairly straightforward.
The product that defines the domain of concern has clear boundaries, and it's
possible to come up with a simple arrangement of its contents according to
the principles, for example:

.. code-block:: text

    home                      <- landing page
        tutorial              <- landing page
            part 1
            part 2
            part 3
        how-to guides         <- landing page
            install
            deploy
            scale
        reference             <- landing page
            commandline tool
            available endpoints
            API
        explanation           <- landing page
            best practice recommendations
            security overview
            performance

In each case, a landing page contains an overview of the contents within. The
tutorial for example describes what the tutorial has to offer, providing
context for it.

Adding a layer of hierarchy
---------------------------

Even very large documentation sets can use this effectively, though after a
while some grouping of pages withing sections might be wise. This can be done
by adding another layer of hierarchy - for example to be able to address
different installation options separately:

..  code-block:: text
    :emphasize-lines: 8-11

    home                      <- landing page
        tutorial
            part 1
            part 2
            part 3
        how-to guides         <- landing page
            install           <- landing page
                locally
                Docker
                virtual machine
                Linux container
            deploy
            scale
        reference             <- landing page
            commandline tool
            available endpoints
            API
        explanation           <- landing page
            best practice recommendations
            security overview
            performance

Once again, each level of the hierarchy in a section has an overview landing
page, for orientation.


The problem of lists
~~~~~~~~~~~~~~~~~~~~

Lists longer than a few items are very hard for humans to read, unless they
have an inherent mechanical order - numerical, or alphabetical. *Seven items
seems to be a comfortable general limit.* If you find that you're looking at
lists longer than that in your tables of contents, you need to find a way to
break them up into small ones.

Once again, what matters here most is not the integrity of whatever scheme
you're working with, but **the experience of the reader**. Diátaxis works
because it fits user needs well - if your execution of Diátaxis leads you to
formats that seem uncomfortable or ugly, then you need to use it
differently.

Overviews and introductory text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**The content of a landing page itself should read like an overview.**

That is, it should not simply present lists of other content, it should
introduce them. *Remember that you are always authoring for a human user, not
fulfilling the demands of a scheme.*

Headings and snippets of introductory text catch the eye and provide context;
for example, a **how-to landing page**:

..  code-block:: text

    How to guides
    =============

    Lorem ipsum dolor sit amet, consectetur adipiscing elit.

    Installation guides
    -------------------

    Pellentesque malesuada, ipsum ac mollis pellentesque, risus nunc ornare
    odio, et imperdiet dui mi et dui. Phasellus vel porta turpis. In feugiat
    ultricies ipsum.

    * locally                  |
    * Docker                   |  links to
    * Virtual machines         |  the guides
    * Linux containers         |

    Deployment and scaling
    -----------------------

    Morbi sed scelerisque ligula. In dictum lacus quis felis facilisis
    vulputate. Quisque lacinia condimentum ipsum laoreet tempus.

    * Deploy an instance       |  links to
    * Scale your application   |  the guides


Two-dimensional problems
------------------------

A more difficult problem is when the structure outlined by Diátaxis meets
another structure - often, a structure of topic areas within the
documentation, or when documentation encounters very different user-types.

For example we might have a product that is used on land, sea and air, and
though the same product, is used quite differently in each case. And it could
be that a user who uses it on land is very unlikely to use it at sea.

Or, the product documentation addresses the needs of:

* users
* developers who build other products around it
* the contributors who help maintain it.

The same product, but very different concerns.

A final example: a product that can be deployed on different public clouds,
with each public cloud presenting quite different workflows, commands, APIs,
GUIs, constraints and so on. Even though it's the same product, as far as the
users in each case are concerned, what they need to know and do is very
different - what they need is documentation not for *product*,
but

* *product-on-public-cloud-one*
* *product-on-public-cloud-two*
* and so on...

So, we *could* decide on an overall structure that does this:

.. code-block:: text

    tutorial
        for users on land
            [...]
        for users at sea
            [...]
        for users in the air
            [...]
    [and then so on for how-to guides, reference and explanation]

or maybe instead this:

.. code-block:: text

    for users on land
        tutorial
            [...]
        how-to guides
            [...]
        reference
            [...]
        explanation
            [...]
    for users at sea
        [tutorial, how-to, reference, explanation sections]
    for users in the air
        [tutorial, how-to, reference, explanation sections]

Which is better? There seems to be a lot of repetition in either cases. What
about the material that can be shared between land, sea and air?


What *is* the problem?
~~~~~~~~~~~~~~~~~~~~~~

Firstly, the problem is in no way limited to Diátaxis - there would be the
difficulty of managing documentation in any case. However, Diátaxis certainly
helps reveal the problem, as it does in many cases. It brings it into focus
and demands that it be addressed.

Secondly, the question highlights a common misunderstanding. Diátaxis is not a
scheme into which documentation must be placed - four boxes. It posits four
different kinds of documentation, around which documentation should be
structured, but this does not mean that there must be simply four divisions
of documentation in the hierarchy, one for each of those categories.


Diátaxis as an approach
------------------------------------------

:ref:`Diátaxis can be neatly represented in a diagram <map>` - but it is not
the *same* as that diagram.

It should be understood as an approach, a way of working with documentation,
that identifies four different needs and uses them to author and structure
documentation effectively.

This will *tend* towards a clear, explicit, structural division into the four
categories - but that is a typical outcome of the good practice, not its
end.


User-first thinking
------------------------------------------

**Diátaxis is underpinned by attention to user needs**, and once again it's that
concern that must direct us.

What we must document is the product *as it is for the user*, the product as
it is in their hands and minds. (Sadly for the creators of products, how they
conceive them is much less relevant.)

Is the product on land, sea and air effectively three different products,
perhaps for three different users?

In that case, let that be the starting point for thinking about it.

If the documentation needs to meet the needs of users, developers and
contributors, how do *they* see the product? Should we assume that a
developer who incorporates it into other products will typically need a good
understanding of how it's used, and that a contributor needs to know what
a developer knows too?

Then perhaps it makes sense to be freer with the structure, in some parts
(say, the tutorial) allowing the developer-facing content to follow on from
the user-facing material, while completely separating the contributors' how-to
guides from both.

And so on. If the structure is not :ref:`the simple, uncomplicated structure we
began with <basic-structure>`, that's not a problem - as long as there *is*
arrangement according to Diátaxis principles, that documentation does not
muddle up its different forms and purposes.


Let documentation be complex if necessary
------------------------------------------

Documentation should be as complex as it needs to be, and it will sometimes
have complex structures. But even complex structures can be made
straightforward to navigate as long as they are logical and incorporate
patterns that fit the needs of users.
