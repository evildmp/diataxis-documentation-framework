Towards a theory of quality in documentation
===============================================

Diátaxis is an approach to *quality* in documentation.

"Quality" is a word in danger of losing some of its meaning; it's something we
all approve of, but rarely risk trying to describe in any rigorous way. We
want quality in our documentation, but much less often specify what exactly
what we mean by that.

All the same, we can generally point to examples of "high quality
documentation" when asked, and can identify lapses in quality when we see
them - and more than that, we often agree when we do. This suggests that
we still have a useful grasp on the notion of quality.

As we pursue quality in documentation, it helps to make that grasp surer,
by paying some attention to it - here, attempting to refine our grasp by
positing a distinction between **functional quality** and **deep quality**.


Functional quality
------------------

We need documentation to meet standards of *accuracy*, *completeness*,
*consistency*, *usefulness*, *precision* and so on. We can call these
aspects of its **functional quality**. Documentation that fails to meet
any one of them is failing to perform one of its key functions.

These properties of functional quality are all independent of each other.
Documentation can be accurate without being complete. It can be complete, but
inaccurate and inconsistent. It can be accurate, complete, consistent and
also useless.

Attaining functional quality means meeting high, objectively-measurable
standards in multiple independent dimensions, consistently. It requires
discipline and attention to detail, and high levels of technical skill.

To make it harder for the creator of documentation, any failure to meet
all of these standards is readily apparent to the user.


.. _deep-quality:

Deep quality
------------
There are other characteristics, that we can call **deep quality**.

Functional quality is not enough, or even satisfactory on its own as an
ambition. True excellence in documentation implies characteristics of quality
that are not included in accuracy, completeness and so on.

Think of characteristics such as:

* *feeling good to use*
* *having flow*
* *fitting to human needs*
* *being beautiful*
* *anticipating the user*

Unlike the characteristics of functional quality, they cannot be checked or
measured, but they can still be clearly identified. When we encounter them,
we usually (not always, because we need to be capable of it) recognise
them.

They are characteristics of *deep quality*.


What's the difference?
---------------------------------------------------------------

Aspects of deep quality seem to be genuinely distinct in kind from the
characteristics of functional quality.

Documentation can meet all the demands of functional quality, and still fail
to exhibit deep quality. There are many examples of documentation that is
accurate and consistent (and even very useful) but which is also awkward and
unpleasant to use.

It's also noticeable that while characteristics of functional quality such as
completeness and accuracy are **independent** of each other, those of deep
quality are hard to disentangle. *Having flow* and *anticipating the user*
are aspects of each other - they are **interdependent**. It's hard to see how
something could feel good to use without fitting to our needs.

Aspects of functional quality can be measured - literally, with numbers, in
some cases (consider completeness). That's clearly not possible with
qualities such as *having flow*. Instead, such qualities can only be enquired
into, interrogated. Instead of taking **measurements**, we must make
**judgements**.

Functional quality is **objective** - it belongs to the world. Accuracy of
documentation means the extent to which it conforms to the world it’s trying
to describe. Deep quality can’t be ascertained by holding something up to the
world. It’s **subjective**, which means that we can assess it only in the light
of the needs of the subject of experience, the human.

And, deep quality is **conditional** upon functional quality. Documentation
can be accurate and complete and consistent without being truly excellent -
but it will never have deep quality without being accurate and complete and
consistent. No user of documentation will experience it as beautiful, if it's
inaccurate, or enjoy the way it anticipates their needs if it's inconsistent.
The moment we run into such lapses the experience of documentation is
tarnished.

Finally, all of the characteristics of functional quality appear to us, as
documentation creators, as burdens and **constraints**. Each one of them
represents a test or challenge we might fail. Or, even if we have met
one *now*, we can never rest, because the next release or update means that
we'll have to check our work once again, against the thing that it's
documenting. Characteristics such as anticipating needs or flow, on the other
hand, represent **liberation**, the work of creativity or taste. To attain
functional quality in our work, we must *conform* to constraints; to attain
deep quality we must *invent*.

.. list-table::
   :header-rows: 1

   * - Functional quality
     - Deep quality
   * - independent characteristics
     - independent characteristics
   * - objective
     - subjective
   * - measured against the world
     - assessed against the human
   * - a condition of deep quality
     - conditional upon functional quality
   * - aspects of constraint
     - aspects of liberation


How we recognise deep quality
-----------------------------

