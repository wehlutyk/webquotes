import logging
from csv import DictReader, reader as csvreader

import numpy as np
from nltk.corpus import cmudict, wordnet

from brainscopypaste.utils import is_int, memoized, unpickle
from brainscopypaste.paths import (aoa_Kuperman_csv, clearpond_csv,
                                   fa_norms_degrees_pickle,
                                   fa_norms_PR_scores_pickle,
                                   fa_norms_BCs_pickle, fa_norms_CCs_pickle,
                                   mt_frequencies_pickle)


logger = logging.getLogger(__name__)


@memoized
def _get_pronunciations():
    logger.debug('Loading CMU data')
    return cmudict.dict()


@memoized
def _get_aoa():
    logger.debug('Loading Age-of-Acquisition data')

    aoa = {}
    with open(aoa_Kuperman_csv) as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            word = row['Word']
            mean = row['Rating.Mean']
            if mean == 'NA':
                continue
            if word in aoa:
                raise Exception("'{}' is already is AoA dictionary"
                                .format(word))
            aoa[word] = float(mean)
    return aoa


@memoized
def _get_clearpond():
    logger.debug('Loading Clearpond data')

    clearpond_orthographical = {}
    clearpond_phonological = {}
    with open(clearpond_csv, encoding='iso-8859-2') as csvfile:
        reader = csvreader(csvfile, delimiter='\t')
        for row in reader:
            word = row[0].lower()
            if word in clearpond_phonological:
                raise Exception("'{}' is already is Clearpond phonological "
                                'dictionary'.format(word))
            if word in clearpond_orthographical:
                raise Exception("'{}' is already is Clearpond orthographical "
                                'dictionary'.format(word))
            clearpond_orthographical[word] = int(row[5])
            clearpond_phonological[word] = int(row[29])
    return {'orthographical': clearpond_orthographical,
            'phonological': clearpond_phonological}


class SubstitutionFeaturesMixin:

    __features__ = {
        'syllables_count': 'tokens',
        'phonemes_count': 'tokens',
        'letters_count': 'tokens',
        'synonyms_count': 'lemmas',
        'aoa': 'lemmas',
        'fa_degree': 'lemmas',
        'fa_pagerank': 'lemmas',
        'fa_betweenness': 'lemmas',
        'fa_clustering': 'lemmas',
        'frequency': 'lemmas',
        'phonological_density': 'tokens',
        'orthographical_density': 'tokens',
    }

    @memoized
    def features(self, name, sentence_relative=False):
        if name not in self.__features__:
            raise ValueError("Unknown feature: '{}'".format(name))

        # Get the substitution's tokens or lemmas,
        # depending on the requested feature.
        source_type = self.__features__[name]
        word1, word2 = getattr(self, source_type)

        # Compute the features.
        feature = getattr(self, '_' + name)
        feature1, feature2 = feature(word1), feature(word2)

        if sentence_relative:
            # Substract the average sentence feature.
            destination_words = getattr(self.destination, source_type)
            source_words = getattr(self.source, source_type)[
                self.start:self.start + len(destination_words)]
            feature1 -= np.nanmean([feature(word) for word
                                    in source_words])
            feature2 -= np.nanmean([feature(word) for word
                                    in destination_words])

        return (feature1, feature2)

    @classmethod
    @memoized
    def feature_h0(self, name, neighbour_range=None):
        # TODO: implement
        raise NotImplementedError

    @classmethod
    @memoized
    def _syllables_count(self, word):
        pronunciations = _get_pronunciations()
        if word not in pronunciations:
            return np.nan
        return np.mean([sum([is_int(ph[-1]) for ph in pronunciation])
                        for pronunciation in pronunciations[word]])

    @classmethod
    @memoized
    def _phonemes_count(self, word):
        pronunciations = _get_pronunciations()
        if word not in pronunciations:
            return np.nan
        return np.mean([len(pronunciation)
                        for pronunciation in pronunciations[word]])

    @classmethod
    @memoized
    def _letters_count(self, word):
        return len(word)

    @classmethod
    @memoized
    def _synonyms_count(self, word):
        synsets = wordnet.synsets(word)
        if len(synsets) == 0:
            return np.nan
        count = np.mean([len(synset.lemmas()) - 1 for synset in synsets])
        return count if count != 0 else np.nan

    @classmethod
    @memoized
    def _aoa(self, word):
        aoa = _get_aoa()
        return aoa.get(word, np.nan)

    @classmethod
    @memoized
    def _fa_degree(self, word):
        fa_degree = unpickle(fa_norms_degrees_pickle)
        return fa_degree.get(word, np.nan)

    @classmethod
    @memoized
    def _fa_pagerank(self, word):
        fa_pagerank = unpickle(fa_norms_PR_scores_pickle)
        return fa_pagerank.get(word, np.nan)

    @classmethod
    @memoized
    def _fa_betweenness(self, word):
        fa_betweenness = unpickle(fa_norms_BCs_pickle)
        return fa_betweenness.get(word, np.nan)

    @classmethod
    @memoized
    def _fa_clustering(self, word):
        fa_clustering = unpickle(fa_norms_CCs_pickle)
        return fa_clustering.get(word, np.nan)

    @classmethod
    @memoized
    def _frequency(self, word):
        frequency = unpickle(mt_frequencies_pickle)
        return frequency.get(word, np.nan)

    @classmethod
    @memoized
    def _phonological_density(self, word):
        clearpond_phonological = _get_clearpond()['phonological']
        return clearpond_phonological.get(word, np.nan)

    @classmethod
    @memoized
    def _orthographical_density(self, word):
        clearpond_orthographical = _get_clearpond()['orthographical']
        return clearpond_orthographical.get(word, np.nan)
