#!/usr/bin/env python
from pyparam import params

params.a = 1
params.auto = params.a

print(params._complete('zsh', True, withtype = True))