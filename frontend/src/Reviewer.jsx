import { useState, useEffect } from 'react';
import axios from 'axios';


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

function Reviewer() {
  const [currentImage, setCurrentImage] = useState(null);
  const [correctedLabel, setCorrectedLabel] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [allDone, setAllDone] = useState(false);
  const [stats, setStats] = useState(null);
  const [lastSubmission, setLastSubmission] = useState(null);
  const [undoTimer, setUndoTimer] = useState(null);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchNextImage = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/images/next`);
      if (response.status === 204) {
        setAllDone(true);
        setCurrentImage(null);
      } else {
        setCurrentImage(response.data);
        setCorrectedLabel('');
      }
    } catch (error) {
      console.error("Error fetching image:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const commitSubmission = () => {
    setLastSubmission(null);
    setUndoTimer(null);
    fetchNextImage();
  };

  const handleUndo = async () => {
    if (!lastSubmission) return;

    clearTimeout(undoTimer);
    setUndoTimer(null);

    const submissionToUndo = { ...lastSubmission };
    setLastSubmission(null);
    setIsLoading(true);

    try {
      await axios.delete(`${API_BASE_URL}/api/labels/${submissionToUndo.id}`);
      
      fetchStats();
      setCurrentImage(submissionToUndo.image);
      setCorrectedLabel(
        submissionToUndo.label === submissionToUndo.image.suggested_label ? '' : submissionToUndo.label
      );
    } catch (error) {
      console.error("Error undoing label:", error);
      fetchNextImage();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNextImage();
    fetchStats();
    

    return () => {
      if (undoTimer) clearTimeout(undoTimer);
    };
  }, []);

  const submitReview = async (label) => {
    if (!currentImage) return;

    if (undoTimer) clearTimeout(undoTimer);

    const imageBeingReviewed = currentImage;
    setCurrentImage(null);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/labels`, {
        image_id: imageBeingReviewed.id,
        label: label,
      });

      const newLabel = response.data; 

      setIsLoading(false);
      fetchStats();

      setLastSubmission({
        id: newLabel.id,
        label: newLabel.label,
        image: imageBeingReviewed,
      });

      const timerId = setTimeout(commitSubmission, 3000);
      setUndoTimer(timerId);

    } catch (error) {
      console.error("Error submitting label:", error);
      setCurrentImage(imageBeingReviewed);
      setIsLoading(false);
    }
  };

  const handleConfirm = () => {
    submitReview(currentImage.suggested_label);
  };

  const handleCorrect = () => {
    if (!correctedLabel.trim()) {
      alert("Please add label before submitting correction.");
      return;
    }
    submitReview(correctedLabel.trim());
  };

  return (
    <div className="main-layout">
      <aside className="sidebar">
        <h2>Instructions</h2>
        <p>
          Review the image and the model's suggested label.
        </p>
        <ul>
          <li>If the suggestion is correct, click <strong>"Confirm"</strong>.</li>
          <li>If the suggestion is wrong, type the correct label and click <strong>"Correct"</strong>.</li>
          <li>To undo your last submission, click <strong>"Undo"</strong>, <strong>You have 3 seconds!</strong></li>
        </ul>
        <p>Your feedback will be used to retrain the model. Thank you!</p>

        <hr />

        <h2>Statistics</h2>
        {isLoading && !stats && <p>Loading stats...</p>}
        {stats && (
          <div className="stats-container">
            <div className="stat-item">
              <h3>{stats.total_processed}</h3>
              <p>Total Reviewed</p>
            </div>
            <div className="stat-item">
              <h3>{stats.accuracy.toFixed(1)}%</h3>
              <p>Model Accuracy</p>
            </div>
          </div>
        )}
      </aside>

      <main className="reviewer-container">
        {lastSubmission && (
          <div className="undo-toast">
            <p>Label '<strong>{lastSubmission.label}</strong>' saved.</p>
            <button onClick={handleUndo} className="btn btn-undo">
              Undo
            </button>
          </div>
        )}

        {isLoading && !lastSubmission && <div className="loading-message">Loading...</div>}

        {allDone && <div className="all-done-message">All images reviewed! Thank you!</div>}

        {!isLoading && !allDone && currentImage && !lastSubmission && (
          <>
            <h2>Image Review</h2>
            <div className="image-container">
              <img src={currentImage.url} alt={`Review image ${currentImage.id}`} />
            </div>

            <div className="suggestion-info">
              <h3>Model Suggestion: <strong>{currentImage.suggested_label}</strong></h3>
              <p>Confidence: {Math.round(currentImage.confidence * 100)}%</p>
            </div>

            <div className="action-buttons">
              <button className="btn btn-confirm" onClick={handleConfirm}>
                Confirm
              </button>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid #eee', margin: '2rem 0' }} />

            <div className="correction-form">
              <label htmlFor="correction-input" style={{ display: 'none' }}>Corrected Label</label>
              <input
                type="text"
                placeholder="Enter correct label"
                value={correctedLabel}
                onChange={(e) => setCorrectedLabel(e.target.value)}
                id="correction-input"
                name="correction-input"
              />
              <button
                className="btn btn-correct"
                onClick={handleCorrect}
              >
                Correct
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default Reviewer;