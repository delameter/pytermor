# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from math import isclose

import pytest

from pytermor import (
    NOOP_SEQ,
    Style,
    SequenceSGR,
    IntCode,
    color,
    resolve_color,
    DEFAULT_COLOR,
    NOOP_COLOR,
    Color16,
    Color256,
    ColorRGB,
    cv,
)
from pytermor.color import ColorNameConflictError, ColorCodeConflictError
from pytermor.common import LogicError


def assert_close(a: float, b: float):
    assert isclose(a, b, abs_tol=0.01)


class TestResolving:
    def test_module_method_resolve_works(self):
        assert ColorRGB(0xFFFFF0) == resolve_color("ivory")

    def test_module_method_resolve_alias_works(self):
        assert ColorRGB(0x0052CC) == resolve_color("jira-blue")

    def test_module_method_resolve_full_rgb_form_works(self):
        assert ColorRGB(0xFFD000) == resolve_color("#ffd000")

    def test_module_method_resolve_short_rgb_form_works(self):
        assert ColorRGB(0x3399FF) == resolve_color("#39f")

    def test_module_method_resolve_integer_rgb_form_works(self):
        assert ColorRGB(0x00039F) == resolve_color(0x39F)

    def test_module_method_resolve_rgb_form_works_upon_color_rgb(self):
        assert ColorRGB(0xFAFAFE) == resolve_color("#fafafe", ColorRGB)

    @pytest.mark.xfail(raises=LookupError)
    def test_module_method_resolve_rgb_form_fails_upon_color_256(self):
        resolve_color("#148811", Color256)

    @pytest.mark.xfail(raises=LookupError)
    def test_module_method_resolve_rgb_form_fails_upon_color_16(self):
        resolve_color("#111488", Color16)

    @pytest.mark.xfail(raises=LookupError)
    def test_module_method_resolve_of_non_existing_color_fails(self):
        resolve_color("non-existing-color")

    def test_module_method_resolve_ambiguous_color_works_upon_abstract_color(self):
        col = resolve_color("green")
        assert col.hex_value == 0x008000
        assert isinstance(col, Color16)

    def test_module_method_resolve_ambiguous_color_works_upon_color_16(self):
        col = resolve_color("green", Color16)
        assert col.hex_value == 0x008000
        assert isinstance(col, Color16)

    def test_module_method_resolve_ambiguous_color_works_upon_color_256(self):
        col = resolve_color("green", Color256)
        assert col.hex_value == 0x008000
        assert isinstance(col, Color256)

    def test_module_method_resolve_ambiguous_color_works_upon_color_rgb(self):
        col = resolve_color("green", ColorRGB)
        assert col.hex_value == 0x1CAC78
        assert isinstance(col, ColorRGB)


class TestColorRegistry:
    # @TODO the state of the registry better be reset before each one of those,
    #       but at the moment I don't see a fast and reliable way to achieve this

    def test_registering_works(self):
        map_length_start = len(ColorRGB._registry)
        col = ColorRGB(0x2, "test 2", register=True)

        assert map_length_start + 1 == len(ColorRGB._registry)
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


class TestColorIndex:
    def test_adding_to_index_works(self):
        index_length_start = len(ColorRGB._index)
        col = ColorRGB(0x1, "test 1", index=True)

        assert index_length_start + 1 == len(ColorRGB._index)
        assert col is ColorRGB.find_closest(0x1)

    def test_adding_duplicate_to_index_doesnt_change_index_length(self):
        Color16(0x1, 131, 141, "test 1", index=True)
        index_length_start = len(Color16._index)
        Color16(0x1, 131, 141, "test 1", index=True)

        assert index_length_start == len(Color16._index)

    @pytest.mark.xfail(raises=ColorCodeConflictError)
    def test_adding_code_duplicate_to_index_fails(self):
        Color16(0x1, 131, 141, "test 1", index=True)
        Color16(0x2, 131, 141, "test 1", index=True)

    @pytest.mark.xfail(raises=KeyError)
    def test_getting_of_non_existing_color_fails(self):
        Color256.get_by_code(256)


