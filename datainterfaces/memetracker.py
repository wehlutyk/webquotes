#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Structures and methods to deal with the MemeTracker dataset
See http://memetracker.org/ for details about it
'''


# Imports
from __future__ import division
from codecs import open as c_open
import re
import os


# Module code
class MT_dataset(object):
    def __init__(self, mt_filename):
        self.mt_filename = mt_filename
        self.rootfolder = os.path.split(mt_filename)[0]
        self.n_skip = 6
        self.n_lines = 8357595 # or count them self.count_lines(mt_filename)
        self.lineinfostep = self.n_lines//20
    
    def print_quotes_freq(self):
        '''
        Reads the clusters file and prints out in another file what quotes are present, along with their frequencies
        '''
        
        # Open the files
        outfilename = os.path.join(self.rootfolder, 'quotes_and_frequency')
        with c_open(self.mt_filename, 'rb', encoding='utf-8') as infile, \
             c_open(outfilename, 'wb', encoding='utf-8') as outfile:
            # Skip the first lines
            self.skip_lines(infile)
            
            # Parse it all
            print 'Reading cluster file and writing the quotes and frequencies...',
            for line in infile:
                if line[0] == '\t' and line[1] != '\t':
                    tokens = line.split('\t')
                    outfile.write(u'%s\t%d\n' % (tokens[3], int(tokens[1])))
            print 'done'
        
        # Return the created file name
        return outfilename

    def print_quote_ids(self):
        '''
        Reads the cluster file and prints out on each line all the quotes that belong to the same cluster
        (Was called 'leskovec_clusters_encoding.py', changed to this name to reflect what is does)
        '''
        
        # Open the files
        outfilename = os.path.join(self.rootfolder, 'quote_ids')
        with c_open(self.mt_filename, 'rb', encoding='utf-8') as infile, \
             c_open(outfilename, 'wb', encoding='utf-8') as outfile:
            # Skip the first few lines
            self.skip_lines(infile)
            
            # Parse it all
            print 'Reading cluster file and writing quote ids...',
            clust = []
            j = 0
            for line in infile:
                line0 = re.split(r'[\xa0\s+\t\n]+', line)
                if line0[0] != '':
                    clust.append([])
                elif line[0] == '\t' and line[1] != '\t':
                    clust[-1].append(j)
                    j += 1
            
            for cl in clust:
                for x in cl:
                    outfile.write('%d ' % x)
                outfile.write('\n')
            
            print 'done'
        
        # Return the created file name
        return outfilename
    
    def skip_lines(self, f):
        for i in xrange(self.n_skip):
            f.readline()
    
    def count_lines(self, filename):
        print "Counting lines for '" + filename + "'..."
        with c_open(filename, 'rb', encoding='utf-8') as f:
            for i, l in enumerate(f):
                pass
            return i + 1
    
    def load_clusters(self):
        '''
        Load the whole clusters file into a dictionary
        '''
        
        # Open the file
        with c_open(self.mt_filename, 'rb', encoding='utf-8') as infile:
            # Skip the first few lines
            self.skip_lines(infile)
            
            # Parse the file
            print 'Loading cluster file into a dictionary... ( percentage completed:',
            self.clusters = {}
            for i, line in enumerate(infile):
                # Give some info about progress
                if i % self.lineinfostep == 0:
                    print int(round(i*100/self.n_lines)),
                line0 = re.split(r'[\xa0\s+\t\r\n]+', line)
                line_fields = re.split(r'[\t\r\n]', line)
                # Is this a cluster definition line?
                if line0[0] != '':
                    cluster_id = int(line_fields[3])
                    self.clusters[cluster_id] = {'ClSz': int(line_fields[0]), \
                                                 'TotFq': int(line_fields[1]), \
                                                 'Root': line_fields[2], \
                                                 'Quotes': {}}
                # Is this a quote definition line?
                elif line[0] == '\t' and line[1] != '\t':
                    quote_id = int(line_fields[4])
                    self.clusters[cluster_id]['Quotes'][quote_id] = {'QtFq': int(line_fields[1]), \
                                                                     'N_Urls': int(line_fields[2]), \
                                                                     'QtStr': line_fields[3], \
                                                                     'Links': {}}
                # Is this a url definition line?
                elif line[0] == '\t' and line[1] == '\t' and line[2] != '\t':
                    self.clusters[cluster_id]['Quotes'][quote_id]['Links'][line_fields[5]] = {'Tm': line_fields[2], \
                                                                                             'Fq': int(line_fields[3]), \
                                                                                             'UrlTy': line_fields[4]}
            print ') done'
