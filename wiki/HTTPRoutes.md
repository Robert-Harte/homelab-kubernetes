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

    %% Every HTTPRoute attaches to both the http and https listeners.
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

    %% postgres is NOT routed through the Gateway — it uses its own LoadBalancer.
    U -. direct LoadBalancer :5432 .-> PG[svc postgres :5432]
```

## HTTPRoutes

| HTTPRoute | Hostname | Listeners attached (`sectionName`) | Backend |
|-----------|----------|------------------------------------|---------|
| calibre   | calibre.robertharte.home  | http, https | calibre:8083 |
| homepage  | homepage.robertharte.home | http, https | homepage:3000 |
| linkding  | linkding.robertharte.home | http, https | linkding:9090 |
| mealie    | mealie.robertharte.home   | http, https | mealie:9000 |
| pgadmin   | pgadmin.robertharte.home  | http, https | pgadmin:80 |

All routes share the single `traefik-gateway` Gateway
(GatewayClass `traefik`, controller `traefik.io/gateway-controller`).

## Notes

- All five HTTPRoutes attach to both the `http` (:80) and `https` (:443) listeners.
- **PostgreSQL is intentionally not routed through the Gateway.** Its HTTPRoute (and
  Ingress) were removed — Postgres is a raw TCP service and is exposed directly via its
  own `LoadBalancer` Service on `:5432`, with TLS handled by Postgres (`sslmode`).
