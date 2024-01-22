# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import itertools
import typing as t
from collections.abc import Iterable
from copy import copy
from dataclasses import dataclass
from typing import overload

import pytest

xfail = pytest.mark.xfail

from pytermor import (
    HSV,
    LAB,
    RGB,
    XYZ,
    IColorValue,
    Style,
    make_color_256,
    Text,
    OutputMode,
    render,
    RealColor,
    DynamicColor,
    FrozenStyle,
)
from pytermor import (
    NOOP_SEQ,
    SequenceSGR,
    IntCode,
    color,
    resolve_color,
    DEFAULT_COLOR,
    NOOP_COLOR,
    Color16,
    Color256,
    ColorRGB,
    Color,
    approximate,
    ColorTarget,
)
from pytermor.color import (
    _ColorRegistry,
    _ColorIndex,
    _ConstrainedValue,
)
from pytermor.cval import cv
from pytermor.exception import LogicError, ColorNameConflictError, ColorCodeConflictError
from tests import assert_close, format_test_params, skip_pre_310_typing

NON_EXISTING_COLORS = [0xFEDCBA, 0xFA0CCC, *range(1, 7)]


def format_test_params_ext(value) -> str | None:
    if isinstance(value, (ValueSet, DiffSet)):
        return str(value)
    return format_test_params(value)


@dataclass(frozen=True)
class ValueSet:
    int: RGB
    rgb: RGB
    hsv: HSV
    xyz: XYZ
    lab: LAB
    expect_match: bool = True

    def __str__(self):
        return f"{self.rgb!r}-{self.expect_match}"


@dataclass(frozen=True)
class DiffSet:
    col_a: IColorValue
    col_b: IColorValue
    rgb: float
    hsv: float
    lab: float
    xyz: None = None

    def __str__(self):
        return "-".join(
            [repr(self.col_a), repr(self.col_b)] + [f"D{k}={getattr(self, k)}" for k in SPACES]
        )


# fmt: off
VALUES = [     # ___hex___                    _r_  _g_  _b_        __h__ __s__ __v__        __x__   __y__   __z__        __l__    __a__    __b__     # noqa
    ValueSet(RGB(0x000000), RGB.from_channels(  0,   0,   0), HSV(  0.00, 0.00, 0.00), XYZ(  0.00,   0.00,   0.00), LAB(  0.00,    0.00,    0.00)),  # noqa
    ValueSet(RGB(0xFFFFFF), RGB.from_channels(255, 255, 255), HSV(  0.00, 0.00, 1.00), XYZ( 95.05,  100.0, 108.88), LAB( 100.0, 0.00526, 0.00184)),  # noqa
    ValueSet(RGB(0xFF0000), RGB.from_channels(255,   0,   0), HSV(  0.00, 1.00, 1.00), XYZ( 41.24,  21.26,  1.930), LAB(53.232,  80.109,   67.22)),  # noqa
    ValueSet(RGB(0x00FF00), RGB.from_channels(  0, 255,   0), HSV( 120.0, 1.00, 1.00), XYZ( 35.76,  71.52,  11.92), LAB(87.737, -86.184,  83.181)),  # noqa
    ValueSet(RGB(0x0000FF), RGB.from_channels(  0,   0, 255), HSV( 240.0, 1.00, 1.00), XYZ( 18.05,   7.22,  95.03), LAB(32.302,  79.197, -107.85)),  # noqa
    ValueSet(RGB(0x100000), RGB.from_channels( 16,   0,   0), HSV(  0.00, 1.00, 1/16), XYZ(0.2137,   0.11,   0.01), LAB( 0.995,   4.464,  1.5726)),  # noqa
    ValueSet(RGB(0xc02040), RGB.from_channels(192,  32,  64), HSV( 348.0,  5/6,  3/4), XYZ(23.180,  12.61,  6.062), LAB(42.169,   61.66,  23.924)),  # noqa
    ValueSet(RGB(0x00ff80), RGB.from_channels(  0, 255, 128), HSV(150.11, 1.00, 1.00), XYZ(39.656,  73.08,  32.43), LAB(88.485, -76.749,  46.577)),  # noqa
    ValueSet(RGB(0x000080), RGB.from_channels(  0,   0, 128), HSV( 240.0, 1.00,  1/2), XYZ( 3.896,  1.558,  20.51), LAB(12.975,  47.508, -64.704)),  # noqa
    ValueSet(RGB(0xffccab), RGB.from_channels(255, 204, 171), HSV( 23.57,  1/3, 1.00), XYZ(70.183,  67.39,  47.83), LAB(85.698,  13.572,  23.309)),  # noqa
    ValueSet(RGB(0x406080), RGB.from_channels( 64,  96, 128), HSV( 210.0,  1/2,  1/2), XYZ(10.194, 11.014,  22.01), LAB(39.601, -2.1089, -21.501)),  # noqa
    ValueSet(RGB(0x20181c), RGB.from_channels( 32,  24,  28), HSV( 330.0,  1/4,  1/8), XYZ(1.1319, 1.0442, 1.2403), LAB(9.3542,  4.8953,  -1.286)),  # noqa
    ValueSet(RGB(0x2d0a50), RGB.from_channels( 45,  10,  80), HSV( 270.0,  7/8, 5/16), XYZ(2.6387, 1.3542, 7.7101), LAB(11.649, 32.2209, -35.072)),  # noqa
    ValueSet(RGB(0x102030), RGB.from_channels( 50,  60,  70), HSV(  80.0, 9/10, 1.00), XYZ(  50.0,   50.0,   50.0), LAB(  50.0,   -50.0,   -50.0), False)  # noqa
]

SPACES = ["rgb", "hsv", "xyz", "lab"]

