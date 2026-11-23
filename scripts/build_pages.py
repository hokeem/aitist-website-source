#!/usr/bin/env python3
"""Generate bilingual (EN + /zh/) Zenith pages and the homepage nav/footer/product band.
Facts: tokens.aitist.ai Model Square (Nov 20 2026), BRAND.md, Feishu brand plan, published research notes."""
import re, pathlib

SITE = pathlib.Path(__file__).resolve().parents[1] / 'dist'
TOKENS = 'https://tokens.aitist.ai'
SIGNUP = f'{TOKENS}/sign-up'
TG = 'https://t.me/hokeemDeng'
LOGO = '<svg viewBox="36 40 128 120" aria-hidden="true"><path fill="currentColor" d="M36 40H164V68H36Z M158.3 76L89.7 124H41.7L110.3 76Z M36 132H164V160H36Z"/></svg>'
AR = '<span aria-hidden="true">→</span>'

# name, vendor_en, vendor_zh, logo, in, out, tags_en, tags_zh, glow
MODELS = [
    ('deepseek-ai/DeepSeek-V4.1-Flash', 'DeepSeek', '深度求索 DeepSeek', 'deepseek-color', '0.10', '0.20', ['Fast', 'General', 'Batch'], ['快速', '通用', '批处理'], 'rgba(77,107,254,.18)'),
    ('zai-org/GLM-5.3', 'Zhipu', '智谱', 'zhipu-color', '0.10', '0.20', ['Coding', 'Agents', 'General'], ['编程', 'Agent', '通用'], 'rgba(52,96,252,.16)'),
    ('glm-5.3-flash', 'Zhipu', '智谱', 'zhipu-color', '0.10', '0.20', ['Low latency', 'Chat'], ['低延迟', '对话'], 'rgba(52,96,252,.16)'),
    ('moonshotai/Kimi-K3.1-Pro', 'Moonshot', '月之暗面 Moonshot', 'kimi-light', '0.20', '0.40', ['Agents', 'Long sessions', 'Coding'], ['Agent', '长会话', '编程'], 'rgba(2,122,255,.16)'),
    ('qwen3.8-flash-next', 'Alibaba', '阿里巴巴 通义', 'qwen-color', '0.10', '0.20', ['Low latency', 'General'], ['低延迟', '通用'], 'rgba(97,92,237,.18)'),
]


class P:  # language helper
    def __init__(self, lang): self.lang = lang; self.zh = lang == 'zh'
    def t(self, en, zh): return zh if self.zh else en
    def u(self, path):  # internal link in this language
        return ('/zh' + path) if self.zh else path


def nav(L, path):
    sw = (f'<a class="lang" href="{path}" hreflang="en" lang="en">EN · <b>中文</b></a>' if L.zh
          else f'<a class="lang" href="/zh{path}" hreflang="zh-CN" lang="zh-CN"><b>EN</b> · 中文</a>')
    return f'''<header class="nav" role="banner">
  <a class="brand" href="{L.u('/')}" aria-label="Zenith home">{LOGO}<span>Zenith</span></a>
  <nav aria-label="Main">
    <a href="{L.u('/platform/')}">{L.t('Platform', '平台')}</a>
    <a href="{L.u('/models/')}">{L.t('Models', '模型')}</a>
    <a href="{L.u('/blog/')}">{L.t('Engineering', '技术博客')}</a>
    <a href="{L.u('/news/')}">{L.t('News', '动态')}</a>
    <a href="{L.u('/about/')}">{L.t('About', '关于')}</a>
  </nav>
  <div class="nav-right">{sw}<a class="btn btn-light btn-sm" href="{SIGNUP}">{L.t('Start building', '开始使用')}</a></div>
</header>'''


def footer(L):
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <a class="brand" href="{L.u('/')}" aria-label="Zenith home">{LOGO}<span>Zenith</span></a>
        <p>{L.t('Efficient inference for open models. Any GPU we touch turns to gold.', '面向开源模型的高效推理。经我们之手的每一块 GPU，都会点石成金。')}</p>
        <div class="actions" style="margin-top:22px"><a class="btn btn-light btn-sm" href="{SIGNUP}">{L.t('Start building', '开始使用')} {AR}</a></div>
      </div>
      <div class="footer-cols">
        <div><p class="label">{L.t('Product', '产品')}</p><a href="{L.u('/platform/')}">Zenith Tokens</a><a href="{L.u('/models/')}">{L.t('Models &amp; pricing', '模型与价格')}</a><a href="{TOKENS}/dashboard">{L.t('Console', '控制台')} ↗</a><a href="{TOKENS}/rankings">{L.t('Rankings', '排行榜')} ↗</a></div>
        <div><p class="label">{L.t('Developers', '开发者')}</p><a href="{L.u('/docs/')}">{L.t('Quickstart', '快速开始')}</a><a href="{L.u('/credits/')}">{L.t('Developer credits', '开发者额度')}</a><a href="https://docs.newapi.pro/">{L.t('API reference', 'API 文档')} ↗</a></div>
        <div><p class="label">{L.t('Research', '研究')}</p><a href="{L.u('/blog/')}">{L.t('Engineering', '技术博客')}</a><a href="{L.u('/blog/pcie-inference/')}">{L.t('Inference without NVLink', '无 NVLink 推理')}</a><a href="{L.u('/blog/million-token-context/')}">{L.t('Million-token context', '百万 token 上下文')}</a></div>
        <div><p class="label">{L.t('Company', '公司')}</p><a href="{L.u('/about/')}">{L.t('About', '关于')}</a><a href="{L.u('/news/')}">{L.t('News', '动态')}</a><a href="{L.u('/security/')}">{L.t('Security', '安全')}</a><a href="{TG}">Telegram @hokeemDeng ↗</a></div>
      </div>
    </div>
    <div class="footer-mark" aria-hidden="true">Zenith</div>
    <div class="footer-base"><span>{L.t('© 2026 Zenith', '© 2026 芯华算 Zenith')}</span><span>{L.t('Made from sand', '源于沙')}</span></div>
  </div>
</footer>'''


def write(L, path, title, desc, body):
    lang = 'zh-CN' if L.zh else 'en'
    alt_en, alt_zh = path, '/zh' + path
    html = f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0a0a0a">
<title>{title} · Zenith</title>
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="zh-CN" href="{alt_zh}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/v2.css?v=7">
<link rel="stylesheet" href="/assets/pages.css?v=5">
</head>
<body class="home v2">
<a class="skip" href="#main">{L.t('Skip to content', '跳到正文')}</a>
{nav(L, path)}
<main id="main" class="page">
{body}
</main>
{footer(L)}
<script src="/assets/v2.js?v=5" defer></script>
</body>
</html>
'''
    if L.zh: html = html.replace('href="/blog', 'href="/zh/blog')
    out = SITE / (('zh/' if L.zh else '') + path.strip('/')) / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print('wrote', out.relative_to(SITE))


def hero(label, h1, lede, actions, art=None):
    a = f'<div class="page-hero-art reveal"><img src="{art}" alt="" decoding="async"></div>' if art else ''
    return f'''<section class="page-hero"><div class="wrap">
  <p class="label reveal">{label}</p>
  <h1 class="reveal">{h1}</h1>
  <p class="lede reveal">{lede}</p>
  <div class="actions reveal">{actions}</div>
  {a}
</div></section>'''


