from copy import deepcopy
from datetime import date
import unittest

from humanifest.review import render_source_review, source_review


class SourceReviewTests(unittest.TestCase):
    def review(self, sources, **kwargs):
        return source_review([{"id": "project", "sources": sources}], [],
                             as_of=date(2026, 9, 8), max_age_days=30, **kwargs)

    def source(self, source_id, accessed, url="https://example.test/source"):
        return {"id": source_id, "accessed": accessed, "url": url}

    def test_window_boundary_is_inclusive_and_future_dates_are_flagged(self):
        result = self.review([
            self.source("cutoff", "2026-08-09"),
            self.source("old", "2026-08-08"),
            self.source("future", "2026-09-09"),
        ])
        by_id = {entry["source_id"]: entry for entry in result["sources"]}
        self.assertEqual(by_id["cutoff"]["review_reasons"], [])
        self.assertEqual(by_id["old"]["review_reasons"], ["older-than-window"])
        self.assertEqual(by_id["future"]["review_reasons"], ["future-date"])
        self.assertEqual(by_id["future"]["age_days"], -1)
        self.assertEqual(result["sources_needing_review"], 2)

    def test_local_files_keep_both_age_and_accessibility_reasons(self):
        result = self.review([
            self.source("local", "2026-08-01", "file:///private/tmp/evidence"),
            self.source("recent-local", "2026-09-08", "file://localhost/tmp/evidence"),
        ])
        self.assertEqual(result["sources"][0]["review_reasons"], ["older-than-window", "local-file"])
        self.assertEqual(result["sources"][1]["review_reasons"], ["local-file"])

    def test_filter_keeps_portfolio_totals_and_record_context(self):
        result = self.review([self.source("old", "2026-08-01"), self.source("new", "2026-09-08")],
                             needs_review_only=True)
        self.assertEqual(result["total_sources"], 2)
        self.assertEqual(result["sources_needing_review"], 1)
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["sources"][0]["record_type"], "project")
        self.assertEqual(result["sources"][0]["record_id"], "project")

    def test_repeated_urls_are_not_merged_across_records_or_dates(self):
        projects = [{"id": "same", "sources": [self.source("s1", "2026-09-08")]}]
        opportunities = [{"id": "same", "sources": [self.source("s1", "2026-08-01")]}]
        before = deepcopy((projects, opportunities))
        result = source_review(projects, opportunities, as_of=date(2026, 9, 8), max_age_days=30)
        self.assertEqual(result["total_sources"], 2)
        self.assertEqual({entry["record_type"] for entry in result["sources"]}, {"project", "opportunity"})
        self.assertEqual((projects, opportunities), before)

    def test_optional_cause_sources_keep_cause_provenance(self):
        causes = [{"id": "malaria", "sources": [self.source("who", "2026-08-01")]}]
        review = source_review([], [], as_of=date(2026, 9, 8), max_age_days=30,
                               needs_review_only=True, causes=causes)
        self.assertEqual(review["sources_needing_review"], 1)
        self.assertEqual(review["sources"][0]["record_type"], "cause")
        self.assertEqual(review["sources"][0]["record_id"], "malaria")
        self.assertEqual(review["sources"][0]["source_id"], "who")

    def test_output_does_not_depend_on_record_or_source_input_order(self):
        sources = [self.source("b", "2026-09-08"), self.source("a", "2026-09-08")]
        self.assertEqual(self.review(sources), self.review(list(reversed(sources))))

    def test_zero_day_window_and_leap_day(self):
        result = source_review([], [{"id": "opp", "sources": [self.source("leap", "2024-02-29")]}],
                               as_of=date(2024, 3, 1), max_age_days=0)
        self.assertEqual(result["sources"][0]["age_days"], 1)
        self.assertEqual(result["sources_needing_review"], 1)

    def test_invalid_review_windows_are_rejected(self):
        for age in [-1, True, 1.5, "30"]:
            with self.assertRaises(ValueError):
                source_review([], [], as_of=date(2026, 9, 8), max_age_days=age)

    def test_empty_filtered_output_is_explicit(self):
        result = self.review([self.source("new", "2026-09-08")], needs_review_only=True)
        text = render_source_review(result)
        self.assertIn("No sources match this review filter", text)
        self.assertIn("Sources: 1; needing review: 0", text)
        self.assertIn("no sources fetched", text)
