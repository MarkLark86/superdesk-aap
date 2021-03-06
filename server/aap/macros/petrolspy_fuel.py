# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from flask import render_template_string
from datetime import datetime
from flask import current_app as app
from apps.prepopulate.app_initialize import get_filepath
import json
from superdesk import get_resource_service
from superdesk.utils import config
from eve.utils import ParsedRequest
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from titlecase import titlecase
import re

logger = logging.getLogger(__name__)

# These are the markets (cities) that we expect that data is available for
MARKETS = ["Perth", "Sydney", "Melbourne", "Brisbane", "Adelaide"]


def get_areas():
    """
    Read the GeoJson file that outlines a list of named polygons describing the areas we can extract the prices from
    :return:
    """
    areas = []
    path = get_filepath('fuel_geojson.json')
    try:
        with path.open('r') as f:
            areas = json.load(f)
    except Exception as ex:
        logger.error('Exception loading fuel_geojson.json : {}'.format(ex))
    return areas


def fuel_story(item, **kwargs):
    def _get_today():
        """
        Get the current days thumbprint
        :return:
        """
        return datetime.now().isoformat()[:10]

    # groupin clause for the requests
    group = {
        "$group":
            {
                "_id": "$fuel_type",
                "avg": {"$avg": "$price"},
                "min": {"$min": "$price"},
                "max": {"$max": "$price"},
                "std": {"$stdDevPop": "$price"}
            }
    }

    area = get_areas()
    fuel_map = dict()

    for market in MARKETS:
        pipeline = [{
            "$match": {
                "market": market,
                "sample_date": _get_today()
            }
        }, group]

        fuel_types = list(app.data.mongo.aggregate('fuel', pipeline, {}))
        for i in fuel_types:
            fuel_map[market.lower() + '_avg_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('avg')
            fuel_map[market.lower() + '_min_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('min')
            fuel_map[market.lower() + '_max_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('max')

            # If the max is more that X times the std from the average fix it!
            delta_avg_per_std = (i.get('max') - i.get('avg')) / i.get('std') \
                if (i.get('max') - i.get('avg')) != 0 else 0
            if delta_avg_per_std > 5:
                max_limit = i.get('avg') + (5 * i.get('std'))
                req = ParsedRequest()
                req.max_results = 1
                req.sort = '[("price", -1)]'
                expensive = get_resource_service('fuel').get_from_mongo(req=req, lookup={'market': market,
                                                                                         'sample_date': _get_today(),
                                                                                         'fuel_type': i.get('_id'),
                                                                                         'price': {'$lt': max_limit}})
                if expensive.count() > 0:
                    logger.warn('patch max {} to {} from {} for {}'.format(i.get('_id'), expensive[0].get('price'),
                                                                           i.get('max'), market))

                    fuel_map[market.lower() + '_max_' + i.get('_id').lower().replace('-', '')] = '%.1f' % expensive[
                        0].get('price')

            min_price = i.get('min')
            delta_avg_per_std = (i.get('avg') - i.get('min')) / i.get('std') \
                if (i.get('avg') - i.get('min')) != 0 else 0
            if delta_avg_per_std > 5:
                min_limit = i.get('avg') - (5 * i.get('std'))
                req = ParsedRequest()
                req.max_results = 1
                req.sort = '[("price", 1)]'
                lowest = get_resource_service('fuel').get_from_mongo(req=req, lookup={'market': market,
                                                                                      'sample_date': _get_today(),
                                                                                      'fuel_type': i.get('_id'),
                                                                                      'price': {'$gt': min_limit}})
                if lowest.count() > 0:
                    logger.warn('patch min {} to {} from {} for {}'.format(i.get('_id'), lowest[0].get('price'),
                                i.get('min'), market))
                    fuel_map[market.lower() + '_min_' + i.get('_id').lower().replace('-', '')] = '%.1f' % lowest[0].get(
                        'price')
                    min_price = lowest[0].get('price')

            req = ParsedRequest()
            req.max_results = 3
            req.sort = '[("price", 1)]'
            cheapest = get_resource_service('fuel').get_from_mongo(req=req, lookup={'market': market,
                                                                                    'sample_date': _get_today(),
                                                                                    'fuel_type': i.get('_id'),
                                                                                    'price': min_price})
            cheap_tag = market.lower() + '_cheap_' + i.get('_id').lower().replace('-', '')
            cheap_list = None
            for cheap in cheapest:
                suburb = titlecase(cheap.get('address', {}).get('suburb', ''))
                if cheap_list:
                    if suburb not in cheap_list:
                        cheap_list = cheap_list + ', ' + suburb
                else:
                    cheap_list = suburb
            fuel_map[cheap_tag] = re.sub(r",([^,]*)$", r" and\1", cheap_list)

    if len(area):
        for feature in area.get('features', []):
            area_name = feature['properties']['name']
            logger.info('Available area {}'.format(area_name))
            coords = feature.get('geometry').get('coordinates')
            pipeline = [{
                "$match": {
                    "sample_date": _get_today(),
                    "location": {
                        "$geoWithin": {
                            "$geometry": {
                                "type": "Polygon",
                                "coordinates": coords
                            }
                        }
                    }
                }
            }, group]
            fuel_types = list(app.data.mongo.aggregate('fuel', pipeline, {}))
            for i in fuel_types:
                fuel_map[area_name.lower() + '_avg_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('avg')
                fuel_map[area_name.lower() + '_min_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('min')
                fuel_map[area_name.lower() + '_max_' + i.get('_id').lower().replace('-', '')] = '%.1f' % i.get('max')

                # If the max is more that X times the std from the average fix it!
                delta_avg_per_std = (i.get('max') - i.get('avg')) / i.get('std') if (i.get('max') - i.get(
                    'avg')) != 0 else 0
                if delta_avg_per_std > 5:
                    max_limit = i.get('avg') + (5 * i.get('std'))
                    req = ParsedRequest()
                    req.max_results = 1
                    req.sort = '[("price", -1)]'
                    lookup = pipeline[0].get('$match')
                    lookup['fuel_type'] = i.get('_id')
                    lookup['price'] = {'$lt': max_limit}

                    expensive = get_resource_service('fuel').get_from_mongo(req=req, lookup=lookup)
                    if expensive.count() > 0:
                        logger.warn('patch max {} to {} from {} for {}'.format(i.get('_id'), expensive[0].get('price'),
                                                                               i.get('max'), area_name))
                        fuel_map[area_name.lower() + '_max_' + i.get('_id').lower().replace('-', '')] = '%.1f' % \
                                                                                                        expensive[
                                                                                                            0].get(
                                                                                                            'price')
                min_price = i.get('min')
                delta_avg_per_std = (i.get('avg') - i.get('min')) / i.get('std')\
                    if (i.get('avg') - i.get('min')) != 0 else 0
                if delta_avg_per_std > 5:
                    min_limit = i.get('avg') - (5 * i.get('std'))
                    req = ParsedRequest()
                    req.max_results = 1
                    req.sort = '[("price", 1)]'
                    lookup = pipeline[0].get('$match')
                    lookup['fuel_type'] = i.get('_id')
                    lookup['price'] = {'$gt': min_limit}
                    lowest = get_resource_service('fuel').get_from_mongo(req=req, lookup=lookup)
                    if lowest.count() > 0:
                        logger.warn('patch min {} to {} from {} for {}'.format(i.get('_id'), lowest[0].get('price'),
                                                                               i.get('min'), area_name))
                        fuel_map[area_name.lower() + '_min_' + i.get('_id').lower().replace('-', '')] = '%.1f' % lowest[
                            0].get(
                            'price')
                        min_price = lowest[0].get('price')

                req = ParsedRequest()
                req.max_results = 3
                req.sort = '[("price", 1)]'
                lookup = pipeline[0].get('$match')
                lookup['fuel_type'] = i.get('_id')
                lookup['price'] = min_price
                cheapest = get_resource_service('fuel').get_from_mongo(req=req, lookup=lookup)
                cheap_tag = area_name.lower() + '_cheap_' + i.get('_id').lower().replace('-', '')
                cheap_list = None
                for cheap in cheapest:
                    suburb = titlecase(cheap.get('address', {}).get('suburb', ''))
                    if cheap_list:
                        if suburb not in cheap_list:
                            cheap_list = cheap_list + ', ' + suburb
                    else:
                        cheap_list = suburb
                fuel_map[cheap_tag] = re.sub(r",([^,]*)$", r" and\1", cheap_list)

    item['body_html'] = render_template_string(item.get('body_html', ''), **fuel_map)

    update = dict()
    update['body_html'] = item['body_html']
    get_resource_service('archive').system_update(item[config.ID_FIELD], update, item)

    # If the macro is being executed by a scheduled template then publish the item as well
    if 'desk' in kwargs and 'stage' in kwargs:
        get_resource_service('archive_publish').patch(id=item[config.ID_FIELD],
                                                      updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                               'auto_publish': True})
        return get_resource_service('archive').find_one(req=None, _id=item[config.ID_FIELD])

    return item


name = 'fuel injection'
label = 'Fuel Injection'
callback = fuel_story
access_type = 'frontend'
action_type = 'direct'
group = 'AM Desk'
