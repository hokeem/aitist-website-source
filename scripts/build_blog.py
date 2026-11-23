#!/usr/bin/env python3
"""Zenith engineering notes, rebuilt from the source reports (Oct 2026 tech share deck, Kimi-K3 tech share,
Kimi-K3 frontier report, RSI workflow deck). Bilingual, figures redrawn as monochrome SVG. No outbound report links."""
import build_pages as B
import blog_figs as F

EN, ZH = B.EN, B.ZH
SITE = B.SITE
AR = B.AR
S = lambda en, zh: (en, zh)  # bilingual pair


def cell(L, c):
    return L.t(*c) if isinstance(c, tuple) else c


def render_blocks(L, blocks):
    out = []
    for b in blocks:
        k = b[0]
        if k == 'h': out.append(f'<h2 id="{b[3]}">{L.t(b[1], b[2])}</h2>' if len(b) > 3 else f'<h2>{L.t(b[1], b[2])}</h2>')
        elif k == 'p': out.append(f'<p>{L.t(b[1], b[2])}</p>')
        elif k == 'ul': out.append('<ul>' + ''.join(f'<li>{L.t(*x)}</li>' for x in b[1]) + '</ul>')
        elif k == 'note': out.append(f'<p class="art-note">{L.t(b[1], b[2])}</p>')
        elif k == 'quote': out.append(f'<blockquote>{L.t(b[1], b[2])}</blockquote>')
        elif k == 'fig':
            svgf, cap, legend = b[1], b[2], (b[3] if len(b) > 3 else None)
            leg = legend(L) if callable(legend) else (legend or '')
            out.append(f'<figure class="art-fig">{svgf(L)}{leg}<figcaption>{L.t(*cap)}</figcaption></figure>')
        elif k == 'tbl':
            hdr, rows = b[1], b[2]
            cap = b[3] if len(b) > 3 else None
            out.append('<div class="art-tbl"><div class="tbl-wrap"><table class="tbl"><thead><tr>' + ''.join(f'<th>{cell(L, h)}</th>' for h in hdr) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{cell(L, c)}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>'
                       + (f'<p class="fine">{L.t(*cap)}</p>' if cap else '') + '</div>')
    return '\n'.join(out)


# ======================================================================= articles
ART = []

# ---------------------------------------------------------------- 1 PCIe
ART.append(dict(
    slug='pcie-inference', cover='/assets/research/cover-0.webp', date='2026-11-13', cat=S('Systems', '系统'),
    title=S('Rethinking inference without NVLink', '没有 NVLink 时，重新思考推理'),
    dek=S('On our RTX 6000D cluster, two GPUs in the same server talk more slowly than two servers do. Every design choice in our stack follows from that one measurement.',
          '在我们的 RTX 6000D 集群上，同一台服务器里的两张卡之间，比两台服务器之间还慢。我们推理栈里的每个设计选择，都是从这一个实测结论推出来的。'),
    kpis=[('40.6 → 5.9', S('µs, one-row all-reduce', 'µs，单行 all-reduce')), ('47%', S('of a prefill chunk was pure communication', '的 prefill 分块时间花在纯通信上')), ('36 → 10.9', S('ms per token, GLM-5.3 single stream', 'ms/token，GLM-5.3 单流'))],
    blocks=[
        ('h', 'A machine that breaks the usual rules', '一套反直觉的机器', 'machine'),
        ('p', 'We serve four frontier MoE models (GLM-5.3, DeepSeek-V4.1-Flash, GLM-5.3-Flash and Qwen3.8-Flash-Next), all with a 1,048,576-token context, on 39 nodes and 312 RTX 6000D GPUs (Blackwell SM120, 84 GiB each). There is no NVLink. Each server holds eight GPUs split across two CPU sockets, and every GPU has its own 400G ConnectX-8 NIC with GPUDirect RDMA. The workload is mostly coding agents: long inputs, tools, many turns, and prefix-cache hit rates of 96–99%.',
              '我们在 39 台节点、312 张 RTX 6000D（Blackwell SM120，每卡 84 GiB）上运行四个前沿 MoE 模型：GLM-5.3、DeepSeek-V4.1-Flash、GLM-5.3-Flash 和 Qwen3.8-Flash-Next，全部支持 1,048,576 token 上下文。集群没有 NVLink。每台服务器 8 张卡，分挂在两个 CPU 插槽下；每张卡各配一块 400G ConnectX-8 网卡，支持 GPUDirect RDMA。负载以编码 agent 为主：长输入、带工具、多轮对话，前缀缓存命中率 96–99%。'),
        ('fig', F.node, S('Fig. 1 · One server. Crossing CPU sockets inside a box is slower than leaving the box through a single 400G NIC.', '图 1 · 一台服务器。机内跨 CPU 插槽，比通过一块 400G 网卡出机还慢。')),
        ('p', 'We measured the whole bandwidth ladder before tuning anything. Memory bandwidth reached about 96% of spec and compute was ample (FP8 259–288 TFLOPS, NVFP4 526–571 TFLOPS). The bottleneck was the PCIe fabric inside each node.',
              '调优之前，我们先把整条带宽阶梯测了一遍。显存带宽达到规格的约 96%，算力也充足（FP8 259–288 TFLOPS，NVFP4 526–571 TFLOPS）。瓶颈在节点内部的 PCIe。'),
        ('fig', lambda L: F.hbars([
            (L.t('GDDR7 memory (one GPU)', '显存 GDDR7（单卡）'), 1340, '≈1,340', False),
            (L.t('Cross-node RDMA, 8 ports', '跨节点 RDMA，8 口合计'), 382, '382', False),
            (L.t('Cross-node RDMA, one 400G port', '跨节点 RDMA，单口 400G'), 47.8, '47.8', False),
            (L.t('Same-socket GPU-to-GPU', '同插槽 GPU 直传'), 37, '37', False),
            (L.t('Across CPU sockets', '跨 CPU 插槽'), 20, '≈20', True),
            (L.t('8-GPU all-reduce bus bandwidth', '8 卡 all-reduce 总线带宽'), 19.5, '19.5', True),
            (L.t('8-GPU all-to-all, per GPU', '8 卡 all-to-all，每卡'), 3, '≈3', True)],
            log=True, vmin=1, vmax=3000, label_w=330, note=L.t('GB/s, log scale. Production-class nodes and research-cluster microbenchmarks, Aug–Oct 21, 2026.', 'GB/s，对数坐标。生产同型节点与研究集群微基准，2026-08 至 10-21。')),
            S('Fig. 2 · The bandwidth ladder. Gold rows are the paths a naive tensor-parallel layout depends on.', '图 2 · 带宽阶梯。金色几行，正是照搬张量并行时最依赖的通信路径。')),
        ('h', 'Where the time went', '时间花在了哪里', 'time'),
        ('p', 'We profiled one 128K-token cold request across all eight tensor-parallel ranks and aligned every collective by call index. Almost half of each prefill chunk was spent moving data, not computing.',
              '我们对一个 128K token 的冷请求，在 8 个张量并行 rank 上做了 GPU profile，并按调用序号对齐每一次集合通信。每个 prefill 分块里，将近一半时间在搬数据，而不是在计算。'),
        ('fig', lambda L: F.stacked([(L.t('Pure communication', '纯通信'), 47, '341 ms', True), (L.t('Compute', '计算'), 37, '266 ms', False),
                                     (L.t('Waiting for slow ranks', '等慢的 rank'), 9, '68 ms', False), (L.t('Idle', '空闲'), 7, '', False)],
                                    note=L.t('One prefill chunk, 8 TP ranks, test instance with the production configuration, Oct 16.', '一个 prefill 分块，8 个 TP rank，生产同配置测试实例，10-16。')),
            S('Fig. 3 · Time inside one prefill chunk.', '图 3 · 一个 prefill 分块内部的时间分布。')),
        ('p', 'That gave us four working rules: <strong>do less communication</strong> (prefer parallelism that needs fewer collectives: pipeline, context and MoE tensor parallelism); <strong>route by message size</strong> (small messages over PCIe IPC, large ones over a tuned NCCL, cross-node over RDMA); <strong>schedule around the KV cache</strong>; and <strong>trust only evidence</strong> (byte-identical A/B, locked clocks, alternating runs, numeric gates).',
              '由此得出四条工作原则：<strong>少做通信</strong>，优先选择集合通信更少的并行方式（流水线、上下文与 MoE 张量并行）；<strong>按消息大小分路</strong>，小消息走 PCIe IPC，大消息走调优后的 NCCL，跨机走 RDMA；<strong>以 KV 为中心调度</strong>；以及<strong>只相信证据</strong>：同字节 A/B、锁频、交替测量、数值门禁。'),
        ('h', 'Small messages should not go through NCCL', '小消息不该交给 NCCL', 'ipc'),
        ('p', 'During decode, each all-reduce carries only a handful of token rows. NCCL pays a fixed cost of roughly 40 µs per call on this hardware, which dominates when the message is tiny. A direct PCIe-IPC all-reduce removes most of that cost, and its advantage grows as the message shrinks.',
              'decode 阶段，每次 all-reduce 只携带寥寥几行 token。在这套硬件上，NCCL 每次调用有约 40 µs 的固定开销，消息越小，这部分占比越大。直接走 PCIe IPC 的 all-reduce 去掉了大部分固定开销，消息越小，优势越大。'),
        ('fig', lambda L: F.grouped(['1', '8', '48', '96', '192'],
                                    [('NCCL', F.GREY, [40.6, 47.3, 106, 186, 350]), ('PCIe-IPC', F.GOLD, [5.9, 14.2, 59.3, 112, 172])],
                                    unit=L.t('µs per all-reduce · token rows per call', 'µs / 次 · 每次 all-reduce 的 token 行数'),
                                    note=L.t('TP8, hidden size 5120, bf16, timed inside CUDA graphs. Test instance with the production configuration, Oct 16.', 'TP8，hidden 5120，bf16，CUDA graph 内计时。生产同配置测试实例，10-16。')),
            S('Fig. 4 · All-reduce latency by message size. At one row: 40.6 → 5.9 µs. This is a collective microbenchmark, not an end-to-end speedup.', '图 4 · 不同消息大小下的 all-reduce 延迟。单行时 40.6 → 5.9 µs。这是集合通信微基准，不代表端到端加速。')),
        ('h', 'Many wins came from fixing defaults', '很多收益来自「把默认配置改对」', 'defaults'),
        ('tbl', [S('Change', '改动'), S('Problem', '问题'), S('Result', '结果')], [
            [S('Force NCCL P2P inside a node', 'NCCL 节点内强制 P2P'), S('By default, 8 GPUs in one node detoured through the NIC', '单节点 8 卡默认绕道网卡'), S('80 MiB all-reduce 7.54 → 6.37 ms; cold 128K first token −6.4%', '80 MiB all-reduce 7.54 → 6.37 ms；冷 128K 首字 −6.4%')],
            [S('Pin the autotune choice', '固定 autotune 组合'), S('Every restart re-rolled kernels; c16 varied 16–20% fast or slow', '每次启动重新抽签，c16 快慢差 16–20%'), S('−19% to −21% per step at each concurrency', '各档每步 −19% ~ −21%')],
            [S('Sparse MLA decode table', '稀疏 MLA decode 参数表'), S('Warm-up used the wrong shape, so the table was never built', '预热形状错误，参数表从未生成'), S('Kernel about −16% (about −2% end to end), outputs bit-identical', 'kernel 约 −16%（端到端约 −2%），输出逐位相同')],
            [S('MXFP8 tactic for small M', 'MXFP8 小 M tactic'), S('Default tactic was chosen for large M', '默认 tactic 按大 M 选择'), S('−18% per step at c1', 'c1 每步 −18%')],
        ], S('Rejected on the record: quantized all-reduce (4.7% error, only 1.02× faster on large messages) and global EP32 (going from 16 to 32 GPUs raised latency from 4.4 to 130 ms).', '记录在案的否决：量化 all-reduce（误差 4.7%，大消息只快 1.02 倍）；全局 EP32（从 16 卡到 32 卡，延迟从 4.4 ms 升到 130 ms）。')),
        ('h', 'What it added up to', '合在一起的效果', 'result'),
        ('p', 'For GLM-5.3, the new generation combines disaggregated prefill and decode, pipeline-parallel prefill, PCIe-IPC, EAGLE speculative decoding and MoE tensor parallelism. In a stress test, single-stream time per token went from about 36 ms to 10.9 ms; on real text the combined gain was about 2–2.7×. These are several changes measured together, so we do not attribute the gain to any single one.',
              'GLM-5.3 的新一代部署组合了 PD 分离、流水线并行 prefill、PCIe-IPC、EAGLE 投机解码和 MoE 张量并行。压测中，单流每 token 耗时从约 36 ms 降到 10.9 ms；在真实文本上，合计收益约 2–2.7 倍。这是多项改动一起测得的结果，我们不把它归功于其中任何单独一项。'),
    ],
    data=[[S('One-row all-reduce', '单行 all-reduce'), '40.6 → 5.9 µs', S('TP8 microbenchmark, Oct 16', 'TP8 微基准，10-16')],
          [S('Prefill chunk communication share', 'prefill 分块通信占比'), '47%', S('128K cold request, 8 ranks', '128K 冷请求，8 个 rank')],
          [S('GLM-5.3 time per token', 'GLM-5.3 每 token 耗时'), '≈36 → 10.9 ms', S('Stress text, Oct 13 vs Oct 18, several changes combined', '压测文本，10-13 vs 10-18，多项合计')]],
))

