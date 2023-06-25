# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest
from pytest import mark

from pytermor import (
    FrozenText,
    RT,
    SgrRenderer,
    Style,
    Styles,
    cv,
    make_clear_line,
    make_set_cursor_column,
    render,
)
from pytermor.ansi import SeqIndex
from pytermor.common import get_qname, get_subclasses
from pytermor.filter import *
from tests import format_test_params, load_data_file


class TestStdlibExtensions:
    _TEST_STRING = "123_456_789_0💩晥abc_def_"  # noqa

    @mark.parametrize(
        "fns",
        [(center_sgr, str.center), (ljust_sgr, str.ljust), (rjust_sgr, str.rjust)],
        ids=format_test_params,
    )
    @mark.parametrize("len_shift", range(-3, 3))
    @mark.parametrize("width", range(4, 18))
    def test_methods_are_equivalent_to_stdlib(
        self, width: int, len_shift: int, fns: tuple[t.Callable[[str, int, str], str]]
    ):
        len = width + len_shift
        assert len > 0

        raw_string = self._TEST_STRING[:len]
        sgr_string = raw_string.replace("123", f"1{SeqIndex.RED}2{SeqIndex.COLOR_OFF}3")
        actual = fns[1](raw_string, width, ".")
        expected = SgrStringReplacer().apply(fns[0](sgr_string, width, "."))
        assert actual == expected


