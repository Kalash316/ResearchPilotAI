
import { useState, useRef } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedSource, setSelectedSource] = useState("");
  const fileInputRef = useRef(null);

  const uploadPDFs = async () => {
    if (selectedFiles.length === 0) {
      setUploadStatus("Please select at least one PDF file.");
      return;
    }

    const invalidFile = selectedFiles.find(
      (file) => !file.name.toLowerCase().endsWith(".pdf")
    );

    if (invalidFile) {
      setUploadStatus("Only PDF files are allowed.");
      return;
    }

    const oversizedFile = selectedFiles.find(
      (file) => file.size > 20 * 1024 * 1024
    );

    if (oversizedFile) {
      setUploadStatus(`${oversizedFile.name} exceeds the 20 MB limit.`);
      return;
    }

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    setUploading(true);
    setUploadStatus("Uploading and processing your PDF files...");

    try {
      const response = await fetch(`${API_URL}/upload-pdfs`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed.");
      }

      const successfulFiles = data.files || [];

      setUploadedFiles((previousFiles) => {
        const updatedFiles = [...previousFiles];

        successfulFiles.forEach((file) => {
          const existingIndex = updatedFiles.findIndex(
            (item) => item.filename === file.filename
          );

          if (existingIndex >= 0) {
            updatedFiles[existingIndex] = file;
          } else {
            updatedFiles.push(file);
          }
        });

        return updatedFiles;
      });

      // Automatically select the first PDF uploaded in this batch.
      if (successfulFiles.length > 0) {
        setSelectedSource(successfulFiles[0].filename);
      }

      setUploadStatus(
        `Success! ${data.total_files} PDF file(s) processed, ` +
          `${data.total_chunks} text chunks created.`
      );

      setSelectedFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      setUploadStatus(
        error.message ||
          "Could not connect to the backend. Check whether FastAPI is running."
      );
    } finally {
      setUploading(false);
    }
  };

  const askQuestion = async (event) => {
    event.preventDefault();

    const userQuestion = question.trim();

    if (!userQuestion || asking) {
      return;
    }

    if (!selectedSource) {
      setUploadStatus("Please upload and select a PDF before asking a question.");
      return;
    }

    setMessages((previousMessages) => [
      ...previousMessages,
      { role: "user", content: userQuestion },
    ]);

    setQuestion("");
    setAsking(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          source: selectedSource,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to generate an answer.");
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content:
            `Error: ${error.message}. ` +
            "Please check that your backend is running.",
          sources: [],
        },
      ]);
    } finally {
      setAsking(false);
    }
  };

  const newChat = () => {
    setMessages([]);
    setQuestion("");
  };

  const styles = {
    page: {
      minHeight: "100vh",
      background: "#f4f7fb",
      padding: "24px 16px",
      fontFamily: "Arial, sans-serif",
      color: "#172033",
      boxSizing: "border-box",
    },
    container: {
      maxWidth: "850px",
      margin: "0 auto",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      gap: "12px",
      flexWrap: "wrap",
      marginBottom: "24px",
    },
    title: {
      margin: 0,
      fontSize: "28px",
      color: "#243b80",
    },
    subtitle: {
      color: "#64748b",
      marginTop: "8px",
      marginBottom: 0,
      fontSize: "14px",
    },
    panel: {
      background: "#ffffff",
      border: "1px solid #e2e8f0",
      borderRadius: "14px",
      padding: "20px",
      marginBottom: "18px",
      boxShadow: "0 3px 12px rgba(15, 23, 42, 0.04)",
    },
    sectionTitle: {
      margin: "0 0 8px",
      fontSize: "18px",
    },
    description: {
      color: "#64748b",
      fontSize: "14px",
      lineHeight: 1.6,
    },
    input: {
      display: "block",
      width: "100%",
      margin: "14px 0",
      boxSizing: "border-box",
      padding: "10px",
      border: "1px solid #cbd5e1",
      borderRadius: "8px",
      background: "#ffffff",
    },
    primaryButton: {
      background: "#3155c6",
      color: "#ffffff",
      border: "none",
      borderRadius: "8px",
      padding: "11px 16px",
      cursor: "pointer",
      fontWeight: 600,
    },
    secondaryButton: {
      background: "#e8edff",
      color: "#243b80",
      border: "none",
      borderRadius: "8px",
      padding: "10px 14px",
      cursor: "pointer",
      fontWeight: 600,
    },
    status: {
      marginTop: "12px",
      fontSize: "14px",
      lineHeight: 1.5,
      overflowWrap: "anywhere",
    },
    chat: {
      display: "flex",
      flexDirection: "column",
      gap: "14px",
      minHeight: "180px",
      maxHeight: "480px",
      overflowY: "auto",
      padding: "8px 0 18px",
    },
    userMessage: {
      alignSelf: "flex-end",
      maxWidth: "85%",
      padding: "12px 14px",
      borderRadius: "12px 12px 2px 12px",
      background: "#e8edff",
      lineHeight: 1.6,
      whiteSpace: "pre-wrap",
      overflowWrap: "anywhere",
    },
    assistantMessage: {
      alignSelf: "flex-start",
      maxWidth: "95%",
      padding: "12px 14px",
      borderRadius: "12px 12px 12px 2px",
      background: "#f1f5f9",
      lineHeight: 1.7,
      whiteSpace: "pre-wrap",
      overflowWrap: "anywhere",
    },
    chatForm: {
      display: "flex",
      gap: "10px",
      alignItems: "center",
    },
    questionInput: {
      flex: 1,
      minWidth: 0,
      padding: "13px",
      border: "1px solid #cbd5e1",
      borderRadius: "8px",
      fontSize: "15px",
    },
    select: {
      display: "block",
      width: "100%",
      margin: "12px 0",
      padding: "12px",
      border: "1px solid #cbd5e1",
      borderRadius: "8px",
      background: "#ffffff",
      fontSize: "14px",
    },
  };

  return (
    <main style={styles.page}>
      <div style={styles.container}>
        <header style={styles.header}>
          <div>
            <h1 style={styles.title}>ResearchPilotAI</h1>
            <p style={styles.subtitle}>
              Your AI research assistant, powered by local AI.
            </p>
          </div>

          <button
            type="button"
            style={styles.secondaryButton}
            onClick={newChat}
          >
            New Chat
          </button>
        </header>

        <section style={styles.panel}>
          <h2 style={styles.sectionTitle}>Upload Research PDFs</h2>

          <p style={styles.description}>
            Upload your PDFs, then select one document to ask questions about.
            Maximum size: 20 MB per file.
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            style={styles.input}
            onChange={(event) => {
              setSelectedFiles(Array.from(event.target.files || []));
              setUploadStatus("");
            }}
          />

          {selectedFiles.length > 0 && (
            <ul>
              {selectedFiles.map((file, index) => (
                <li key={`${file.name}-${index}`}>
                  {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                </li>
              ))}
            </ul>
          )}

          <button
            type="button"
            style={{
              ...styles.primaryButton,
              opacity: uploading ? 0.65 : 1,
            }}
            onClick={uploadPDFs}
            disabled={uploading}
          >
            {uploading ? "Processing PDFs..." : "Upload PDF"}
          </button>

          {uploadStatus && (
            <p role="status" style={styles.status}>
              {uploadStatus}
            </p>
          )}

          {uploadedFiles.length > 0 && (
            <div style={{ marginTop: "18px" }}>
              <h3 style={{ fontSize: "15px" }}>Select PDF for your questions</h3>

              <select
                aria-label="Select a PDF to ask questions about"
                style={styles.select}
                value={selectedSource}
                onChange={(event) => setSelectedSource(event.target.value)}
              >
                <option value="">-- Select a PDF --</option>
                {uploadedFiles.map((file) => (
                  <option key={file.filename} value={file.filename}>
                    {file.filename}
                  </option>
                ))}
              </select>

              {uploadedFiles.map((file) => (
                <p
                  key={file.filename}
                  style={{ ...styles.description, margin: "6px 0" }}
                >
                  {file.filename} — {file.pages} pages, {file.chunks} chunks
                </p>
              ))}
            </div>
          )}
        </section>

        <section style={styles.panel}>
          <h2 style={styles.sectionTitle}>Ask Your Research Assistant</h2>

          <p style={styles.description}>
            Questions will be searched in the selected PDF.
          </p>

          <p style={{ ...styles.description, fontWeight: 600 }}>
            Selected document: {selectedSource || "No PDF selected"}
          </p>

          <div
            style={styles.chat}
            aria-live="polite"
            aria-label="Chat messages"
          >
            {messages.length === 0 && (
              <p style={styles.description}>
                Try: "What is the main topic of my uploaded PDF?"
              </p>
            )}

            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                style={
                  message.role === "user"
                    ? styles.userMessage
                    : styles.assistantMessage
                }
              >
                <strong>
                  {message.role === "user" ? "You" : "ResearchPilotAI"}
                </strong>

                <div style={{ marginTop: "5px" }}>{message.content}</div>

                {message.sources && message.sources.length > 0 && (
                  <div
                    style={{
                      marginTop: "12px",
                      paddingTop: "10px",
                      borderTop: "1px solid #dbe2ea",
                      fontSize: "13px",
                    }}
                  >
                    <strong>Sources</strong>
                    <ul style={{ paddingLeft: "20px", marginBottom: 0 }}>
                      {message.sources.map((source, sourceIndex) => (
                        <li
                          key={`${source.source}-${source.page}-${sourceIndex}`}
                        >
                          {source.source}, page {source.page}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}

            {asking && (
              <div style={styles.assistantMessage}>
                ResearchPilotAI is thinking...
              </div>
            )}
          </div>

          <form onSubmit={askQuestion} style={styles.chatForm}>
            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about your research..."
              aria-label="Your question"
              style={styles.questionInput}
              disabled={asking}
            />

            <button
              type="submit"
              style={{
                ...styles.primaryButton,
                opacity: asking ? 0.65 : 1,
              }}
              disabled={asking || !question.trim() || !selectedSource}
            >
              {asking ? "Thinking..." : "Ask"}
            </button>
          </form>
        </section>

        <p
          style={{
            textAlign: "center",
            color: "#64748b",
            fontSize: "12px",
          }}
        >
          ResearchPilotAI · Local LLM · RAG · ChromaDB
        </p>
      </div>
    </main>
  );
}

export default App;