# ---------------------------------------------------------------- 2 long context
ART.append(dict(
    slug='million-token-context', cover='/assets/research/cover-1.webp', date='2026-11-13', cat=S('Long context', '长上下文'),
    title=S('Making a million tokens usable', '让百万 token 真正可用'),
    dek=S('A million-token context is a capacity, communication and scheduling problem before it is a model feature. We do the KV accounting first, then take each model apart.',
          '百万 token 上下文首先是容量、通信和调度问题，然后才是模型功能。我们先算 KV 账，再逐个模型拆瓶颈。'),
    kpis=[('1,045,368', S('input tokens, three needles retrieved', '输入 token，三根针全部找回')), ('710 → ≈195', S('s, GLM-5.3 cold first token at 1M', 's，GLM-5.3 百万 token 冷启动首字')), ('12.4M', S('token KV pool, Kimi-K3 DCP8', 'token KV 池，Kimi-K3 DCP8'))],
    blocks=[
        ('h', 'Start with the KV bill', '先算 KV 账', 'kv'),
        ('p', 'Every token in context leaves state behind. How much state each model keeps per token decides how many long requests fit on a machine at the same time, and therefore what kind of parallelism we need.',
              '上下文里的每个 token 都会留下状态。每个模型每 token 留多少状态，决定了一台机器能同时容纳几个长请求，也就决定了我们需要什么样的并行方式。'),
        ('tbl', [S('Model', '模型'), S('KV per token', '每 token KV'), S('KV pool (measured)', 'KV 池（实测）'), S('1M cold first token', '1M 冷启动首字'), S('Key measure', '关键措施')], [
            ['GLM-5.3', '≈55 KB', S('1.12M on decode: one 1M request per node at a time', 'decode 112 万：每台同时 1 个 1M'), '194–200 s', S('Pipeline-parallel prefill; decode KV-wait timeout 300 → 1,800 s', 'prefill PP8；decode 等 KV 超时 300 → 1,800 s')],
            ['DeepSeek-V4.1', S('MLA compressed', 'MLA 压缩'), '2.2M', '152–233 s', S('Fixed an indexer out-of-memory; long-request admission and length-aware placement', '修复索引器显存溢出；长请求准入 + 按长度放置')],
            ['GLM-5.3-Flash', '≈31 KB', S('2.415M per replica', '每副本 241.5 万'), '174 s', S('Single-socket TP4 to avoid the cross-socket link', '单插槽 TP4，避开跨插槽链路')],
            ['Qwen3.8', '≈24 KB', '≈1.05M', '811–825 s', S('YaRN ×4; KV pool cap still to be raised (target 600 s)', 'YaRN ×4；KV 池上限待放开（门槛 600 s）')],
        ], S('Needles hidden at the start, middle and end with IDs; every run gets a random prefix so the cache cannot help.', 'needle 藏在开头、中间、结尾并编号；每次加随机开头，确保缓存帮不上忙。')),
        ('p', 'The Qwen row is honest about a gap: its cold first token is still above our 600-second bar, and the fix (raising the KV pool cap) is not done yet.',
              'Qwen 这一行如实标出了差距：它的冷启动首字仍高于我们 600 秒的门槛，修复（放开 KV 池上限）尚未完成。'),
        ('h', 'Why Kimi-K3 is friendly to long context', '为什么 Kimi-K3 对长上下文友好', 'k3'),
        ('p', 'Kimi-K3 mixes two kinds of attention. Only 24 of its 93 layers use MLA, whose KV cache grows with the context. The other 69 use KDA, which keeps a fixed-size state no matter how long the input is. Between pipeline stages, only a few KB of activations per token cross the network.',
              'Kimi-K3 混合了两种注意力。93 层里只有 24 层使用 MLA，其 KV 随上下文增长；另外 69 层使用 KDA，无论输入多长都只保留固定大小的状态。流水线段之间，每个 token 只需跨网络传几 KB 激活。'),
        ('fig', F.layers93, S('Fig. 1 · Kimi-K3 layer types. Long context costs KV on about a quarter of the layers.', '图 1 · Kimi-K3 的层类型。长上下文只在约四分之一的层上产生 KV 开销。')),
        ('p', 'On two H200 servers we enabled decode context parallelism across eight GPUs (DCP8), which splits one request\'s KV into eight shards. The KV pool reached 12.4 million tokens. A 1,045,368-token input retrieved all three needles in 167 seconds. The trade-off: no speculative decoding in this pool, so a single request runs at 61 tok/s.',
              '我们在两台 H200 上开启了 8 卡解码上下文并行（DCP8），把一个请求的 KV 切成 8 份。KV 池达到 1,240 万 token。一次 1,045,368 token 的输入，167 秒内三根针全部取回。代价是这个池里关闭了投机解码，单请求速度为 61 tok/s。'),
        ('fig', lambda L: F.topology(L, L.t('Kimi-K3 · 2×H200 · DCP8 · 1M context', 'Kimi-K3 · 2×H200 · DCP8 · 1M 上下文'),
                                     [('8×H200 (141 GB)', 'h200', L.t('Layers 1–47 (47)', '第 1–47 层（47 层）'), 47), ('8×H200 (141 GB)', 'h200', L.t('Layers 48–93 (46)', '第 48–93 层（46 层）'), 46)], ['RDMA'],
                                     [(L.t('GPUs', '卡'), '16'), (L.t('1M retrieval', '1M 取回'), L.t('1,045,368 tok · 167 s', '1,045,368 token · 167 s')), (L.t('Needles', '针'), '3 / 3'), (L.t('KV pool', 'KV 池'), L.t('12.4M', '1,240 万')), (L.t('Single request', '单请求'), '61 tok/s')]),
            S('Fig. 2 · The long-context pool for Kimi-K3.', '图 2 · Kimi-K3 的长上下文专用池。'), F.topo_legend),
        ('h', 'GLM-5.3: prefill and decode want different shapes', 'GLM-5.3：prefill 与 decode 需要不同的形状', 'glm'),
        ('p', 'For GLM-5.3 we split prefill and decode onto different machines with different parallelism. Prefill runs as an eight-stage pipeline, so each layer\'s all-reduce becomes a point-to-point hand-off between stages. Decode uses tensor parallelism plus context parallelism so a 1M-token KV can be spread over several GPUs. Cold first token at 1M dropped from 710 s to about 195 s (194–200 s across runs), with 8 of 8 needle requests correct.',
              'GLM-5.3 的 prefill 与 decode 被拆到不同机器上，用不同的并行方式。prefill 用 8 段流水线，每层的 all-reduce 变成段与段之间的点对点交接；decode 用张量并行加上下文并行，把 1M token 的 KV 分摊到多张卡上。1M 冷启动首字从 710 s 降到约 195 s（多次测量 194–200 s），8/8 个 needle 请求全部正确。'),
        ('fig', F.pd_arch, S('Fig. 3 · GLM-5.3 production layout.', '图 3 · GLM-5.3 的生产部署结构。')),
        ('p', 'One more lesson from that work: a decode worker that waits for a 1M-token KV transfer needs a long enough timeout. We raised it from 300 to 1,800 seconds; with the old value, the longest requests failed even though everything else was correct.',
              '这次工作还有一个教训：decode 等待一个 1M token 的 KV 传输，需要足够长的超时。我们把它从 300 秒调到 1,800 秒；用旧值时，即使其他一切正确，最长的请求也会失败。'),
    ],
    data=[[S('Kimi-K3 retrieval', 'Kimi-K3 检索'), S('1,045,368 input tokens', '1,045,368 输入 token'), S('Three targets retrieved · 167 s', '三个目标全部取回 · 167 s')],
          [S('GLM-5.3 cold first token', 'GLM-5.3 冷启动首字'), '194–200 s', S('8/8 needle requests correct', '8/8 个 needle 请求正确')],
          [S('Kimi DCP8 KV pool', 'Kimi DCP8 KV 池'), S('12.4M tokens', '1,240 万 token'), S('Capacity, not a single-request length', '容量，不是单请求长度')]],
))

