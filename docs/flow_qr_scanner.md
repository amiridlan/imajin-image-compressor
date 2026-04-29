# User Flow — QR Scanner

```mermaid
flowchart TD
    A([Enter from Hub]) --> B[QR Scanner window]
    B --> C{Choose input mode}

    %% ── Camera path ─────────────────────────────────────────────────────
    C -->|Camera tab| D[Click Start Camera]
    D --> E{Webcam available?}
    E -->|No| F[Error shown\ncheck Privacy settings]
    E -->|Yes| G[Live viewfinder\nOpenCV frame feed]

    G --> H{QR code in frame?}
    H -->|No| G
    H -->|Yes| I[Bounding box drawn around code]
    I --> J[Decode with pyzbar]
    J --> K[Check threat status]

    %% ── Upload path ──────────────────────────────────────────────────────
    C -->|Upload tab| L{Add file}
    L -->|Drag & drop| M[Image or PDF queued]
    L -->|Browse| N[File picker] --> M
    M --> O[Click Scan]
    O --> P[Render PDF pages via pdf2image\nor read image directly]
    P --> J

    %% ── Threat check (shared) ────────────────────────────────────────────
    K --> Q{URL detected?}
    Q -->|No — raw data| R["Result: UNKNOWN\n(non-URL payload)"]
    Q -->|Yes| S{In URLhaus blocklist?}
    S -->|Yes| T["Result: MALICIOUS 🔴"]
    S -->|No| U{VirusTotal API key set?}
    U -->|No| V["Result: SAFE ✅\n(offline check only)"]
    U -->|Yes| W[Live VirusTotal scan]
    W --> X{VT verdict}
    X -->|Clean| V
    X -->|Flagged| T

    %% ── Results panel ────────────────────────────────────────────────────
    R --> Y[Result added to panel\nwith badge]
    T --> Y
    V --> Y

    Y --> Z{User action on result}
    Z -->|Click Copy| AA[Data copied to clipboard\nButton flashes ✓]
    Z -->|Double-click| AB[QR Detail Dialog\nFull data · Open URL button]
    Z -->|Ignore| AC{More codes?}

    AA --> AC
    AB --> AC
    AC -->|Camera: more frames| H
    AC -->|Upload: more pages/files| P
    AC -->|Done| AD{Continue?}

    AD -->|Scan another| C
    AD -->|Stop Camera| AE[Camera released]
    AE --> C
    AD -->|Back to Hub| AF([↩ Back])
```

> **VirusTotal** — optional. Add your API key in the Settings panel (right side) to enable live scanning beyond the offline URLhaus blocklist.  
> **PDF scanning** — requires Poppler for Windows on the system `PATH`.
