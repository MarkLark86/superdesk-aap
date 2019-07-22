# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from datetime import timedelta

from superdesk.tests import TestCase
from superdesk.utc import utc_to_local, utcnow

from .generate_slugline_story_by_desk import (
    GenerateBodyHtmlForPublishedArticlesByDesk,
    generate_published_slugline_story_by_desk
)
from . import init_app


class SluglineStoryByDesk(TestCase):
    articles = []
    published = []
    desks = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_app(None)

    def setUp(self):
        local_time = utc_to_local(self.app.config['DEFAULT_TIMEZONE'], utcnow())

        self.desks = [
            {'name': 'authoring', 'source': 'aap', 'desk_type': 'authoring'},
            {'name': 'production', 'source': 'aap', 'desk_type': 'production'},
            {'name': 'production2', 'source': 'aap', 'desk_type': 'production'}
        ]

        self.app.data.insert('desks', self.desks)

        self.articles = [
            {
                '_id': '1', 'type': 'text', 'abstract': 'abstract item 1', 'slugline': 'slugline item 1',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'in_progress',
                'versioncreated': local_time + timedelta(minutes=-1),
                'task': {
                    'desk': self.desks[0].get('_id')
                }
            },
            {
                '_id': '2', 'type': 'text', 'abstract': 'abstract "item 2" A\\ test.', 'slugline': 'slugline item 2',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'submitted',
                'versioncreated': local_time + timedelta(minutes=-2),
                'task': {
                    'desk': self.desks[1].get('_id'),
                    'last_authoring_desk': self.desks[0].get('_id')
                }
            },
            {
                '_id': '2a', 'type': 'text', 'abstract': 'abstract item 2a', 'slugline': 'slugline item 2a',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(minutes=-5),
                'task': {
                    'desk': self.desks[1].get('_id'),
                    'last_authoring_desk': self.desks[0].get('_id')
                }
            },
            {
                '_id': '3', 'type': 'text', 'abstract': 'abstract item 3', 'slugline': 'slugline item 3',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'submitted',
                'versioncreated': local_time + timedelta(days=-2),
                'task': {
                    'desk': self.desks[1].get('_id'),
                    'last_authoring_desk': self.desks[0].get('_id')
                }
            },
            {
                '_id': '4', 'type': 'text', 'abstract': 'abstract item 4', 'slugline': 'slugline item 4',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'corrected',
                'versioncreated': local_time + timedelta(minutes=-1),
                'task': {
                    'desk': self.desks[1].get('_id')
                }
            },
            {
                '_id': '5', 'type': 'text', 'abstract': 'abstract item 5', 'slugline': 'slugline item 5',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'in_progress',
                'versioncreated': local_time + timedelta(minutes=-1),
                'task': {
                    'desk': self.desks[2].get('_id'),
                    'last_production_desk': self.desks[1].get('_id')
                }
            },
            {
                '_id': '6', 'type': 'text', 'abstract': 'abstract item 6', 'slugline': 'slugline item 6',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(days=-1),
                'task': {
                    'desk': self.desks[2].get('_id')
                }
            },
            {
                '_id': '7', 'type': 'text', 'abstract': 'abstract item 7', 'slugline': 'slugline item 7',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(minutes=-7),
                'task': {
                    'desk': self.desks[0].get('_id')
                }
            }
        ]

        self.published = [
            {
                'item_id': '2a', 'type': 'text', 'abstract': 'abstract item 2a', 'slugline': 'slugline item 2a',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(minutes=-5),
                'task': {
                    'desk': self.desks[1].get('_id'),
                    'last_authoring_desk': self.desks[0].get('_id')
                }
            },
            {
                'item_id': '4', 'type': 'text', 'abstract': 'abstract item 4', 'slugline': 'slugline item 4',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'corrected',
                'versioncreated': local_time + timedelta(minutes=-1),
                'task': {
                    'desk': self.desks[1].get('_id')
                }
            },
            {
                'item_id': '4', 'type': 'text', 'abstract': 'abstract item 4', 'slugline': 'slugline item 4',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(minutes=-5),
                'task': {
                    'desk': self.desks[1].get('_id')
                }
            },
            {
                'item_id': '6', 'type': 'text', 'abstract': 'abstract item 6', 'slugline': 'slugline item 6',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(days=-1),
                'task': {
                    'desk': self.desks[2].get('_id')
                }
            },
            {
                'item_id': '7', 'type': 'text', 'abstract': 'abstract item 7', 'slugline': 'slugline item 7',
                'dateline': {
                    'text': 'Sydney, 01 Jan AAP -',
                    'located': {
                        'city': 'Sydney'
                    }
                },
                'state': 'published',
                'versioncreated': local_time + timedelta(minutes=-7),
                'task': {
                    'desk': self.desks[0].get('_id')
                }
            }
        ]

        self.app.data.insert('archive', self.articles)
        self.app.data.insert('published', self.published)

    def test_slugline_by_desk_for_authoring(self):
        cls = GenerateBodyHtmlForPublishedArticlesByDesk(self.desks[0].get('_id'))
        query, repo = cls.create_query()
        articles = cls.get_articles(query, repo)
        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0]['_id'], '2')
        self.assertEqual(articles[1]['_id'], '2a')
        self.assertEqual(articles[2]['_id'], '7')

    def test_slugline_by_desk_for_production(self):
        cls = GenerateBodyHtmlForPublishedArticlesByDesk(self.desks[1].get('_id'))
        query, repo = cls.create_query()
        articles = cls.get_articles(query, repo)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['_id'], '4')
        self.assertEqual(articles[1]['_id'], '2a')

    def test_generate_body_html(self):
        item = {
            'task': {
                'desk': self.desks[0].get('_id')
            }
        }

        generate_published_slugline_story_by_desk(item)
        self.assertTrue('SYDNEY abstract "item 2" A\\ test. (slugline item 2)' in item['body_html'])
        self.assertTrue('SYDNEY abstract item 2a (slugline item 2a)' in item['body_html'])
        self.assertTrue('SYDNEY abstract item 7 (slugline item 7)' in item['body_html'])
