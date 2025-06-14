# CAVIAR

CAVIAR is a full-stack co-simulation tool for 5G/B5G, allowing all-in-loop software communication with well-known communication
(Wireless Insite, Sionna, ns-3, 5G-Lena), mobility (AirSim, Carla) and AI models (e.g., YOLO). CAVIAR is built in asyncio and NATS

## Installation

### Linux:

Current, CAVIAR is tested in Ubuntu *v22.04*. In the root folder, check the ```install.sh```. It basically install three necessary tools: ```docker```, ```docker-compose``` and ```ffmpeg``` and install the *conda* environment. You must have ```conda``` installed. Please, run in your terminal and in the CAVIAR root folder. @NOTE: we may need your password.

```bash
./install.sh
```

### macOS

*Coming soon...*

### Windows

*Coming soon...*

## System Requirement

* **GPU**: NVIDIA 3060 (*8 Gb of VRAM required*)
* **RAM**: 24 Gb
* **Processor**: i7-12a generation
* **Disk**: 128 Gb 

## Kernel

In this section, we discuss more about the kernel part of the co-simulator, how we monitor variables and persist store them. How we schedule events
in parallel asyncio-based system and the module's life-cycle.

* [Modules](kernel/module.md)
* [Scheduler](kernel/scheduler.md)
* [Monitoring](kernel/monitor.md)


### Orchestrator

As previously mentioned, CAVIAR works with NATS. NATS is a message forwarder that allows such data exchange, segmented in the form of messages. We call it as a "message oriented middleware". NATS has two main different ways of communication: publication and subscription (pub-sub) and request-reply. CAVIAR uses pub-sub to leverage inter-modules communication. In the following sections we discuss how the orchestrator initializes and performs some important functions during the event loop.

#### Initialization

The first thing that any entity in CAVIAR does, is to initialize. The initialization process of the NATS-based orchestrator is basically to deploy the ```nats-server``` function (take a loot at the NATS documentation), grabbing the correct `host` and `port` where to intialize the server. This information can be changed in `kernel/.config/config.json`, in the highlited section shown below:

![Highlited section to change nats port and host](imgs/conifg_kernel.png)

As a side information, the json file also contains a part that defines how logger can be configured. If it should be enabled and the log level (DEBUG, INFO, WARNING, ERROR). The scheduler part of the `config.json` is discussed in scheduler section.

#### Event-loop aware

The orchestrator leaves the functionality of scheduling to the scheduler member. However, the orchestrator must handle functionalities regarding receive, send the message and check it's format.

##### Send

The orchestrator waits until a module call `await NATS.send()`. When this function is called, the NATS-module's member (refer to module's section) is called and wraps this information in a json-based message. I.e., it's serialized in a json-format and send it via publication.

##### Receive

Whenever a module receives a message, NATS-module's member calls, intrisically, a method to check if the received message is correct and aligned with what is expected by the receiver module. This is necessary to avoid bad behaviors in the mdoule's architecture. 

## Blueprints

iN THIS SECTION, we show some standard blueprints and the use of it in different scenarios. This can be helpful to you when create your own blueprint. 

* [BP1 - Search & Rescue (S&R)](blueprints/bp1.md)
* [BP2 - Animal Monitoring](blueprints/bp2.md)
* [BP3 - Indoor Industry (II)](blueprints/bp3.md)
