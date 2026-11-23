"""SVG figure kit for Zenith engineering notes. Monochrome on black, gold only for the highlighted value."""
import math

FG, MUTED, FAINT, GRID, GOLD, GREY, DIM = '#f3f1ec', '#a9a59c', '#6f6c66', 'rgba(243,241,236,.10)', '#c9a86a', '#55524c', '#2a2926'


def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def svg(w, h, body, label=''):
    return f'<svg class="fig-svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def t(x, y, s, size=14, fill=MUTED, anchor='start', weight=400, extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{esc(s)}</text>'


def hbars(items, unit='', log=False, vmin=1, vmax=None, w=960, label_w=300, row=44, note=None, label=''):
    """items: (label, value, display, highlight)"""
    vmax = vmax or max(v for _, v, _, _ in items) * 1.08
    x0, x1 = label_w, w - 110
    def X(v):
        if log: return x0 + (math.log10(max(v, vmin)) - math.log10(vmin)) / (math.log10(vmax) - math.log10(vmin)) * (x1 - x0)
        return x0 + v / vmax * (x1 - x0)
    h = 30 + row * len(items) + (34 if note else 10)
    g = []
    if log:
        k = math.floor(math.log10(vmin))
        while 10 ** k <= vmax:
            if 10 ** k >= vmin:
                xx = X(10 ** k); g.append(f'<line x1="{xx:.1f}" y1="18" x2="{xx:.1f}" y2="{h - (30 if note else 6)}" stroke="{GRID}"/>' + t(xx, 14, f'{10 ** k:,g}', 11, FAINT, 'middle'))
            k += 1
    for i, (lab, v, disp, hi) in enumerate(items):
        y = 30 + i * row
        g.append(t(x0 - 16, y + 20, lab, 14.5, FG if hi else MUTED, 'end'))
        g.append(f'<rect x="{x0}" y="{y + 6}" width="{max(2, X(v) - x0):.1f}" height="{row - 18}" rx="3" fill="{GOLD if hi else FG}" opacity="{1 if hi else .82}"/>')
        g.append(t(X(v) + 10, y + 20, disp, 14, GOLD if hi else FG, weight=500))
    if note: g.append(t(x0, h - 8, note, 12, FAINT))
    return svg(w, h, ''.join(g), label)


def grouped(cats, series, unit='', w=960, h=360, note=None, label=''):
    """cats: list of labels; series: list of (name, color, values)"""
    left, right, top, bot = 70, 30, 40, 70
    vmax = max(max(v) for _, _, v in series) * 1.12
    cw = (w - left - right) / len(cats)
    bw = cw * 0.32
    g = []
    for k in range(5):
        val = vmax * k / 4; y = h - bot - (h - top - bot) * k / 4
        g.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{GRID}"/>' + t(left - 10, y + 4, f'{val:,.0f}', 11, FAINT, 'end'))
    for i, c in enumerate(cats):
        cx = left + cw * i + cw / 2
        for j, (name, col, vals) in enumerate(series):
            v = vals[i]; bh = (h - top - bot) * v / vmax
            x = cx - bw - 4 + j * (bw + 8)
            g.append(f'<rect x="{x:.1f}" y="{h - bot - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{col}"/>')
            g.append(t(x + bw / 2, h - bot - bh - 8, f'{v:g}', 12.5, col if col != GREY else MUTED, 'middle', 500))
        g.append(t(cx, h - bot + 22, c, 13, MUTED, 'middle'))
    lx = left
    for name, col, _ in series:
        g.append(f'<rect x="{lx}" y="12" width="12" height="12" rx="2" fill="{col}"/>' + t(lx + 18, 22, name, 13, FG)); lx += 30 + len(name) * 8
    if unit: g.append(t(w - right, 22, unit, 12, FAINT, 'end'))
    if note: g.append(t(left, h - 14, note, 12, FAINT))
    return svg(w, h, ''.join(g), label)


