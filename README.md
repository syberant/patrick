# R&D Project 2020-2021, Discord bot assisting in seminars
We will make a Discord bot that helps with the organisation of tutorials via Discord.
It is intended to ease the organisation for teachers and TAs and to streamline the process for students leading to fewer misunderstandings.
This results in much more time that the underfunded education system can put into students, instead of Discord.

TODO

## Installation instructions with pip
First make sure you have installed:
- python (3.8)
- pip

To build and install the package to a local folder named `build` run:
```
$ cd /path/to/r-and-d-discord-bot
$ pip install . -t build
```
For subsequent builds you can use the following:
```
$ pip install . -t build --no-deps -U
```
If you have no qualms about polluting your python path you can leave out the `-t build`.


To execute run:
```bash
$ ./build/bin/r_and_d_discord_bot
```

## Building instructions with Nix
First make sure you have installed a version of Nix with flakes enabled, then use:
- `nix build` to build
- `./result/bin/r_and_d_discord_bot` to execute the built program
- `nix run` to compile and run the program

Take note however that you must first run `git add -A` if there are any new files, otherwise the flake doesn't see them.

## Authors
- Nathalie

## License
Coming soon...
