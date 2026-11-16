# Dataset provenance

The Cookie Cats player-level dataset is distributed through
[Aurelia Sui's Kaggle dataset](https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing).
The experiment compares the first progression gate at levels 30 and 40.

Run `python download_data.py`, or save your own download as `data/cookie_cats.csv`.
The downloader uses the CSV mirror in the
[reference project](https://github.com/Quantique-Realm/cookie-cats-ab-test), pinned
to commit `5fff3ae4e17de6cecb31a46650110bc1bc2f8f77`.

Expected SHA-256:
`5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`

The 90,189 rows contain `userid`, `version`, `sum_gamerounds`, `retention_1`,
and `retention_7`. Game rounds measure engagement, not which level was reached.
The raw CSV is ignored by Git and is not redistributed here. Dataset rights
remain with its providers; this repository does not assign it a new license.
