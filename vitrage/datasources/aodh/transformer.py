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

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps
from vitrage.common import datetime_utils
from vitrage.datasources.alarm_properties import AlarmProperties as AlarmProps
from vitrage.datasources.alarm_transformer_base import AlarmTransformerBase
from vitrage.datasources.aodh.properties import AodhProperties as AodhProps
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import Neighbor
import vitrage.graph.utils as graph_utils

LOG = logging.getLogger(__name__)


class AodhTransformer(AlarmTransformerBase):

    STATUS_OK = 'ok'

    def __init__(self, transformers):
        super(AodhTransformer, self).__init__(transformers)

    def _create_snapshot_entity_vertex(self, entity_event):
        if _is_vitrage_alarm(entity_event):
            return self._create_merge_alarm_vertex(entity_event)
        return self._create_vertex(entity_event)

    def _create_update_entity_vertex(self, entity_event):
        if _is_vitrage_alarm(entity_event):
            return self._create_merge_alarm_vertex(entity_event)
        return self._create_vertex(entity_event)

    def _create_vertex(self, entity_event):
        metadata = {
            VProps.NAME: entity_event[AodhProps.NAME],
            VProps.SEVERITY: entity_event[AodhProps.SEVERITY],
            AodhProps.DESCRIPTION: entity_event[AodhProps.DESCRIPTION],
            AodhProps.ENABLED: entity_event[AodhProps.ENABLED],
            VProps.PROJECT_ID: entity_event[AodhProps.PROJECT_ID],
            AodhProps.REPEAT_ACTIONS: entity_event[AodhProps.REPEAT_ACTIONS],
            'alarm_type': entity_event[AodhProps.TYPE]
        }

        if entity_event[AodhProps.TYPE] == AodhProps.EVENT:
            metadata[AodhProps.EVENT_TYPE] = entity_event[AodhProps.EVENT_TYPE]

        elif entity_event[AodhProps.TYPE] == AodhProps.THRESHOLD:
            metadata[AodhProps.STATE_TIMESTAMP] = \
                entity_event[AodhProps.STATE_TIMESTAMP]

        sample_timestamp = entity_event[DSProps.SAMPLE_DATE]

        update_timestamp = self._format_update_timestamp(
            AodhTransformer._timestamp(entity_event), sample_timestamp)

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            entity_id=entity_event[AodhProps.ALARM_ID],
            entity_category=EntityCategory.ALARM,
            entity_type=entity_event[DSProps.SYNC_TYPE],
            entity_state=AlarmProps.ALARM_ACTIVE_STATE,
            sample_timestamp=sample_timestamp,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _create_snapshot_neighbors(self, entity_event):
        return self._create_aodh_neighbors(entity_event)

    def _create_update_neighbors(self, entity_event):
        return self._create_aodh_neighbors(entity_event)

    def _create_aodh_neighbors(self, entity_event):
        graph_neighbors = entity_event.get(self.QUERY_RESULT, [])
        result = []
        for vertex in graph_neighbors:
            edge = graph_utils.create_edge(
                source_id=self._create_entity_key(entity_event),
                target_id=vertex.vertex_id,
                relationship_type=EdgeLabel.ON)
            result.append(Neighbor(vertex, edge))
        return result

    def _create_merge_alarm_vertex(self, entity_event):
        """Handle an alarm that already has a vitrage_id

        This is a deduced alarm created in aodh by vitrage, so it already
        exists in the graph.
        This function will update the exiting vertex (and not create a new one)
        """
        metadata = {
            AodhProps.DESCRIPTION: entity_event[AodhProps.DESCRIPTION],
            VProps.PROJECT_ID: entity_event[AodhProps.PROJECT_ID],
        }
        sample_timestamp = entity_event[DSProps.SAMPLE_DATE]
        update_timestamp = self._format_update_timestamp(
            AodhTransformer._timestamp(entity_event), sample_timestamp)

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            entity_id=entity_event.get(AodhProps.ALARM_ID),
            entity_category=EntityCategory.ALARM,
            entity_type='vitrage',
            sample_timestamp=sample_timestamp,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _ok_status(self, entity_event):
        return entity_event[AodhProps.STATE] == self.STATUS_OK

    def _create_entity_key(self, entity_event):
        if _is_vitrage_alarm(entity_event):
            return entity_event.get(AodhProps.VITRAGE_ID)

        sync_type = entity_event[DSProps.SYNC_TYPE]
        alarm_name = entity_event[AodhProps.NAME]
        resource_id = entity_event[AodhProps.RESOURCE_ID]
        return (tbase.build_key(self._key_values(sync_type,
                                                 resource_id,
                                                 alarm_name)) if resource_id
                else tbase.build_key(self._key_values(sync_type, alarm_name)))

    @staticmethod
    def _timestamp(entity_event):
        return datetime_utils.change_time_str_format(
            entity_event[AodhProps.TIMESTAMP],
            '%Y-%m-%dT%H:%M:%S.%f',
            tbase.TIMESTAMP_FORMAT)

    @staticmethod
    def get_enrich_query(event):
        affected_resource_id = event.get(AodhProps.RESOURCE_ID, None)
        if not affected_resource_id:
            return None
        return {VProps.ID: affected_resource_id}


def _is_vitrage_alarm(entity_event):
    return entity_event.get(AodhProps.VITRAGE_ID) is not None
