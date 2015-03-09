---
title: App Engine
layout: default
---

## app engine support

dmangame has support for google app engine built in. this
allows you to run as many games as you want in parallel and
then browse their results through a web UI.

by default, it is configured to run games on [my app engine
instance][0]. it is on the latest (and possibly later) code
from github and contain the latest AI from dmanai/. 

if you you'd like to have your AI run on my app engine
instance, see the instructions on how to submit an AI to
dmanai in the [more AI][1] section.

### running on app engine

use the `-a` or `--app-engine` flag when running `main.py` to
run the game with the specified parameters on the app engine
instance specified in `app.yaml.`

### setting up your own app engine instance

edit `app.yaml` and replace "dmangame-hrd" as the application
name with your own application name. This lets `main.py` know
which URL to post the game parameters to.

#### uploading to app engine:

    python /path/to/google_appengine/appcfg.py update dmangame/


### notes & caveats

#### memory limit

when running on app engine, there is a 200 - 300MB hard limit, so some games may not run if they grow beyond the correct size.

#### code freshness

the code uploaded in the appcfg.py update step is the code
that is being run, so if you modify your AI you need to
re-upload the code.

the typical flow is to work on your AI and test it locally,
and when ready to see results in larger quantities run the
update step.

[0]: http://dmangame-hrd.appspot.com
[1]: more_ais.html



