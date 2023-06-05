# Robotics 2023 Motherforker-9000

You can run the challenges by running the following command in the terminal:

> python3 motherforker-9000/challenge_1.py

You will need to install the following packages:

- opencv-python 4.7.0.72
- numpy 1.24.3

## Tips & Tricks

This section explains some easy tricks to work on this project

### Find The yetiborg

**MacOs**:

> arp -na | grep -i b8:27:eb

> nmap -v -sn 192.168.1.0/24

**Windows**:

> arp -a

**Linux**:

> {unkown}

### Working on The yetiborg

An easy way to work with the yetiborg is to install [Cyberduck](https://cyberduck.io/). In this way you are able to use vscode on the yetiborg.

### Use python3

alias python=python3

### Control the arm

To control the servor arm with the helper functions make sure that pigpiod is running.
To run it:

> sudo pigpiod
