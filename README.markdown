# GPSD-sizzle

WARNING: Any files at GitLab, GitHub, or other providers are not official release files. The releases only occur at PyPI, similar to GPSD releasing only at Savannah.

## General

This package is a Fork of GPSDs' 'gps' python package for installs not blessed by GPSD. It includes some clients interacting with gpsd.

## Clients

* gpscat(1) - dump the output from a GPS
* gpscsv(1) - convert gpsd JSON sentences to CSV files
* gpsfake(1) - test gpsd by simulating a sensor
* gpsplot(1) - form scatterplots and stripcharts of gpsd data
* gpsprof(1) - staticaly plot fixes, skyview, fic latency or other data
* gpssubframe(1) - read and decode gpsd JSON subframe data
* ntpshmviz(1) - plot NTP SHM segments reported clock offset
* ubxtool(1) - communicate with u-blox gps and parse return
* xgpsspeed)(1) - graphically show speed and skyview using GTK
* xgps(1) - graphically show much data about configured sensors ala cgps
* zerk(1) - interface with Javad GPS using GREIS

## untested clients

* gpsData(1) - dump GPS data
* gpssim(1) - a test GPS simulator
* skyview2svg(1) - create an SVG image of GPS satellites sky view
* webgps(1) - create a skyview of the currently visible GPS satellites with tracks

## Buyer beware

* gpscat -[pt] and gpsfake are broken because I am not including the upstream gps.packet and libgpspacket.
* gpsfake requires an external gpsd on the same machine
* gpsplot requires external GNU Plot.
* ntpshmviz only supports 2 sample channels and require matplotlib IIRC.
* webgps only makes sense with an external web server and browser.
* ubxtool and zerk require the serial package to directly talk to GPS devices/logfiles and an external gpsd to do so indirectly.
* xgps and xgpsspeed require pycairo, python bindings to GObject introspection and GObject binding for GTK and Cairo 


## Resources and Support

There are none; deal with it. In particular, DON'T clog the GPSD community support asking for help with this.

## Credit
The members of the GPSD community who have worked so hard on the clients, libgpspacket, and the gps package.

## LICENSE

This parent software (The clients and gps package of GPSD) is released under the terms and conditions of the BSD-2-Clause License, including a copy in the file COPYING.

The parent software and its bits are Copyrighted by the GPSD project.

All changed to the code since are under the BSD-2-Clause License as well.
