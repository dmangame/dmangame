---
layout: post
title: how safe is it to run remote code?
author: okay
---

#### tldr:

somewhat safer, now.

use the `-s` or `--safe-mode` flag when running remote AI to run the
game with more restrictions. do it. it'll keep you safe.

#### the long of it:

one really cool feature of dmangame is that it has support for
loading AI off github, allowing for AIs to play against each other
from any repository.  unfortunately, this also means that if you run
an AI from someone else's repository, you are about to run untrusted
code.

i am happy with running untrusted code on app engine, because they
are google's machines.  i am less okay with running untrusted code on
my own machine. For example: `import os; os.system("rm -rf /")` is
all that is needed to bring down my computer by a rogue AI.

according to the python wiki, [sandboxing python][0] is notoriously
hard and difficult.  so, i've been keeping an eye out for how other
projects are sandboxing python.

two interesting projects i've seen that sandbox python are [zope][1]
and [hackiki][2]. they take different approaches: zope creates a very
limited subset of python features that can be used and drops the
interpreter into a lower state of trust, while hackicki creates
chroot jails for running the python in.

they both looked to have high setup costs, though, so i actually
decided to try out [tav's safelite][3] mechanism. safelite went
around the python mailing lists in 2009 and through a day of
iteration, led to a stripped down python.  unfortunately, due to the
way the game works, f_locals has to remain exposed in stack frames in
order to verify that AIs are only accessing allowed variables.

#### conclusion:

it's still being tested, so for now, use the `--safe-mode` or `-s`
option to run AI's in safe mode. It will prompt you whenever an
untrusted module is loaded - try not to allow AIs loading `sys` or
`os` and if your AI depends on either of those, consider removing
them as dependencies. once the kinks are worked out in the future,
games will run in safe mode by default.

[0]: http://wiki.python.org/moin/SandboxedPython
[1]: http://svn.zope.org/zope.security/trunk/src/zope/security/untrustedinterpreter.txt?rev=75174&view=markup
[2]: http://hackiki.org/wiki/
[3]: http://tav.espians.com/a-challenge-to-break-python-security.html
