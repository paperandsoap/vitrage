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
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import log as logging

from vitrage.common.constants import EventAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.consistency import CONSISTENCY_DATASOURCE
from vitrage.datasources.consistency.transformer import ConsistencyTransformer
from vitrage.tests import base

from vitrage.tests.mocks import mock_driver as mock_sync

LOG = logging.getLogger(__name__)


class TestConsistencyTransformer(base.BaseTest):

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        cls.transformers = {}
        cls.transformers[CONSISTENCY_DATASOURCE] = \
            ConsistencyTransformer(cls.transformers)
        cls.actions = [EventAction.DELETE_ENTITY,
                       EventAction.REMOVE_DELETED_ENTITY]

    def test_snapshot_transform(self):
        LOG.debug('Consistency transformer test: transform entity event '
                  'snapshot')

        # Test setup
        spec_list = mock_sync.simple_consistency_generators(consistency_num=7,
                                                            update_events=7)
        static_events = mock_sync.generate_random_events_list(spec_list)

        for event in static_events:
            # Test action
            wrapper = self.transformers[CONSISTENCY_DATASOURCE].transform(
                event)

            # Test assertions
            vertex = wrapper.vertex
            self._validate_consistency_vertex_props(vertex, event)

            neighbors = wrapper.neighbors
            self.assertEqual(None, neighbors)

            action = wrapper.action
            self.assertIn(action, self.actions)

    def test_update_transform(self):
        LOG.debug('Consistency transformer test: transform entity event '
                  'update')

        # Test setup
        spec_list = mock_sync.simple_consistency_generators(consistency_num=7,
                                                            update_events=7)
        static_events = mock_sync.generate_random_events_list(spec_list)

        for event in static_events:
            # Test action
            wrapper = self.transformers[CONSISTENCY_DATASOURCE].transform(
                event)

            # Test assertions
            vertex = wrapper.vertex
            self._validate_consistency_vertex_props(vertex, event)

            neighbors = wrapper.neighbors
            self.assertEqual(None, neighbors)

            action = wrapper.action
            self.assertIn(action, self.actions)

    def _validate_consistency_vertex_props(self, vertex, event):
        vitrage_id = event.get(VProps.VITRAGE_ID, None)
        self.assertIsNotNone(vitrage_id)

        vertex_id = vertex.vertex_id
        self.assertIsNotNone(vertex_id)

        sample_timestamp = vertex.get(VProps.SAMPLE_TIMESTAMP, None)
        self.assertIsNotNone(sample_timestamp)
