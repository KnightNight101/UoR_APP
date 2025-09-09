# Project_APP Docker Usage

## Quickstart

1. **Build the Docker image:**
   ```sh
   docker build -t project_app:latest .
   ```

2. **Run the container:**
   ```sh
   docker run -it --rm -p 8000:8000 -v $(pwd)/Project_APP:/workspace project_app:latest
   ```

## Components Included

- **App:** Python backend in `/APP`
- **Documentation:** Markdown, diagrams in `/Documentation`
- **Benchmarks:** Scripts and results in `/Benchmarks`
- **Report:** LaTeX sources and PDF in `/Report`

## Volumes

- Mount `/workspace` to persist changes:
  - `-v $(pwd)/Project_APP:/workspace` (Linux/macOS)
  - `-v %cd%\Project_APP:/workspace` (Windows)

## Docker Hub Usage

If published to Docker Hub:
```sh
docker pull <your-dockerhub-username>/project_app:latest
docker run -it --rm -p 8000:8000 -v $(pwd)/Project_APP:/workspace <your-dockerhub-username>/project_app:latest
```

## Notes

- The container starts the app server by default (`python APP/main.py`).
- All components (app, docs, benchmarks, report) are available in `/workspace`.
- For custom commands (e.g., building docs or report), use:
  ```sh
  docker run -it --rm project_app:latest bash
  ```
  Then run the desired build commands inside the container.

- For LaTeX report builds, ensure `Report/Report.tex` is present.

## Troubleshooting

- If you need to install extra Python or Node packages, use an interactive shell as above.
- For persistent data, always use the volume mount.
