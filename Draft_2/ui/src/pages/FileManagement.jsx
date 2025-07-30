import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function FileManagement() {
  const [files, setFiles] = React.useState([]);
  const [uploading, setUploading] = React.useState(false);

  React.useEffect(() => {
    fetch("/api/files")
      .then(res => res.json())
      .then(data => setFiles(data))
      .catch(() => setFiles([]));
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch("/api/files/upload", {
        method: "POST",
        body: formData,
      });
    } catch {
      // handle error
    }
    setUploading(false);
    // Refresh file list
    fetch("/api/files")
      .then(res => res.json())
      .then(data => setFiles(data))
      .catch(() => setFiles([]));
  };

  const handleDownload = async (filename) => {
    window.location.href = `/api/files/download/${filename}`;
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
    >
      <Container maxWidth={false} sx={{ maxWidth: "60vw", width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2} width="100%">
          <Typography variant="h4" gutterBottom>
            File Management
          </Typography>
          <input type="file" onChange={handleUpload} disabled={uploading} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {files.length === 0 ? "No files found." : "Files:"}
          </Typography>
          <ul>
            {files.map((file) => (
              <li key={file}>
                {file}{" "}
                <button onClick={() => handleDownload(file)}>Download</button>
              </li>
            ))}
          </ul>
        </Box>
      </Container>
    </Box>
  );
}

export default FileManagement;