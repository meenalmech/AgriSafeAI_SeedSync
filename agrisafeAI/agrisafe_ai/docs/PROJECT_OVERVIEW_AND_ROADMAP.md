# AgriSafe AI: Project Overview and Roadmap

## 1. Project Overview

AgriSafe AI is a farm-task safety decision-support application for Malaysian farmers and field workers. A user records a planned task, crop, time, location, weather, chemical, PPE status, equipment, crew size, prior outdoor exposure, and selected worker risk flags. The application evaluates the information and returns one of four outcomes:

- `PROCEED`
- `MODIFY`
- `DELAY`
- `AVOID`

The main safety decision is produced by deterministic rules in the risk engine. The result includes reasons and recommended actions so a farmer can understand what contributed to the outcome. The app is not a substitute for product labels, Safety Data Sheets (SDS), farm procedures, medical advice, or a formal occupational safety assessment.

## 2. Technology

- **Backend:** Python and FastAPI
- **Risk logic:** Deterministic rule-based scoring
- **Database:** SQLite through SQLAlchemy
- **Weather:** Open-Meteo integration with a demo fallback
- **Frontend:** Static HTML, CSS, and JavaScript served by FastAPI
- **Documents:** PDF and text extraction, plus local knowledge retrieval
- **Deployment:** Docker and Docker Compose support
- **Default interface language:** Bahasa Melayu, with English available in the assessment form
- **Default local port:** `8011`

## 3. Current Functionality

### Safety assessment

- Task, crop, growth stage, planned date/time, location, equipment, and worker count inputs
- Weather inputs and forecast lookup
- Chemical reference lookup for the included demonstration products
- PPE confirmation and worker flags for pregnancy, respiratory concerns, and heat acclimatisation
- Risk score, severity, decision, triggered rules, reasons, and recommended actions
- Heat work/rest and hydration guidance
- Chemical-based PPE suggestions and demo re-entry / pre-harvest timing
- Safer-window comparison using the current deterministic/demo forecast candidates
- Assessment history

### Farmer and farm records

- Create a farmer profile and receive a local API key
- Create farms and plots with crop and area details
- Record near misses, chemical exposure, heat illness, and injuries
- Queue SMS, WhatsApp, or email messages for a future delivery integration
- Export an HTML or CSV HIRARC-style report

### Supporting features

- Malay emergency guidance for chemical exposure and heat illness
- Task and chemical catalogue endpoints
- Demo scenarios for presentation use
- PDF and text document extraction
- Local knowledge search

## 4. Running Locally

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn agrisafe_ai.app.main:app --host 0.0.0.0 --port 8011
```

Open the app at `http://localhost:8011`. API documentation is available at `http://localhost:8011/docs`.

Run tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 5. Useful API Routes

- `GET /api/health` - service health
- `GET /api/tasks` - task catalogue
- `GET /api/chemicals` - configured chemical reference records
- `GET /api/weather` - weather lookup
- `POST /api/assessments` - evaluate a planned task
- `GET /api/assessments` - recent assessment history
- `POST /api/safer-windows` - compare candidate work windows
- `GET /api/emergency?language=ms` - emergency guidance
- `POST /api/farmers` - create a local farmer profile
- `GET /api/farms` and `POST /api/farms` - list and create farms
- `GET /api/farms/{farm_id}/plots` and `POST /api/farms/{farm_id}/plots` - list and create plots
- `GET /api/incidents` and `POST /api/incidents` - list and record incidents
- `POST /api/alerts` - queue an alert message
- `GET /api/reports/hirarc.csv` - download CSV report
- `GET /api/reports/hirarc.html` - open printable HTML report

Farmer and farm-management routes currently use the `X-Farmer-Key` header. The key is a prototype credential, not production-grade authentication.

## 6. Important Prototype Limitations

The application is suitable for demonstrations and continued development, but it is not yet ready to make independent real-world safety decisions:

- The included chemical records are demonstration data, not an authoritative pesticide/SDS database.
- Re-entry intervals, pre-harvest intervals, and PPE values must be checked against the exact product label and current local requirements.
- A HIRARC-style export is a record format only; it is not a DOSH-approved or formally validated HIRARC assessment.
- Alert messages are queued; the app does not deliver SMS, WhatsApp, or email without a configured provider.
- Farmer API keys are issued locally and lack production identity, password recovery, access revocation, and role management.
- Farm, plot, incident, and assessment data need stronger ownership scoping before use by multiple real customers. Current report/history behavior is prototype-level and must not be treated as tenant-isolated.
- Demo safer windows use fixed example conditions; they are not a verified 24-72-hour operational forecast.
- There is no complete offline synchronization or conflict resolution yet.
- Work/rest guidance is indicative prototype guidance and must be reviewed by qualified occupational-health and safety specialists before operational use.

