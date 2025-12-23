# AGENTS.md

This document defines **non-negotiable rules, assumptions, and design constraints**
for implementing `jupyterlab-paperspace-model-cockpit`.

The purpose of this file is to ensure that AI agents (e.g. Cursor) do **not**
introduce unnecessary complexity, state, or architectural drift.

If something is not explicitly allowed here, assume it is **not allowed**.

---

## Project Overview

- Project name: `jupyterlab-paperspace-model-cockpit`
- Type: JupyterLab extension
- Target environment:
  - Paperspace (ephemeral runtime)
  - JupyterLab
  - ComfyUI (model consumer)
- Primary goal:
  - Declarative, reproducible model installation
  - Zero persistent runtime state
  - Safe reinstallation on every environment start

---

## Fundamental Assumptions (Do Not Violate)

- Paperspace environments are **ephemeral**
- Model files are **not persistent**
- JSON configuration files **are persistent**
- Reinstallation is expected and cheap
- Failure should result in a clean retry, not recovery logic

---

## Core Design Principles

### 1. No State Management
- Do NOT use databases (SQLite, etc.)
- Do NOT persist install history
- Do NOT track timestamps or install records
- Installation state is determined **only by file existence**

### 2. Declarative Configuration
- Models and bundles are defined in JSON
- JSON represents intent, not state
- Runtime must be reconstructible from JSON alone

### 3. File-Based Truth
- A model is considered installed if and only if:
  - The target file exists at the expected path
- Partial or failed files must not remain

---

## Data Model Specification

### models.json (single file)

The configuration file contains **both models and bundles**.

#### Models

- Each model has a **deterministic, human-readable ID**
- IDs are NOT random
- IDs must be stable across environments and regenerations

Example structure:

    {
      "models": {
        "sdxl_base_1_0_128713": {
          "display_name": "SDXL Base",
          "version": "1.0",
          "type": "checkpoint",
          "source": {
            "kind": "civitai",
            "model_id": 12345,
            "version_id": 128713
          },
          "path": "checkpoints/sdxl_base_1_0.safetensors"
        }
      }
    }

#### Bundles

- A bundle is a simple collection of model IDs
- Bundles do NOT nest
- Bundles do NOT track install state

    {
      "bundles": {
        "sdxl_basic": {
          "description": "Basic SDXL setup",
          "models": ["sdxl_base_1_0_128713"],
          "auto_install": true
        }
      }
    }

---

## ID Generation Rules

- IDs must be deterministic
- IDs must be derived from:
  - model name
  - version name or number
  - a unique version identifier provided by the source
- Do NOT use UUIDs or random strings
- Source kind (`civitai`, `huggingface`) must NOT be embedded in the ID

### Unique Version Identifier by Source

Each model source must provide a **stable, source-specific identifier**
that uniquely represents the exact downloadable artifact.

This identifier is used as the final anchor to guarantee determinism.

#### Civitai

- Use `modelVersion.id`
- This value is:
  - Globally unique within Civitai
  - Stable over time
  - Guaranteed not to change

Example:

    model.name        = "SDXL Base"
    modelVersion.name = "1.0"
    modelVersion.id   = 128713

Resulting ID (example):

    sdxl_base_1_0_128713

#### HuggingFace

- Use the **commit hash** that identifies the exact file revision
- The following combination defines a unique artifact:
  - repository ID
  - filename
  - commit hash (revision)
- Branch names such as `main` MUST NOT be used as identifiers

Example:

    repo      = "stabilityai/stable-diffusion-xl-base-1.0"
    filename  = "sdxl_base_1.0.safetensors"
    revision  = "a1b2c3d4e5f6..."

Resulting ID (example, using short commit hash):

    sdxl_base_1_0_a1b2c3d

The role of the HuggingFace commit hash is equivalent to
Civitai's `modelVersion.id`.


---

## Installation Behavior

### Download Strategy
- Downloads MUST be processed **serially**
- No parallel downloads
- Use a server-side queue with a single worker

### Failure Handling
- On download failure:
  - Immediately delete the target file
  - Do NOT leave partial files
- Retry is handled by re-running installation

### Cancellation
- Cancellation is allowed
- On cancel:
  - Abort download
  - Delete target file
  - Leave no state behind

---

## Auto Install on Startup

- Bundles may specify `auto_install: true`
- On JupyterLab startup:
  1. Load models.json
  2. Find auto_install bundles
  3. For each model:
     - If file exists, skip
     - If not, download
- No UI interaction is required
- No success logging is required

---

## UI Responsibilities

- UI is optional for core functionality
- UI may:
  - Trigger installs
  - Trigger cancellations
  - Display installed / not installed status
- UI must NOT:
  - Assume persistent state
  - Require logs for correctness
  - Block startup behavior

---

## Frontend Technology Constraints

The frontend implementation MUST follow these constraints:

- The frontend MUST be implemented using React.
- UI components MUST use MUI (Material UI v5).
- Styling MUST rely on Emotion, as used by MUI.
- Do NOT introduce alternative UI frameworks (e.g. Chakra, AntD, custom CSS frameworks).
- JupyterLab UI components may be used where appropriate, but MUI is the primary UI toolkit.

---

## Explicitly Forbidden

The following are NOT allowed:

- SQLite or any database
- UUID-based model IDs
- Parallel downloads
- Persistent install logs
- Complex recovery or resume logic
- Automatic model updates
- Semantic compatibility checks
- Engine-specific logic (ComfyUI vs A1111)

---

## Architectural Expectations

- Follow standard JupyterLab extension structure
- Separate frontend and server logic
- Server side handles:
  - Downloads
  - File system operations
- Frontend side handles:
  - User interaction only

The exact directory layout may evolve, but the above separation must remain.

---

## Guiding Philosophy

This project optimizes for:

- Predictability over cleverness
- Reproducibility over performance
- Simplicity over features

If a design choice introduces ambiguity, state, or hidden behavior,
it is almost certainly wrong for this project.
