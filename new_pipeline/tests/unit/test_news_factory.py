from new_pipeline.adapters.factory import build_news_source
from new_pipeline.adapters.news_static import StaticNewsSource
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.config import get_config


def test_build_news_source_offline_is_static_fixture():
    src = build_news_source(get_config(), StaticUniverseProvider())
    assert isinstance(src, StaticNewsSource)
