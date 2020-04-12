<h1 align="center">
  A . L . I . C . E .
  <br>
</h1>

<h4 align="center">A Logically Interacting Computing Entity</h4><br>

<p align="center">
  <a href="#introduction">Introduction</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#project">Project</a> •
  <a href="#pipeline">Pipeline</a> •
  <a href="#version-history">Version History</a> •
  <a href="#contribution">Contribution</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>


## Introduction
Hello World! <br>
A . L . I . C . E  - (Alice) is an open source AI project who can respond to the user's thoughts, try to solve problems and automate daily tasks if needed. Over the course of her existence as an AI project, using the potential of Deep Learning, Computer Vision and Natural Language Processing she would become "human-like" in her personality and should eventually gain a more natural way of speaking, an improved sense of humor, cognitive and smart predictive skills.
The project will be built in several chunks and I would update the README document as and when I develop or modify OR update certain bits. Alice aims to focus on conversational aspect (chatbot) more as of now.

## Getting Started

Alice is an ongoing project written in [Python](https://www.python.org/downloads/). Alice runs locally on system and uses Python console (currently) as her current interface to communicate with the user. It would potentially change as the project progresses in future.

The code should ideally provide support for both Mac OS and Windows, however the code will works on Windows 10 without any issues as it was natively written on it.
* [Prerequisites](#prerequisites)
* [Steps to follow](#steps-to-follow)
	 * ### Prerequisites
          *  Make sure you are on minimum Python 3.6.x + version.
	      *  Check if you have TensorFlow installed minimum v1.4.0.
          *  TensorFlow's GPU version works significantly faster than it's CPU counterpart. So if you have a decent GPU (min. Nvidia 1050Ti) to spare install TensorFlow-GPU for python using the `pip install tensorflow-gpu==1.5.0` command.

	 * ### Steps to follow
	      * Run "setup.py" file. This makes sure that the directory structure is in place as required. It is always better to run code from command line.
          * Navigate in correct directory.
          ```shell
          Z:\alice>cd utils
          ```
          * Once you are in the required directory, run <b>parser.py</b> file.
          ```shell
          Z:\alice\utils>py parser.py
          ```

## Pipeline

Pipeline shows the scope of the project
* [Planned Features](#planned-features)
* [Known Issues](#known-issues)
	 * ### Planned Features
        * Adding support for voice input-output ✅
        * GUI support.
        * Integrating [FaceID](https://github.com/xames3/faceid/) module.
        * Support for automation using voice command.
	    * Integrating Twitter streaming module.

	 * ### Known Issues
        * Cannot train the multiple training files (.bz2 files) ✅

## Discontinued!

## Version History

* [Latest Build](#latest-build)
* [Experimental Build](#experimental-build)
	 * ### Latest Build
		* v1.2.4.20190318

	 * ### Experimental Build
		* 1.2.4.20190318 - beta<br>
        Under `./sandbox/` directory.

## Contribution
Feel free to send pull requests and raise issues.
* Feel free to contribute to the project by mirroring another branch with distinct name so as to avoid confusions.
* Stick to minimal and simplistic approach of coding using comments wherever necessary.
* All Machine Learning approaches are welcomed.

## Credits
* [Sentdex](https://github.com/sentdex)
* [TensorFlow](https://github.com/tensorflow/)

## License
A . L . I . C . E . is an open source project licensed under GNU GPL v3.0.
