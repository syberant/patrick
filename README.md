# R&D Project 2020-2021, Discord bot assisting in seminars
We will make a Discord bot that helps with the organisation of tutorials via Discord.
It is intended to ease the organisation for teachers and TAs and to streamline the process for students leading to fewer misunderstandings.
This results in much more time that the underfunded education system can put into students, instead of Discord.

TODO

## Installation instructions with pip
First make sure you have installed:
- python (3.8)
- pip

To build and install the package to a local folder named build run:
```
$ cd /home/sybrand/Documents/Radboud_Universiteit_1/r-and-d-discord-bot
$ # Your directory will be in a different place, navigate to it with cd
$ pip install . -t build
Processing /home/sybrand/Documents/Radboud_Universiteit_1/r-and-d-discord-bot
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
    Preparing wheel metadata: started
    Preparing wheel metadata: finished with status 'done'
Collecting discord.py>=1.3.4
  Using cached discord.py-1.7.1-py3-none-any.whl (786 kB)
Collecting aiohttp<3.8.0,>=3.6.0
  Using cached aiohttp-3.7.4.post0-cp38-cp38-manylinux2014_x86_64.whl (1.5 MB)
Collecting chardet<5.0,>=2.0
  Using cached chardet-4.0.0-py2.py3-none-any.whl (178 kB)
Collecting async-timeout<4.0,>=3.0
  Using cached async_timeout-3.0.1-py3-none-any.whl (8.2 kB)
Collecting typing-extensions>=3.6.5
  Using cached typing_extensions-3.7.4.3-py3-none-any.whl (22 kB)
Collecting attrs>=17.3.0
  Using cached attrs-20.3.0-py2.py3-none-any.whl (49 kB)
Collecting yarl<2.0,>=1.0
  Using cached yarl-1.6.3-cp38-cp38-manylinux2014_x86_64.whl (324 kB)
Collecting multidict<7.0,>=4.5
  Using cached multidict-5.1.0-cp38-cp38-manylinux2014_x86_64.whl (159 kB)
Collecting idna>=2.0
  Using cached idna-3.1-py3-none-any.whl (58 kB)
Building wheels for collected packages: r-and-d-discord-bot
  Building wheel for r-and-d-discord-bot (PEP 517): started
  Building wheel for r-and-d-discord-bot (PEP 517): finished with status 'done'
  Created wheel for r-and-d-discord-bot: filename=r_and_d_discord_bot-0.0.0-py3-none-any.whl size=2290 sha256=cc02c01fe718c3618ece5fcd2db84618202f25cdfa92115db2799bc5043732be
  Stored in directory: /home/sybrand/.cache/pip/wheels/9c/3f/af/8e5158c98cae9ee08bb588920b8a0543e255d5709a3722da18
Successfully built r-and-d-discord-bot
Installing collected packages: multidict, idna, yarl, typing-extensions, chardet, attrs, async-timeout, aiohttp, discord.py, r-and-d-discord-bot
Successfully installed aiohttp-3.7.4.post0 async-timeout-3.0.1 attrs-20.3.0 chardet-4.0.0 discord.py-1.7.1 idna-3.1 multidict-5.1.0 r-and-d-discord-bot-0.0.0 typing-extensions-3.7.4.3 yarl-1.6.3
```
For subsequent builds you can use the following:
```
$ pip install . -t build --no-deps -U
Processing /home/sybrand/Documents/Radboud_Universiteit_1/r-and-d-discord-bot
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
    Preparing wheel metadata: started
    Preparing wheel metadata: finished with status 'done'
Building wheels for collected packages: r-and-d-discord-bot
  Building wheel for r-and-d-discord-bot (PEP 517): started
  Building wheel for r-and-d-discord-bot (PEP 517): finished with status 'done'
  Created wheel for r-and-d-discord-bot: filename=r_and_d_discord_bot-0.0.0-py3-none-any.whl size=3223 sha256=ce64c0fd6eae55bf8191707995529bb5d51ac617c425d61cb23dd996a01c342b
  Stored in directory: /home/sybrand/.cache/pip/wheels/9c/3f/af/8e5158c98cae9ee08bb588920b8a0543e255d5709a3722da18
Successfully built r-and-d-discord-bot
Installing collected packages: r-and-d-discord-bot
Successfully installed r-and-d-discord-bot-0.0.0
```
If you have no qualms about polluting your python path you can leave out the `-t build`.


To execute run:
```bash
$ ./build/bin/r_and_d_discord_bot
```

## Building instructions with nix
First make sure you have installed a version of Nix with flakes enabled, then use:
- `nix build` to build
- `./result/bin/r_and_d_discord_bot` to execute the built program
- `nix run` to compile and run the program

Take note however that you must first run `git add -A` if there are any new files, otherwise the flake doesn't see them.

## License
Coming soon...