DIFFS = [
    DiffSet(RGB(   0x000001),  RGB(  0x000002),   1.00, 0.004,   0.40),   # noqa
    DiffSet(RGB(   0x000001),  RGB(  0xFFFFFF), 441.09, 1.561,  99.98),   # noqa
    DiffSet(RGB(   0xFF0000),  RGB(  0xFFFFFF), 360.63, 1.000, 114.55),   # noqa
    DiffSet(RGB(   0xFF00FF),  RGB(  0x00FF00), 441.68, 1.000, 235.60),   # noqa
    DiffSet(RGB(   0x808080),  RGB(  0x828282),   3.46, 0.008,   0.78),   # noqa
    DiffSet(RGB(   0x808080),  RGB(  0x888080),   8.00, 0.067,   3.28),   # noqa
    DiffSet(RGB(   0x808080),  RGB(  0x887070),  24.00, 0.179,  10.87),   # noqa
    DiffSet(RGB(   0xf0c0da),  RGB(  0xe0d089),  84.10, 0.494,  50.70),   # noqa
    DiffSet(HSV(240, 1,  1 ),  HSV( 60, 1, 1 ), 441.67, 1.000, 235.15),   # noqa
    DiffSet(HSV(  0, .5, 1 ),  HSV(  0, 1, 1 ), 181.02, 0.500,  56.79),   # noqa
    DiffSet(HSV( 90, 1,  1 ),  HSV( 90, 1, .5), 142.21, 0.500,  61.19),   # noqa
    DiffSet(HSV(270, 1,  1 ),  HSV(270, 1, .5), 142.21, 0.500,  55.12),   # noqa
    DiffSet(HSV(270, .5, 1 ),  HSV(270, .5,.5), 171.59, 0.500,  44.21),   # noqa
    DiffSet(HSV(  0, 0,  0 ),  HSV(  0, 1, 1 ), 255.00, 1.414, 117.34),   # noqa
    DiffSet(HSV(  0, 0,  0 ),  HSV(180, 1, 1 ), 360.62, 1.732, 103.99),   # noqa
    DiffSet(HSV(180, 0,  0 ),  HSV(180, 1, 1 ), 360.62, 1.414, 103.99),   # noqa
    DiffSet(HSV(  0, 1,  0 ),  HSV(180, 1, 1 ), 360.62, 1.414, 103.99),   # noqa
    DiffSet(HSV(  0, 0,  1 ),  HSV(180, 1, 1 ), 255.00, 1.414,  50.90),   # noqa
    DiffSet(HSV(  0, 1,  1 ),  HSV(180, 1, 1 ), 441.68, 1.000, 156.47),   # noqa
    DiffSet(HSV( 60, 0,  0 ),  HSV(240, 1, 1 ), 255.00, 1.732, 137.65),   # noqa
    DiffSet(HSV(120, 0,  0 ),  HSV(300, 1, 1 ), 360.62, 1.732, 130.35),   # noqa
    DiffSet(HSV(180, 0,  0 ),  HSV(360, 1, 1 ), 255.00, 1.732, 117.34),   # noqa
    DiffSet(HSV( 60, 0,  .5),  HSV(240, 1, .5), 181.02, 1.410,  89.95),   # noqa
    DiffSet(HSV(120, 0,  .5),  HSV(300, 1, .5), 128.00, 1.410,  73.30),   # noqa
    DiffSet(HSV(180, 0,  .5),  HSV(360, 1, .5), 181.02, 1.410,  67.41),   # noqa
    DiffSet(HSV( 60, 1,  .5),  HSV(240, 1, .5), 221.70, 1.000, 141.05),   # noqa
    DiffSet(HSV(120, 1,  .5),  HSV(300, 1, .5), 221.70, 1.000, 141.33),   # noqa
    DiffSet(HSV(180, 1,  .5),  HSV(360, 1, .5), 221.70, 1.000,  92.70),   # noqa
    DiffSet(LAB( 50, 50, 50),  LAB(50,-50,-50), 222.78, 1.168, 141.42),   # noqa
]
# fmt: on


@pytest.mark.skip("it's just too complicated to mock all this. @TODO refactor")
class TestDeferredLoading:
    def test_presets_are_not_loaded_initially(self):
        assert len(ColorRGB._registry) == 0

    def test_presets_are_loaded_at_access(self):
        assert len(ColorRGB._registry) == 0
        assert ColorRGB.find_by_name("red-bronze").int == 0xFB8136
        assert len(ColorRGB._registry) > 0


class TestColorValue:
    @pytest.mark.parametrize(
        "col",
        [
            RGB(0x440044),
            HSV(100, 0.5, 1.0),
            LAB(0.9, 4.4, 83.2),
            XYZ(0.2, 7.2, 32.4),
        ],
        ids=format_test_params,
    )
    def test_to_str(self, col: t.Type[IColorValue]):
        col_str = str(col)
        assert str(col.__class__.__name__) in col_str
        assert col_str.count("=") == 3

    @pytest.mark.parametrize(
        "cls, values",
        [
            (RGB, (-10,)),
            (RGB, (2220,)),
            (RGB.from_channels, (-10, 400, 1e-9)),
            (HSV, (-10, 400, 1e9)),
            (XYZ, (-10, 400, 1e9)),
            (LAB, (-10, 400, 1e9)),
        ],
        ids=format_test_params,
    )
    def test_applying_thresholds(self, cls, values: Iterable[int | float]):
        col = cls(*values)
        assert 0 <= col.int <= 0xFFFFFF

    @pytest.mark.xfail(raises=ValueError)
    def test_invalid_constraint(self):
        _ConstrainedValue[int](50, 100, 0)

    @pytest.mark.parametrize("diffset", DIFFS, ids=format_test_params_ext)
    @pytest.mark.parametrize("space", SPACES, ids=format_test_params)
    def test_diff(self, space: str, diffset: DiffSet):
        cls = getattr(diffset.col_a, space).__class__
        if (expected := getattr(diffset, space)) is None:
            pytest.skip("Not implemented")
        actual = cls.diff(diffset.col_a, diffset.col_b)
        assert_close(actual, expected)

    @pytest.mark.parametrize("val", [0x0, 0x808080, 0xFFFFFF], ids=format_test_params)
    @pytest.mark.parametrize(
        "fn",
        [
            lambda v: RGB(v),
            lambda v: HSV(*RGB(v).hsv),
            lambda v: XYZ(*RGB(v).xyz),
            lambda v: LAB(*RGB(v).lab),
        ],
        ids=format_test_params,
    )
    def test_equality(self, fn: t.Callable[[int], IColorValue], val: int):
        assert fn(val) == fn(val)


