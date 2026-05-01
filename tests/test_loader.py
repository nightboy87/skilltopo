from skilltopo.loader import load_skills, validate_skills


def test_load_yaml_skills():
    skills = load_skills("examples/skills")
    names = {s.name for s in skills}
    assert "systematic-debugging" in names
    assert "arxiv-research" in names


def test_validate_examples():
    skills, errors = validate_skills("examples/skills")
    assert skills
    assert errors == []


def test_load_skill_md_frontmatter():
    skills = load_skills("examples/skill-md-example")
    assert skills[0].name == "synthetic-skill-md-example"
    assert "frontmatter" in skills[0].keywords
