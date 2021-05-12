#!/usr/bin/env python3

import configparser

c = configparser.ConfigParser()
c.read("setup.cfg")

with open("requirements.txt", "w") as f:
    f.write(c["options"]["install_requires"])
