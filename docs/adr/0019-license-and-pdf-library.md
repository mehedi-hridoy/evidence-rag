# ADR-0019: Project License and PDF Processing Library

- Status: accepted
- Date: 2026-10-31

## Context

EvidenceRAG is distributed under the MIT License. The original PRD selected PyMuPDF for PDF text extraction.

PyMuPDF is available under AGPL-3.0 or a commercial license. Its use introduces licensing considerations that could conflict with our goal of keeping EvidenceRAG permissively licensed and easily reusable by individuals and companies.

Our v1 requirement is limited to extracting text from text-based PDFs while retaining enough structural information to preserve headings and document sections. Scanned PDFs and OCR are out of scope.

We therefore need a PDF extraction library that satisfies these requirements without introducing unnecessary licensing complexity.

## Options considered

1. **pdfplumber (MIT):** Provides text extraction and layout information. Built on pdfminer.six, which is also MIT-licensed.
2. **pypdf (BSD-3-Clause):** Provides PDF text extraction with a relatively lightweight implementation, but offers different layout extraction capabilities.
3. **PyMuPDF (AGPL-3.0 / Commercial):** Provides fast, feature-rich PDF processing with layout information, but introduces additional licensing considerations.
4. **Commercial PyMuPDF license:** Retains PyMuPDF capabilities under an appropriate commercial licensing arrangement, with additional cost.

## Decision

Keep EvidenceRAG under the MIT License and use pdfplumber for PDF text extraction.

pdfplumber satisfies the current text-based PDF ingestion requirements and provides useful layout information while aligning with our permissive licensing goals.

The parser will remain replaceable through the existing parser registry in `backend/.../adapters/parsers/`. The ingestion service will depend on the parser boundary and its `ParsedDocument` output, not on pdfplumber directly.

We will not introduce a separate parser interface or abstraction because the existing function registry provides the required replacement boundary.

## Consequences (trade-offs accepted)

- EvidenceRAG retains its MIT License.
- PDF extraction uses pdfplumber instead of PyMuPDF.
- pdfplumber may have lower extraction throughput than native-library-based alternatives.
- We accept this performance trade-off for v1 because PDF extraction occurs during background ingestion, outside the chat request path.
- Embedding generation may also contribute significantly to ingestion time; actual bottlenecks must be measured rather than assumed.
- pdfplumber and its relevant dependency licences, including pdfminer.six, must be checked against the versions recorded in the dependency lockfile.
- PDF extraction performance will be measured separately from normalization, chunking, embedding and storage during ingestion.
- Replacing the PDF library should require changing the PDF parser implementation, not the ingestion service.

## Revisit if

- PDF extraction becomes a measurable ingestion bottleneck.
- Corpus size or document complexity increases substantially.
- Benchmarking demonstrates a meaningful performance improvement with another parser without compromising extraction quality or licensing goals.
- New PDF requirements exceed pdfplumber's capabilities.
- Project licensing or distribution goals change.