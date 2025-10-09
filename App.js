import React, { useState } from "react";
// Imports the core React library and the 'useState' Hook, which lets you store
// and manage data that changes over time in your component.

import axios from "axios";
// Imports 'axios', a popular JavaScript library used to easily send HTTP requests
// (like the POST request) to the backend server.

import "./App.css";

function App() {
  const [mode, setMode] = useState("form"); // "form" | "json"
  // State for tracking whether the user is using the multiple-text 'form' input or the raw 'json' input.

  const [texts, setTexts] = useState([{ id: 1, value: "" }]); // Dynamic array of statements
  // State that holds the array of individual text inputs when in 'form' mode. It starts with one empty box.

  const [jsonInput, setJsonInput] = useState("");
  // State to store the raw text entered by the user in the 'JSON Input' box.

  const [isJsonValid, setIsJsonValid] = useState(true);
  // State to track if the text in the 'JSON Input' box is properly formatted JSON.

  const [targetLanguage, setTargetLanguage] = useState("hindi");
  // State to store the language the user wants to translate the text into (e.g., "hindi").

  const [translatedText, setTranslatedText] = useState({});
  // State to store the translated result (an object) received back from the backend API.

  const [loading, setLoading] = useState(false);
  // State to track if a translation request is currently being processed, used to show "Translating..." and disable the button.

  // Update value for a specific statement
  const handleChange = (id, newValue) => {
    setTexts(texts.map(t => (t.id === id ? { ...t, value: newValue } : t)));
  };
  // Finds a text box by its ID and updates its content (value) in the 'texts' state.

  // Add a new statement
  const handleAdd = () => {
    setTexts([...texts, { id: texts.length + 1, value: "" }]);
  };
  // Adds a new, empty text box to the list for the user to type in.

  // Remove a statement and renumber IDs
  const handleRemove = (id) => {
    const updated = texts.filter(t => t.id !== id);
    const renumbered = updated.map((t, index) => ({ ...t, id: index + 1 }));
    setTexts(renumbered);
  };
  // Removes a text box and then re-assigns simple sequential IDs (1, 2, 3...) to the remaining boxes.

  // JSON Mode Function
  const handleJsonChange = (e) => {
    const value = e.target.value;
    setJsonInput(value);
    // Stores the raw text from the JSON textarea into the 'jsonInput' state.

    try {
      // Validates the JSON → sets isJsonValid to false if invalid.
      JSON.parse(value);
      setIsJsonValid(true);
    } catch {
      // Ensures React disables the translate button when JSON is malformed.
      setIsJsonValid(false);
    }
  };

  // Translate Function
  // Triggered when the Translate button is clicked.
  const handleTranslate = async () => {
    setLoading(true);
    // Sets loading state to true to show the user a process is running.
    try {
      let payloadText = {};
      // Initializes an empty object that will hold the text data to be sent to the backend.

      if (mode === "form") {
        // Convert array to object: key1, key2, ...
        texts.forEach((t, index) => {
          payloadText[`key${index + 1}`] = t.value;
        });
        // If in 'form' mode, it converts the array of texts into an object
        // where the keys are 'key1', 'key2', etc. (as required by the FastAPI/Pydantic model).
      } else {
        // Parses JSON mode input if selected.
        try {
          payloadText = JSON.parse(jsonInput);
        } catch (err) {
          alert("Invalid JSON format. Please correct it.");
          setLoading(false);
          return;
        }
      }
      // Sends POST request to FastAPI backend /translate
      const response = await axios.post("http://127.0.0.1:8000/translate", {
        text: payloadText,
        target_language: targetLanguage,
        user: {
          name: "rohit",
          email: "rohit@example.com"
        }
      });
       
      // Stores the translated text returned from backend in translatedText.
      setTranslatedText(response.data.translated_text);
    } 
    // Handles API errors with an alert.
    catch (error) {
      console.error("Translation error:", error);
      alert("Translation failed. Check console for details.");
    }
    setLoading(false);
    // Sets loading state back to false to enable the button again.
  };


  // UI Rendering (return)
  // The return block is what actually draws the elements on the web page:
  return (
    <div className="App" style={{ padding: "4rem", fontFamily: "Arial" }}>
      <h1>FastAPI Translator</h1>

      {/* Mode Toggle */}
      {/* Displays the two radio buttons to switch between "Form Input" and "JSON Input" modes. */}
      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            type="radio"
            value="form"
            checked={mode === "form"}
            onChange={() => setMode("form")}
          />
          Form Input
        </label>
        &nbsp;&nbsp;
        <label>
          <input
            type="radio"
            value="json"
            checked={mode === "json"}
            onChange={() => setMode("json")}
          />
          JSON Input
        </label>
      </div>

      {/* Form Mode */}
      {mode === "form" &&
        texts.map((t) => (
          <div key={t.id} style={{ marginBottom: "1rem" }}>
            <label>Text {t.id}:</label>
            <textarea
              id="txtarea" placeholder = "Enter your text..."
              value={t.value}
              onChange={(e) => handleChange(t.id, e.target.value)}
              rows="5"
              cols="60"
            />
            {texts.length > 1 && (
              <button
                type="button"
                style={{ marginLeft: "1rem" }}
                onClick={() => handleRemove(t.id)}
              >
                Remove
              </button>
            )}
          </div>
        ))}
      {mode === "form" && (
        <button type="button" onClick={handleAdd}>
          Add Statement
        </button>
      )}

      {/* JSON Mode */}
      {mode === "json" && (
        <div style={{ marginBottom: "1rem" }}>
          <label>Enter JSON Object:</label>
          <textarea
            id="txtarea"
            className={isJsonValid ? "valid-json" : "invalid-json"}
            value={jsonInput}
            onChange={handleJsonChange}
            rows="10"
            cols="60"
            placeholder='{"key1":"Hello","key2":"World"}'
          />
          {!isJsonValid && (
            <p style={{ color: "red" }}>⚠ Invalid JSON format</p>
          )}
        </div>
      )}

      {/* Target Language */}
      <div style={{ marginTop: "1rem" }}>
        <label>Target Language:</label>
        <select
          id="select"
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
        >
          <option value="hindi">Hindi</option>
          <option value="english">English</option>
          <option value="marathi">Marathi</option>
        </select>
      </div>

      {/* Translate Button */}
      <button
        id="btn"
        onClick={handleTranslate}
        disabled={loading || (mode === "json" && !isJsonValid)}
      >
        {loading ? "Translating..." : "Translate"}
      </button>

      {/* Translated Output */}
      {Object.keys(translatedText).length > 0 && (
        <div style={{ marginTop: "2rem", textAlign: "left" }}>
          <h2>Translated Text:</h2>
          {/* ✅ Use JSON.stringify to render nested objects safely */}
          <pre style={{ background: "#f4f4f4", padding: "1rem", borderRadius: "8px", whiteSpace: "pre-wrap" }}>
            {JSON.stringify(translatedText, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
