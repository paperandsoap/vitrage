# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR  CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg

NOVA_ZONE_DATASOURCE = 'nova.zone'

OPTS = [
    cfg.StrOpt('transformer',
               default='vitrage.datasources.nova.zone.transformer.'
                       'ZoneTransformer',
               help='Nova zone transformer class path',
               required=True),
    cfg.StrOpt('driver',
               default='vitrage.datasources.nova.zone.driver'
                       '.ZoneDriver',
               help='Nova zone datasource class path',
               required=True),
]
