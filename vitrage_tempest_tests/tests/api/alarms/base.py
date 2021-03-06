# Copyright 2016 Nokia
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import random
import time

from oslo_log import log as logging
from vitrage import clients
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties

from vitrage_tempest_tests.tests.api.base import BaseApiTest

import vitrage_tempest_tests.tests.utils as utils

LOG = logging.getLogger(__name__)

TEMPLATES_RESOURCES_PATH = 'resources/templates/'
TEMPLATES_SOURCES_PATH = '/etc/vitrage/templates/'


class BaseAlarmsTest(BaseApiTest):
    """Topology test class for Vitrage API tests."""

    @classmethod
    def setUpClass(cls):
        super(BaseAlarmsTest, cls).setUpClass()
        cls.ceilometer_client = clients.ceilometer_client(cls.conf)

    @staticmethod
    def _filter_alarms_by_parameter(alarms_list,
                                    keys, values):
        filtered_alarms_list = []
        for item in alarms_list:
            verification = 0
            category = utils.uni2str(item[VertexProperties.CATEGORY])
            for index in range(len(keys)):
                key = utils.uni2str(item[keys[index]])
                if category == EntityCategory.ALARM \
                        and key == values[index]:
                    verification += 1
                else:
                    break
            if verification == len(keys):
                filtered_alarms_list.append(item)
        return filtered_alarms_list

    def _create_ceilometer_alarm(self, resource_id=None,
                                 name=None, unic=True):
        if not name:
            name = '%s-%s' % ('test_', random.randrange(0, 100000, 1))
        elif unic:
            name = '%s-%s' % (name, random.randrange(0, 100000, 1))

        aodh_request = self._aodh_request(resource_id=resource_id, name=name)
        self.ceilometer_client.alarms.create(**aodh_request)
        self._wait_for_status(20,
                              self._check_num_alarms,
                              num_alarms=1)
        time.sleep(25)

    def _delete_ceilometer_alarms(self):
        alarms = self.ceilometer_client.alarms.list()
        for alarm in alarms:
            self.ceilometer_client.alarms.delete(alarm.alarm_id)
        self._wait_for_status(20,
                              self._check_num_alarms,
                              num_alarms=0)
        time.sleep(25)

    @staticmethod
    def _aodh_request(resource_id=None, name=None):
        query = []
        if resource_id:
            query = [
                dict(
                    field=u'resource_id',
                    type='',
                    op=u'eq',
                    value=resource_id)
            ]

        return dict(
            name=name,
            description=u'test alarm',
            event_rule=dict(query=query),
            severity='low',
            state='alarm',
            type=u'event')

    def _check_num_alarms(self, num_alarms=0, state=''):
        if len(self.ceilometer_client.alarms.list()) != num_alarms:
            return False

        return all(alarm.state.upper() == state.upper()
                   for alarm in self.ceilometer_client.alarms.list())
