Metro
=====

Metro is a somewhat complex set of shell and python scripts and various files
used to build install and LiveCD media for Gentoo Linux and its derivatives
(like Funtoo Linux).

TL;DR:

- `Quick Start Tutorial <http://www.funtoo.org/wiki/Metro_Quick_Start_Tutorial>`_
- `Metro AutoSetup <https://www.funtoo.org/Metro_AutoSetup>`_


How Metro Works
---------------

You may be wondering how Metro creates its first stage tarball. As you may have
guessed, Metro cannot create a stage tarball out of thin air. To build a new
stage tarball, Metro must use an existing, older stage tarball called a "seed"
stage. This "seed" stage typically is used as the build environment for
creating the stage we want.

Metro can use two kinds of seed stages. Traditionally, Metro has used a stage3
as a seed stage. This stage3 is then used to build a new stage1, which in turn
is used to build a new stage2, and then a new stage3. This is generally the
most reliable way to build Gentoo Linux or Funtoo Linux, so it's the
recommended approach.

Seeds and Build Isolation
~~~~~~~~~~~~~~~~~~~~~~~~~

Another important concept to mention here is something called *build
isolation*.  Because Metro creates an isolated build environment, and the build
environment is explicitly defined using existing, tangible entities -- a seed
stage and a portage snapshot -- you will get consistent, repeatable results. In
other words, the same seed stage, portage snapshot and build instructions will
generate an essentially identical result, even if you perform the build a month
later on someone else's workstation.

Local Build
~~~~~~~~~~~

Say you wanted to build a new ``pentium4`` stage3 tarball. The recommended
method of doing this would be to grab an existing ``pentium4`` stage3 tarball
to use as your seed stage. Metro will be told to use this existing ``pentium4``
stage3 to build a new stage1 for the same ``pentium4``. For this process, the
generic ``pentium4`` stage3 would provide the *build environment* for creating
our new stage1. Then, the new stage1 would serve as the build environment for
creating the new ``pentium4`` stage2. And the new ``pentium4`` stage2 would
serve as the build environment for creating the new ``pentium4`` stage3.

In the Metro terminology this is called a *local build*, which means a stage3
of a given architecture is used to seed a brand new build of the same
architecture.

A week later, you may want to build a brand new ``pentium4`` stage3 tarball. Rather
than starting from the original ``pentium4`` stage3 again, you'd probably configure
Metro to use the most-recently-built ``pentium4`` stage3 as the seed. Metro has
built-in functionality to make this easy, allowing it to easily find and track
the most recent stage3 seed available.

Remote Build
~~~~~~~~~~~~

Metro can also perform a *remote build*, where a stage3 of a different, but binary
compatible, architecture is used as a seed to build a different architecture
stage3.

Tailored Build
~~~~~~~~~~~~~~

Last, it's also worthy noting that both in local and remote builds, Metro can
be configured to add and/or remove individual packages to the final tarball.
Let's say you can't live without app-misc/screen, at the end of this tutorial,
we will show how to have your tailored stage3 to include it.

Metro Data Model
----------------

The Metro Data Model has been designed to provide you with an optimal way to
organize build data.

Here are the primary goals for the data model:

* Provide useful ways to organize data
* Use mechanisms and syntax that maximize maintainability of the data over
  time
* Reduce and (ideally) eliminate side-effects at every opportunity

To attain these goals, Metro uses a functional data model, where an element
(variable) can be defined only once, and cannot be redefined.

By default, the Metro parser operates in "strict" mode, which means that it
will throw an error if a variable has been referenced that has not been
defined. This "strict" mode is actually very useful in catching errors that
might otherwise go unnoticed and result in broken builds.

In addition, the Metro parser was designed so that the order in which data
elements are defined is not important, even if they reference one another. This
was done to eliminate side-effects related to data ordering, where changing the
order in which things are defined in a file can change the behavior of or break
your code.

First Look
~~~~~~~~~~

Here is some sample Metro data::

  path: /usr/bin

Above, we have defined the element ``path`` to have the value ``/usr/bin``.
``path`` is a single-line element, and the Metro parser takes care of trimming
any trailing whitespace that may be on the line. You can also define
single-line elements that have values that consist of multiple
whitespace-separated values::

  options: ccache replace

Sometimes, you need to define an element but leave it blank. To do this, don't
specify any values after the colon::

  options:

In Metro, the / character is used to delineate various classes of elements, as
follows::

  path/mirror: /home/mirror/funtoo
  path/mirror/snapshot: /home/mirror/funtoo/snapshots
  path/metro: /usr/lib/metro

Above, we see the proper Metro convention for specifying paths. Each path has a
prefix of ``path/``. We have a ``path/mirror`` element but also have a
path/mirror/snapshot element. The ``/`` is used to organize our data into
logical groups. This is not enforced by Metro but is presented here as a best
practice.

The data above could also be represented using a section annotation, as
follows::

  [section path]

  mirror: /home/mirror/funtoo
  mirror/snapshot: /home/mirror/funtoo/snapshots
  metro: /usr/lib/metro