def stacked(parts, w=960, note=None, title=None, label=''):
    """parts: (label, pct, sub, highlight)"""
    h = 150 + (24 if note else 0)
    x0, x1, y = 20, w - 20, 50
    g = [t(x0, 26, title, 14, FG, weight=500)] if title else []
    x = x0
    for lab, pct, sub, hi in parts:
        ww = (x1 - x0) * pct / 100
        g.append(f'<rect x="{x + 1:.1f}" y="{y}" width="{ww - 2:.1f}" height="46" rx="4" fill="{GOLD if hi else (FG if pct > 25 else GREY)}" opacity="{1 if hi else .85}"/>')
        if ww > 60: g.append(t(x + ww / 2, y + 29, f'{pct:g}%', 16, '#0a0a0a' if (hi or pct > 25) else FG, 'middle', 600))
        g.append(t(x + 2, y + 72, lab, 13, FG if hi else MUTED))
        if sub: g.append(t(x + 2, y + 90, sub, 12, FAINT))
        x += ww
    if note: g.append(t(x0, h - 6, note, 12, FAINT))
    return svg(w, h, ''.join(g), label)


def before_after(rows, w=960, note=None, label=''):
    """rows: (label, before_val, before_disp, after_val, after_disp, max)"""
    h = 40 + 96 * len(rows) + (26 if note else 0)
    x0, x1 = 230, w - 120
    g = [t(x0, 22, '', 12)]
    for i, (lab, b, bd, a, ad, vmax) in enumerate(rows):
        y = 36 + i * 96
        g.append(t(20, y + 30, lab, 14.5, FG, weight=500))
        g.append(t(x0 - 12, y + 18, '—', 1))
        g.append(f'<rect x="{x0}" y="{y + 4}" width="{max(2, (x1 - x0) * b / vmax):.1f}" height="26" rx="3" fill="{GREY}"/>' + t(x0 + (x1 - x0) * b / vmax + 10, y + 23, bd, 14, MUTED, weight=500))
        g.append(f'<rect x="{x0}" y="{y + 40}" width="{max(3, (x1 - x0) * a / vmax):.1f}" height="26" rx="3" fill="{GOLD}"/>' + t(x0 + max(3, (x1 - x0) * a / vmax) + 10, y + 59, ad, 14, GOLD, weight=600))
    if note: g.append(t(20, h - 8, note, 12, FAINT))
    return svg(w, h, ''.join(g), label)


def legend_ba(L):
    return (f'<div class="fig-legend"><span><i style="background:{GREY}"></i>{L.t("Before", "修复前")}</span>'
            f'<span><i style="background:{GOLD}"></i>{L.t("After", "修复后")}</span></div>')