class TestCutAndFit:
    @mark.parametrize(
        "input, max_len, align, overflow, expected_fit",
        [
            ("1234567890", 12, None, "…", "1234567890  "),
            ("1234567890", 10, None, "…", "1234567890"),
            ("1234567890", 9, None, "…", "12345678…"),
            ("1234567890", 5, None, "…", "1234…"),
            ("1234567890", 2, None, "…", "1…"),
            ("1234567890", 1, None, "…", "…"),
            ("1234567890", 0, None, "…", ""),
            ("1234567890", 12, Align.CENTER, "…", " 1234567890 "),
            ("1234567890", 10, Align.CENTER, "…", "1234567890"),
            ("1234567890", 9, Align.CENTER, "…", "1234…7890"),
            ("1234567890", 5, Align.CENTER, "…", "12…90"),
            ("1234567890", 2, Align.CENTER, "…", "…0"),
            ("1234567890", 1, Align.CENTER, "…", "…"),
            ("1234567890", 0, Align.CENTER, "…", ""),
            ("1234567890", 12, Align.RIGHT, "…", "  1234567890"),
            ("1234567890", 10, Align.RIGHT, "…", "1234567890"),
            ("1234567890", 9, Align.RIGHT, "…", "…34567890"),
            ("1234567890", 5, Align.RIGHT, "…", "…7890"),
            ("1234567890", 2, Align.RIGHT, "…", "…0"),
            ("1234567890", 1, Align.RIGHT, "…", "…"),
            ("1234567890", 0, Align.RIGHT, "…", ""),
            ("1234567890", 0, Align.LEFT, "...", ""),
            ("1234567890", 1, Align.LEFT, "..?", "."),
            ("1234567890", 2, Align.LEFT, "..?", ".."),
            ("1234567890", 3, Align.LEFT, "..?", "..?"),
            ("1234567890", 4, Align.LEFT, "..?", "1..?"),
            ("1234567890", 5, Align.LEFT, "..?", "12..?"),
            ("1234567890", 9, Align.LEFT, "..?", "123456..?"),
            ("1234567890", 10, Align.LEFT, "..?", "1234567890"),
            ("1234567890", 12, Align.LEFT, "..?", "1234567890  "),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.CENTER, "..?", "."),
            ("1234567890", 2, Align.CENTER, "..?", ".."),
            ("1234567890", 3, Align.CENTER, "..?", "..?"),
            ("1234567890", 4, Align.CENTER, "..?", "..?0"),
            ("1234567890", 5, Align.CENTER, "..?", "1..?0"),
            ("1234567890", 9, Align.CENTER, "..?", "123..?890"),
            ("1234567890", 10, Align.CENTER, "..?", "1234567890"),
            ("1234567890", 12, Align.CENTER, "..?", " 1234567890 "),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.RIGHT, "..?", "."),
            ("1234567890", 2, Align.RIGHT, "..?", ".."),
            ("1234567890", 3, Align.RIGHT, "..?", "..?"),
            ("1234567890", 4, Align.RIGHT, "..?", "..?0"),
            ("1234567890", 5, Align.RIGHT, "..?", "..?90"),
            ("1234567890", 9, Align.RIGHT, "..?", "..?567890"),
            ("1234567890", 10, Align.RIGHT, "..?", "1234567890"),
            ("1234567890", 12, Align.RIGHT, "..?", "  1234567890"),
        ],
        ids=format_test_params,
    )
    def test_fit(
        self,
        input: str,
        max_len: int,
        align: Align | str,
        overflow: str,
        expected_fit: str,
    ):
        actual_fit = fit(input, max_len, align, overflow)
        assert len(actual_fit) <= max_len
        assert actual_fit == expected_fit

    @mark.parametrize(
        "input, max_len, align, overflow, expected_cut",
        [
            ("1234567890", 12, None, "…", "1234567890"),
            ("1234567890", 10, None, "…", "1234567890"),
            ("1234567890", 9, None, "…", "12345678…"),
            ("1234567890", 5, None, "…", "1234…"),
            ("1234567890", 2, None, "…", "1…"),
            ("1234567890", 1, None, "…", "…"),
            ("1234567890", 0, None, "…", ""),
            ("1234567890", 12, Align.CENTER, "…", "1234567890"),
            ("1234567890", 10, Align.CENTER, "…", "1234567890"),
            ("1234567890", 9, Align.CENTER, "…", "1234…7890"),
            ("1234567890", 5, Align.CENTER, "…", "12…90"),
            ("1234567890", 2, Align.CENTER, "…", "…0"),
            ("1234567890", 1, Align.CENTER, "…", "…"),
            ("1234567890", 0, Align.CENTER, "…", ""),
            ("1234567890", 12, Align.RIGHT, "…", "1234567890"),
            ("1234567890", 10, Align.RIGHT, "…", "1234567890"),
            ("1234567890", 9, Align.RIGHT, "…", "…34567890"),
            ("1234567890", 5, Align.RIGHT, "…", "…7890"),
            ("1234567890", 2, Align.RIGHT, "…", "…0"),
            ("1234567890", 1, Align.RIGHT, "…", "…"),
            ("1234567890", 0, Align.RIGHT, "…", ""),
            ("1234567890", 0, Align.LEFT, "...", ""),
            ("1234567890", 1, Align.LEFT, "..?", "."),
            ("1234567890", 2, Align.LEFT, "..?", ".."),
            ("1234567890", 3, Align.LEFT, "..?", "..?"),
            ("1234567890", 4, Align.LEFT, "..?", "1..?"),
            ("1234567890", 5, Align.LEFT, "..?", "12..?"),
            ("1234567890", 9, Align.LEFT, "..?", "123456..?"),
            ("1234567890", 10, Align.LEFT, "..?", "1234567890"),
            ("1234567890", 12, Align.LEFT, "..?", "1234567890"),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.CENTER, "..?", "."),
            ("1234567890", 2, Align.CENTER, "..?", ".."),
            ("1234567890", 3, Align.CENTER, "..?", "..?"),
            ("1234567890", 4, Align.CENTER, "..?", "..?0"),
            ("1234567890", 5, Align.CENTER, "..?", "1..?0"),
            ("1234567890", 9, Align.CENTER, "..?", "123..?890"),
            ("1234567890", 10, Align.CENTER, "..?", "1234567890"),
            ("1234567890", 12, Align.CENTER, "..?", "1234567890"),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.RIGHT, "..?", "."),
            ("1234567890", 2, Align.RIGHT, "..?", ".."),
            ("1234567890", 3, Align.RIGHT, "..?", "..?"),
            ("1234567890", 4, Align.RIGHT, "..?", "..?0"),
            ("1234567890", 5, Align.RIGHT, "..?", "..?90"),
            ("1234567890", 9, Align.RIGHT, "..?", "..?567890"),
            ("1234567890", 10, Align.RIGHT, "..?", "1234567890"),
            ("1234567890", 12, Align.RIGHT, "..?", "1234567890"),
        ],
        ids=format_test_params,
    )
    def test_cut(
        self,
        input: str,
        max_len: int,
        align: Align | str,
        overflow: str,
        expected_cut: str,
    ):
        actual_cut = cut(input, max_len, align, overflow)
        assert len(actual_cut) <= max_len
        assert actual_cut == expected_cut


