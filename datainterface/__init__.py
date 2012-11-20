#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Load data from raw datasets into the datastructure objects.

These modules are used to load raw dataset files into objects defined in the
datastructure package.

The spinn3r module successively uses the nltktools and xmlparsing modules.
The memetracker module is pretty standalone (but uses the datastructure
package). The timeparsing and picklesaver modules are utilities that are used
everywhere throughout the code.

Modules:
  * aoatools: load data from the Age-of-Acquisition dataset
  * memetracker: load data from the MemeTracker dataset
  * freeassociation: load data from FreeAssociation dataset
  * nltktools: interface NLTK objects and dataset objects
  * picklesaver: save or load any data in pickle format
  * redistools: wrappers for Redis data access
             Reader
  * timeparsing: parse and convert strings representing dates and times

"""
