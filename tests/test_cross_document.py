import unittest
from unittest.mock import patch

from kb import cross_document


class FakePlan:
    topic = ["program"]


class CrossDocumentTests(unittest.TestCase):
    def test_deduplicates_and_preserves_sources(self):
        def search_chunks(db, plan, top_k, ids, **kw):
            if not ids:
                return ([{"doc_id": "d1", "title": "Doc 1", "chunk_id": "c1", "text": "evidence", "score": 1.0}], ["fulltext"])
            return ([{"doc_id": "d1", "title": "Doc 1", "chunk_id": "c1", "text": "duplicate", "score": .9},
                     {"doc_id": "d2", "title": "Doc 2", "chunk_id": "c2", "text": "linked evidence", "score": .8}], ["graph"])

        links = [{"doc_id": "d2", "title": "Doc 2", "shared": [{"kind": "Tag", "name": "program"}]}]
        with patch.object(cross_document, "analyze", return_value=FakePlan()), \
             patch.object(cross_document.search, "search_chunks", side_effect=search_chunks), \
             patch.object(cross_document.search, "expand_graph", return_value=links):
            result = cross_document.retrieve(object(), "program details", 5)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["document_ids"], ["d1", "d2"])
        self.assertEqual([item["chunk_id"] for item in result["evidence"]], ["c1", "c2"])
        self.assertEqual(result["citations"][1]["doc_id"], "d2")
        self.assertEqual(result["graph_links"][0]["doc_id"], "d2")


if __name__ == "__main__":
    unittest.main()
