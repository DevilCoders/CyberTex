# Security Web Builders

SAPL now ships with a fluent collection of builders dedicated to security-first
web development. The classes live in the standard library and are exposed as
built-ins, meaning you can instantiate them directly in any `.sapl` playbook
without additional imports.

The builders capture functional requirements and security posture side-by-side,
so the resulting configuration objects can be inspected, rendered, or passed to
automation pipelines.

## Static sites and documentation

```sapl
cyber_portfolio = (
    StaticSite("security-researcher-portfolio")
    .template("dark-theme")
    .content(posts=blog_posts, projects=research_projects)
    .security_headers(csp=True, hsts=True, xss_protection=True)
    .deploy(providers=["github-pages", "netlify", "s3"])
)

docs = (
    SecurityDocumentation("enterprise-policies")
    .sections(["incident-response", "access-control", "data-protection"])
    .generate_static()
    .deploy_internal()
)
```

Each chaining call records configuration while returning the builder so you can
continue the fluent workflow. Calling `.describe()` on any builder returns a
serialisable dictionary of the captured settings.

## Dashboards, components, and real-time experiences

`WebApp`, `RealTimeApp`, `RealTimeDashboard`, and the `Component` builder let you
model SOC dashboards, live incident views, and login flows that include security
controls as first-class fields.

```sapl
security_dashboard = (
    WebApp("soc-dashboard")
    .frontend("react-like-components")
    .backend("real-time-api")
    .database("encrypted-at-rest")
    .authentication("mfa-required")
)

login_form = (
    Component("LoginForm")
    .state(username="", password="", mfa_code="")
    .security(rate_limiting="5 attempts per minute", csrf_protection=True)
    .method("authenticate", "Use api.auth.login with MFA and session hardening")
    .render("<form>…</form>")
)

security_dashboard.register_component(login_form)
```

Components track state, security policies, subscriptions, and arbitrary method
summaries so you can feed them into code generators, templates, or reporting
pipelines.

## APIs and automation backends

Use `WebAPI` to declare API middleware, persistence, and cache layers. Call
`.endpoint(path, **options)` to register endpoints and describe expected
behaviour via `.handler(description)`.

The same script can orchestrate vulnerability portals, threat intelligence
pipelines, bug bounty platforms, and SOC coordination hubs by combining builders
such as `WebApplication`, `ThreatIntelPlatform`, `BugBountyPlatform`, and
`Component` instances that capture automation steps.

## Deployment and infrastructure

`SecureDeployment` and `CloudDeployment` model CI/CD safeguards, security gates,
and cloud hosting configurations. Combine them with `SecurityHeaders`,
`InputValidator`, `AuthenticationSystem`, and `RBACSystem` to ensure every
surface includes hardened defaults.

```sapl
deployment = (
    SecureDeployment("security-app")
    .source_control("git-encrypted")
    .build_process("security-scans-included")
    .testing("automated-pentest")
    .deployment("zero-downtime")
)

deployment.add_gate("sast-scan")
deployment.add_gate("dependency-vulnerability-scan")
```

## Network primitives

The stdlib exposes `scan`, `Packet`, and `brute_force` so security builders can
be paired with low-level assessments inside a single SAPL file.

```sapl
target = scan("192.168.1.0/24")
services = target.port_scan([22, 80, 443, 3389])

packet = Packet()
packet.ip.fields["src"] = "192.168.1.100"
packet.tcp.fields["dport"] = 80
packet.payload = "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
response = send_raw(packet)
```

## Full example

See `examples/security_web_revolution.sapl` for an end-to-end blueprint covering
static sites, SOC dashboards, threat intelligence, penetration testing,
deployment pipelines, and network primitives—all composed with the new
builders.
