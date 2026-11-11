# Grid Cost Planner

[Open the live Grid Cost Planner](https://ssosalevis26-coder.github.io/Transmission-infrastructure-cost-calculator/)

University of Delaware CISC 106 final project. Compare illustrative utility-scale solar,
four-hour battery energy storage (BESS), and hybrid costs. Save cases and inspect a
transmission raw-material breakdown. The state selection labels a case and uses the
same classroom cost rates for each state.

## Run and test

Use Python 3.12 or newer.

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python -m drafter main.py
```

Open the local URL printed by Drafter. Saved cases live in the running browser session.

## Deploy to GitHub Pages

1. Put this folder's contents, including the hidden `.github` folder, at the root of
   the GitHub repository's `main` branch. Use a descriptive commit message such as
   `Build renewable energy screening planner`.
2. Under **Settings → Pages → Build and deployment**, select **GitHub Actions**.
3. Under **Actions**, open **Test and deploy Drafter**, run it for `main`, and open
   the URL from the completed `github-pages` deployment.
4. Open the link in a signed-out window. Calculate a case, save and compare it, and open
   Transmission and Assumptions.

The workflow runs the tests and compiles a static Drafter site. Python runs in the
visitor's browser. For background, see the [Drafter Pages guide](https://drafter-edu.github.io/drafter/your-project/deploy/github-pages/).

## Submission materials

- [Project plan](PLANNING.md)
- [AI assistance disclosure and archived conversation](AI-DISCLOSURE.md)
- [Video recording and verification checklist](VIDEO.md)
- Demo video link pending recording and upload.
