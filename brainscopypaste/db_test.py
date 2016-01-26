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


def test_url(some_urls):
    with session_scope() as session:
        assert session.query(Url).count() == 20

        assert session.query(Url).get(2).quote.sid == 2
        assert session.query(Url).get(2).cluster.sid == 2
        assert session.query(Url).get(6).quote.sid == 6
        assert session.query(Url).get(6).cluster.sid == 1
        assert session.query(Url).get(10).quote.sid == 0
        assert session.query(Url).get(10).cluster.sid == 0
        assert session.query(Url).get(17).quote.sid == 7
        assert session.query(Url).get(17).cluster.sid == 2

        assert abs(session.query(Url).get(0).timestamp -
                   datetime.utcnow()) < timedelta(seconds=5)
        assert abs(session.query(Url).get(3).timestamp - datetime.utcnow() -
                   timedelta(days=3)) < timedelta(seconds=5)

        assert session.query(Quote).filter_by(sid=0).one().size == 2
        assert session.query(Quote).filter_by(sid=0).one().frequency == 4
        assert abs(session.query(Quote).filter_by(sid=0).one().span -
                   timedelta(days=10)) < timedelta(seconds=5)
        assert [url.id for url
                in session.query(Quote).filter_by(sid=1).one().urls] == [1, 11]

        assert session.query(Cluster).filter_by(sid=0).one().size == 2
        assert session.query(Cluster).filter_by(sid=0).one().size_urls == 4
        assert session.query(Cluster).filter_by(sid=0).one().frequency == 8
        assert abs(session.query(Cluster).filter_by(sid=0).one().span -
                   timedelta(days=15)) < timedelta(seconds=5)

        assert [url.id for url in session.query(Cluster).filter_by(sid=0)
                .one().urls] == [0, 5, 10, 15]
        assert [url.id for url in session.query(Cluster).filter_by(sid=1)
                .one().urls] == [1, 6, 11, 16]

    with pytest.raises(DataError):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(sid=1).one()
            session.add(Url(quote=quote,
                            timestamp=datetime.now(),
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
        assert cloned.urls.all() == []

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
        assert cloned.urls.all() == []


def test_clone_url(some_urls):
    with session_scope() as session:
        url = session.query(Url).get(1)
        cloned = url.clone()
        assert cloned.id is None
        assert cloned.quote_id == url.quote_id
        assert cloned.filtered == url.filtered
        assert cloned.timestamp == url.timestamp
        assert cloned.frequency == url.frequency
        assert cloned.url_type == url.url_type
        assert cloned.url == url.url

        cloned = url.clone(id=700, filtered=True, quote_id=110, url='bla')
        assert cloned.id == 700
        assert cloned.id != url.id
        assert cloned.quote_id == 110
        assert cloned.quote_id != url.quote_id
        assert cloned.filtered is True
        assert cloned.filtered != url.filtered
        assert cloned.timestamp == url.timestamp
        assert cloned.frequency == url.frequency
        assert cloned.url_type == url.url_type
        assert cloned.url == 'bla'
        assert cloned.url != url.url
