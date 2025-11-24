# HistoryMixin

Provides operation tracking and replay functionality.

## Overview

The `HistoryMixin` automatically records all operations performed on a dataset, enabling:

- **Reproducibility** - Replay operations to recreate datasets
- **Documentation** - Export history as Python code, JSON, or YAML
- **Visualization** - View history as text, DOT graphs, or Mermaid diagrams
- **Debugging** - Understand how a dataset was constructed

## Key Methods

- `get_history()` - Get list of recorded operations
- `export_history(format)` - Export as 'python', 'json', or 'yaml'
- `visualize_history(format)` - Visualize as 'text', 'dot', or 'mermaid'
- `replay_history(history)` - Recreate dataset from history
- `reset_history()` - Clear history and start fresh

## Usage

See the [History Tracking Guide](../../user-guide/history-tracking.md) for detailed examples.

## API Reference

::: dummyxarray.history.HistoryMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