Above, the ``[section path]`` line is a *section annotation*, and it tells the
Metro parser that the ``path/`` prefix should be applied to all following data
elements.  A section annotation is in effect until another section annotation
is encountered by the parser.

While our data above is getting more organized, there is some redundancy in our
data, which generally isn't a good thing. Here's an example of how to make our
data a bit more compact::

  [section path]

  mirror: /home/mirror/funtoo
  mirror/snapshot: $[path/mirror]/snapshots
  metro: /usr/lib/metro

Above, we have used an *element reference* of ``$[path/mirror]`` to reference
our path/mirror element. What this means is that ``path/snapshot`` will have a
value of ``/home/mirror/funtoo/snapshots``.

Also, it's worth pointing out that we could just have well written::

  [section path]

  mirror/snapshot: $[path/mirror]/snapshots
  mirror: /home/mirror/funtoo
  metro: /usr/lib/metro

In other words, it's perfectly OK to use the element reference of
``$[path/mirror]`` on a line before the actual definition of ``path/mirror``.
Metro doesn't care about the order in which data is defined.

Metro provides another way to organize your data in an efficient way. Supposing
that you had a lot of ``path/mirror``-related data, then it might be useful to
organize your data as follows::

  [section path]

  metro: /usr/lib/metro

  [section path/mirror]

  : /home/mirror/funtoo
  snapshot: $[]/snapshot
  source: $[]/$[source/subarch]/funtoo-$[source/subarch]-$[source/version]/$[source/name].tar.bz2

Above, we have used two new parser features. Inside ``[section path/mirror]``,
we can define the ``path/mirror`` element itself by using a blank element name,
followed by a ``:``. The next parser feature we see above is that we can use
``$[]`` to reference the value of the ``path/mirror`` value. ``$[]`` will
always reference the value of the element specified in the section annotation.
Also note that as of Metro 1.1, ``$[:]`` can be used as an alternate form of
``$[]``. In addition, as of Metro 1.2.4, ``$[:foo]`` can be used as an
alternate form of ``$[section-name/foo]``.

Collect Annotations
~~~~~~~~~~~~~~~~~~~

Many scripting languages have the notion of an "include" file, or "importing"
additional data from a remote file. Metro has this concept as well, but it is
implemented in a somewhat different way. You can tell Metro to include data
from another file by using a *collect annotation*.

A collect annotation looks like this::

  [collect $[path/metro]/myfile.txt]

Now, we called these things "collect annotations" for a reason - in Metro, they
work slightly different than most languages implement ``include`` and
``import``. The main difference is that in Metro, a collect annotation does not
happen right away. Instead, Metro will add the file to be collected (in this
case, that would be the file ``/usr/lib/metro/myfile.txt``, or whatever
``$[path/metro]/myfile.txt`` evaluates to) to a collection queue.

This means that Metro will read in the contents of the file at some point in
time, and the data in the file will be available to you by the time the parsing
is complete. But because Metro doesn't care about the order in which data is
defined, it doesn't have the same concept of "read in the data - right now!"
that an include or import statement does in other languages.

Conditional Collect Annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Metro no longer officially supports conditional collect annotations; however,
simple collect annotations can be used to make conditional decisions in Metro,
as follows::

  [collect ./snapshots/$[snapshot/type]]

Above, Metro will collect from a file based on the value of the
``$[snapshot/type]`` element. This allows for varying definitions of elements
to exist dependent on the value of ``$[snapshot/type]``.

Above, Metro will raise an exception if ``$[snapshot/type]`` is undefined or has a
value that does not map to a file on disk. If it is possible that
``$[snapshot/type]`` may not be defined, use the following format::

  [collect ./snapshots/$[snapshot/type:zap]]

Using the ``:zap`` modifier, the entire collect argument will be replaced with
the empty string if ``$[snapshot/type]`` is undefined. If Metro is asked to
collect an empty string, it will not throw an exception. So this is a handy way
to conditionally disable collection of a file. But please note that for all
non-null values of ``$[snapshot/type]``, a corresponding file must exist on
disk in ``./snapshots/`` or Metro will throw an exception. ``:zap`` is
explained in more detail in the "Special Variable Expansion" section, below.

Multi-line elements
~~~~~~~~~~~~~~~~~~~

Metro supports multi-line elements and they are the foundation of Metro's
template engine. A multi-line element can be defined as follows, by using
square brackets to delimit multi-line data::

  myscript: [
  #!/bin/bash
  echo $*
  ]

The terminating closing square bracket should be on a line all by itself.

One of the very useful things about multi-line elements is that they support
Metro element references::

  myscript: [
  #!/bin/bash
  echo Metro's path/metro setting is $[path/metro].
  ]

In the above multi-line element, the ``$[path/metro]`` reference will be expanded
to contain the appropriate value of the element. It is possible to expand
single-line elements inside multi-line elements simply by referencing them
using a dollar sign and square brackets.

Metro also allows you to expand multi-line elements inside other multi-line
elements. Here's an example of how that works::

  myscript: [
  #!/bin/bash
  $[[steps/setup]]
  echo Hi There :)
  ]

