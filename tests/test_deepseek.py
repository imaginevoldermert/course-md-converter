from cmd_converter.providers import get_provider


def test_deepseek_never_receives_image_formula_requests():
    assert get_provider("deepseek", "not-a-real-key", "https://api.deepseek.com", "deepseek-v4-pro") is None