class TestApproximation:
    def test_module_method_find_closest_works_as_256_by_default(self):
        assert color.find_closest(0x87FFD7) is cv.AQUAMARINE_1

    def test_module_method_find_closest_works_for_16(self):
        assert color.find_closest(0x87FFD7, Color16) is cv.WHITE

    def test_module_method_find_closest_works_for_rgb(self):
        assert resolve_color("aquamarine", ColorRGB) is color.find_closest(
            0x87FFD7, ColorRGB
        )

    def test_module_method_approximate_works_as_256_by_default(self):
        assert color.approximate(0x87FFD7)[0].color is cv.AQUAMARINE_1

    def test_module_method_approximate_works_for_16(self):
        assert color.approximate(0x87FFD7, Color16)[0].color is cv.WHITE

    def test_module_method_approximate_works_for_rgb(self):
        assert (
            resolve_color("aquamarine", ColorRGB)
            is color.approximate(0x87FFD7, ColorRGB)[0].color
        )

    def test_class_method_find_closest_works_for_16(self):
        assert Color16.find_closest(0x87FFD7) is cv.WHITE

    def test_class_method_find_closest_works_for_256(self):
        assert Color256.find_closest(0x87FFD7) is cv.AQUAMARINE_1

    def test_class_method_find_closest_works_for_rgb(self):
        assert 0x7FFFD4 == ColorRGB.find_closest(0x87FFD7).hex_value

    def test_class_method_approximate_works_for_16(self):
        assert Color16.approximate(0x87FFD7)[0].color is cv.WHITE

    def test_class_method_approximate_works_for_256(self):
        assert Color256.approximate(0x87FFD7)[0].color is cv.AQUAMARINE_1

    def test_class_method_approximate_works_for_rgb(self):
        assert ColorRGB.approximate(0x87FFD7)[0].color.hex_value == 0x7FFFD4


