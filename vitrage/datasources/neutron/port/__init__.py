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

NEUTRON_PORT_DATASOURCE = 'neutron.port'

OPTS = [
    cfg.StrOpt('transformer',
               default='vitrage.datasources.neutron.port.'
                       'transformer.PortTransformer',
               help='Neutron port transformer class path',
               required=True),
    cfg.StrOpt('driver',
               default='vitrage.datasources.neutron.port.driver.PortDriver',
               help='Neutron port driver class path',
               required=True),
    cfg.StrOpt('notification_topic',
               default='vitrage_notifications',
               help='Neutron port configured notifications topic for Vitrage'),
]
