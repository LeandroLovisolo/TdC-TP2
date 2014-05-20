TdC-TP2
=======

Teoría de las Comunicaciones: Trabajo Práctico 2

1° Cuatrimestre 2014

Departamento de Computación,  
Facultad de Ciencias Exactas y Naturales,  
Universidad de Buenos Aires.

Alumnos
-------

Nahuel Delgado (LU 601/11) [nahueldelgado@gmail.com](mailto:nahueldelgado@gmail.com)  
Leandro Lovisolo (LU 645/11) [leandro@leandro.me](mailto:leandro@leandro.me)  
Lautaro José Petaccio  (LU 443/11) [lausuper@gmail.com](mailto:lausuper@gmail.com)

Requerimientos
--------------

Se requieren las siguientes bibliotecas Python versión 2.x:

- scapy
- pygeoip
- matplotlib
- basemap

Para instalar dichas dependencias en Arch Linux, basta con ejecutar los siguientes comandos como usuario root:

`pacman -S python2-pip python2-pygeoip python2-matplotlib python2-basemap`

`pip2 install scapy`

Luego de instalar las bibliotecas Python es necesario bajar la base de datos de geolocación [Maxmind GeoLite City](http://dev.maxmind.com/geoip/legacy/geolite/), para lo que se provee un objetivo en el Makefile:

`make download-geolocation-db`

Uso
---

El script central es `traceroute`.

Como ejemplo de uso, para hacer un traceroute a `www.google.com`, ejecutar lo siguiente como usuario root:

`./traceroute www.google.com`

El script imprime IPs, ubicación geográfica (cuando es posible), RTTs y ZRTTs para cada hop.
