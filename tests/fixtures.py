# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import pytest

from pytermor import RendererManager
from pytermor.config import init_config, replace_config, Config

_default_config = Config()


@pytest.fixture(scope="function", autouse=True)
def config(request):
    """
    Global module config replacement, recreated for each test with
    default values or ones specified by ``setup`` mark:

        >>> @pytest.mark.setup(prefer_rgb=True)
        ... def fn(): pass

    :return: Config
    """
    current_config = _default_config
    setup = request.node.get_closest_marker("setup")

    if setup is not None:
        current_config = Config(**setup.kwargs)

    replace_config(current_config)
    RendererManager.set_default()
    yield current_config
    init_config()
    RendererManager.set_default()