# ---------------------------------------------------------------- 3 throughput frontier
ART.append(dict(
    slug='kimi-deployment-frontier', cover='/assets/research/cover-2.webp', date='2026-11-13', cat=S('Deployment', '部署'),
    title=S('Finding the useful throughput frontier', '寻找有用的吞吐边界'),
    dek=S('A faster batch is useful only while every user still gets an acceptable stream. We measured Kimi-K3 on eleven hardware configurations and drew the line at 40 tok/s per user.',
          '更快的批处理，只有在每位用户的输出依然流畅时才有意义。我们在 11 种硬件配置上实测了 Kimi-K3，把验收线划在每用户 40 tok/s。'),
    kpis=[('1,991', S('tok/s total, 41 tok/s per user, 2×B200', 'tok/s 总吞吐，每用户 41 tok/s，2×B200')), ('496', S('tok/s at the line, recommended 2×H200', 'tok/s 达标吞吐，推荐的 2×H200')), ('34/34', S('official interface tests passed', '官方接口用例全部通过'))],
    blocks=[
        ('h', 'The question', '问题是什么', 'q'),
        ('p', 'Adding concurrency always raises total throughput for a while. But every user sees a slower stream. So we only count throughput while each user still gets at least 40 tokens per second, and compare configurations at that point. Workload: about 7.6K input tokens per request with unique prefixes (no cache hits) and 1,024 output tokens; concurrency 1/4/16/32/64, two rounds each.',
              '并发加上去，总吞吐会涨一段，但每个用户看到的速度都在变慢。所以我们只在每用户仍有至少 40 tok/s 时计算吞吐，并在这一点上比较各方案。负载：每请求约 7.6K 输入 token，前缀各不相同（不命中缓存），输出 1,024 token；并发 1/4/16/32/64，每档跑两轮。'),
        ('h', 'The layouts we ran', '我们跑过的布局', 'layouts'),
        ('p', 'Each box below is one eight-GPU machine with tensor parallelism inside it; arrows are pipeline hand-offs; the strip shows how the 93 layers are split.',
              '下图每个方框是一台机内做张量并行的 8 卡机器，箭头是流水线段之间的交接，底部色条是 93 层在各机器上的分配。'),
        ('fig', lambda L: F.topology(L, L.t('A · Full K3 · 2×H200 · TP8×PP2', 'A · 完整 K3 · 2×H200 · TP8×PP2'),
                                     [('8×H200 (141 GB)', 'h200', L.t('Layers 1–47 (47)', '第 1–47 层（47 层）'), 47), ('8×H200 (141 GB)', 'h200', L.t('Layers 48–93 (46)', '第 48–93 层（46 层）'), 46)], ['RDMA'],
                                     [(L.t('GPUs', '卡'), '16'), (L.t('Single request', '单请求'), '114 tok/s'), (L.t('10K first token', '10K 首字'), '1.02 s'), (L.t('Peak throughput', '峰值吞吐'), '645 @32'), (L.t('KV pool', 'KV 池'), L.t('620K', '62 万')), (L.t('Acceptance', '验收'), '34/34 · 18/18')]),
            S('Fig. 1 · Layout A, the accepted recommendation.', '图 1 · 方案 A，已验收的推荐方案。'), F.topo_legend),
        ('fig', lambda L: F.topology(L, L.t('B · Full K3 · 2×H100 + 2×H200 · TP8×PP4 · split by memory', 'B · 完整 K3 · 2×H100 + 2×H200 · TP8×PP4 · 按显存分层'),
                                     [('8×H100 (80 GB)', 'h100', L.t('Layers 1–18 (18)', '第 1–18 层（18 层）'), 18), ('8×H100 (80 GB)', 'h100', L.t('Layers 19–36 (18)', '第 19–36 层（18 层）'), 18),
                                      ('8×H200 (141 GB)', 'h200', L.t('Layers 37–64 (28)', '第 37–64 层（28 层）'), 28), ('8×H200 (141 GB)', 'h200', L.t('Layers 65–93 (29)', '第 65–93 层（29 层）'), 29)], ['RDMA', 'TCP', 'RDMA'],
                                     [(L.t('GPUs', '卡'), '32'), (L.t('Single request', '单请求'), '104 tok/s'), (L.t('10K first token', '10K 首字'), '1.37 s'), (L.t('Peak throughput', '峰值吞吐'), '874 @64'), (L.t('KV pool', 'KV 池'), L.t('1.74M', '174 万')), (L.t('Acceptance', '验收'), L.t('not run', '未测'))]),
            S('Fig. 2 · Layout B. An even split ran out of memory on the H100 stage; splitting by memory (18/18/28/29) fit.', '图 2 · 方案 B。平均分层时 H100 那段直接显存溢出；按显存比例 18/18/28/29 才放得下。'), F.topo_legend),
        ('fig', lambda L: F.topology(L, L.t('C · Full K3 · 3×RTX 6000D · TP8×PP3', 'C · 完整 K3 · 3×RTX 6000D · TP8×PP3'),
                                     [('8×6000D (84 GB · PCIe)', 'd6000', L.t('Layers 1–32 (32)', '第 1–32 层（32 层）'), 32), ('8×6000D (84 GB · PCIe)', 'd6000', L.t('Layers 33–63 (31)', '第 33–63 层（31 层）'), 31), ('8×6000D (84 GB · PCIe)', 'd6000', L.t('Layers 64–93 (30)', '第 64–93 层（30 层）'), 30)], ['RoCE', 'RoCE'],
                                     [(L.t('GPUs', '卡'), '24'), (L.t('Single request', '单请求'), '49 tok/s'), (L.t('10K first token', '10K 首字'), '2.9 s'), (L.t('Peak throughput', '峰值吞吐'), '82 @8'), (L.t('KV pool', 'KV 池'), L.t('210K', '21 万')), (L.t('Acceptance', '验收'), L.t('not run', '未跑'))]),
            S('Fig. 3 · Layout C on our own RTX 6000D machines. It runs, but MoE goes through Marlin kernels and speculative acceptance is only about 25%. This is the gap we most want to close.', '图 3 · 方案 C，运行在我们自有的 RTX 6000D 上。能跑，但 MoE 走 Marlin，投机解码接受率只有约 25%。这是我们最想解决的问题。'), F.topo_legend),
        ('h', 'Throughput at the line', '达标时的吞吐', 'line'),
        ('fig', lambda L: F.hbars([
            (L.t('2×B200 · EFA · k=2 · fp8 KV', '2×B200 · EFA · k=2 · fp8 KV'), 124.4, '124.4', True),
            (L.t('2×B200 · EFA · k=4 · fp8 KV', '2×B200 · EFA · k=4 · fp8 KV'), 90.1, '90.1', False),
            (L.t('2×H200 · EFA · k=4 (recommended)', '2×H200 · EFA · k=4（推荐）'), 31.0, '31.0', False),
            (L.t('REAP-448 pruned · 1×H200', 'REAP-448 剪枝 · 1×H200'), 29.1, '29.1', False),
            (L.t('2×H100 + 2×H200 · PP4 · TCP', '2×H100 + 2×H200 · PP4 · TCP'), 16.6, '16.6', False),
            (L.t('2×H200 · TCP · k=8', '2×H200 · TCP · k=8'), 14.1, '14.1', False),
            (L.t('2×H200 · DCP8 · 1M context', '2×H200 · DCP8 · 1M 上下文'), 3.6, '3.6', False),
            (L.t('3×RTX 6000D · PP3', '3×RTX 6000D · PP3'), 1.8, '1.8', False)], label_w=330,
            note=L.t('Output tok/s per GPU at the highest concurrency that keeps every user ≥ 40 tok/s.', '在每用户 ≥ 40 tok/s 的最高并发下，每张卡的输出 tok/s。')),
            S('Fig. 4 · Per-GPU throughput at the acceptance line.', '图 4 · 验收线上的每卡吞吐。')),
        ('p', '<strong>Fastest: 2×B200</strong> with tensor parallelism inside each machine, two pipeline stages, EFA networking, DSpark speculative decoding with k=2 and fp8 KV. Single request 177 tok/s with a 0.38 s first token. At 64 concurrent requests each user still gets 41 tok/s and the total is 1,991 tok/s, or 124 per GPU, 4.0× the 2×H200 layout. Peak reached 2,348 tok/s at 96 concurrency (about 34 per user). Correctness checks passed (OCRBench 0.890, MMMU Pro 0.799, tool schema 408/408); full acceptance is still pending.',
              '<strong>最快：2×B200</strong>，机内张量并行、两段流水线、EFA 网络、DSpark 投机解码 k=2、fp8 KV。单请求 177 tok/s，首字 0.38 s。64 并发时每用户仍有 41 tok/s，总吞吐 1,991 tok/s，即每卡 124，是 2×H200 的 4.0 倍。峰值在 96 并发达到 2,348 tok/s（每用户约 34）。正确性检查通过（OCRBench 0.890、MMMU Pro 0.799、工具 schema 408/408），完整验收仍在进行。'),
        ('p', '<strong>Recommended today: 2×H200</strong> with k=4. At 16 concurrency each user gets 40 tok/s and the total is 496 tok/s (31 per GPU), the highest per-GPU number among full-model layouts at the line. It passed all 34 official interface tests, 18 cross-model tests and our team acceptance. To scale, add replicas rather than pipeline stages.',
              '<strong>当前推荐：2×H200</strong>，k=4。16 并发时每用户 40 tok/s，总吞吐 496 tok/s（每卡 31），在所有完整模型方案中，达标时的每卡吞吐最高。它通过了官方 34 项接口用例、跨模型 18 项用例和团队验收。要扩容，加副本，而不是加流水线段。'),
        ('h', 'What the numbers taught us', '数字教会我们的事', 'lessons'),
        ('fig', lambda L: F.before_after([
            (L.t('Cross-node bandwidth', '跨机带宽'), 351, 'RDMA 351 GB/s', 4.8, 'TCP 4.8 GB/s', 380),
            (L.t('Single request', '单请求'), 106, 'RDMA 106 tok/s', 102, 'TCP 102 tok/s', 120),
            (L.t('16 concurrent', '16 并发'), 496, 'RDMA 496 tok/s', 419, 'TCP 419 tok/s', 540)],
            note=L.t('Same 2×H200 layout. A 70× bandwidth gap barely moves single-request speed.', '同样是 2×H200。带宽差 70 倍，单请求速度几乎不变。')),
            S('Fig. 5 · Network affects loading and high concurrency, not single-request speed.', '图 5 · 网络影响的是加载和高并发，不是单请求速度。'),
            lambda L: f'<div class="fig-legend"><span><i style="background:{F.GREY}"></i>RDMA</span><span><i style="background:{F.GOLD}"></i>TCP</span></div>'),
        ('ul', [S('<strong>Speculative decoding is mandatory.</strong> Without it, 63 tok/s; with DSpark, 125 tok/s. On H200, k=4 keeps single-request speed and gives 17% more throughput at 16 concurrency than k=8.', '<strong>投机解码是必开项。</strong>不开 63 tok/s，开 DSpark 125 tok/s。在 H200 上，k=4 单请求不变，16 并发吞吐比 k=8 高 17%。'),
                S('<strong>Throughput peaks around 32 concurrency on 2×H200</strong> (645 tok/s) and falls at 64 (579 tok/s, 20 tok/s per user, 21 s first token). The KV pool is the ceiling.', '<strong>2×H200 的吞吐在 32 并发附近到顶</strong>（645 tok/s），64 并发反降到 579（每用户 20 tok/s，首字 21 s）。KV 池是天花板。'),
                S('<strong>Pruning hurts the long tail.</strong> A community build that removes half the experts (REAP-448) is fast and passes the interface tests, but in scenes that should call a question tool it answered in text about 40% of the time (21 calls out of 36).', '<strong>剪枝伤的是长尾能力。</strong>社区把专家剪掉一半的版本（REAP-448）速度正常、接口用例也通过，但在该调用提问工具的场景里，约 4 成改用文字反问（36 次中只调用 21 次）。'),
                S('<strong>Measure throughput honestly.</strong> Throughput is total output tokens divided by wall-clock time. Earlier internal reports summed per-request speeds and overstated throughput by 2.3–2.5×; every number here was recomputed from raw per-request data.', '<strong>诚实地测吞吐。</strong>吞吐 = 总输出 token ÷ 实际墙钟时间。早期内部报告把各请求速度相加，高估了 2.3–2.5 倍；本文所有数字都从原始逐请求数据重算。')]),
        ('h', 'The cost line', '成本线', 'cost'),
        ('fig', lambda L: F.hbars([
            (L.t('2×B200 · k=2', '2×B200 · k=2'), 17, '$17', True), (L.t('2×B200 · k=4', '2×B200 · k=4'), 23, '$23', False),
            (L.t('2×H200 · EFA · k=4', '2×H200 · EFA · k=4'), 39, '$39', False), (L.t('2×H100 + 2×H200 · PP4', '2×H100 + 2×H200 · PP4'), 53, '$53', False),
            (L.t('2×H200 · TCP · k=8', '2×H200 · TCP · k=8'), 85, '$85', False), (L.t('3×RTX 6000D', '3×RTX 6000D'), 144, '$144', False),
            (L.t('2×H200 · DCP8 · 1M', '2×H200 · DCP8 · 1M'), 336, '$336', False)], log=True, vmin=10, vmax=500, label_w=300,
            note=L.t('Rental cost per million output tokens; 25th-percentile 8-GPU rental quotes, Oct 28. Market median price for this model: about $31.', '每产出 100 万输出 token 的租卡成本；按 10-28 八卡租价的 25 分位计算。该模型的市场中位售价约 $31。')),
            S('Fig. 6 · Cost per million output tokens on this cache-free workload.', '图 6 · 在这个不命中缓存的负载下，每百万输出 token 的成本。')),
        ('p', 'On this workload, 2×B200 costs about $17 per million output tokens, under the roughly $31 market median, so even short chats are profitable. 2×H200 costs $39 and only breaks even at about $3.47 per GPU-hour. Agent traffic with high cache hit rates changes the economics in our favor; that is the traffic we design for.',
              '在这个负载下，2×B200 每百万输出 token 约 $17，低于约 $31 的市场中位价，短对话也能赚钱。2×H200 为 $39，租价要压到约 $3.47/卡时才打平。缓存命中率高的 agent 流量会让这笔账对我们更有利，而这正是我们重点设计的流量。'),
    ],
    data=[[S('2×B200 · k=2', '2×B200 · k=2'), S('1,991 tok/s at 64 concurrency', '64 并发 1,991 tok/s'), S('41 tok/s per user; acceptance pending', '每用户 41 tok/s；验收进行中')],
          [S('2×H200 · k=4', '2×H200 · k=4'), S('496 tok/s at 16 concurrency', '16 并发 496 tok/s'), '34/34 · 18/18'],
          [S('2×H200 · DCP8', '2×H200 · DCP8'), S('1M retrieval passed', '1M 取回通过'), S('KV pool 12.4M tokens', 'KV 池 1,240 万 token')]],
))

