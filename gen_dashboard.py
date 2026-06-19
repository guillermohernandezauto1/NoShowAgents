#!/usr/bin/env python3
"""
No-Show Call Outcomes Dashboard Generator
Usage:  python3 gen_dashboard.py [monthly.csv] [weekly.csv] [output.html]
Defaults: data/Monthly_Feed.csv  data/Weekly_Feed.csv  index.html
"""
import csv, json, sys, os

_DIR = os.path.dirname(os.path.abspath(__file__))
MONTHLY_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_DIR, 'data', 'Monthly_Feed.csv')
WEEKLY_PATH  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_DIR, 'data', 'Weekly_Feed.csv')
OUTPUT_PATH  = sys.argv[3] if len(sys.argv) > 3 else os.path.join(_DIR, 'index.html')

NUM_FIELDS = [
    'total_submissions','reached_yes','reached_no','at_branch_yes','at_branch_no',
    'reason_forgot','reason_tried_cancel','reason_did_not_cancel','reason_problem_branch',
    'reason_problem_cs','reason_no_info','reason_late','reason_no_docs','reason_car_not_running',
    'reason_car_deregistered','reason_not_found_branch','reason_duplication','reason_appt_took_place','reason_other',
    'pb_sent_away_docs','pb_eval_rejected','pb_unfriendly','pb_employee_late','pb_price_no_eval',
    'pb_eval_sell_commit','pb_disagree_process','pb_other',
    'result_new_appt','result_follow_up','result_not_interested','result_sold','result_other'
]

def load_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for field in NUM_FIELDS:
            v = r.get(field, '')
            try: r[field] = float(v) if v != '' else 0.0
            except: r[field] = 0.0
        r['year'] = int(r['year'])
    return rows

monthly = load_csv(MONTHLY_PATH)
weekly  = load_csv(WEEKLY_PATH)
for r in monthly: r['month'] = int(r['month'])
for r in weekly:  r['week']  = int(r['week'])