class TestColorTransform:
    @pytest.mark.parametrize("value", VALUES, ids=format_test_params_ext)
    @pytest.mark.parametrize(
        "s_from, s_to", itertools.product(SPACES, SPACES), ids=format_test_params
    )
    def test_transforms(self, value: ValueSet, s_from: str, s_to: str):
        if not value.expect_match and s_from == s_to:
            pytest.skip("Control self-transform makes no sense")

        src = getattr(value, s_from)
        dest = getattr(value, s_to)
        assert type(src).__name__.lower() == s_from
        assert type(dest).__name__.lower() == s_to

        result = getattr(src, s_to)
        assert type(result).__name__.lower() == s_to

        if value.expect_match:
            assert_close(dest, result)
        else:
            assert dest != result

    def test_rgb_from_ratios(self):
        assert_close(RGB.from_ratios(0, 0.5, 1.0), RGB.from_channels(0, 128, 255))


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("value", NON_EXISTING_COLORS, ids=format_test_params)
def test_non_existing_colors_do_not_exist(value: int):
    assert approximate(value)[0].color.int != value


class TestResolving:
    def setup_method(self):
        Color256._approximator.invalidate_cache()

    def test_module_method_resolve_works(self):
        assert ColorRGB(0xFFFFCB) == resolve_color("ivory")

    def test_module_method_resolve_alias_works(self):
        assert ColorRGB(0x0052CC) == resolve_color("jira-blue")

    def test_module_method_resolve_full_rgb_form_works(self):
        assert ColorRGB(0xFFD000) == resolve_color("#ffd000")

    def test_module_method_resolve_short_rgb_form_works(self):
        assert ColorRGB(0x3399FF) == resolve_color("#39f")

    def test_module_method_resolve_integer_rgb_form_works(self):
        assert ColorRGB(0x00039F) == resolve_color(0x39F)

    @pytest.mark.skip("RGB is not indexed anymore")
    def test_module_method_resolve_rgb_form_works_with_instantiating(self):
        NON_EXISTING_COLOR = 0xFEDCBA
        assert NON_EXISTING_COLOR not in [c.int for c in ColorRGB._registry._map.values()]
        col1 = resolve_color(NON_EXISTING_COLOR)
        col2 = resolve_color(f"#{NON_EXISTING_COLOR:06x}")
        assert col1 == col2
        assert col1 is not col2
        assert ColorRGB.find_closest(NON_EXISTING_COLOR).int != NON_EXISTING_COLOR

    @pytest.mark.skip("RGB is not indexed anymore")
    def test_module_method_resolve_rgb_form_works_upon_color_rgb(self):
        assert ColorRGB.find_by_name("wash-me") == resolve_color("#fafafe", ColorRGB)

    def test_module_method_resolve_rgb_form_works_upon_color_256(self):
        assert cv.GREEN_5 == resolve_color("#118800", Color256)

    def test_module_method_resolve_rgb_form_works_upon_color_16(self):
        assert cv.BLUE == resolve_color("#111488", Color16)

    @pytest.mark.xfail(raises=LookupError)
    def test_module_method_resolve_of_non_existing_color_fails(self):
        resolve_color("non-existing-color")

    def test_module_method_resolve_ambiguous_color_works_upon_abstract_color(self):
        col = resolve_color("green")
        assert col.int == 0x008000
        assert isinstance(col, Color16)

    def test_module_method_resolve_ambiguous_color_works_upon_color_16(self):
        col = resolve_color("green", Color16)
        assert col.int == 0x008000
        assert isinstance(col, Color16)

    def test_module_method_resolve_ambiguous_color_works_upon_color_256(self):
        col = resolve_color("green", Color256)
        assert col.int == 0x008000
        assert isinstance(col, Color256)

    def test_module_method_resolve_ambiguous_color_works_upon_color_rgb(self):
        col = resolve_color("green", ColorRGB)
        assert col.int == 0x15B01A
        assert isinstance(col, ColorRGB)

    def test_module_method_resolve_invalid_type_works_as_rgb(self):
        col = resolve_color(0x11111, str)  # noqa
        assert col.int == 0x11111
        assert isinstance(col, ColorRGB)

    def test_param_enables_cache(self):
        NEW_COLOR = 0xFA0CCC
        assert NEW_COLOR not in Color256._approximator._cache.keys()
        resolve_color(NEW_COLOR, Color256, approx_cache=True)
        assert NEW_COLOR in Color256._approximator._cache.keys()

    def test_param_disables_cache(self):
        NEW_COLOR = 0xFA0CCC
        assert NEW_COLOR not in Color256._approximator._cache.keys()
        resolve_color(NEW_COLOR, Color256, approx_cache=False)
        assert NEW_COLOR not in Color256._approximator._cache.keys()

    @pytest.mark.parametrize(
        "ctype, expected_text",
        [
            (Color16, "Color16"),
            (Color256, "Color256"),
            (ColorRGB, "ColorRGB"),
            (None, "any"),
        ],
        ids=format_test_params,
    )
    def test_exception_message(self, ctype: t.Type[Color], expected_text: str):
        try:
            non_existing_value = -1
            if not ctype:
                non_existing_value = 0x000001
            resolve_color(non_existing_value, ctype)
        except LookupError as e:
            assert expected_text in str(e)

    def test_resolving_works(self):
        assert ColorRGB.find_by_name("atomic tangerine")

    def test_resolving_by_kebab_cased_name(self):
        assert ColorRGB.find_by_name("atomic-tangerine")

    def test_resolving_by_snake_cased_name(self):
        assert ColorRGB.find_by_name("air_superiority_blue")

    def test_resolving_by_screaming_cased_name(self):
        assert ColorRGB.find_by_name("AIR_SUPERIORITY_BLUE")

    def test_resolving_by_camel_cased_name(self):
        assert ColorRGB.find_by_name("celestialBlue")

    def test_resolving_by_pascal_cased_name(self):
        assert ColorRGB.find_by_name("CelestialBlue")

    @pytest.mark.parametrize(
        "name",
        ["icathian YELLOW", "Icathian-Yellow", "AIR superiority-blue"],
        ids=format_test_params,
    )
    def test_resolving_by_mixed_name(self, name):
        assert ColorRGB.find_by_name("icathian YELLOW")