# ---------------------------------------------------------------- 4 correctness
ART.append(dict(
    slug='agent-correctness', cover='/assets/research/cover-3.webp', date='2026-11-13', cat=S('Agent reliability', 'Agent 可靠性'),
    title=S('Correctness beyond a successful response', '正确性，不止于接口返回成功'),
    dek=S('An HTTP 200 and valid JSON are not enough. Agent workloads need complete streams, correct tool arguments and faithful protocol behavior, so every fix here comes with a controlled comparison.',
          'HTTP 200 和合法的 JSON 远远不够。agent 负载需要完整的流式输出、正确的工具参数和忠实的协议行为，所以这里的每一项修复都附带对照实验。'),
    kpis=[('4.7% → 0', S('tool-argument leaks in long multi-turn sessions', '长上下文多轮下的工具参数泄漏')), ('97 → 0', S('empty-argument failures, 1,600 forced calls', '空参数错误，1,600 次强制调用')), ('24 → 34', S('of 34 official interface tests after patches', '项官方接口用例（补丁后）'))],
    blocks=[
        ('h', 'The arguments leaked into the arguments', '参数漏进了参数里', 'leak'),
        ('p', 'In long, multi-turn coding sessions, a small fraction of tool calls came back broken: the model wrote its own end-of-argument marker into the argument text. The cause was a worker setting that applied full constrained decoding to every request that carried tools. We reproduced it by replaying real sessions from three clients (Claude Code, Codex and opencode) and changed exactly one switch on the same worker.',
              '在长时间、多轮的编码会话里，一小部分工具调用返回时是坏的：模型把自己的参数结束标记写进了参数文本。原因是 worker 对所有带工具的请求都做了全量约束解码。我们用三个真实客户端（Claude Code、Codex、opencode）回放真实会话复现了问题，并在同一台 worker 上只改一个开关做对照。'),
        ('fig', lambda L: F.before_after([
            (L.t('Tool-argument leaks', '工具参数泄漏'), 4.7, '4.7% (17 / 361)', 0, '0', 6),
            (L.t('Empty-argument failures', '空参数错误'), 97, L.t('97 · JSON-only constraint', '97 · 只约束合法 JSON'), 0, L.t('0 · schema-constrained', '0 · 按参数 schema 约束'), 110)],
            note=L.t('Leaks: same worker, real Claude Code sessions, one setting changed, Oct 15. Failures: BFCL forced calls, 1,600 per arm, Oct 21 canary.', '泄漏：同一台 worker、真实 Claude Code 会话、只改一项，10-15。错误：BFCL 强制调用，每组 1,600 次，10-21 金丝雀。')),
            S('Fig. 1 · Two failure modes, before and after.', '图 1 · 两种失败模式，修复前后对比。'), F.legend_ba),
        ('p', 'After the change, 467 tool calls in our own real sessions produced zero leaks and zero regressions. For forced tool calls (a named function or <code>required</code>), we now constrain decoding to the function\'s argument schema instead of generic JSON; <code>auto</code> is unchanged. Empty-argument failures fell from 97 to 0 and Pass@1 rose from 87.4% to 92.6%.',
              '改动上线后，我方真实会话中的 467 次工具调用，0 泄漏、0 退化。对于强制工具调用（指定函数名或 <code>required</code>），我们改为按该函数的参数 schema 约束解码，而不是只约束成合法 JSON；<code>auto</code> 保持不变。空参数错误从 97 次降到 0，Pass@1 从 87.4% 升到 92.6%。'),
        ('h', 'Guards that stay on', '常驻的保护', 'guards'),
        ('ul', [S('<strong>Degeneration loop guard.</strong> If more than 98% of the last 2,048 tokens are short repeated fragments, generation ends with <code>length</code>. In the canary it truncated 2 of 32 runs.', '<strong>退化循环保护。</strong>最近 2,048 个 token 中有 98% 以上是短片段重复时，以 <code>length</code> 结束生成。金丝雀中截断了 32 次里的 2 次。'),
                S('<strong>Control-token injection guard.</strong> Control-token spellings inside user text are encoded as plain text. End and tool markers take effect only by token ID.', '<strong>控制标记注入防护。</strong>用户正文里出现的控制标记拼写，一律按普通文本编码；结束与工具标记只按 token ID 生效。'),
                S('<strong>A reference oracle.</strong> The same batch of requests is compared token by token against the official open-source reference implementation.', '<strong>参考实现做 oracle。</strong>同一批请求与官方开源参考实现逐 token 比对。')]),
        ('h', 'Protocol details break agents too', '协议细节同样会弄坏 agent', 'protocol'),
        ('p', 'The same round of work fixed four compatibility problems that never showed up as errors on a health check:',
              '同一轮工作还修复了四个从来不会在健康检查里报错的兼容问题：'),
        ('ul', [S('Segmented thinking content sent to the engine as an array failed from the second turn on.', '分段思考内容以数组形式发给引擎，从第二轮起报错。'),
                S('The gateway dropped the thinking-effort field.', '入口丢掉了思考档位字段。'),
                S('Clients that send no output budget now get a default reservation of min(32K, remaining context).', '客户端不传输出预算时，默认预留 min(32K, 剩余上下文)。'),
                S('A hosted search tool that some clients include by default caused requests to be rejected.', '部分客户端默认携带的托管搜索工具会导致请求被拒。')]),
        ('h', 'Seven interface patches for Kimi-K3', '为 Kimi-K3 打的 7 处接口补丁', 'k3'),
        ('tbl', [S('Symptom', '现象'), S('How we measured it', '怎么测出来的'), S('Fix', '改法')], [
            [S('With thinking off and temperature 1.0, about 10% of auto calls skip the tool', '关思考 + 温度 1.0 时，约 10% 不调用工具'), S('60 runs: 54/60 at 1.0 · 59/60 at 0.6 · 60/60 at 0', '60 次：温度 1.0 54/60 · 0.6 59/60 · 0 60/60'), S('Default temperature 0.6 when thinking is off and none is given', '关思考且未指定温度时默认 0.6')],
            [S('Thinking on without an effort often answers in text instead of calling tools', '开思考但未指定档位时，常用文字代替工具调用'), S('36 runs: unspecified 30/36 · high 36/36 (half the tokens)', '36 次：不指定 30/36 · high 36/36（token 还少一半）'), S('Default thinking effort = high', '默认 thinking_effort=high')],
            [S('Named-function tool_choice reports finish_reason stop', '指定函数名的 tool_choice，finish_reason 报 stop'), S('One of the 34 official tests', '官方 34 项之一'), S('Report tool_calls when calls are present', '有 tool_calls 时报 tool_calls')],
            [S('Small output budgets are eaten by thinking, no answer', '小输出预算被思考吃光，没有正文'), S('64-token budget case', '64 token 预算用例'), S('Thinking capped at half the total budget', '思考预算上限 = 总预算一半')],
            [S('OpenAI / Anthropic effort names not recognized', 'OpenAI / Anthropic 的档位名不认'), S('Messages / Responses cases', 'Messages / Responses 用例'), S('Map to the nearest K3 level', '映射到 K3 最近档位')],
            [S('Prompt cache hits not reported', 'prompt 缓存命中数不上报'), S('Cache case', '缓存用例'), S('Enable prompt token details', '启动开启 prompt token 明细')],
            [S('Invalid role returns 200', '非法 role 返回 200'), S('One of 18 cross-model tests', '跨模型 18 项之一'), S('Use the official encoder', '使用官方编码器')],
        ], S('Official interface tests went from 24/34 to 34/34; cross-model tests from 17/18 to 18/18; team acceptance passed four rounds in a row. All patches are in the interface layer; the model is untouched.', '官方 34 项从 24/34 到 34/34，跨模型 18 项从 17/18 到 18/18，团队验收连续 4 轮全过。所有补丁都只在接口层，不改模型。')),
        ('h', 'Thinking effort, and how to call us', '思考档位与调用建议', 'effort'),
        ('tbl', [S('Effort', '档位'), 'AIME 24+25', S('Note', '说明')], [
            [S('50 (before alignment)', '50（对齐官方前）'), '97.9%', '—'], [S('75 (high / xhigh)', '75（high / xhigh）'), '99.6%', S('Default when thinking is on without a level', '开思考但不指定档位时的默认')],
            [S('100 (max)', '100（max）'), '99.6%', S('About 18% more output tokens', '输出 token 多约 18%')]]),
        ('ul', [S('<strong>Give enough output budget.</strong> Reasoning is 76–82% of output; set <code>max_tokens</code> to at least 4K–8K.', '<strong>输出预算给足。</strong>推理 token 占输出的 76–82%，<code>max_tokens</code> 至少 4K–8K。'),
                S('<strong>Read <code>tool_calls</code>.</strong> When a function is named, calls always come back as <code>tool_calls</code>.', '<strong>看 <code>tool_calls</code>。</strong>指定函数时，统一返回 <code>tool_calls</code>。'),
                S('<strong>Stream for agents.</strong> A non-streaming response cut off before a tool block closes can lose completed calls.', '<strong>agent 用流式。</strong>非流式响应若在工具块闭合前被截断，已完成的调用可能丢失。'),
                S('<strong>Retry with Retry-After.</strong> Overload returns a retry hint; honor it.', '<strong>按 Retry-After 重试。</strong>过载时会返回重试提示，请按提示重试。')]),
        ('h', 'Drill failures before designing for them', '先演练故障，再设计底座', 'drills'),
        ('tbl', [S('Drill (before the rework)', '演练（改造前）'), S('What happened', '发生了什么'), S('What we run now', '现在的底座')], [
            [S('2× overload for 5 minutes', '2 倍过载 5 分钟'), S('All 523 requests returned 200; first token 17 → 148 s; health checks stayed green', '523 个请求全部 200；首字 17 → 148 s；健康检查一直是绿的'), S('Concurrency cap at the measured knee; queue cap = first-token SLO − cold prefill', '并发上限取实测拐点；排队上限 = 首字 SLO − 冷 prefill')],
            [S('Kill a worker', 'kill worker'), S('7 streams cut after 200, with no [DONE] and no error', '7 条流在 200 之后截断，没有 [DONE] 也没有 error'), S('Primary/standby gateways; switch after 3 failed checks; actual gap 0.28–0.49 s', '主备入口：3 次检查失败才切，实际空档 0.28–0.49 s')],
            [S('Pause for 60 s', '暂停 60 s'), S('One stream silently stalled for 70 s', '一条流静默卡住 70 s'), S('60 s inter-token timeout; first-token timeout grows with uncached length', 'token 间隔超时 60 s；首 token 超时随未缓存量增长')],
            [S('Client disconnects', '客户端断开'), S('Worker released within 7 s', 'worker 7 s 内释放'), S('Retry once on another node only if no bytes were sent', '只在未发出字节时换一台重试 1 次')],
        ], S('Lesson: HTTP 200 is not a pass. A server must recognize a truncated stream and enforce an inter-token timeout.', '结论：HTTP 200 不等于通过。服务端必须能识别被截断的流，并设置 token 间隔超时。')),
    ],
    data=[[S('Tool-argument leaks', '工具参数泄漏'), '4.7% → 0', S('Real sessions, one setting changed, Oct 15', '真实会话，只改一项，10-15')],
          [S('Empty-argument failures', '空参数错误'), '97 → 0', S('BFCL forced calls, 1,600 per arm', 'BFCL 强制调用，每组 1,600 次')],
          [S('Official interface tests (K3)', '官方接口用例（K3）'), '24/34 → 34/34', S('After seven interface-layer patches', '7 处接口层补丁后')]],
))

