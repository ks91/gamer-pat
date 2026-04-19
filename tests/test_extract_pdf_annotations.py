import importlib.util
from pathlib import Path
import sys
from unittest import TestCase, mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_pdf_annotations.py"
SPEC = importlib.util.spec_from_file_location("extract_pdf_annotations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def make_word(text, x_min, x_max, y_min=10.0, y_max=20.0):
    return MODULE.Word(text=text, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)


class JoinWordsWithLayoutTests(TestCase):
    def test_inserts_spaces_for_english_words(self):
        words = [
            make_word("A", 0.0, 5.0),
            make_word("Case", 8.0, 28.0),
            make_word("Study", 31.0, 55.0),
        ]
        self.assertEqual(MODULE.join_words_with_layout(words), "A Case Study")

    def test_keeps_cjk_without_inserted_spaces(self):
        words = [
            make_word("早稲田", 0.0, 20.0),
            make_word("大学", 24.0, 40.0),
        ]
        self.assertEqual(MODULE.join_words_with_layout(words), "早稲田大学")

    def test_avoids_space_before_punctuation(self):
        words = [
            make_word("Miro", 0.0, 18.0),
            make_word(",", 20.0, 22.0),
        ]
        self.assertEqual(MODULE.join_words_with_layout(words), "Miro,")

    def test_keeps_japanese_punctuation_tight(self):
        words = [
            make_word("早稲田大学", 0.0, 40.0),
            make_word("、", 43.0, 46.0),
            make_word("経営学研究科", 49.0, 95.0),
        ]
        self.assertEqual(MODULE.join_words_with_layout(words), "早稲田大学、経営学研究科")

    def test_keeps_japanese_and_ascii_mixed_text_without_forced_spaces(self):
        words = [
            make_word("AI", 0.0, 12.0),
            make_word("と", 15.0, 20.0),
            make_word("MBA", 23.0, 41.0),
        ]
        self.assertEqual(MODULE.join_words_with_layout(words), "AIとMBA")


class BuildAnnotationsRegressionTests(TestCase):
    def test_preserves_spaces_in_target_and_context(self):
        fake_pdf = (
            b"1 0 obj\n<< /Type /Page >>\nendobj\n"
            b"2 0 obj\n<< /Subtype/Highlight /P 1 0 R "
            b"/QuadPoints [0 90 55 90 0 80 55 80] "
            b"/Contents(test comment) >>\nendobj\n"
        )

        words = [
            make_word("A", 0.0, 5.0),
            make_word("Case", 8.0, 28.0),
            make_word("Study", 31.0, 55.0),
        ]
        lines = [
            MODULE.Line(
                text=MODULE.join_words_with_layout(words),
                x_min=0.0,
                y_min=0.0,
                x_max=55.0,
                y_max=20.0,
            )
        ]

        with mock.patch.object(Path, "read_bytes", return_value=fake_pdf):
            with mock.patch.object(
                MODULE,
                "load_pages_from_bbox",
                return_value=({1: words}, {1: lines}, {1: 100.0}),
            ):
                annots = MODULE.build_annotations(Path("commented.pdf"), Path("clean.pdf"))

        self.assertEqual(len(annots), 1)
        self.assertEqual(annots[0].target, "A Case Study")
        self.assertEqual(annots[0].context, "A Case Study")
        self.assertEqual(annots[0].comment, "test comment")

    def test_preserves_japanese_target_and_context(self):
        fake_pdf = (
            b"1 0 obj\n<< /Type /Page >>\nendobj\n"
            b"2 0 obj\n<< /Subtype/Highlight /P 1 0 R "
            b"/QuadPoints [0 90 95 90 0 80 95 80] "
            b"/Contents(\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e\xe3\x82\xb3\xe3\x83\xa1\xe3\x83\xb3\xe3\x83\x88) >>\nendobj\n"
        )

        words = [
            make_word("早稲田大学", 0.0, 40.0),
            make_word("、", 43.0, 46.0),
            make_word("経営学研究科", 49.0, 95.0),
        ]
        lines = [
            MODULE.Line(
                text=MODULE.join_words_with_layout(words),
                x_min=0.0,
                y_min=0.0,
                x_max=95.0,
                y_max=20.0,
            )
        ]

        with mock.patch.object(Path, "read_bytes", return_value=fake_pdf):
            with mock.patch.object(
                MODULE,
                "load_pages_from_bbox",
                return_value=({1: words}, {1: lines}, {1: 100.0}),
            ):
                annots = MODULE.build_annotations(Path("commented.pdf"), Path("clean.pdf"))

        self.assertEqual(len(annots), 1)
        self.assertEqual(annots[0].target, "早稲田大学、経営学研究科")
        self.assertEqual(annots[0].context, "早稲田大学、経営学研究科")
        self.assertEqual(annots[0].comment, "日本語コメント")

    def test_extracts_text_annotation_near_figure(self):
        fake_pdf = (
            b"1 0 obj\n<< /Type /Page >>\nendobj\n"
            b"2 0 obj\n<< /Subtype/Text /P 1 0 R "
            b"/Rect [60 64 84 88] "
            b"/Contents(figure note) >>\nendobj\n"
        )

        lines = [
            MODULE.Line(text="write before discussion", x_min=15.0, y_min=35.0, x_max=120.0, y_max=47.0),
            MODULE.Line(text="persistent visual record", x_min=15.0, y_min=50.0, x_max=130.0, y_max=62.0),
        ]

        with mock.patch.object(Path, "read_bytes", return_value=fake_pdf):
            with mock.patch.object(
                MODULE,
                "load_pages_from_bbox",
                return_value=({1: []}, {1: lines}, {1: 120.0}),
            ):
                annots = MODULE.build_annotations(Path("commented.pdf"), Path("clean.pdf"))

        self.assertEqual(len(annots), 1)
        self.assertEqual(annots[0].target, "write before discussion")
        self.assertIn("write before discussion", annots[0].context)
        self.assertEqual(annots[0].comment, "figure note")