class TestColorRegistry:
    # @TEMP? The problem: reimporting the CVAL class that recreates colors and
    #        thus registry results in making completely new classes that don't
    #        pass instance checks in the tests code (because python thinks the
    #        old ones and the new ones are completely unrelated).
    # Current approach is to clone the original registry in the setup method,
    # and clone the clone back before every test, as that effectively reverts
    # any changes the tests possibly did to it. After the tests have been run
    # restore the origin and clear the reference. It works OK but I feel that
    # there should be more optimal way to do the same.

    _keeper_registry: _ColorRegistry | None = None

    @classmethod
    def setup_class(cls):
        cls._keeper_registry = copy(ColorRGB._registry)
        cls._keeper_registry._map = copy(ColorRGB._registry._map)
        cls._keeper_registry._set = copy(ColorRGB._registry._set)

    @classmethod
    def teardown_class(cls):
        ColorRGB._registry = cls._keeper_registry
        cls._keeper_registry = None

    def setup_method(self):
        ColorRGB._registry._map = copy(self._keeper_registry._map)
        ColorRGB._registry._set = copy(self._keeper_registry._set)

    def test_registering_works(self):
        map_length_start = len(ColorRGB._registry)
        col = ColorRGB(0x2, "test 2", register=True)

        # one for original name, one for tokens
        assert map_length_start + 2 == len(ColorRGB._registry)
        assert col is resolve_color("test 2", ColorRGB)

    def test_registering_of_duplicate_doesnt_change_map_length(self):
        ColorRGB(0x3, "test 3", register=True)
        map_length_start = len(ColorRGB._registry)
        ColorRGB(0x3, "test 3", register=True)

        assert map_length_start == len(ColorRGB._registry)

    @pytest.mark.xfail(raises=ColorNameConflictError)
    def test_registering_of_name_duplicate_fails(self):
        ColorRGB(0x4, "test 4", register=True)
        ColorRGB(0x3, "test 4", register=True)

    def test_registering_of_indirect_name_duplicate_works(self):
        col1 = ColorRGB(0x4, "test+4b", register=True)
        col2 = ColorRGB(0x3, "test 4b", register=True)
        assert col1 is resolve_color("test+4b", ColorRGB)
        assert col2 is resolve_color("test 4b", ColorRGB)
        assert col1 is resolve_color("test-4b", ColorRGB)

    def test_registering_of_variation_works(self):
        col = ColorRGB(0x5, "test 5", variation_map={0x2: "2"}, register=True)

        assert len(col.variations) == 1
        vari = col.variations.get("2")

        assert vari.base is col
        assert vari.name == "2"
        assert vari is resolve_color("test 5 2", ColorRGB)

    def test_creating_color_without_name_works(self):
        col = Color256(0x6, code=256, register=True)
        assert col.name is None

    def test_registry_length(self):
        assert len(ColorRGB._registry) == len(ColorRGB._registry._map)

    def test_registry_casts_to_true_if_has_elements(self):
        ColorRGB.approximate(0)
        assert bool(ColorRGB._registry)

    def test_registry_casts_to_false_if_empty(self):
        assert not bool(_ColorRegistry())

    def test_iterating(self):
        assert len([*ColorRGB._registry]) == len(ColorRGB._registry._set)

    def test_names(self):
        assert len([*ColorRGB._registry.names()]) == len(ColorRGB._registry._map)

    def test_name_with_prohibited_chars_can_be_resolved_directly(self):
        col = ColorRGB(0x9, "test#A", register=True)
        assert ("test#A",) in ColorRGB._registry.names()
        assert col is resolve_color("test#a", ColorRGB)

    def test_name_with_prohibited_chars_can_be_resolved_by_tokens(self):
        col = ColorRGB(0x10, "test#B", register=True)
        assert ("test", "b") in ColorRGB._registry.names()
        assert col is resolve_color("test-b", ColorRGB)

    @pytest.mark.xfail(raises=LookupError)
    def test_unnamed_color_cant_be_resolved(self):
        ColorRGB(0x11, None, register=True)
        resolve_color("", ColorRGB)


class TestColorIndex:
    _keeper_index: _ColorIndex | None = None

    @classmethod
    def setup_class(cls):
        cls._keeper_index = copy(ColorRGB._index)
        cls._keeper_index._map = copy(ColorRGB._index._map)

    @classmethod
    def teardown_class(cls):
        ColorRGB._index = cls._keeper_index
        cls._keeper_index = None

    def setup_method(self):
        ColorRGB._index._map = copy(self._keeper_index._map)

    def test_adding_to_index_works(self):
        col = Color256(0x1, 257, "test 1", approx=True)
        assert col is Color256.find_closest(0x1)

    def test_adding_duplicate_to_index_doesnt_change_index_length(self):
        Color16(0x1, 131, 141, "test 1")
        index_length_start = len(Color16._index)
        Color16(0x1, 131, 141, "test 1")

        assert index_length_start == len(Color16._index)

    @pytest.mark.xfail(raises=ColorCodeConflictError)
    def test_adding_code_duplicate_to_index_fails(self):
        Color16(0x1, 131, 141, "test 1")
        Color16(0x2, 131, 141, "test 1")

    @pytest.mark.parametrize("cls", [Color16, Color256])
    @pytest.mark.xfail(raises=LookupError)
    def test_getting_of_non_existing_color_fails(self, cls: t.Type[Color16 | Color256]):
        cls.get_by_code(256000)

    def test_index_casts_to_true_if_not_empty(self):
        assert len(Color256._index) > 0
        assert bool(Color256._index)

    def test_index_casts_to_false_if_empty(self):
        assert not bool(_ColorRegistry())


