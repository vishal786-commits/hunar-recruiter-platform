# Hunar Recruiter Platform

An AI-powered recruiter workflow built as part of the **Hunar.ai Forward Deployed Engineer (FDE) assignment**.

The platform is designed to help a recruiter move from an unstructured Job Description (JD) to candidate discovery, candidate selection, AI voice screening, and eventually a unified recruiter dashboard.

The project focuses on building a practical, integration-driven system around **JD understanding, candidate sourcing, intelligent Hunar agent selection, human-in-the-loop approval, and automated voice screening**.

![Architecture](image.png)

---

## Overview

The platform follows this workflow:

```text
Job Description
      │
      ▼
JD Ingestion
(TXT / PDF / DOCX)
      │
      ▼
JD Parsing
      │
      ▼
Structured Job Description
      │
      ├──────────────────────────────┐
      ▼                              ▼
Candidate Search                Agent Routing
      │                              │
      ▼                              ▼
Candidate Normalization       Hunar Agent Registry
      │                              │
      ▼                              ▼
Candidate Matching / Ranking   Selected Hunar Agent
      │
      ▼
Recruiter Review & Approval
      │
      ▼
Hunar Voice Screening
      │
      ▼
Call Results / Transcript
      │
      ▼
SQLite Database
      │
      ▼
Recruiter Dashboard