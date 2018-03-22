# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import json
from superdesk.publish.transmitters import HTTPPushService
from superdesk.publish import register_transmitter
from superdesk.errors import PublishHTTPPushError
import requests
from superdesk import get_resource_service

errors = [PublishHTTPPushError.httpPushError().get_error_description()]
logger = logging.getLogger(__name__)


class HTTPAgendaPush(HTTPPushService):
    hash_header = 'x-agenda-api-key'
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    user_api_key = None

    def _get_headers(self, destination, current_headers):
        secret_token = self._get_secret_token(destination) if self.user_api_key is None else self.user_api_key
        if not secret_token:
            return current_headers
        headers = current_headers
        headers[self.hash_header] = secret_token
        return headers

    def _get_user_api_key(self, user_id, destination):
        """
        Match the Superdesk user with the Agenda user, if an Agenda Api Key is set for the user return that
        If none then try to create one and update the Agenda user.
        If anything goes wrong use the token set in the config
        :param user_id:
        :param destination:
        :return:
        """
        user = get_resource_service('users').find_one(req=None, _id=user_id)
        if user:
            # Try to find the user in Agenda matching on the email address
            try:
                response = requests.post(self._get_assets_url(destination) + '/user/search',
                                         data=json.dumps({'email': user.get('email')}),
                                         headers=self._get_headers(destination, self.headers))
                response.raise_for_status()
            except:
                logger.warn('Exception on search for agenda user email {}'.format(user.get('email')))
                return self._get_secret_token(destination)

            agenda_users = json.loads(response.text)
            if len(agenda_users):
                agenda_user = agenda_users[0]
                ApiKey = agenda_user.get('ApiKey')
                agenda_user_id = agenda_user.get('IDUser')
                if not ApiKey:
                    try:
                        response = requests.get(self._get_assets_url(destination) + '/account/generatekey')
                        response.raise_for_status()
                        ApiKey = json.loads(response.text).get('key')
                    except:
                        logger.warn('Failed to get a new API key from Agenda')
                        return self._get_secret_token(destination)
                    if ApiKey:
                        try:
                            requests.post(self._get_assets_url(destination) + '/user/edit', data=json.dumps(
                                {'ID': agenda_user_id, 'ApiKey': ApiKey,
                                 'FirstName': agenda_user.get('FirstName'),
                                 'LastName': agenda_user.get('LastName'),
                                 'Email': agenda_user.get('Email')}),
                                headers=self._get_headers(destination, self.headers))
                            response.raise_for_status()
                            return ApiKey
                        except Exception:
                            logger.warn('Failed to set API key in the Agenda user {}'.format(agenda_user.get('Email')))
                            return self._get_secret_token(destination)
                else:
                    return ApiKey
            else:
                logger.warn(
                    'Failed to match superdesk user with agenda user using email address {}'.format(user.get('email')))
        logger.warn('Failed to get the superdesk user')
        return self._get_secret_token(destination)

    def _push_item(self, destination, data):
        # pop the ExternalIdentifier as the Superdesk planning id is to long for the Agenda database
        formatted_item = json.loads(data)
        id = formatted_item.pop('ExternalIdentifier')
        type = formatted_item.pop('Type')
        user_id = formatted_item.pop('PublishingUser')

        self.user_api_key = self._get_user_api_key(user_id, destination)
        agenda_entry = json.dumps(formatted_item)

        resource_url = self._get_assets_url(destination) + '/entry/saveentry?pScheduledEntryChangePolicy=1'
        headers = self._get_headers(destination, self.headers)
        try:
            response = requests.post(resource_url, data=agenda_entry, headers=headers)
            response.raise_for_status()
        except Exception as ex:
            logger.exception(ex)
            message = 'Error pushing item %s: %s' % (response.status_code, response.text)
            self._raise_publish_error(response.status_code, Exception(message), destination)

        # need to rethrow exception as a superdesk exception for now for notifiers.
        try:
            # The id from agenda is returned as part of the location header when the Event is created in Agenda
            location = response.headers.get('Location', None)
            if location:
                self._save_agenda_id(id, location, type)
            response.raise_for_status()
        except Exception as ex:
            logger.exception(ex)
            message = 'Error pushing item %s: %s' % (response.status_code, response.text)
            self._raise_publish_error(response.status_code, Exception(message), destination)

    def _save_agenda_id(self, id, location, type):
        agendaId = location.split('/')[-1]
        service = get_resource_service('events') if type == 'event' else get_resource_service('planning')
        original = service.find_one(req=None, _id=id)
        if original:
            service.system_update(id, {'unique_id': agendaId}, original)


register_transmitter('http_agenda_push', HTTPAgendaPush(), errors)