# ---------------------------------------------------------------- 5 KV
ART.append(dict(
    slug='kv-aware-serving', cover='/assets/research/cover-4.webp', date='2026-11-13', cat=S('Serving', '服务调度'),
    title=S('A cache hit is not the end of the journey', '缓存命中，并不是终点'),
    dek=S('Our cache hit rate was 98.6%, yet the first token still took 3.6 seconds. Following the bytes showed where the time went, and why a hit-rate dashboard can mislead.',
          '缓存命中率 98.6%，首字却仍要 3.6 秒。跟着字节走，我们找到了时间去了哪里，也明白了为什么命中率看板会误导人。'),
    kpis=[('98.6%', S('cache hit rate, 3.6 s first token', '缓存命中率，首字仍 3.6 s')), ('57%', S('of first-token time was KV transfer', '的首字时间在 KV 传输')), ('35 → 2.5', S('s first-token p50 with admission control', 's 首字 p50（加准入控制后）'))],
    blocks=[
        ('h', 'Split the first token into stages', '把首字时间按环节拆开', 'split'),
        ('p', 'We stitched together per-request logs from four layers (gateway, entry, prefill and decode) for 5,858 requests between October 19 and 21, then attributed the average first-token time to each stage.',
              '我们把网关、入口、prefill、decode 四层日志按请求拼接起来，覆盖 10-19 至 10-21 的 5,858 个请求，再把平均首字时间分摊到各个环节。'),
        ('fig', lambda L: F.stacked([(L.t('Gateway dispatch', '入口分发'), 9, '', False), (L.t('Prefill of the uncached part', '等 prefill 算未命中部分'), 32, '', False),
                                     (L.t('KV transfer, prefill → decode', 'prefill → decode 的 KV 传输'), 57, '', True), (L.t('Other', '其他'), 2, '', False)],
                                    note=L.t('Share of mean first-token time, 5,858 requests, Oct 19–21.', '占首字均值的比例，5,858 个请求，10-19 至 10-21。')),
            S('Fig. 1 · More than half of the first token was spent moving KV that decode already could have had.', '图 1 · 一半以上的首字时间，花在搬运本可以复用的 KV 上。')),
        ('p', 'The transfer volume did not depend on the hit rate at all. It was a straight line in input length.',
              '传输量与命中率毫无关系，它只是输入长度的一条直线。'),
        ('fig', F.line_fit, S('Fig. 2 · Bytes sent per request scale with the whole input, hit or miss.', '图 2 · 每个请求发送的字节数随整段输入增长，与是否命中无关。')),
        ('p', 'Two causes. First, prefix reuse was not enabled on the decode side, so prefill always sent KV from token zero. Second, the gateway applied session affinity only to prefill (99.4% of turns returned to the same prefill node) while only 6.7% of decode turns returned to the same decode node. A third finding was about reading metrics: a "connect 1.6 s" field was really time spent waiting for prefill to finish; the handshake itself took tens of milliseconds.',
              '原因有两个。第一，decode 侧没有开启前缀复用，prefill 永远从第 0 个 token 开始发送 KV。第二，入口只对 prefill 做了会话亲和（99.4% 的轮次回到同一台 prefill），decode 只有 6.7% 回到同一台。第三个发现与读指标有关：日志里「建连 1.6 s」其实是在等 prefill 算完，握手本身只有几十毫秒。'),
        ('h', 'Route to where the KV already is', '把请求送到 KV 所在的地方', 'route'),
        ('fig', F.affinity, S('Fig. 3 · The second turn contains the whole first turn. Sending it back to the same machine reuses the KV and computes only what is new.', '图 3 · 第二轮的输入包含第一轮的全部内容。回到同一台机器，就能复用已算好的 KV，只算新增部分。')),
        ('p', 'For GLM, consistent hashing sends a session back to the same prefill node, which raised the prefix hit from 0.64 to 0.98. For GLM-5.3-Flash, routing by prefix to the same replica gives near-100% affinity. Hit rates today: GLM 97–99%, DeepSeek about 96%.',
              '对 GLM，一致性哈希让同一会话回到同一台 prefill，前缀命中率从 0.64 升到 0.98。对 GLM-5.3-Flash，按前缀发往同一副本，亲和度接近 100%。目前命中率：GLM 97–99%，DeepSeek 约 96%。'),
        ('h', 'Say no when the system is full', '系统满了，就要敢拒绝', 'admit'),
        ('fig', lambda L: F.before_after([
            (L.t('First token p50', '首字 p50'), 35, L.t('35 s · no admission control', '35 s · 无准入'), 2.5, L.t('2.5 s · with admission control', '2.5 s · 有准入'), 75),
            (L.t('First token p99', '首字 p99'), 68, L.t('68 s', '68 s'), 4.2, L.t('4.2 s', '4.2 s'), 75)],
            note=L.t('Two independent drills on a standby instance, Oct 18 and 19.', '备用实例上两次独立演练，10-18 与 10-19。')),
            S('Fig. 4 · Admission control trades a few fast rejections for a usable first token for everyone else.', '图 4 · 准入控制用少量快速拒绝，换来其他所有人可用的首字时间。'),
            lambda L: f'<div class="fig-legend"><span><i style="background:{F.GREY}"></i>{L.t("Without admission control", "无准入控制")}</span><span><i style="background:{F.GOLD}"></i>{L.t("With admission control", "有准入控制")}</span></div>'),
        ('h', 'Read a hit, don\'t recompute it', '命中就读，不要重算', 'tiers'),
        ('fig', lambda L: F.hbars([
            (L.t('Local memory (same NUMA side)', '本机内存（本侧 NUMA）'), 0.14, '0.07–0.14 s', False),
            (L.t('Another machine\'s memory (RDMA)', '别的机器的内存（RDMA）'), 0.15, '0.02–0.15 s', True),
            (L.t('Local NVMe', '本地 NVMe'), 1.0, '≈1.0 s', False),
            (L.t('Shared storage', '共享存储'), 1.9, '≈1.9 s', False),
            (L.t('Recompute (prefill again)', '重新 prefill'), 14, '≈7–14 s', False)], log=True, vmin=0.01, vmax=30, label_w=330,
            note=L.t('Projected from bandwidth measured Oct 21; the recompute row is an order-of-magnitude estimate.', '按 10-21 实测带宽推算；重算一行为量级估计。')),
            S('Fig. 5 · KV storage tiers, reordered by measured bandwidth.', '图 5 · 按实测带宽重排的 KV 存储层级。')),
        ('ul', [S('Another machine\'s memory over RDMA is about 7× faster than local NVMe and as fast as local memory. Across the cluster, about 39 TB of memory can act as one shared KV pool.', '别的机器的内存经 RDMA 读取，比本机 NVMe 快约 7 倍，和本机内存一样快。全集群约 39 TB 内存，可以当作一个共享 KV 池。'),
                S('Writes to host memory must stay on the local NUMA side: split writes from 8 GPUs reach 144 GB/s; writing everything to one side drops to 46 GB/s.', '写主机内存必须写本侧 NUMA：8 卡分侧写 144 GB/s，全写一侧只剩 46 GB/s。'),
                S('One GPU sending to many machines does not add bandwidth. To go faster, use more GPUs and more NICs at once.', '一张卡往多台机器发，总量不会涨；要快，只能多卡、多网口一起发。')]),
        ('h', 'Next', '下一步', 'next'),
        ('tbl', [S('Direction', '方向'), S('Measured basis', '依据（实测）'), S('Expected (projected)', '预期（推算）')], [
            [S('Send only missing KV', '只传缺失的 KV'), S('57% of first token is KV transfer; full KV sent at 98.6% hit', '首字 57% 在 KV 传输；命中 98.6% 仍传全量'), S('First-token median 3.6 → about 1.2–1.4 s', '首字中位数 3.6 → 约 1.2–1.4 s')],
            [S('Decode KV residency and release', 'decode KV 驻留与释放'), S('At 90% KV occupancy only about half is generating', 'KV 占用 90% 时只有约一半在生成'), S('+23% to +42% throughput ceiling on the same machines', '同样机器吞吐上限 +23% ~ +42%')],
            [S('Entry overhead', '入口开销'), S('Already-cached context still costs about 8 ms per 1K tokens', '已命中的上下文每千 token 仍要约 8 ms'), S('Lower long-context first token', '长上下文首字再降一截')],
        ], S('Projections are estimates, not results. Every change goes through an idle-machine canary, benchmark and approval first.', '推算值是估计，不是结果。所有改动都先经过空闲机金丝雀、基准测试与审批。')),
    ],
    data=[[S('First-token breakdown', '首字拆解'), S('57% KV transfer', '57% 在 KV 传输'), S('5,858 requests, Oct 19–21', '5,858 个请求，10-19 至 10-21')],
          [S('Transfer volume', '传输量'), '0.4175 MB × input', 'R² = 1.0000'],
          [S('Admission control', '准入控制'), S('p50 35 → 2.5 s · p99 68 → 4.2 s', 'p50 35 → 2.5 s · p99 68 → 4.2 s'), S('Standby drills, Oct 18–19', '备用实例演练，10-18 至 10-19')]],
))

