# -*- coding: utf-8 -*-
"""
A number of generic default fixtures to use with tests.

All model-related fixtures defined here require the database, and should imply as much by
including ``db`` fixture in the function resolution scope.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import sys
import yaml
import sentry

import pytest
import six

from datetime import datetime


DEFAULT_EVENT_DATA = {
    'extra': {
        'loadavg': [0.97607421875, 0.88330078125, 0.833984375],
        'sys.argv': [
            '/Users/dcramer/.virtualenvs/sentry/bin/raven', 'test',
            'https://ebc35f33e151401f9deac549978bda11:f3403f81e12e4c24942d505f086b2cad@sentry.io/1'
        ],
        'user':
        'dcramer'
    },
    'modules': {
        'raven': '3.1.13'
    },
    'request': {
        'cookies': {},
        'data': {},
        'env': {},
        'headers': {},
        'method': 'GET',
        'query_string': '',
        'url': 'http://example.com',
    },
    'stacktrace': {
        'frames': [
            {
                'abs_path':
                'www/src/sentry/models/foo.py',
                'context_line':
                '                        string_max_length=self.string_max_length)',
                'filename':
                'sentry/models/foo.py',
                'function':
                'build_msg',
                'in_app':
                True,
                'lineno':
                29,
                'module':
                'raven.base',
                'post_context': [
                    '                },', '            })', '',
                    "        if 'stacktrace' in data:",
                    '            if self.include_paths:'
                ],
                'pre_context': [
                    '', '            data.update({',
                    "                'stacktrace': {",
                    "                    'frames': get_stack_info(frames,",
                    '                        list_max_length=self.list_max_length,'
                ],
                'vars': {
                    'culprit': 'raven.scripts.runner',
                    'date': 'datetime.datetime(2013, 2, 14, 20, 6, 33, 479471)',
                    'event_id': '598fb19363e745ec8be665e6ba88b1b2',
                    'event_type': 'raven.events.Message',
                    'frames': '<generator object iter_stack_frames at 0x103fef050>',
                    'handler': '<raven.events.Message object at 0x103feb710>',
                    'k': 'logentry',
                    'public_key': None,
                    'result': {
                        'logentry':
                        "{'message': 'This is a test message generated using ``raven test``', 'params': []}"
                    },
                    'self': '<raven.base.Client object at 0x104397f10>',
                    'stack': True,
                    'tags': None,
                    'time_spent': None,
                },
            },
            {
                'abs_path':
                '/Users/dcramer/.virtualenvs/sentry/lib/python2.7/site-packages/raven/base.py',
                'context_line':
                '                        string_max_length=self.string_max_length)',
                'filename':
                'raven/base.py',
                'function':
                'build_msg',
                'in_app':
                False,
                'lineno':
                290,
                'module':
                'raven.base',
                'post_context': [
                    '                },', '            })', '',
                    "        if 'stacktrace' in data:",
                    '            if self.include_paths:'
                ],
                'pre_context': [
                    '', '            data.update({',
                    "                'stacktrace': {",
                    "                    'frames': get_stack_info(frames,",
                    '                        list_max_length=self.list_max_length,'
                ],
                'vars': {
                    'culprit': 'raven.scripts.runner',
                    'date': 'datetime.datetime(2013, 2, 14, 20, 6, 33, 479471)',
                    'event_id': '598fb19363e745ec8be665e6ba88b1b2',
                    'event_type': 'raven.events.Message',
                    'frames': '<generator object iter_stack_frames at 0x103fef050>',
                    'handler': '<raven.events.Message object at 0x103feb710>',
                    'k': 'logentry',
                    'public_key': None,
                    'result': {
                        'logentry':
                        "{'message': 'This is a test message generated using ``raven test``', 'params': []}"
                    },
                    'self': '<raven.base.Client object at 0x104397f10>',
                    'stack': True,
                    'tags': None,
                    'time_spent': None,
                },
            },
        ],
    },
    'tags': [],
    'platform': 'python',
}


@pytest.mark.django_db
@pytest.fixture
def factories():
    # XXX(dcramer): hack to prevent recursive imports
    from sentry.testutils.factories import Factories

    return Factories


@pytest.mark.django_db
@pytest.fixture
def project(team, factories):
    return factories.create_project(
        name='bar',
        slug='bar',
        teams=[team]
    )


@pytest.fixture
def task_runner():
    from sentry.testutils.helpers.task_runner import TaskRunner
    return TaskRunner


@pytest.fixture(scope='function')
def session():
    return factories.create_session()


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_user(factories):
    return factories.create_user(email='admin@localhost', is_superuser=True)


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_organization(factories, default_user):
    # XXX(dcramer): ensure that your org slug doesnt match your team slug
    # and the same for your project slug
    return factories.create_organization(
        name='baz',
        slug='baz',
        owner=default_user,
    )


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_team(factories, default_organization):
    from sentry.models import OrganizationMember, OrganizationMemberTeam

    team = factories.create_team(
        organization=default_organization,
        name='foo',
        slug='foo',
    )
    # XXX: handle legacy team fixture
    queryset = OrganizationMember.objects.filter(
        organization=default_organization,
    )
    for om in queryset:
        OrganizationMemberTeam.objects.create(
            team=team,
            organizationmember=om,
            is_active=True,
        )
    return team


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_project(factories, default_team):
    return factories.create_project(
        name='Bar',
        slug='bar',
        teams=[default_team],
    )


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_projectkey(factories, default_project):
    return factories.create_project_key(project=default_project)


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_environment(factories, default_project):
    return factories.create_environment(
        name='development',
        project=default_project,
    )


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_group(factories, default_project):
    return factories.create_group(
        project=default_project,
        message=u'\u3053\u3093\u306b\u3061\u306f',
    )


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_event(factories, default_group):
    return factories.create_event(
        group=default_group,
        event_id='a' * 32,
        message=u'\u3053\u3093\u306b\u3061\u306f',
    )


@pytest.mark.django_db
@pytest.fixture(scope='function')
def default_activity(default_group, default_project, default_user):
    from sentry.models import Activity

    return Activity.objects.create(
        group=default_group, project=default_project, type=Activity.NOTE, user=default_user, data={}
    )


_snapshot_writeback = os.environ.get("SENTRY_SNAPSHOTS_WRITEBACK") or '0'
if _snapshot_writeback in ('true', '1', 'overwrite'):
    _snapshot_writeback = 'overwrite'
elif _snapshot_writeback != 'new':
    _snapshot_writeback = None
_test_base = os.path.realpath(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(sentry.__file__)))))
_yaml_snap_re = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$(?s)')


@pytest.fixture
def log():
    def inner(x):
        return sys.stdout.write(x + '\n')
    return inner


class ReadableYamlDumper(yaml.dumper.SafeDumper):
    """Disable pyyaml aliases for identical object references"""

    def ignore_aliases(self, data):
        return True


@pytest.fixture
def insta_snapshot(request, log):
    def inner(output, reference_file=None, subname=None):
        if reference_file is None:
            name = request.node.name
            for c in ('::', '-', '[', ']'):
                name = name.replace(c, '/')
            name = name.strip('/')

            reference_file = os.path.join(
                os.path.dirname(six.text_type(request.node.fspath)),
                'snapshots',
                os.path.splitext(os.path.basename(request.node.parent.name))[0],
                name + '.pysnap'

            )
        elif subname is not None:
            raise ValueError(
                "subname only works if you don't provide your own entire reference_file")

        if not isinstance(output, six.string_types):
            output = yaml.dump(
                output,
                indent=2,
                default_flow_style=False,
                Dumper=ReadableYamlDumper)

        try:
            with open(reference_file) as f:
                match = _yaml_snap_re.match(f.read().decode('utf-8'))
                if match is None:
                    raise IOError()
                _header, refval = match.groups()
        except IOError:
            refval = ''

        refval = refval.rstrip()
        output = output.rstrip()

        if _snapshot_writeback is not None and refval != output:
            if not os.path.isdir(os.path.dirname(reference_file)):
                os.makedirs(os.path.dirname(reference_file))
            source = os.path.realpath(six.text_type(request.node.fspath))
            if source.startswith(_test_base + os.path.sep):
                source = source[len(_test_base) + 1:]
            if _snapshot_writeback == 'new':
                reference_file += '.new'
            with open(reference_file, "w") as f:
                f.write('---\n%s\n---\n%s\n' % (yaml.safe_dump({
                    'created': datetime.utcnow().isoformat() + 'Z',
                    'creator': 'sentry',
                    'source': source,
                }, indent=2, default_flow_style=False).rstrip(), output))
        else:
            log("Run with SENTRY_SNAPSHOTS_WRITEBACK=1 to update snapshots.")
            assert refval == output

    yield inner
