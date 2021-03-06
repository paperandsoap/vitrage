# Copyright 2016 - Nokia
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

from oslo_log import log
from six.moves import reduce
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.template import Template
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.base import Result
from vitrage.evaluator.template_validation.error_messages import error_msgs

LOG = log.getLogger(__name__)


RESULT_DESCRIPTION = 'Template content validation'
CORRECT_RESULT_MESSAGE = 'Template content is OK'


def content_validation(template):

    template_definitions = template[TemplateFields.DEFINITIONS]

    entity_ids = []
    entities = template_definitions[TemplateFields.ENTITIES]
    result = validate_entities_definition(entities, entity_ids)

    relationship_ids = []

    if result.is_valid and \
       TemplateFields.RELATIONSHIPS in template_definitions:

        relationships = template_definitions[TemplateFields.RELATIONSHIPS]
        result = validate_relationships_definitions(relationships,
                                                    relationship_ids,
                                                    entity_ids)
    if result.is_valid:
        scenarios = template[TemplateFields.SCENARIOS]
        result = validate_scenarios(scenarios, entity_ids, relationship_ids)

    return result


def validate_entities_definition(entities, entity_ids):

    for entity in entities:

        entity_dict = entity[TemplateFields.ENTITY]
        result = validate_entity_definition(entity_dict, entity_ids)

        if not result.is_valid:
            return result

        entity_ids.append(entity_dict[TemplateFields.TEMPLATE_ID])

    return _get_correct_result()


def validate_entity_definition(entity, entities_ids):

    template_id = entity[TemplateFields.TEMPLATE_ID]
    if template_id in entities_ids:
        LOG.error(error_msgs[2])
        return _get_fault_result(error_msgs[2])

    return _get_correct_result()


def validate_relationships_definitions(relationships,
                                       relationship_ids,
                                       entity_ids):

    for relationship in relationships:

        relationship_dict = relationship[TemplateFields.RELATIONSHIP]
        result = validate_relationship(relationship_dict,
                                       relationship_ids,
                                       entity_ids)
        if not result.is_valid:
            return result

        relationship_ids.append(relationship_dict[TemplateFields.TEMPLATE_ID])
    return _get_correct_result()


def validate_relationship(relationship, relationships_ids, entities_ids):

    template_id = relationship[TemplateFields.TEMPLATE_ID]
    if template_id in (entities_ids or relationships_ids):
        LOG.error(error_msgs[2])
        return _get_fault_result(error_msgs[2])

    target = relationship[TemplateFields.TARGET]
    result = _validate_template_id(entities_ids, target)

    if result.is_valid:
        source = relationship[TemplateFields.SOURCE]
        result = _validate_template_id(entities_ids, source)

    return result


def validate_scenarios(scenarios, entities_id, relationship_ids):

    for scenario in scenarios:

        scenario_values = scenario[TemplateFields.SCENARIO]

        condition = scenario_values[TemplateFields.CONDITION]
        result = validate_scenario_condition(condition, relationship_ids)

        if not result.is_valid:
            return result

        actions = scenario_values[TemplateFields.ACTIONS]
        result = validate_scenario_actions(actions, entities_id)

        if not result.is_valid:
            return result

    return _get_correct_result()


def validate_scenario_condition(condition, template_ids):

    try:
        Template.convert_to_dnf_format(condition)
    except Exception:
        LOG.error(error_msgs[85])
        return _get_fault_result(error_msgs[85])

    values_to_replace = ' and ', ' or ', ' not ', '(', ')'
    condition = reduce(lambda cond, v: cond.replace(v, ' '),
                       values_to_replace,
                       condition)

    for condition_var in condition.split(' '):

        result = _validate_template_id(template_ids, condition_var)
        if not result.is_valid:
            return result

    return _get_correct_result()


def validate_scenario_actions(actions, entities_ids):

    for action in actions:
        result = validate_scenario_action(action[TemplateFields.ACTION],
                                          entities_ids)
        if not result.is_valid:
            return result

    return _get_correct_result()


def validate_scenario_action(action, entities_ids):

    action_type = action[TemplateFields.ACTION_TYPE]

    if action_type == ActionType.RAISE_ALARM:
        return validate_raise_alarm_action(action, entities_ids)
    elif action_type == ActionType.SET_STATE:
        return validate_set_state_action(action, entities_ids)
    elif action_type == ActionType.ADD_CAUSAL_RELATIONSHIP:
        return validate_add_causal_relationship_action(action, entities_ids)
    else:
        LOG.error(error_msgs[120])
        return _get_fault_result(error_msgs[120])


def validate_raise_alarm_action(action, entities_ids):

    properties = action[TemplateFields.PROPERTIES]

    if TemplateFields.ALARM_NAME not in properties:
        LOG.error(error_msgs[125])
        return _get_fault_result(error_msgs[125])

    if TemplateFields.SEVERITY not in properties:
        LOG.error(error_msgs[126])
        return _get_fault_result(error_msgs[126])

    action_target = action[TemplateFields.ACTION_TARGET]
    if TemplateFields.TARGET not in action_target:
        LOG.error(error_msgs[127])
        return _get_fault_result(error_msgs[127])

    target = action_target[TemplateFields.TARGET]
    return _validate_template_id(entities_ids, target)


def validate_set_state_action(action, entities_ids):

    properties = action[TemplateFields.PROPERTIES]

    if TemplateFields.STATE not in properties:
        LOG.error(error_msgs[128])
        return _get_fault_result(error_msgs[128])

    action_target = action[TemplateFields.ACTION_TARGET]
    if TemplateFields.TARGET not in action_target:
        LOG.error(error_msgs[129])
        return _get_fault_result(error_msgs[129])

    target = action_target[TemplateFields.TARGET]
    return _validate_template_id(entities_ids, target)


def validate_add_causal_relationship_action(action, entities_ids):

    action_target = action[TemplateFields.ACTION_TARGET]

    if TemplateFields.TARGET not in action_target:
        LOG.error(error_msgs[130])
        return _get_fault_result(error_msgs[130])

    target = action_target[TemplateFields.TARGET]
    result = _validate_template_id(entities_ids, target)

    if not result.is_valid:
        return result

    if TemplateFields.SOURCE not in action_target:
        LOG.error(error_msgs[130])
        return _get_fault_result(error_msgs[130])

    source = action_target[TemplateFields.SOURCE]
    return _validate_template_id(entities_ids, source)


def _validate_template_id(ids, id_to_check):

    if id_to_check not in ids:
        LOG.error(error_msgs[3])
        return _get_fault_result(error_msgs[3])

    return _get_correct_result()


def _get_correct_result():
    return Result(RESULT_DESCRIPTION, True, 'Template content is OK')


def _get_fault_result(comment):
    return Result(RESULT_DESCRIPTION, False, comment)
