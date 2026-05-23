"""Pytest-обёртка над ADK Evaluation.

Запуск:
    cd checkpoints/09_evaluation
    pytest -v my_first_agent/tests/test_agent.py
"""

import pathlib

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


HERE = pathlib.Path(__file__).parent


@pytest.mark.asyncio
async def test_basic_evalset() -> None:
    """Прогоняет basic.evalset.json и проверяет пороги из test_config.json."""
    await AgentEvaluator.evaluate(
        agent_module="my_first_agent",
        eval_dataset_file_path_or_dir=str(HERE / "basic.evalset.json"),
    )
