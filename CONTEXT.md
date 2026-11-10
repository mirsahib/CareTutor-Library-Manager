# Project Context & Candidate Assessment Guide

## 1. Candidate Context
- **Candidate Knowledge Level:** Currently learning Python Flask, SQLite, and AngularJS 1.8 concurrently.
- **Constraints:** 48-hour total turnaround window for Part 1 submission.
- **Primary Goal:** Successfully complete a clean, fully functional submission that passes all specified acceptance criteria and prepares the candidate for the Part 2 in-person technical evaluation.

---

## 2. Assessment Structure Overview

### Part 1: Home Task (Current Phase)
- **Time Commitment:** ~2-3 hours of coding effort within a 48-hour deadline.
- **Deliverables:**
  - Public/Private GitHub Repository with distinct subfolders: `backend/` and `frontend/`.
  - Comprehensive `README.md` covering setup, seeding, running, and testing instructions.
  - Granular Git commit history demonstrating incremental code evolution.
  - Written reflections in `README.md`:
    1. *Future Improvements:* What would be refactored given additional time.
    2. *AI Tools Disclosure:* Explicit documentation of where AI assistants were utilized.

### Part 2: In-Person Office Session (50 Minutes)
Candidates will bring their laptop with the Part 1 submission ready to run locally.
1. **10 Mins:** App demonstration and code walkthrough.
2. **20 Mins:** Live coding — implementing a new feature on top of the Part 1 codebase.
3. **10 Mins:** Debugging session — identifying and fixing bugs in a provided snippet.
4. **10 Mins:** Technical Q&A on AngularJS 1.8 and Flask fundamentals.

---

## 3. Evaluation Criteria (What Reviewers Look For)
- **Functional Completeness:** All 5 user stories working without unhandled exceptions.
- **Code Cleanliness:** Clear folder organization, separation of concerns (API calls in service, clean SQLite connection isolation).
- **API Robustness:** Strict adherence to HTTP status codes (`200`, `201`, `204`, `400`, `404`, `409`) and non-crashing JSON error responses.
- **Readability & Explainability:** The candidate must fully understand every line of code generated in Part 1 to successfully pass Part 2 live modifications.