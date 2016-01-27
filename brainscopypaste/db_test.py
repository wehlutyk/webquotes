from datetime import datetime, timedelta

from sqlalchemy.exc import DataError
import pytest

from brainscopypaste.utils import session_scope
from brainscopypaste.db import Cluster, Quote, Url


def test_cluster(some_clusters):
    with session_scope() as session:
        assert session.query(Cluster).count() == 5
        assert session.query(Cluster.sid).all() == \
            [(i,) for i in some_clusters]
        assert session.query(Cluster).filter_by(sid=0).one().size == 0
        assert session.query(Cluster).filter_by(sid=0).one().size_urls == 0
        assert session.query(Cluster).filter_by(sid=0).one().frequency == 0

        assert session.query(Cluster).get(1).format_copy() == \
            '1\t0\tFalse\ttest'


def test_quote(some_quotes):
    with session_scope() as session:
        assert session.query(Quote).count() == 10

        assert session.query(Quote).filter_by(sid=0).one().cluster.sid == 0
        assert session.query(Quote).filter_by(sid=2).one().cluster.sid == 2
        assert session.query(Quote).filter_by(sid=4).one().cluster.sid == 4
        assert session.query(Quote).filter_by(sid=6).one().cluster.sid == 1
        assert session.query(Quote).filter_by(sid=6).one().tokens == \
            ['Some', 'quote', 'to', 'tokenize', '6']

        assert [quote.sid for quote in
                session.query(Cluster).filter_by(sid=3).one().quotes] == [3, 8]
        q1 = session.query(Quote).filter_by(sid=1).one()
        assert session.query(Cluster.sid)\
            .filter(Cluster.quotes.contains(q1)).one() == (1,)
        q7 = session.query(Quote).filter_by(sid=7).one()
        assert session.query(Cluster.sid)\
            .filter(Cluster.quotes.contains(q7)).one() == (2,)

        assert session.query(Quote).filter_by(sid=0).one().size == 0
        assert session.query(Quote).filter_by(sid=0).one().frequency == 0
        assert session.query(Quote).filter_by(sid=0).one().span == timedelta(0)
        assert session.query(Cluster).filter_by(sid=3).one().size == 2
        assert session.query(Cluster).filter_by(sid=3).one().size_urls == 0
        assert session.query(Cluster).filter_by(sid=3).one().frequency == 0
        assert session.query(Cluster)\
            .filter_by(sid=3).one().span == timedelta(0)

        assert session.query(Quote).get(1).format_copy() == \
            "1\t1\t0\tFalse\tSome quote to tokenize 0\t{}\t{}\t{}\t{}"


def test_url(some_urls):
    with session_scope() as session:
        basedate = datetime(year=2008, month=1, day=1)
        assert session.query(Quote).get(1).urls[0].timestamp == basedate
        assert session.query(Quote).get(4).urls[0].timestamp == \
            basedate + timedelta(days=3)

        assert session.query(Quote).filter_by(sid=0).one().size == 2
        assert session.query(Quote).filter_by(sid=0).one().frequency == 4
        assert session.query(Quote).filter_by(sid=0).one().span == \
            timedelta(days=10)

        assert session.query(Cluster).filter_by(sid=0).one().size == 2
        assert session.query(Cluster).filter_by(sid=0).one().size_urls == 4
        assert session.query(Cluster).filter_by(sid=0).one().frequency == 8
        assert session.query(Cluster).filter_by(sid=0).one().span == \
            timedelta(days=15)

        assert session.query(Quote).get(1).format_copy() == \
            ('1\t1\t0\tFalse\tSome quote to tokenize 0\t'
             '{2008-01-01 00:00:00, 2008-01-11 00:00:00}\t'
             '{2, 2}\t{B, B}\t'
             '{"Url with \\\\" and \' 0", "Url with \\\\" and \' 10"}')

    with pytest.raises(DataError):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(sid=1).one()
            quote.add_url(Url(timestamp=datetime.now(),
                              frequency=1,
                              url_type='C',
                              url='some url'))


def test_clone_cluster(some_urls):
    with session_scope() as session:
        cluster = session.query(Cluster).get(1)
        cloned = cluster.clone()
        assert cloned.id is None
        assert cloned.sid == cluster.sid
        assert cloned.filtered == cluster.filtered
        assert cloned.source == cluster.source
        assert cloned.quotes.all() == []

        cloned = cluster.clone(id=500, filtered=True, source='another')
        assert cloned.id == 500
        assert cloned.id != cluster.id
        assert cloned.sid == cluster.sid
        assert cloned.filtered is True
        assert cloned.filtered != cluster.filtered
        assert cloned.source == 'another'
        assert cloned.source != cluster.source
        assert cloned.quotes.all() == []


def test_clone_quote(some_urls):
    with session_scope() as session:
        quote = session.query(Quote).get(1)
        cloned = quote.clone()
        assert cloned.id is None
        assert cloned.cluster_id == quote.cluster_id
        assert cloned.sid == quote.sid
        assert cloned.filtered == quote.filtered
        assert cloned.string == quote.string
        assert cloned.urls == quote.urls

        cloned = quote.clone(id=600, filtered=True,
                             cluster_id=125, string='hello')
        assert cloned.id == 600
        assert cloned.id != quote.id
        assert cloned.cluster_id == 125
        assert cloned.cluster_id != quote.cluster_id
        assert cloned.sid == quote.sid
        assert cloned.filtered is True
        assert cloned.filtered != quote.filtered
        assert cloned.string == 'hello'
        assert cloned.string != quote.string
        assert cloned.urls == quote.urls