def topology(L, title, machines, links, stats, w=1000):
    """machines: (label, kind, layers_text, layer_count); kind in h200/h100/d6000; links: list of ('RDMA'|'TCP'|'RoCE') between machines"""
    n = len(machines)
    gap = 54
    mw = (w - 40 - gap * (n - 1)) / n
    g = [t(20, 26, title, 15, FG, weight=600)]
    total = sum(m[3] for m in machines)
    fills = {'h200': FG, 'h100': GREY, 'd6000': 'none'}
    for i, (lab, kind, ltxt, cnt) in enumerate(machines):
        x = 20 + i * (mw + gap); y = 44
        g.append(f'<rect x="{x:.1f}" y="{y}" width="{mw:.1f}" height="168" rx="12" fill="rgba(243,241,236,.03)" stroke="rgba(243,241,236,.22)"/>')
        g.append(t(x + mw / 2, y + 28, lab, 13.5, FG, 'middle', 500))
        s, sp = 22, 7
        gx = x + mw / 2 - (4 * s + 3 * sp) / 2
        for r in range(2):
            for c in range(4):
                fx, fy = gx + c * (s + sp), y + 46 + r * (s + sp)
                if kind == 'd6000':
                    g.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{s}" height="{s}" rx="4" fill="none" stroke="{FG}" stroke-width="1.6"/>')
                else:
                    g.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{s}" height="{s}" rx="4" fill="{fills[kind]}"/>')
        g.append(t(x + mw / 2, y + 134, ltxt, 12.5, MUTED, 'middle'))
        if i < n - 1:
            ax0, ax1, ay = x + mw + 6, x + mw + gap - 6, y + 84
            kindl = links[i]
            dash = ' stroke-dasharray="5 4"' if kindl == 'TCP' else ''
            g.append(f'<line x1="{ax0:.1f}" y1="{ay}" x2="{ax1 - 8:.1f}" y2="{ay}" stroke="{GOLD if kindl != "TCP" else MUTED}" stroke-width="2"{dash}/>'
                     f'<path d="M{ax1 - 9:.1f} {ay - 5} L{ax1:.1f} {ay} L{ax1 - 9:.1f} {ay + 5}Z" fill="{GOLD if kindl != "TCP" else MUTED}"/>')
            g.append(t((ax0 + ax1) / 2, ay - 10, kindl, 11.5, GOLD if kindl != 'TCP' else MUTED, 'middle', 600))
    # layer strip
    x = 20; y = 230
    for i, (lab, kind, ltxt, cnt) in enumerate(machines):
        ww = (w - 40) * cnt / total
        col = FG if kind == 'h200' else (GREY if kind == 'h100' else '#8c8880')
        g.append(f'<rect x="{x + 1:.1f}" y="{y}" width="{ww - 2:.1f}" height="22" rx="3" fill="{col}" opacity=".9"/>')
        g.append(t(x + ww / 2, y + 16, ltxt.split('（')[0].split(' (')[0].replace('第 ', '').replace(' 层', '').replace('Layers ', ''), 11.5, '#0a0a0a' if kind != 'h100' else FG, 'middle', 600))
        x += ww
    # stats
    sy = 272; sw = (w - 40 - 10 * (len(stats) - 1)) / len(stats)
    for i, (k, v) in enumerate(stats):
        sx = 20 + i * (sw + 10)
        g.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw:.1f}" height="58" rx="8" fill="rgba(243,241,236,.05)"/>')
        g.append(t(sx + 12, sy + 20, k, 11.5, FAINT))
        g.append(t(sx + 12, sy + 44, v, 15, GOLD if i == 1 else FG, weight=600))
    return svg(w, 346, ''.join(g), title)


def topo_legend(L):
    return (f'<div class="fig-legend"><span><i style="background:{FG}"></i>H200 · 141 GB</span><span><i style="background:{GREY}"></i>H100 · 80 GB</span>'
            f'<span><i style="background:none;border:1.5px solid {FG}"></i>RTX 6000D · 84 GB · PCIe</span>'
            f'<span><i style="background:{GOLD};height:2px;border-radius:0"></i>RDMA / RoCE</span><span><i style="background:none;border-top:2px dashed {MUTED};height:0;border-radius:0"></i>TCP</span></div>')


def node(L, w=1000):
    """One RTX 6000D server: two CPU sockets, four GPUs each, a 400G NIC per GPU."""
    g = [t(20, 26, L.t('One server · 8 × RTX 6000D · no NVLink', '一台服务器 · 8 × RTX 6000D · 无 NVLink'), 15, FG, weight=600)]
    for sidx in range(2):
        x = 20 + sidx * 490; y = 50
        g.append(f'<rect x="{x}" y="{y}" width="470" height="250" rx="14" fill="rgba(243,241,236,.03)" stroke="rgba(243,241,236,.22)"/>')
        g.append(t(x + 20, y + 30, L.t(f'CPU socket {sidx} · PCIe switch', f'CPU 插槽 {sidx} · PCIe 交换'), 13.5, MUTED))
        g.append(t(x + 450, y + 30, L.t('≈37 GB/s in-socket', '插槽内 ≈37 GB/s'), 12.5, FAINT, 'end'))
        for k in range(4):
            gx = x + 26 + k * 110
            g.append(f'<rect x="{gx}" y="{y + 56}" width="90" height="70" rx="10" fill="{FG}"/>' + t(gx + 45, y + 97, f'GPU{sidx * 4 + k}', 14, '#0a0a0a', 'middle', 600))
            g.append(f'<line x1="{gx + 45}" y1="{y + 126}" x2="{gx + 45}" y2="{y + 176}" stroke="{GOLD}" stroke-width="2"/>')
            g.append(f'<rect x="{gx + 10}" y="{y + 176}" width="70" height="40" rx="8" fill="none" stroke="{GOLD}" stroke-width="1.5"/>' + t(gx + 45, y + 201, '400G', 13, GOLD, 'middle', 600))
    g.append(f'<line x1="490" y1="140" x2="510" y2="140" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4 3"/>')
    g.append(t(500, 330, L.t('Cross-socket ≈20 GB/s, slower than one 400G NIC (47.8 GB/s)', '跨插槽 ≈20 GB/s，比单块 400G 网卡（47.8 GB/s）还慢'), 13, FG, 'middle', 500))
    return svg(w, 346, ''.join(g), 'node')


