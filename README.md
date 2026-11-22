# 22 November 2026 in One Image

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Reza0109/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Reza0109/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A dense one-page front page summing up Sunday 22 November 2026's world news:
33 stories across 6 regions, led by the Gulf escalation — Iran strikes Bahrain,
two oil tankers hit in the Strait of Hormuz, and Houthi missiles intercepted
over Riyadh.

## What it is

`main.py` (Python 3.13, standard library only) draws a 1024x1024 PNG to
`/output/entry.png`. No network, no external files, no randomness — the same
bytes on every run. It uses a hand-defined 5x7 bitmap font and a hand-written
PNG encoder (zlib + struct).

Layout: masthead ("THE WORLD IN ONE IMAGE" / "SUNDAY 22 NOVEMBER 2026"),
hero panel ("GULF ON EDGE" with the 3 key numbers), six region sections
(Middle East, Asia-Pacific, Europe, World, Americas, Africa) with a drawn
pictogram, headline and one fact line per story, and a "BY THE NUMBERS" strip.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Competition

make.fun — news-image-20261122: "Sum up 22 November's world news in one image".
$100 total, top 50 paid. Entry: this repository.

## License

MIT

<sub>Entered on [make.fun](https://make.fun/?ref=j3h45htn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
