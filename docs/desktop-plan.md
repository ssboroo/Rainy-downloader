# Desktop integration implementation

Goal: Desktop UI + inline browser download controls + Windows packaging.
Spec: docs/desktop-design.md. Execute inline, reuse previous verified engine.

- [x] Test runtime frozen/source commands, browser native manifests and sender restrictions before implementation.
- [x] Add desktop controller, UI, runtime binary lookup, worker mode and version probes. Test controller with real temporary Store and stub only external inspections.
- [x] Add optional-permission video controls, route resolution, Chrome/Edge/Brave/Opera host registration, Firefox build/manifest. Test URL routing and content message validation.
- [x] Add PyInstaller GUI + console native executable builds, verified download steps, Inno installer, Windows workflow and developer build command.
- [ ] Run suites, static/compile/archive checks and independent review. Document unavailable actual Windows/browser/site checks. Deliver source package; ready executable only after successful Windows build.

Windows artifact build and real browser/video validation remain pending a Windows runner. Source verification and independent review completed; final source package prepared.
