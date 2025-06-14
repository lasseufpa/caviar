# Monitor

### :! flag (--enable-monitor)

CAVIAR enables user to monitor and track messages that are forwarded by the orchestrator.
These messages will be held in a influx-based database. The messages are forwarded using
the influx-dB python API. I.e., whenever a message is received by the orchestrator, it forwards
the current information to the database, as shown in the figure below. This database is simply a 
docker container influx-db image and you can look at (if you didn't change the **compose.yml**) *localhost:8086*.
The beautiful of this feature is that you can simply save a timeline story of your data (a time-series dataset).

![Saving information in influx-dB](../imgs/influx.png)

### @ NOTE:

The user may want to save some information that is not actually being transmited among modules. Some *innie*-module info.
To do that, you can simply use the method *monitor_untracked_info*. Remember that the whole call need to be API by the nats
orchestrator. Moreover, only float values can be storage so if you try to save strings, bytes or some other shit. It will 
probably not work xD.

## Grafana

There is some problems in academy... Sometimes we are just looking for the correct number, correct formula and etc. And when
you find it, wow you keep so happy and try to show to someone that briliant terminal with the correct number and the person
who you are showing it keeps like 'ok, wtf that shit means?'. Then you feel miserable because you lost a bunch of time trying
to research that result. But, hey, you know what are you missing? a dashboard. Yeah, it sounds blah because you listen this whenever 
you are seeing tik tok and then someone pass trying to explain why python is good to create a dashboard and blabla, but seriously
it can increases how you show your results. That's why we added Grafana as a caviar's feature. 

We up Grafana as a service (docker container) and it only takes the enabled information in influx
and allows you to show the results in multiple ways, as you can see in the figure below.

![Grafana S&R-blueprint dashboard](../imgs/grafana.png)

We leave to the user be able to configure the Grafana dashboard as he/she wants. You can read more in Grafana [docs](https://grafana.com/docs/), how
to use it correctly with Influx-dB but basically you must copy the element script in Influx-dB and paste it in grafana and then choose your desired
graph to plot it.