def layers93(L, w=1000):
    """Kimi-K3: 24 MLA layers with growing KV, 69 KDA layers with fixed state (exact positions not drawn)."""
    g = [t(20, 26, L.t('Kimi-K3 · 93 layers', 'Kimi-K3 · 93 层'), 15, FG, weight=600)]
    cw = (w - 40) / 93
    for i in range(93):
        mla = i % 4 == 3 and i < 93 - 1 or False
        g.append('')
    mla_idx = set(round(i * 93 / 24) + 2 for i in range(24))
    for i in range(93):
        hi = i in mla_idx
        g.append(f'<rect x="{20 + i * cw + .5:.1f}" y="44" width="{cw - 1.2:.1f}" height="{58 if hi else 34}" rx="1.5" fill="{GOLD if hi else GREY}" {"" if hi else ""}/>')
    g.append(f'<rect x="20" y="130" width="14" height="14" rx="2" fill="{GOLD}"/>' + t(42, 142, L.t('24 MLA layers: KV cache grows with context length', '24 层 MLA：KV 随上下文长度增长'), 13.5, FG))
    g.append(f'<rect x="520" y="130" width="14" height="14" rx="2" fill="{GREY}"/>' + t(542, 142, L.t('69 KDA layers: fixed-size state', '69 层 KDA：固定大小的状态'), 13.5, FG))
    g.append(t(20, 172, L.t('Layer order is schematic. Only about a quarter of the layers pay a per-token KV cost.', '层的排列为示意。只有约四分之一的层需要为每个 token 付 KV 的代价。'), 12, FAINT))
    return svg(w, 184, ''.join(g), 'layers')


