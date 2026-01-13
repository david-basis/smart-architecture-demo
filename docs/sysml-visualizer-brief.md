# SysML Visualizer Tool - Project Brief

## Overview

A browser-based visualization tool for SysML v2 models that provides two complementary "flight levels" of diagram views:

1. **Formal SysML Diagrams** - Standards-compliant SysML v2 notation
2. **Simplified System Diagrams** - Draw.io-style block diagrams for stakeholder presentations

The tool is read-only (no editing) and focused on navigation, exploration, and presentation of existing SysML models.

## Problem Statement

Current options for visualizing SysML v2 models require either:
- Full IDE installations (SysIDE/VS Code, Eclipse SysON)
- Complex setup and configuration
- Technical knowledge to interpret formal SysML notation

Engineers need a lightweight way to:
- Share models with non-technical stakeholders
- Present architecture to colleagues without SysML expertise
- Navigate large models interactively in the browser
- Switch between formal and simplified views based on audience

## Target Users

| User Type | Primary Need |
|-----------|--------------|
| Systems Engineers | Navigate and present their models |
| Technical Managers | Review architecture without learning SysML |
| Stakeholders | Understand system structure at high level |
| Reviewers | Explore models during design reviews |

## Key Features

### Core Visualization

- **Dual View Modes**
  - **SysML View**: Proper SysML v2 diagram notation (BDD, IBD, Requirements, State Machines)
  - **Simplified View**: Clean block diagrams similar to draw.io/Lucidchart style

- **Supported Diagram Types**
  - Block Definition Diagrams (part def hierarchy)
  - Internal Block Diagrams (port connections, interfaces)
  - Requirements Diagrams
  - State Machine Diagrams

### Navigation

- **Model Explorer** - Tree view of model elements
- **Diagram Navigation** - Click-through from elements to related diagrams
- **Search** - Find elements by name, type, or content
- **Breadcrumb Trail** - Track navigation path through model
- **Multi-page Support** - Similar to draw.io page navigation

### Presentation Mode

- **Full-screen diagrams** for meetings/presentations
- **Zoom and pan** controls
- **Element highlighting** on hover/selection
- **Collapsible subsystems** for progressive disclosure

## Technical Approach

### Input Format

- Parse `.sysml` text files directly (SysML v2 textual notation)
- No server required - fully client-side parsing and rendering

### Architecture Options

| Option | Pros | Cons |
|--------|------|------|
| **React + D3.js** | Flexible, large ecosystem | More custom work |
| **React + React Flow** | Built-in node/edge handling, interactive | Good fit for block diagrams |
| **Cytoscape.js** | Graph-focused, layout algorithms | Less customizable styling |
| **mxGraph (draw.io core)** | Proven, familiar look | Complex API, large bundle |

**Recommended**: React + React Flow for the diagram canvas, with custom SysML notation components.

### Key Components

```
sysml-visualizer/
├── src/
│   ├── parser/           # SysML v2 text parser
│   │   ├── lexer.ts
│   │   ├── parser.ts
│   │   └── ast.ts        # AST types
│   ├── model/            # Semantic model
│   │   ├── elements.ts   # Part, Port, Requirement, etc.
│   │   └── resolver.ts   # Reference resolution
│   ├── diagrams/         # Diagram generation
│   │   ├── bdd.ts        # Block Definition Diagram
│   │   ├── ibd.ts        # Internal Block Diagram
│   │   ├── req.ts        # Requirements Diagram
│   │   └── stm.ts        # State Machine Diagram
│   ├── views/            # View modes
│   │   ├── sysml/        # Formal SysML notation
│   │   └── simplified/   # Draw.io style
│   ├── components/       # React components
│   │   ├── Explorer.tsx
│   │   ├── DiagramCanvas.tsx
│   │   ├── Toolbar.tsx
│   │   └── ElementDetails.tsx
│   └── App.tsx
├── public/
└── package.json
```

## View Mode Comparison

### SysML View (Formal)

```
┌─────────────────────────────────────┐
│ «part def» IntegratedMeter          │
├─────────────────────────────────────┤
│ ports                               │
│  ○─ phaseIn : PhasePort             │
│  ○─ phaseOut : PhasePort            │
│  ○─ neutralIn : NeutralPort         │
│  ○─ t1s : T1SPort                   │
├─────────────────────────────────────┤
│ parts                               │
│  ◊ phaseInTerminal : MeterTerminal  │
│  ◊ phaseOutTerminal : MeterTerminal │
└─────────────────────────────────────┘
```

### Simplified View (Draw.io Style)

```
┌────────────────────────────┐
│      Integrated Meter      │
│                            │
│  ┌──────┐    ┌──────┐     │
│  │Phase │    │Phase │     │
│  │ In   │───▶│ Out  │     │
│  └──────┘    └──────┘     │
│       │                    │
│  ┌────▼─────┐             │
│  │ Neutral  │             │
│  └──────────┘             │
└────────────────────────────┘
```

## Reference Tools

| Tool | Key Takeaway |
|------|--------------|
| [SysON](https://mbse-syson.org/) | Web-based, Sirius framework, full SysML v2 compliance |
| [SysIDE](https://sensmetry.com/syside/) | VS Code extension, Tom Sawyer visualization |
| [Tom Sawyer SysML v2 Viewer](https://www.tomsawyer.com/sysml-v2-viewer) | Commercial visualization, layout algorithms |
| [Gaphor](https://gaphor.org/) | Open source UML/SysML, Python-based |

## Scope

### In Scope (MVP)

- [ ] Parse SysML v2 textual files
- [ ] Block Definition Diagram (part hierarchy)
- [ ] Internal Block Diagram (connections)
- [ ] Dual view mode toggle (SysML / Simplified)
- [ ] Model explorer tree
- [ ] Element click-through navigation
- [ ] Basic search
- [ ] Zoom/pan controls
- [ ] Load local .sysml files

### Out of Scope (Future)

- Model editing
- Server/database persistence
- Multi-user collaboration
- Full SysML v2 spec compliance (focus on common constructs)
- Export to other formats
- Simulation/analysis integration

## Success Criteria

1. **Load and display** the Gen2Panel1P12.sysml file correctly
2. **Navigate** between parts, drilling into subsystems
3. **Toggle** between SysML and simplified views
4. **Present** to colleagues without requiring SysML knowledge
5. **Run entirely in browser** with no backend required

## Timeline Estimate

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| 1 | SysML v2 parser (core constructs) | Medium |
| 2 | Model explorer + element details | Small |
| 3 | Block Definition Diagram (both views) | Medium |
| 4 | Internal Block Diagram (both views) | Medium |
| 5 | Navigation + search | Small |
| 6 | Polish + presentation mode | Small |

## Open Questions

1. **Parser approach**: Build custom parser or use/adapt existing SysML v2 parser (e.g., from SysIDE)?
2. **Layout algorithm**: Auto-layout vs manual positioning hints in model?
3. **Styling**: Custom theme or follow SysML v2 graphical notation spec strictly?
4. **Deployment**: Static hosting (GitHub Pages) or need any backend services?

## Next Steps

1. Review and approve brief
2. Evaluate parser options (custom vs existing)
3. Set up project scaffolding (React + React Flow)
4. Implement parser for Gen2Panel subset
5. Build MVP diagram renderer

---

*Created: January 2026*
*Status: Draft*