class TestApproximation:
    def test_module_method_find_closest_works_as_256_by_default(self):
        assert color.find_closest(0x87FFD7) == cv.AQUAMARINE_1

    def test_module_method_find_closest_works_for_16(self):
        assert color.find_closest(0x87FFD7, Color16) == cv.HI_CYAN

    def test_module_method_find_closest_works_for_rgb(self):
        assert resolve_color("light-aqua", ColorRGB) == color.find_closest(0x87FFD7, ColorRGB)

    def test_module_method_approximate_works_as_256_by_default(self):
        assert color.approximate(0x87FFD7)[0].color == cv.AQUAMARINE_1

    def test_module_method_approximate_works_for_16(self):
        assert color.approximate(0x87FFD7, Color16)[0].color == cv.HI_CYAN

    def test_module_method_approximate_works_for_rgb(self):
        assert (
            resolve_color("light-aqua", ColorRGB) == color.approximate(0x87FFD7, ColorRGB)[0].color
        )

    def test_class_method_find_closest_works_for_16(self):
        assert Color16.find_closest(0x87FFD7) == cv.HI_CYAN

    def test_class_method_find_closest_works_for_256(self):
        assert Color256.find_closest(0x87FFD7) == cv.AQUAMARINE_1

    def test_class_method_find_closest_works_for_rgb(self):
        assert 0x8CFFDB == ColorRGB.find_closest(0x87FFD7).int

    def test_class_method_approximate_works_for_16(self):
        assert Color16.approximate(0x87FFD7)[0].color == cv.HI_CYAN

    def test_class_method_approximate_works_for_256(self):
        assert Color256.approximate(0x87FFD7)[0].color == cv.AQUAMARINE_1

    def test_class_method_approximate_works_for_rgb(self):
        assert ColorRGB.approximate(ColorRGB(0x87FFD7, approx=True))[0].color.int == 0x87FFD7

    def test_distance_is_correct(self):
        expected = [
            color.ApxResult(cv.NAVAJO_WHITE_1, 4.394),
            color.ApxResult(cv.MISTY_ROSE_1, 14.25),
            color.ApxResult(cv.WHEAT_1, 16.344),
            color.ApxResult(cv.LIGHT_YELLOW_3, 16.58),
            color.ApxResult(cv.CORNSILK_1, 17.39),
        ]
        result = color.approximate(0xFEDCBA, Color256, len(expected))
        assert len(result) == len(expected)
        while result:
            assert_close(result.pop(0).distance, expected.pop(0).distance)

    def test_approximation_ignores_colors256_with_16_equivs(self):
        assert Color256.get_by_code(1).int == 0x800000  # not accessible by cv constant
        assert Color256.find_closest(0x800000).int != 0x800000

    @pytest.mark.parametrize(
        "space, expected",
        ids=format_test_params,
        argvalues=[
            (RGB, 0x4C9085),
            (HSV, 0x5DA493),
            (XYZ, 0x6D9A79),
            (LAB, 0x3D9973),
        ],
    )
    def test_different_spaces(self, space: t.Type[IColorValue], expected: int):
        ColorRGB._approximator.assign_space(space)
        assert color.find_closest(0x50A080, ColorRGB).rgb == expected


@pytest.mark.parametrize("ctype", [Color16, Color256], ids=format_test_params)
class TestColor:
    def test_iterating(self, ctype: t.Type[Color]):
        assert all(isinstance(c, ctype) for c in [*iter(ctype)])

    def test_names(self, ctype: t.Type[Color]):
        assert len([*ctype.names()]) == len([*ctype._registry.names()])


