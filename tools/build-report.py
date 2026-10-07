#!/usr/bin/env python3
"""AIO調査レポート（aio/report/index.html）を生成する。

デザインは旧・統計ページ（tools/report-template.html に写しを保存）の<style>とヘッダーを流用し、
中身だけをこのファイルの STAGES から組み立てる。数字を直すときはここを直して再実行する。
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "aio"
DATA = (Path(__file__).resolve().parent / "report-template.html").read_text()  # 旧・統計ページの写し
LP_BASE = (Path.home() / ".claude/lp-base.css").read_text()

MF = ("マネーフォワード｜生成AIと検索エンジンの利用実態調査",
      "https://biz.moneyforward.com/research/2026-generative-ai-usage-survey/")
PEW = ("Pew Research Center｜GoogleのAI要約とクリック行動",
       "https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/")
ADOBE = ("Adobe｜AI経由の訪問と購買の分析",
         "https://business.adobe.com/blog/adobe-report-ai-traffic-travel-sites-surges-200-percent")
FINEXT = ("FINEXT｜Googleマップの利用実態調査（ASCII掲載）",
          "https://ascii.jp/elem/000/004/376/4376671/")
GOOGLE = ("Google公式ブログ｜マップの安全性レポート",
          "https://blog.google/products-and-platforms/products/maps/new-ways-were-protecting-businesses-on-maps/")
SPOLLUP = ("Spollup｜ECレビューの信頼に関する調査（ネットショップ担当者フォーラム）",
           "https://netshop.impress.co.jp/index%2Ephp/n/2026/05/27/16134")
DOORDASH = ("DoorDash｜2026 Restaurant Industry Trends Report",
            "https://about.doordash.com/en-us/news/doordash-restaurant-industry-trends-report-2026")
REPUTATION = ("Reputation・CGA by NIQ｜英国の飲食とAI（Craft Guild of Chefs掲載）",
              "https://craftguildofchefs.org/news/study-reveals-ai-driving-uk-consumer-habits-hospitality")
HONICHI_AI = ("訪日ラボ｜AI飲食店検索 利用者調査",
              "https://honichi.com/news/2026/10/01/202610_survey_gourmet_ai/")
HONICHI_NON = ("訪日ラボ｜AI飲食店検索 非利用者調査",
               "https://honichi.com/news/2026/09/24/202609_survey_gourmet_search/")
HLINK = ("エイチリンク｜支援事例", "https://h-link-marketing.co.jp/reason/")
ENHANCE = ("ENHANCE IT｜PR TIMES発表", "https://prtimes.jp/main/html/rd/p/000000013.000176021.html")

MF_META = "日本／2026年1月／AIで調べ物をした経験のある社会人2,204人"
HONICHI_META = "日本／2026年9月／AIで飲食店を選んだことがある20〜50代483人"

# 各カード: metric, title, body, meta, condition, source, hint, (任意) bars / case
STAGES = [
    dict(id="entry", title="AIが、調べ物の入口になった",
         intro="検索の前に、まずAIに聞く。そういう人が、もう多数派に近づいています。",
         cards=[
             dict(metric="58.1%", title="調べ物でAIをよく使う・ほぼ毎回使う",
                  body="AIで調べ物をした経験のある社会人の回答。",
                  meta="日本／2026年1月／2,204人・インターネット調査",
                  cond="社会人全体のAI利用率ではありません。調査開始日は1月16日。",
                  src=MF, hint="お客様が聞きそうな質問で、自社がどう紹介されるかを確認する。"),
             dict(metric="51.5%", title="AIを使う場面の1位は「概要・要点を素早く知りたい時」",
                  body="AIを使う場面を聞いた設問で、最も多かった回答。",
                  meta=MF_META,
                  cond="複数の場面から選ぶ設問です。短い説明で何が伝わるかを考える参考データです。",
                  src=MF, hint="会社の説明を一言で言えるか。AIが要約しても強みが残るかを見る。"),
             dict(metric="44.8%", title="検索エンジンの利用頻度が減った",
                  body="同じ調査で、検索の利用減少を感じた人の割合。",
                  meta=MF_META,
                  cond="本人の回答による利用頻度の変化で、検索市場全体の減少率ではありません。",
                  src=MF, hint="検索とAIの両方で、顧客の疑問に答えられる情報を整える。"),
         ]),
    dict(id="click", title="検索結果のリンクは、押されにくくなった",
         intro="AIの要約で済ませる人がいる。サイトを開く前に伝わる情報が、接点になります。",
         single=True,
         cards=[
             dict(metric="8% / 15%", title="AI要約の有無で、検索結果リンクのクリックに差",
                  body="通常の検索結果リンクをクリックした割合は、AI要約あり8%、なし15%。",
                  bars=[("AI要約あり", 8, 15), ("AI要約なし", 15, 15)],
                  meta="米国／2025年3月の閲覧／900人・68,879件のGoogle検索",
                  cond="検索結果は4月7〜17日に再収集。観測された差で、AI要約の因果効果ではありません。8%はAI要約内の引用リンクのクリック率ではありません。",
                  src=PEW, hint="サイト訪問だけでなく、訪問前に伝わる会社の説明も確認する。"),
         ]),
    dict(id="judge", title="AIの答えが、判断の材料になる",
         intro="参考にしつつ、必要なら公式の情報で確かめる。AIと公式サイトの両方が見られています。",
         cards=[
             dict(metric="77.3%", title="AIの情報が参考になる",
                  body="「非常に参考になる」13.4%と「参考になる」63.9%の合計。",
                  meta=MF_META,
                  cond="参考になるという評価で、正しいと全面的に信じる割合ではありません。",
                  src=MF, hint="自社の得意分野・実績・条件が、AIの説明で正しく伝わるかを見る。"),
             dict(metric="8割以上", title="AIの回答後、状況に応じて再調査する",
                  body="AIだけで完結せず、必要に応じて他の情報を確認するという回答。",
                  meta=MF_META,
                  cond="必ず企業の公式サイトを訪れる割合ではありません。",
                  src=MF, hint="料金・実績・対応範囲・問い合わせ方法を公式サイトで確認できるようにする。"),
         ]),
    dict(id="reviews", title="口コミは信用されている。ただ、利用者は迷っている",
         intro="Googleマップの口コミは今もお店選びの中心です。一方で偽の口コミは増え、利用者は疑いながら読んでいます。",
         cards=[
             dict(metric="90.2%", title="Googleマップの口コミを信頼している",
                  body="「ある程度信頼できる」84.5%と「非常に信頼できる」5.7%の合計。店舗選びで最も重視する情報も「口コミ・評判」（69.1%）でした。",
                  meta="日本／2026年2月／Googleマップで店舗を調べたことがある20〜60代317人",
                  cond="Googleマップの利用者に聞いた調査です。口コミの内容が正しいかを確かめた数字ではありません。",
                  src=FINEXT, hint="口コミは今も判断の中心。件数と中身を整えることが前提になる。"),
             dict(metric="約3億件", title="Googleが2025年に止めた・消した規約違反の口コミ",
                  body="2025年は2億9,200万件。2024年は2億4,000万件超でした。偽の店舗プロフィールも2025年に1,300万件を削除しています。",
                  meta="全世界／2025年の1年間／Google マップ安全性レポート（2026年4月発表）",
                  cond="Googleが投稿前に止めた分も含みます。日本だけの件数ではありません。",
                  src=GOOGLE, hint="偽物と疑われないよう、実際のお客様の具体的な声を増やす。"),
             dict(metric="75.6%", title="レビューを「サクラかも」と疑ったことがある",
                  body="レビューが信用できず購入をやめたことがある人も65.4%いました。",
                  meta="日本／2026年4月／ネット通販の利用者500人",
                  cond="ネット通販のレビューの調査です。Googleマップの口コミに限った数字ではありません。",
                  src=SPOLLUP, hint="星の数だけに頼らず、写真や具体的な内容で信頼を補う。"),
         ]),
    dict(id="restaurant", title="お店選びにも、AIが使われ始めた",
         intro="米国では5人に1人がAIでお店を選んだことがあり、英国ではAIとGoogleマップがほぼ並びました。日本でも、使う人は使う回数を増やしています。",
         cards=[
             dict(metric="22%", title="ChatGPTやGeminiでお店を選んだことがある",
                  body="米国の消費者の約5人に1人。お店選び、新しい店探し、料理・場面・価格での検索に使われています。",
                  meta="米国／2026年3月／3,001人・全国代表サンプル（DoorDash委託、Dynata実施）",
                  cond="前年との比較は公表されていません。「22%まで増えた」ではなく、2026年3月時点の割合です。",
                  src=DOORDASH, hint="AIに「近くのおすすめ」を聞いたとき、自店が候補に出るかを確認する。"),
             dict(metric="26% / 27%", title="お店を調べる手段：AIとGoogleマップがほぼ同じ",
                  body="店について調べるのにAIを使う人が26%、Googleマップが27%、SNSが32%。AIが口コミをまとめた要約を信頼する人も60%いました。",
                  bars=[("AI", 26, 32), ("Googleマップ", 27, 32), ("SNS", 32, 32)],
                  meta="英国／2025年10月発表／Reputation・CGA by NIQ",
                  cond="調査人数は公表されていません。英国の結果で、日本の傾向ではありません。",
                  src=REPUTATION, hint="Googleマップと同じように、AIでの見え方も点検する。"),
             dict(metric="33.7%", title="飲食店選びでAIを使ったことがある",
                  body="AIを使ったことがある人のうち、AIの情報だけで店を決めた人は約28%でした。",
                  meta=HONICHI_META,
                  cond="33.7%の分母は公開部分に書かれていません。全文は会員登録が必要です。調査元は飲食店の集客支援も行う事業者です。",
                  src=HONICHI_AI, hint="業種と地域でAIに質問し、自店が答えに出るかを試す。"),
             dict(metric="約7割", title="1年前より、AIでお店を探す回数が増えた",
                  body="AIでお店を探している人に聞いた、利用頻度の変化。",
                  meta=HONICHI_META,
                  cond="AIでお店を探したことがある人が対象です。利用者全体が増えた割合ではありません。",
                  src=HONICHI_AI, hint="使う人は、使う回数を増やしている。早めに整えた店が有利になる。"),
             dict(metric="60%", title="AIが勧めたお店に、実際に行った",
                  body="AIの提案は、最終的な店選びと来店に影響しています。",
                  meta=HONICHI_META,
                  cond="設問文は公開部分に書かれていません。全文は会員登録が必要です。",
                  src=HONICHI_AI, hint="営業時間・メニュー・予約方法など、基本情報を正確にしておく。"),
             dict(metric="50.8% / 42.5%", title="AIでお店を探せると知らなかった／これから使いたい",
                  body="まだ使っていない人の半数は、AIでお店を探せること自体を知りませんでした。一方で4割強が使いたいと答えています。",
                  meta="日本／2026年9月／AIを普段使うが、飲食店選びには使ったことがない20〜50代360人",
                  cond="AIを普段から使っている人が対象です。「使いたい」は意向で、実際に使うとは限りません。",
                  src=HONICHI_NON, hint="知られていない今のうちに、先に整える。"),
         ]),
    dict(id="buy", title="AI経由のお客様は、買う・決める",
         intro="購入への影響は、利用者の回答にも実際の訪問データにも表れています。",
         cards=[
             dict(metric="79%", title="AIを使った購入で、判断への自信が高まる",
                  body="買い物にAIを使う消費者が、AIの助けを得た購入により自信を感じると回答。",
                  meta="米国／2026年3月／5,000人超の調査に含まれるAI買い物利用者",
                  cond="該当利用者の人数は本文で非公表。自己評価で、購入判断の正しさを実証した数字ではありません。",
                  src=ADOBE, hint="比較に必要な根拠と、購入・相談前に知りたい条件を用意する。"),
             dict(metric="54%高い", title="AI経由訪問の購入転換率",
                  body="米国小売サイトでは、AI経由の購入転換率がAI以外の流入を上回った。",
                  meta="米国の小売サイト／2026年5月／Adobeの訪問・購買データ分析",
                  cond="相対的な差で、購入率54%ではありません。業種差があり、同月の旅行サイトではAI経由の転換率は28%低い結果です。AIO施策の効果測定ではありません。",
                  src=ADOBE, hint="AI経由の流入に加え、問い合わせ・購入までの成果を自社で計測する。"),
         ]),
    dict(id="cases", title="国内でも、問い合わせ・受注につながる例", label="事例",
         note="国内事例は、企業・支援会社が公表した2件です。当社・本サービスの導入実績ではなく、売上・受注を保証するものでもありません。",
         cards=[
             dict(case="エイチリンクの支援先／YouTube運用代行会社", metric="累計579万円",
                  title="ChatGPT経由の問い合わせから受注",
                  body="支援開始から1年3か月時点で、ChatGPT経由の累計受注額を公表。顧客企業名は非公開です。",
                  meta="国内BtoB／支援会社の公式サイト・2026年10月6日確認",
                  cond="支援会社の自己公表。サイト全面改修・SEO・AIO・被リンク獲得を併用。AIO単独の寄与、利益額、他社での再現性は確認できません。",
                  src=HLINK, hint="法人向けでも、問い合わせ時にAIで知ったかを聞き、受注まで記録する。"),
             dict(case="ENHANCE IT／自社インバウンド向け事業", metric="月100万円超",
                  title="AI経由の問い合わせから売上を公表",
                  body="直近30日のAI経由訪問333件、問い合わせ約100件、AI経由の月売上100万円超を報告。",
                  meta="国内企業の訪日外国人向け事業／2026年7月3日発表",
                  cond="企業のプレスリリースによる自己公表。日本人顧客全体の傾向ではありません。複数の集客・サイト改善を併用しており、第三者監査やAIO単独の寄与は確認できません。",
                  src=ENHANCE, hint="店舗・サービスでも、AIでの紹介から問い合わせ・予約までの経路を確認する。"),
         ]),
]

e = html.escape


def card(c):
    out = ['<article class="data-card">']
    if c.get("case"):
        out.append(f'<p class="case-company">{e(c["case"])}</p><span class="self-report">企業側の公表値</span>')
    out.append(f'<p class="metric">{e(c["metric"])}</p><h3>{e(c["title"])}</h3><p class="body">{e(c["body"])}</p>')
    if c.get("bars"):
        out.append(f'<div class="compare" aria-label="{e(c["title"])}の比較">')
        for label, v, mx in c["bars"]:
            out.append(f'<div class="bar-row"><span>{e(label)}</span><div class="track" aria-hidden="true">'
                       f'<div class="fill" style="width:{v / mx * 100:.2f}%"></div></div><strong>{v}%</strong></div>')
        out.append('</div>')
    name, url = c["src"]
    out.append(f'<p class="data-meta">{e(c["meta"])}</p><details><summary>数字の読み方・条件</summary><p>{e(c["cond"])}</p></details>'
               f'<a class="source" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(name)} ↗</a>'
               f'<p class="hint"><strong>提案のヒント</strong>{e(c["hint"])}</p></article>')
    return "".join(out)


n_cards = sum(len(s["cards"]) for s in STAGES)
flow = "".join(f'<a href="#{s["id"]}"><span>{i:02d}</span>{e(s["title"])}</a>' for i, s in enumerate(STAGES, 1))
body = []
for i, s in enumerate(STAGES, 1):
    num = s.get("label", f"{i:02d}")
    grid = "data-grid single" if s.get("single") else "data-grid"
    body.append(f'<section class="stage" id="{s["id"]}" aria-labelledby="title-{s["id"]}"><div class="stage-head">'
                f'<span class="number">{num}</span><h2 id="title-{s["id"]}">{e(s["title"])}</h2></div>')
    if s.get("intro"):
        body.append(f'<p class="stage-intro">{e(s["intro"])}</p>')
    if s.get("note"):
        body.append(f'<p class="case-note">{e(s["note"])}</p>')
    body.append(f'<div class="{grid}">' + "".join(card(c) for c in s["cards"]) + '</div></section>')

# 統計ページの<style>・ヘッダー・ヒーロー画をそのまま流用する
style = re.search(r"<style>([\s\S]*?)</style>", DATA).group(1)
header = re.search(r'<header class="site-header">[\s\S]*?</header>', DATA).group(0).replace(
    '<a href="../report/">', '<a href="../report/" aria-current="page">')
art = re.search(r'<svg class="hero-art"[\s\S]*?</svg>', DATA).group(0)
extra = """
.flow-nav{grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}.flow-nav a{min-height:0;word-break:auto-phrase;line-break:strict}
.data-meta,.data-card .source,.data-card details,.case-company,.self-report{font-size:12px}
@media(max-width:700px){.flow-nav{grid-template-columns:1fr;gap:6px}.flow-nav a{padding:9px 13px}.flow-nav span{display:inline;margin-right:8px}}
"""

page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"><title>AIO調査レポート｜正規パートナー向け</title><meta name="description" content="AIOが売れる根拠を、国内外の調査結果で。AIでの調べ物、検索クリック、口コミ、AIでのお店選び、購買、国内事例の{n_cards}件を調査条件・原典リンク付きで紹介。"><link rel="preload" href="../fonts/noto-sans-jp.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="../fonts/zen-kaku-black.woff2" as="font" type="font/woff2" crossorigin><style>
{LP_BASE}
{style}
{extra}</style><link rel="stylesheet" href="../portal.css"><script src="../portal.js" defer></script><link rel="stylesheet" href="../menu-update.css"><link rel="canonical" href="https://writeup-inc.github.io/partner/aio/report/"></head><body id="top"><a class="skip-link" href="#main">本文へ移動</a>{header}<main class="inner" id="main"><p class="breadcrumb"><a href="../">パートナーポータル</a> / AIO調査レポート</p><section class="intro"><div class="data-intro"><div><p class="kicker">AIO調査レポート</p><h1><span>AIOが売れる根拠を、</span><span>調査結果で。</span></h1><p class="lead">お客様は、AIで調べ、比べ、選ぶようになっています。商談で使える国内外の調査結果を、7つのテーマにまとめました。数字ごとに、調査の条件と出典を載せています。</p><p class="checked">7テーマ・{n_cards}件の調査結果 ／ <span class="nobr">出典確認：2026年10月6日・8日</span></p></div>{art}</div></section><nav class="flow-nav" aria-label="7つのテーマ">{flow}</nav><p class="reading-note">国・時期・対象の異なる調査を、話の流れに沿って並べています。同じ人を追跡した調査ではありません。お客様に数字を伝えるときは「数字の読み方・条件」も合わせて伝えてください。</p>{"".join(body)}<section class="next-section"><h2>データを、次の提案へ。</h2><p>まずは、お客様が聞きそうな質問を5つ。AIの説明・公式サイトの情報・問い合わせ経路を一緒に確認しましょう。</p><div class="next-links"><a href="../talk/">営業トーク10選を見る →</a><a href="../talk/#objections">反論への切り返し10選 →</a></div></section><div class="end-link"><a href="../">← フォローカレンダーへ</a><a href="#top">ページの先頭へ ↑</a></div></main><footer class="site-footer inner"><span>AIO 正規パートナーポータル <small>社内確認用</small></span><div><a href="../#calendar">フォローカレンダー</a><a href="../story/">小説を読む</a></div></footer></body></html>
"""
out = ROOT / "report/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page)
print(out, n_cards, "cards")
