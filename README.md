# デザインアンテナ

毎日ひとつのデザイン知識を公開する静的サイトです。Cloudflare Pages が `main` ブランチのルートにある生成済みの HTML を、ビルドなしで配信します。

公開URLは <https://design-antenna.mlabcraft.com/> です。

最初のレッスンは 2026-11-15 の 17:00頃（日本時間）です。それまでは目次に空の案内だけが出ます。HTML は手で編集しません。`data/lessons.json` に1件足して、ビルドします。

## レッスンを1件追加する

### 1. 図があるときだけ、画像を置く

`images/` にファイルを置きます。例: `images/001.png`

使える拡張子は png、jpg、jpeg、gif、webp、svg です。

### 2. `data/lessons.json` の `lessons` の末尾に、オブジェクトを1つ追加する

`number` は第N回の N です。既存と重複させません。ページのファイル名は、この番号を少なくとも3桁にゼロ埋めした `lessons/NNN.html` です（1 は `lessons/001.html`、12 は `lessons/012.html`、1000 は `lessons/1000.html`）。

```json
{
  "number": 1,
  "date": "2026-11-15",
  "title": "カーニング",
  "titleEn": "Kerning",
  "category": "タイポグラフィ",
  "summary": "目次に出す一行。省略すると「どういう知識か」の先頭から作られます。",
  "what": "どういう知識かの本文です。\n\n空行で段落が分かれます。**太字** と [表示名](https://example.com) が使えます。",
  "example": "具体例の本文です。",
  "tip": "今日から使えるひとことの本文です。",
  "sources": [
    {
      "title": "出典の名前",
      "author": "著者名（省略可）",
      "year": "2020",
      "url": "https://example.com/article",
      "note": "補足（省略可）"
    }
  ],
  "image": "images/001.png",
  "imageAlt": "図の説明。画像があるときは必須です。",
  "imageCaption": "キャプション（省略可）"
}
```

必須なのは `number`、`date`、`title`、`category`、`what`、`example`、`tip`、`sources` です。`sources` は1件以上で、各出典には `title` が必要です。URLのない本や論文は `title` だけでも掲載できます。

省略できるのは `titleEn`、`summary`、`author`、`year`、`url`、`note`、`image`、`imageAlt`、`imageCaption` です。画像を置くときは `image` と `imageAlt` をセットで書きます。`image` は `images/001.png` のように `images/` から書く相対パスです。

`date` は `YYYY-MM-DD` です。`category` は自由な文字列で、目次の絞り込みに使います。いま想定しているテーマは、タイポグラフィ、色彩、レイアウトとグリッド、ゲシュタルト原則、UXの法則、情報デザイン、アクセシビリティ、ブランディング、デザイン史、データ可視化、スライドデザインです。

本文に HTML は書けません。書いた記号はそのまま文字として表示されます。段落は空行で分け、段落のなかの改行はそのまま改行になります。

目次は日付の新しい順です。同じ日付なら番号の大きい方が先です。各レッスンページの「前の回」「次の回」は番号順です。

### 3. ビルドする

リポジトリのルートで実行します。Python 3 の標準ライブラリだけで動き、追加のインストールは要りません。

```bash
python3 scripts/build.py
```

このコマンドが `index.html`、`lessons/NNN.html`、`lessons/index.html`、`404.html`、`sitemap.xml`、`robots.txt` を作り直します。`lessons/` にある、データに対応しない古い HTML は削除します。検証でエラーになると、HTML は書き換えません。表示された箇所を直して、もう一度実行します。

### 4. 表示を確認する

```bash
python3 -m http.server 8000
```

ブラウザで http://127.0.0.1:8000/ を開きます。

### 5. `main` に載せて push する

`data/lessons.json`、追加した画像、ビルドで更新されたファイルをコミットし、`main` に push します。Cloudflare Pages がルートのファイルをそのまま公開します。使わなくなった画像は、手で削除してかまいません。ビルドは画像を消しません。

## データの全体

| フィールド | 役割 |
| --- | --- |
| `schemaVersion` | 形式の版。いまは `1` |
| `url` | 公開URL。末尾のスラッシュは不要 |
| `title` / `titleEn` | サイト名と英語名 |
| `tagline` | 副題 |
| `description` | 目次ページの説明 |
| `launch` | 第1回の予告。`date`、`time`（`HH:MM`）、`timeLabel`（表示用）、`timezone`（`+09:00`） |
| `topics` | レッスンがまだ無いときに見せるテーマの一覧 |
| `lessons` | レッスンの配列。新しい回は末尾に足す |

`launch` を変えると、レッスンが0件のときの「最初のレッスンは、いつ届くか」の文面も変わります。

## ページのきまり

- 各レッスンには「どういう知識か」「具体例」「今日から使えるひとこと」と「出典」を出します。
- フッターに、文章が出典をもとにAIが要約したものであることと、図がAIの書いたコードで描かれていることを記します。この2文はビルドが付けるので、レッスンごとに書く必要はありません。
- 言語は日本語（`lang="ja"`）です。英語名がある見出しには `lang="en"` を付けます。
- 目次のカテゴリ絞り込みは、レッスンが1件以上あるときに出ます。CSS だけで動きます。

## 見た目

スタイルは `css/style.css`、アイコンは `favicon.svg` です。ビルドでは上書きしません。

## 公開

GitHub リポジトリを Cloudflare Pages に接続します。本番ブランチを `main`、フレームワークを「なし」、ビルドコマンドを空欄、ビルド出力ディレクトリを `.` にします。ルートディレクトリは既定のリポジトリルートを使います。プロジェクトの「カスタムドメイン」に `design-antenna.mlabcraft.com` を追加します。