class TestPadding:
    def test_pad(self, n=10):
        assert pad(n) == n * " "

    def test_padv(self, n=10):
        assert padv(n) == n * "\n"


class TestGenericFilters:
    @mark.parametrize(
        "input",
        [
            "",
            "1234567890",
            "qwertyuiop[]",
            "йцукенгшхъ",
            "摕㒃衉退",
            "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
            "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f",
            "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f",
            "\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff",
            b"",
            b"1234567890",
            b"qwertyuiop[]",
            bytes(bytearray(range(0x00, 0x10))),
            bytes(bytearray(range(0x10, 0x20))),
            bytes(bytearray(range(0x80, 0x90))),
            bytes(bytearray(range(0xF0, 0x100))),
        ],
        ids=format_test_params,
    )
    def test_noop_filter(self, input: t.AnyStr):
        assert NoopFilter().apply(input) == input

    @mark.parametrize(
        "input, expected_output",
        [
            (b"", ""),
            (b"1234567890", "1234567890"),
            (b"qwertyuiop[]", "qwertyuiop[]"),
            (bytes(bytearray(range(0x00, 0x10))), bytearray(range(0x00, 0x10)).decode()),
            (bytes(bytearray(range(0x10, 0x20))), bytearray(range(0x10, 0x20)).decode()),
            (
                b"\xd0\xb9\xd1\x86\xd1\x83\xd0\xba\xd0\xb5\xd0\xbd\xd0\xb3\xd1\x88\xd1\x85\xd1\x8a",
                "йцукенгшхъ",
            ),
            (b"\xe6\x91\x95\xe3\x92\x83\xe8\xa1\x89\xe9\x80\x80", "摕㒃衉退"),
            (b"\xe2\x98\x80\xe2\x9b\x88\xf0\x9f\x91\x86\xf0\x9f\x98\x8e", "☀⛈👆😎"),
            pytest.param(
                bytes(bytearray(range(0x80, 0x90))),
                None,
                marks=mark.xfail(raises=UnicodeDecodeError),
            ),
            pytest.param(
                bytes(bytearray(range(0xF0, 0x100))),
                None,
                marks=mark.xfail(raises=UnicodeDecodeError),
            ),
            ("1234567890", "1234567890"),
        ],
    )
    def test_omni_decoder(self, input: bytes, expected_output: str | None):
        assert OmniDecoder().apply(input) == expected_output

    @mark.parametrize(
        "input, expected_output",
        [
            ("", b""),
            ("1234567890", b"1234567890"),
            ("qwertyuiop[]", b"qwertyuiop[]"),
            (bytearray(range(0x00, 0x10)).decode(), bytes(bytearray(range(0x00, 0x10)))),
            (bytearray(range(0x10, 0x20)).decode(), bytes(bytearray(range(0x10, 0x20)))),
            (
                "йцукенгшхъ",
                b"\xd0\xb9\xd1\x86\xd1\x83\xd0\xba\xd0\xb5\xd0\xbd\xd0\xb3\xd1\x88\xd1\x85\xd1\x8a",
            ),
            ("摕㒃衉退", b"\xe6\x91\x95\xe3\x92\x83\xe8\xa1\x89\xe9\x80\x80"),
            ("☀⛈👆😎", b"\xe2\x98\x80\xe2\x9b\x88\xf0\x9f\x91\x86\xf0\x9f\x98\x8e"),
            (b"1234567890", b"1234567890"),
        ],
    )
    def test_omni_encoder(self, input: str, expected_output: bytes):
        assert OmniEncoder().apply(input) == expected_output

    @mark.parametrize(
        "input, expected",
        [
            ("", "    "),
            (b"", b"    "),
            ("123", "  123  "),
            (b"123", b"  123  "),
            ("1\n2", "  1\n2  "),
            (b"1\n3", b"  1\n3  "),
        ],
        ids=format_test_params,
    )
    def test_omni_padder(self, input: t.AnyStr, expected: t.AnyStr):
        assert OmniPadder(2).apply(input) == expected

    def test_name_max_len(self):
        class TestFilterWithOMFGLongVeryVeryLongName(IFilter):
            def _apply(self, inp: IT, extra: t.Any = None) -> OT:
                pass

        TestFilterWithOMFGLongVeryVeryLongName()
        assert IFilter.get_name_max_len() <= 20


