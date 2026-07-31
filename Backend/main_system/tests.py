"""Tests for the API surface and the agent-orchestration service.

No test here reaches OpenAI: every agent factory is replaced with a stub that
returns a canned response, and the PDF extractor is stubbed the same way. The
point is to pin the logic around the model calls -- score conversion, UUID
validation, upload rules, orphan cleanup -- not the model itself.
"""

import os
import tempfile
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from main_system.models import Document, Question, UserAnswer
from main_system.services.recall_service import grade_answer, process_pdf


def stub_agent(response):
    """An object shaped like a BaseAgent whose run() returns `response`."""
    return SimpleNamespace(run=lambda _input: response)


class GradeAnswerTests(TestCase):
    """The grader speaks in 0 / 0.5 / 1; the database stores 0 / 50 / 100."""

    def setUp(self):
        document = Document.objects.create(
            title="Doc", file_path="uploads/doc.pdf", content="body", page_count=1
        )
        self.question = Question.objects.create(
            document=document,
            question_text="What is a cell membrane?",
            answer_explanation="A selectively permeable boundary.",
        )

    def grade_with_score(self, score, feedback="Some feedback."):
        answer = UserAnswer.objects.create(question=self.question, user_answer="An answer")

        graded = SimpleNamespace(score=score, feedback=feedback)
        with patch("main_system.services.recall_service.require_api_key"), patch(
            "main_system.services.recall_service.build_grading_agent",
            return_value=stub_agent(graded),
        ):
            return grade_answer(answer.answer_id)

    def test_score_zero_becomes_mark_zero(self):
        self.assertEqual(self.grade_with_score(0).mark, 0)

    def test_score_half_becomes_mark_fifty(self):
        self.assertEqual(self.grade_with_score(0.5).mark, 50)

    def test_score_one_becomes_mark_hundred(self):
        self.assertEqual(self.grade_with_score(1).mark, 100)

    def test_feedback_is_persisted(self):
        graded = self.grade_with_score(0.5, feedback="You named the boundary but not its selectivity.")
        graded.refresh_from_db()
        self.assertEqual(graded.feedback, "You named the boundary but not its selectivity.")

    def test_mark_zero_survives_the_round_trip_to_the_api(self):
        """A wrong answer scores 0, which must not read back as 'not answered'."""
        self.grade_with_score(0)

        response = self.client.get(f"/api/documents/{self.question.document.document_id}/questions/")
        question_payload = response.json()["questions"][0]

        self.assertTrue(question_payload["has_been_answered"])
        self.assertEqual(question_payload["last_mark"], 0)


class ProcessPdfTests(TestCase):
    """The upload pipeline, with the extractor and both agents stubbed out."""

    def setUp(self):
        handle, self.pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.close(handle)
        self.addCleanup(lambda: os.path.exists(self.pdf_path) and os.remove(self.pdf_path))

        # An absolute file_path makes recall_service's os.path.join a no-op,
        # which keeps the test off the real uploads directory.
        self.document = Document.objects.create(
            title="Doc", file_path=self.pdf_path, content="", page_count=0
        )

        self.extraction = SimpleNamespace(
            content="Mitochondria produce ATP.",
            metadata=SimpleNamespace(
                num_pages=3, title="Biology", author="A. Author", created_date=None
            ),
        )

    def run_pipeline(self, questions, explanations):
        with patch("main_system.services.recall_service.require_api_key"), patch.object(
            __import__("main_system.services.recall_service", fromlist=["pdf_tool"]),
            "pdf_tool",
            SimpleNamespace(run=lambda _input: self.extraction),
        ), patch(
            "main_system.services.recall_service.build_question_agent",
            return_value=stub_agent(SimpleNamespace(questions=questions)),
        ), patch(
            "main_system.services.recall_service.build_answer_agent",
            return_value=stub_agent(SimpleNamespace(explanations=explanations)),
        ):
            return process_pdf(self.document.document_id)

    def test_questions_are_paired_with_their_explanations(self):
        created = self.run_pipeline(["Q1", "Q2"], ["E1", "E2"])

        self.assertEqual(len(created), 2)
        self.assertEqual(
            [(q.question_text, q.answer_explanation) for q in created],
            [("Q1", "E1"), ("Q2", "E2")],
        )

    def test_document_metadata_is_stored(self):
        self.run_pipeline(["Q1"], ["E1"])
        self.document.refresh_from_db()

        self.assertEqual(self.document.content, "Mitochondria produce ATP.")
        self.assertEqual(self.document.page_count, 3)
        self.assertEqual(self.document.title, "Biology")

    def test_mismatched_explanation_count_raises_instead_of_dropping_questions(self):
        """zip() would have silently produced two questions out of three."""
        with self.assertLogs("main_system.services.recall_service", level="ERROR"):
            with self.assertRaises(ValueError):
                self.run_pipeline(["Q1", "Q2", "Q3"], ["E1", "E2"])

        self.assertEqual(Question.objects.count(), 0)


