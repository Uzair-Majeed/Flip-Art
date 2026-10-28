# FlipArt frontend

React + TypeScript UI built with Vite. Follow the [root README](../README.md) for full setup and model requirements.

## Commands

From the project root, keep Flask running with `.\venv\Scripts\python.exe backend\run.py`, then use another PowerShell terminal:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run dev
```

Open the URL printed by Vite (normally http://localhost:5173). The development server proxies `/api` and `/health` to Flask at `http://127.0.0.1:5000`; sample images come from `public/samples/`.

Build for Flask serving:

```powershell
npm.cmd --prefix frontend run build
```

The build runs TypeScript checks and emits `frontend/dist/`, which Flask serves at **http://127.0.0.1:5000**. Rebuild after source changes to update that version. Dependencies and generated output are ignored by Git; `package-lock.json` is retained.

## Code organization

| Folder/file | Responsibility |
| --- | --- |
| `src/App.tsx` | Compose the page sections |
| `src/components/layout/` | Shared FlipArt branding, header, footer |
| `src/components/home/` | Introduction and model information |
| `src/components/conversion/` | Workspace, modes, upload/camera panel, results, settings, preview |
| `src/hooks/useConversion.ts` | Input state, debounced preview, conversion requests |
| `src/hooks/useCamera.ts` | Camera permissions, stream lifecycle, frame capture |
| `src/hooks/useBackendHealth.ts` | Backend readiness status |
| `src/api/client.ts` | Health, sample, preview, and conversion HTTP requests |
| `src/types/conversion.ts` | Shared request/response and option types |
| `src/utils/images.ts` | File validation, reading, PNG data URLs |
| `src/styles/` | Readable base, layout, workspace, and responsive styles |
| `public/samples/` | Demo images shared by the UI and backend tests |

Components render the interface and call hooks; API calls are centralized in the client. Camera streams stop when capture finishes, the upload tab is selected, or the component unmounts. Preview requests are debounced and canceled when inputs change.

## Manual checks

- Confirm FlipArt branding and the Models ready status.
- Use Try a photo, convert, and download `flipart-sketch.png`.
- Use Convert another, then Try a sketch; convert and download `flipart-photo.png`.
- Change direction and cleanup settings; confirm the prepared preview updates.
- Upload a file, check validation for unsupported/oversized input, and test a narrow viewport.
- Allow camera permission on localhost or HTTPS; capture, retake, and switch back to upload.

Generated images are 128 x 128 model outputs enlarged for display. Auto-detection confidence is heuristic.