class TestReplacers:
    def test_replace_esq_replacer(self):
        actual = EscSeqStringReplacer(".").apply(
            f"{make_clear_line()}1{make_set_cursor_column()}"
        )
        assert actual == ".1."

    def test_replace_sgr_filter(self):
        actual = SgrStringReplacer(".").apply(f"{SeqIndex.RED}213{SeqIndex.RESET}")
        assert actual == ".213."

    def test_replace_csi_filter(self):
        actual = CsiStringReplacer(".").apply(f"{make_clear_line()}2{SeqIndex.RESET}")
        assert actual == ".2."

    def test_string_linearizer(self):
        actual = StringLinearizer().apply(f"123\n4 5 6\n78\t 9\t01234\n\n\t\n5")
        assert actual == "123 4 5 6 78 9 01234 5"

    def test_wspace_remover(self):
        actual = WhitespaceRemover().apply(f"123\n4 5 6\n78\t 9\t01234\n\n\t\n5")
        assert actual == "123456789012345"


class TestNamedGroupsRefilter:
    class SgrNamedGroupsRefilter(AbstractNamedGroupsRefilter):
        def _render(self, v: IT, st: FT) -> str:
            return render(v, st, SgrRenderer)

    @mark.parametrize(
        "input, regex, style_map, expected",
        [
            (
                "some text with some words",
                re.compile(r"(some)"),
                {"": cv.RED},
                FrozenText("some", "red", (" text with ",), "some", "red", " words"),
            ),
            (
                "some text with some words",
                re.compile(r"(?P<accent>some)"),
                {"accent": cv.RED},
                FrozenText(("some", "red"), " text with ", ("some", "red"), " words"),
            ),
            (
                "some text with some words",
                re.compile(r"(?P<s1>so)(?:m)(e)"),  # noqa
                {"s1": cv.BLUE},
                FrozenText(("so", "blue"), "e text with ", ("so", "blue"), "e words"),
            ),
            (
                "some text with some words",
                re.compile(r"(?P<s1>some)(\s*)(?P<s2>\w+)()"),  # noqa
                {"s1": cv.BLUE, "s2": cv.RED},
                FrozenText(
                    ("some", "blue"),
                    " ",
                    ("text", "red"),
                    " with ",
                    ("some", "blue"),
                    " ",
                    ("words", "red"),
                ),
            ),
            (
                "__123abcdef456qwert789:_",
                re.compile(r"(?P<c1>\d+)(?P<no>\w+?)(\d+)(?:\w+)(?P<c2>\d+).+"),  # noqa
                {"c1": Styles.ERROR, "c2": Styles.WARNING, "": Styles.CRITICAL},
                FrozenText(
                    "__",
                    ("123", Styles.ERROR),
                    "abcdef",
                    ("456", Styles.CRITICAL),
                    ("9", Styles.WARNING),
                ),
            ),
            (
                "data // comment",
                re.compile(R"(?<=\s)//\s?(?P<val>.+)$"),
                {"val": cv.GRAY},
                FrozenText(
                    "data ",
                    ("comment", "gray"),
                ),
            ),
        ],
    )
    @mark.setup(force_output_mode="xterm_256")
    def test_ngrefilter(
        self,
        input: str,
        regex: re.Pattern,
        style_map: t.Dict[str, FT],
        expected: RT,
    ):
        ngr = self.SgrNamedGroupsRefilter(regex, style_map)
        actual = ngr.apply(input)
        assert actual == render(expected)