def pd_arch(L, w=1000):
    g = [t(20, 26, L.t('GLM-5.3 · heterogeneous PD disaggregation · 112 GPUs', 'GLM-5.3 · 异构 PD 分离 · 112 张卡'), 15, FG, weight=600)]
    g.append(f'<rect x="20" y="70" width="150" height="150" rx="12" fill="none" stroke="rgba(243,241,236,.3)"/>' + t(95, 135, L.t('Gateway', '入口'), 15, FG, 'middle', 600) + t(95, 160, L.t('session affinity', '会话亲和'), 12, MUTED, 'middle') + t(95, 178, L.t('admission', '准入控制'), 12, MUTED, 'middle'))
    # prefill
    g.append(f'<rect x="230" y="50" width="330" height="190" rx="12" fill="rgba(243,241,236,.03)" stroke="rgba(243,241,236,.22)"/>')
    g.append(t(250, 78, L.t('Prefill × 8 nodes · PP8', 'prefill × 8 台 · 流水线 PP8'), 14, FG, weight=600))
    for k in range(8):
        g.append(f'<rect x="{250 + k * 37}" y="98" width="30" height="30" rx="5" fill="{FG}"/>')
    g.append(t(250, 156, L.t('78 layers cut into 8 stages, one per GPU', '78 层切 8 段，一张卡一段'), 12.5, MUTED))
    g.append(t(250, 178, L.t('per-layer all-reduce becomes stage-to-stage P2P', '每层 all-reduce 变成段间点对点'), 12.5, MUTED))
    # decode
    g.append(f'<rect x="680" y="50" width="300" height="190" rx="12" fill="rgba(243,241,236,.03)" stroke="rgba(243,241,236,.22)"/>')
    g.append(t(700, 78, L.t('Decode × 6 nodes', 'decode × 6 台'), 14, FG, weight=600))
    for k in range(6):
        g.append(f'<rect x="{700 + k * 44}" y="98" width="36" height="30" rx="5" fill="none" stroke="{FG}" stroke-width="1.6"/>')
    g.append(t(700, 156, 'TP8 + DCP4 + MoE-TP8', 12.5, MUTED))
    g.append(t(700, 178, L.t('EAGLE speculative decoding · fp8 KV', 'EAGLE 投机解码 · KV fp8'), 12.5, MUTED))
    for (x0, x1, lab, col) in [(170, 230, '', MUTED), (560, 680, L.t('KV over 8 × 400G RDMA', 'KV 经 8 条 400G RDMA'), GOLD)]:
        g.append(f'<line x1="{x0 + 4}" y1="145" x2="{x1 - 10}" y2="145" stroke="{col}" stroke-width="2"/><path d="M{x1 - 11} 140 L{x1 - 2} 145 L{x1 - 11} 150Z" fill="{col}"/>')
        if lab: g.append(t((x0 + x1) / 2 + 2, 166, lab.split(' ', 1)[0] if False else lab, 10.5, col, 'middle', 600))
    g.append(t(20, 272, L.t('Production deployment, Oct 18: 8 prefill + 6 decode nodes. Weights NVFP4, KV fp8, KV transfer via Mooncake.', '生产部署（10-18）：8 台 prefill + 6 台 decode。权重 NVFP4，KV fp8，KV 传输使用 Mooncake。'), 12, FAINT))
    return svg(w, 284, ''.join(g), 'pd')


def affinity(L, w=1000):
    g = [t(20, 26, L.t('Cache-affinity routing', '缓存亲和路由'), 15, FG, weight=600)]
    g.append(f'<rect x="20" y="60" width="200" height="54" rx="10" fill="none" stroke="rgba(243,241,236,.3)"/>' + t(120, 92, L.t('Session A · turn 1', '会话 A · 第 1 轮'), 13.5, FG, 'middle'))
    g.append(f'<rect x="20" y="150" width="200" height="54" rx="10" fill="none" stroke="{GOLD}"/>' + t(120, 182, L.t('Session A · turn 2', '会话 A · 第 2 轮'), 13.5, GOLD, 'middle', 600))
    g.append(f'<rect x="330" y="95" width="200" height="74" rx="10" fill="rgba(243,241,236,.05)" stroke="rgba(243,241,236,.3)"/>' + t(430, 127, L.t('Gateway', '入口'), 14, FG, 'middle', 600) + t(430, 150, L.t('hash by session', '按会话哈希选机器'), 12, MUTED, 'middle'))
    g.append(f'<rect x="660" y="55" width="320" height="74" rx="10" fill="{FG}"/>' + t(820, 86, L.t('Machine 1 · holds A\'s KV', '机器 1：有 A 的 KV'), 14, '#0a0a0a', 'middle', 600) + t(820, 109, L.t('turn 2 computes only the new part', '第 2 轮只算新增部分'), 12, '#3a3833', 'middle'))
    g.append(f'<rect x="660" y="150" width="320" height="74" rx="10" fill="none" stroke="rgba(243,241,236,.22)" stroke-dasharray="5 4"/>' + t(820, 181, L.t('Machine 2', '机器 2'), 14, MUTED, 'middle', 600) + t(820, 204, L.t('would recompute from scratch', '去这里就要从头算'), 12, FAINT, 'middle'))
    for (x0, y0, x1, y1, col, dash) in [(220, 87, 330, 120, MUTED, ''), (220, 177, 330, 145, GOLD, ''), (530, 125, 660, 92, GOLD, ''), (530, 140, 660, 187, FAINT, ' stroke-dasharray="5 4"')]:
        g.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{col}" stroke-width="2"{dash}/>')
    return svg(w, 244, ''.join(g), 'affinity')


