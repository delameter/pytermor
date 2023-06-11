# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest
from pytest import mark

from pytermor import Fragment, Style, render
from pytermor.ansi import SeqIndex
from pytermor.common import get_qname, get_subclasses
from pytermor.filter import *
from tests import format_test_params, load_data_file


@mark.setup(force_output_mode="true_color")
class TestStringAligner:
    @mark.parametrize(
        "expected,align,width",
        [
            ("\x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m" "   ", Align.LEFT, 9),
            ("  \x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m ", Align.CENTER, 9),
            ("   \x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m", Align.RIGHT, 9),
        ],
    )
    def test_sgr_aware_mode(self, expected: str, align: Align, width: int):
        inp = render(Fragment("123", "red") + Fragment("456", "blue"))
        actual = StringAligner(align, width, sgr_aware=True).apply(inp)
        assert actual == expected


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


class TestReplacers:  # @TODO
    def test_replace_sgr_filter(self):
        actual = SgrStringReplacer().apply(f"{SeqIndex.RED}213{SeqIndex.RESET}")
        expected = "213"
        assert actual == expected


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
        ["f" * 64, "qй" * 32, "晦࢈ຮ" * 16, "·＊🐶𑼑􏿿" * 8],
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

    @mark.parametrize("input_cp, expected", [
        [0, 1],
    ])
    def test_offset_max_ucs_chars_cp_length(self, input_cp: int, expected: int):
        assert get_max_ucs_chars_cp_length(chr(input_cp)) == expected


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