class TestMappers:
    @mark.parametrize(
        "input, cmap, expected",
        [
            (b"abc def ghi", {0x20: "."}, b"abc.def.ghi"),
            ("abc def ghi", {0x20: "@"}, "abc@def@ghi"),
            pytest.param("", {400: "@"}, "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param("", {32: "й"}, "", marks=pytest.mark.xfail(raises=ValueError)),
            pytest.param("", {32: 3}, "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param("", {32: None}, "", marks=pytest.mark.xfail(raises=TypeError)),
        ],
        ids=format_test_params,
    )
    def test_omni_mapper(
        self,
        input: t.AnyStr,
        cmap: t.Dict[int, t.AnyStr],
        expected: t.AnyStr,
    ):
        assert OmniMapper(cmap).apply(input) == expected

    @mark.parametrize(
        "input, cmap, expected",
        [
            ("abc def ghi", {0x20: "."}, "abc.def.ghi"),
            ("abc def ghi", {0x20: ""}, "abcdefghi"),
            ("abc def ghi", {0x20: "Й"}, "abcЙdefЙghi"),  # noqa
            pytest.param("", {400: "@"}, "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param("", {32: 3}, "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param("", {32: None}, "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param(b"", {32: "q"}, "", marks=pytest.mark.xfail(raises=TypeError)),
        ],
        ids=format_test_params,
    )
    def test_string_mapper(self, input: str, cmap: t.Dict[int, str], expected: str):
        assert StringMapper(cmap).apply(input) == expected


class TestTracers:
    # fmt: off
    _TRACER_PARAMS = [
        ( 80, "test_tracer_exp-btracer80.txt",   BytesTracer,     "test_tracer_inp-btracer.dat"),
        (140, "test_tracer_exp-btracer140.txt",  BytesTracer,     "test_tracer_inp-btracer.dat"),
        ( 80, "test_tracer_exp-stracer80.txt",   StringTracer,    "test_tracer_inp-stracer.txt"),
        (140, "test_tracer_exp-stracer140.txt",  StringTracer,    "test_tracer_inp-stracer.txt"),
        ( 80, "test_tracer_exp-sutracer80.txt",  StringUcpTracer, "test_tracer_inp-stracer.txt"),
        (140, "test_tracer_exp-sutracer140.txt", StringUcpTracer, "test_tracer_inp-stracer.txt"),
    ]
    
    @mark.parametrize(
        "width, exp_data_filename, cls, inp_filename",
        _TRACER_PARAMS,
        ids=format_test_params,
    )
    # fmt: on
    def test_tracer(
        self,
        width: int,
        exp_data_filename: str,
        cls: t.Type[AbstractTracer],
        inp_filename: str,
    ):
        input = load_data_file(inp_filename)
        actual = cls(width).apply(input, TracerExtra("label"))
        assert actual.rstrip("\n") == load_data_file(exp_data_filename).rstrip("\n")

    @mark.parametrize(
        "width, exp_data_filename, cls, inp_filename",
        [tp for tp in _TRACER_PARAMS if tp[0] == 80],
        ids=format_test_params,
    )
    def test_dump(
        self,
        width: int,
        exp_data_filename: str,
        cls: t.Type[AbstractTracer],
        inp_filename: str,
    ):
        input = load_data_file(inp_filename)
        actual = dump(input, tracer_cls=cls, label="label")
        assert actual.rstrip("\n") == load_data_file(exp_data_filename).rstrip("\n")

    @mark.parametrize("max_width", [None, 40, 60, 80, 100, 120, 160, 240])
    @mark.parametrize(
        "input",
        ["f" * 64, "qй" * 32, "晦࢈ຮ" * 16, "·＊🐶𑼑􏿿" * 8],  # noqa
        ids=lambda s: "UTF8x" + str(get_max_utf8_bytes_char_length(s)),
    )
    @mark.parametrize(
        "cls", [BytesTracer, StringTracer, StringUcpTracer], ids=format_test_params
    )
    def test_line_len_doesnt_exceed_max(
        self, max_width: int | None, input: t.AnyStr, cls: t.Type[AbstractTracer]
    ):
        if cls == BytesTracer:
            input = input.encode()
        if not max_width:
            max_width = get_terminal_width()
        output = cls(max_width).apply(input)
        actual = max(map(len, output.splitlines()))
        assert actual <= max_width

    def test_empty_input(self):
        assert StringTracer().apply("").rstrip("\n") == ""

    def test_input_cast(self):
        assert dump([1, 2, 3], "input cast", StringTracer) == (
            "input cast_________________________________________\n"
            " 0 | 5b 31 2c 20 32 2c 20 33 5d |[1,␣2,␣3]         \n"
            "------------------------------------------------(9)\n"
        )

    @mark.xfail(raises=ValueError)
    def test_too_low_limit(self):
        assert StringTracer(1).apply(".")

    @mark.parametrize(
        "input, expected",
        [
            ["\x00", 1],
            ["й", 2],
            ["₿", 3],
            ["𐍈", 4],
            ["123", 1],
            ["qё", 2],  # noqa
            ["\x04█₼", 3],  # noqa
            ["z𐊣", 4],  # noqa
            ["", 0],
        ],
    )
    def test_get_max_utf8_bytes_char_length(self, input: str, expected: int):
        assert get_max_utf8_bytes_char_length(input) == expected

    @mark.parametrize(
        "input, expected",
        [
            ["\x00", 1],
            ["a", 2],
            ["й", 3],
            ["ᄑ", 4],
            ["𐨀", 5],
            ["􁄑", 6],
            ["\x0f\x00\x04", 1],
            ["\x0a!@#", 2],
            ["я90", 3],
            ["\x01攲", 4],  # noqa
            ["Й🚒0", 5],
            ["𐍂0𐐑􀢈", 6],
            ["", 0],
        ],
    )
    def test_get_max_ucs_chars_cp_length(self, input: str, expected: int):
        assert get_max_ucs_chars_cp_length(input) == expected


class TestReplacerChain:
    @mark.parametrize(
        "input_fname, expected_fname",
        [
            ["test_rplcha_inp.txt", "test_rplcha_exp.ansi"],
        ],
    )
    @mark.setup(force_output_mode="xterm_16")
    def test_replacer_chain(self, input_fname: str, expected_fname: str):
        class RenderingReplacer(StringReplacer):
            def __init__(self, pattern: PTT[str], st: Style):
                self._st = st
                super().__init__(pattern, self._render)

            def _render(self, m: t.Match) -> str:
                return render(m.group(0), self._st)

        filters = [
            StringReplacerChain(
                re.compile(R".*pytermor.*"),
                StringReplacer(R".py", "   "),
                NonPrintsStringVisualizer(),
                StringReplacer(R"\B(␣+)\B", lambda m: len(m[0]) * "."),
                StringReplacer(R"␣", lambda m: " "),
                RenderingReplacer(R"(?<=pytermor/)\w+", Style(bg="black", bold=True)),
                RenderingReplacer("100%", Style(fg="green")),
                RenderingReplacer(R"(?<=\D)([89]\d%).*", Style(fg="yellow")),
                RenderingReplacer(R"\s([^89]\d%).*", Style(fg="red")),
            ),
            RenderingReplacer("%", Style(dim=True)),
        ]
        output = apply_filters(load_data_file(input_fname), *filters).rstrip("\n")
        assert output == load_data_file(expected_fname).rstrip("\n")


class TestAbbrevNames:
    @mark.parametrize(
        "cls",
        sorted(get_subclasses(IFilter), key=lambda c: get_qname(c)),
        ids=format_test_params,
    )
    def test_abbrev_name(self, cls: t.Type[IFilter]):
        assert cls.get_abbrev_name()