MJ = json.dumps(monthly, ensure_ascii=False, separators=(',',':'))
WJ = json.dumps(weekly,  ensure_ascii=False, separators=(',',':'))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>No-Show Call Outcomes Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;font-size:13px;line-height:1.5}
.app{max-width:1440px;margin:0 auto;padding:16px}
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}
header h1{font-size:18px;font-weight:700;opacity:.9}
.tabs{display:flex;border:1px solid rgba(128,128,128,.25);border-radius:8px;overflow:hidden}
.tab-btn{padding:7px 20px;font-size:12px;font-weight:600;cursor:pointer;border:none;background:transparent;transition:all .15s}
.tab-btn.active{background:rgba(59,130,246,.15);color:#3B82F6}
.tab-btn:hover:not(.active){background:rgba(128,128,128,.1)}
#filter-bar{display:flex;flex-wrap:wrap;gap:12px;padding:12px 14px;border-radius:10px;border:1px solid rgba(128,128,128,.18);margin-bottom:14px;align-items:flex-start}
.f-group{display:flex;flex-direction:column;gap:5px}
.f-label{font-size:11px;font-weight:600;opacity:.55;text-transform:uppercase;letter-spacing:.05em}
.pill-row{display:flex;flex-wrap:wrap;gap:4px}
.pill{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;cursor:pointer;border:1.5px solid transparent;transition:all .15s;opacity:.65}
.pill.on{opacity:1;border-color:currentColor}
.pill:hover{opacity:1}
.agent-wrap{position:relative}
#agent-search{width:200px;padding:5px 10px;border-radius:6px;border:1px solid rgba(128,128,128,.3);font-size:12px;font-family:inherit}
#agent-search:focus{outline:2px solid rgba(59,130,246,.4);border-color:#3B82F6}
#agent-dropdown{position:absolute;top:100%;left:0;z-index:50;width:260px;max-height:240px;overflow-y:auto;border:1px solid rgba(128,128,128,.3);border-radius:8px;padding:4px;margin-top:3px;box-shadow:0 8px 24px rgba(0,0,0,.12);display:none;background:#fff}
#agent-dropdown.open{display:block}
.agent-option{display:flex;align-items:center;gap:7px;padding:5px 8px;border-radius:5px;cursor:pointer;font-size:12px}
.agent-option:hover{background:rgba(59,130,246,.08)}
.agent-option input[type=checkbox]{margin:0;accent-color:#3B82F6}
#selected-agents{display:flex;flex-wrap:wrap;gap:3px;max-width:320px}
.agent-tag{padding:2px 8px;border-radius:12px;font-size:11px;font-weight:500;display:flex;align-items:center;gap:4px;background:rgba(59,130,246,.12);color:#3B82F6}
.agent-tag .rm{cursor:pointer;opacity:.6;font-size:10px}
.agent-tag .rm:hover{opacity:1}
.range-row{display:flex;align-items:center;gap:6px}
.range-row select{padding:4px 8px;border-radius:6px;border:1px solid rgba(128,128,128,.3);font-size:12px;font-family:inherit;background:transparent}
.range-row select:focus{outline:2px solid rgba(59,130,246,.4)}
.range-sep{opacity:.4;font-size:11px}
#kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px}
.kpi-card{padding:14px 16px;border-radius:10px;border:1px solid rgba(128,128,128,.18)}
.kpi-label{font-size:11px;font-weight:600;opacity:.5;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
.kpi-value{font-size:22px;font-weight:700;letter-spacing:-.5px}
#charts-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
@media(max-width:900px){#charts-grid{grid-template-columns:1fr}}
.chart-card{border-radius:10px;border:1px solid rgba(128,128,128,.18);padding:14px 16px;overflow:hidden}
.chart-card.full{grid-column:1/-1}
.card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px}
.card-title{font-size:13px;font-weight:700;opacity:.85}
.card-controls{display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.ctrl-btn{padding:3px 10px;border-radius:5px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid rgba(128,128,128,.3);background:transparent;transition:all .15s;font-family:inherit}
.ctrl-btn.active{background:rgba(59,130,246,.12);color:#3B82F6;border-color:rgba(59,130,246,.3)}
.ctrl-btn:hover:not(.active){background:rgba(128,128,128,.08)}
.ctrl-sep{width:1px;height:16px;background:rgba(128,128,128,.25);margin:0 2px}
.ctrl-select{padding:3px 8px;border-radius:5px;font-size:11px;border:1px solid rgba(128,128,128,.3);background:transparent;font-family:inherit}
.chart-scroll{overflow-x:auto}
.chart-inner{position:relative}
.chart-note{font-size:10px;opacity:.35;text-align:center;margin-top:5px}
/* KPI inline */
.kpi-inline-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:12px}
.kpi-sm{padding:10px 12px;border-radius:8px;background:rgba(128,128,128,.05)}
.kpi-sm-label{font-size:10px;font-weight:600;opacity:.5;text-transform:uppercase;letter-spacing:.05em}
.kpi-sm-value{font-size:17px;font-weight:700}
/* ── Mini-table (inside chart cards) ── */
.mini-tbl-wrap{display:none;padding-top:2px}
.mini-tbl-toolbar{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}
.mini-tbl-search{flex:1;max-width:220px;padding:5px 10px;border-radius:6px;border:1px solid rgba(128,128,128,.3);font-size:12px;font-family:inherit;background:transparent}
.mini-tbl-search:focus{outline:2px solid rgba(59,130,246,.35);border-color:#3B82F6}
.mini-tbl-info{font-size:11px;opacity:.4}
.mini-tbl-scroll{max-height:360px;overflow-y:auto;border-radius:7px;border:1px solid rgba(128,128,128,.14)}
.mt{width:100%;border-collapse:collapse}
.mt th{padding:8px 11px;text-align:left;font-size:11px;font-weight:700;opacity:.55;cursor:pointer;user-select:none;position:sticky;top:0;z-index:2;border-bottom:1px solid rgba(128,128,128,.14);white-space:nowrap}
.mt th:hover{opacity:.85}
.mt th .si{margin-left:3px;opacity:.3}
.mt th.srt .si{opacity:1;color:#3B82F6}
.mt td{padding:8px 11px;font-size:12px;border-bottom:1px solid rgba(128,128,128,.08);white-space:nowrap}
.mt tr:last-child td{border-bottom:none}
.mt tr:hover td{background:rgba(128,128,128,.03)}
.mt .nm{max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;font-weight:500}
.mt .pct-g{color:#059669;font-weight:700}
.mt .pct-r{color:#DC2626;font-weight:700}
/* global agent-table */
#table-wrap{overflow-x:auto;margin-top:4px}
table.agt{width:100%;border-collapse:collapse}
table.agt th,table.agt td{padding:8px 10px;text-align:left;border-bottom:1px solid rgba(128,128,128,.15);font-size:12px;white-space:nowrap}
table.agt th{font-weight:600;opacity:.65;cursor:pointer;user-select:none;position:sticky;top:0;z-index:3;transition:background .12s,opacity .12s;border-bottom:2px solid transparent}
table.agt th:hover{opacity:1;background:rgba(59,130,246,.05)}
table.agt th.sorted{opacity:1;color:#3B82F6;background:rgba(59,130,246,.07);border-bottom:2px solid rgba(59,130,246,.35)}
table.agt th .sort-icon{display:inline-flex;flex-direction:column;vertical-align:middle;margin-left:5px;opacity:.3;font-size:9px;line-height:1.1;gap:0px}
table.agt th:hover .sort-icon{opacity:.65}
table.agt th.sorted .sort-icon{opacity:1;color:#3B82F6}
table.agt tr:hover td{background:rgba(128,128,128,.04)}
.cell-green{color:#059669;font-weight:600}
.cell-red{color:#DC2626;font-weight:600}
.cell-neutral{opacity:.6}
.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;font-weight:600}
.empty-state{padding:40px 20px;text-align:center;opacity:.35;font-size:13px}
/* ── Top-level view tabs (bigger) ── */
header .tabs .tab-btn{font-size:14px;padding:10px 24px}
/* ── Granularity toggle inside filter bar ── */
.granularity-tabs .tab-btn{padding:8px 18px;font-size:13px}
/* ── Prominent filters (Country + time range) ── */
#filter-bar{gap:20px;padding:16px 18px}
.f-group.prominent .f-label{font-size:12px;opacity:.7;margin-bottom:3px}
.pill-lg{padding:8px 16px;font-size:14px;border-radius:22px;border-width:2px}
.range-row.lg{gap:8px}
.range-row.lg select{padding:9px 14px;font-size:14px;font-weight:600;border-radius:8px;border-width:1.5px}
.range-row.lg .range-sep{font-size:13px;opacity:.6}
/* ── Trend tab ── */
#view-trend .card-title{font-size:16px}
#view-trend .ctrl-select{padding:6px 12px;font-size:13px}
</style>
</head>
<body>
<div class="app">

<!-- HEADER -->
<header>
  <div style="display:flex;align-items:center;gap:12px">
    <h1>No-Show Call Outcomes</h1>
  </div>
  <div class="tabs">
    <button class="tab-btn active" id="btn-view-agent" onclick="setView('agent')">Agent view</button>
    <button class="tab-btn"        id="btn-view-trend" onclick="setView('trend')">Trend over time</button>
  </div>
</header>

<!-- FILTER BAR -->
<div id="filter-bar">
  <div class="f-group">
    <div class="f-label">Data</div>
    <div class="tabs granularity-tabs">
      <button class="tab-btn active" id="btn-monthly" onclick="setTab('monthly')">Monthly</button>
      <button class="tab-btn"        id="btn-weekly"  onclick="setTab('weekly')">Weekly</button>
    </div>
  </div>
  <div class="f-group">
    <div class="f-label">Year</div>
    <div class="pill-row" id="year-pills"></div>
  </div>
  <div class="f-group prominent">
    <div class="f-label">Country</div>
    <div class="pill-row" id="country-pills"></div>
  </div>
  <div class="f-group">
    <div class="f-label">Agent</div>
    <div class="agent-wrap">
      <input type="text" id="agent-search" placeholder="Search agents…" autocomplete="off">
      <div id="agent-dropdown">
        <div style="padding:4px 8px;border-bottom:1px solid rgba(128,128,128,.15);display:flex;gap:8px">
          <span style="font-size:11px;cursor:pointer;color:#3B82F6" onclick="selectAllAgents()">All</span>
          <span style="font-size:11px;cursor:pointer;color:#3B82F6" onclick="clearAgents()">Clear</span>
        </div>
        <div id="agent-list"></div>
      </div>
    </div>
    <div id="selected-agents"></div>
  </div>
  <div class="f-group prominent" id="month-range-group">
    <div class="f-label">Month Range</div>
    <div class="range-row lg">
      <select id="month-from" onchange="onMonthRange()"></select>
      <span class="range-sep">to</span>
      <select id="month-to"   onchange="onMonthRange()"></select>
    </div>
  </div>
  <div class="f-group prominent" id="week-range-group" style="display:none">
    <div class="f-label">Week Range</div>
    <div class="range-row lg">
      <select id="week-from" onchange="onWeekRange()"></select>
      <span class="range-sep">to</span>
      <select id="week-to"   onchange="onWeekRange()"></select>
    </div>
  </div>
</div>

<!-- ============ AGENT VIEW ============ -->
<div id="view-agent">

<!-- CHARTS GRID -->
<div id="charts-grid">

  <!-- 1: Customers Reached -->
  <div class="chart-card">
    <div class="card-header">
      <div class="card-title">Customers Reached</div>
      <div class="card-controls">
        <button class="ctrl-btn"        id="reached-v-country" onclick="setCView('reached','country')">By Country</button>
        <button class="ctrl-btn active" id="reached-v-agent"   onclick="setCView('reached','agent')">Top Agents</button>
        <div class="ctrl-sep"></div>
        <button class="ctrl-btn"        id="reached-v-table"   onclick="setCView('reached','table')">Table</button>
      </div>
    </div>
    <div id="reached-chart-wrap" class="chart-inner" style="height:280px">
      <canvas id="chart-reached"></canvas>
    </div>
    <div class="chart-note" id="reached-note"></div>
    <div class="mini-tbl-wrap" id="reached-tbl-wrap">
      <div class="mini-tbl-toolbar">
        <input class="mini-tbl-search" id="reached-q" placeholder="Filter agents or countries…" oninput="filterMT('reached')">
        <span class="mini-tbl-info" id="reached-tbl-info"></span>
      </div>
      <div class="mini-tbl-scroll">
        <table class="mt">
          <thead><tr>
            <th onclick="sortMT('reached','agent')">Agent <span class="si">↕</span></th>
            <th onclick="sortMT('reached','country')">Country <span class="si">↕</span></th>
            <th onclick="sortMT('reached','reached_yes')">Reached <span class="si">↕</span></th>
            <th onclick="sortMT('reached','reached_no')">Not Reached <span class="si">↕</span></th>
            <th onclick="sortMT('reached','total')">Total <span class="si">↕</span></th>
            <th onclick="sortMT('reached','pct')">% Reached <span class="si">↕</span></th>
          </tr></thead>
          <tbody id="reached-tbl-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 2: No-show Reason Split -->
  <div class="chart-card">
    <div class="card-header">
      <div class="card-title">No-Show Reason Split</div>
      <div class="card-controls">
        <button class="ctrl-btn"        id="reason-v-overall" onclick="setCView('reason','overall')">Overall</button>
        <button class="ctrl-btn"        id="reason-v-country" onclick="setCView('reason','country')">By Country</button>
        <button class="ctrl-btn active" id="reason-v-agent"   onclick="setCView('reason','agent')">Top Agents</button>
        <div class="ctrl-sep"></div>
        <button class="ctrl-btn"        id="reason-v-table"   onclick="setCView('reason','table')">Table</button>
      </div>
    </div>
    <div id="reason-subtoggle" style="display:none;gap:5px;margin-bottom:8px">
      <button class="ctrl-btn active" id="reason-btn-pie" onclick="setReasonSubView('pie')">Pie</button>
      <button class="ctrl-btn"        id="reason-btn-bar" onclick="setReasonSubView('bar')">Bar</button>
    </div>
    <div id="reason-chart-wrap" class="chart-inner" style="height:320px">
      <canvas id="chart-reason"></canvas>
    </div>
    <div class="chart-note" id="reason-note"></div>
    <div class="mini-tbl-wrap" id="reason-tbl-wrap">
      <div class="mini-tbl-toolbar">
        <input class="mini-tbl-search" id="reason-q" placeholder="Filter agents or countries…" oninput="filterMT('reason')">
        <span class="mini-tbl-info" id="reason-tbl-info"></span>
      </div>
      <div class="mini-tbl-scroll">
        <table class="mt">
          <thead><tr>
            <th onclick="sortMT('reason','agent')">Agent <span class="si">↕</span></th>
            <th onclick="sortMT('reason','country')">Country <span class="si">↕</span></th>
            <th onclick="sortMT('reason','total')">Total <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_forgot')">Forgot <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_tried_cancel')">Tried Cancel <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_did_not_cancel')">Did Not Cancel <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_problem_branch')">Prob Branch <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_problem_cs')">Prob CS <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_no_info')">No Info <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_late')">Late <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_no_docs')">No Docs <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_car_not_running')">Car Not Run <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_car_deregistered')">Car Dereg <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_not_found_branch')">Not Found <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_duplication')">Duplication <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_appt_took_place')">Appt Took Place <span class="si">↕</span></th>
            <th onclick="sortMT('reason','reason_other')">Other <span class="si">↕</span></th>
          </tr></thead>
          <tbody id="reason-tbl-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 3: % At Branch -->
  <div class="chart-card">
    <div class="card-header">
      <div class="card-title">% Customer Was at the Branch</div>
      <div class="card-controls">
        <button class="ctrl-btn"        id="branch-v-country" onclick="setCView('branch','country')">By Country</button>
        <button class="ctrl-btn active" id="branch-v-agent"   onclick="setCView('branch','agent')">Top Agents</button>
        <div class="ctrl-sep"></div>
        <button class="ctrl-btn"        id="branch-v-table"   onclick="setCView('branch','table')">Table</button>
      </div>
    </div>
    <div id="branch-chart-wrap" class="chart-inner" style="height:280px">
      <canvas id="chart-branch-pct"></canvas>
    </div>
    <div class="chart-note" id="branch-note"></div>
    <div class="mini-tbl-wrap" id="branch-tbl-wrap">
      <div class="mini-tbl-toolbar">
        <input class="mini-tbl-search" id="branch-q" placeholder="Filter agents or countries…" oninput="filterMT('branch')">
        <span class="mini-tbl-info" id="branch-tbl-info"></span>
      </div>
      <div class="mini-tbl-scroll">
        <table class="mt">
          <thead><tr>
            <th onclick="sortMT('branch','agent')">Agent <span class="si">↕</span></th>
            <th onclick="sortMT('branch','country')">Country <span class="si">↕</span></th>
            <th onclick="sortMT('branch','at_branch_yes')">At Branch <span class="si">↕</span></th>
            <th onclick="sortMT('branch','at_branch_no')">Not At Branch <span class="si">↕</span></th>
            <th onclick="sortMT('branch','total')">Total <span class="si">↕</span></th>
            <th onclick="sortMT('branch','pct')">% At Branch <span class="si">↕</span></th>
          </tr></thead>
          <tbody id="branch-tbl-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 4: Problem at Branch -->
  <div class="chart-card">
    <div class="card-header">
      <div class="card-title">Problem at Branch</div>
      <div class="card-controls">
        <button class="ctrl-btn"        id="problem-v-overall"  onclick="setCView('problem','overall')">Overall</button>
        <button class="ctrl-btn"        id="problem-v-country"  onclick="setCView('problem','country')">By Country</button>
        <button class="ctrl-btn active" id="problem-v-agent"    onclick="setCView('problem','agent')">Top Agents</button>
        <button class="ctrl-btn"        id="problem-v-mix"      onclick="setCView('problem','mix')">Agent Mix</button>
        <div class="ctrl-sep"></div>
        <button class="ctrl-btn"        id="problem-v-table"    onclick="setCView('problem','table')">Table</button>
      </div>
    </div>
    <div id="problem-kpi-wrap"></div>
    <div id="problem-chart-wrap" class="chart-inner" style="height:220px">
      <canvas id="chart-pb"></canvas>
    </div>
    <div class="chart-note" id="problem-note"></div>
    <div class="mini-tbl-wrap" id="problem-tbl-wrap">
      <div class="mini-tbl-toolbar">
        <input class="mini-tbl-search" id="problem-q" placeholder="Filter agents or countries…" oninput="filterMT('problem')">
        <span class="mini-tbl-info" id="problem-tbl-info"></span>
      </div>
      <div class="mini-tbl-scroll">
        <table class="mt">
          <thead><tr>
            <th onclick="sortMT('problem','agent')">Agent <span class="si">↕</span></th>
            <th onclick="sortMT('problem','country')">Country <span class="si">↕</span></th>
            <th onclick="sortMT('problem','submissions')">Submissions <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_total')">PB Total <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pct')">PB Rate % <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_sent_away_docs')">Sent Away <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_eval_rejected')">Eval Rej <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_unfriendly')">Unfriendly <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_employee_late')">Emp Late <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_price_no_eval')">Price/Eval <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_eval_sell_commit')">Sell Commit <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_disagree_process')">Disagree <span class="si">↕</span></th>
            <th onclick="sortMT('problem','pb_other')">Other <span class="si">↕</span></th>
          </tr></thead>
          <tbody id="problem-tbl-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 4b: Problem at Branch — Agent Mix (separate full-width card) -->
  <div class="chart-card full">
    <div class="card-header">
      <div class="card-title">Problem Type Mix per Agent</div>
      <div style="font-size:11px;opacity:.45">Each bar = that agent's % breakdown across all 8 branch problem types · Hover for team avg comparison</div>
    </div>
    <div style="max-height:480px;overflow-y:auto;border-radius:6px">
      <div id="pb-mix-chart-wrap" class="chart-inner">
        <canvas id="chart-pb-mix"></canvas>
      </div>
    </div>
    <div class="chart-note" id="pb-mix-note"></div>
  </div>

  <!-- 5: Rescheduled % -->
  <div class="chart-card">
    <div class="card-header">
      <div class="card-title">Appointment Rescheduled %</div>
      <div class="card-controls">
        <button class="ctrl-btn"        id="resched-v-country" onclick="setCView('resched','country')">By Country</button>
        <button class="ctrl-btn active" id="resched-v-agent"   onclick="setCView('resched','agent')">Top Agents</button>
        <div class="ctrl-sep"></div>
        <button class="ctrl-btn"        id="resched-v-table"   onclick="setCView('resched','table')">Table</button>
      </div>
    </div>
    <div id="resched-chart-wrap" class="chart-inner" style="height:280px">
      <canvas id="chart-reschedule"></canvas>
    </div>
    <div class="chart-note" id="resched-note"></div>
    <div class="mini-tbl-wrap" id="resched-tbl-wrap">
      <div class="mini-tbl-toolbar">
        <input class="mini-tbl-search" id="resched-q" placeholder="Filter agents or countries…" oninput="filterMT('resched')">
        <span class="mini-tbl-info" id="resched-tbl-info"></span>
      </div>
      <div class="mini-tbl-scroll">
        <table class="mt">
          <thead><tr>
            <th onclick="sortMT('resched','agent')">Agent <span class="si">↕</span></th>
            <th onclick="sortMT('resched','country')">Country <span class="si">↕</span></th>
            <th onclick="sortMT('resched','rescheduled')">Rescheduled <span class="si">↕</span></th>
            <th onclick="sortMT('resched','total')">Reached <span class="si">↕</span></th>
            <th onclick="sortMT('resched','pct')">% Rescheduled <span class="si">↕</span></th>
          </tr></thead>
          <tbody id="resched-tbl-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 7: Agent Performance Table -->
  <div class="chart-card full">
    <div class="card-header">
      <div class="card-title">Agent Performance</div>
      <span id="table-count" style="font-size:11px;opacity:.4"></span>
    </div>
    <div id="table-wrap" style="max-height:520px;overflow-y:auto">
      <table class="agt" id="agent-table">
        <thead id="table-head"></thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>

</div><!-- /charts-grid -->
</div><!-- /view-agent -->

<!-- ============ TREND VIEW ============ -->
<div id="view-trend" style="display:none">
  <div class="chart-card full">
    <div class="card-header">
      <div class="card-title">Trend Over Time</div>
      <div class="card-controls">
        <select class="ctrl-select" id="trend-metric" onchange="renderTrend()">
          <option value="reached_yes">Reached</option>
          <option value="result_new_appt">Rescheduled</option>
          <option value="at_branch_yes">At Branch</option>
          <option value="reason_problem_branch">Reason: Branch Problem</option>
          <option value="total_submissions">Total Submissions</option>
        </select>
        <select class="ctrl-select" id="trend-group" onchange="onTrendGroupChange()">
          <option value="agent">By Agent</option>
          <option value="country">By Country</option>
        </select>
        <!-- Agent picker — shown only in By Agent mode -->
        <div id="trend-agent-filter" style="display:none;position:relative">
          <button class="ctrl-btn" id="trend-agent-btn" onclick="toggleTrendAgentDd()" style="min-width:110px;text-align:left;justify-content:space-between;display:inline-flex;align-items:center;gap:4px">
            <span id="trend-agent-label">All agents</span><span style="opacity:.5;font-size:10px">▼</span>
          </button>
          <div id="trend-agent-dd" style="display:none;position:absolute;top:calc(100% + 3px);right:0;z-index:60;width:250px;max-height:280px;overflow-y:auto;border:1px solid rgba(128,128,128,.3);border-radius:8px;padding:4px;box-shadow:0 8px 24px rgba(0,0,0,.14);background:#fff">
            <div style="padding:4px 8px;border-bottom:1px solid rgba(128,128,128,.12);display:flex;gap:10px;align-items:center">
              <span style="font-size:11px;cursor:pointer;color:#3B82F6" onclick="selectAllTrendAgents()">All</span>
              <span style="font-size:11px;cursor:pointer;color:#3B82F6" onclick="clearTrendAgents()">None</span>
              <span id="trend-agent-dd-count" style="font-size:11px;opacity:.4;margin-left:auto"></span>
            </div>
            <input type="text" id="trend-agent-search" placeholder="Search agents…" oninput="filterTrendAgentDd()"
              style="display:block;width:calc(100% - 12px);margin:5px 6px;padding:4px 8px;border-radius:5px;border:1px solid rgba(128,128,128,.3);font-size:12px;font-family:inherit">
            <div id="trend-agent-list"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="chart-inner" style="height:600px">
      <canvas id="chart-trend"></canvas>
    </div>
  </div>
</div><!-- /view-trend -->
</div><!-- /app -->

<script>
// ============================================================
// DATA
// ============================================================
const MONTHLY = """ + MJ + r""";
const WEEKLY  = """ + WJ + r""";

// ============================================================
// CONSTANTS
// ============================================================
const COUNTRIES = ['BE','DE','ES','FR','IT','NL','PT','SE'];
const CCOLOR = {
  BE:'#F59E0B', DE:'#3B82F6', ES:'#EF4444', FR:'#7C3AED',
  IT:'#10B981', NL:'#F97316', PT:'#EC4899', SE:'#06B6D4'
};
const NUM_FIELDS = [
  'total_submissions','reached_yes','reached_no','at_branch_yes','at_branch_no',
  'reason_forgot','reason_tried_cancel','reason_did_not_cancel','reason_problem_branch',
  'reason_problem_cs','reason_no_info','reason_late','reason_no_docs','reason_car_not_running',
  'reason_car_deregistered','reason_not_found_branch','reason_duplication','reason_appt_took_place','reason_other',
  'pb_sent_away_docs','pb_eval_rejected','pb_unfriendly','pb_employee_late','pb_price_no_eval',
  'pb_eval_sell_commit','pb_disagree_process','pb_other',
  'result_new_appt','result_follow_up','result_not_interested','result_sold','result_other'
];
const REASON_COLS = [
  'reason_forgot','reason_tried_cancel','reason_did_not_cancel','reason_problem_branch',
  'reason_problem_cs','reason_no_info','reason_late','reason_no_docs','reason_car_not_running',
  'reason_car_deregistered','reason_not_found_branch','reason_duplication','reason_appt_took_place','reason_other'
];
const REASON_LABELS = [
  'Forgot','Tried to Cancel','Did Not Cancel','Problem Branch','Problem CS',
  'No Info','Late','No Docs','Car Not Running','Car Deregistered',
  'Not Found Branch','Duplication','Appt Took Place','Other'
];
const PB_COLS = [
  'pb_sent_away_docs','pb_eval_rejected','pb_unfriendly','pb_employee_late',
  'pb_price_no_eval','pb_eval_sell_commit','pb_disagree_process','pb_other'
];
const PB_LABELS = [
  'Sent Away (Docs)','Eval Rejected','Unfriendly','Employee Late',
  'Price/No Eval','Sell Commitment','Disagree Process','Other'
];
const REASON_COLORS = [
  '#6366F1','#8B5CF6','#EC4899','#F43F5E','#F97316','#EAB308',
  '#22C55E','#14B8A6','#06B6D4','#3B82F6','#A78BFA','#FB7185',
  '#34D399','#94A3B8'
];
const PB_COLORS = [
  '#EF4444','#F97316','#EAB308','#22C55E','#06B6D4','#8B5CF6','#EC4899','#94A3B8'
];
const TOP_N = 15; // agents shown in "Top Agents" view

// ============================================================
// STATE
// ============================================================
let S = {
  view: 'agent',          // 'agent' | 'trend' (top-level tab)
  tab: 'monthly',         // 'monthly' | 'weekly' (data granularity)
  years: [], countries: [], agents: [],
  monthPeriodFrom: 0, monthPeriodTo: 999999,  // overridden by buildMonthSelects
  weekPeriodFrom:  0, weekPeriodTo:  999999,  // overridden by buildWeekSelects
  reasonView: 'pie',
  sortCol: 'total_submissions', sortDir: -1
};
let CH = {};

// Chart view modes — default every chart to Top Agents
let CV = { reached: 'agent', branch: 'agent', resched: 'agent', reason: 'agent', problem: 'agent' };

// Mini-table state per chart
let MT = {
  reached: { data:[], sortCol:'total',   sortDir:-1, filter:'' },
  branch:  { data:[], sortCol:'pct',     sortDir:-1, filter:'' },
  resched: { data:[], sortCol:'pct',     sortDir:-1, filter:'' },
  reason:  { data:[], sortCol:'total',   sortDir:-1, filter:'' },
  problem: { data:[], sortCol:'pct',     sortDir:-1, filter:'' }
};

// ============================================================
// HELPERS
// ============================================================
function srcData() { return S.tab === 'monthly' ? MONTHLY : WEEKLY; }

function filtered() {
  return srcData().filter(r => {
    if (S.years.length    && !S.years.includes(r.year))        return false;
    if (S.countries.length && !S.countries.includes(r.country)) return false;
    if (S.agents.length   && !S.agents.includes(r.agent_name)) return false;
    if (S.tab === 'monthly') {
      if ((r.year*100+r.month) < S.monthPeriodFrom || (r.year*100+r.month) > S.monthPeriodTo) return false;
    } else {
      if ((r.year*100+r.week) < S.weekPeriodFrom || (r.year*100+r.week) > S.weekPeriodTo) return false;
    }
    return true;
  });
}

function sumField(rows, field) { return rows.reduce((s,r) => s + (r[field]||0), 0); }

function aggByAgent(rows) {
  const map = {};
  for (const r of rows) {
    if (!map[r.agent_name]) {
      map[r.agent_name] = { agent: r.agent_name, country: r.country };
      for (const f of NUM_FIELDS) map[r.agent_name][f] = 0;
    }
    for (const f of NUM_FIELDS) map[r.agent_name][f] += r[f];
  }
  return Object.values(map);
}

function aggByCountry(rows) {
  const map = {};
  for (const r of rows) {
    const k = r.country;
    if (!map[k]) {
      map[k] = { country: k };
      for (const f of NUM_FIELDS) map[k][f] = 0;
    }
    for (const f of NUM_FIELDS) map[k][f] += r[f];
  }
  return Object.values(map);
}

function h2r(hex, a) {
  const rv = parseInt(hex.slice(1,3),16);
  const g  = parseInt(hex.slice(3,5),16);
  const b  = parseInt(hex.slice(5,7),16);
  return a == null ? `rgb(${rv},${g},${b})` : `rgba(${rv},${g},${b},${a})`;
}
function fmtPct(v, total) { if (!total) return '—'; return (v/total*100).toFixed(1)+'%'; }
function pctN(v, total) { if (!total) return 0; return +(v/total*100).toFixed(2); }
function fmtNum(v) { return Math.round(v).toLocaleString(); }
function trunc(s, n) { return s.length > n ? s.slice(0,n-1)+'…' : s; }

function mkChart(id, cfg) {
  if (CH[id]) CH[id].destroy();
  CH[id] = new Chart(document.getElementById(id), cfg);
  return CH[id];
}

// ============================================================
// CHART VIEW TOGGLE (for the 3 agent bar charts)
// ============================================================
const C_MAP = {
  reached: { canvas: 'reached-chart-wrap', table: 'reached-tbl-wrap', note: 'reached-note',
             modes: ['country','agent','table'] },
  branch:  { canvas: 'branch-chart-wrap',  table: 'branch-tbl-wrap',  note: 'branch-note',
             modes: ['country','agent','table'] },
  resched: { canvas: 'resched-chart-wrap', table: 'resched-tbl-wrap', note: 'resched-note',
             modes: ['country','agent','table'] },
  reason:  { canvas: 'reason-chart-wrap',  table: 'reason-tbl-wrap',  note: 'reason-note',
             modes: ['overall','country','agent','table'], subtoggle: 'reason-subtoggle' },
  problem: { canvas: 'problem-chart-wrap', table: 'problem-tbl-wrap', note: 'problem-note',
             modes: ['overall','country','agent','mix','table'], kpi: 'problem-kpi-wrap' }
};

function setCView(chart, mode) {
  CV[chart] = mode;
  const cm = C_MAP[chart];
  cm.modes.forEach(m => {
    const el = document.getElementById(`${chart}-v-${m}`);
    if (el) el.classList.toggle('active', m === mode);
  });
  const showChart = mode !== 'table';
  document.getElementById(cm.canvas).style.display = showChart ? '' : 'none';
  document.getElementById(cm.note).style.display   = showChart ? '' : 'none';
  document.getElementById(cm.table).style.display  = mode === 'table' ? 'block' : 'none';
  if (cm.subtoggle) document.getElementById(cm.subtoggle).style.display = (mode === 'overall') ? '' : 'none';
  if (cm.kpi)       document.getElementById(cm.kpi).style.display       = (mode === 'overall') ? '' : 'none';

  const rows = filtered();
  if (mode === 'table') {
    buildMT(chart, rows);
    renderMTUI(chart);
  } else {
    if (chart === 'reached') renderReachedChart(rows);
    if (chart === 'branch')  renderBranchChart(rows);
    if (chart === 'resched') renderRescheduleChart(rows);
    if (chart === 'reason')  renderReasonChart(rows);
    if (chart === 'problem') renderProblemChart(rows);
  }
}

// ============================================================
// TOP-LEVEL VIEW  (Agent view / Trend over time)
// ============================================================
function setView(view) {
  S.view = view;
  document.getElementById('btn-view-agent').classList.toggle('active', view === 'agent');
  document.getElementById('btn-view-trend').classList.toggle('active', view === 'trend');
  document.getElementById('view-agent').style.display = view === 'agent' ? '' : 'none';
  document.getElementById('view-trend').style.display = view === 'trend' ? '' : 'none';
  // Re-render the now-visible view so charts size correctly after being unhidden.
  if (view === 'trend') {
    renderTrend();
    if (CH['chart-trend']) CH['chart-trend'].resize();
  } else {
    render();
  }
}

// ============================================================
// TAB  (Monthly / Weekly data granularity)
// ============================================================
function setTab(tab) {
  S.tab = tab;
  document.getElementById('btn-monthly').classList.toggle('active', tab === 'monthly');
  document.getElementById('btn-weekly').classList.toggle('active',  tab === 'weekly');
  document.getElementById('month-range-group').style.display = tab === 'monthly' ? '' : 'none';
  document.getElementById('week-range-group').style.display  = tab === 'weekly'  ? '' : 'none';
  buildYearPills();
  buildAgentList();
  render();
}

// ============================================================
// FILTER UI
// ============================================================
function buildYearPills() {
  const years = [...new Set(srcData().map(r => r.year))].sort();
  const el = document.getElementById('year-pills');
  el.innerHTML = '';
  for (const y of years) {
    const btn = document.createElement('button');
    btn.className = 'pill' + (S.years.includes(y) ? ' on' : '');
    btn.textContent = y;
    btn.style.color = '#6B7280';
    btn.onclick = () => toggleFilter(S.years, y, buildYearPills, render);
    el.appendChild(btn);
  }
}

function buildCountryPills() {
  const el = document.getElementById('country-pills');
  el.innerHTML = '';
  for (const c of COUNTRIES) {
    const btn = document.createElement('button');
    btn.className = 'pill pill-lg' + (S.countries.includes(c) ? ' on' : '');
    btn.textContent = c;
    btn.style.color = CCOLOR[c];
    btn.onclick = () => selectCountry(c);
    el.appendChild(btn);
  }
}

// Country is single-select: pick one country, or click the active one again to clear (all countries).
function selectCountry(c) {
  S.countries = (S.countries.length === 1 && S.countries[0] === c) ? [] : [c];
  buildCountryPills();
  buildAgentList();
  render();
}

function toggleFilter(arr, val, rebuildUI, callback) {
  const i = arr.indexOf(val);
  if (i >= 0) arr.splice(i,1); else arr.push(val);
  rebuildUI();
  callback();
}

function buildMonthSelects() {
  const MN = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'};
  // Only include year-month combinations that have actual data rows
  const existing = new Set(MONTHLY.map(r => `${r.year}-${r.month}`));
  const opts = [...existing]
    .map(k => { const [y,m] = k.split('-').map(Number); return [y, m, `${MN[m]} ${y}`]; })
    .sort((a,b) => a[0]*100+a[1] - (b[0]*100+b[1]));
  ['month-from','month-to'].forEach((id,idx) => {
    const sel = document.getElementById(id);
    sel.innerHTML = '';
    for (const [y,m,label] of opts) {
      const o = document.createElement('option');
      o.value = `${y}-${m}`; o.textContent = label;
      sel.appendChild(o);
    }
    sel.value = idx === 0 ? `${opts[0][0]}-${opts[0][1]}` : `${opts[opts.length-1][0]}-${opts[opts.length-1][1]}`;
  });
  onMonthRange();
}

function buildWeekSelects() {
  // Only include year-week combinations that have actual data rows
  const existing = new Set(WEEKLY.map(r => `${r.year}-${r.week}`));
  const opts = [...existing]
    .map(k => { const [y,w] = k.split('-').map(Number); return [y, w, `W${w} ${y}`]; })
    .sort((a,b) => a[0]*100+a[1] - (b[0]*100+b[1]));
  ['week-from','week-to'].forEach((id,idx) => {
    const sel = document.getElementById(id);
    sel.innerHTML = '';
    for (const [y,w,label] of opts) {
      const o = document.createElement('option');
      o.value = `${y}-${w}`; o.textContent = label;
      sel.appendChild(o);
    }
    sel.value = idx === 0 ? `${opts[0][0]}-${opts[0][1]}` : `${opts[opts.length-1][0]}-${opts[opts.length-1][1]}`;
  });
  onWeekRange();
}

function onMonthRange() {
  const f = document.getElementById('month-from').value.split('-').map(Number);
  const t = document.getElementById('month-to').value.split('-').map(Number);
  S.monthPeriodFrom = f[0]*100 + f[1];  // year*100 + month
  S.monthPeriodTo   = t[0]*100 + t[1];
  render();
}
function onWeekRange() {
  const f = document.getElementById('week-from').value.split('-').map(Number);
  const t = document.getElementById('week-to').value.split('-').map(Number);
  S.weekPeriodFrom = f[0]*100 + f[1];  // year*100 + week
  S.weekPeriodTo   = t[0]*100 + t[1];
  render();
}

function buildAgentList() {
  const agents = [...new Set(srcData()
    .filter(r => !S.countries.length || S.countries.includes(r.country))
    .map(r => r.agent_name))].sort();
  const el = document.getElementById('agent-list');
  el.innerHTML = '';
  for (const a of agents) {
    const div = document.createElement('div');
    div.className = 'agent-option'; div.dataset.name = a;
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.checked = S.agents.includes(a);
    cb.addEventListener('change', () => {
      if (cb.checked) { if (!S.agents.includes(a)) S.agents.push(a); }
      else S.agents = S.agents.filter(x => x !== a);
      renderSelectedAgents(); render();
    });
    const lbl = document.createElement('label'); lbl.textContent = a;
    div.appendChild(cb); div.appendChild(lbl);
    el.appendChild(div);
  }
  renderSelectedAgents();
}

function renderSelectedAgents() {
  const el = document.getElementById('selected-agents');
  if (!S.agents.length) { el.innerHTML = '<span style="font-size:11px;opacity:.4">All agents</span>'; return; }
  el.innerHTML = S.agents.map(a =>
    `<span class="agent-tag">${a}<span class="rm" onclick="removeAgent('${a.replace(/'/g,"\\'")}')">✕</span></span>`
  ).join('');
}

function removeAgent(name) {
  S.agents = S.agents.filter(a => a !== name);
  document.querySelectorAll('.agent-option').forEach(d => {
    if (d.dataset.name === name) d.querySelector('input').checked = false;
  });
  renderSelectedAgents(); render();
}

function selectAllAgents() {
  S.agents = [...new Set(srcData().map(r => r.agent_name))].sort();
  buildAgentList(); render();
}
function clearAgents() {
  S.agents = [];
  document.querySelectorAll('.agent-option input').forEach(cb => cb.checked = false);
  renderSelectedAgents(); render();
}

document.getElementById('agent-search').addEventListener('focus', () =>
  document.getElementById('agent-dropdown').classList.add('open'));
document.addEventListener('click', e => {
  if (!document.querySelector('.agent-wrap').contains(e.target))
    document.getElementById('agent-dropdown').classList.remove('open');
});
document.getElementById('agent-search').addEventListener('input', function() {
  const q = this.value.toLowerCase();
  document.querySelectorAll('.agent-option').forEach(d => {
    d.style.display = d.dataset.name.toLowerCase().includes(q) ? '' : 'none';
  });
});

// ============================================================
// CHART 1: CUSTOMERS REACHED  (country / top-agents)
// ============================================================
function renderReachedChart(rows) {
  if (CV.reached === 'agent') renderReachedAgents(rows);
  else renderReachedCountry(rows);
}

function renderReachedCountry(rows) {
  const by = aggByCountry(rows).sort((a,b)=>(b.reached_yes+b.reached_no)-(a.reached_yes+a.reached_no));
  const n  = by.length;
  const h  = Math.max(200, n * 38);
  const wrap = document.getElementById('reached-chart-wrap');
  wrap.style.height = h + 'px';
  document.getElementById('reached-note').textContent = '';

  mkChart('chart-reached', {
    type: 'bar',
    data: {
      labels: by.map(c => c.country),
      datasets: [
        { label:'Reached',     data: by.map(c=>c.reached_yes), backgroundColor: by.map(c=>CCOLOR[c.country]||'#94A3B8'), stack:'s' },
        { label:'Not Reached', data: by.map(c=>c.reached_no),  backgroundColor: by.map(c=>h2r(CCOLOR[c.country]||'#94A3B8',.2)), stack:'s' }
      ]
    },
    options: agentBarOpts({
      tooltip: ctx => {
        const c = by[ctx.dataIndex];
        const tot = c.reached_yes + c.reached_no;
        return ctx.datasetIndex===0
          ? `Reached: ${fmtNum(ctx.raw)} (${pctN(ctx.raw,tot).toFixed(1)}%)`
          : `Not Reached: ${fmtNum(ctx.raw)}`;
      }
    })
  });
}

function renderReachedAgents(rows) {
  const all = aggByAgent(rows).sort((a,b)=>(b.reached_yes+b.reached_no)-(a.reached_yes+a.reached_no));
  const top = all.slice(0, TOP_N);
  const h   = Math.max(240, top.length * 38);
  const wrap = document.getElementById('reached-chart-wrap');
  wrap.style.height = h + 'px';
  document.getElementById('reached-note').textContent =
    all.length > TOP_N ? `Showing top ${TOP_N} of ${all.length} agents by volume — use Table for full list` : '';

  mkChart('chart-reached', {
    type: 'bar',
    data: {
      labels: top.map(a => trunc(a.agent, 22)),
      datasets: [
        { label:'Reached',     data: top.map(a=>a.reached_yes), backgroundColor: top.map(a=>CCOLOR[a.country]||'#94A3B8'), stack:'s' },
        { label:'Not Reached', data: top.map(a=>a.reached_no),  backgroundColor: top.map(a=>h2r(CCOLOR[a.country]||'#94A3B8',.2)), stack:'s' }
      ]
    },
    options: agentBarOpts({
      tooltip: ctx => {
        const a = top[ctx.dataIndex];
        const tot = a.reached_yes + a.reached_no;
        return ctx.datasetIndex===0
          ? `${a.agent} (${a.country})\nReached: ${fmtNum(ctx.raw)} (${pctN(ctx.raw,tot).toFixed(1)}%)`
          : `Not Reached: ${fmtNum(ctx.raw)}`;
      }
    })
  });
}

// ============================================================
// CHART 3: % AT BRANCH  (country / top-agents)
// ============================================================
function renderBranchChart(rows) {
  if (CV.branch === 'agent') renderBranchAgents(rows);
  else renderBranchCountry(rows);
}

function renderBranchCountry(rows) {
  const by = aggByCountry(rows)
    .map(c => ({ ...c, pct: pctN(c.at_branch_yes, c.reached_yes) }))
    .filter(c => c.reached_yes > 0)
    .sort((a,b) => b.pct - a.pct);
  const avg = by.length ? by.reduce((s,c)=>s+c.pct,0)/by.length : 0;
  const h   = Math.max(200, by.length * 38);
  document.getElementById('branch-chart-wrap').style.height = h + 'px';
  document.getElementById('branch-note').textContent = '';

  mkChart('chart-branch-pct', branchBarCfg(by, avg,
    d => `${d.country}: ${d.pct.toFixed(1)}% at branch (${fmtNum(d.at_branch_yes)} of ${fmtNum(d.reached_yes)} reached)`
  ));
}

function renderBranchAgents(rows) {
  const all = aggByAgent(rows)
    .map(a => ({ ...a, pct: pctN(a.at_branch_yes, a.reached_yes) }))
    .filter(a => a.reached_yes > 0)
    .sort((a,b) => b.pct - a.pct);
  const top = all.slice(0, TOP_N);
  const avg = all.length ? all.reduce((s,a)=>s+a.pct,0)/all.length : 0;
  const h   = Math.max(240, top.length * 38);
  document.getElementById('branch-chart-wrap').style.height = h + 'px';
  document.getElementById('branch-note').textContent =
    all.length > TOP_N ? `Showing top ${TOP_N} of ${all.length} agents — use Table for full list` : '';

  mkChart('chart-branch-pct', branchBarCfg(
    top.map(a => ({ ...a, label: trunc(a.agent, 22) })), avg,
    d => `${d.agent} (${d.country}): ${d.pct.toFixed(1)}% at branch`
  ));
}

function branchBarCfg(items, avg, tooltipFn) {
  const labels = items.map(d => d.label || d.country);
  const colors = items.map(d => {
    const base = CCOLOR[d.country]||'#94A3B8';
    return d.pct >= avg ? base : h2r(base, .4);
  });
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label:'% At Branch', data: items.map(d=>d.pct), backgroundColor: colors, borderWidth:0 }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {
        x: { beginAtZero:true, max:100, ticks:{ callback:v=>v+'%' }, grid:{ color:'rgba(128,128,128,.1)' } },
        y: { ticks:{ font:{ size:12 }, autoSkip:false } }
      },
      plugins: {
        legend: { display:false },
        annotation: { annotations: { avg: {
          type:'line', scaleID:'x', value:avg, borderColor:'#6B7280',
          borderWidth:1.5, borderDash:[4,3],
          label:{ content:`Avg ${avg.toFixed(1)}%`, display:true, position:'start', font:{ size:10 } }
        }}},
        tooltip: { callbacks: { label: ctx => ` ${tooltipFn(items[ctx.dataIndex])}` } }
      }
    }
  };
}

// ============================================================
// CHART 5: RESCHEDULED %  (country / top-agents)
// ============================================================
function renderRescheduleChart(rows) {
  if (CV.resched === 'agent') renderReschedAgents(rows);
  else renderReschedCountry(rows);
}

function renderReschedCountry(rows) {
  const by = aggByCountry(rows)
    .map(c => ({ ...c, pct: pctN(c.result_new_appt, c.reached_yes) }))
    .filter(c => c.reached_yes > 0)
    .sort((a,b) => b.pct - a.pct);
  const avg = by.length ? by.reduce((s,c)=>s+c.pct,0)/by.length : 0;
  const h   = Math.max(200, by.length * 38);
  document.getElementById('resched-chart-wrap').style.height = h + 'px';
  document.getElementById('resched-note').textContent = '';

  mkChart('chart-reschedule', reschedBarCfg(by, avg,
    d => `${d.country}: ${d.pct.toFixed(1)}% rescheduled (${fmtNum(d.result_new_appt)} of ${fmtNum(d.reached_yes)} reached)`
  ));
}

function renderReschedAgents(rows) {
  const all = aggByAgent(rows)
    .map(a => ({ ...a, pct: pctN(a.result_new_appt, a.reached_yes) }))
    .filter(a => a.reached_yes > 0)
    .sort((a,b) => b.pct - a.pct);
  const top = all.slice(0, TOP_N);
  const avg = all.length ? all.reduce((s,a)=>s+a.pct,0)/all.length : 0;
  const h   = Math.max(240, top.length * 38);
  document.getElementById('resched-chart-wrap').style.height = h + 'px';
  document.getElementById('resched-note').textContent =
    all.length > TOP_N ? `Showing top ${TOP_N} of ${all.length} agents — use Table for full list` : '';

  mkChart('chart-reschedule', reschedBarCfg(
    top.map(a => ({ ...a, label: trunc(a.agent, 22) })), avg,
    d => `${d.agent} (${d.country}): ${d.pct.toFixed(1)}% rescheduled`
  ));
}

function reschedBarCfg(items, avg, tooltipFn) {
  const labels = items.map(d => d.label || d.country);
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label:'% Rescheduled', data: items.map(d=>d.pct),
        backgroundColor: items.map(d => CCOLOR[d.country]||'#94A3B8'), borderWidth:0 }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {
        x: { beginAtZero:true, ticks:{ callback:v=>v+'%' }, grid:{ color:'rgba(128,128,128,.1)' } },
        y: { ticks:{ font:{ size:12 }, autoSkip:false } }
      },
      plugins: {
        legend: { display:false },
        annotation: { annotations: { avg: {
          type:'line', scaleID:'x', value:avg, borderColor:'#6B7280',
          borderWidth:1.5, borderDash:[4,3],
          label:{ content:`Avg ${avg.toFixed(1)}%`, display:true, position:'start', font:{ size:10 } }
        }}},
        tooltip: { callbacks: { label: ctx => ` ${tooltipFn(items[ctx.dataIndex])}` } }
      }
    }
  };
}

