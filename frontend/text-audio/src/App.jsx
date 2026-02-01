import { useState } from "react";
import "./App.css";

function App() {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("http://localhost:5000/convert", {
        method: "POST",
        body: formData,
      });

      const blob = await response.blob();
      setAudioUrl(URL.createObjectURL(blob));
    } catch (err) {
      alert("Error converting image");
    }

    setLoading(false);
  };

  return (
    <>
    <div className="container">
      <h1>🔊 Image to Audio Converter</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => handleUpload(e.target.files[0])}
      />
     <div></div>
      {loading && <p>Processing...</p>}

      {audioUrl && (
        <audio controls src={audioUrl} />
      )}
    </div>
    </>
  );
}

export default App;
