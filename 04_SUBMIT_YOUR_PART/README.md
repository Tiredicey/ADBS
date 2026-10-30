# Submit your part here

Only the repo owner (@Tiredicey) merges. Nothing reaches the final deck without review.

## Option A: no Git needed (easiest)

1. Open https://github.com/Tiredicey/ADBS/tree/main/04_SUBMIT_YOUR_PART
2. Click **Add file → Upload files**.
3. Drag in `part<N>_<yourname>.pptx` (example: `part3_maria.pptx`).
4. Choose **"Create a new branch for this commit and start a pull request"**, then click **Propose changes → Create pull request**.
5. Done. The owner reviews it, then merges it or asks for changes.

No Upload button? You need collaborator access. Ask the owner to add you, or send the file to the owner directly.

## Option B: Git

```bash
git clone https://github.com/Tiredicey/ADBS.git
cd ADBS
git checkout -b part3-maria
cp ~/Downloads/part3_maria.pptx 04_SUBMIT_YOUR_PART/
git add 04_SUBMIT_YOUR_PART/part3_maria.pptx
git commit -m "Add part 3 (Maria)"
git push -u origin part3-maria
```

Then open the pull-request link that Git prints.

## Rules

- Name the file `part<N>_<yourname>.pptx`.
- Add only your own file. Do not edit other parts or `05_FINAL_SUBMISSION/`.
- Resubmitting? Push to the same branch, and the pull request updates automatically.
