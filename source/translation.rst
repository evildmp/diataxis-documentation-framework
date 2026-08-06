Help translate Diátaxis
=======================

If you'd like to help translate Diátaxis into your language, that would be very welcome.

Currently, the only other language available is Polish.

Translation is in progress for various other languages, including French, Italian, Portuguese (Brazil), Chinese (Simplified), Korean and Japanese. Others can be added on request and will be published there when more translations are added.

As soon as a translation is complete, I will publish it on https://diataxis.fr.


Translation guide
-----------------


The best way to contribute to translation is via `Transifex <https://transifex.com>`_, where you'll need an account.


Joining a language team
~~~~~~~~~~~~~~~~~~~~~~~

Go to the `Diátaxis page on Transifex <https://explore.transifex.com/danieleprocida/diataxis/>`_, and select `Join this project <https://app.transifex.com/join/?o=danieleprocida&p=diataxis&t=opensource>`_.

There you'll find the option to join the translation team for the language you're interested in. After that I will receive notification of your join request, and will add you to the team. Your own `Transifex dashboard <https://app.transifex.com/home/>`_ will remain blank until I do.

By all means email me to let me know, because the Transifex notifications don't come in immediately.


Translating
~~~~~~~~~~~~~~~~~~~~~~~

Once you've been added to the team, you'll see an overview of the available languages. You can see all of them, but can only translate the one whose team you're in.

Translation takes place page by page and then string by string - little fragments of the overall text. When you save a translation string, it's marked as translated. I get notifications of these, and periodically I'll pull them down into the repository and publish a new version of the site containing them.


References and file names
..........................

Don't translate names of files or Sphinx references. For example, if you see the string ``:doc:`tutorials` - learning-oriented experiences`` you need to leave ``tutorials`` as it is.

Right now page URLs are *not* being translated, so the French page for *Tutoriels* will be at https://diataxis-translated.readthedocs.io/fr/tutorials/.

That's not very elegant, but at this stage I don't know if there is an alternative.


Placeholders
............

In Transifex you will sometimes see `numbered placeholder symbols <https://help.transifex.com/en/articles/6240403-translating-html-content>`_ for functional Sphinx references. Your translation should include the placeholders too.


Translation practice
~~~~~~~~~~~~~~~~~~~~~~~

Where to start
..............

**The first page to translate** (Transifex calls pages "resources) for a new language should be *Start here*. It should also be the first one to refer to if you're contributing to an existing language.

The reason for that is that it covers the whole of Diátaxis in one page, and gathers together almost all the special terms and forms of words that you will encounter elsewhere. It should be a good guide to translation decisions in general.


What to aim for
...............

I prefer translations to contain good translations for key terms **in their own language**. Even if it's common to use the English term "how-to" in your language, I don't want the translations to do that. They should find a native alternative, and use it consistently.

I care much more about **the meaning and force of the ideas** in Diátaxis than the preservation of the way I have expressed them in English. I certainly don't want or expect literal translation. Translations should be idiomatic and sound unforced. Use native sentence structures and constructions. If better metaphors or turns of phrase exist in your language, use those. I'll be happy to discuss those questions.


Be aware of context
...................

**Take note of the bigger picture.** When you're looking at string by string translations, it's easy to acquire tunnel vision and lose awareness of the context.


Correcting and updating others' translations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I expect that translation will be collaborative work involving multiple translators, not all of whom might agree on how to translate a particular string.

If you see something that's clearly wrong (spelling, grammar, punctuation, lost meaning, unidiomatic rendering) correct it.

If it's more complex, and seems like a stylistic choice or a question of judgement, it would be good to discuss it first. There is a `Transifex forum for this project <https://app.transifex.com/danieleprocida/teams/120528/discussions/>`_, or you can raise the question with me.

-------

Translation contributions are accepted under the `Creative Commons Attribution-ShareAlike 4.0 International Public License <https://github.com/evildmp/diataxis-documentation-framework/blob/main/LICENSE.rst>`_.