// Shared option builder for horizontal bar charts
function agentBarOpts({ tooltip }) {
  return {
    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    scales: {
      x: { stacked:true, beginAtZero:true, grid:{ color:'rgba(128,128,128,.1)' } },
      y: { stacked:true, ticks:{ font:{ size:12 }, autoSkip:false } }
    },
    plugins: {
      legend: { position:'top', labels:{ font:{ size:11 }, boxWidth:12 } },
      tooltip: { callbacks: { label: ctx => ` ${tooltip(ctx)}` } }
    }
  };
}

// ============================================================
// CHART 2: REASON SPLIT
// ============================================================
let reasonSubView = 'pie';
function setReasonSubView(v) {
  reasonSubView = v;
  document.getElementById('reason-btn-pie').classList.toggle('active', v==='pie');
  document.getElementById('reason-btn-bar').classList.toggle('active', v==='bar');
  renderReasonChart(filtered());
}

function renderReasonChart(rows) {
  const mode = CV.reason || 'overall';
  const wrap = document.getElementById('reason-chart-wrap');
  if (mode === 'overall')  renderReasonOverall(rows, wrap);
  else if (mode === 'country') renderReasonCountry(rows, wrap);
  else if (mode === 'agent')   renderReasonAgents(rows, wrap);
}

