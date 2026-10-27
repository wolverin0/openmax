"""Do not confuse Python credential access with literal published credentials."""
import pytest

from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import content_findings

KEY = 'pass' + 'word'


@pytest.mark.parametrize('text', [
    f'client.connect({KEY}={KEY})',
    f'user, {KEY} = credential()',
    f'client.connect({KEY}={KEY} if condition else "")',
])
def test_python_variable_expressions_are_not_literal_credentials(text):
    assert not content_findings(text.encode())


@pytest.mark.parametrize('text', [
    f'{KEY}=not_a_placeholder_value',
    f'export {KEY}=not_a_placeholder_value',
    f'{KEY}="fixture-sensitive-example"',
    f'client.connect({KEY}="fixture-sensitive-example")',
    f'client.connect({KEY}={KEY} if condition else "fixture-sensitive-example")',
])
def test_literals_and_unquoted_config_values_remain_blocked(text):
    assert content_findings(text.encode())
