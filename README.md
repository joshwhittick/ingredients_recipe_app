# ingredients_recipe_app

Personal Streamlit app for planning the week's meals and building a combined shopping list. Recipes live in a Google Sheet; the app reads and appends to it via a service account.

Live: https://ingredients-planner-app.streamlit.app/ (Streamlit Community Cloud, deploys from `main`).

## Contents

| Path | What it does |
|---|---|
| `ingredient.py` | The whole app. Sidebar switches between **Meal Chooser** and **Recipe Builder**. |
| `requirements.txt` | Python deps for Streamlit Cloud. |
| `.streamlit/secrets.toml` | Service-account key + sheet id. **Gitignored, never commit.** Local copy only. |

## How it works

- **Meal Chooser** - pick a recipe and head-count for Monday to Friday (leave a day blank to skip it), press Submit. Each recipe's quantities are scaled by `people / serves_persons`, then summed by `ingredient_name` + `units` into one shopping list (`shopping_list()`):
  - an ingredient listed in more than one volume unit (`tsp`, `tbsp`, `ml`, `l`, `cups`) is merged into `ml`;
  - `unit` items round up to whole items; `g`/`ml` round to whole numbers; everything else to 2 dp.
- **Recipe Builder** - enter a recipe name, servings and ingredient rows (existing ingredient from the dropdown, or a new one), press Submit to append the rows to `Sheet1`.

## Data (Google Sheet `Ingredients_DB`)

| Tab | Contents |
|---|---|
| `Sheet1` | One row per recipe ingredient: `recipe_name, serves_persons, ingredient_name, quantity, units`. Read by both tabs; Recipe Builder appends here. |
| `Sheet2` | Header only (`Day, Meal, Number of People`). Unused by the current code. |
| `Sheet1_backup_2026-11-06_pre_vegan` | The pre-vegan recipe set (98 rows), kept for rollback. |

- All recipes are vegan as of 2026-11-06: 21 recipes, 206 rows.
- Each recipe should have a single `serves_persons` value (Meal Chooser uses the max if they differ).
- Units should be one of the Recipe Builder options: `g, pinch, όσο παίρνει, splash, unit, ml, l, tsp, tbsp, cups`. Tins/cloves/bunches are counted as `unit`.
- The sheet must be shared with the service account's `client_email`.

## Secrets

Same keys locally (`.streamlit/secrets.toml`) and in Streamlit Cloud (app ⋮ -> Settings -> Secrets), all top-level:

```toml
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
spreadsheet_key = "<Google Sheet id>"
```

Source of the key: GCP project `ingredients-411515`; the original JSON key is in Google Drive `My Drive/ingredients/`.

## How to run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run ingredient.py
```

**Note:** running locally hits the live sheet. Recipe Builder's Submit writes to it.

## Status

- 2026-11-06 - app was down (`KeyError` on `st.secrets['type']`: Cloud secrets missing); secrets restored, app up. Recipes converted to vegan + 10 new ones added (`Sheet1`).
- 2026-11-06 - shopping list rounds whole items up, merges volume units into ml, skips blank days; fixed `is ''` and `int(unique())`; dropped unused matplotlib import.
- Known issues / TODO:
  - `matplotlib` and `XlsxWriter` are in `requirements.txt` but unused.
  - Uses `oauth2client` (deprecated); `google-auth` is the replacement.
  - Streamlit Cloud runtime Python version not pinned.