class TestColor16:
    def test_get_code(self):
        col = Color16(0xF00000, 200 + IntCode.RED, 200 + IntCode.BG_RED)
        assert col.code_fg == 200 + IntCode.RED
        assert col.code_bg == 200 + IntCode.BG_RED

    @pytest.mark.parametrize(
        "upper_bound, target, expected_result, msg",
        map(lambda p: (p+[None])[:4], [
            [None, ColorTarget.FG, SequenceSGR(31)],
            [None, ColorTarget.BG, SequenceSGR(41)],
            [None, ColorTarget.UNDERLINE, NOOP_SEQ],
            [ColorRGB, ColorTarget.FG, SequenceSGR(31)],
            [ColorRGB, ColorTarget.BG, SequenceSGR(41)],
            [
                ColorRGB,
                ColorTarget.UNDERLINE,
                SequenceSGR(58, 5, 88),
                "should be 256 because prefer_rgb is False by default",
            ],
            [Color256, ColorTarget.FG, SequenceSGR(31)],
            [Color256, ColorTarget.BG, SequenceSGR(41)],
            [Color256, ColorTarget.UNDERLINE, SequenceSGR(58, 5, 88)],
            [Color16, ColorTarget.FG, SequenceSGR(31)],
            [Color16, ColorTarget.BG, SequenceSGR(41)],
            [Color16, ColorTarget.UNDERLINE, NOOP_SEQ],
        ]),
    )
    def test_to_sgr(
        self,
        upper_bound: type[Color] | None,
        target: ColorTarget,
        expected_result: str | None,
        msg: str,
    ):
        c = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert c.to_sgr(target, upper_bound) == expected_result, msg

    @pytest.mark.parametrize(
        "upper_bound, target, expected_result, msg",
        [
            (
                ColorRGB,
                ColorTarget.UNDERLINE,
                SequenceSGR(58, 2, 135, 0, 0),
                "should be RGB because of configuration param",
            ),
            (
                Color256,
                ColorTarget.UNDERLINE,
                SequenceSGR(58, 5, 88),
                "should be 256 because of restriction",
            ),
            (
                Color16,
                ColorTarget.UNDERLINE,
                NOOP_SEQ,
                "should be NOOP because no such SGR exists",
            ),
        ],
    )
    @pytest.mark.config(prefer_rgb=True)
    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_rgb_if_preferred(
        self,
        upper_bound: type[Color] | None,
        target: ColorTarget,
        expected_result: str | None,
        msg: str,
    ):
        c = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert c.to_sgr(target, upper_bound) == expected_result, msg

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, "ultrared"),
            (ColorTarget.BG, "ultrared"),
            pytest.param(ColorTarget.UNDERLINE, None, marks=xfail(raises=NotImplementedError)),
        ],
    )
    def test_to_tmux(self, target: ColorTarget, expected_result: str | None):
        color = Color16(0xF00000, 300 + IntCode.RED, 300 + IntCode.BG_RED, "ultrared")
        assert color.to_tmux(target) == expected_result

    @pytest.mark.xfail(raises=LogicError)
    def test_to_tmux_without_name_fails(self):
        Color16(0x800000, IntCode.RED, IntCode.BG_RED).to_tmux(ColorTarget.FG)

    def test_format_value(self):
        assert Color16(0x800000, 133, 143).format_value() == "0x800000"
        assert Color16(0x800000, 134, 144).format_value("#") == "#800000"

    def test_repr(self):
        assert repr(Color16(0x800000, 135, 145)) == "<Color16[c135(#800000?)]>"
        assert repr(cv.RED) == "<Color16[c31(#800000? red)]>"

    def test_equality(self):
        assert Color16(0x010203, 136, 146) == Color16(0x010203, 136, 146)

    def test_not_equality(self):
        assert Color16(0x010203, 136, 146) != Color16(0xFFEEDD, 137, 147)
        assert Color16(0x010203, 136, 146) != Color16(0x010203, 146, 136)
        assert Color16(0x010203, 136, 146) != Color256(0x010203, 356)
        assert Color16(0x010203, 136, 146) != ColorRGB(0x010203)

    def test_to_hsv(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        h, s, v = col.hsv
        assert_close(0, h)
        assert_close(1, s)
        assert_close(0.50, v)

    def test_to_rgb(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        r, g, b = col.rgb
        assert r == 128
        assert g == 0
        assert b == 0

    def test_applying_thresholds(self):
        col = Color16(-0x10, -1, -1)
        assert 0 <= col.int <= 0xFFFFFF


class TestColor256:
    _keeper_index: _ColorIndex[Color256] | None = None

    @classmethod
    def setup_class(cls):
        cls._keeper_index = copy(Color256._index)
        cls._keeper_index._map = copy(Color256._index._map)

    @classmethod
    def teardown_class(cls):
        Color256._index = cls._keeper_index
        cls._keeper_index = None

    def setup_method(self):
        Color256._index._map = copy(self._keeper_index._map)

    def test_get_code(self):
        col = Color256(0xF00000, 457)
        assert 457 == col.code

    @pytest.mark.parametrize(
        "upper_bound, target, expected_result",
        [
            (None, ColorTarget.FG, SequenceSGR(38, 5, 1)),
            (None, ColorTarget.BG, SequenceSGR(48, 5, 1)),
            (None, ColorTarget.UNDERLINE, SequenceSGR(58, 5, 1)),
            (ColorRGB, ColorTarget.FG, SequenceSGR(38, 5, 1)),
            (ColorRGB, ColorTarget.BG, SequenceSGR(48, 5, 1)),
            (
                ColorRGB,
                ColorTarget.UNDERLINE,
                SequenceSGR(58, 5, 1),
            ),  # prefer_rgb is False by default
            (Color256, ColorTarget.FG, SequenceSGR(38, 5, 1)),
            (Color256, ColorTarget.BG, SequenceSGR(48, 5, 1)),
            (Color256, ColorTarget.UNDERLINE, SequenceSGR(58, 5, 1)),
            (Color16, ColorTarget.FG, SequenceSGR(31)),
            (Color16, ColorTarget.BG, SequenceSGR(41)),
            (Color16, ColorTarget.UNDERLINE, NOOP_SEQ),
        ],
    )
    def test_to_sgr(
        self,
        upper_bound: type[Color] | None,
        target: ColorTarget,
        expected_result: str | None,
    ):
        c = Color256.get_by_code(1)
        assert c.to_sgr(target, upper_bound) == expected_result

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, SequenceSGR(38, 2, 255, 204, 1)),
            (ColorTarget.BG, SequenceSGR(48, 2, 255, 204, 1)),
            (ColorTarget.UNDERLINE, SequenceSGR(58, 2, 255, 204, 1)),
        ],
    )
    @pytest.mark.config(prefer_rgb=True)
    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_rgb_if_preferred(
        self, target: ColorTarget, expected_result: str | None
    ):
        col = Color256(0xFFCC01, len(Color256._index))
        assert col.to_sgr(target, upper_bound=ColorRGB) == expected_result

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16_equiv(self):
        col16 = Color16(0xFFCC00, 132, 142)
        col = Color256(0xFFCC01, 258, color16_equiv=col16)
        assert col.to_sgr(ColorTarget.FG, upper_bound=Color16) == col16.to_sgr(ColorTarget.FG)
        assert col.to_sgr(ColorTarget.BG, upper_bound=Color16) == col16.to_sgr(ColorTarget.BG)
        assert col.to_sgr(ColorTarget.UNDERLINE, upper_bound=Color16) == NOOP_SEQ

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, "colour258"),
            (ColorTarget.BG, "colour258"),
            pytest.param(ColorTarget.UNDERLINE, None, marks=xfail(raises=NotImplementedError)),
        ],
    )
    def test_to_tmux(self, target: ColorTarget, expected_result: str | None):
        assert Color256(0xFF00FF, 258).to_tmux(target) == expected_result

    def test_format_value(self):
        assert Color256(0xFF00FF, 259).format_value() == "0xff00ff"
        assert Color256(0xFF00FF, 260).format_value("#") == "#ff00ff"

    def test_repr(self):
        assert repr(Color256(0xFF00FF, 259)) == "<Color256[x259(#ff00ff)]>"
        assert repr(cv.DARK_GREEN) == "<Color256[x22(#005f00 dark-green)]>"

    def test_equality(self):
        idx = len(Color256._index) + 1
        assert Color256(0x010203, idx) == Color256.get_by_code(idx)

    color16black = Color16.get_by_code(IntCode.BLACK)
    color256blackbound = Color256.get_by_code(0)
    color256blackunbound = Color256.get_by_code(16)
    color16blackfd = cv.BLACK
    color256blackfd = cv.GRAY_0

    @pytest.mark.parametrize(
        "col1,col2,expected_equality",
        [
            (color16black, color256blackbound, True),
            (color256blackunbound, color256blackbound, False),
            (color256blackunbound, color16black, False),
            (color16black, color16blackfd, True),
            (color256blackbound, color256blackfd, False),
            (color256blackunbound, color256blackfd, True),
        ],
        ids=format_test_params,
    )
    def test_equality_of_different_codes_and_same_equivs(
        self,
        col1: Color16 | Color256,
        col2: Color16 | Color256,
        expected_equality: bool,
    ):
        assert (col1 == col2) == expected_equality

    def test_not_equality(self):
        idx = len(Color256._index) + 10
        assert Color256(0x010203, (idx := idx + 1)) != Color256(0x030201, (idx := idx + 1))
        assert Color256(0x010203, (idx := idx + 1)) != Color256(0xFFEE14, (idx := idx + 1))
        assert Color256(0x010203, (idx := idx + 1)) != Color16(
            0x010203, (idx := idx + 1), (idx := idx + 1)
        )
        assert Color256(0x010203, (idx := idx + 1)) != ColorRGB(0x010203)

    def test_to_hsv(self):
        col = Color256(0x808000, code=len(Color256._index) + 1)
        h, s, v = col.hsv
        assert_close(h, 60)
        assert_close(s, 1)
        assert_close(v, 0.5)

    def test_to_rgb(self):
        col = Color256(0x808000, code=len(Color256._index) + 1)
        r, g, b = col.rgb
        assert r == 128
        assert g == 128
        assert b == 0

    def test_applying_thresholds(self):
        col = Color256(-0x10, -1)
        assert 0 <= col.int <= 0xFFFFFF


