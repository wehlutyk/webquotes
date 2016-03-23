from os.path import exists
from warnings import warn

import pytest
import numpy as np

from brainscopypaste.db import Quote, Substitution
from brainscopypaste.features import (_get_pronunciations, _get_aoa,
                                      _get_clearpond,
                                      SubstitutionFeaturesMixin)
from brainscopypaste.paths import (fa_norms_degrees_pickle,
                                   fa_norms_PR_scores_pickle,
                                   fa_norms_BCs_pickle, fa_norms_CCs_pickle,
                                   mt_frequencies_pickle)


def test_get_pronunciations():
    pronunciations = _get_pronunciations()
    # We have the right kind of data.
    assert pronunciations['hello'] == [['HH', 'AH0', 'L', 'OW1'],
                                       ['HH', 'EH0', 'L', 'OW1']]
    # And what's loaded is memoized.
    assert pronunciations is _get_pronunciations()


def test_get_aoa():
    aoa = _get_aoa()
    # We have the right kind of data.
    assert aoa['time'] == 5.16
    # 'NA' terms were not loaded.
    assert 'wickiup' not in aoa
    assert len(aoa) == 30102
    # And what's loaded is memoized.
    assert aoa is _get_aoa()


def test_get_clearpond():
    clearpond = _get_clearpond()
    # We have the right kind of data.
    assert clearpond['phonological']['dog'] == 25
    assert clearpond['phonological']['cat'] == 50
    assert clearpond['phonological']['ghost'] == 14
    assert clearpond['phonological']['you'] == 49
    assert clearpond['orthographical']['dog'] == 20
    assert clearpond['orthographical']['cat'] == 33
    assert clearpond['orthographical']['ghost'] == 2
    assert clearpond['orthographical']['you'] == 4
    # And what's loaded is memoized.
    assert clearpond is _get_clearpond()


def test_syllables_count():
    assert SubstitutionFeaturesMixin._syllables_count('hello') == 2
    assert SubstitutionFeaturesMixin._syllables_count('mountain') == 2
    assert np.isnan(SubstitutionFeaturesMixin._syllables_count('makakiki'))


def test_phonemes_count():
    assert SubstitutionFeaturesMixin._phonemes_count('hello') == 4
    assert SubstitutionFeaturesMixin._phonemes_count('mountain') == 6
    assert np.isnan(SubstitutionFeaturesMixin._phonemes_count('makakiki'))


def test_letters_count():
    assert SubstitutionFeaturesMixin._letters_count('hello') == 5
    assert SubstitutionFeaturesMixin._letters_count('mountain') == 8
    assert SubstitutionFeaturesMixin._letters_count('makakiki') == 8


def test_synonyms_count():
    # 'hello' has a single synset, with 5 members. So 4 synonyms.
    assert SubstitutionFeaturesMixin._synonyms_count('hello') == 4
    # 'mountain' has two synsets, with 2 and 27 members.
    # So ((2-1) + (27-1))/2 synonyms.
    assert SubstitutionFeaturesMixin._synonyms_count('mountain') == 13.5
    # 'lamp' has two synsets, with only one member in each.
    # So no synonyms, which yields `np.nan`.
    assert np.isnan(SubstitutionFeaturesMixin._synonyms_count('lamp'))
    # 'makakiki' does not exist.
    assert np.isnan(SubstitutionFeaturesMixin._synonyms_count('makakiki'))


def test_aoa():
    assert SubstitutionFeaturesMixin._aoa('time') == 5.16
    assert SubstitutionFeaturesMixin._aoa('vocative') == 14.27
    assert np.isnan(SubstitutionFeaturesMixin._aoa('wickiup'))


def guard_feature_test(file):
    if not exists(file):
        # TODO: make this how up in pytest report
        warn("Skipping feature test: feature file ('{}') not "
             'found. You should run `brainscopypaste load features` '
             'beforehand if you want this test to run.'
             .format(file))
        return False
    else:
        return True


def test_fa_degree():
    if guard_feature_test(fa_norms_degrees_pickle):
        assert SubstitutionFeaturesMixin._fa_degree('abdomen') == \
            1 / (10617 - 1)
        assert SubstitutionFeaturesMixin._fa_degree('speaker') == \
            9 / (10617 - 1)
        assert np.isnan(SubstitutionFeaturesMixin._fa_degree('wickiup'))


def test_fa_pagerank():
    if guard_feature_test(fa_norms_PR_scores_pickle):
        assert abs(SubstitutionFeaturesMixin._fa_pagerank('you') -
                   0.0006390798677378056) < 1e-15
        assert abs(SubstitutionFeaturesMixin._fa_pagerank('play') -
                   0.0012008124120435305) < 1e-15
        assert np.isnan(SubstitutionFeaturesMixin._fa_pagerank('wickiup'))


def test_fa_betweenness():
    if guard_feature_test(fa_norms_BCs_pickle):
        assert SubstitutionFeaturesMixin.\
            _fa_betweenness('dog') == 0.0046938277117769605
        assert SubstitutionFeaturesMixin.\
            _fa_betweenness('play') == 0.008277234906313704
        assert np.isnan(SubstitutionFeaturesMixin._fa_betweenness('wickiup'))


def test_fa_clustering():
    if guard_feature_test(fa_norms_CCs_pickle):
        assert SubstitutionFeaturesMixin.\
            _fa_clustering('dog') == 0.0009318641757868838
        assert SubstitutionFeaturesMixin.\
            _fa_clustering('play') == 0.0016238663632016216
        assert np.isnan(SubstitutionFeaturesMixin._fa_clustering('wickiup'))