def code_curl(L, model='deepseek-ai/DeepSeek-V4.1-Flash'):
    hello = L.t('Hello, Zenith', '你好，Zenith')
    return f'''<div class="code"><div class="code-bar"><span><i></i><i></i><i></i></span><span>curl · {L.t('OpenAI-compatible', '兼容 OpenAI')}</span></div><pre><span class="kw">curl</span> {TOKENS}/v1/chat/completions \\
  -H <span class="s">"Authorization: Bearer $ZENITH_API_KEY"</span> \\
  -H <span class="s">"Content-Type: application/json"</span> \\
  -d <span class="s">'{{
    "model": "{model}",
    "messages": [{{"role": "user", "content": "{hello}"}}]
  }}'</span></pre></div>'''


def code_py(L):
    return f'''<div class="code"><div class="code-bar"><span><i></i><i></i><i></i></span><span>python · openai SDK</span></div><pre><span class="kw">from</span> openai <span class="kw">import</span> OpenAI

client = OpenAI(
    base_url=<span class="s">"{TOKENS}/v1"</span>,
    api_key=<span class="s">"sk-..."</span>,  <span class="c"># {L.t('create a key in the console', '在控制台创建 key')}</span>
)

reply = client.chat.completions.create(
    model=<span class="s">"zai-org/GLM-5.3"</span>,
    messages=[{{<span class="s">"role"</span>: <span class="s">"user"</span>, <span class="s">"content"</span>: <span class="s">"{L.t('Summarize this repo.', '总结一下这个仓库。')}"</span>}}],
    stream=<span class="kw">True</span>,
)
<span class="kw">for</span> chunk <span class="kw">in</span> reply:
    print(chunk.choices[0].delta.content <span class="kw">or</span> <span class="s">""</span>, end=<span class="s">""</span>)</pre></div>'''


def stats(L):
    return f'''<div class="stat-row">
  <a href="/blog/pcie-inference/"><b>40.6 → 5.9</b><span>{L.t('µs one-row all-reduce on PCIe GPUs', 'µs，PCIe GPU 上的单行 all-reduce')}</span></a>
  <a href="/blog/million-token-context/"><b>1,045,368</b><span>{L.t('input tokens in a measured retrieval run', '输入 token，一次实测的长上下文检索')}</span></a>
  <a href="/blog/kimi-deployment-frontier/"><b>1,991</b><span>{L.t('output tok/s, Kimi-K3 on 16 B200 GPUs', '输出 tok/s，Kimi-K3 运行于 16 张 B200')}</span></a>
  <a href="/blog/agent-correctness/"><b>97 → 0</b><span>{L.t('empty-argument failures, 1,600 forced calls', '空参数错误，1,600 次强制调用')}</span></a>
</div>
<p class="fine">{L.t('Research measurements under the conditions described in each note. They show how we engineer the stack. They are not platform service levels.', '以上为各篇技术文章中所述条件下的研究实测，用于说明我们如何打磨推理栈，不代表平台的服务等级承诺。')}</p>'''


def cta_band(L):
    return f'''<section class="cta-band"><div class="wrap">
  <p class="label reveal">Zenith Tokens</p>
  <h2 class="display-sm reveal">{L.t('Make your first call in <em>minutes.</em>', '几分钟内，完成<em>第一次调用。</em>')}</h2>
  <div class="actions reveal"><a class="btn btn-light" href="{SIGNUP}">{L.t('Get an API key', '获取 API key')} {AR}</a><a class="btn btn-ghost" href="{L.u('/docs/')}">{L.t('Read the quickstart', '阅读快速开始')}</a><a class="btn btn-ghost" href="{TG}">{L.t('Talk to us on Telegram', '在 Telegram 联系我们')}</a></div>
</div></section>'''


def logo_img(name, cls='', size=None):
    return f'<img class="{cls}" src="/assets/logos/{name}.svg" alt="" width="{size or 30}" height="{size or 30}">'