class TestColor16:
    def test_get_code(self):
        col = Color16(0xF00000, IntCode.RED, IntCode.BG_RED)
        assert col.code_fg == IntCode.RED
        assert col.code_bg == IntCode.BG_RED

    def test_to_sgr_without_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert col.to_sgr(False) == SequenceSGR(31)
        assert col.to_sgr(True) == SequenceSGR(41)

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert col.to_sgr(False, upper_bound=ColorRGB) == SequenceSGR(31)
        assert col.to_sgr(True, upper_bound=ColorRGB) == SequenceSGR(41)

    def test_to_sgr_with_256_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert col.to_sgr(False, upper_bound=Color256) == SequenceSGR(31)
        assert col.to_sgr(True, upper_bound=Color256) == SequenceSGR(41)

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        assert col.to_sgr(False, upper_bound=Color16) == SequenceSGR(31)
        assert col.to_sgr(True, upper_bound=Color16) == SequenceSGR(41)

    def test_to_tmux(self):
        col = Color16(0xF00000, IntCode.RED, IntCode.BG_RED, "ultrared")
        assert col.to_tmux(False) == "ultrared"
        assert col.to_tmux(True) == "ultrared"

    @pytest.mark.xfail(raises=LogicError)
    def test_to_tmux_without_name_fails(self):
        Color16(0x800000, IntCode.RED, IntCode.BG_RED).to_tmux(False)

    def test_format_value(self):
        assert Color16(0x800000, 133, 143).format_value() == "0x800000"
        assert Color16(0x800000, 134, 144).format_value("#") == "#800000"

    def test_repr(self):
        assert repr(Color16(0x800000, 135, 145)) == "<Color16[c135(#800000?)]>"
        assert repr(cv.RED) == "<Color16[c31(#800000? red)]>"

    def test_equality(self):
        assert Color16(0x010203, 11, 12) == Color16(0x010203, 11, 12)

    def test_not_equality(self):
        assert Color16(0x010203, 11, 12) != Color16(0xFFEEDD, 11, 12)
        assert Color16(0x010203, 11, 12) != Color16(0x010203, 12, 11)
        assert Color16(0x010203, 11, 12) != Color256(0x010203, 12)
        assert Color16(0x010203, 11, 12) != ColorRGB(0x010203)

    def test_to_hsv(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        h, s, v = col.to_hsv()
        assert_close(0, h)
        assert_close(1, s)
        assert_close(0.50, v)

    def test_to_rgb(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        r, g, b = col.to_rgb()
        assert r == 128
        assert g == 0
        assert b == 0


class TestColor256:
    def test_get_code(self):
        col = Color256(0xF00000, 257)
        assert 257 == col.code

    def test_to_sgr_without_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        assert col.to_sgr(False) == SequenceSGR(38, 5, 1)
        assert col.to_sgr(True) == SequenceSGR(48, 5, 1)

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        assert col.to_sgr(False, upper_bound=ColorRGB) == SequenceSGR(38, 5, 1)
        assert col.to_sgr(True, upper_bound=ColorRGB) == SequenceSGR(48, 5, 1)

    @pytest.mark.setup(prefer_rgb=True)
    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_rgb_if_preferred(self):
        col = Color256(0xFFCC01, 1)
        assert col.to_sgr(False, upper_bound=ColorRGB) == SequenceSGR(38, 2, 255, 204, 1)
        assert col.to_sgr(True, upper_bound=ColorRGB) == SequenceSGR(48, 2, 255, 204, 1)

    def test_to_sgr_with_256_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        assert col.to_sgr(False, upper_bound=Color256) == SequenceSGR(38, 5, 1)
        assert col.to_sgr(True, upper_bound=Color256) == SequenceSGR(48, 5, 1)

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = Color256(0xFFCC01, 1)
        assert col.to_sgr(False, upper_bound=Color16) == SequenceSGR(93)
        assert col.to_sgr(True, upper_bound=Color16) == SequenceSGR(103)

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16_equiv(self):
        col16 = Color16(0xFFCC00, 132, 142, index=True)
        col = Color256(0xFFCC01, 1, color16_equiv=col16)
        assert col16.to_sgr(False) == col.to_sgr(False, upper_bound=Color16)
        assert col16.to_sgr(True) == col.to_sgr(True, upper_bound=Color16)

    def test_to_tmux(self):
        col = Color256(0xFF00FF, 258)
        assert col.to_tmux(False) == "colour258"
        assert col.to_tmux(True) == "colour258"

    def test_format_value(self):
        assert Color256(0xFF00FF, 259).format_value() == "0xff00ff"
        assert Color256(0xFF00FF, 260).format_value("#") == "#ff00ff"

    def test_repr(self):
        assert repr(Color256(0xFF00FF, 259)) == "<Color256[x259(#ff00ff)]>"
        assert repr(cv.DARK_GREEN) == "<Color256[x22(#005f00 dark-green)]>"

    def test_equality(self):
        assert Color256(0x010203, 11) == Color256(0x010203, 11)

    def test_not_equality(self):
        assert Color256(0x010203, 11) != Color256(0x010203, 12)
        assert Color256(0x010203, 11) != Color256(0x030201, 11)
        assert Color256(0x010203, 11) != Color256(0xFFEE14, 88)
        assert Color256(0x010203, 11) != Color16(0x010203, 11, 11)
        assert Color256(0x010203, 11) != ColorRGB(0x010203)

    def test_to_hsv(self):
        col = Color256(0x808000, code=256)
        h, s, v = col.to_hsv()
        assert_close(h, 60)
        assert_close(s, 1)
        assert_close(v, 0.5)

    def test_to_rgb(self):
        col = Color256(0x808000, code=256)
        r, g, b = col.to_rgb()
        assert r == 128
        assert g == 128
        assert b == 0


class TestColorRGB:
    def test_to_sgr_without_upper_bound_results_in_sgr_rgb(self):
        col = ColorRGB(0xFF33FF)
        assert col.to_sgr(False) == SequenceSGR(38, 2, 255, 51, 255)
        assert col.to_sgr(True) == SequenceSGR(48, 2, 255, 51, 255)

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_rgb(self):
        col = ColorRGB(0xFF33FF)
        assert col.to_sgr(False, upper_bound=ColorRGB) == SequenceSGR(
            38, 2, 255, 51, 255
        )
        assert col.to_sgr(True, upper_bound=ColorRGB) == SequenceSGR(48, 2, 255, 51, 255)

    def test_to_sgr_with_256_upper_bound_results_in_sgr_256(self):
        col = ColorRGB(0xFF33FF)
        assert col.to_sgr(False, upper_bound=Color256) == SequenceSGR(38, 5, 207)
        assert col.to_sgr(True, upper_bound=Color256) == SequenceSGR(48, 5, 207)

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = ColorRGB(0xFF33FF)
        assert col.to_sgr(False, upper_bound=Color16) == SequenceSGR(95)
        assert col.to_sgr(True, upper_bound=Color16) == SequenceSGR(105)

    def test_to_tmux(self):
        col = ColorRGB(0xFF00FF)
        assert col.to_tmux(False) == "#ff00ff"
        assert col.to_tmux(True) == "#ff00ff"

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
        assert ColorRGB(0x010203) != Color256(0x010203, 1)
        assert ColorRGB(0x010203) != Color16(0x556677, IntCode.WHITE, IntCode.BG_WHITE)

    def test_to_hsv(self):
        col = ColorRGB(0x008000)
        h, s, v = col.to_hsv()
        assert_close(h, 120)
        assert_close(s, 1)
        assert_close(v, 0.50)

    def test_to_rgb(self):
        col = ColorRGB(0x008000)
        r, g, b = col.to_rgb()
        assert r == 0
        assert g == 128
        assert b == 0


class TestNoopColor:
    def test_equality(self):
        assert NOOP_COLOR.to_sgr(True, Color16) == NOOP_SEQ
        assert NOOP_COLOR.to_sgr(False, ColorRGB) == NOOP_SEQ

    def test_format_value(self):
        assert NOOP_COLOR.format_value() == "NOP"

    def test_repr(self):
        assert repr(NOOP_COLOR) == "<_NoopColor[NOP]>"

    def test_to_tmux(self):
        assert NOOP_COLOR.to_tmux(False) == ""
        assert NOOP_COLOR.to_tmux(True) == ""

    @pytest.mark.xfail(raises=LogicError)
    def test_getting_hex_value_fails(self):
        (lambda: NOOP_COLOR.hex_value)()


class TestDefaultColor:
    def test_default_equality(self):
        assert DEFAULT_COLOR == DEFAULT_COLOR

    def test_default_neq_noop(self):
        assert DEFAULT_COLOR != NOOP_COLOR

    def test_format_value(self):
        assert DEFAULT_COLOR.format_value() == "DEF"

    def test_repr(self):
        assert repr(DEFAULT_COLOR) == "<_DefaultColor[DEF]>"
