# 五目並べ (Gomoku)

Python + [Flet](https://flet.dev) で作った五目並べアプリです。  
15×15 の碁盤で、2人対戦または AI との対戦が楽しめます。

![board](https://img.shields.io/badge/board-15×15-brown) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![flet](https://img.shields.io/badge/flet-0.85-green)

---

## 機能

| 機能 | 説明 |
|------|------|
| 🎮 2人対戦 | 同じデバイスで黒・白を交互に操作 |
| 🤖 AI対戦 | ミニマックス法＋αβ枝刈りによる AI（白番）と対局 |
| ⛔ 禁じ手 | 黒番の三三・四四・長連を自動でブロック |
| 🏆 勝利ハイライト | 5つ並んだ石を赤くハイライト表示 |
| 📜 手の履歴 | 任意の手番に戻れるタイムトラベル機能 |
| 🎨 囲碁風UI | Canvas で描画した本格的な碁盤（交点に石を配置） |

---

## スクリーンショット

```
        五目並べ
  ○ 2人対戦  ● AI対戦

  次の手番：黒 ●

  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
  ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
  ...（15×15 碁盤）
```

---

## セットアップ

### 必要環境

- Python 3.10 以上
- [uv](https://github.com/astral-sh/uv) または pip

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/kokisuke/gomoku.git
cd gomoku

# 依存関係をインストール
pip install flet

# 起動
python main.py
```

---

## ファイル構成

```
gomoku/
├── main.py           # Flet UI（碁盤・モード選択・履歴パネル）
├── game_logic.py     # ゲームロジック（勝利判定・禁じ手チェック）
├── ai.py             # AI エンジン（ミニマックス＋αβ枝刈り）
├── pyproject.toml    # プロジェクト設定
└── tests/
    ├── test_game_logic.py   # ゲームロジックのテスト（24件）
    └── test_ai.py           # AI のテスト（10件）
```

---

## AI の仕組み

1. **即勝ち優先** — AI が1手で勝てる場合は即座に打つ
2. **即ブロック** — 相手が次の手で勝てる場合は先にブロック
3. **ミニマックス探索** — αβ枝刈りで深さ2まで先読みし、ヒューリスティック評価関数でスコアを算出

候補手は既存の石から2マス以内に絞ることで、15×15の全探索を回避し応答速度を確保しています。

---

## 禁じ手ルール（黒番のみ）

| 禁じ手 | 内容 |
|--------|------|
| 長連 | 6個以上の連続 |
| 四四 | 2つ以上の「四」を同時に作る |
| 三三 | 2つ以上の「活三」を同時に作る |

---

## テスト実行

```bash
pip install pytest
pytest tests/ -v
```

---

## 使用技術

- [Flet](https://flet.dev) — Python 製クロスプラットフォーム UI フレームワーク
- `flet.canvas` — 碁盤・石の描画
- `asyncio.to_thread` — AI 計算の非同期オフロード