# ---------------------------------------------------------------- 6 evidence
ART.append(dict(
    slug='evidence-driven-engineering', cover='/assets/research/cover-5.webp', date='2026-11-13', cat=S('Engineering method', '工程方法'),
    title=S('Every iteration should leave better evidence', '每一次迭代，都应留下更好的证据'),
    dek=S('Recursive self-improvement, the way we mean it: not a model changing its own weights, but a team of people, agents and a shared knowledge base that gets better at getting better.',
          '我们所说的「递归自我改进」：不是模型自己改自己的权重，而是一支由人、agent 和共享知识库组成的团队，在「如何改进」这件事上越做越好。'),
    kpis=[('227', S('commits across two repos, Oct 11–20', '次提交，两个仓库，10-11 至 10-20')), ('64%', S('co-authored by agents (168 of 227)', '由 agent 共同署名（227 次中 168 次）')), ('36', S('merged PRs, every change reviewed', '个合并 PR，每个改动都经评审'))],
    blocks=[
        ('h', 'What improves', '被改进的是什么', 'what'),
        ('p', 'Four engineers set the direction and approve every production change. Agents dig, measure, write things down and correct each other. Every lesson goes back into the repository as an SOP, a rule in AGENTS.md, a test case or a measuring tool. The next agent reads those first, so it starts where the last round ended. The recursion is that the process itself, including the rulers, thresholds and rules, is one of the things being improved.',
              '四位工程师确定方向，并审批每一项生产变更；agent 负责深挖、测量、写记录，并相互纠错。每一轮的教训都写回仓库：SOP、AGENTS.md 里的规矩、测试样例、测量工具。下一个 agent 进仓库先读这些，于是从上一轮的终点出发。递归之处在于：被改进的对象也包括改进流程本身，比如量尺、门槛和规矩。'),
        ('tbl', [S('Layer that improves', '被改进的层'), S('Example', '例子')], [
            [S('Code and configuration', '代码与配置'), S('18 gateway versions in 4 days; 15 worker patch sets', '入口 4 天 18 个版本；worker 补丁目录 15 个')],
            [S('Rulers', '量尺'), S('A 4–9% noisy metric replaced by one at 0.8–2.4%', '噪声 4–9% 的指标换成 0.8–2.4%')],
            [S('Process', '流程'), S('A six-stage SOP; canary plus shadow gateway', 'SOP 六阶段；金丝雀 + 影子入口')],
            [S('Rules', '规矩'), S('Nine hard rules in AGENTS.md, each with the incident behind it', 'AGENTS.md 9 条硬规矩，每条写明出过什么事')]]),
        ('h', 'The rhythm is visible in the history', '节奏写在提交历史里', 'rhythm'),
        ('fig', F.commits, S('Fig. 1 · Commits per day. Peaks land on days that needed an answer the same day: on Oct 14 the DeepSeek gateway changed 8 times; on Oct 17 twelve sub-threads ran in parallel; on Oct 18 the reliability base went from design to production.', '图 1 · 每日提交数。高峰都落在需要当天定论的日子：10-14 DeepSeek 入口一天换 8 个版本；10-17 十二条子线并行；10-18 可靠性底座从设计到上线。')),
        ('h', 'One loop, six steps', '一轮循环，六个步骤', 'loop'),
        ('fig', F.loop6, S('Fig. 2 · Every round reads from the knowledge base and writes back to it.', '图 2 · 每一轮都从知识库读取，再写回知识库。')),
        ('ul', [S('<strong>Define the problem:</strong> a replayable input, the wrong output before the fix and a pass condition. Without all three, work does not start.', '<strong>定义问题：</strong>可复跑的输入、修复前的错误输出、通过条件，三样齐了才开始。'),
                S('<strong>Freeze the ruler:</strong> the same request bytes, the same machine, and A/A noise measured first.', '<strong>冻结量尺：</strong>同一批请求字节、同一台机器，先测 A/A 噪声。'),
                S('<strong>Cross-check:</strong> a sub-agent\'s conclusion counts only after we verify it against raw data.', '<strong>交叉复核：</strong>子 agent 的结论，要我方用原始数据核过才算数。'),
                S('<strong>Canary rollout:</strong> the standby machine runs the full suite first; then node by node, with the rollback command written before anyone touches production.', '<strong>金丝雀上线：</strong>备用机先跑全套，再逐台替换；回退命令在动手前就写好。')]),
        ('h', 'The ruler improves too', '量尺本身也在迭代', 'ruler'),
        ('fig', F.ranges, S('Fig. 3 · The old metric averaged in the partially filled tail of each batch. Measuring only full-batch steady state cut repeat noise to 0.8–2.4%, below the 2% decision threshold.', '图 3 · 旧指标把未满批的尾部也算进平均值。只取满批的稳态步长后，重复测量噪声降到 0.8–2.4%，低于 2% 的判定门槛。')),
        ('p', 'The same day we added quality gates (gsm8k, math500, BFCL and a 512K needle test) with paired McNemar tests. After that, every "x% faster" had to clear this ruler first.',
              '同一天还加上了质量门禁：gsm8k、math500、BFCL 与 512K needle，并做配对 McNemar 检验。此后每一个「快了 x%」，都必须先过这把尺子。'),
        ('h', 'Sub-agents are wrong sometimes', '子 agent 也会错', 'wrong'),
        ('tbl', [S('Original claim', '原来的说法'), S('Overturned by', '谁推翻的'), S('Evidence', '依据'), S('Outcome', '结论')], [
            [S('Bounded replay is off', 'bounded replay 没开'), S('Our own check', '我方核实'), S('Already on in the production launch args', '生产启动参数里已经开着'), S('A batch of upstream fixes became applicable', '一批上游修复变成适用')],
            [S('NCCL without in-node network: decode unchanged', 'NCCL 关节点内网络：decode 不变'), S('Same-machine recheck', '同机复核'), S('Alternated 4 times: c8 decode 3.3–4.0% slower', '同机交替 4 次：c8 decode 慢 3.3–4.0%'), S('Not in the default config', '不进默认配置')],
            [S('EP4 regresses 9% at c16', 'EP4 在 c16 回归 9%'), S('ABABA restarts', 'ABABA 五次重启'), S('Mostly that one machine was about 6% slower', '主要是那台机器本身慢约 6%'), S('EP4 adopted', '采纳 EP4')],
            [S('Cross-machine noise floor is 2%', '跨机噪声底 2%'), S('ABABA restarts', 'ABABA 五次重启'), S('A restart alone on one machine drifts 3–4%', '同机仅重启就漂 3–4%'), S('Threshold raised', '判定门槛上调')]],
            S('Our verified conclusion beats a sub-agent\'s summary. Cross-machine conclusions only count after a same-machine recheck.', '我方核实的结论优先于子 agent 的总结；跨机结论一律要同机复核才算数。')),
        ('h', 'Vetoed as often as adopted', '被否决的和被采纳的一样多', 'veto'),
        ('tbl', [S('Decision', '决定'), S('Data', '数据')], [
            [S('Vetoed: DeepSeek PD disaggregation', '否决：DeepSeek 做 PD 分离'), S('3P+1D had 17% less throughput than 4 aggregated nodes', '3P+1D 比 4 台不分离吞吐低 17%')],
            [S('Vetoed: prefill compute overlap', '否决：prefill 计算重叠'), S('+0.52%, under the 3% bar', '+0.52%，未达 3% 门槛')],
            [S('Vetoed: KV pool raised to 6M', '否决：KV 池放大到 6M'), S('First revisit took 40% longer', '首轮回访反而多 40% 耗时')],
            [S('Adopted: GLM prefill chunk 2048', '采纳：GLM prefill chunk 2048'), S('Cold-start p99 157 s → 57 s', '冷启动 p99 157 s → 57 s')],
            [S('Adopted: MXFP8 tactic by M', '采纳：MXFP8 按 M 选 tactic'), S('c1 time per token −18%, outputs bit-identical', 'c1 TPOT −18%，输出逐位一致')],
            [S('Adopted: short requests avoid long prefills', '采纳：短请求避开长 prefill'), S('4K-token p90 12 s → 0.58 s', '4K 请求 p90 12 s → 0.58 s')]],
            S('Elegance here means that every design choice that remains beat its alternatives, by more than the noise.', '所谓优雅，是指留下来的每一个设计选择都赢过了其他候选，而且赢的幅度大于噪声。')),
        ('h', 'Honest limits', '还没做好的', 'limits'),
        ('ul', [S('The loop is still pushed by people: engineers decide which threads to open and close.', '循环仍靠人推动：哪条线该开、该停，目前由工程师判断。'),
                S('Changes between teams are not yet announced in one place; two incidents came from unannounced bulk replacements.', '团队之间的变更还没有统一通报；两次故障都来自不打招呼的整批更换。'),
                S('Non-determinism is not solved: with the same config, greedy output can diverge after a few dozen tokens across restarts.', '非确定性没有根治：同配置跨重启，greedy 输出会在几十个 token 后分叉。'),
                S('Some conclusions hold only at today\'s scale, such as "no PD for DeepSeek" at four machines.', '部分结论只在当前规模成立，比如「DeepSeek 不做 PD」只在 4 台机器时成立。')]),
        ('p', 'Next: run the ruler, the gates and the rollback automatically on every commit, so the loop depends less on people remembering.',
              '下一步：把「量尺 + 门禁 + 回滚」做成每次提交都自动运行的流水线，让循环少依赖人记得。'),
    ],
    data=[[S('Commits', '提交'), '227', S('Knowledge base 117 · ops 110, Oct 11–20', '知识库 117 · 运维 110，10-11 至 10-20')],
          [S('Agent co-authored', 'agent 共同署名'), '168 / 227 (64%)', S('Repository history', '仓库历史')],
          [S('Metric noise', '指标噪声'), '4–9% → 0.8–2.4%', S('Decision threshold 2%', '判定门槛 2%')]],
))

