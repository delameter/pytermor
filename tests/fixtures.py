# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import pytest

from pytermor import ExtendedEnum, OutputMode, RendererManager
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
        kwargs = dict()
        for k, v in setup.kwargs.items():
            if isinstance(v, ExtendedEnum):
                v = v.value
            kwargs[k] = v
        current_config = Config(**kwargs)

    replace_config(current_config)
    RendererManager.set_default()
    yield current_config
    init_config()
    RendererManager.set_default()
