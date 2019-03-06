# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.errors import ParserError, SuperdeskPublishError


class AAPParserError(ParserError):

    ParserError._codes.update({1100: 'ZCZC input could not be processed',
                               1101: 'News Bites input could not be processed',
                               1102: 'PDA Results input could not be processed',
                               1103: 'AsiaNet input could not be processed'})

    @classmethod
    def ZCZCParserError(cls, exception=None, provider=None):
        return ParserError(1100, exception, provider)

    @classmethod
    def NewsBitesParserError(cls, exception=None, provider=None):
        return ParserError(1101, exception, provider)

    @classmethod
    def PDAResulstParserError(cls, exception=None, provider=None):
        return ParserError(1102, exception, provider)

    @classmethod
    def AsiaNetParserError(cls, exception=None, provider=None):
        return ParserError(1103, exception, provider)


class PublishSocketError(SuperdeskPublishError):
    _codes = {
        15101: "Socket publish connection error",
        15102: "Socket publish send error"
    }

    @classmethod
    def socketConnectionError(cls, exception=None, destination=None):
        return PublishSocketError(15101, exception, destination)

    @classmethod
    def socketSendError(cls, exception=None, destination=None):
        return PublishSocketError(15102, exception, destination)


class AppleNewsError(SuperdeskPublishError):
    _codes = {
        50000: 'Article couldn"t be converted to Apple news format',
        50001: 'Failed to publish article to Apple News'
    }

    @classmethod
    def AppleNewsFormatter(cls, exception=None, destination=None):
        return AppleNewsError(50000, exception, destination)

    @classmethod
    def AppleNewsPublishError(cls, exception=None, destination=None):
        return AppleNewsError(50001, exception, destination)