def build(L):
    # ---------------------------------------------------------------- platform
    write(L, '/platform/', 'Zenith Tokens', L.t('Zenith Tokens: one OpenAI-compatible API for leading open models, priced to be used.', 'Zenith Tokens：一个兼容 OpenAI 的 API，调用主流开源模型，价格亲民。'),
    hero(L.t('Zenith Tokens', 'Zenith Tokens · 芯华算 Token 平台'),
         L.t('Open models, one API. <em>Priced to be used.</em>', '开源模型，一个 API。<em>价格让你用得起。</em>'),
         L.t('Zenith Tokens is our inference platform: one OpenAI-compatible gateway to DeepSeek, GLM, Kimi and Qwen, served on the stack we research and measure. Open models start at $0.10 per million input tokens.',
             'Zenith Tokens 是我们的推理平台：通过一个兼容 OpenAI 的网关，调用 DeepSeek、GLM、Kimi 和 Qwen，运行在我们持续研究和实测的推理栈上。开源模型输入低至每百万 token 0.10 美元。'),
         f'<a class="btn btn-light" href="{SIGNUP}">{L.t("Start building", "开始使用")} {AR}</a><a class="btn btn-ghost" href="{L.u("/models/")}">{L.t("Models &amp; pricing", "模型与价格")}</a><a class="btn btn-ghost" href="{TOKENS}/sign-in">{L.t("Sign in", "登录")}</a>',
         '/assets/tiles/gpus-wide.webp') + f'''
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Works with what you use', '兼容你在用的工具')}</p><h2 class="display-sm reveal">{L.t('Change one URL.', '只需改一个地址。')}</h2></div><p class="reveal">{L.t(f'Point any OpenAI-compatible client at <code>{TOKENS}/v1</code>. Desktop clients can be configured in one click from the console.', f'把任意兼容 OpenAI 的客户端指向 <code>{TOKENS}/v1</code> 即可。桌面客户端可在控制台一键配置。')}</p></div>
  <div class="works reveal"><span>OpenAI SDK (Python, Node)</span><span>Cherry Studio</span><span>CC Switch</span><span>curl</span><span>{L.t('Any OpenAI-compatible client', '任意兼容 OpenAI 的客户端')}</span></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Built for', '适用场景')}</p><h2 class="display-sm reveal">{L.t('Real workloads, at open-model prices.', '真实任务，开源模型的价格。')}</h2></div></div>
  <div class="cards-4">
    <div class="box reveal"><p class="k">{L.t('Coding agents', '编程 Agent')}</p><h3>{L.t('Long sessions, many tool calls.', '长会话，大量工具调用。')}</h3><p>{L.t('GLM-5.3 and Kimi-K3.1-Pro behind one key. Our correctness work targets complete streams and valid tool arguments.', '一个 key 调用 GLM-5.3 和 Kimi-K3.1-Pro。我们的正确性工作专注于完整的流式输出和合法的工具参数。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Assistants &amp; chat', '助手与对话')}</p><h3>{L.t('Streaming chat for products.', '为产品提供流式对话。')}</h3><p>{L.t('Fast Flash models for interactive apps, with server-sent events and per-key limits.', '快速的 Flash 模型适合交互应用，支持 SSE 流式输出和按 key 限流。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Search &amp; RAG', '检索与 RAG')}</p><h3>{L.t('Read long documents.', '读懂长文档。')}</h3><p>{L.t('Built on our long-context serving research, where capacity, retrieval and latency are measured together.', '基于我们的长上下文推理研究：容量、检索与延迟一起实测。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Batch &amp; data', '批处理与数据')}</p><h3>{L.t('Process at scale.', '规模化处理。')}</h3><p>{L.t('Classification, extraction and synthesis from $0.10 in / $0.20 out per million tokens.', '分类、抽取、合成，每百万 token 输入 0.10 / 输出 0.20 美元起。')}</p></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('How it works', '如何使用')}</p><h2 class="display-sm reveal">{L.t('Three steps to production.', '三步上线。')}</h2></div></div>
  <ol class="steps-h">
    <li class="reveal"><b>01</b><h3>{L.t('Create a key', '创建 key')}</h3><p>{L.t('Sign up, then create an API key in the console. Set quotas and permissions per key.', '注册后在控制台创建 API key，可为每个 key 设置额度和权限。')}</p></li>
    <li class="reveal"><b>02</b><h3>{L.t('Connect', '接入')}</h3><p>{L.t('Use the OpenAI-compatible endpoint from your SDK, agent framework or desktop client.', '在 SDK、Agent 框架或桌面客户端里使用兼容 OpenAI 的接口。')}</p></li>
    <li class="reveal"><b>03</b><h3>{L.t('Monitor', '监控')}</h3><p>{L.t('Track tokens, cost and latency per key and per model in real time.', '按 key、按模型实时查看 token 用量、费用和延迟。')}</p></li>
  </ol>
  <div style="margin-top:48px" class="reveal">{code_curl(L)}</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Platform', '平台能力')}</p><h2 class="display-sm reveal">{L.t('The parts you would otherwise build.', '这些你本来要自己搭的，我们都做好了。')}</h2></div></div>
  <div class="cards-3">
    <div class="box reveal"><p class="k">{L.t('Unified API', '统一 API')}</p><h3>{L.t('One protocol, many models.', '一个协议，多个模型。')}</h3><p>{L.t('OpenAI-compatible chat routes, with Claude, Gemini and Responses-style routes supported by the gateway.', '兼容 OpenAI 的对话接口，网关同时支持 Claude、Gemini 和 Responses 风格的接口。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Routing', '路由')}</p><h3>{L.t('Load balancing.', '负载均衡。')}</h3><p>{L.t('Requests are spread across upstream channels with automatic failover.', '请求分散到多个上游渠道，故障自动切换。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Control', '管控')}</p><h3>{L.t('Rate limits &amp; quotas.', '限流与额度。')}</h3><p>{L.t('Set limits per key so one runaway agent cannot drain a team budget.', '按 key 设置上限，避免某个失控的 Agent 耗光团队预算。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Billing', '计费')}</p><h3>{L.t('Pay as you go.', '按量付费。')}</h3><p>{L.t('Token-based pricing with real-time usage and cost tracking.', '按 token 计费，实时追踪用量和费用。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Teams', '团队')}</p><h3>{L.t('Shared access.', '共享访问。')}</h3><p>{L.t('Multi-user management with flexible permissions.', '多用户管理，权限灵活分配。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Transparency', '透明')}</p><h3>{L.t('Live status &amp; rankings.', '实时状态与排行。')}</h3><p>{L.t('Per-model availability, latency and usage rankings are public on the platform.', '每个模型的可用率、延迟和用量排行，都在平台上公开。')}</p></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('The engineering underneath', '底层的工程')}</p><h2 class="display-sm reveal">{L.t('We publish the measurements.', '我们公开实测数据。')}</h2></div><p class="reveal">{L.t('Cheaper tokens come from better systems. Each number links to the note that explains how it was measured.', '更便宜的 token 来自更好的系统。每个数字都链接到说明测量方法的文章。')}</p></div>
  <div class="reveal">{stats(L)}</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Pricing', '价格')}</p><h2 class="display-sm reveal">{L.t('From $0.10 per million tokens.', '每百万 token 0.10 美元起。')}</h2></div><a class="btn btn-ghost btn-sm reveal" href="{L.u('/models/')}">{L.t('All models', '全部模型')} {AR}</a></div>
  <div class="cards-3">''' + ''.join(f'''
    <a class="box reveal" href="{L.u('/models/')}"><p class="k">{logo_img(lg, size=18)} {L.t(ven, vzh)}</p><h3>{n.split('/')[-1]}</h3><p>{L.t(f'${i} input · ${o} output per 1M tokens', f'输入 ${i} · 输出 ${o} / 百万 token')}</p><span class="more">{L.t('Details', '详情')} {AR}</span></a>'''
        for n, ven, vzh, lg, i, o, *_ in [MODELS[0], MODELS[1], MODELS[3]]) + f'''
  </div>
</div></section>
''' + cta_band(L))

    # ---------------------------------------------------------------- models
    cards = ''.join(f'''
    <article class="model reveal" style="--glow:{glow}">
      <div class="model-logo">{logo_img(lg)}</div>
      <div><h3>{n.split('/')[-1]}</h3><p class="vendor">{L.t(ven, vzh)} · <code style="font-size:12.5px">{n}</code></p></div>
      <div class="tags">{''.join(f'<i>{x}</i>' for x in (tz if L.zh else te))}</div>
      <div class="price"><div><small>{L.t('Input', '输入')}</small><b>${i} <em>/ 1M</em></b></div><div><small>{L.t('Output', '输出')}</small><b>${o} <em>/ 1M</em></b></div></div>
    </article>''' for n, ven, vzh, lg, i, o, te, tz, glow in MODELS)
    vendors = ''.join(f'<span>{logo_img(lg, size=28)}{name}</span>' for lg, name in
                      [('deepseek-color', 'DeepSeek'), ('zhipu-color', L.t('Zhipu GLM', '智谱 GLM')), ('kimi-light', 'Kimi'), ('qwen-color', L.t('Qwen', '通义千问 Qwen'))])
    rows = '\n'.join(f'<tr><td class="m">{logo_img(lg, "logo", 20)}{n}<small>{L.t(ven, vzh)}</small></td>'
                     f'<td class="p">${i} <em>/ 1M</em></td><td class="p">${o} <em>/ 1M</em></td><td>{L.t("Chat · OpenAI-compatible", "对话 · 兼容 OpenAI")}</td></tr>'
                     for n, ven, vzh, lg, i, o, *_ in MODELS)
    write(L, '/models/', L.t('Models & pricing', '模型与价格'), L.t('Open models on Zenith Tokens with per-token pricing.', 'Zenith Tokens 上的开源模型与按 token 计价。'),
    hero(L.t('Models &amp; pricing', '模型与价格'), L.t('Open models, <em>honest prices.</em>', '开源模型，<em>价格透明。</em>'),
         L.t('Every model is served through the same OpenAI-compatible API. Prices are per million tokens, billed by usage.', '所有模型都通过同一个兼容 OpenAI 的 API 提供，按每百万 token 计价，按量计费。'),
         f'<a class="btn btn-light" href="{SIGNUP}">{L.t("Get an API key", "获取 API key")} {AR}</a><a class="btn btn-ghost" href="{TOKENS}/pricing">{L.t("Live Model Square", "实时模型广场")} ↗</a><a class="btn btn-ghost" href="{TOKENS}/rankings">{L.t("Usage rankings", "用量排行")} ↗</a>') + f'''
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Available now', '当前可用')}</p><h2 class="display-sm reveal">{L.t('Five models, one key.', '五个模型，一个 key。')}</h2></div><p class="reveal">{L.t('Copy the full model name into the <code>model</code> field of any OpenAI-compatible request.', '把完整的模型名填入任意兼容 OpenAI 请求的 <code>model</code> 字段即可。')}</p></div>
  <div class="model-grid">{cards}
    <a class="model reveal" href="{TOKENS}/pricing" style="justify-content:center;align-items:flex-start;background:#0f0f0e">
      <div class="model-logo" style="font-size:24px;color:var(--gold)">+</div>
      <h3>{L.t('More on the live Model Square', '更多模型见实时模型广场')}</h3>
      <p style="color:var(--fg-2);font-size:15px">{L.t('Serving variants, live latency, throughput and availability for every model.', '各模型的服务变体、实时延迟、吞吐与可用率。')}</p>
      <span class="more" style="margin-top:auto">tokens.aitist.ai/pricing ↗</span>
    </a>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Price list', '价格表')}</p><h2 class="display-sm reveal">{L.t('Per million tokens, in USD.', '每百万 token，美元计价。')}</h2></div></div>
  <div class="tbl-wrap reveal"><table class="tbl">
    <thead><tr><th>{L.t('Model', '模型')}</th><th>{L.t('Input', '输入')}</th><th>{L.t('Output', '输出')}</th><th>{L.t('Endpoint', '接口')}</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table></div>
  <p class="fine">{L.t(f'Prices as listed on the Zenith Tokens Model Square on November 20, 2026. Kimi-K3.1-Pro is also served as kimi-k3.1-pro and kimi-k3.1-pro-sgl. Live prices and status are on <a href="{TOKENS}/pricing" style="color:var(--fg)">tokens.aitist.ai/pricing</a>, which is the source of truth.',
      f'价格取自 2026 年 11 月 20 日的 Zenith Tokens 模型广场。Kimi-K3.1-Pro 另有 kimi-k3.1-pro 与 kimi-k3.1-pro-sgl 两个服务变体。实时价格与状态以 <a href="{TOKENS}/pricing" style="color:var(--fg)">tokens.aitist.ai/pricing</a> 为准。')}</p>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Choosing a model', '如何选模型')}</p><h2 class="display-sm reveal">{L.t('Start fast, scale up.', '先跑起来，再按需升级。')}</h2></div></div>
  <div class="cards-3">
    <div class="img-box reveal"><img src="/assets/tiles/chip.webp" alt="" loading="lazy"><div><p class="k">{L.t('Default', '默认之选')}</p><h3>DeepSeek-V4.1-Flash</h3><p>{L.t('A strong, fast general model at the lowest price tier. A good first choice for chat, extraction and batch jobs.', '最低价档里强劲又快速的通用模型，适合作为对话、抽取和批处理的首选。')}</p></div></div>
    <div class="img-box reveal"><img src="/assets/tiles/gold-gpu.webp" alt="" loading="lazy"><div><p class="k">{L.t('Coding &amp; agents', '编程与 Agent')}</p><h3>GLM-5.3 · Kimi-K3.1-Pro</h3><p>{L.t('For long agent sessions and tool use. Kimi-K3.1-Pro is offered in several serving variants.', '适合长时间的 Agent 会话与工具调用。Kimi-K3.1-Pro 提供多个服务变体。')}</p></div></div>
    <div class="img-box reveal"><img src="/assets/tiles/crystal.webp" alt="" loading="lazy"><div><p class="k">{L.t('Low latency', '低延迟')}</p><h3>GLM-5.3-Flash · Qwen3.8-Flash-Next</h3><p>{L.t('Lightweight models for interactive products where time to first token matters.', '轻量模型，适合首 token 延迟敏感的交互式产品。')}</p></div></div>
  </div>
</div></section>
''' + cta_band(L))

    # ---------------------------------------------------------------- docs
    write(L, '/docs/', L.t('Quickstart', '快速开始'), L.t('Make your first call to Zenith Tokens in minutes.', '几分钟内完成对 Zenith Tokens 的第一次调用。'),
    hero(L.t('Developers · Quickstart', '开发者 · 快速开始'), L.t('Your first call <em>in three steps.</em>', '三步，<em>完成第一次调用。</em>'),
         L.t('Zenith Tokens speaks the OpenAI API. If your code already works with OpenAI, change the base URL and the key.', 'Zenith Tokens 兼容 OpenAI API。如果你的代码已经能调用 OpenAI，只需更换 base URL 和 key。'),
         f'<a class="btn btn-light" href="{SIGNUP}">{L.t("Create an account", "注册账号")} {AR}</a><a class="btn btn-ghost" href="https://docs.newapi.pro/">{L.t("Full API reference", "完整 API 文档")} ↗</a>') + f'''
<section class="sec"><div class="wrap split">
  <aside class="split-aside"><p class="label">{L.t('On this page', '本页内容')}</p><a href="#key">{L.t('1. Get a key', '1. 获取 key')}</a><a href="#call">{L.t('2. Make a call', '2. 发起调用')}</a><a href="#apps">{L.t('3. Use it in apps', '3. 在应用中使用')}</a><a href="#help">{L.t('Help', '帮助')}</a></aside>
  <div class="prose">
    <h2 id="key">{L.t('1. Get a key', '1. 获取 key')}</h2>
    <p>{L.t(f'<a href="{SIGNUP}">Create an account</a> on Zenith Tokens, open the <a href="{TOKENS}/dashboard">console</a> and create an API key. You can set a quota, an expiry and the models each key may call.', f'在 Zenith Tokens <a href="{SIGNUP}">注册账号</a>，打开<a href="{TOKENS}/dashboard">控制台</a>创建 API key。每个 key 都可以设置额度、有效期和可调用的模型。')}</p>
    <p>Base URL: <strong>{TOKENS}/v1</strong></p>
    <h2 id="call">{L.t('2. Make a call', '2. 发起调用')}</h2>
    <p>{L.t('With curl or the OpenAI Python SDK:', '使用 curl 或 OpenAI Python SDK：')}</p>
  </div>
</div>
<div class="wrap split" style="margin-top:20px"><div></div><div style="max-width:760px">{code_curl(L)}<div style="height:16px"></div>{code_py(L)}</div></div>
<div class="wrap split" style="margin-top:20px"><div></div>
  <div class="prose">
    <p>{L.t(f'Any model on the <a href="{L.u("/models/")}">models page</a> works. Copy the model name exactly, for example <strong>moonshotai/Kimi-K3.1-Pro</strong>.', f'<a href="{L.u("/models/")}">模型页</a>上的任意模型都可以调用，模型名需完整复制，例如 <strong>moonshotai/Kimi-K3.1-Pro</strong>。')}</p>
    <h2 id="apps">{L.t('3. Use it in apps', '3. 在应用中使用')}</h2>
    <ul>
      <li>{L.t('<strong>Cherry Studio, CC Switch:</strong> use the one-click configuration in the console, or add an OpenAI-compatible provider with the base URL above and your key.', '<strong>Cherry Studio、CC Switch：</strong>使用控制台中的一键配置，或手动添加一个兼容 OpenAI 的服务商，填入上面的 base URL 和你的 key。')}</li>
      <li>{L.t('<strong>Agent frameworks:</strong> any framework that accepts an OpenAI base URL works. Streaming uses server-sent events.', '<strong>Agent 框架：</strong>任何支持自定义 OpenAI base URL 的框架都可以直接使用，流式输出采用 SSE。')}</li>
      <li>{L.t('<strong>Monitoring:</strong> usage, cost and latency per key appear in the console in real time.', '<strong>监控：</strong>每个 key 的用量、费用和延迟会实时显示在控制台。')}</li>
    </ul>
    <h2 id="help">{L.t('Help', '帮助')}</h2>
    <p>{L.t(f'The full API reference for the gateway is at <a href="https://docs.newapi.pro/">docs.newapi.pro</a>. For anything else, message us on Telegram at <a href="{TG}">@hokeemDeng</a>.', f'网关的完整 API 文档见 <a href="https://docs.newapi.pro/">docs.newapi.pro</a>。其他问题请在 Telegram 联系 <a href="{TG}">@hokeemDeng</a>。')}</p>
  </div>
</div></section>
''' + cta_band(L))

    # ---------------------------------------------------------------- news
    NEWS = [
        ('Nov 20, 2026', '2026-11-20', ('Product', '产品'), ('Zenith Tokens: open models through one API', 'Zenith Tokens：一个 API 调用开源模型'), ('DeepSeek, GLM, Kimi and Qwen through one OpenAI-compatible endpoint, from $0.10 per million input tokens.', '通过一个兼容 OpenAI 的接口调用 DeepSeek、GLM、Kimi 和 Qwen，输入低至每百万 token 0.10 美元。'), L.u('/platform/')),
        ('Nov 20, 2026', '2026-11-20', ('Program', '计划'), ('Developer credits: first cohort', '开发者额度计划：首批开放'), ('Credits for developers, creators and researchers building real projects on open models.', '面向用开源模型做真实项目的开发者、创作者和研究者。'), L.u('/credits/')),
        ('Nov 19, 2026', '2026-11-19', ('Company', '公司'), ('Aitist is now Zenith', 'Aitist 更名为 Zenith'), ('A new name and mark for the same work: making useful AI cheaper to serve.', '新的名字和标志，不变的使命：让有用的 AI 更便宜地被提供。'), L.u('/about/')),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('Rethinking inference without NVLink', '没有 NVLink 时，重新思考推理'), ('On PCIe-connected GPUs, a one-row all-reduce went from 40.6 to 5.9 µs.', '在 PCIe 互联的 GPU 上，单行 all-reduce 从 40.6 µs 降到 5.9 µs。'), '/blog/pcie-inference/'),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('Making a million tokens usable', '让百万 token 真正可用'), ('A measured retrieval run at 1,045,368 input tokens, with capacity and latency evaluated together.', '一次 1,045,368 输入 token 的实测检索，容量与延迟一起评估。'), '/blog/million-token-context/'),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('Finding the useful throughput frontier', '寻找有用的吞吐边界'), ('Kimi-K3 on 16 B200 GPUs: 1,991 output tok/s while each user keeps a usable stream.', 'Kimi-K3 运行于 16 张 B200：总输出 1,991 tok/s，同时保证每位用户的生成速度可用。'), '/blog/kimi-deployment-frontier/'),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('Correctness beyond a successful response', '正确性，不止于接口返回成功'), ('Empty-argument tool-call failures fell from 97 to 0 across 1,600 forced calls.', '在 1,600 次强制调用中，空参数工具调用错误从 97 次降到 0。'), '/blog/agent-correctness/'),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('A cache hit is not the end of the journey', '缓存命中，并不是终点'), ('Why a high cache hit rate can still be slow: KV transfer, scheduling and first-token latency.', '为什么缓存命中率高仍可能慢：KV 传输、调度与首 token 延迟。'), '/blog/kv-aware-serving/'),
        ('Nov 13, 2026', '2026-11-13', ('Engineering', '技术'), ('Every iteration should leave better evidence', '每一次迭代，都应留下更好的证据'), ('How engineers, agents and a shared knowledge base drove 227 commits and 36 merged PRs.', '工程师、Agent 与共享知识库如何协作，完成 227 次提交和 36 个合并 PR。'), '/blog/evidence-driven-engineering/'),
    ]
    en_note = ''
    rows = '\n'.join(f'<a class="news-row reveal" href="{L.u(u) if u.startswith("/blog") else u}"><time datetime="{iso}">{L.t(d, iso)}</time><div><p class="tag">{L.t(*tg)}</p><h3 style="margin-top:10px">{L.t(*h)} {en_note if u.startswith("/blog") else ""}</h3><p>{L.t(*p)}</p></div><span class="more" style="color:var(--fg-2)">{AR}</span></a>' for d, iso, tg, h, p, u in NEWS)
    write(L, '/news/', L.t('News', '动态'), L.t('Product updates, programs and engineering notes from Zenith.', 'Zenith 的产品更新、计划与技术文章。'),
    hero(L.t('News', '动态'), L.t('What we shipped, <em>with dates.</em>', '我们做了什么，<em>都有日期。</em>'),
         L.t('Product updates, programs and engineering notes. Every entry links to the source.', '产品更新、计划与技术文章，每一条都链接到原文。'),
         f'<a class="btn btn-ghost" href="/blog/">{L.t("Engineering notes", "技术博客")}</a><a class="btn btn-ghost" href="{TG}">{L.t("Press &amp; partnerships: Telegram", "媒体与合作：Telegram")}</a>') + f'''
<section class="sec"><div class="wrap"><div class="news-list">
{rows}
</div></div></section>''')

    # ---------------------------------------------------------------- about
    write(L, '/about/', L.t('About', '关于'), L.t('Zenith makes high-quality open models affordable to use, through inference engineering.', 'Zenith 用推理工程，让高质量开源模型更便宜、更好用。'),
    hero(L.t('About Zenith', '关于芯华算 Zenith'), L.t('Useful AI should cost <em>less to serve.</em>', '有用的 AI，<em>应该更便宜地被提供。</em>'),
         L.t('We are an inference company. We make high-quality open models fast, correct and affordable, and we publish how.', '我们是一家推理公司：让高质量开源模型更快、更正确、更便宜，并公开我们是怎么做到的。'),
         f'<a class="btn btn-light" href="{SIGNUP}">{L.t("Try Zenith Tokens", "试用 Zenith Tokens")} {AR}</a><a class="btn btn-ghost" href="/blog/">{L.t("Read the engineering", "阅读技术博客")}</a>',
         '/assets/tiles/sand.webp') + f'''
<section class="sec"><div class="wrap split">
  <aside class="split-aside"><p class="label">{L.t('Contents', '目录')}</p><a href="#why">{L.t('Why inference', '为什么做推理')}</a><a href="#what">{L.t('What we build', '我们做什么')}</a><a href="#how">{L.t('How we work', '我们怎么做')}</a><a href="#values">{L.t('What we value', '我们看重什么')}</a><a href="#contact">{L.t('Contact', '联系')}</a></aside>
  <div class="prose">
    {'' if L.zh else '<blockquote>Make high-quality open models a productive tool that more people can afford.</blockquote>'}
    <h2 id="why">{L.t('Why inference', '为什么做推理')}</h2>
    <p>{L.t('Open models are now good enough for most real work: coding, search, analysis, agents. What stands between them and everyday use is the cost and reliability of serving them. A model that is cheap to download can still be expensive to run, slow to answer, or subtly wrong in production.', '开源模型已经能胜任大多数真实工作：编程、检索、分析、Agent。挡在它们和日常使用之间的，是推理的成本与可靠性。一个可以免费下载的模型，在生产环境里依然可能运行昂贵、响应缓慢，或者出现不易察觉的错误。')}</p>
    <p>{L.t("At their core, GPUs are sand. The value comes from what the system around them does: how chips talk to each other, how memory holds a long context, how a scheduler keeps every user's stream fast, how an agent's tool call arrives intact. That is where we work.", 'GPU 的本质是沙。价值来自它周围的系统：芯片之间如何通信，显存如何承载长上下文，调度器如何让每位用户的输出都保持流畅，Agent 的工具调用如何完整无误地送达。这正是我们工作的地方。')}</p>
    <h2 id="what">{L.t('What we build', '我们做什么')}</h2>
    <p>{L.t('<strong>Engineering.</strong> We optimize the inference path end to end: GPU communication without NVLink, million-token context, throughput at a usable per-user speed, KV-aware serving and agent correctness. We publish the methods and the numbers in our <a href="/blog/">engineering notes</a>.', '<strong>工程。</strong>我们端到端优化推理链路：没有 NVLink 时的 GPU 通信、百万 token 上下文、保证单用户速度前提下的吞吐、感知 KV 的服务调度，以及 Agent 的正确性。方法和数据都公开在我们的<a href="/blog/">技术博客</a>里。')}</p>
    <p>{L.t(f'<strong>Zenith Tokens.</strong> Our <a href="{L.u("/platform/")}">platform</a> turns that work into a product: one OpenAI-compatible API for leading open models, priced so teams can actually use them.', f'<strong>Zenith Tokens。</strong>我们的<a href="{L.u("/platform/")}">平台</a>把这些工程成果变成产品：一个兼容 OpenAI 的 API，调用主流开源模型，价格让团队真正用得起。')}</p>
    <h2 id="how">{L.t('How we work', '我们怎么做')}</h2>
    <p>{L.t('Every change starts with a test. We measure the baseline before tuning, re-run and challenge our own conclusions, and keep the evidence so the next iteration starts further ahead. When a claim has limits, we say so next to the number.', '每一次改动都从一个测试开始。调优前先测基线，反复复现并质疑自己的结论，把证据留下来，让下一次迭代从更高的起点出发。一个结论有边界时，我们就把边界写在数字旁边。')}</p>
    <h2 id="values">{L.t('What we value', '我们看重什么')}</h2>
  </div>
</div>
<div class="wrap"><div class="values">
  <div class="reveal"><b>{L.t('Rigor', '技术求实')}</b><p>{L.t('Numbers come with conditions. We claim what we measured, nothing more.', '数字都带着条件。我们只声明实测过的结论，不多说一句。')}</p></div>
  <div class="reveal"><b>{L.t('Openness', '开放共建')}</b><p>{L.t('Open models, published methods, compatible APIs. Build with the ecosystem, not around it.', '开源模型、公开方法、兼容接口。和生态一起建设，而不是绕开它。')}</p></div>
  <div class="reveal"><b>{L.t('User value', '用户价值')}</b><p>{L.t("Lower cost and faster answers that show up in our users' products.", '更低的成本、更快的响应，体现在用户的产品里。')}</p></div>
  <div class="reveal"><b>{L.t('Trust', '服务可信')}</b><p>{L.t('Clear prices, visible status and a real person to talk to.', '清楚的价格、可见的状态，以及一个真正能找到的人。')}</p></div>
</div></div>
<div class="wrap split" style="margin-top:72px"><div></div><div class="prose">
  <h2 id="contact">{L.t('Contact', '联系')}</h2>
  <p>{L.t(f'Partnerships, enterprise use, press or questions: message <a href="{TG}">@hokeemDeng</a> on Telegram.', f'商务合作、企业使用、媒体或任何问题，请在 Telegram 联系 <a href="{TG}">@hokeemDeng</a>。')}</p>
</div></div></section>
''' + cta_band(L))

    # ---------------------------------------------------------------- credits
    write(L, '/credits/', L.t('Developer credits', '开发者额度'), L.t('Zenith developer credits for builders, creators and researchers using open models.', 'Zenith 开发者额度：支持用开源模型做事的开发者、创作者与研究者。'),
    hero(L.t('Developers · Credits', '开发者 · 额度'), L.t('Build on open models. <em>We cover the first tokens.</em>', '用开源模型去创造。<em>第一批 token，我们来出。</em>'),
         L.t('Developer credits on Zenith Tokens for people building real things: apps and agents, tutorials and reviews, research and teaching.', '为做真实项目的人提供 Zenith Tokens 额度：应用与 Agent、教程与评测、研究与教学。'),
         f'<a class="btn btn-light" href="{TG}">{L.t("Apply on Telegram", "通过 Telegram 申请")} {AR}</a><a class="btn btn-ghost" href="{L.u("/docs/")}">{L.t("Quickstart", "快速开始")}</a>',
         '/assets/tiles/gold-gpu.webp') + f'''
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="label reveal">{L.t('Three ways in', '三种方式')}</p><h2 class="display-sm reveal">{L.t('Credits sized to the work.', '额度与项目匹配。')}</h2></div><p class="reveal">{L.t('The first cohort is limited to 50 projects. Credit amounts are set per project after review.', '首批限 50 个项目，额度在审核后按项目确定。')}</p></div>
  <div class="cards-3">
    <div class="box reveal"><p class="k">{L.t('Starter', '入门')}</p><h3>{L.t('New developers', '新开发者')}</h3><p>{L.t('Trial credits to make your first calls and compare models on a real task.', '试用额度，用来完成第一次调用，并在真实任务上对比模型。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Creator', '创作者')}</p><h3>{L.t('Tutorials &amp; reviews', '教程与评测')}</h3><p>{L.t('For creators who publish an honest tutorial, benchmark or review showing the task, the calls and the cost.', '面向发布真实教程、测评或评测的创作者，展示任务、调用过程与成本。')}</p></div>
    <div class="box reveal"><p class="k">{L.t('Project', '项目')}</p><h3>{L.t('Projects &amp; research', '项目与研究')}</h3><p>{L.t('Larger support for open-source projects, products and research that run meaningful workloads on open models.', '为在开源模型上运行实际负载的开源项目、产品与研究提供更大支持。')}</p></div>
  </div>
</div></section>
<section class="sec"><div class="wrap split">
  <aside class="split-aside"><p class="label">{L.t('Details', '详情')}</p><a href="#apply">{L.t('How to apply', '如何申请')}</a><a href="#terms">{L.t('Terms', '条款')}</a></aside>
  <div class="prose">
    <h2 id="apply">{L.t('How to apply', '如何申请')}</h2>
    <p>{L.t(f'Message <a href="{TG}">@hokeemDeng</a> on Telegram with:', f'在 Telegram 联系 <a href="{TG}">@hokeemDeng</a>，并说明：')}</p>
    <ul><li>{L.t('what you are building and who it is for;', '你在做什么、面向谁；')}</li><li>{L.t('which models you plan to use and a rough monthly token estimate;', '计划使用哪些模型，以及大致的月度 token 用量；')}</li><li>{L.t('a link to your project, profile or past work.', '项目、个人主页或过往作品的链接。')}</li></ul>
    <p>{L.t('We review applications on a rolling basis. Projects that share feedback or publish their results may receive additional credits.', '我们滚动审核申请。分享反馈或公开成果的项目，可能获得追加额度。')}</p>
    <h2 id="terms">{L.t('Terms', '条款')}</h2>
    <p>{L.t('Credits apply to Zenith Tokens usage only. Each award states its amount, the models it covers, its validity period and any rate limits. Credits have no cash value and cannot be transferred.', '额度仅可用于 Zenith Tokens。每笔额度都会写明金额、适用模型、有效期与速率限制。额度不可兑现，不可转让。')}</p>
  </div>
</div></section>
''' + cta_band(L))

    # ---------------------------------------------------------------- security
    write(L, '/security/', L.t('Security', '安全'), L.t('How to report a security issue to Zenith.', '如何向 Zenith 报告安全问题。'),
    hero(L.t('Security', '安全'), L.t('Report a vulnerability.', '报告安全漏洞。'),
         L.t('If you find a security issue in Zenith Tokens or this website, please tell us privately first.', '如果你在 Zenith Tokens 或本网站发现安全问题，请先私下告知我们。'),
         f'<a class="btn btn-light" href="{TG}">{L.t("Report on Telegram", "通过 Telegram 报告")} {AR}</a>') + f'''
<section class="sec"><div class="wrap split">
  <aside class="split-aside"><p class="label">{L.t('Policy', '政策')}</p><a href="#scope">{L.t('Scope', '范围')}</a><a href="#report">{L.t('How to report', '如何报告')}</a><a href="#commitments">{L.t('Our commitments', '我们的承诺')}</a></aside>
  <div class="prose">
    <h2 id="scope">{L.t('Scope', '范围')}</h2>
    <p>{L.t('tokens.aitist.ai (the Zenith Tokens console and API) and this website.', 'tokens.aitist.ai（Zenith Tokens 控制台与 API）以及本网站。')}</p>
    <h2 id="report">{L.t('How to report', '如何报告')}</h2>
    <ul><li>{L.t(f'Message <a href="{TG}">@hokeemDeng</a> on Telegram with a description, the affected URL or endpoint, steps to reproduce and the impact you observed.', f'在 Telegram 联系 <a href="{TG}">@hokeemDeng</a>，附上问题描述、受影响的 URL 或接口、复现步骤以及观察到的影响。')}</li>
    <li>{L.t("Please do not access other users' data, degrade the service or run automated scans at high volume.", '请勿访问其他用户的数据、影响服务可用性，或进行高频自动化扫描。')}</li>
    <li>{L.t('Give us reasonable time to fix the issue before any public disclosure.', '在公开披露之前，请给我们合理的修复时间。')}</li></ul>
    <h2 id="commitments">{L.t('Our commitments', '我们的承诺')}</h2>
    <p>{L.t('We will acknowledge your report, keep you updated while we investigate, and credit you publicly once the issue is fixed if you would like us to.', '我们会确认收到你的报告，在调查过程中同步进展，并在修复后按你的意愿公开致谢。')}</p>
  </div>
</div></section>''')


