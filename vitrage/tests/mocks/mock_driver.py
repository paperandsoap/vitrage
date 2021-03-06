# Copyright 2015 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""Methods for generating driver events

For each type of entity, need to supply configuration files that specify (a
regex of) what can be returned, which will be used to generate driver events

usage example:
    test_entity_spec_list = [
        {mg.DYNAMIC_INFO_FKEY: 'driver_inst_snapshot_dynamic.json',
         mg.STATIC_INFO_FKEY: 'driver_inst_snapshot_static.json',
         mg.MAPPING_KEY: [('vm1', 'host1'), ('vm2', 'host1'), ('vm3','host2')],
         mg.NAME_KEY: 'Instance (vm) generator',
         NUM_EVENTS_KEY: 10
         }
    ]
    spec_list = get_mock_generators(test_entity_spec_list)
    events = generate_random_events_list(spec_list)
    for e in events:
        print e
"""

import random

import vitrage.tests.mocks.trace_generator as tg


def generate_random_events_list(generator_spec_list):
    """Generates random events for the generators given.

     Each element in the list of generators includes a generator and
     number of events to generate for it's entities

     :param generator_spec_list: list of generators
     :type generator_spec_list: list

     :return list of driver events
     :rtype list

    """

    data = []
    for spec in generator_spec_list:
        generator = spec[tg.GENERATOR]
        data += tg.generate_data_stream(generator.models, spec[tg.NUM_EVENTS])
    random.shuffle(data)
    return data


def generate_sequential_events_list(generator_spec_list):
    """Generates random events for the generators given.

     Each element in the list of generators includes a generator and
     number of events to generate for it's entities

     :param generator_spec_list: list of generators
     :type generator_spec_list: list

     :return list of driver events
     :rtype list

    """

    data = []
    for spec in generator_spec_list:
        generator = spec[tg.GENERATOR]
        data += tg.generate_round_robin_data_stream(generator.models,
                                                    spec[tg.NUM_EVENTS])
    return data


def simple_instance_generators(host_num, vm_num,
                               snapshot_events=0, update_events=0,
                               snap_vals=None, update_vals=None):
    """A function for returning vm event generators.

    Returns generators for a given number of hosts and
    instances. Instances will be distributed across hosts in round-robin style.

    :param host_num: number of hosts
    :param vm_num: number of vms
    :param snapshot_events: number of snapshot events per instance
    :param update_events: number of update events per instance
    :param snap_vals: preset vals for ALL snapshot events
    :param update_vals: preset vals for ALL update events
    :return: generators for vm_num vms as specified
    """

    mapping = [('vm-{0}'.format(index), 'host-{0}'.format(index % host_num))
               for index in range(vm_num)
               ]

    test_entity_spec_list = []
    if snapshot_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_INST_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: tg.DRIVER_INST_SNAPSHOT_S,
             tg.EXTERNAL_INFO_KEY: snap_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Instance (vm) snapshot generator',
             tg.NUM_EVENTS: snapshot_events
             }
        )
    if update_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_INST_UPDATE_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: update_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Instance (vm) update generator',
             tg.NUM_EVENTS: update_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_host_generators(zone_num, host_num, snapshot_events=0,
                           snap_vals=None):
    """A function for returning vm event generators.

    Returns generators for a given number of hosts and
    instances. Instances will be distributed across hosts in round-robin style.

    :param zone_num: number of zones
    :param host_num: number of hosts
    :param snapshot_events: number of snapshot events per host
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for host_num hosts as specified
    """

    mapping = [('host-{0}'.format(index), 'zone-{0}'.format(index % zone_num))
               for index in range(host_num)
               ]

    test_entity_spec_list = []
    if snapshot_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_HOST_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: snap_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Host snapshot generator',
             tg.NUM_EVENTS: snapshot_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_zone_generators(zone_num, host_num, snapshot_events=0,
                           snap_vals=None):
    """A function for returning zone event generators.

    Returns generators for a given number of hosts and
    zones. Hosts will be distributed across zones in round-robin style.

    :param zone_num: number of zones
    :param host_num: number of hosts
    :param snapshot_events: number of snapshot events per zone
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for zone_num zones as specified
    """

    mapping = [('host-{0}'.format(index), 'zone-{0}'.format(index % zone_num))
               for index in range(host_num)
               ]

    test_entity_spec_list = []
    if snapshot_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_ZONE_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: snap_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Zone snapshot generator',
             tg.NUM_EVENTS: snapshot_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_volume_generators(volume_num, instance_num,
                             snapshot_events=0, update_events=0,
                             snap_vals=None, update_vals=None):
    """A function for returning vm event generators.

    Returns generators for a given number of volumes and
    instances. Instances will be distributed across hosts in round-robin style.

    :param update_vals:  number of values from update event
    :param update_events: number of events from update event
    :param volume_num: number of volumes
    :param instance_num: number of instances
    :param snapshot_events: number of snapshot events per host
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for volume_num volumes as specified
    """

    mapping = [('volume-{0}'.format(index % volume_num),
                'vm-{0}'.format(index))
               for index in range(instance_num)
               ]

    test_entity_spec_list = []
    if snapshot_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_VOLUME_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: snap_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Volume snapshot generator',
             tg.NUM_EVENTS: snapshot_events
             }
        )
    if update_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_VOLUME_UPDATE_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: update_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Volume update generator',
             tg.NUM_EVENTS: update_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_consistency_generators(consistency_num, update_events=0,
                                  snap_vals=None, update_vals=None):
    """A function for returning consistency event generators.

    Returns generators for a given number of consistency events.
    Instances will be distributed across hosts in round-robin style.

    :param update_vals:  number of values from update event
    :param update_events: number of events from update event
    :param consistency_num: number of consisteny events
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for consistency_num consistency events as specified
    """

    test_entity_spec_list = []
    if update_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_CONSISTENCY_UPDATE_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: update_vals,
             tg.MAPPING_KEY: consistency_num,
             tg.NAME_KEY: 'Consistency update generator',
             tg.NUM_EVENTS: update_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_switch_generators(switch_num, host_num,
                             snapshot_events=0, snap_vals=None,
                             update_events=0, update_vals=None):
    """A function for returning switch event generators.

    Returns generators for a given number of switches and hosts.
    Hosts will be distributed across switches in round-robin style.
    Switches are interconnected in a line.

    :param update_vals:  number of events from update event
    :param update_events: number of values from update event
    :param switch_num: number of zones
    :param host_num: number of hosts
    :param snapshot_events: number of snapshot events per zone
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for zone_num zones as specified
    """

    mapping = [('host-{0}'.format(index), 'switch-{0}'.format(index %
                                                              switch_num))
               for index in range(host_num)
               ]

    test_entity_spec_list = []
    if snapshot_events:
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_SWITCH_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: snap_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Switch snapshot generator',
             tg.NUM_EVENTS: snapshot_events
             }
        )
    if update_events:
        update_vals = {} if not update_vals else update_vals
        update_vals['sync_mode'] = 'update'
        test_entity_spec_list.append(
            {tg.DYNAMIC_INFO_FKEY: tg.DRIVER_SWITCH_SNAPSHOT_D,
             tg.STATIC_INFO_FKEY: None,
             tg.EXTERNAL_INFO_KEY: update_vals,
             tg.MAPPING_KEY: mapping,
             tg.NAME_KEY: 'Switch update generator',
             tg.NUM_EVENTS: update_events
             }
        )
    return tg.get_trace_generators(test_entity_spec_list)


def simple_nagios_alarm_generators(host_num,
                                   events_num=0,
                                   snap_vals=None):
    """A function for returning Nagios alarm event generators.

    Returns generators for a given number of Nagios alarms.

    :param host_num: number of hosts
    :param events_num: number of snapshot alarms per hosts
    :param snap_vals: preset vals for ALL snapshot events
    :return: generators for zone_num zones as specified
    """

    hosts = ['host-{0}'.format(index) for index in range(host_num)]

    test_entity_spec_list = []
    if events_num:
        test_entity_spec_list.append({
            tg.DYNAMIC_INFO_FKEY: tg.DRIVER_NAGIOS_SNAPSHOT_D,
            tg.STATIC_INFO_FKEY: None,
            tg.EXTERNAL_INFO_KEY: snap_vals,
            tg.MAPPING_KEY: hosts,
            tg.NAME_KEY: 'Nagios alarm generator (alarm on)',
            tg.NUM_EVENTS: max(events_num - len(hosts), 0)
        })
        test_entity_spec_list.append({
            tg.DYNAMIC_INFO_FKEY: tg.DRIVER_NAGIOS_SNAPSHOT_D,
            tg.STATIC_INFO_FKEY: tg.DRIVER_NAGIOS_SNAPSHOT_S,
            tg.EXTERNAL_INFO_KEY: snap_vals,
            tg.MAPPING_KEY: hosts,
            tg.NAME_KEY: 'Nagios alarm generator (alarm off)',
            tg.NUM_EVENTS: len(hosts)
        })

    return tg.get_trace_generators(test_entity_spec_list)
