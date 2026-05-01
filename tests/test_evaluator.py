from skilltopo.evaluator import evaluate


def test_evaluate_seed_subset():
    result = evaluate("evals/zh_basic.yaml", "examples/skills")
    assert result["metrics"]["total"] == 4
    assert result["metrics"]["accuracy_at_1"] >= 0.75
