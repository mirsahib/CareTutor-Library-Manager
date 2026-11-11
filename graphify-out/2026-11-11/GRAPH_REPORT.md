# Graph Report - Library_Book_Manager  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 20 nodes · 11 edges · 11 communities (2 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- backend
- frontend
- services

## God Nodes (most connected - your core abstractions)
1. `backend` - 5 edges
2. `frontend` - 4 edges
3. `services` - 3 edges
4. `build` - 1 edges
5. `environment` - 1 edges
6. `ports` - 1 edges
7. `volumes` - 1 edges
8. `build` - 1 edges
9. `depends_on` - 1 edges
10. `ports` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (11 total, 9 thin omitted)

### Community 0 - "backend"
Cohesion: 0.40
Nodes (5): build, environment, ports, volumes, backend

### Community 1 - "frontend"
Cohesion: 0.50
Nodes (4): build, depends_on, ports, frontend

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `services` connect `services` to `backend`, `frontend`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **Why does `backend` connect `backend` to `services`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `frontend` connect `frontend` to `services`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._