def test_frequency():
    if guard_feature_test(mt_frequencies_pickle):
        assert SubstitutionFeaturesMixin._frequency('dog') == 7865
        assert SubstitutionFeaturesMixin._frequency('play') == 45848
        assert np.isnan(SubstitutionFeaturesMixin._frequency('wickiup'))


def test_phonological_density():
    assert SubstitutionFeaturesMixin._phonological_density('time') == 29
    assert np.isnan(SubstitutionFeaturesMixin._phonological_density('wickiup'))


def test_orthographical_density():
    assert SubstitutionFeaturesMixin._orthographical_density('time') == 13
    assert np.isnan(SubstitutionFeaturesMixin.
                    _orthographical_density('wickiup'))


def test_features():
    q1 = Quote(string='It is the containing part')
    q2 = Quote(string='It is the other part')
    s = Substitution(source=q1, destination=q2, start=0, position=3)
    # Check we defined the right substitution.
    assert s.tokens == ('containing', 'other')
    assert s.lemmas == ('contain', 'other')

    # An unknown feature raises an error
    with pytest.raises(ValueError):
        s.features('unknown_feature')
    with pytest.raises(ValueError):
        s.features('unknown_feature', sentence_relative=True)

    # Syllable, phonemes, letters counts, and densities are right,
    # and computed on tokens.
    assert s.features('syllables_count') == (3, 2)
    assert s.features('phonemes_count') == (8, 3)
    assert s.features('letters_count') == (10, 5)
    assert s.features('phonological_density') == (0, 7)
    assert s.features('orthographical_density') == (0, 5)
    # Same with features computed relative to sentence.
    assert s.features('syllables_count',
                      sentence_relative=True) == (3 - 7/5, 2 - 6/5)
    assert s.features('phonemes_count',
                      sentence_relative=True) == (8 - 18/5, 3 - 13/5)
    assert s.features('letters_count',
                      sentence_relative=True) == (10 - 21/5, 5 - 16/5)
    assert s.features('phonological_density',
                      sentence_relative=True) == (0 - 92/5, 7 - 99/5)
    assert s.features('orthographical_density',
                      sentence_relative=True) == (0 - 62/5, 5 - 67/5)

    # Synonyms count, age-of-acquisition, FA features, and frequency
    # are right, and computed on lemmas.
    assert s.features('synonyms_count') == (3, .5)
    assert s.features('aoa') == (7.88, 5.33)
    if guard_feature_test(fa_norms_degrees_pickle):
        assert s.features('fa_degree') == \
            (9.419743782969103e-05, 0.0008477769404672192)
    if guard_feature_test(fa_norms_PR_scores_pickle):
        assert abs(s.features('fa_pagerank')[0] -
                   2.9236183726513393e-05) < 1e-15
        assert abs(s.features('fa_pagerank')[1] -
                   6.421655879054584e-05) < 1e-15
    if guard_feature_test(fa_norms_BCs_pickle):
        assert np.isnan(s.features('fa_betweenness')[0])
        assert s.features('fa_betweenness')[1] == 0.0003369277738594168
    if guard_feature_test(fa_norms_CCs_pickle):
        assert np.isnan(s.features('fa_clustering')[0])
        assert s.features('fa_clustering')[1] == 0.0037154495910700605
    if guard_feature_test(mt_frequencies_pickle):
        assert s.features('frequency') == (3992, 81603)
    # Same with features computed relative to sentence.
    assert s.features('synonyms_count', sentence_relative=True) == \
        (3 - 1.8611111111111112, .5 - 1.2361111111111112)
    assert s.features('aoa', sentence_relative=True) == \
        (7.88 - 6.033333333333334, 5.33 - 5.183333333333334)
    if guard_feature_test(fa_norms_degrees_pickle):
        assert s.features('fa_degree', sentence_relative=True) == \
            (9.419743782969103e-05 - 0.0010550113036925397,
             0.0008477769404672192 - 0.0012057272042200451)
    if guard_feature_test(fa_norms_PR_scores_pickle):
        assert abs(s.features('fa_pagerank', sentence_relative=True)[0] -
                   (2.9236183726513393e-05 - 9.2820794154173557e-05)) < 1e-15
        assert abs(s.features('fa_pagerank', sentence_relative=True)[1] -
                   (6.421655879054584e-05 - 9.9816869166980042e-05)) < 1e-15
    if guard_feature_test(fa_norms_BCs_pickle):
        assert np.isnan(s.features('fa_betweenness',
                                   sentence_relative=True)[0])
        assert s.features('fa_betweenness', sentence_relative=True)[1] == \
            0.0003369277738594168 - 0.00081995401378403285
    if guard_feature_test(fa_norms_CCs_pickle):
        assert np.isnan(s.features('fa_clustering', sentence_relative=True)[0])
        assert s.features('fa_clustering', sentence_relative=True)[1] == \
            0.0037154495910700605 - 0.0021628891370054143
    if guard_feature_test(mt_frequencies_pickle):
        assert s.features('frequency', sentence_relative=True) == \
            (3992 - 1373885.6000000001, 81603 - 1389407.8)

    # Unknown words are ignored. Also when in the rest of the sentence.
    q1 = Quote(string='makakiki is the goal')
    q2 = Quote(string='makakiki is the moukakaka')
    s = Substitution(source=q1, destination=q2, start=0, position=3)
    assert s.features('syllables_count')[0] == 1
    # np.nan != np.nan so we can't `assert s.features(...) == (1, np.nan)`
    assert np.isnan(s.features('syllables_count')[1])
    assert s.features('syllables_count', sentence_relative=True)[0] == 1 - 3/3
    assert np.isnan(s.features('syllables_count', sentence_relative=True)[1])