## 7. Recommended Roadmap

### Priority 1: Data safety and trustworthy decisions

1. **Tenant isolation and access control**
   - Replace prototype API keys with secure authentication and password recovery.
   - Add roles such as farmer, worker, and supervisor.
   - Attach every assessment, incident, plot, and report to the owning farm and enforce ownership on every query.
   - Add audit logs for edits, report downloads, and overrides.

2. **Authoritative chemical and SDS workflow**
   - Integrate a maintained, legally usable chemical reference source.
   - Store active ingredient, concentration, formulation, hazard class, label/SDS version, required PPE, re-entry interval, pre-harvest interval, and source/update date.
   - Require confirmation against the exact product label when data is missing or ambiguous.
   - Extract SDS documents for review, but require human confirmation before extracted values affect a safety decision.

3. **Risk engine validation**
   - Review thresholds with Malaysian agricultural and occupational-safety experts.
   - Add rule provenance, threshold explanations, uncertainty, and confidence where appropriate.
   - Build scenario tests for different crops, tasks, worker profiles, and weather conditions.
   - Keep hard safety blocks separate from advisory scoring; do not let an AI model override hard rules.

### Priority 2: Field reliability

4. **Offline-first operation**
   - Cache the app shell and reference data with a service worker.
   - Save drafts and queued incidents locally when there is no connection.
   - Synchronize safely when online, with visible sync state and conflict handling.
   - Clearly distinguish cached weather from live forecasts and show its timestamp.

5. **Real alerts and task scheduling**
   - Add a background scheduler for evening-before reminders and forecast-change checks.
   - Integrate a provider such as an approved SMS gateway or WhatsApp Business provider.
   - Track delivery, failure, retry, opt-out, language, and consent status.
   - Escalate critical alerts only under clearly defined policies.

6. **Task completion and exposure tracking**
   - Record actual start/end time, workers involved, PPE used, whether recommendations were followed, and post-task feedback.
   - Track cumulative heat and chemical exposure by worker and week.
   - Provide supervisor views for active tasks and unresolved incidents.

### Priority 3: Farm and compliance workflows

7. **Plot-aware farm operations**
   - Link assessments and applications to a farm and plot.
   - Track chemical application history and plot status.
   - Add nearby sensitive receptors such as homes, schools, water, beehives, and organic plots.
   - Use wind direction and mapped plot boundaries to improve drift warnings.

8. **Formal reporting and evidence**
   - Add attachments and photos for incidents, near misses, labels, and SDS records.
   - Add versioned report templates with reviewer and sign-off fields.
   - Generate regulator-ready HIRARC and chemical application reports only after expert review and legal validation.
   - Add CSV/Excel exports for farm registers and exposure logs.

### Priority 4: Accessibility and learning

9. **More languages and voice interaction**
   - Add Tamil, Nepali, and Indonesian translations reviewed by native speakers and farm communities.
   - Add voice input and spoken result summaries with a manual confirmation step.
   - Offer large controls, low-literacy icons, and accessible color/contrast behavior.

10. **Local calibration and learning**
    - Collect opt-in post-task feedback and weather observations.
    - Compare station forecasts with plot-level measurements.
    - Use anonymized aggregate trends only with informed consent and privacy safeguards.
    - Never use learned recommendations to silently weaken a hard safety rule.

## 8. Suggested Delivery Sequence

For a realistic next release, work in this order:

1. Add proper tenant isolation and secure authentication before onboarding multiple farms.
2. Link task assessments and chemical applications to farm and plot IDs.
3. Replace demonstration chemical data with verified product records and audited SDS handling.
4. Add local drafts and offline synchronization for assessments and incident reports.
5. Add task completion, exposure history, and audit trails.
6. Integrate alert delivery after consent, provider configuration, retries, and monitoring are in place.
7. Validate reporting templates with Malaysian safety professionals before calling them compliance reports.

## 9. Product Principle

AgriSafe AI should give farmers an understandable reason, a practical next step, and a safer alternative when possible. It should make uncertainty visible, preserve the authority of product labels and qualified safety professionals, and never present demonstration data as verified operational guidance.