class TestColorRGB:
    @pytest.mark.parametrize(
        "upper_bound, target, expected_result",
        [
            (None, ColorTarget.FG, SequenceSGR(38, 2, 255, 51, 255)),
            (None, ColorTarget.BG, SequenceSGR(48, 2, 255, 51, 255)),
            (None, ColorTarget.UNDERLINE, SequenceSGR(58, 2, 255, 51, 255)),
            (ColorRGB, ColorTarget.FG, SequenceSGR(38, 2, 255, 51, 255)),
            (ColorRGB, ColorTarget.BG, SequenceSGR(48, 2, 255, 51, 255)),
            (ColorRGB, ColorTarget.UNDERLINE, SequenceSGR(58, 2, 255, 51, 255)),
            (Color256, ColorTarget.FG, SequenceSGR(38, 5, 201)),
            (Color256, ColorTarget.BG, SequenceSGR(48, 5, 201)),
            (Color256, ColorTarget.UNDERLINE, SequenceSGR(58, 5, 201)),
            (Color16, ColorTarget.FG, SequenceSGR(95)),
            (Color16, ColorTarget.BG, SequenceSGR(105)),
            (Color16, ColorTarget.UNDERLINE, NOOP_SEQ),
        ],
    )
    def test_to_sgr(
        self,
        upper_bound: type[Color] | None,
        target: ColorTarget,
        expected_result: str | None,
    ):
        col = ColorRGB(0xFF33FF)
        assert col.to_sgr(target, upper_bound) == expected_result

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, "#ff00ff"),
            (ColorTarget.BG, "#ff00ff"),
            pytest.param(
                ColorTarget.UNDERLINE,
                None,
                marks=pytest.mark.xfail(raises=NotImplementedError),
            ),
        ],
    )
    def test_to_tmux(self, target: ColorTarget, expected_result: str | None):
        assert ColorRGB(0xFF00FF).to_tmux(target) == expected_result

    def test_format_value(self):
        assert ColorRGB(0xFF00FF).format_value() == "0xff00ff"
        assert ColorRGB(0xFF00FF).format_value("#") == "#ff00ff"

    def test_repr(self):
        assert repr(ColorRGB(0xFF00FF)) == "<ColorRGB[#ff00ff]>"
        assert repr(ColorRGB(0xFF00FF, name="testrgb")) == "<ColorRGB[#ff00ff(testrgb)]>"

    def test_equality(self):
        assert ColorRGB(0x010203) == ColorRGB(0x010203)

    def test_not_equality(self):
        assert ColorRGB(0x010203) != ColorRGB(0x030201)
        assert ColorRGB(0x010203) != Color256(0x010203, len(Color256._index) + 1)
        assert ColorRGB(0x010203) != Color16(
            0x556677, len(Color256._index) + 1, len(Color256._index) + 1
        )

    def test_to_hsv(self):
        col = ColorRGB(0x008000)
        h, s, v = col.hsv
        assert_close(h, 120)
        assert_close(s, 1)
        assert_close(v, 0.50)

    def test_to_rgb(self):
        col = ColorRGB(0x008000)
        r, g, b = col.rgb
        assert r == 0
        assert g == 128
        assert b == 0

    def test_applying_thresholds(self):
        col = ColorRGB(-0x10)
        assert 0 <= col.int <= 0xFFFFFF


