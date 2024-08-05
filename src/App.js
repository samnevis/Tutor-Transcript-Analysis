import React, { useState, useEffect } from 'react';
import './App.css';

function formatSummarizedText(summarizedText) {
  let listItems = summarizedText.split(/\d+\.\s+/);
  listItems = listItems.filter(item => item.trim() !== '');
  return listItems.map((item, index) => `${index + 1}. ${item.trim()}`).join('\n');
}

function App() {
  const [data, setData] = useState({});
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const onFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const onFileUpload = () => {
    if (!file) {
      setMessage('Please select a file to upload');
      setMessageType('error');
      return;
    }
    setMessage('Uploading file...');
    setMessageType('');
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
    .then(res => {
      if (!res.ok) {
        throw new Error('Network response was not ok');
      }
      return res.json();
    })
    .then(res => {
      setData(res);
      setMessage('File successfully uploaded');
      setMessageType('success');
      console.log(res);
    })
    .catch(error => {
      setMessage('Error uploading file');
      setMessageType('error');
      console.error('Error:', error);
    });
  };

  useEffect(() => {
    fetch("/members")
      .then(res => res.json())
      .then(res => {
        setData(res);
        console.log(res);
      });
  }, []);

  return (
    <div className="app-container">
      <div className="container">
        <h2>Transcript Analysis Tool</h2>
        <div className="file-upload-container">
          <label className="file-upload-label">
            Choose File
            <input type="file" onChange={onFileChange} />
          </label>
          {file && <span className="file-name">{file.name}</span>}
        </div>
        <button onClick={onFileUpload}>Upload</button>
        {message && <div className={`message ${messageType}`}>{message}</div>}
  
        <div>
          {(data.members && data.members.length > 0) ? (
            data.members.map((member, i) => {
              const formattedText = formatSummarizedText(member.summarized_text);
              return (
                <div key={i} className="analysis-result">
                  <p>
                    <strong>File:</strong> {member.filename}
                    <br /> <br />
                    <strong>Speaking Percentages:</strong> <br />
                    Teacher: {member.speaking_percents[0]}%, <br />
                    Student: {member.speaking_percents[1]}%<br /> 
                    <strong>Bad Words:</strong> {member.bad_words}<br />
                    <strong>Sentiments:</strong><br />
                    Teacher: {member.sentiments[0]} <br />
                    Student: {member.sentiments[1]}<br />
                    <strong>Encouragement:</strong> {member.encouragement[0]}<br />
                    <br />
                    <strong>Lesson Content Summary:</strong><br />
                    {formattedText.split('\n').map((item, index) => (
                      <React.Fragment key={index}>
                        {item}
                        <br />
                      </React.Fragment>
                    ))}
                </p>
                </div>
              );
            })
          ) : (
            <p>Upload a .vtt file</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;