function renderReasonOverall(rows, wrap) {
  wrap.style.height = '320px';
  document.getElementById('reason-note').textContent = '';
  const totals = REASON_COLS.map(c => sumField(rows, c));
  const grand  = totals.reduce((s,v)=>s+v, 0);
  if (reasonSubView === 'pie') {
    mkChart('chart-reason', {
      type: 'doughnut',
      data: { labels: REASON_LABELS, datasets: [{ data: totals, backgroundColor: REASON_COLORS, borderWidth:1 }] },
      options: {
        responsive:true, maintainAspectRatio:false,
        plugins: {
          legend: { position:'right', labels:{ font:{ size:11 }, boxWidth:12 } },
          tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmtNum(ctx.raw)} (${pctN(ctx.raw,grand).toFixed(1)}%)` } }
        }
      }
    });
  } else {
    const pairs = REASON_LABELS.map((l,i)=>[l,totals[i],REASON_COLORS[i]]).sort((a,b)=>b[1]-a[1]);
    mkChart('chart-reason', {
      type: 'bar',
      data: {
        labels: pairs.map(p=>p[0]),
        datasets: [{ label:'Count', data: pairs.map(p=>pctN(p[1],grand)), backgroundColor: pairs.map(p=>p[2]), borderWidth:0 }]
      },
      options: {
        indexAxis:'y', responsive:true, maintainAspectRatio:false,
        scales: {
          x: { beginAtZero:true, title:{ display:true, text:'% of reasons', font:{size:11} }, grid:{ color:'rgba(128,128,128,.1)' } },
          y: { ticks:{ font:{ size:11 } } }
        },
        plugins: { legend:{display:false}, tooltip:{ callbacks:{ label: ctx=>` ${ctx.raw.toFixed(1)}%` } } }
      }
    });
  }
}

function renderReasonStacked(items, labelKey, wrap) {
  // items: array of objects with REASON_COLS fields + labelKey field
  const h = Math.max(260, items.length * 38);
  wrap.style.height = h + 'px';
  const datasets = REASON_COLS.map((col, i) => ({
    label: REASON_LABELS[i],
    data: items.map(d => {
      const tot = REASON_COLS.reduce((s,c) => s + (d[c]||0), 0);
      return tot ? +(d[col]/tot*100).toFixed(2) : 0;
    }),
    backgroundColor: REASON_COLORS[i],
    stack: 's'
  }));
  mkChart('chart-reason', {
    type: 'bar',
    data: { labels: items.map(d => d[labelKey]), datasets },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {
        x: { stacked:true, beginAtZero:true, max:100, ticks:{ callback:v=>v+'%' }, grid:{ color:'rgba(128,128,128,.1)' } },
        y: { stacked:true, ticks:{ font:{ size:12 }, autoSkip:false } }
      },
      plugins: {
        legend: { position:'right', labels:{ font:{ size:10 }, boxWidth:10 } },
        tooltip: { callbacks: { label: ctx => {
          const d = items[ctx.dataIndex];
          const col = REASON_COLS[ctx.datasetIndex];
          return ` ${ctx.dataset.label}: ${ctx.raw.toFixed(1)}% (${fmtNum(d[col]||0)})`;
        }}}
      }
    }
  });
}

function renderReasonCountry(rows, wrap) {
  document.getElementById('reason-note').textContent = '';
  const by = aggByCountry(rows)
    .sort((a,b) => REASON_COLS.reduce((s,c) => s+(b[c]||0),0) - REASON_COLS.reduce((s,c) => s+(a[c]||0),0));
  renderReasonStacked(by.map(c => ({...c, _label: c.country})), '_label', wrap);
}

function renderReasonAgents(rows, wrap) {
  const all = aggByAgent(rows)
    .map(a => ({...a, _total: REASON_COLS.reduce((s,c) => s+(a[c]||0),0)}))
    .filter(a => a._total > 0)
    .sort((a,b) => b._total - a._total);
  const top = all.slice(0, TOP_N);
  document.getElementById('reason-note').textContent =
    all.length > TOP_N ? `Showing top ${TOP_N} of ${all.length} agents by reason volume — use Table for full list` : '';
  renderReasonStacked(top.map(a => ({...a, _label: trunc(a.agent, 22)})), '_label', wrap);
}

// ============================================================
// CHART 4: PROBLEM AT BRANCH
// ============================================================
function renderProblemChart(rows) {
  const mode = CV.problem || 'overall';
  const wrap = document.getElementById('problem-chart-wrap');
  if      (mode === 'overall') renderProblemOverall(rows, wrap);
  else if (mode === 'country') renderProblemByGroup(rows, wrap, 'country');
  else if (mode === 'agent')   renderProblemByGroup(rows, wrap, 'agent');
  else if (mode === 'mix')     renderProblemMix(rows, wrap);
}

// ============================================================
// STANDALONE: Problem Type Mix per Agent (full-width card)
// ============================================================
function renderProblemMixStandalone(rows) {
  const wrap = document.getElementById('pb-mix-chart-wrap');
  const byAgent = aggByAgent(rows)
    .map(a => ({ ...a, pbTotal: PB_COLS.reduce((s,c) => s+(a[c]||0), 0) }))
    .filter(a => a.pbTotal > 0)
    .sort((a,b) => b.pbTotal - a.pbTotal);

  const teamTotal = byAgent.reduce((s,a) => s+a.pbTotal, 0);
  // Team-average % per type
  const teamAvg = PB_COLS.map(col => teamTotal ? byAgent.reduce((s,a)=>s+(a[col]||0),0)/teamTotal*100 : 0);

  const h = Math.max(200, byAgent.length * 30);  // outer div is scrollable
  wrap.style.height = h + 'px';
  document.getElementById('pb-mix-note').textContent =
    byAgent.length === 0 ? 'No branch problems recorded in current filter.' : '';

  if (!byAgent.length) { if (CH['chart-pb-mix']) CH['chart-pb-mix'].destroy(); return; }

  const datasets = PB_COLS.map((col, i) => ({
    label: PB_LABELS[i],
    data: byAgent.map(a => a.pbTotal ? +(a[col]/a.pbTotal*100).toFixed(2) : 0),
    backgroundColor: PB_COLORS[i],
    stack: 's'
  }));

  mkChart('chart-pb-mix', {
    type: 'bar',
    data: { labels: byAgent.map(a => trunc(a.agent, 26)), datasets },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {
        x: { stacked: true, beginAtZero: true, max: 100,
             ticks: { callback: v => v+'%' }, grid: { color:'rgba(128,128,128,.1)' } },
        y: { stacked: true, ticks: { font: { size: 11 }, autoSkip: false } }
      },
      plugins: {
        legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 10 } },
        tooltip: { callbacks: { label: ctx => {
          const a = byAgent[ctx.dataIndex];
          const col = PB_COLS[ctx.datasetIndex];
          const myPct  = ctx.raw.toFixed(1);
          const avgPct = teamAvg[ctx.datasetIndex].toFixed(1);
          const diff   = (ctx.raw - teamAvg[ctx.datasetIndex]).toFixed(1);
          const arrow  = ctx.raw > teamAvg[ctx.datasetIndex] ? '▲' : (ctx.raw < teamAvg[ctx.datasetIndex] ? '▼' : '=');
          return ` ${ctx.dataset.label}: ${myPct}%  ${arrow} ${Math.abs(diff)}pp vs team avg ${avgPct}%  (${fmtNum(a[col])} incidents)`;
        }}}
      }
    }
  });
}

// Agent Mix: stacked 100% bar showing each agent's pb_* type breakdown
function renderProblemMix(rows, wrap) {
  const byAgent = aggByAgent(rows)
    .map(a => ({ ...a, pbTotal: PB_COLS.reduce((s,c) => s+(a[c]||0), 0) }))
    .filter(a => a.pbTotal > 0)
    .sort((a,b) => b.pbTotal - a.pbTotal);
  const top = byAgent.slice(0, 20);
  const h   = Math.max(260, top.length * 36);
  wrap.style.height = h + 'px';
  document.getElementById('problem-note').textContent =
    byAgent.length > 20 ? `Showing top 20 of ${byAgent.length} agents by problem count — use Table for full data` : '';

  const datasets = PB_COLS.map((col, i) => ({
    label: PB_LABELS[i],
    data: top.map(a => a.pbTotal ? +(a[col]/a.pbTotal*100).toFixed(2) : 0),
    backgroundColor: PB_COLORS[i],
    stack: 's'
  }));

  // Team-average reference line per column (% of all problems)
  const teamTotal = byAgent.reduce((s,a) => s+a.pbTotal, 0);

  mkChart('chart-pb', {
    type: 'bar',
    data: { labels: top.map(a => trunc(a.agent, 24)), datasets },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {
        x: { stacked: true, beginAtZero: true, max: 100,
             ticks: { callback: v => v+'%' }, grid: { color:'rgba(128,128,128,.1)' } },
        y: { stacked: true, ticks: { font: { size: 11 }, autoSkip: false } }
      },
      plugins: {
        legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 10 } },
        tooltip: { callbacks: { label: ctx => {
          const a = top[ctx.dataIndex];
          const col = PB_COLS[ctx.datasetIndex];
          const teamPct = teamTotal ? (byAgent.reduce((s,x)=>s+(x[col]||0),0)/teamTotal*100).toFixed(1) : '—';
          return ` ${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%  (team avg ${teamPct}%)  · ${fmtNum(a[col])} incidents`;
        }}}
      }
    }
  });
}

function renderProblemOverall(rows, wrap) {
  wrap.style.height = '220px';
  document.getElementById('problem-note').textContent = '';
  let pbCount=0;
  for (const r of rows) {
    if (PB_COLS.some(c=>r[c]>0)) pbCount += r.reached_yes;
  }
  const totalReached = sumField(rows, 'reached_yes');
  const pbTotals = PB_COLS.map(c => sumField(rows,c));
  const pbGrand  = pbTotals.reduce((s,v)=>s+v, 0);
  // kpi-pb-rate and kpi-pb-count elements removed from HTML — skip update
  mkChart('chart-pb', {
    type: 'bar',
    data: {
      labels: PB_LABELS,
      datasets: [{ label:'% of branch problems', data: PB_COLS.map((c,i)=>pctN(pbTotals[i],pbGrand)), backgroundColor:PB_COLORS, borderWidth:0 }]
    },
    options: {
      indexAxis:'y', responsive:true, maintainAspectRatio:false,
      scales: {
        x: { beginAtZero:true, ticks:{ callback:v=>v+'%' }, grid:{ color:'rgba(128,128,128,.1)' } },
        y: { ticks:{ font:{ size:11 } } }
      },
      plugins: { legend:{display:false}, tooltip:{ callbacks:{ label: ctx=>` ${ctx.raw.toFixed(1)}%` } } }
    }
  });
}

function renderProblemByGroup(rows, wrap, groupBy) {
  const agg = groupBy === 'country' ? aggByCountry(rows) : aggByAgent(rows);
  const withPct = agg.map(d => ({
    ...d,
    label: groupBy === 'country' ? d.country : trunc(d.agent||d.country, 22),
    pbTotal: PB_COLS.reduce((s,c) => s+(d[c]||0), 0),
    pct: pctN(PB_COLS.reduce((s,c) => s+(d[c]||0),0), d.reached_yes)
  })).filter(d => d.reached_yes > 0).sort((a,b) => b.pct - a.pct);

  const items = groupBy === 'agent' ? withPct.slice(0, TOP_N) : withPct;
  const avg = withPct.length ? withPct.reduce((s,d) => s+d.pct, 0)/withPct.length : 0;
  const h = Math.max(220, items.length * 38);
  wrap.style.height = h + 'px';

  document.getElementById('problem-note').textContent =
    (groupBy === 'agent' && withPct.length > TOP_N)
      ? `Showing top ${TOP_N} of ${withPct.length} agents by problem rate — use Table for full list` : '';

  mkChart('chart-pb', {
    type: 'bar',
    data: {
      labels: items.map(d => d.label),
      datasets: [{ label:'% Problem Rate',
        data: items.map(d => d.pct),
        backgroundColor: items.map(d => CCOLOR[d.country]||'#94A3B8'), borderWidth:0 }]
    },
    options: {
      indexAxis:'y', responsive:true, maintainAspectRatio:false,
      scales: {
        x: { beginAtZero:true, ticks:{ callback:v=>v+'%' }, grid:{ color:'rgba(128,128,128,.1)' } },
        y: { ticks:{ font:{ size:12 }, autoSkip:false } }
      },
      plugins: {
        legend: { display:false },
        annotation: { annotations: { avg: {
          type:'line', scaleID:'x', value:avg, borderColor:'#6B7280',
          borderWidth:1.5, borderDash:[4,3],
          label:{ content:`Avg ${avg.toFixed(1)}%`, display:true, position:'start', font:{ size:10 } }
        }}},
        tooltip: { callbacks: { label: ctx => {
          const d = items[ctx.dataIndex];
          return ` ${d.pct.toFixed(1)}% (${fmtNum(d.pbTotal)} incidents / ${fmtNum(d.reached_yes)} reached)`;
        }}}
      }
    }
  });
}

// ============================================================
// CHART 6: TREND + AGENT PICKER
// ============================================================
let trendAgents = []; // empty = all agents

function onTrendGroupChange() {
  const group = document.getElementById('trend-group').value;
  const filterWrap = document.getElementById('trend-agent-filter');
  if (group === 'agent') {
    filterWrap.style.display = '';
    rebuildTrendAgentList();
  } else {
    filterWrap.style.display = 'none';
    trendAgents = [];
    updateTrendAgentLabel();
  }
  renderTrend();
}

function rebuildTrendAgentList() {
  const rows = filtered();
  const allAgents = [...new Set(rows.map(r => r.agent_name))].sort();
  const el = document.getElementById('trend-agent-list');
  const q = (document.getElementById('trend-agent-search') || {}).value || '';
  el.innerHTML = '';
  for (const a of allAgents) {
    if (q && !a.toLowerCase().includes(q.toLowerCase())) continue;
    const div = document.createElement('div');
    div.className = 'agent-option'; div.dataset.name = a;
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.checked = trendAgents.includes(a);
    cb.addEventListener('change', () => {
      if (cb.checked) { if (!trendAgents.includes(a)) trendAgents.push(a); }
      else trendAgents = trendAgents.filter(x => x !== a);
      updateTrendAgentLabel();
      renderTrend();
    });
    const lbl = document.createElement('label'); lbl.textContent = a;
    div.appendChild(cb); div.appendChild(lbl);
    el.appendChild(div);
  }
  document.getElementById('trend-agent-dd-count').textContent =
    trendAgents.length ? `${trendAgents.length} selected` : `${allAgents.length} agents`;
}

function updateTrendAgentLabel() {
  const lbl = document.getElementById('trend-agent-label');
  if (!lbl) return;
  if (!trendAgents.length) lbl.textContent = 'All agents';
  else if (trendAgents.length === 1) lbl.textContent = trunc(trendAgents[0], 14);
  else lbl.textContent = `${trendAgents.length} agents`;
  const count = document.getElementById('trend-agent-dd-count');
  if (count) {
    const rows = filtered();
    const total = new Set(rows.map(r => r.agent_name)).size;
    count.textContent = trendAgents.length ? `${trendAgents.length} selected` : `${total} agents`;
  }
}

function toggleTrendAgentDd() {
  const dd = document.getElementById('trend-agent-dd');
  if (!dd) return;
  const isOpen = dd.style.display !== 'none';
  dd.style.display = isOpen ? 'none' : '';
  if (!isOpen) {
    document.getElementById('trend-agent-search').value = '';
    rebuildTrendAgentList();
    document.getElementById('trend-agent-search').focus();
  }
}

function filterTrendAgentDd() {
  rebuildTrendAgentList();
}

function selectAllTrendAgents() {
  const rows = filtered();
  trendAgents = [...new Set(rows.map(r => r.agent_name))].sort();
  rebuildTrendAgentList();
  updateTrendAgentLabel();
  renderTrend();
}

function clearTrendAgents() {
  trendAgents = [];
  rebuildTrendAgentList();
  updateTrendAgentLabel();
  renderTrend();
}

// Close dropdown on outside click
document.addEventListener('click', e => {
  const wrap = document.getElementById('trend-agent-filter');
  if (wrap && !wrap.contains(e.target)) {
    const dd = document.getElementById('trend-agent-dd');
    if (dd) dd.style.display = 'none';
  }
});

function renderTrend() {
  const metric = document.getElementById('trend-metric').value;
  const group  = document.getElementById('trend-group').value;
  const rows   = filtered();
  let periods, getPeriod;
  if (S.tab === 'monthly') {
    const mn = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'};
    getPeriod = r => `${r.year}-${String(r.month).padStart(2,'0')}`;
    periods   = [...new Set(rows.map(getPeriod))].sort();
  } else {
    getPeriod = r => `${r.year}-W${String(r.week).padStart(2,'0')}`;
    periods   = [...new Set(rows.map(getPeriod))].sort();
  }

  let groupKeys;
  if (group === 'country') {
    groupKeys = [...new Set(rows.map(r=>r.country))].sort();
  } else {
    const allAgents = [...new Set(rows.map(r=>r.agent_name))].sort();
    const validSel = trendAgents.filter(a => allAgents.includes(a));
    groupKeys = validSel.length > 0 ? validSel : allAgents;
    // Keep picker label in sync
    updateTrendAgentLabel();
  }

  // Denominator rules:
  //   total_submissions → raw count (no division)
  //   reached_yes       → total_submissions (% reached = reached/total calls)
  //   all others        → reached_yes (at_branch_yes, result_new_appt, reason_problem_branch, …)
  const isPercentage = metric !== 'total_submissions';
  const denomField   = metric === 'reached_yes' ? 'total_submissions' : 'reached_yes';

  const aggMap = {};
  for (const r of rows) {
    const gk = group==='country' ? r.country : r.agent_name;
    const p  = getPeriod(r);
    if (!aggMap[gk]) aggMap[gk] = {};
    if (!aggMap[gk][p]) aggMap[gk][p] = { val:0, total:0 };
    aggMap[gk][p].val   += r[metric]||0;
    if (isPercentage) aggMap[gk][p].total += r[denomField]||0;
  }

  const datasets = groupKeys.map((gk,i) => {
    const color = group==='country' ? CCOLOR[gk] : (CCOLOR[COUNTRIES[i%COUNTRIES.length]]||'#6B7280');
    return {
      label: gk,
      data: periods.map(p => {
        const a = aggMap[gk] && aggMap[gk][p];
        if (!a) return null;
        return isPercentage && a.total ? +(a.val/a.total*100).toFixed(2) : a.val;
      }),
      borderColor:color, backgroundColor:h2r(color,.08),
      tension:.35, fill:false, pointRadius:3, borderWidth:2
    };
  });

  const mn2 = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'};
  const displayLabels = periods.map(p => {
    if (S.tab==='monthly') { const [y,m]=p.split('-'); return `${mn2[+m]}-${y.slice(2)}`; }
    return p.replace('-W',' W');
  });

  mkChart('chart-trend', {
    type: 'line',
    data: { labels: displayLabels, datasets },
    options: {
      responsive:true, maintainAspectRatio:false,
      interaction: { mode:'index', intersect:false },
      scales: {
        x: { grid:{ color:'rgba(128,128,128,.08)' }, ticks:{ font:{ size:10 } } },
        y: { beginAtZero:true, ticks:{ callback:v=>isPercentage?v.toFixed(1)+'%':fmtNum(v), font:{ size:11 } }, grid:{ color:'rgba(128,128,128,.1)' } }
      },
      plugins: {
        legend: { display: group==='country', position:'top', labels:{ font:{ size:11 }, boxWidth:12, usePointStyle:true } },
        tooltip: { callbacks: { label: ctx => ctx.raw==null?null:` ${ctx.dataset.label}: ${isPercentage?ctx.raw.toFixed(1)+'%':fmtNum(ctx.raw)}` } },
        datalabels: {
          display: 'auto',          // auto-hide labels that would overlap
          align: 'top', offset: 3, clamp: true,
          formatter: v => v==null ? null : (isPercentage ? v.toFixed(1)+'%' : fmtNum(v)),
          font: { size: 9, weight: '600' },
          color: ctx => ctx.dataset.borderColor
        }
      }
    }
  });
}

// ============================================================
// MINI-TABLES  (inside chart cards)
// ============================================================
function buildMT(chart, rows) {
  const byAgent = aggByAgent(rows);
  let data;
  if (chart === 'reached') {
    data = byAgent.map(a => ({
      agent: a.agent, country: a.country,
      reached_yes: a.reached_yes, reached_no: a.reached_no,
      total: a.reached_yes + a.reached_no,
      pct: pctN(a.reached_yes, a.reached_yes + a.reached_no)
    }));
  } else if (chart === 'branch') {
    data = byAgent.map(a => ({
      agent: a.agent, country: a.country,
      at_branch_yes: a.at_branch_yes, at_branch_no: a.at_branch_no,
      total: a.reached_yes,
      pct: pctN(a.at_branch_yes, a.reached_yes)
    })).filter(d => d.total > 0);
  } else if (chart === 'resched') {
    data = byAgent.map(a => ({
      agent: a.agent, country: a.country,
      rescheduled: a.result_new_appt,
      total: a.reached_yes,
      pct: pctN(a.result_new_appt, a.reached_yes)
    })).filter(d => d.total > 0);
  } else if (chart === 'reason') {
    data = byAgent.map(a => {
      const total = REASON_COLS.reduce((s,c) => s+(a[c]||0), 0);
      const entry = { agent: a.agent, country: a.country, total };
      REASON_COLS.forEach(c => { entry[c] = a[c]||0; });
      return entry;
    }).filter(d => d.total > 0);
  } else if (chart === 'problem') {
    data = byAgent.map(a => {
      const pb_total = PB_COLS.reduce((s,c) => s+(a[c]||0), 0);
      const entry = {
        agent: a.agent, country: a.country,
        submissions: a.total_submissions,
        pb_total,
        pct: pctN(pb_total, a.reached_yes)
      };
      PB_COLS.forEach(c => { entry[c] = a[c]||0; });
      return entry;
    }).filter(d => d.submissions > 0);
  }
  MT[chart].data = data;
}

function renderMTUI(chart) {
  const mt = MT[chart];
  let data = [...mt.data];

  // filter
  if (mt.filter) {
    const q = mt.filter.toLowerCase();
    data = data.filter(d => d.agent.toLowerCase().includes(q) || d.country.toLowerCase().includes(q));
  }

  // sort
  data.sort((a,b) => {
    const av = typeof a[mt.sortCol]==='number' ? a[mt.sortCol] : 0;
    const bv = typeof b[mt.sortCol]==='number' ? b[mt.sortCol] : 0;
    if (typeof a[mt.sortCol]==='string') return a[mt.sortCol].localeCompare(b[mt.sortCol])*mt.sortDir;
    return (av-bv)*mt.sortDir;
  });

  const infoEl = document.getElementById(`${chart}-tbl-info`);
  if (infoEl) infoEl.textContent = `${data.length} agent${data.length!==1?'s':''}`;

  // avg for conditional formatting
  const pctVals = data.map(d=>d.pct).filter(v=>v>0);
  const avg = pctVals.length ? pctVals.reduce((s,v)=>s+v,0)/pctVals.length : 0;

  const tbody = document.getElementById(`${chart}-tbl-body`);
  if (!tbody) return;

  if (!data.length) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;opacity:.4;font-size:12px">No data</td></tr>`;
    return;
  }

  const badge = c => `<span class="badge" style="background:${h2r(CCOLOR[c]||'#888',.12)};color:${CCOLOR[c]||'#888'}">${c}</span>`;

  tbody.innerHTML = data.map(d => {
    const pCls = d.pct > 0 ? (d.pct >= avg ? 'pct-g' : 'pct-r') : '';
    if (chart === 'reached') {
      return `<tr>
        <td><span class="nm" title="${d.agent}">${d.agent}</span></td>
        <td>${badge(d.country)}</td>
        <td>${fmtNum(d.reached_yes)}</td>
        <td>${fmtNum(d.reached_no)}</td>
        <td>${fmtNum(d.total)}</td>
        <td class="${pCls}">${d.pct.toFixed(1)}%</td>
      </tr>`;
    } else if (chart === 'branch') {
      return `<tr>
        <td><span class="nm" title="${d.agent}">${d.agent}</span></td>
        <td>${badge(d.country)}</td>
        <td>${fmtNum(d.at_branch_yes)}</td>
        <td>${fmtNum(d.at_branch_no)}</td>
        <td>${fmtNum(d.total)}</td>
        <td class="${pCls}">${d.pct.toFixed(1)}%</td>
      </tr>`;
    } else if (chart === 'resched') {
      return `<tr>
        <td><span class="nm" title="${d.agent}">${d.agent}</span></td>
        <td>${badge(d.country)}</td>
        <td>${fmtNum(d.rescheduled)}</td>
        <td>${fmtNum(d.total)}</td>
        <td class="${pCls}">${d.pct.toFixed(1)}%</td>
      </tr>`;
    } else if (chart === 'reason') {
      return `<tr>
        <td><span class="nm" title="${d.agent}">${d.agent}</span></td>
        <td>${badge(d.country)}</td>
        <td><strong>${fmtNum(d.total)}</strong></td>
        ${REASON_COLS.map(c => `<td>${fmtNum(d[c]||0)}</td>`).join('')}
      </tr>`;
    } else {
      const pbCls = d.pct > 0 ? (d.pct >= avg ? 'pct-g' : 'pct-r') : '';
      return `<tr>
        <td><span class="nm" title="${d.agent}">${d.agent}</span></td>
        <td>${badge(d.country)}</td>
        <td>${fmtNum(d.submissions)}</td>
        <td>${fmtNum(d.pb_total)}</td>
        <td class="${pbCls}">${d.pct.toFixed(1)}%</td>
        ${PB_COLS.map(c => `<td>${fmtNum(d[c]||0)}</td>`).join('')}
      </tr>`;
    }
  }).join('');

  // update sort indicators
  document.querySelectorAll(`#${chart}-tbl-wrap .mt th`).forEach(th => {
    const col = th.getAttribute('onclick').match(/'([^']+)'\)$/)?.[1];
    th.classList.toggle('srt', col === mt.sortCol);
    const si = th.querySelector('.si');
    if (si) si.textContent = col===mt.sortCol ? (mt.sortDir===-1?'↓':'↑') : '↕';
  });
}

function filterMT(chart) {
  MT[chart].filter = document.getElementById(`${chart}-q`).value;
  renderMTUI(chart);
}

function sortMT(chart, col) {
  const mt = MT[chart];
  if (mt.sortCol === col) mt.sortDir = -mt.sortDir;
  else { mt.sortCol = col; mt.sortDir = -1; }
  renderMTUI(chart);
}

// ============================================================
// AGENT PERFORMANCE TABLE (bottom)
// ============================================================
const TABLE_COLS = [
  { key:'agent',           label:'Agent',          type:'text'  },
  { key:'country',         label:'Country',        type:'badge' },
  { key:'total_submissions', label:'Submissions',  type:'num'   },
  { key:'reached_yes',     label:'Reached',        type:'num'   },
  { key:'reached_no',      label:'Not Reached',    type:'num'   },
  { key:'pct_reached',     label:'% Reached',      type:'pct'   },
  { key:'at_branch_yes',   label:'At Branch',      type:'num'   },
  { key:'at_branch_no',    label:'Not At Branch',  type:'num'   },
  { key:'pct_branch',      label:'% At Branch',    type:'pct2'  },
  { key:'result_new_appt', label:'Rescheduled',    type:'num'   },
  { key:'pct_reschedule',  label:'% Rescheduled',  type:'pct'   }
];

let tblSortCol='total_submissions', tblSortDir=-1;

function renderTable(rows) {
  const byAgent = aggByAgent(rows);
  const td = byAgent.map(a => {
    const tot = a.total_submissions;
    return {
      agent: a.agent, country: a.country,
      total_submissions: tot,
      reached_yes: a.reached_yes, reached_no: a.reached_no,
      pct_reached: tot ? +(a.reached_yes/tot*100).toFixed(1) : null,
      at_branch_yes: a.at_branch_yes, at_branch_no: a.at_branch_no,
      pct_branch: a.reached_yes ? +(a.at_branch_yes/a.reached_yes*100).toFixed(1) : null,
      result_new_appt: a.result_new_appt,
      pct_reschedule: a.reached_yes ? +(a.result_new_appt/a.reached_yes*100).toFixed(1) : null
    };
  });

  td.sort((a,b) => {
    const av = typeof a[tblSortCol]==='number' ? a[tblSortCol] : (a[tblSortCol]||'').toString();
    const bv = typeof b[tblSortCol]==='number' ? b[tblSortCol] : (b[tblSortCol]||'').toString();
    if (typeof av==='string') return av.localeCompare(bv)*tblSortDir;
    return ((av||0)-(bv||0))*tblSortDir;
  });

  const pctRVals = td.map(d=>d.pct_reached).filter(v=>v!=null);
  const avgR = pctRVals.length ? pctRVals.reduce((s,v)=>s+v,0)/pctRVals.length : 0;
  const pctSVals = td.map(d=>d.pct_reschedule).filter(v=>v!=null);
  const avgS = pctSVals.length ? pctSVals.reduce((s,v)=>s+v,0)/pctSVals.length : 0;

  const thead = document.getElementById('table-head');
  thead.innerHTML = '<tr>' + TABLE_COLS.map(c => {
    const sorted = c.key===tblSortCol;
    // Two stacked mini-arrows: active one is solid, inactive is faded
    const upActive   = sorted && tblSortDir===1;
    const downActive = sorted && tblSortDir===-1;
    const icon = `<span class="sort-icon" aria-hidden="true">`
      + `<span style="opacity:${upActive?1:.3};color:${upActive?'#3B82F6':'inherit'}">▲</span>`
      + `<span style="opacity:${downActive?1:.3};color:${downActive?'#3B82F6':'inherit'}">▼</span>`
      + `</span>`;
    return `<th class="${sorted?'sorted':''}" onclick="sortTable('${c.key}')" title="Sort by ${c.label}">${c.label}${icon}</th>`;
  }).join('') + '</tr>';

  document.getElementById('table-count').textContent = `${td.length} agents`;
  const tbody = document.getElementById('table-body');
  if (!td.length) { tbody.innerHTML=`<tr><td colspan="${TABLE_COLS.length}" class="empty-state">No data</td></tr>`; return; }

  tbody.innerHTML = td.map(d => {
    const cells = TABLE_COLS.map(c => {
      let val = d[c.key], cls = '';
      if (c.type==='badge') {
        return `<td><span class="badge" style="background:${h2r(CCOLOR[val]||'#888',.15)};color:${CCOLOR[val]||'#888'}">${val}</span></td>`;
      }
      if (c.type==='pct') {
        const n = val;
        cls = n!=null ? (n>=(c.key==='pct_reached'?avgR:avgS)?'cell-green':'cell-red') : 'cell-neutral';
        return `<td class="${cls}">${n!=null?n.toFixed(1)+'%':'—'}</td>`;
      }
      if (c.type==='pct2') return `<td>${val!=null?val.toFixed(1)+'%':'—'}</td>`;
      if (c.type==='num')  return `<td>${fmtNum(val||0)}</td>`;
      return `<td>${val||''}</td>`;
    });
    return `<tr>${cells.join('')}</tr>`;
  }).join('');
}

function sortTable(col) {
  if (tblSortCol===col) tblSortDir=-tblSortDir; else { tblSortCol=col; tblSortDir=-1; }
  renderTable(filtered());
}

// ============================================================
// MAIN RENDER
// ============================================================
function render() {
  const rows = filtered();
  if (CV.reached === 'table') { buildMT('reached', rows); renderMTUI('reached'); }
  else renderReachedChart(rows);
  if (CV.branch  === 'table') { buildMT('branch', rows);  renderMTUI('branch');  }
  else renderBranchChart(rows);
  if (CV.resched === 'table') { buildMT('resched', rows);  renderMTUI('resched'); }
  else renderRescheduleChart(rows);
  if (CV.reason  === 'table') { buildMT('reason', rows);   renderMTUI('reason');  }
  else renderReasonChart(rows);
  if (CV.problem === 'table') { buildMT('problem', rows);  renderMTUI('problem'); }
  else renderProblemChart(rows);
  renderProblemMixStandalone(rows);
  renderTrend();
  renderTable(rows);
}

// ============================================================
// INIT
// ============================================================
(function init() {
  // Data-label plugin auto-registers globally; keep it OFF everywhere by
  // default — only the Trend chart re-enables it in its own options.
  if (window.ChartDataLabels) {
    Chart.register(ChartDataLabels);
    Chart.defaults.set('plugins.datalabels', { display: false });
  }
  buildYearPills();
  buildCountryPills();
  buildAgentList();
  buildMonthSelects();
  buildWeekSelects();
  render();
  onTrendGroupChange();  // trend defaults to "By Agent" — reveal the agent picker
})();
</script>
</body>
</html>"""

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = len(html.encode()) // 1024
print(f"Dashboard written: {OUTPUT_PATH}")
print(f"File size: {size_kb} KB")