class TestRealColor:
    def test_construct_from_cv(self):
        cv = HSV(180, 0.5, 0.5)
        assert RealColor(cv).rgb == cv.rgb

    def test_construct_from_int(self):
        assert RealColor(0xFF0099).rgb == RGB(0xFF0099)

    def test_to_xyz(self):
        assert RealColor(0xFF0099).xyz == XYZ(x=46.99, y=23.56, z=32.20)


class TestNoopColor:
    def test_equality(self):
        assert NOOP_COLOR.to_sgr(ColorTarget.BG, Color16) == NOOP_SEQ
        assert NOOP_COLOR.to_sgr(ColorTarget.FG, ColorRGB) == NOOP_SEQ

    def test_format_value(self):
        assert NOOP_COLOR.format_value() == "NOP"

    def test_repr(self):
        assert repr(NOOP_COLOR) == "<NoopColor[NOP]>"

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, ""),
            (ColorTarget.BG, ""),
            pytest.param(
                ColorTarget.UNDERLINE,
                None,
                marks=pytest.mark.xfail(raises=NotImplementedError),
            ),
        ],
    )
    def test_to_tmux(self, target: ColorTarget, expected_result: str | None):
        assert NOOP_COLOR.to_tmux(target) == expected_result


class TestDefaultColor:
    def test_default_equality(self):
        assert DEFAULT_COLOR == DEFAULT_COLOR

    def test_default_neq_noop(self):
        assert DEFAULT_COLOR != NOOP_COLOR

    def test_format_value(self):
        assert DEFAULT_COLOR.format_value() == "DEF"

    def test_repr(self):
        assert repr(DEFAULT_COLOR) == "<DefaultColor[DEF]>"

    def test_default_resets_text_color(self):
        assert str(IntCode.COLOR_OFF.value) in DEFAULT_COLOR.to_sgr().assemble()

    def test_default_resets_bg_color(self):
        assert str(IntCode.BG_COLOR_OFF.value) in DEFAULT_COLOR.to_sgr(ColorTarget.BG).assemble()

    @pytest.mark.parametrize(
        "target, expected_result",
        [
            (ColorTarget.FG, "default"),
            (ColorTarget.BG, "default"),
            pytest.param(
                ColorTarget.UNDERLINE,
                None,
                marks=pytest.mark.xfail(raises=NotImplementedError),
            ),
        ],
    )
    def test_to_tmux(self, target: ColorTarget, expected_result: str | None):
        assert DEFAULT_COLOR.to_tmux(target) == expected_result


class TestDynamicColor:
    def test_initial_state(self, dynamic_style: Style):
        assert dynamic_style.fg == DEFAULT_COLOR

    @pytest.mark.dynamic_style(current_mode="help")
    def test_update(self, dynamic_style: Style):
        assert dynamic_style.fg == cv.HI_GREEN

    @pytest.mark.dynamic_style(current_mode="help")
    def test_to_sgr(self, dynamic_style: Style):
        assert dynamic_style.bg.to_sgr() == make_color_256(22)

    @pytest.mark.dynamic_style(current_mode="auto")
    def test_to_tmux(self, dynamic_style: Style):
        assert dynamic_style.fg.to_tmux() == "brightred"

    class _TestDynamicColor(DynamicColor[Color256]):
        @classmethod
        @overload
        def update(cls, *, current_mode: str) -> None:
            ...

        @classmethod
        def update(cls, **kwargs) -> None:
            super().update(**kwargs)

        @classmethod
        def _update_impl(cls, *, current_mode: str = "main") -> Color256:
            return cv.DARK_RED_2 if current_mode == "main" else cv.DARK_GREEN

    def test_without_extractor(self):
        col = self._TestDynamicColor(extractor=None)
        col.update(current_mode="help")
        assert col.to_sgr() == cv.DARK_GREEN.to_sgr()

    def test_with_callable_extractor(self):
        col = self._TestDynamicColor(extractor=lambda c: Color256(c._value.int * 2, code=267))
        col.update(current_mode="help")
        assert col._value._value.int == cv.DARK_GREEN._value.int * 2  # noqa


@skip_pre_310_typing
class TestDeferredColor:
    def test_initial_state(self, deferred: tuple[Style, any]):
        deferred_style, _ = deferred
        assert deferred_style.fg == NOOP_COLOR

    def test_update(self, deferred: tuple[Style, any]):
        deferred_style, resolver = deferred
        assert deferred_style.fg == NOOP_COLOR
        resolver.initialize("help")
        assert deferred_style.fg == cv.HI_GREEN

    def test_to_sgr(self, deferred: tuple[Style, any]):
        deferred_style, resolver = deferred
        assert deferred_style.fg.to_sgr() == NOOP_COLOR.to_sgr()
        resolver.initialize("help")
        assert deferred_style.fg.to_sgr() == cv.HI_GREEN.to_sgr()

    def test_to_tmux(self, deferred: tuple[Style, any]):
        deferred_style, resolver = deferred
        assert deferred_style.fg.to_tmux() == ""
        resolver.initialize("help")
        assert deferred_style.fg.to_tmux() == "brightgreen"

    @pytest.mark.config(force_output_mode=OutputMode.TRUE_COLOR)
    def test_text_changes(self, deferred: tuple[Style, any]):
        deferred_style, resolver = deferred
        text = Text("123", deferred_style)
        assert render(text) == "123"
        resolver.initialize("help")
        assert render(text) == "\x1b[92;48;5;22m" "123" "\x1b[39;49m"

    def test_deferred_auto_init_works(self, deferred: tuple[Style, any]):
        deferred_style, resolver = deferred
        resolver.initialize("help")
        col = deferred_style.fg.__class__("fg")
        deferred_style = FrozenStyle(fg=col)
        text = Text("123", deferred_style)
        assert render(text) == "123"
