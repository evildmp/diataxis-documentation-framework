.. _complex-documentation:

Diátaxis in complex hierarchies
==================================

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
    :emphasize-lines: 6-15

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
--------------------

Lists longer than a few items are very hard for humans to read, unless they
have an inherent mechanical order - numerical, or alphabetical. Seven items
seems to be a comfortable general limit. If you find that you're looking at
lists longer than that in your tables of contents, you need to find a way to
break them up into small ones.

Once again, what matters here most is not the integrity of whatever scheme
you're working with, but the experience of the reader. Diátaxis works because
it fits user needs well - if your execution of Diátaxis leads you to formats
that seem uncomfortable or ugly, then you need to use it differently.

Overviews and introductory text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The content of a landing page itself should read like an overview - *it should
not simply present lists of other content*. Remember that you are always
authoring for a human user, not fulfilling the demands of a scheme.

Headings and snippets of introductory text catch the eye and provide context.

For example, a **how-to landing page**:

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




