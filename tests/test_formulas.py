from cmd_converter.formulas import inline_formula_markdown, omml_text_to_latex


def test_formula_line_is_display_math():
    assert "$$" in inline_formula_markdown("CR = CI / RI")


def test_omml_tokens_are_normalized():
    assert r"\le" in omml_text_to_latex("x≤y")
