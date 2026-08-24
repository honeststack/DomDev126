#!/usr/bin/env python3
"""Astradive static page generator.

Reads the hand-authored `index.html`, lifts its <header> and <footer> so every
sub-page shares one navigation chrome, then writes the service / company /
legal pages from the data structures below.

    python build.py            # write all pages
    python build.py --list     # show what would be written

Editing content: change PAGES / SERVICES below and re-run. Editing chrome:
change index.html and re-run — sub-pages pick it up automatically.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"


# --------------------------------------------------------------------------- #
# chrome extraction                                                            #
# --------------------------------------------------------------------------- #

def load_chrome():
    """Pull header + footer markup out of index.html and localise their links."""
    src = INDEX.read_text(encoding="utf-8")

    header = re.search(r"<header class=\"header\".*?</header>", src, re.S)
    footer = re.search(r"<footer class=\"footer\">.*?</footer>", src, re.S)
    if not header or not footer:
        sys.exit("build: could not find <header>/<footer> in index.html")

    def localise(markup):
        # On a sub-page, homepage anchors must point back at index.html.
        markup = markup.replace('href="#top"', 'href="index.html"')
        markup = re.sub(r'href="#(?!\")', 'href="index.html#', markup)
        return markup

    return localise(header.group(0)), localise(footer.group(0))


# --------------------------------------------------------------------------- #
# small markup helpers                                                         #
# --------------------------------------------------------------------------- #

def crumbs(*trail):
    """trail: (label, href) pairs; last item renders as plain text."""
    out = ['<nav class="crumbs" aria-label="Breadcrumb">', '<a href="index.html">Home</a>']
    for label, href in trail:
        out.append("<span>/</span>")
        out.append(f'<a href="{href}">{label}</a>' if href else f"<b>{label}</b>")
    out.append("</nav>")
    return "\n      ".join(out)


def facts(items):
    cells = "\n        ".join(
        f"<div><b>{k}</b><span>{v}</span></div>" for k, v in items
    )
    return f'<div class="facts reveal">\n        {cells}\n      </div>'


def checklist(items):
    lis = "\n        ".join(f"<li>{i}</li>" for i in items)
    return f'<ul class="checklist reveal">\n        {lis}\n      </ul>'


def cards(items):
    """items: (title, body) pairs -> service capability grid."""
    out = []
    for title, body in items:
        out.append(
            '<article class="card reveal">'
            f"<h3>{title}</h3><p>{body}</p></article>"
        )
    return f'<div class="svc-grid">\n        {chr(10).join(out)}\n      </div>'


def faq(items):
    blocks = "\n        ".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items
    )
    return f'<div class="faq reveal">\n        {blocks}\n      </div>'


def related(slugs, catalogue):
    out = []
    for slug in slugs:
        page = catalogue[slug]
        out.append(
            f'<a href="{slug}.html"><b>{page["nav"]}</b>'
            f'<span>{page["blurb"]}</span></a>'
        )
    return f'<div class="related reveal">\n        {chr(10).join(out)}\n      </div>'


def section(inner, eyebrow=None, heading=None, lead=None, cls="section", sid=None):
    head = ""
    if eyebrow or heading or lead:
        head = '<header class="section-head reveal">'
        if eyebrow:
            head += f'<span class="eyebrow">{eyebrow}</span>'
        if heading:
            head += f"<h2>{heading}</h2>"
        if lead:
            head += f'<p class="lead">{lead}</p>'
        head += "</header>\n      "
    ident = f' id="{sid}"' if sid else ""
    return (
        f'<section class="{cls}"{ident}>\n    <div class="shell">\n      '
        f"{head}{inner}\n    </div>\n  </section>"
    )


CTA_BAND = """<section class="section">
    <div class="shell">
      <div class="cta-inner reveal">
        <h2>Let&rsquo;s scope it together</h2>
        <p class="lead" style="text-align:center">Send the problem and the constraints. You get a scope, a timeline and a number &mdash; usually inside two working days.</p>
        <div class="hero-cta">
          <a href="schedule-meeting.html" class="btn btn-primary">Book a strategy call</a>
          <a href="lets-connect.html" class="btn btn-ghost">Send a brief</a>
        </div>
      </div>
    </div>
  </section>"""


# --------------------------------------------------------------------------- #
# page shell                                                                   #
# --------------------------------------------------------------------------- #

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta name="theme-color" content="#05070f" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Astradive" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="assets/styles.css" />
<link rel="stylesheet" href="assets/pages.css" />
</head>
<body>
<a href="#main" class="sr-only">Skip to main content</a>

{header}

<main id="main">
  <section class="page-hero">
    <div class="glow glow-a" aria-hidden="true"></div>
    <div class="shell">
      {crumbs}
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      {hero_extra}
    </div>
  </section>

  {body}
</main>

{footer}

<script src="assets/app.js" defer></script>
</body>
</html>
"""


