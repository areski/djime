Djime - A Django-based time tracking tool
=========================================

** Update - 30th September 2009 **
After seeing the [Pinax][] project evolve, we have spent some time working
on integrating [Djime][] with [Pinax][] something which can be used as an
intranet. We have codenamed the [Pinax][] [Djime][] combo Pine. Our own focus
is to use Pine rather than using [Djime][] as a stand alone web app. The
result of this re factor of [Djime][] is that we now have two examples, a
basic project and Pine. Since our focus with [Djime][] has been the move the
Pine, the basic project is no longer in a working state. Once we are done
tweaking and testing Pine, we will fix the basic project to also work with the
changes to the internals of [Djime][]. The Pine version is atm. only dependent
on [Pinax][], and a working version is ready now.

[Djime][] is a an open source project. We are working to create a good time
tracking and billing tool using the [Django][] web framework.

The team behind this project is still fairly small, but feel free to join us.

We have:

* a [bug tracker on Github][issues].
* an IRC channel, #djime, on the [Freenode][] network.
* a [Google Groups mailing list][ggroup].

[The source code](http://github.com/djime/djime/tree/master) is also managed on Github.

#### External django apps needed ####

* [django-pagination][], maintained by Eric Florenzano.
* [South][] by Andrew Godwin and Andy McCurdy.

[Django]: http://www.djangoproject.com/ "The Django project"
[Djime]: http://djime.github.com/ "Djime web site"
[South]: http://south.aeracode.org/ "South project homepage"
[Pinax]: http://pinaxproject.com/ "The Pinax project"
[django-pagination]: http://code.google.com/p/django-pagination/ "django-pagination at google code"
[Freenode]: http://freenode.net/
[issues]: http://github.com/djime/djime/issues
[ggroup]: http://groups.google.com/group/djime