# ---------------------------------------------------------------- 7, 8 method frameworks
ART.append(dict(
    slug='inference-efficiency', cover='/assets/tiles/wafer.webp', date='2026-11-13', cat=S('Inference · framework', '推理 · 方法框架'),
    title=S('What does it mean to get more from every chip?', '从每一块芯片榨出更多，意味着什么？'),
    dek=S('A framework for measuring inference efficiency across latency, throughput and cost per completed task.', '一个衡量推理效率的框架：同时看延迟、吞吐与每个完成任务的成本。'),
    kpis=[],
    blocks=[
        ('h', '01 · Start with the workload', '01 · 从负载出发', 'w'),
        ('p', 'The unit of comparison is a workload. Fix the model, the request mix and the quality requirements before comparing configurations. Record the hardware, concurrency, prompt length and output length so a result can be read in context.', '比较的单位是负载。比较配置之前，先固定模型、请求组合与质量要求。记录硬件、并发、输入长度与输出长度，让每个结果都能在上下文中被正确解读。'),
        ('h', '02 · Measure the service', '02 · 测量服务本身', 's'),
        ('p', 'Track time to first token and time per output token alongside throughput, and report tail latency at the target load. A higher token rate is useful only while requests still finish within the service\'s latency budget.', '在看吞吐的同时，追踪首 token 时间与每个输出 token 的时间，并报告目标负载下的长尾延迟。只有当请求仍能在服务的延迟预算内完成时，更高的 token 速率才有意义。'),
        ('h', '03 · Count completed work', '03 · 只数完成的工作', 'c'),
        ('p', 'Cost per completed task brings compute, retries and quality into one account. For a fixed workload, divide serving cost by the number of requests that meet both the quality and the latency criteria.', '每个完成任务的成本，把算力、重试与质量放进同一本账。对固定负载，用服务成本除以同时满足质量与延迟要求的请求数。'),
        ('h', '04 · Keep the evidence', '04 · 留下证据', 'e'),
        ('p', 'Record the baseline, the candidate, the test conditions and any regressions. Repeat the comparison before promoting a candidate, and use the accepted configuration as the baseline for the next round.', '记录基线、候选、测试条件与任何回归。在推广候选之前重复比较一次，并把被采纳的配置作为下一轮的基线。'),
    ], data=[]))
