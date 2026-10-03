# ThreatGuard upgrade: email to email + URL + SMS

This release extends the existing project. Nothing was regenerated: the email pipeline, auth, dashboard, history and results page are the same code, with small additive hooks.

## What changed at a glance

- **Backend:** `POST /api/analyze/url` and `POST /api/analyze/sms`, a `scan_type` filter on `/api/history`, extended `/api/dashboard`, per-channel `/health`.
- **ML:** separate SMS and URL pipelines (loader, preprocessing/features, training with LR/RF/XGBoost, comparison, best-model selection, confusion matrices, explainability, persistence, inference). Models are stored in `models/sms/` and `models/url/`, apart from the email models in `models/`.
- **Database:** one additive migration (`scan_type`, generated `title`, one index).
- **Frontend:** Analyze URL and Analyze SMS pages with a type switcher, type-aware results and history, extended dashboard, redesigned landing page.

## Modified files (26)

- `README.md`
- `backend/.env.example`
- `backend/.gitignore`
- `backend/app/api/routes.py`
- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/schemas/scan.py`
- `backend/app/services/analyzer.py`
- `backend/app/services/scans.py`
- `backend/ml/inference/__init__.py`
- `backend/ml/inference/predictor.py`
- `backend/ml/training/pipeline.py`
- `frontend/app/(app)/analyze/page.tsx`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`
- `frontend/components/charts/weekly-trend-chart.tsx`
- `frontend/components/dashboard-view.tsx`
- `frontend/components/history-table.tsx`
- `frontend/components/result-loader.tsx`
- `frontend/components/result-view.tsx`
- `frontend/components/sidebar.tsx`
- `frontend/hooks/use-history.ts`
- `frontend/services/api.ts`
- `frontend/types/index.ts`

## New files (27)

- `backend/datasets/generate_sample_sms_url.py`
- `backend/ml/explainability/sms_explainer.py`
- `backend/ml/explainability/url_explainer.py`
- `backend/ml/inference/sms_predictor.py`
- `backend/ml/inference/url_predictor.py`
- `backend/ml/preprocessing/sms.py`
- `backend/ml/preprocessing/url.py`
- `backend/ml/training/sms_dataset.py`
- `backend/ml/training/sms_pipeline.py`
- `backend/ml/training/url_dataset.py`
- `backend/ml/training/url_pipeline.py`
- `backend/models/sms/.gitkeep`
- `backend/models/url/.gitkeep`
- `backend/train_sms.py`
- `backend/train_url.py`
- `frontend/app/(app)/analyze/sms/page.tsx`
- `frontend/app/(app)/analyze/url/page.tsx`
- `frontend/components/analyze-sms-form.tsx`
- `frontend/components/analyze-tabs.tsx`
- `frontend/components/analyze-url-form.tsx`
- `frontend/components/charts/type-distribution-chart.tsx`
- `frontend/components/landing/dashboard-preview.tsx`
- `frontend/components/landing/hero-demo.tsx`
- `frontend/components/landing/site-footer.tsx`
- `frontend/components/recent-activity.tsx`
- `frontend/lib/scan-types.ts`
- `supabase/migrations/20261003_multi_channel_scans.sql`

`docs/UPGRADE.md` itself is also new.

## Integration notes

- **Email behaviour is unchanged.** `ml/training/pipeline.py` gained one optional `loader` argument (default is the old loader) so SMS reuses the same TF-IDF, comparison and saving code. `PhishingPredictor` gained a `train_hint` attribute so the SMS predictor can subclass it. Email model files and routes are untouched.
- **`prediction` values are unchanged** (`phishing` / `safe`). `phishing` means "threat" for all types, so the existing check constraint and old rows stay valid. The UI shows Phishing, Malicious or Scam according to `scan_type`.
- **URL and SMS reuse existing columns:** URL stored in `body`; SMS text in `body`, optional sender in `sender`. Old rows become `scan_type = 'email'` through the column default.
- **`title`** is a Postgres generated column (subject, else the first 120 characters of the body). History and recent activity use it so they never load full bodies.
- **`/api/dashboard`** keeps all previous fields and adds `email_scans`, `url_scans`, `sms_scans` under `metrics`, plus `type_distribution` and `recent_activity`. The `phishing_vs_safe` slice is now named "Threats" instead of "Phishing".
- **`/health`** keeps its `status` and `model` fields and adds `models.email|sms|url`.
- **History search** now also matches URL and message text (through `title`). It still does not scan full email bodies.
- **Config:** optional `SMS_MODEL_DIR` and `URL_MODEL_DIR`. Defaults need no change.
- **URL features:** 37 lexical features in `ml/preprocessing/url.py`. The predictor refuses a model whose saved feature list differs, so edit features only together with retraining.
- **URLs are never fetched.** Analysis is lexical only.

## Merge instructions

Two zips are provided: the full project, and an overlay containing only the new and modified files at their project paths.

1. **Back up** your repo and, in Supabase, take a backup or confirm point-in-time recovery is on.
2. **Database first.** In the SQL Editor run `supabase/migrations/20261003_multi_channel_scans.sql`. It only adds a column, a constraint, a generated column and an index, and it is safe to repeat. Adding the generated `title` column rewrites the table once, so run it off-peak on very large tables. Old backend code keeps working after the migration.
3. **Copy the overlay** over your project. Files listed under "Modified files" will be replaced. If you edited any of them, diff before overwriting. The most likely conflicts are `frontend/app/page.tsx` (fully redesigned), `backend/app/services/scans.py` and `frontend/components/history-table.tsx`.
4. **Install dependencies.** No new Python or npm packages were added.
5. **Train the new models** (each is optional until you need that channel):
   `python train_sms.py --data datasets/sms.csv` and `python train_url.py --data datasets/urls.csv`. Keep your existing email models in `models/`.
6. **Restart the backend** and open `/health`. Each trained channel should show `ok`.
7. **Deploy the frontend.**

### Verification checklist

- Old email scans appear in History with type Email and open normally.
- Analyze an email, a URL and an SMS. Each redirects to a result page with the right labels.
- History filter by type, search for part of a URL, and pagination work.
- Dashboard shows three type counts, the detection-types chart and recent activity.
- Untrained channel: the analyze call returns 503 naming the training command, and other channels keep working.

### Rollback

The migration file ends with commented rollback statements. Revert the code first, then run them only if needed. Email data is not affected.

## What was and was not verified in the build environment

Verified by running code: SMS and URL preprocessing, dataset loaders, training pipelines (Logistic Regression and Random Forest on small synthetic data), model comparison and saving, inference, explanations for both the linear and tree paths, request validation, scan persistence, history filtering and dashboard aggregation (against an in-memory stand-in for Supabase, including a legacy row without the new columns).

Not verified, because the environment had no package access: XGBoost training, the FastAPI HTTP layer end to end, the Supabase client, the SQL migration on a live database, `npm install`, `next build` and visual rendering of the pages. The frontend was only syntax- and consistency-checked with type shims. Run `npm run typecheck` and `npm run build`, and apply the migration to a staging project, before production.