def line_fit(L, w=1000, h=330):
    left, right, top, bot = 80, 30, 30, 60
    xmax, ymax = 1_000_000, 0.4175 * 1_000_000 / 1000 * 1.05  # input tokens -> MB (0.4175 MB per 1K? keep linear)
    g = [t(20, 22, L.t('KV bytes sent from prefill to decode vs. input length', 'prefill 发往 decode 的 KV 量 vs 输入长度'), 14, FG, weight=600)]
    for k in range(5):
        y = h - bot - (h - top - bot) * k / 4
        g.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{GRID}"/>')
    pts = [(left + (w - left - right) * i / 20, h - bot - (h - top - bot) * i / 20) for i in range(21)]
    g.append('<polyline fill="none" stroke="#c9a86a" stroke-width="2.5" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '"/>')
    import random
    random.seed(4)
    for i in range(60):
        f = random.random(); x = left + (w - left - right) * f; y = h - bot - (h - top - bot) * f
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{FG}" opacity=".75"/>')
    g.append(t(left, h - bot + 24, L.t('input length →', '输入长度 →'), 12.5, MUTED) + t(left - 12, top + 10, 'MB', 12.5, MUTED, 'end'))
    g.append(t(w - right, top + 30, L.t('transfer = 0.4175 MB × input length · R² = 1.0000', '传输量 = 0.4175 MB × 输入长度 · R² = 1.0000'), 14, GOLD, 'end', 600))
    g.append(t(w - right, top + 52, L.t('Same at 98.6% cache hit: the full KV is still sent.', '缓存命中 98.6% 时依然传全量。'), 12.5, MUTED, 'end'))
    g.append(t(left, h - 12, L.t('Points are illustrative of the fit; the relationship is from 5,858 logged requests.', '散点为示意，关系式来自 5,858 个请求的日志拟合。'), 11.5, FAINT))
    return svg(w, h, ''.join(g), 'fit')


def ranges(L, w=1000):
    g = [t(20, 24, L.t('Repeat-measurement spread of the decode step metric', '同一配置重复测量的离散度（decode 每步耗时）'), 14, FG, weight=600)]
    x0, x1 = 280, w - 60
    X = lambda v: x0 + v / 10 * (x1 - x0)
    for k in range(0, 11, 2):
        g.append(f'<line x1="{X(k):.1f}" y1="44" x2="{X(k):.1f}" y2="160" stroke="{GRID}"/>' + t(X(k), 178, f'{k}%', 11.5, FAINT, 'middle'))
    for i, (lab, a, b, col) in enumerate([(L.t('Old: step_ms', '旧指标 step_ms'), 4, 9, GREY), (L.t('New: steady_step_ms', '新指标 steady_step_ms'), .8, 2.4, GOLD)]):
        y = 64 + i * 50
        g.append(t(x0 - 16, y + 18, lab, 14, FG, 'end'))
        g.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="26" rx="13" fill="{col}"/>' + t(X(b) + 10, y + 18, f'{a:g}–{b:g}%', 13.5, col if col == GOLD else MUTED, weight=600))
    g.append(f'<line x1="{X(2):.1f}" y1="44" x2="{X(2):.1f}" y2="160" stroke="{FG}" stroke-width="1.5" stroke-dasharray="4 3"/>' + t(X(2) + 6, 54, L.t('decision threshold 2%', '判定门槛 2%'), 12, FG))
    return svg(w, 190, ''.join(g), 'ranges')


def commits(L, w=1000, h=320):
    days = ['10-11', '10-12', '10-13', '10-14', '10-15', '10-16', '10-17', '10-18', '10-19', '10-20']
    kb = [4, 7, 13, 22, 6, 12, 6, 31, 12, 4]
    ops = [0, 0, 23, 21, 5, 14, 33, 14, 0, 0]
    left, right, top, bot = 50, 20, 44, 50
    vmax = 50
    cw = (w - left - right) / len(days); bw = cw * .56
    g = [f'<rect x="{left}" y="12" width="12" height="12" rx="2" fill="{FG}"/>' + t(left + 18, 22, L.t('Knowledge-base repo (117)', '知识库仓库（117）'), 13, FG),
         f'<rect x="{left + 230}" y="12" width="12" height="12" rx="2" fill="{GOLD}"/>' + t(left + 248, 22, L.t('Ops repo (110)', '运维仓库（110）'), 13, FG)]
    for k in range(0, 51, 10):
        y = h - bot - (h - top - bot) * k / vmax
        g.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{GRID}"/>' + t(left - 8, y + 4, str(k), 11, FAINT, 'end'))
    for i, d in enumerate(days):
        x = left + cw * i + (cw - bw) / 2
        h1 = (h - top - bot) * kb[i] / vmax; h2 = (h - top - bot) * ops[i] / vmax
        g.append(f'<rect x="{x:.1f}" y="{h - bot - h1:.1f}" width="{bw:.1f}" height="{h1:.1f}" fill="{FG}" opacity=".85"/>')
        g.append(f'<rect x="{x:.1f}" y="{h - bot - h1 - h2:.1f}" width="{bw:.1f}" height="{h2:.1f}" fill="{GOLD}"/>')
        g.append(t(x + bw / 2, h - bot - h1 - h2 - 8, str(kb[i] + ops[i]), 12, FG, 'middle', 500))
        g.append(t(x + bw / 2, h - bot + 20, d, 12, MUTED, 'middle'))
    return svg(w, h, ''.join(g), 'commits')


def loop6(L, w=1000, h=420):
    steps = [(L.t('Define the problem', '定义问题'), L.t('replayable input + pass bar', '可复跑输入 + 通过条件')),
             (L.t('Dig in parallel', '并行深挖'), L.t('several sub-threads at once', '多条子线同时查')),
             (L.t('Freeze the ruler', '冻结量尺'), L.t('same bytes · same box · A/A noise', '同字节 · 同机 · A/A 噪声')),
             (L.t('Cross-check', '交叉复核'), L.t('our own verification wins', '我方核实优先')),
             (L.t('Canary rollout', '金丝雀上线'), L.t('node by node · reversible', '逐台滚动 · 可回退')),
             (L.t('Write the rule', '写成规矩'), L.t('SOP · AGENTS.md', 'SOP · AGENTS.md'))]
    cx, cy, R = w / 2, h / 2 + 4, 150
    g = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="rgba(243,241,236,.18)" stroke-dasharray="3 5"/>',
         f'<circle cx="{cx}" cy="{cy}" r="74" fill="rgba(201,168,106,.08)" stroke="{GOLD}"/>',
         t(cx, cy - 4, L.t('Knowledge base', '知识库'), 15, GOLD, 'middle', 600), t(cx, cy + 18, L.t('rules & rulers', '规矩与量尺'), 12, MUTED, 'middle')]
    for i, (a, b) in enumerate(steps):
        ang = -math.pi / 2 + i * 2 * math.pi / 6
        x, y = cx + R * math.cos(ang) * 1.9, cy + R * math.sin(ang) * 1.05
        g.append(f'<rect x="{x - 110:.1f}" y="{y - 30:.1f}" width="220" height="60" rx="12" fill="#121211" stroke="rgba(243,241,236,.25)"/>')
        g.append(t(x - 96, y - 6, f'0{i + 1}', 11.5, GOLD, weight=600) + t(x - 70, y - 6, a, 14, FG, weight=600) + t(x - 96, y + 16, b, 11.5, MUTED))
    return svg(w, h, ''.join(g), 'loop')