class UploadEndpointTests(TestCase):
    URL = "/api/documents/upload/"

    def test_get_is_not_allowed(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"], "Method not allowed")

    def test_non_pdf_upload_is_rejected(self):
        upload = SimpleUploadedFile("notes.txt", b"plain text", content_type="text/plain")

        response = self.client.post(self.URL, {"file": upload})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Only PDF files are supported")
        self.assertEqual(Document.objects.count(), 0)

    def test_missing_file_is_rejected(self):
        response = self.client.post(self.URL, {})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No file uploaded")

    def test_successful_upload_stores_a_uuid_prefixed_filename(self):
        with tempfile.TemporaryDirectory() as base_dir:
            with self.settings(BASE_DIR=base_dir), patch(
                "main_system.views.process_pdf", return_value=[]
            ):
                upload = SimpleUploadedFile("notes.pdf", b"%PDF-1.4", content_type="application/pdf")
                response = self.client.post(self.URL, {"file": upload})

            self.assertEqual(response.status_code, 200)

            document = Document.objects.get()
            stored_name = os.path.basename(document.file_path)
            self.assertTrue(stored_name.endswith("_notes.pdf"))
            self.assertNotEqual(stored_name, "notes.pdf")
            self.assertTrue(os.path.exists(os.path.join(base_dir, document.file_path)))

    def test_failed_processing_leaves_no_document_and_no_orphaned_file(self):
        with tempfile.TemporaryDirectory() as base_dir:
            with self.settings(BASE_DIR=base_dir), patch(
                "main_system.views.process_pdf", side_effect=RuntimeError("model exploded")
            ), self.assertLogs("main_system.views", level="ERROR"):
                upload = SimpleUploadedFile("notes.pdf", b"%PDF-1.4", content_type="application/pdf")
                response = self.client.post(self.URL, {"file": upload})

            self.assertEqual(response.status_code, 500)
            self.assertEqual(Document.objects.count(), 0)
            self.assertEqual(os.listdir(os.path.join(base_dir, "uploads")), [])

    def test_internal_errors_are_not_leaked_to_the_client(self):
        with tempfile.TemporaryDirectory() as base_dir:
            with self.settings(BASE_DIR=base_dir), patch(
                "main_system.views.process_pdf",
                side_effect=RuntimeError("sk-secret-looking-detail at /srv/app/x.py"),
            ), self.assertLogs("main_system.views", level="ERROR") as logged:
                upload = SimpleUploadedFile("notes.pdf", b"%PDF-1.4", content_type="application/pdf")
                response = self.client.post(self.URL, {"file": upload})

        self.assertNotIn("sk-secret-looking-detail", response.json()["error"])
        self.assertNotIn("/srv/app", response.json()["error"])
        # ...but it is still recoverable from the server's own logs.
        self.assertIn("sk-secret-looking-detail", "\n".join(logged.output))


class MalformedUuidTests(TestCase):
    """`except (ValueError, uuid.ValueError)` used to raise AttributeError here,
    turning every one of these into a 500."""

    def test_document_detail(self):
        response = self.client.get("/api/documents/not-a-uuid/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid document ID format")

    def test_document_questions(self):
        response = self.client.get("/api/documents/not-a-uuid/questions/")
        self.assertEqual(response.status_code, 400)

    def test_question_detail(self):
        response = self.client.get("/api/questions/not-a-uuid/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid question ID format")

    def test_answer_detail(self):
        response = self.client.get("/api/answers/not-a-uuid/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid answer ID format")

    def test_submit_answer(self):
        response = self.client.post(
            "/api/questions/not-a-uuid/answer/",
            data='{"answer": "hi"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid question ID format")


class SubmitAnswerTests(TestCase):
    def setUp(self):
        document = Document.objects.create(
            title="Doc", file_path="uploads/doc.pdf", content="body", page_count=1
        )
        self.question = Question.objects.create(
            document=document, question_text="Q?", answer_explanation="E."
        )
        self.url = f"/api/questions/{self.question.question_id}/answer/"

    def post(self, body):
        return self.client.post(self.url, data=body, content_type="application/json")

    def test_grade_and_feedback_are_returned(self):
        graded = SimpleNamespace(score=0.5, feedback="Half right.")
        with patch("main_system.services.recall_service.require_api_key"), patch(
            "main_system.services.recall_service.build_grading_agent",
            return_value=stub_agent(graded),
        ):
            response = self.post('{"answer": "A partial answer"}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mark"], 50)
        self.assertEqual(response.json()["feedback"], "Half right.")

    def test_unknown_question_is_a_404(self):
        response = self.client.post(
            f"/api/questions/{uuid.uuid4()}/answer/",
            data='{"answer": "hi"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_json_is_rejected(self):
        response = self.post("this is not json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON data")

    def test_empty_answer_is_rejected(self):
        response = self.post('{"answer": ""}')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No answer provided")

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class ContentExtractorTests(TestCase):
    """The extractor must not flatten distinguishable failures into Exception."""

    def test_missing_file_raises_file_not_found(self):
        from main_system.tools.content_extractor import (
            PDFExtractorTool,
            PDFExtractorToolInputSchema,
        )

        with self.assertRaises(FileNotFoundError):
            PDFExtractorTool().run(PDFExtractorToolInputSchema(file_path="no-such-file.pdf"))

    def test_unreadable_file_raises_runtime_error_with_the_cause_attached(self):
        from main_system.tools.content_extractor import (
            PDFExtractorTool,
            PDFExtractorToolInputSchema,
        )

        handle, path = tempfile.mkstemp(suffix=".pdf")
        os.write(handle, b"definitely not a pdf")
        os.close(handle)
        self.addCleanup(os.remove, path)

        with self.assertRaises(RuntimeError) as caught:
            PDFExtractorTool().run(PDFExtractorToolInputSchema(file_path=path))

        self.assertIsNotNone(caught.exception.__cause__)
