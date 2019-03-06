# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from .resource import SubscriberTransmitReferenceResource
from .service import SubscriberTransmitReferenceService


def init_app(app):
    endpoint_name = 'subscriber_transmit_references'
    refs_service = SubscriberTransmitReferenceService(endpoint_name, backend=superdesk.get_backend())
    SubscriberTransmitReferenceResource(endpoint_name, app=app, service=refs_service)