EN, ZH = P('en'), P('zh')


def main():
    build(EN)
    build(ZH)
    homes()


# ---------------------------------------------------------------- homepage (EN) + /zh/ homepage
def product_band(L):
    chips = ''.join(f'<span>{logo_img(lg, size=16)} {n.split("/")[-1]} <em>${i} / ${o}</em></span>' for n, _, _, lg, i, o, *_ in MODELS)
    return f'''<section class="product" id="product">
  <div class="wrap product-grid">
    <div>
      <p class="label reveal">{L.t('Zenith Tokens', 'Zenith Tokens · 芯华算 Token 平台')}</p>
      <h2 class="display-sm reveal">{L.t('One API for open models. <em>Priced to be used.</em>', '一个 API，调用开源模型。<em>价格让你用得起。</em>')}</h2>
      <p class="lede reveal">{L.t('Call DeepSeek, GLM, Kimi and Qwen through one OpenAI-compatible endpoint, served on the stack we research. From $0.10 per million input tokens.', '通过一个兼容 OpenAI 的接口调用 DeepSeek、GLM、Kimi 和 Qwen，运行在我们研究的推理栈上。输入低至每百万 token 0.10 美元。')}</p>
      <div class="chips reveal">{chips}</div>
      <p class="fine reveal" style="margin-top:12px">{L.t('USD per 1M input / output tokens, November 20, 2026.', '美元 / 每百万 token（输入 / 输出），2026 年 11 月 20 日。')}</p>
      <div class="actions reveal"><a class="btn btn-light" href="{SIGNUP}">{L.t('Get an API key', '获取 API key')} {AR}</a><a class="btn btn-ghost" href="{L.u('/models/')}">{L.t('Models &amp; pricing', '模型与价格')}</a><a class="btn btn-ghost" href="{L.u('/docs/')}">{L.t('Quickstart', '快速开始')}</a></div>
    </div>
    <div class="reveal">{code_curl(L)}</div>
  </div>
</section>
'''


