# ELPaaS
ELPaaS(Event Log Privacy as a Service) is a web based tool, that allow users to apply state of the art privacy algorithms from the process mining domain to their event logs. 
The algorithms provided include:

* PRETSA (https://github.com/samadeusfp/PRETSA)
* PRIPEL (https://github.com/samadeusfp/PRIPEL) 
* Process Discovery with Differential Privacy (https://github.com/fmannhardt/pddp)
* Quantifying the Re-identification Risk of Event Logs for Process Mining (https://arxiv.org/abs/2003.10707)

We welcome other researchers to integrate their privacy algorithms for process mining in our tool. If you are interested in doing so please contact us under: Stephan.Fahrenkrog-Petersen || hu-berlin.de

If you use ELPaaS or the source code from it in an academic setting please cite our tool paper:
```
@inproceedings{DBLP:conf/bpm/0006FKMAW19,
  author    = {Martin Bauer and
               Stephan A. Fahrenkrog{-}Petersen and
               Agnes Koschmider and
               Felix Mannhardt and
               Han van der Aa and
               Matthias Weidlich},
  title     = {ELPaaS: Event Log Privacy as a Service},
  booktitle = {Proceedings of the Dissertation Award, Doctoral Consortium, and Demonstration
               Track at {BPM} 2019 co-located with 17th International Conference
               on Business Process Management, {BPM} 2019, Vienna, Austria, September
               1-6, 2019.},
  pages     = {159--163},
  year      = {2019},
  crossref  = {DBLP:conf/bpm/2019d},
  url       = {http://ceur-ws.org/Vol-2420/paperDT9.pdf},
  timestamp = {Fri, 30 Aug 2019 13:15:06 +0200},
  biburl    = {https://dblp.org/rec/bib/conf/bpm/0006FKMAW19},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
The bib code is courtesy of [dblp](https://dblp1.uni-trier.de/rec/bibtex0/conf/bpm/0006FKMAW19).

## Screencast
We show the basic functionality in ELPaaS in the following video:
https://youtu.be/XLq124VpZ6Q

## Test Deployment
We have set-up a test deployment at:
https://elpaas.fmannhardt.de

Note that we may disable the test deployment at any time or limit the rate of requests to prevent server resources from being overloaded.

## Functionality Overview

### PRETSA

PRETSA is an algorithm which ensures t-closeness and k- anonymity.
* PRETSA on GitHub (https://github.com/samadeusfp/PRETSA)

### Laplacian df-based

Query - based algorithm that adds Laplacian noise to event frequencies in the generated directly-follows-grap of the log.

### Laplacian tv-based

Query - based algorithm that adds Laplacian noise to trace-variant frequencies.

### PRIPEL


* PRIPEL on GitHub (https://github.com/samadeusfp/PRIPEL)

### Quantifying Re-identification Risk

* Quantifying the Re-identification Risk of Event Logs for Process Mining (https://arxiv.org/abs/2003.10707)


## Installation & Deployment
You can install ELPaaS in your own environment to avoid sharing your data with a untrusted third party.
Here are installation instructions for:
* [Docker](setup_docker_readme.md)
* [Standard Python](setup_python_readme.md) 

## License
We provide our code, for the web application, under the MIT license. However, this project uses frameworks that are not published under MIT license, like the Microsoft PINQ framework, that we use for differential private queries. Please consider the respective licenses if you want to use this application in a commercial setting.

## Find out more about our research
If you wamt find out more about our research, you can visit the following website: 
https://sites.google.com/view/sfahrenkrog-petersen/start
