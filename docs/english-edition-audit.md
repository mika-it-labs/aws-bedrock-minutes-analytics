# English Edition Audit

Audit date: 2026-10-17

## Scope and source snapshots

- English repository: [mika-it-labs/aws-bedrock-minutes-analytics](https://github.com/mika-it-labs/aws-bedrock-minutes-analytics), inspected at the pre-change snapshot `dedf948d043765e8cc145664117abb4de067b1d8`.
- The resulting editorial changes are recorded in [commit ad59ac3](https://github.com/mika-it-labs/aws-bedrock-minutes-analytics/commit/ad59ac3ae39f9e8b62b9d2be0be38151630d4a03). The pre-change snapshot above is the audit baseline, not the resulting revision.
- Original Japanese repository: [mika-it-labs/minutes-analytics](https://github.com/mika-it-labs/minutes-analytics), read only at `1c2c09d42d163cd370cbb311db1e0892d5f52ce2`.
- The audit covered every tracked text file and visually inspected the published classification PNG. Git history was not rewritten.

The English snapshot already contained English text in all eight tracked text files. Its only Python file, `src/demo_bedrock_pipeline.py`, already had English comments, prompts, synthetic records, messages, and report labels. The published PNG already used English labels. The remaining work was to make experiment provenance explicit, reconcile the README with the actual files, and fix two output paths containing a trailing directory-space.

## Changes

| File | Audit finding and resolution |
|---|---|
| README.md | Clarified that saved results measure Japanese data and that the included script runs a separate English demo. Corrected the install command, generated-image path, prerequisites, and repository listing. |
| src/demo_bedrock_pipeline.py | Added English documentation and an explicit provenance line to new reports. Preserved the synthetic records, model settings, SQL, category names, selection prefix, and numerical analysis logic. |
| output/analysis_result.txt | Moved from `output /analysis_result.txt`. Added a translation note: English keyword labels are glosses of Japanese features; all original measured values are retained. |
| output/bedrock_classification_result.txt | Expanded OK/NG to Correct/Incorrect and explicitly confirmed that document IDs, predictions, and numerical results are unchanged. |
| output/bedrock_clustering_evaluation.txt | Moved from `output /bedrock_clustering_evaluation.txt`. Added original-Japanese-data provenance and distinguished clustering from classification. |
| output/bedrock_classification_map.png | Already English; retained the existing image unchanged. |
| requirements.txt, .env.example, .gitignore | Already English; retained unchanged. |

The directory named `output ` (with a trailing space) was consolidated into `output`. This also avoids a path that cannot be checked out normally on Windows.

## Measurement preservation

| Experiment | Preserved measurements |
|---|---|
| Bedrock classification | 30 documents; 24 correct; 6 incorrect; 80.00% accuracy |
| Predicted categories | AWS/Infrastructure: 4; AI/Analytics: 10; Security: 16 |
| TF-IDF + UMAP + HDBSCAN analysis | 30 documents; 212 terms; ARI 0.4493; NMI 0.6184 |
| Separate Bedrock clustering | 30 documents; 3 clusters; ARI 1.0000; NMI 1.0000; agreement 30/30 (100.00%) |

Classification document IDs, ground-truth labels, and predictions were compared with the [original Japanese classification log](https://github.com/mika-it-labs/minutes-analytics/blob/1c2c09d42d163cd370cbb311db1e0892d5f52ce2/output/bedrock_classification_result.txt). The six incorrect predictions are IDs 8 through 13.

The analysis report's document IDs, per-document cluster assignments, UMAP coordinates, category/cluster counts, keyword ranks, keyword weights, ARI, and NMI were compared with the [original Japanese analysis log](https://github.com/mika-it-labs/minutes-analytics/blob/1c2c09d42d163cd370cbb311db1e0892d5f52ce2/output/analysis_result.txt). English keyword labels represent translations of the original tokens, not newly computed English TF-IDF terms.

The Bedrock clustering measurements were compared with the [original evaluation report](https://github.com/mika-it-labs/minutes-analytics/blob/1c2c09d42d163cd370cbb311db1e0892d5f52ce2/output/bedrock_clustering_evaluation.txt).

No Amazon Bedrock inference, database writes, feature extraction, dimensionality reduction, or model evaluation was performed for this editorial update. The Japanese repository was not modified.

## Running the English demo

The existing demo processes only records whose titles start with `[EN-DEMO2026] `. Its categories are `Infrastructure`, `AI & Analytics`, and `Security`; these names intentionally remain unchanged because they are used in stored demo records.

The demo writes `output/english_classification_map.png` and `output/english_classification_evaluation.txt`. It computes its own results and does not establish or reproduce the historical Japanese-data accuracy. The `classify` command reuses valid stored English-demo predictions and invokes Bedrock only when a valid prediction is missing. The `visualize` command recomputes metrics from stored predictions and overwrites both English-demo output files without invoking Bedrock. A regenerated report is therefore not evidence of a fresh inference run. Follow the README for its separate AWS and database prerequisites, repository-root working directory, and example table definition.

The Japanese experiment scripts listed in the previous README are not present in this English repository snapshot. This update documents that fact instead of implying that those scripts or missing images are included.

## Validation

- Scanned all final tracked text for Japanese kana and CJK characters.
- Checked that documented repository files and relative Markdown links exist.
- Compared the numeric sequences in the translated historical reports against their saved baselines and Japanese sources.
- Compared all classification IDs, labels, predictions, statuses, and category counts.
- Checked Python syntax and confirmed that the executable syntax tree is unchanged except for the module documentation and the new report provenance sentence.
- Retained the published PNG's original Git blob.
- Live AWS/RDS execution was not performed; no new English-demo accuracy is claimed.