def update_home(src, L):
    s = src
    s = re.sub(r'<header class="nav" role="banner">.*?</header>', nav(L, '/'), s, flags=re.S)
    s = re.sub(r'<footer class="footer">.*?</footer>', footer(L), s, flags=re.S)
    s = re.sub(r'<section class="product" id="product">.*?</section>\n', product_band(L), s, flags=re.S)
    s = s.replace('pages.css?v=1', 'pages.css?v=5').replace('boot.js?v=7', 'boot.js?v=8')
    if '<link rel="alternate" hreflang' not in s:
        s = s.replace('<link rel="icon"', '<link rel="alternate" hreflang="en" href="/">\n<link rel="alternate" hreflang="zh-CN" href="/zh/">\n<link rel="icon"', 1)
    return s


def homes():
    idx = SITE / 'index.html'
    en_home = update_home(idx.read_text(), EN)
    idx.write_text(en_home)
    print('updated index.html')

    # Chinese homepage: translate visible strings of the English homepage
    H1_EN = re.search(r'<h1 id="intro-title"[^>]*>.*?</h1>', en_home, flags=re.S).group(0)
    H1_ZH = re.sub(r'>.*</h1>', '>经我们之手的每一块 <em class="dim">GPU</em>，<br>都会点石成<em class="gold">金。</em></h1>', H1_EN, flags=re.S)
    TR = [
        ('Efficient inference', '高效推理'),
        ('At their core, GPUs are sand. We make that sand smarter, so useful AI costs less to serve.', 'GPU 的本质是沙。我们让这些沙变得更聪明，让有用的 AI 以更低的成本被提供。'),
        ('Start building', '开始使用'), ('Explore Zenith Tokens', '了解 Zenith Tokens'),
        ('Communication', '通信'), ('Long context', '长上下文'), ('Throughput', '吞吐'), ('Reliability', '可靠性'),
        ('From silicon to possibility', '从硅到可能'),
        ('Intelligence starts with sand.', '智能，始于沙。'),
        ('Across communication, memory and serving, we make the path from GPU to useful AI more efficient, and we publish the measurements behind every claim.', '从通信、显存到服务调度，我们让 GPU 通往有用 AI 的路径更高效，并公开每一个结论背后的实测数据。'),
        ('Sand', '沙'), ('The raw material behind every chip.', '每一颗芯片的原料。'),
        ('Silicon', '硅'), ('Purified, patterned, made precise.', '提纯、刻蚀，变得精确。'),
        ('Service', '服务'), ('Useful AI, served for less.', '有用的 AI，以更低成本提供。'),
        ('Zenith / material', 'Zenith / 材料'), ('Silicon.', '硅。'), ('Sand, purified and made precise.', '提纯的沙，变得精确。'),
        ('Less waiting. More computing.', '更少等待，更多计算。'),
        ('µs · one-row all-reduce', 'µs · 单行 all-reduce'),
        ('Topology-aware communication reduces overhead on PCIe-connected GPUs. A collective microbenchmark, not an end-to-end speedup.', '拓扑感知的通信降低了 PCIe 互联 GPU 的开销。这是集合通信的微基准测试，不代表端到端加速。'),
        ('Read the research and conditions', '阅读研究与测试条件'),
        ('A million tokens. Still within reach.', '百万 token，依然触手可及。'),
        ('input tokens · three needles retrieved', '输入 token · 三根针全部找回'),
        ('A measured long-context retrieval run. Capacity, communication and latency are evaluated together.', '一次实测的长上下文检索，容量、通信与延迟一起评估。'),
        ('Useful throughput', '有用的吞吐'), ('More output. A usable stream.', '更多输出，依然流畅。'),
        ('output tok/s · 16 B200 GPUs', '输出 tok/s · 16 张 B200'),
        ('Kimi-K3 at concurrency 64: 41 tok/s per user. Corrected wall-clock measurement; broader acceptance pending.', 'Kimi-K3 在 64 并发下，每位用户 41 tok/s。已修正墙钟测量，更大范围验收仍在进行。'),
        ('Agent reliability', 'Agent 可靠性'), ('Correctness is part of performance.', '正确性，也是性能的一部分。'),
        ('empty-argument failures · 1,600 forced calls', '空参数错误 · 1,600 次强制调用'),
        ('Observed failures in this test suite fell to zero after the fix. A measured sample, not a universal zero-error claim.', '修复后，该测试集中观察到的错误降为零。这是实测样本，不代表任何场景都零错误。'),
        ('Research', '研究'), ('Show the work.', '用作品说话。'), ('Systems', '系统'),
        ('Inference, without NVLink.', '没有 NVLink 的推理。'),
        ('On PCIe GPUs, a small collective can matter more than a faster matrix multiply.', '在 PCIe GPU 上，一次小小的集合通信，可能比更快的矩阵乘法更重要。'),
        ('Read the research', '阅读研究'), ('A million tokens.', '百万 token。'),
        ('Capacity, communication and latency, measured together.', '容量、通信与延迟，一起实测。'),
        ('Read', '阅读'), ('Deployment', '部署'), ('The useful frontier.', '有用的边界。'),
        ('Faster batches, only while every user still gets a usable stream.', '更快的批处理，前提是每位用户的输出依然流畅。'),
        ('Beyond HTTP 200.', '不止 HTTP 200。'),
        ('Complete streams, correct tool arguments, faithful protocols.', '完整的流式输出，正确的工具参数，忠实的协议。'),
        ('97 → 0 failures', '97 → 0 次错误'),
        ('Serving', '服务调度'), ('Follow the bytes.', '跟着字节走。'),
        ('A cache hit is not the end of the journey.', '缓存命中，并不是终点。'),
        ('Engineering method', '工程方法'), ('Every iteration leaves', '每一次迭代'), ('better evidence.', '都留下更好的证据。'),
        ('Humans, agents and a shared knowledge base improve the system, and the next experiment.', '人、Agent 与共享知识库一起改进系统，也改进下一次实验。'),
        ('All research', '全部研究'), ('Latest research notes', '最新技术文章'), ('View all', '查看全部'),
        ('Rethinking inference without NVLink', '没有 NVLink 时，重新思考推理'),
        ('Making a million tokens usable', '让百万 token 真正可用'),
        ('Finding the useful throughput frontier', '寻找有用的吞吐边界'),
        ('Correctness beyond a successful response', '正确性，不止于接口返回成功'),
        ('A cache hit is not the end of the journey', '缓存命中，并不是终点'),
        ('Every iteration should leave better evidence', '每一次迭代，都应留下更好的证据'),
        ('What does it mean to get more from every chip?', '从每一块芯片榨出更多，意味着什么？'),
        ('Target, verify, compound', '设定目标、验证、复利'),
        ('Systems · Nov 13, 2026', '系统 · 2026-11-13'), ('Long context · Nov 13, 2026', '长上下文 · 2026-11-13'),
        ('Deployment · Nov 13, 2026', '部署 · 2026-11-13'), ('Agent reliability · Nov 13, 2026', 'Agent 可靠性 · 2026-11-13'),
        ('Serving · Nov 13, 2026', '服务调度 · 2026-11-13'), ('Engineering method · Nov 13, 2026', '工程方法 · 2026-11-13'),
        ('Inference · Framework', '推理 · 方法框架'), ('Method · Framework', '方法 · 方法框架'),
        ('How we work', '我们怎么做'), ('Every iteration leaves a better', '每一次迭代，都留下一个更好的'), ('starting point.', '起点。'),
        ('Define a test', '定义测试'), ('Start from the question and the workload it should serve.', '从问题和它要服务的负载出发。'),
        ('Measure the baseline', '测量基线'), ('Profile topology, memory and latency before tuning anything.', '调优之前，先剖析拓扑、显存与延迟。'),
        ('Challenge the conclusion', '质疑结论'), ('Re-run, cross-check, publish with the conditions.', '重跑、交叉验证，连同条件一起公开。'),
        ('Keep the evidence', '留下证据'), ('What we learn becomes the next starting point.', '学到的东西，成为下一次的起点。'),
        ('commits', '次提交'), ('merged PRs', '个合并 PR'),
        ('October 11 to 20, 2026 repository review. Engineers directed the work and approved production changes.', '2026 年 10 月 11 日至 20 日的代码库回顾。工程师主导工作，并审批生产环境变更。'),
        ('Our mission', '我们的使命'), ('Bring AI within', '让 AI'), ('everyone’s reach.', '触手可及。'),
        ('Talk to us on Telegram', '在 Telegram 联系我们'), ('Skip to content', '跳到正文'),
    ]
    zh = en_home.replace(H1_EN, H1_ZH)
    main_start, main_end = zh.index('<main'), zh.index('</main>')
    mid = zh[main_start:main_end]
    pre_blocks = re.findall(r'<pre>.*?</pre>', mid, flags=re.S)
    for i, b in enumerate(pre_blocks): mid = mid.replace(b, f'@@PRE{i}@@')
    prod = re.search(r'<section class="product" id="product">.*?</section>\n', mid, flags=re.S).group(0)
    mid = mid.replace(prod, '@@PRODUCT@@')
    for en, zt in sorted(TR, key=lambda x: -len(x[0])):
        mid = re.sub(r'(>\s*)' + re.escape(en.replace('’', '&rsquo;') if False else en) + r'(\s*<)', lambda m: m.group(1) + zt + m.group(2), mid)
    mid = mid.replace('@@PRODUCT@@', product_band(ZH))
    for i, b in enumerate(pre_blocks): mid = mid.replace(f'@@PRE{i}@@', b)
    zh = zh[:main_start] + mid + zh[main_end:]
    zh = re.sub(r'<header class="nav" role="banner">.*?</header>', nav(ZH, '/'), zh, flags=re.S)
    zh = re.sub(r'<footer class="footer">.*?</footer>', footer(ZH), zh, flags=re.S)
    zh = zh.replace('<html lang="en">', '<html lang="zh-CN">')
    zh = re.sub(r'<title>[^<]*</title>', '<title>Zenith · 芯华算 · 高效推理</title>', zh)
    zh = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="芯华算 Zenith：用推理工程，让高质量开源模型更便宜、更好用。">', zh)
    zh = zh.replace('>Skip to content<', '>跳到正文<')
    # section internal links that point to English subpages
    zh = zh.replace('href="/blog', 'href="/zh/blog')
    for p in ['/platform/', '/models/', '/docs/', '/news/', '/about/', '/credits/', '/security/']:
        zh = zh.replace(f'href="{p}"', f'href="/zh{p}"')
    (SITE / 'zh').mkdir(exist_ok=True)
    (SITE / 'zh' / 'index.html').write_text(zh)
    left = [m for m in re.findall(r'>\s*([A-Za-z][^<>]{3,})\s*<', zh[zh.index('<main'):zh.index('</main>')]) if not re.search(r'[一-鿿]', m)]
    print('zh home written; untranslated text nodes:', len(left))
    for m in left[:60]: print('  ', m)

    # ---------------------------------------------------------------- blog: contact
    for f in SITE.glob('blog/**/index.html'):
        t = f.read_text()
        t2 = t.replace('mailto:contact@aitist.ai', TG).replace('>Contact ↗<', '>Telegram ↗<')
        if t2 != t: f.write_text(t2)


if __name__ == '__main__':
    main()
