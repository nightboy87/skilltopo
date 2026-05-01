from skilltopo.loader import load_skills
from skilltopo.router import SkillRouter


def test_keyword_recommend_debugging():
    skills = load_skills("examples/skills")
    result = SkillRouter(skills).recommend("代码崩了", top_k=3)
    assert result.recommendations[0].skill == "systematic-debugging"
    assert "崩了" in result.recommendations[0].matched_terms


def test_negative_query_returns_none():
    skills = load_skills("examples/skills")
    result = SkillRouter(skills).recommend("帮我订外卖", top_k=3)
    assert result.recommendations == []
    assert result.no_match_reason == "global_negative_keyword_matched"


def test_arxiv_query():
    skills = load_skills("examples/skills")
    result = SkillRouter(skills).recommend("找一篇论文", top_k=3)
    assert result.recommendations[0].skill == "arxiv-research"


def test_workflow_recommend():
    skills = load_skills("examples/skills")
    result = SkillRouter(skills).workflow_recommend("读一篇论文并整理成知识卡片", top_k=3)
    chains = [r["chain"] for r in result["workflow_recommendations"]]
    assert any("arxiv-research" in chain for chain in chains)
