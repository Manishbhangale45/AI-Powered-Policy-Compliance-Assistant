from rag.prompt_template import build_prompt


def test_prompt_template_mentions_rules():
    prompt = build_prompt("Source: policy.txt\nPage: 1\nPasswords must be rotated.", "What is the password policy?")
    assert "Answer ONLY using retrieved context." in prompt
    assert "What is the password policy?" in prompt
