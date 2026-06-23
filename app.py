<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BPM Team Project Management Dashboard</title>
<style>
  :root{
    --bg1:#f1f2f9; --bg2:#f6f7fc; --bg3:#faf9fd;
    --ink:#2b2447; --ink2:#615a7d; --ink3:#938cae;
    --card:#ffffff; --card2:#f7f7fc;
    --navy:#2b2447; --purple:#8b7ef0; --purple-soft:#ece8fd;
    --coral:#f4845f; --coral-soft:#fde6dd; --coral-ink:#c9532e;
    --blue:#3B9BE8; --blue-soft:#dbeeff;
    --orange:#f97316; --orange-soft:#ffedd5;
    --mint:#57c4a3; --mint-soft:#dcf3eb;
    --red:#e8607a; --red-soft:#fbe1e7; --red-ink:#c23a55;
    --grey:#b9bccd; --grey-soft:#eceef5;
    --line:#ecedf4;
    --shadow:0 18px 40px -22px rgba(43,36,71,.35), 0 2px 6px -2px rgba(43,36,71,.06);
    --shadow-soft:0 10px 24px -16px rgba(43,36,71,.30);
    --r:22px; --r-sm:14px;
    --font:"Inter",system-ui,-apple-system,"Segoe UI","PingFang TC","Microsoft JhengHei","Noto Sans TC",sans-serif;
  }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{
    font-family:var(--font); color:var(--ink);
    background:
      radial-gradient(1200px 600px at 12% -8%, #f6f2fd 0%, transparent 55%),
      radial-gradient(900px 500px at 105% 0%, #eef4fd 0%, transparent 50%),
      linear-gradient(160deg,var(--bg1),var(--bg2) 45%,var(--bg3));
    min-height:100vh; padding:26px clamp(14px,3vw,40px) 60px;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:1280px;margin:0 auto}
  .topbar{display:flex;align-items:center;gap:18px;justify-content:space-between;
    background:linear-gradient(135deg,#ffffff,#f6f5fd);border-radius:var(--r);padding:18px 24px;
    box-shadow:var(--shadow);margin-bottom:22px;flex-wrap:wrap}
  .brand{display:flex;align-items:center;gap:14px}
  .brand h1{font-size:19px;margin:0;letter-spacing:.2px}
  .topmeta{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .chip{display:inline-flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);
    color:var(--ink2);font-size:12.5px;padding:8px 13px;border-radius:999px;box-shadow:var(--shadow-soft)}
  .chip b{color:var(--ink);font-weight:700}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 4px var(--mint-soft)}
  .sec-h{display:flex;align-items:baseline;gap:10px;margin:26px 4px 13px}
  .sec-h h2{font-size:16px;margin:0;letter-spacing:.2px}
  .sec-h span{font-size:12.5px;color:var(--ink3)}
  .grid{display:grid;gap:18px}
  .charts{grid-template-columns:repeat(4,1fr);align-items:stretch}
  .two{grid-template-columns:1fr 1fr}
  @media(max-width:980px){.kpis{grid-template-columns:repeat(2,1fr)}.charts{grid-template-columns:1fr}.two{grid-template-columns:1fr}.charts .card[style*="span"]{grid-column:span 1}}
  @media(max-width:560px){.charts{grid-template-columns:1fr}}
  .card{background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);padding:20px 22px}
  .card-donut{display:flex;flex-direction:column}
  .card-h{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
  .card-h h3{font-size:14.5px;margin:0}
  .card-h .hint{font-size:11.5px;color:var(--ink3)}
  .kpi{position:relative;overflow:hidden;background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);padding:18px 20px}
  .kpi .ico{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;margin-bottom:14px}
  .kpi .ico svg{width:19px;height:19px}
  .kpi .num{font-size:38px;font-weight:800;line-height:1;letter-spacing:-.5px}
  .kpi .lbl{font-size:13px;color:var(--ink2);margin-top:7px;font-weight:600}
  .kpi .sub{font-size:11.5px;color:var(--ink3);margin-top:3px}
  .kpi.alert{background:linear-gradient(160deg,#fff,var(--red-soft))}
  .kpi.warn{background:linear-gradient(160deg,#fff,var(--coral-soft))}
  .i-navy{background:var(--purple-soft);color:var(--purple)}
  .i-blue{background:var(--orange-soft);color:var(--orange)}
  .i-mint{background:var(--mint-soft);color:var(--mint)}
  .i-coral{background:var(--coral-soft);color:var(--coral-ink)}
  .i-red{background:var(--red-soft);color:var(--red-ink)}
  .donut-wrap{display:flex;flex-direction:row;align-items:stretch;gap:0;flex:1}
  .donut-area{flex:2;display:flex;align-items:center;justify-content:center;padding:8px}
  .donut{position:relative;width:100%;aspect-ratio:1;max-width:280px}
  .donut svg{width:100%;height:100%;display:block}
  .donut .center{position:absolute;inset:0;display:grid;place-content:center;text-align:center}
  .donut .center b{font-size:clamp(24px,4.5vw,42px);font-weight:800;letter-spacing:-.5px}
  .donut .center small{display:block;font-size:clamp(12px,1.2vw,14px);color:var(--ink3);margin-top:2px}
  .legend{display:flex;flex-direction:column;gap:10px;flex:1;justify-content:center}
  .legend .row{display:flex;align-items:center;gap:6px;font-size:12px}
  .legend .sw{width:10px;height:10px;border-radius:3px;flex:none}
  .legend .row .v{font-weight:700;color:var(--ink);margin-left:4px}
  .bars{display:flex;flex-direction:column;gap:13px;margin-top:4px}
  .bar-row .top{display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:6px}
  .bar-row .top .name{color:var(--ink2);font-weight:600}
  .bar-row .top .val{color:var(--ink);font-weight:700}
  .bar-tip-wrap{position:relative}
  .bar-tip{position:absolute;top:-30px;left:50%;transform:translateX(-50%);background:var(--navy);color:#fff;font-size:11px;padding:4px 10px;border-radius:6px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:10}
  .bar-tip-wrap:hover .bar-tip{opacity:1}
  .fixed-table{width:100%;border-collapse:collapse;table-layout:fixed}
  .fixed-table th{font-size:11.5px;color:var(--ink3);text-align:left;font-weight:600;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:middle;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .fixed-table td{font-size:13px;padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:middle;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .fixed-table tr:last-child td{border-bottom:none}
  .col-w1{width:20%}.col-w2{width:20%}.col-w3{width:14%}.col-w4{width:18%}.col-w5{width:18%}.col-w6{width:10%}
  .track{height:13px;border-radius:999px;background:var(--grey-soft);overflow:hidden;display:flex}
  .track > span{height:100%;display:block}
  .track.bare{background:transparent;overflow:visible}
  .track.bare > span{border-radius:999px}
  table{width:100%;border-collapse:collapse}
  th{font-size:11.5px;color:var(--ink3);text-align:left;font-weight:600;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
  td{font-size:13px;padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
  tr:last-child td{border-bottom:none}
  .tg{display:inline-block;font-size:11px;padding:3px 9px;border-radius:999px;font-weight:600;white-space:nowrap}
  .tg.proj{background:var(--purple-soft);color:#6c5fd0}
  .tg.hi{background:var(--red-soft);color:var(--red-ink)}
  .tg.mid{background:var(--coral-soft);color:var(--coral-ink)}
  .tg.lo{background:var(--grey-soft);color:var(--ink2)}
  .late{color:var(--red-ink);font-weight:700}
  .empty{text-align:center;padding:26px 10px;color:var(--ink3)}
  .empty .big{font-size:15px;color:var(--ink2);font-weight:700;margin-bottom:4px}
  .empty .sm{font-size:12.5px}
  .proj{border:1px solid var(--line);border-radius:var(--r-sm);margin-bottom:11px;overflow:hidden;background:var(--card2)}
  .proj:last-child{margin-bottom:0}
  .proj-head{display:flex;align-items:center;gap:14px;padding:15px 17px;cursor:pointer;user-select:none}
  .proj-head:hover{background:#f1f0f9}
  .proj-head .chev{transition:transform .25s;color:var(--ink3);flex:none}
  .proj.open .chev{transform:rotate(90deg)}
  .proj-head .pname{font-weight:700;font-size:14px}
  .proj-head .pmeta{font-size:11.5px;color:var(--ink3);margin-top:2px}
  .proj-prog{margin-left:auto;display:flex;align-items:center;gap:12px;min-width:170px}
  .proj-prog .ptrack{flex:1;height:9px;border-radius:999px;background:#e7e7f0;overflow:hidden}
  .proj-prog .pfill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--purple),var(--blue))}
  .proj-prog .ppct{font-weight:800;font-size:14px;width:42px;text-align:right}
  .proj-body{display:none;padding:2px 8px 8px;background:#fff}
  .proj.open .proj-body{display:block}
  .st{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600}
  .st .sdot{width:8px;height:8px;border-radius:50%}
  .mini{height:7px;width:70px;border-radius:999px;background:var(--grey-soft);overflow:hidden;display:inline-block;vertical-align:middle}
  .mini > i{display:block;height:100%;background:linear-gradient(90deg,var(--purple),var(--blue))}
  .kanban{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  @media(max-width:860px){.kanban{grid-template-columns:1fr}}
  .col{background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);padding:15px 14px;display:flex;flex-direction:column}
  .col-h{display:flex;align-items:center;gap:9px;margin-bottom:13px;padding:0 4px}
  .col-h .sdot{width:10px;height:10px;border-radius:50%}
  .col-h h3{font-size:14px;margin:0}
  .col-h .cnt{margin-left:auto;font-size:12px;font-weight:700;color:var(--ink2);background:var(--grey-soft);padding:2px 10px;border-radius:999px}
  .col-body{display:flex;flex-direction:column;gap:11px;max-height:430px;overflow:auto;padding:2px}
  .kc{background:var(--card2);border:1px solid var(--line);border-radius:var(--r-sm);padding:13px 13px;border-left:3px solid var(--grey)}
  .kc .kt{font-weight:700;font-size:13.5px}
  .kc .kp{font-size:11px;color:var(--ink3);margin-top:3px}
  .kc .kfoot{display:flex;align-items:center;gap:9px;margin-top:11px}
  .kc .kfoot .mini{width:auto;flex:1}
  .kc .kt-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
  .kc .kt-row .kt{min-width:0}
  .kc .kt-row .tg{flex:none}
  .kc .kpct{font-size:11px;font-weight:700;color:var(--ink2)}
  .col-body .empty{padding:20px 6px
