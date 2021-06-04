# R&D Project 2020-2021, Discord bot assisting in seminars
We have made a Discord bot (called patrick) that helps with the organisation of tutorials via Discord.
It is intended to ease the organisation for teachers and TAs and to streamline the process for students leading to fewer misunderstandings.
This results in much more time that the underfunded education system can put into students, instead of Discord.

## Installation instructions with Docker

First you need the Docker image: either download from a [release](https://github.com/syberant/r-and-d-discord-bot/releases) or build it yourself with `nix build github:syberant/patrick#docker` if you have installed Nix with Flakes enabled (see below).

Then you need to load it into docker. Assuming the image file is called `image`:
```
$ docker load < image
b2d5eeeaba3a: Loading layer [==================================================>]   5.88MB/5.88MB
8d3a731fe204: Loading layer [==================================================>]  119.4MB/119.4MB
Loaded image: patrick:f7lh0dwp45637f5hsf7nky2f2di3srx4
```
But this Docker image does not know the needed token to authenticate itself to Discord. Let's fix that by creating a new docker image:
```
FROM patrick:f7lh0dwp45637f5hsf7nky2f2di3srx4
ENV DISCORD_BOT_TOKEN="your_token_here_obviously"
```
Store that as `Dockerfile` and build it (we named it `patrickenv` here but you may use another name):
```
$ docker build -t patrickenv .
Sending build context to Docker daemon  14.46MB
Step 1/2 : FROM patrick:f7lh0dwp45637f5hsf7nky2f2di3srx4
 ---> 5bb8bb364779
Step 2/2 : ENV DISCORD_BOT_TOKEN="your_token_here_obviously"
 ---> Running in 59bb7913fae1
Removing intermediate container 59bb7913fae1
 ---> 6c59f1d33eee
Successfully built 6c59f1d33eee
Successfully tagged patrickenv:latest
```
You can now run the bot with:
```
$ docker run -t patrickenv:latest
```

## Installation instructions with pip
First make sure you have installed:
- python (3.8)
- pip

To build and install the package to a local folder named `build` run:
```
$ cd /path/to/patrick
$ pip install . -t build
```
For subsequent builds you can use the following:
```
$ pip install . -t build --no-deps -U
```
If you have no qualms about polluting your python path you can leave out the `-t build`.

To execute, run:
```bash
$ ./build/bin/patrick
```

## Installation instructions with Nix
If you have installed [Nix](https://nixos.org/) with flake support you could also run `nix run github:syberant/patrick`.
This will install and download all dependencies and run the program.
To just build the program run `nix build github:syberant/patrick`, this will create a `result` symlink with the executable. `./result/bin/patrick` will then run the program.

## Usage instructions

To run the bot, you must follow the following steps.

### Create a Discord server

First, you have to create a Discord server.
This can be done from the Discord application.
In this server, you must create:
- A channel named `#admin`. This channel is used for issuing commands to the bot. If you want to restrict non-admins from issuing commands, make sure the `#admin` channel is only accessible to the admin users.
- A role named `TA`, which the bot needs to distinguish TAs and students.

### Create a Discord bot

Have a look at the [discordpy documentation](https://discordpy.readthedocs.io/en/stable/discord.html).
You are unlikely to want others to be able to invite your bot, as such you should probably leave "Public Bot" unchecked.
Do make sure you check the "Server Members Intent" option.
Copy the token as you will need it in the next step.

### Running the bot

The instructions for running the bot are written above.
You can pick any method you fancy to install and run the bot.
If you use the pip or Nix method, you must set the `DISCORD_BOT_TOKEN` environment variable to the token you copied in the previous step when you run the bot.
For Nix, for example, you must use:
```bash
$ DISCORD_BOT_TOKEN=your_token_here nix run github:syberant/patrick
```

### Inviting the bot into your server

Go to the OAuth page and check "bot" under the scopes setting.
Then make sure you give the bot the following permissions:
- Manage Roles
- Manage Channels
- View Channels
- Send Messages
- Manage Messages
- Add Reactions

Open the resulting URL in a new tab and invite the bot to your server.

### Retrieving Brightspace information

In order to retrieve and send announcements from Brightspace to your server, the bot needs the URL of the Announcements page and an active Brightspace session.
The `>configure_announcements` command needs to receive the following parameters: `url`, `d2lSessionVal`, `d2lSecureSessionVal`, and the channel in which to send the announcements, in that order, separated by one or more spaces.
To retrieve these, you must go to the ‘Course Home’ of the desired course in your browser.
Then, you must click the ‘Announcements’ link.
For the `url` parameter, use the URL of the page you are now visiting in you browser.
For the `d2lSessionVal` and `d2lSecureSessionVal` cookies, open ‘Inspect element’ and go to the ‘Network’ tab (this is the name in Firefox and Chromium; other browsers might use a different name).
You probably need to reload the page for the necessary information to be visible.
Now, select the very first request and open the ‘Headers’ tab (probably on the right).
Look for the ‘Cookie’ header, and find the values of `d2lSessionVal` and `d2lSecureSessionVal` there.

When you send the command, the given parameters are stored and the bot will send new Brightspace announcements every five minutes, if there are any new announcements.

## Authors
- Nathalie
- Splinter
- Mike
- Sybrand

## License
GNU General Public License v3 (GPLv3)