ART.append(dict(
    slug='target-verify-compound', cover='/assets/tiles/hands.webp', date='2026-11-13', cat=S('Method · framework', '方法 · 方法框架'),
    title=S('Target, verify, compound', '设定目标、验证、复利'),
    dek=S('How a measurable objective becomes a repeatable loop for systems improvement.', '一个可衡量的目标，如何变成可重复的系统改进循环。'),
    kpis=[],
    blocks=[
        ('h', '01 · Define the target', '01 · 定义目标', 't'),
        ('p', 'Write down the workload and the metric before proposing changes. Set the constraints that protect correctness, latency and service behavior.', '提出改动之前，先写下负载与指标，并设定保护正确性、延迟与服务行为的约束。'),
        ('h', '02 · Verify independently', '02 · 独立验证', 'v'),
        ('p', 'Run the candidate and the baseline under comparable conditions. Repeat measurements where variance could change the conclusion, and keep the configuration and test inputs with the result.', '在可比条件下运行候选与基线。方差可能改变结论时就重复测量，并把配置与测试输入和结果一起保存。'),
        ('h', '03 · Promote and repeat', '03 · 推广并重复', 'p'),
        ('p', 'Promote candidates that satisfy the constraints and improve the target. Keep a rollback path, and use the newly verified baseline for the next experiment.', '推广满足约束且改进了目标的候选；保留回退路径，并以新验证的基线开始下一次实验。'),
    ], data=[]))


# ======================================================================= pages
def article_page(L, a, idx):
    prev_a = ART[idx - 1] if idx > 0 else None
    next_a = ART[idx + 1] if idx + 1 < len(ART) else None
    kp = ''.join(f'<div><b>{v}</b><span>{L.t(*d)}</span></div>' for v, d in a['kpis'])
    toc = ''.join(f'<a href="#{b[3]}">{L.t(b[1], b[2])}</a>' for b in a['blocks'] if b[0] == 'h' and len(b) > 3)
    data = ''
    if a['data']:
        rows = ''.join('<tr>' + ''.join(f'<td>{cell(L, c)}</td>' for c in r) + '</tr>' for r in a['data'])
        data = f'''<section class="art-data"><h2 id="data">{L.t('Data &amp; sources', '数据与来源')}</h2>
<div class="tbl-wrap"><table class="tbl"><thead><tr><th>{L.t('Test', '测试')}</th><th>{L.t('Observed result', '观测结果')}</th><th>{L.t('Scope', '范围')}</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="fine">{L.t('October 2026 engineering measurements on the stated hardware and workload. They are not a cross-model ranking or a service-level guarantee.', '2026 年 10 月在文中所述硬件与负载下的工程实测，不构成跨模型排名，也不是服务等级承诺。')}</p></section>'''
    nav_links = ''
    if prev_a: nav_links += f'<a class="art-pn" href="{L.u("/blog/" + prev_a["slug"] + "/")}"><small>{L.t("Previous", "上一篇")}</small>{L.t(*prev_a["title"])}</a>'
    else: nav_links += '<span></span>'
    if next_a: nav_links += f'<a class="art-pn next" href="{L.u("/blog/" + next_a["slug"] + "/")}"><small>{L.t("Next", "下一篇")}</small>{L.t(*next_a["title"])}</a>'
    body = f'''<article class="art">
  <header class="art-hero wrap">
    <a class="art-back" href="{L.u('/blog/')}">← {L.t('All engineering notes', '全部技术文章')}</a>
    <p class="label">{L.t(*a['cat'])} · {a['date']}</p>
    <h1>{L.t(*a['title'])}</h1>
    <p class="art-dek">{L.t(*a['dek'])}</p>
    {f'<div class="art-kpis">{kp}</div>' if kp else ''}
  </header>
  <div class="art-cover wrap"><img src="{a['cover']}" alt="" decoding="async"></div>
  <div class="art-layout wrap">
    <aside class="art-toc">{('<p class="label">' + L.t('On this page', '本页内容') + '</p>' + toc + (f'<a href="#data">{L.t("Data &amp; sources", "数据与来源")}</a>' if a['data'] else '')) if toc else ''}</aside>
    <div class="art-body">
{render_blocks(L, a['blocks'])}
{data}
      <div class="art-cta"><p>{L.t('This work runs underneath Zenith Tokens.', '这些工程都运行在 Zenith Tokens 之下。')}</p><a class="btn btn-light btn-sm" href="{B.SIGNUP}">{L.t('Try Zenith Tokens', '试用 Zenith Tokens')} {AR}</a></div>
      <nav class="art-nav">{nav_links}</nav>
    </div>
  </div>
</article>'''
    B.write(L, f'/blog/{a["slug"]}/', L.t(*a['title']), L.t(*a['dek'])[:150], body)


def index_page(L):
    main_ = [a for a in ART if a['kpis']]
    rest = [a for a in ART if not a['kpis']]
    feat = main_[0]
    cards = ''.join(f'''<a class="note-card reveal" href="{L.u('/blog/' + a['slug'] + '/')}"><div class="note-media"><img src="{a['cover']}" alt="" loading="lazy"></div>
<div class="note-body"><p class="label">{L.t(*a['cat'])} · {a['date']}</p><h3>{L.t(*a['title'])}</h3><p>{L.t(*a['dek'])}</p><div class="note-kpi"><b>{a['kpis'][0][0]}</b><span>{L.t(*a['kpis'][0][1])}</span></div></div></a>''' for a in main_[1:])
    small = ''.join(f'<a class="news-row reveal" href="{L.u("/blog/" + a["slug"] + "/")}"><time>{a["date"]}</time><div><p class="tag">{L.t(*a["cat"])}</p><h3 style="margin-top:10px">{L.t(*a["title"])}</h3><p>{L.t(*a["dek"])}</p></div><span class="more" style="color:var(--fg-2)">{AR}</span></a>' for a in rest)
    body = B.hero(L.t('Engineering', '技术博客'), L.t('Show the work. <em>With the numbers.</em>', '用作品说话，<em>带着数字。</em>'),
                  L.t('How we make open models fast, correct and affordable to serve: methods, measurements and the conditions behind every claim.', '我们如何让开源模型推理更快、更正确、更便宜：方法、实测数据，以及每个结论背后的条件。'),
                  f'<a class="btn btn-light" href="{L.u("/blog/" + feat["slug"] + "/")}">{L.t("Start with the hardware", "从硬件读起")} {AR}</a><a class="btn btn-ghost" href="{B.SIGNUP}">{L.t("Try Zenith Tokens", "试用 Zenith Tokens")}</a>') + f'''
<section class="sec"><div class="wrap">
  <a class="note-feature reveal" href="{L.u('/blog/' + feat['slug'] + '/')}"><div class="note-media"><img src="{feat['cover']}" alt=""></div><div class="note-body"><p class="label">{L.t(*feat['cat'])} · {feat['date']}</p><h2>{L.t(*feat['title'])}</h2><p>{L.t(*feat['dek'])}</p><div class="note-kpis">{''.join(f'<div><b>{v}</b><span>{L.t(*d)}</span></div>' for v, d in feat['kpis'])}</div></div></a>
  <div class="note-grid">{cards}</div>
</div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><p class="label reveal">{L.t('Method', '方法')}</p><h2 class="display-sm reveal">{L.t('Frameworks we use', '我们使用的方法框架')}</h2></div></div><div class="news-list">{small}</div></div></section>'''
    B.write(L, '/blog/', L.t('Engineering', '技术博客'), L.t('Zenith engineering notes on efficient inference.', 'Zenith 关于高效推理的技术文章。'), body)


if __name__ == '__main__':
    for L in (EN, ZH):
        for i, a in enumerate(ART): article_page(L, a, i)
        index_page(L)
