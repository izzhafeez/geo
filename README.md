# Geo

[![Upload Python Package](https://github.com/mynameizzhafeez/geo/actions/workflows/python-publish.yml/badge.svg?event=push)](https://github.com/mynameizzhafeez/geo/actions/workflows/python-publish.yml)

Geo is a geospatial management tool for Python. It facilitates the creation of Location objects, and acts as a model for Singapore's urban environment.

During my National Service, I was involved in the DRO project, a piece of software used to optimise the placement of ambulances in Singapore. In addition, I further worked with medical, fire alarm and MyResponder data. This started my journey into Geospatial Analytics.

After concluding my service, I began exploring different aspects of Singapore's urban geography; I used BeautifulSoup and Selenium to extract data pertaining to Malls, Schools, Services, Transportation, Shops and the like. I further extracted and processed datasets from LTA, URA and GovTech, which I explored using tools such as Tableau and QGis. This eventually led me to creating my MALLS Card Game, utilising as much of the data collected as possible to produce a strategic card game.

This Python package details some of the ways I have managed this data, and applied programming principles learned from my Computer Science modules. Through this project, I hope to display strong concepts in Object Oriented Progamming, Generics, Immutability and Tree Data Structures.

[Link to website post about the project](https://www.izzhafeez.com/#/works/projects/geospatial-management)

## Geometry

The "geom" submodule contains classes representing different aspects of a location in Singapore, including points, lines and shapes. It also includes a dynamic distance calculator as well as one for elevation.

## Structures

The "structures" submodule contains data structures to facilitate certain operations. In it, I have implemented many data structures learned from my modules, such as the AVLTree, KDTree, Priority Queue and the Median Finding Algorithm. But I've also implemented my own Bounds Tree, which stores multiple shapes.

## Locations

Using the two submodules mentioned previously, the "locations" submodule contains objects representing locations in Singapore. Be it MRT, Bus, Land Lots, Malls, Planning Areas, Roads or Schools, the objects have been optimised to handle queries much more quickly. The objects facilitate filtering, mapping, sorting, grouping, regex searching, distance querying, iterating and many more.