Consider how we judge the quality of say, clothing. Clothes must have
*functional quality* (they must keep us appropriately warm and dry, stand up
to wear). These things are objectively measurable. You don't really need to
know much about clothes to assess how well they do those this. If water gets
in, or the clothing falls apart - it lacks quality.

There are other characteristics of quality in clothing that can't simply be
measured objectively, and to recognise those characteristics, we need to have
an understanding of clothing. The quality of materials or workmanship isn't
always immediately obvious. Being able to judge that an item of clothing
hangs well, moves well or has been expertly shaped requires developing at
least a basic eye for those things. And these are its characteristics
of *deep quality*.

But: even someone who can't recognise, or fails to understand, those
characteristics - who cannot say *what* they are - can still recognise very
well *that* the clothing is excellent, because they find it that **it feels
good to wear**, because it's such that they want to wear it. No expertise is
required to realise that clothing does or doesn't feel comfortable as you
move in it, that it fits and moves with you well. *Your body knows it*.

And it's the same in documentation. Perhaps you need to be a connoisseur to
recognise *what* it is that makes some documentation excellent, but that's
not necessary to be able to realise *that* it is excellent. Good
documentation **feels good**; you feel pleasure and satisfaction when you use
it - it feels like it fits and moves with you.

The users of our documentation may or may not have the understanding to say
why it's good, or where its quality lapses. They might recognise only the
more obvious aspects of functional quality in it, mistaking those for its
deeper excellence. That doesn't matter - it will feel good, or not, and
that's what is important.

But we, as its creators, need a clear and effective understanding of what
makes documentation good. We need to develop our sense of it so that we
recognise *what* is good about it, as well as *that* it is good. And we need
to develop an understanding of how people will *feel* when they're using it.

Producing work of deep quality depends on our ability to do this.


Diátaxis and quality
--------------------

Functional quality's obligations are met through conscientious observance of
the demands of the craft of documentation. They require solid skill and
knowledge of the technical domain, the ability to gather up a complete
terrain into a single, coherent, consistent map of it.

**Diátaxis cannot address functional quality in documentation.** It is concerned
only with certain aspects of deep quality, some more than others - though if
all the aspects of deep quality are tangled up in each other, then it affects
all of them.


Exposing lapses in functional quality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although Diátaxis cannot address, or *give* us, functional quality, it can
still serve it.

It works very effectively to *expose* lapses in functional quality. It's often
remarked that one effect of applying Diátaxis to existing documentation is
that problems in it suddenly become apparent that were obscured before.

For example: the Diátaxis approach recommends that :ref:`the architecture of
reference documentation should reflect the architecture of the code it
documents <respect-structure>`. This makes gaps in the documentation much
more clearly visible.

Or, moving explanatory verbiage out of a tutorial (in accordance with Diátaxis
demands) often has the effect of highlighting a section where the reader has
been left to work something out for themselves.

But, as far as functional quality goes, Diátaxis principles can have only an
*analytical* role.


Creating deep quality
~~~~~~~~~~~~~~~~~~~~~

In deep quality on the other hand, the Diátaxis approach can do more.

For example, it helps documentation *fit user needs* by describing
documentation modes that are based on them; its categories exist as a
response to needs.

We must pay attention to the correct organisation of these categories then,
and the arrangement of its material and the relationships within them, the
form and language adopted in different parts of documentation - as a way
of fitting to user needs.

Or, in Diátaxis we are directly concerned with *flow*. In flow - whether the
context is documentation or anything else - we experience a movement from one
stage or state to another that seems right, unforced and in sympathy with
both our concerns of the moment, and the way our minds and bodies work in
general.

Diátaxis preserves flow by helping prevent the kind of disruption of rhythm
that occurs when something runs across our purpose and steady progress
towards it (for example when a digression into explanation interrupts a
how-to guide).

And so on.


Understanding the limits
~~~~~~~~~~~~~~~~~~~~~~~~

It's important to understand that Diátaxis can never be *all* that is
required in the pursuit of deep quality.

For example, while it can *help* attain beauty in documentation, at least in
its overall form, it doesn't by itself *make documentation beautiful*.

Diátaxis offers a set of principles - it doesn't offer a formula. It certainly
cannot offer a short-cut to success, bypassing the skills and insights of
disciplines such as user experience or user interaction design, or even
visual design.

Using Diátaxis does not guarantee deep quality. The characteristics of deep
quality are forever being renegotiated, reinterpreted, rediscovered and
reinvented. But what Diátaxis *can* do is lay down some conditions for the
*possibility* of deep quality in documentation.