def render(slug, *, title, desc, eyebrow, h1, lead, body, trail, hero_extra="", chrome=None):
    header, footer = chrome
    html = SHELL.format(
        title=title,
        desc=desc,
        header=header,
        footer=footer,
        crumbs=crumbs(*trail),
        eyebrow=eyebrow,
        h1=h1,
        lead=lead,
        hero_extra=hero_extra,
        body=body,
    )
    (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")
    return slug


HERO_CTA = """<div class="hero-cta">
        <a href="schedule-meeting.html" class="btn btn-primary">Book a strategy call</a>
        <a href="lets-connect.html" class="btn btn-ghost">Send a brief</a>
      </div>"""


def two_col(left, aside_title, aside_body, aside_points):
    points = "".join(f"<li>{p}</li>" for p in aside_points)
    return f"""<section class="section">
    <div class="shell two-col">
      <div>{left}</div>
      <aside class="aside-card reveal">
        <h3>{aside_title}</h3>
        <p>{aside_body}</p>
        <ul>{points}</ul>
        <a href="schedule-meeting.html" class="btn btn-primary">Book a call</a>
      </aside>
    </div>
  </section>"""


# --------------------------------------------------------------------------- #
# content: service pages                                                       #
# --------------------------------------------------------------------------- #

SERVICES = {
    "mvp-development": {
        "nav": "MVP Development",
        "blurb": "Launchable product in 8-12 weeks",
        "h1": "MVPs that survive their own success",
        "lead": "A scoped, production-grade first version in 8&ndash;12 weeks &mdash; architected so the version that finds traction is the one you keep building on.",
        "desc": "MVP development in 8-12 weeks: scoped discovery, production architecture, weekly demos and a launch you can build on.",
        "facts": [("Timeline", "8&ndash;12 weeks to launch"),
                  ("Squad", "PM, 2&ndash;3 engineers, designer"),
                  ("Model", "Fixed scope or monthly squad")],
        "cards": [
            ("Scope you can defend", "We cut the feature list to what proves the riskiest assumption, and write down what we are deliberately not building."),
            ("Production from day one", "CI, migrations, auth, logging and error tracking ship in week two &mdash; not after the first outage."),
            ("Weekly demos", "A working build every Friday. You steer with what you see, not with a status document."),
            ("Instrumented launch", "Analytics and funnels are part of the build, so the first month of usage actually tells you something."),
            ("Clean handover", "Repos, runbooks and architecture notes are yours. Keep us on or take it in-house."),
        ],
        "deliverables": [
            "Scoped product definition with an explicit non-goals list",
            "Clickable prototype of the core flow before code starts",
            "Deployed staging and production environments",
            "The MVP itself, in your cloud account and your repos",
            "Analytics, error tracking and uptime monitoring wired up",
            "Architecture decision record and onboarding runbook",
        ],
        "faq": [
            ("What does an MVP cost?", "Most land between $40k and $120k depending on integrations, compliance and whether design starts from scratch. You get a fixed number after the scoping session, not a range."),
            ("Do we own the code?", "Yes &mdash; repos, infrastructure and IP are yours from the first commit, in your accounts."),
            ("What if the scope changes mid-build?", "Expected. We re-cut the backlog at every sprint boundary and tell you plainly what a change costs in days."),
            ("Can you work with our engineers?", "Often the best setup. We pair with your team and hand over gradually rather than building in a silo."),
        ],
        "related": ["ui-ux-designing", "product-development", "enterprise-ai-solutions"],
    },
    "enterprise-ai-solutions": {
        "nav": "Enterprise AI Solutions",
        "blurb": "Assistants, agents and document AI",
        "h1": "Enterprise AI that passes review",
        "lead": "Retrieval assistants, document pipelines and agentic workflows wired into the systems your teams already use &mdash; with evaluation and access control built in, not bolted on.",
        "desc": "Enterprise AI: RAG assistants, document intelligence and agent workflows with evaluation harnesses, access control and cost governance.",
        "facts": [("First value", "4&ndash;8 weeks to pilot"),
                  ("Deploys to", "Your cloud or VPC"),
                  ("Comes with", "Eval harness + cost dashboard")],
        "cards": [
            ("Retrieval that cites", "Grounded answers with sources, chunking tuned to your documents, and refusal behaviour when the corpus does not know."),
            ("Document intelligence", "Extraction and classification pipelines for contracts, claims and invoices, with human review where it matters."),
            ("Agentic workflows", "Multi-step automations with tool access, guardrails, timeouts and a full audit trail of every action."),
            ("Evaluation harness", "A graded test set per use case, so a model or prompt change is a measurable decision rather than a gamble."),
            ("Cost and access governance", "Per-team budgets, rate limits, PII handling and role-based access reviewed with your security group."),
        ],
        "deliverables": [
            "Use-case assessment with expected accuracy and cost per request",
            "Ingestion and retrieval pipeline over your own corpus",
            "Evaluation suite with a baseline score and regression gate",
            "Deployment in your cloud, behind your identity provider",
            "Observability: traces, token spend, latency and failure modes",
            "Rollout plan with human-in-the-loop stages",
        ],
        "faq": [
            ("Does our data train anyone's model?", "No. We deploy in your account and use providers under no-training terms; sensitive corpora can stay inside your VPC."),
            ("Which models do you use?", "Whichever survives the evals for your task and budget &mdash; frontier hosted models, smaller ones for narrow steps, open-weight where residency demands it."),
            ("How do you stop it making things up?", "Grounding plus refusal behaviour, then a graded eval set that measures how often it happens before and after each change."),
            ("Can it work with our legacy systems?", "Yes. Most projects spend more time on connectors and permissions than on the model itself."),
        ],
        "related": ["data-analytics", "cloud-engineering", "mvp-development"],
    },
    "data-analytics": {
        "nav": "Data Analytics",
        "blurb": "Pipelines, warehouse and BI",
        "h1": "Numbers your team stops arguing about",
        "lead": "Warehouses, transformation pipelines and dashboards with defined metrics and tested models &mdash; so two people asking the same question get the same answer.",
        "desc": "Data analytics engineering: warehouse design, dbt transformation, tested metric layers and dashboards teams trust.",
        "facts": [("First dashboard", "3&ndash;5 weeks"),
                  ("Stack", "dbt, Airflow, Snowflake/BigQuery"),
                  ("Includes", "Metric definitions + tests")],
        "cards": [
            ("Warehouse design", "Modelled layers from raw ingestion to reporting marts, with a naming convention your analysts can predict."),
            ("Reliable pipelines", "Orchestrated, idempotent jobs with freshness checks and alerts that name the owner, not just the failure."),
            ("A metric layer", "One definition of revenue, churn and activation, versioned in code and reused by every dashboard."),
            ("Dashboards people open", "Few, focused views built around decisions, not a wall of charts nobody reads."),
            ("Data quality tests", "Uniqueness, nullability and business-rule tests that block bad data before it reaches a chart."),
        ],
        "deliverables": [
            "Source audit and ingestion plan across your systems",
            "Warehouse with staging, core and mart layers",
            "Orchestrated transformation project with tests in CI",
            "Documented metric definitions signed off by the business",
            "Dashboard set for the questions you asked for",
            "Runbook covering backfills, failures and onboarding",
        ],
        "faq": [
            ("We already have a warehouse. Can you fix it?", "Common starting point. We audit what exists, keep what works, and migrate incrementally rather than proposing a rebuild."),
            ("Which BI tool?", "Whatever your team already uses. We care that the metric layer is upstream of the tool so switching stays cheap."),
            ("How do you handle PII?", "Classified at ingestion, masked in non-production, access granted by role and reviewed with your compliance owner."),
        ],
        "related": ["enterprise-ai-solutions", "cloud-engineering", "product-development"],
    },
    "cloud-engineering": {
        "nav": "Cloud Engineering",
        "blurb": "IaC, CI/CD and observability",
        "h1": "Boring deploys, predictable bills",
        "lead": "Infrastructure as code, pipelines that ship on merge, and observability that tells you which change broke things &mdash; on AWS, Azure or Google Cloud.",
        "desc": "Cloud engineering: Terraform infrastructure, CI/CD pipelines, Kubernetes, observability and cloud cost reduction.",
        "facts": [("Typical engagement", "4&ndash;10 weeks"),
                  ("Clouds", "AWS, Azure, GCP"),
                  ("Outcome", "Faster releases, lower spend")],
        "cards": [
            ("Infrastructure as code", "Every environment reproducible from Terraform, reviewed like application code, with no console-only resources."),
            ("Delivery pipelines", "Build, test, scan and deploy on merge, with one-command rollback and environments that match."),
            ("Kubernetes when it earns it", "Right-sized platform choices &mdash; sometimes containers on managed compute beats a cluster nobody wants to operate."),
            ("Observability", "Metrics, traces, structured logs and alerts routed to the people who can act on them."),
            ("Cost engineering", "Rightsizing, autoscaling, storage tiering and commitment planning, with the savings reported monthly."),
        ],
        "deliverables": [
            "Reviewed architecture and network topology",
            "Terraform modules covering all environments",
            "CI/CD pipelines with automated tests and rollback",
            "Monitoring, alerting and on-call runbooks",
            "Security baseline: secrets, IAM, backups, patching",
            "Cost report with prioritised savings actions",
        ],
        "faq": [
            ("Can you migrate us between clouds?", "Yes, incrementally and with a rollback path at every stage. Big-bang migrations are where the outages live."),
            ("Do you take on-call?", "We can cover a transition period and train your team into it, but the goal is always that you own the platform."),
            ("How much can we realistically save?", "Teams that have never tuned spend commonly see 25&ndash;45%. We measure first and only then promise a number."),
        ],
        "related": ["data-analytics", "enterprise-ai-solutions", "product-development"],
    },
    "ios-android-app-development": {
        "nav": "iOS &amp; Android Apps",
        "blurb": "Native-feeling mobile products",
        "h1": "Mobile apps that feel native",
        "lead": "One product, both platforms, shared business logic &mdash; with offline behaviour, push, deep links and store releases we handle for you.",
        "desc": "iOS and Android app development: native and cross-platform builds with offline support, push, deep links and managed store releases.",
        "facts": [("First build in stores", "6&ndash;10 weeks"),
                  ("Approach", "Native or React Native, per case"),
                  ("Includes", "Store submission + release ops")],
        "cards": [
            ("The right platform call", "React Native when the product is mostly screens and sync; Swift and Kotlin when hardware, performance or platform features lead."),
            ("Offline first", "Local state, queued writes and conflict handling, so a lift or a tunnel does not lose someone's work."),
            ("Release engineering", "Signing, beta tracks, phased rollouts and crash reporting set up once and reused every release."),
            ("Design that respects the OS", "Navigation, gestures and typography that follow platform conventions instead of fighting them."),
            ("Backend included", "APIs, push infrastructure and admin tooling built alongside the app by the same team."),
        ],
        "deliverables": [
            "Platform and architecture recommendation with reasoning",
            "iOS and Android builds on internal test tracks",
            "Backend APIs, push and deep-link handling",
            "Store listings, screenshots and submission through review",
            "Crash reporting, analytics and release checklist",
            "Handover docs for signing keys and release process",
        ],
        "faq": [
            ("Native or cross-platform?", "We decide from your feature list, not from preference. Heavy media, background hardware or platform-specific UX pushes us native."),
            ("Can you take over an existing app?", "Yes. We start with a codebase audit and a stabilisation sprint before adding features."),
            ("Who handles app review rejections?", "We do, including the resubmission and the back-and-forth with the review team."),
        ],
        "related": ["ui-ux-designing", "mvp-development", "product-development"],
    },
    "ui-ux-designing": {
        "nav": "UI/UX Design",
        "blurb": "Research, flows, design systems",
        "h1": "Design that survives contact with code",
        "lead": "Research, flows and a component system engineers can build from &mdash; delivered as tokens and states, not a picture of a screen.",
        "desc": "UI/UX design: user research, product flows, design systems and prototypes handed over as tokens and component states.",
        "facts": [("Discovery", "1&ndash;2 weeks"),
                  ("Deliverable", "Design system + prototype"),
                  ("Handover", "Tokens engineers can import")],
        "cards": [
            ("Research with real users", "Interviews and usability sessions on the flows that carry your revenue, summarised into decisions."),
            ("Flows before pixels", "We map the journey, the edge cases and the empty states before anything gets styled."),
            ("Design systems", "Tokens, components and states documented so the tenth screen costs a fraction of the first."),
            ("Prototypes that answer questions", "Clickable enough to test with users and to settle internal debates before code."),
            ("Accessibility as default", "Contrast, focus order, keyboard paths and reduced-motion behaviour specified up front."),
        ],
        "deliverables": [
            "Research findings with prioritised usability issues",
            "End-to-end flows including error and empty states",
            "High-fidelity screens for every core surface",
            "Component library with variants and interaction states",
            "Design tokens exported for your codebase",
            "Annotated handover for engineering",
        ],
        "faq": [
            ("Can you work from our brand guidelines?", "Yes &mdash; we extend an existing brand into a product system rather than restyling it."),
            ("Do you do design-only engagements?", "Yes, though the strongest results come when the designers sit with the engineers building it."),
            ("How do you test with users pre-launch?", "Prototype sessions with five to eight people from your target segment; enough to find the blocking problems."),
        ],
        "related": ["mvp-development", "ios-android-app-development", "product-development"],
    },
    "product-development": {
        "nav": "Product Development",
        "blurb": "An embedded senior squad",
        "h1": "An embedded squad that owns outcomes",
        "lead": "A senior team working to your roadmap month over month &mdash; discovery, delivery and the reliability work that keeps a product alive after launch.",
        "desc": "Embedded product development squads: roadmap ownership, continuous delivery and post-launch iteration with senior engineers.",
        "facts": [("Cadence", "Two-week sprints"),
                  ("Squad", "PM, designer, 2&ndash;4 engineers"),
                  ("Commitment", "Monthly, 30 days notice")],
        "cards": [
            ("Continuous discovery", "Every cycle starts with evidence &mdash; usage data, support tickets, interviews &mdash; not just the loudest request."),
            ("Predictable delivery", "Sprint goals, demos and a changelog your stakeholders can read without a translation layer."),
            ("Reliability work", "Performance, cost and incident follow-ups get real capacity, not whatever is left over."),
            ("Metrics that decide", "We agree the number a cycle is meant to move, then report against it honestly."),
            ("Growing your team", "Pairing, reviews and documentation aimed at your engineers taking over more each quarter."),
        ],
        "deliverables": [
            "Quarterly roadmap with explicit bets and success metrics",
            "Two-week sprints with demo and changelog",
            "Shipped increments behind feature flags",
            "Monthly report on metrics, cost and reliability",
            "Documentation and onboarding for your engineers",
            "Incident reviews with concrete follow-through",
        ],
        "faq": [
            ("How is this different from staff augmentation?", "You get a squad that owns an outcome and brings its own process, not individual contractors slotted into yours."),
            ("Minimum commitment?", "Three months to be useful, then rolling with 30 days notice."),
            ("Can the squad scale up or down?", "Monthly, at sprint boundaries, so nothing gets dropped mid-cycle."),
        ],
        "related": ["mvp-development", "cloud-engineering", "data-analytics"],
    },
}


INDUSTRIES = [
    ("&#127973;", "Healthcare", "Clinical workflow tooling and document intelligence, built with auditability and consent handling from the first sprint.",
     ["Care coordination and referral workflows", "Clinical document extraction with human review", "Audit trails and role-based access"]),
    ("&#128179;", "Fintech", "Onboarding, risk and reconciliation systems that hold up when an auditor asks how a decision was made.",
     ["KYC and onboarding orchestration", "Risk scoring with explainable features", "Ledger reconciliation and exception queues"]),
    ("&#128722;", "Retail &amp; E-commerce", "Forecasting, catalogue enrichment and support automation across channels that never quite agree.",
     ["Demand forecasting and replenishment", "Attribute extraction for large catalogues", "Support assistants with order context"]),
    ("&#127981;", "Manufacturing", "Sensor pipelines and plant-floor visibility that survive intermittent connectivity and legacy protocols.",
     ["Telemetry ingestion at the edge", "Predictive maintenance models", "OEE dashboards per line and shift"]),
    ("&#128218;", "Education", "Adaptive learning products and content tooling for platforms growing faster than their stack.",
     ["Adaptive assessment engines", "Content authoring and review tools", "Cohort and outcome analytics"]),
    ("&#128666;", "Logistics", "Routing, tracking and exception handling across partner data that arrives late and malformed.",
     ["Route and load optimisation", "Shipment tracking across carriers", "Exception triage and customer comms"]),
    ("&#127968;", "Real Estate", "Valuation, listing intelligence and transaction workflows built on messy public and private data.",
     ["Automated valuation support", "Listing enrichment and deduplication", "Deal and document pipelines"]),
    ("&#9889;", "Energy", "Consumption analytics and optimisation for distributed assets and volatile pricing.",
     ["Meter and asset data pipelines", "Load forecasting and tariff optimisation", "Field operations tooling"]),
]

ROLES = [
    ("Senior Full-Stack Engineer", "TypeScript, Node, React &mdash; product-facing work with real ownership", "Remote &middot; EU/US", "Engineering"),
    ("AI Engineer", "Retrieval, evals and agent workflows in production, not demos", "Remote &middot; Global", "Engineering"),
    ("Data Engineer", "dbt, Airflow and warehouse modelling for analytics clients", "Noida or remote", "Data"),
    ("Product Designer", "Research through to design systems, embedded in delivery squads", "Remote &middot; EU", "Design"),
    ("Delivery Lead", "Own scope, cadence and client trust across two squads", "Los Angeles hybrid", "Delivery"),
]

POSTS = [
    ("Engineering", "What we cut first when an MVP is running late",
     "Scope triage, in the order we actually apply it: nice-to-have surfaces, then admin tooling, then anything that can be a manual process for eight weeks.",
     "9 min read"),
    ("AI", "Evaluation harnesses are the deliverable",
     "A graded test set is what turns a promising assistant into something a compliance team will sign off. How we build one in the first two weeks.",
     "12 min read"),
    ("Architecture", "The MVP decisions that are expensive to undo",
     "Most first-version shortcuts are fine. These four &mdash; identity, tenancy, money and audit &mdash" + "; are the ones worth two extra days now.",
     "8 min read"),
    ("Data", "One definition of revenue",
     "Why the metric layer belongs upstream of the BI tool, and what changes the week a team finally agrees on churn.",
     "7 min read"),
    ("Cloud", "Making deploys boring",
     "Reproducible environments, one-command rollback, and the alerting rules that stopped waking anyone up at 3am.",
     "10 min read"),
    ("Practice", "How we scope a fixed price without guessing",
     "The scoping session, the assumptions list, and why the non-goals document is the part clients quote back to us.",
     "6 min read"),
]

OFFICES = """<div class="offices">
        <div class="office">
          <h3>United States</h3>
          <p>1 Placeholder Plaza, Suite 900<br />Los Angeles, CA 90045</p>
          <a href="tel:+15550000000">+1 555 000 0000</a>
        </div>
        <div class="office">
          <h3>India</h3>
          <p>Placeholder Business Park, Tower 2<br />Sector 135, Noida, UP 201305</p>
          <a href="mailto:hello@example.com">hello@example.com</a>
        </div>
      </div>"""

CONTACT_FORM = """<form id="contactForm" novalidate>
        <div class="row">
          <label>Full name<input type="text" name="name" placeholder="Jane Mercer" required /></label>
          <label>Work email<input type="email" name="email" placeholder="jane@company.com" required /></label>
        </div>
        <div class="row">
          <label>Company<input type="text" name="company" placeholder="Company Ltd" /></label>
          <label>Budget range
            <select name="budget">
              <option>Under $25k</option>
              <option selected>$25k &ndash; $75k</option>
              <option>$75k &ndash; $150k</option>
              <option>$150k+</option>
            </select>
          </label>
        </div>
        <label>What are you building?<textarea name="brief" placeholder="The problem, who it is for, and any deadline you are working against." required></textarea></label>
        <button type="submit" class="btn btn-primary">Send brief</button>
        <p class="form-status" id="formStatus" role="status"></p>
        <p class="form-note">Demo form &mdash; no backend wired up. Point <code>action</code> at your form handler or CRM endpoint.</p>
      </form>"""


# --------------------------------------------------------------------------- #
# page builders                                                                #
# --------------------------------------------------------------------------- #

def build_service(slug, data, chrome):
    body = "\n\n  ".join([
        section(
            cards(data["cards"]),
            eyebrow="Capabilities",
            heading="What this engagement covers",
            lead="Every point below is something we have shipped, not a service line we are willing to try.",
        ),
        two_col(
            '<header class="section-head reveal" style="margin-bottom:2rem">'
            '<span class="eyebrow">Deliverables</span><h2>What you walk away with</h2></header>'
            + checklist(data["deliverables"]),
            "Not sure it is a fit?",
            "Bring the problem to a 30-minute call. If we are the wrong team we will say so and point you somewhere better.",
            ["No sales deck, a senior engineer on the call",
             "Scope and price inside two working days",
             "Your code, your cloud, your IP"],
        ),
        section(faq(data["faq"]), eyebrow="FAQ", heading="Questions we get asked"),
        section(related(data["related"], SERVICES), eyebrow="Related", heading="Often paired with"),
        CTA_BAND,
    ])
    return render(
        slug,
        title=f'{data["nav"].replace("&amp;", "&")} | Astradive',
        desc=data["desc"],
        eyebrow="Service",
        h1=data["h1"],
        lead=data["lead"],
        hero_extra=HERO_CTA + "\n      " + facts(data["facts"]),
        trail=[("Services", "index.html#services"), (data["nav"], None)],
        body=body,
        chrome=chrome,
    )


def build_industries(chrome):
    blocks = []
    for icon, name, body, bullets in INDUSTRIES:
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        blocks.append(
            f'<article class="reveal"><i aria-hidden="true">{icon}</i><h3>{name}</h3>'
            f"<p>{body}</p><ul>{lis}</ul></article>"
        )
    grid = f'<div class="ind-detail">\n        {chr(10).join(blocks)}\n      </div>'
    body = "\n\n  ".join([
        section(grid, eyebrow="Sectors", heading="Where we have shipped"),
        section(
            related(["enterprise-ai-solutions", "data-analytics", "mvp-development"], SERVICES),
            eyebrow="Services",
            heading="How we usually start",
        ),
        CTA_BAND,
    ])
    return render(
        "industries",
        title="Industries | Astradive",
        desc="Sectors we build in: healthcare, fintech, retail, manufacturing, education, logistics, real estate and energy.",
        eyebrow="Industries",
        h1="Domain context, not just generic code",
        lead="We have delivered in regulated and high-volume environments, so compliance, data residency and unit economics belong in the first conversation.",
        hero_extra=HERO_CTA,
        trail=[("Industries", None)],
        body=body,
        chrome=chrome,
    )


def build_careers(chrome):
    roles = "".join(
        f'<div class="role reveal"><div><b>{title}</b><em>{blurb}</em></div>'
        f'<span class="meta">{loc}</span>'
        f'<a class="btn btn-ghost" href="lets-connect.html">Apply</a></div>'
        for title, blurb, loc, _team in ROLES
    )
    perks = "".join(
        f"<div class=\"reveal\"><b>{t}</b><p>{p}</p></div>"
        for t, p in [
            ("Remote, with overlap", "Work where you live; four hours of overlap with your squad is the only rule."),
            ("Senior by default", "Small teams of experienced people. No layers to route a decision through."),
            ("Learning budget", "Conferences, courses and a paid week each year to go deep on something."),
            ("Real project variety", "AI platforms, data pipelines, mobile products &mdash; rarely the same quarter twice."),
        ]
    )
    body = "\n\n  ".join([
        section(f'<div class="roles">{roles}</div>', eyebrow="Open roles",
                heading="Five seats to fill",
                lead="Placeholder listings &mdash; swap them for your real openings and point Apply at your ATS."),
        section(f'<div class="perks">{perks}</div>', eyebrow="Working here", heading="What we offer"),
        section(
            '<div class="cta-inner reveal"><h2>No role that fits?</h2>'
            '<p class="lead" style="text-align:center">Send work you are proud of and what you want to be doing in a year. '
            'We keep good applications on file and come back to them.</p>'
            '<div class="hero-cta"><a href="lets-connect.html" class="btn btn-primary">Introduce yourself</a></div></div>'
        ),
    ])
    return render(
        "careers",
        title="Careers | Astradive",
        desc="Open roles at Astradive: full-stack, AI, data engineering, product design and delivery leadership.",
        eyebrow="Careers",
        h1="Build products that actually ship",
        lead="Small senior squads, real ownership, and clients who let us do the work properly. If that sounds like the job you wanted, talk to us.",
        hero_extra="",
        trail=[("Careers", None)],
        body=body,
        chrome=chrome,
    )


def build_blogs(chrome):
    posts = "".join(
        f'<article class="post reveal"><span class="kicker">{kicker}</span>'
        f"<h3>{title}</h3><p>{body}</p>"
        f'<div class="meta"><span>Placeholder post</span><span>&middot;</span><span>{read}</span></div></article>'
        for kicker, title, body, read in POSTS
    )
    body = "\n\n  ".join([
        section(f'<div class="posts">{posts}</div>', eyebrow="Writing",
                heading="Notes from delivery",
                lead="Placeholder entries &mdash; replace with your CMS feed or generated post pages."),
        CTA_BAND,
    ])
    return render(
        "blogs",
        title="Blog | Astradive",
        desc="Notes on shipping AI products: scoping, evaluation harnesses, architecture decisions and delivery practice.",
        eyebrow="Blog",
        h1="What we learned shipping it",
        lead="Short, specific write-ups from live projects &mdash; scoping calls, eval harnesses, and the architecture decisions that are expensive to undo.",
        hero_extra="",
        trail=[("Blog", None)],
        body=body,
        chrome=chrome,
    )


def build_contact(chrome):
    left = (
        '<span class="eyebrow">Let&rsquo;s talk</span>'
        "<h2>Tell us what you&rsquo;re building</h2>"
        '<p class="lead">A senior engineer joins the first call &mdash; not a salesperson. '
        "Expect straight answers about feasibility, cost and what we would cut.</p>" + OFFICES
    )
    body = (
        '<section class="section">\n    <div class="shell contact-grid">\n      '
        f'<div class="reveal">{left}</div>\n      {CONTACT_FORM}\n    </div>\n  </section>'
    )
    return render(
        "lets-connect",
        title="Let&rsquo;s Connect | Astradive",
        desc="Send us a brief or book a call. Offices in Los Angeles and Noida.",
        eyebrow="Contact",
        h1="Start with the problem, not the spec",
        lead="Send a few paragraphs about what you are trying to do. We reply with questions, a scope and a number &mdash; usually within two working days.",
        hero_extra="",
        trail=[("Let&rsquo;s Connect", None)],
        body=body,
        chrome=chrome,
    )


def build_schedule(chrome):
    steps = "".join(
        f'<div class="reveal"><b>{n}</b><p>{p}</p></div>'
        for n, p in [
            ("30 minutes", "One call, no deck. You describe the problem; we ask the awkward questions."),
            ("Who joins", "A delivery lead and the engineer who would own the architecture."),
            ("You leave with", "A feasibility read, a rough shape, and whether we are the right team at all."),
        ]
    )
    slots = "".join(
        f'<button type="button" aria-pressed="false">{s}</button>'
        for s in ["Mon 09:00", "Mon 14:00", "Tue 11:00", "Wed 09:30", "Wed 16:00", "Thu 13:00", "Fri 10:00"]
    )
    body = "\n\n  ".join([
        section(
            f'<div class="booking">{steps}</div>'
            '<div class="card reveal"><h3>Pick a slot</h3>'
            '<p>Times shown in your local timezone. Placeholder UI &mdash; connect your scheduling '
            "provider or calendar embed here.</p>"
            f'<div class="slots" id="slots">{slots}</div></div>',
            eyebrow="Strategy call",
            heading="How the first call works",
        ),
        '<section class="section">\n    <div class="shell contact-grid">\n      '
        '<div class="reveal"><span class="eyebrow">Or write instead</span>'
        "<h2>Prefer to send it in writing?</h2>"
        '<p class="lead">Some problems are easier to describe than to discuss. Send the brief and we '
        "will come back with questions.</p>" + OFFICES + "</div>\n      " + CONTACT_FORM
        + "\n    </div>\n  </section>",
    ])
    return render(
        "schedule-meeting",
        title="Book a Strategy Call | Astradive",
        desc="Book a free 30-minute strategy call with a senior engineer and a delivery lead.",
        eyebrow="Book a call",
        h1="A free 30-minute strategy call",
        lead="No sales deck. A delivery lead and a senior engineer, your problem, and an honest read on whether it is worth building the way you were planning to.",
        hero_extra="",
        trail=[("Book a call", None)],
        body=body,
        chrome=chrome,
    )


LEGAL_NOTICE = ('<p class="notice"><b>Template text.</b> This page is placeholder boilerplate for '
                "layout purposes only. Replace it with a policy reviewed by your own counsel before "
                "going live.</p>")


def build_legal(slug, title, h1, lead, blocks, chrome):
    prose = LEGAL_NOTICE + '<p class="updated">Last updated: placeholder date</p>'
    for heading, paras in blocks:
        prose += f"<h2>{heading}</h2>"
        for p in paras:
            if isinstance(p, list):
                prose += "<ul>" + "".join(f"<li>{i}</li>" for i in p) + "</ul>"
            else:
                prose += f"<p>{p}</p>"
    body = (
        '<section class="section">\n    <div class="shell">\n      '
        f'<div class="prose reveal">{prose}</div>\n    </div>\n  </section>'
    )
    return render(
        slug,
        title=f"{title} | Astradive",
        desc=f"{title} for the Astradive website template.",
        eyebrow="Legal",
        h1=h1,
        lead=lead,
        hero_extra="",
        trail=[(title, None)],
        body=body,
        chrome=chrome,
    )


PRIVACY_BLOCKS = [
    ("What this policy covers", [
        "This policy describes what information this website collects, why it is collected, and the choices available to visitors.",
    ]),
    ("Information collected", [
        "Two categories of information may be collected:",
        ["Information you provide directly &mdash; for example a name, email address and message submitted through a contact form.",
         "Technical information collected automatically &mdash; for example browser type, referring page and approximate location derived from an IP address."],
    ]),
    ("How information is used", [
        "Submitted information is used to respond to enquiries, to provide requested services, and to keep records of business correspondence. Technical information is used to keep the site running and to understand which pages are useful.",
        "Information is not sold, and it is not shared with third parties except where a service provider processes it on our behalf or where disclosure is required by law.",
    ]),
    ("Cookies and analytics", [
        "This template ships without analytics or advertising cookies. If you add an analytics provider, describe it here and add a consent mechanism where your jurisdiction requires one.",
    ]),
    ("Data retention", [
        "Enquiry correspondence is retained for as long as needed to answer it and to meet record-keeping obligations, then deleted.",
    ]),
    ("Your rights", [
        "Depending on where you live you may have the right to request a copy of your personal data, ask for it to be corrected or deleted, or object to certain processing. Requests can be sent to the contact address below.",
    ]),
    ("Contact", [
        'Questions about this policy can be sent to <a href="mailto:hello@example.com">hello@example.com</a>.',
    ]),
]

TERMS_BLOCKS = [
    ("Agreement to these terms", [
        "By using this website you agree to these terms. If you do not agree, please do not use the site.",
    ]),
    ("Use of the site", [
        "You may view and share the content here for your own informational purposes. You may not:",
        ["Use the site in a way that disrupts it or interferes with anyone else's use of it.",
         "Attempt to gain unauthorised access to any part of the site or its infrastructure.",
         "Reproduce substantial parts of the content commercially without written permission."],
    ]),
    ("Intellectual property", [
        "Unless stated otherwise, the content, design and code of this site belong to its operator. Third-party names and marks mentioned belong to their respective owners and are used descriptively only.",
    ]),
    ("Services and quotations", [
        "Descriptions of services on this site are informational and are not an offer. Any engagement is governed by a separate signed agreement setting out scope, fees, timelines and ownership of deliverables.",
    ]),
    ("No warranty", [
        "The site is provided as-is. While we aim to keep information accurate and the site available, no guarantee is given that it will be error-free or uninterrupted.",
    ]),
    ("Limitation of liability", [
        "To the extent permitted by law, the site operator is not liable for indirect or consequential loss arising from use of this site.",
    ]),
    ("Changes and governing law", [
        "These terms may be updated; the current version is always the one published here. Insert the governing jurisdiction that applies to your entity before publishing.",
    ]),
]


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description="Generate Astradive sub-pages.")
    ap.add_argument("--list", action="store_true", help="list target pages and exit")
    args = ap.parse_args()

    targets = list(SERVICES) + [
        "industries", "careers", "blogs", "lets-connect",
        "schedule-meeting", "privacy-policy", "terms-condition",
    ]
    if args.list:
        for t in targets:
            print(f"{t}.html")
        return

    chrome = load_chrome()
    written = []

    for slug, data in SERVICES.items():
        written.append(build_service(slug, data, chrome))

    written.append(build_industries(chrome))
    written.append(build_careers(chrome))
    written.append(build_blogs(chrome))
    written.append(build_contact(chrome))
    written.append(build_schedule(chrome))
    written.append(build_legal(
        "privacy-policy", "Privacy Policy", "Privacy policy",
        "What this site collects, why, and how to ask us to delete it.",
        PRIVACY_BLOCKS, chrome))
    written.append(build_legal(
        "terms-condition", "Terms &amp; Conditions", "Terms &amp; conditions",
        "The terms that apply to using this website.",
        TERMS_BLOCKS, chrome))

    for slug in written:
        size = (ROOT / f"{slug}.html").stat().st_size
        print(f"  wrote {slug}.html  ({size:,} bytes)")
    print(f"\n{len(written)} pages generated.")


if __name__ == "__main__":
    main()

