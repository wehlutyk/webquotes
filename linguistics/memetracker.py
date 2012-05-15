#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Linguistic analysis tools for the MemeTracker dataset.

Methods:
  * levenshtein: compute levenshtein distance between s1 and s2
  * levenshtein_word: compute levenshtein distance between s1 and s2, taking
                      words as the editing unit
  * timebag_levenshtein_sphere: get the indexes of the strings in a TimeBag
                                that are at levenshtein-distance == d from a
                                string
  * timebag_levenshtein_word_sphere: get the indexes of the strings in a
                                     TimeBag that are at
                                     levenshtein_word-distance == d from a
                                     string
  * hamming: compute hamming distance between s1 and s2
  * hamming_word: compute hamming distance between s1 and s2, taking words as
                  the editing unit
  * timebag_hamming_sphere: get the indexes of the strings in a TimeBag that
                            are at hamming-distance == d from a string
  * timebag_hamming_word_sphere: get the indexes of the strings in a TimeBag
                                 that are at hamming_word-distance == d from a
                                 string
  * sublists: get all sublists of s of length l
  * subhamming: compute the minimum hamming distance between s2 and all
                sublists of s1
  * subhamming_word: compute subhamming distance between s1 and s2, taking
                     words as the editing unit
  * timebag_subhamming_sphere: get the indices and motherstrings of the
                               substrings in a TimeBag that are at
                               subhamming-distance == d from a string
  * timebag_subhamming_word_sphere: get the indices and motherstrings of the
                                    substrings in a TimeBag that are at
                                    subhamming_word-distance == d from a
                                    string

"""


import numpy as np

from linguistics.treetagger import TreeTaggerTags
import settings as st


def levenshtein(s1, s2):
    """Compute levenshtein distance between s1 and s2."""

    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    
    if not s2:
        return len(s1)
    
    previous_row = xrange(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        
        current_row = [i + 1]
        
        for j, c2 in enumerate(s2):
            
            # previous_row and current_row are one character longer than s2,
            # hence the 'j + 1'
            
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        
        previous_row = current_row 
    
    return previous_row[-1]


tagger = TreeTaggerTags(TAGLANG='en', TAGDIR=st.treetagger_TAGDIR,
                        TAGINENC='utf-8', TAGOUTENC='utf-8')


def levenshtein_word(s1, s2):
    """Compute levenshtein distance between s1 and s2, taking words as the
    editing unit."""
    return levenshtein(tagger.Tokenize(s1), tagger.Tokenize(s2))


def timebag_levenshtein_sphere(timebag, center_string, d):
    """Get the indexes of the strings in a TimeBag that are at
    levenshtein-distance == d from a string."""
    distances = np.array([levenshtein(center_string, bag_string)
                          for bag_string in timebag.strings])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        return idx[0].tolist()
    else:
        return []


def timebag_levenshtein_word_sphere(timebag, center_string, d):
    """Get the indexes of the strings in a TimeBag that are at
    levenshtein_word-distance == d from a string."""
    distances = np.array([levenshtein_word(center_string, bag_string)
                          for bag_string in timebag.strings])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        return idx[0].tolist()
    else:
        return []


def hamming(s1, s2):
    """Compute the hamming distance between s1 and s2."""
    if len(s1) != len(s2):
        return -1
    else:
        return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


def hamming_word(s1, s2):
    """Compute the hamming distance between s1 and s2, taking words as the
    editing unit."""
    return hamming(tagger.Tokenize(s1), tagger.Tokenize(s2))


def timebag_hamming_sphere(timebag, center_string, d):
    """Get the indexes of the strings in a TimeBag that are at
    hamming-distance == d from a string."""
    distances = np.array([hamming(center_string, bag_string)
                          for bag_string in timebag.strings])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        return idx[0].tolist()
    else:
        return []


def timebag_hamming_word_sphere(timebag, center_string, d):
    """Get the indexes of the strings in a TimeBag that are at
    hamming_word-distance == d from a string."""
    distances = np.array([hamming_word(center_string, bag_string)
                          for bag_string in timebag.strings])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        return idx[0].tolist()
    else:
        return []


def sublists(s, l):
    """Get all sublists of s of length l."""
    return [s[i:i + l] for i in range(len(s) - l + 1)]


def subhamming(s1, s2):
    """Compute the minimum hamming distance between s2 and all sublists of
    s1."""
    
    l1 = len(s1)
    l2 = len(s2)
    
    if l1 < l2:
        return (-1, -1, -1)
    if l1 == l2:
        return (hamming(s1, s2), 0, l2)
    
    distances = np.zeros(l1 - l2 + 1)
    
    for i, subs in enumerate(sublists(s1, l2)):
        distances[i] = hamming(subs, s2)
    
    amin = np.argmin(distances)
    return (distances[amin], amin, l2)


def subhamming_word(s1, s2):
    """Compute the subhamming distance between s1 and s2, taking words as the
    editing unit."""
    return subhamming(tagger.Tokenize(s1), tagger.Tokenize(s2))


def timebag_subhamming_sphere(timebag, center_string, d):
    """Get the indices and motherstrings of the substrings in a TimeBag that
    are at subhamming-distance == d from a string."""
    subhs = [subhamming(center_string, bag_string)
             for bag_string in timebag.strings]
    distances = np.array([subh[0] for subh in subhs])
    subindices = np.array([subh[1] for subh in subhs])
    lens = np.array([subh[2] for subh in subhs])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        
        motherstrings = [(subindices[i], lens[i]) for i in idx[0]]
        return zip(idx[0].tolist(), motherstrings)
    
    else:
        return []


def timebag_subhamming_word_sphere(timebag, center_string, d):
    """Get the indices and motherstrings of the substrings in a TimeBag that
    are at subhamming_word-distance == d from a string."""
    subhs = [subhamming_word(center_string, bag_string)
             for bag_string in timebag.strings]
    distances = np.array([subh[0] for subh in subhs])
    subindices = np.array([subh[1] for subh in subhs])
    lens = np.array([subh[2] for subh in subhs])
    
    idx = np.where(distances == d)
    
    if len(idx) > 0:
        
        motherstrings = [(subindices[i], lens[i]) for i in idx[0]]
        return zip(idx[0].tolist(), motherstrings)
    
    else:
        return []
