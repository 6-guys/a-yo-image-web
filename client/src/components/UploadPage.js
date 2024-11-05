import React, { useState } from "react";
// import "./UploadPage.css"; // CSS 파일 임포트
import "../styles/UploadPage.css";
function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [resultMessage, setResultMessage] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewImage(reader.result);
    };
    if (file) {
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      console.log("Upload Success:", result);
      setResultMessage(result.message);
    } catch (error) {
      console.error("Upload Error:", error);
    }
  };

  const handleGenerateMotion = async () => {
    try {
      const response = await fetch("http://localhost:5000/motion", {
        method: "POST",
      });
      const result = await response.json();
      console.log("Motion Generation Success:", result);
      setResultMessage("Motion generated successfully!");
    } catch (error) {
      console.error("Motion Generation Error:", error);
    }
  };

  return (
    <div className="upload-page">
      <h1>사진 업로드</h1>

      <div className="button-container">
        <label className="upload-button">
          사진 선택
          <input
            type="file"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
        </label>
        <button onClick={handleUpload} className="upload-button">
          업로드
        </button>
        <button
          onClick={handleGenerateMotion}
          className="generate-motion-button"
        >
          모션 만들기
        </button>
      </div>

      <div className="image-container">
        {previewImage ? (
          <img src={previewImage} alt="Preview" />
        ) : (
          <img src="default.png" alt="Default" />
        )}
      </div>

      <p>{resultMessage}</p>
    </div>
  );
}

export default UploadPage;
