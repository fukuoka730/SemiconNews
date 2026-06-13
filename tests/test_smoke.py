def test_imports_work():
    import config
    import src.collector  # noqa: F401
    assert hasattr(config, "RSS_FEEDS")
