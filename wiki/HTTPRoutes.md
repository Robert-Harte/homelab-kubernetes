# HTTPRoutes

Gateway API routing topology for the cluster. All routes share a single Traefik-backed
Gateway. (Classic `Ingress` resources also exist for these apps but are intentionally
omitted here — see [[Home]].)

```mermaid
flowchart LR
    U([*.robertharte.home]) --> GW

    subgraph gw ["Gateway: traefik-gateway"]
        L80["listener: http :80"]
        L443["listener: https :443<br/>TLS Terminate · cert: secret-tls"]
    end

    GW[(traefik-gateway)] --- L80
    GW --- L443

    %% HTTPRoutes -> services. parentRef sectionName shown on the edge.
    L443 -->|calibre| SVC1[svc calibre :8083]
    L80  -->|calibre| SVC1
    L443 -->|homepage| SVC2[svc homepage :3000]
    L80  -->|homepage| SVC2
    L443 -->|linkding| SVC3[svc linkding :9090]
    L80  -->|linkding| SVC3
    L443 -->|mealie| SVC4[svc mealie :9000]
    L80  -->|mealie| SVC4
    L443 -->|pgadmin| SVC5[svc pgadmin :80]
    L80  -->|pgadmin| SVC5
    L80  -->|postgres| SVC6[svc postgres :5432]
```

## HTTPRoutes

| HTTPRoute | Hostname | Listeners attached (`sectionName`) | Backend |
|-----------|----------|------------------------------------|---------|
| calibre   | calibre.robertharte.home  | http, https | calibre:8083 |
| homepage  | homepage.robertharte.home | http, https | homepage:3000 |
| linkding  | linkding.robertharte.home | http, https | linkding:9090 |
| mealie    | mealie.robertharte.home   | http, https | mealie:9000 |
| pgadmin   | pgadmin.robertharte.home  | http, https | pgadmin:80 |
| postgres  | postgres.robertharte.home | **http only** | postgres:5432 |

All routes share the single `traefik-gateway` Gateway
(GatewayClass `traefik`, controller `traefik.io/gateway-controller`).

## Notes

- **`postgres` attaches to the `http` listener only** — the other five attach to both
  `http` and `https`, so `https://postgres.robertharte.home` will not route.
- Postgres is a raw TCP service on `:5432`; routing it through an HTTP-layer Gateway is
  questionable. A Gateway API `TCPRoute` or a Traefik `IngressRouteTCP` is a better fit.
