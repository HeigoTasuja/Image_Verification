import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

function App() {
  const [currentImage, setCurrentImage] = useState(null)
  const [correctedLabel, setCorrectedLabel] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [allDone, setAllDone] = useState(false)

  const fetchNextImage = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(`${VITE_API_BASE_URL}/api/images/next`)


      if (response.status === 204) {
        setAllDone(true)
        setCurrentImage(null)
      } else {
        setCurrentImage(response.data)
        setCorrectedLabel('')
      }
    } catch (error) {
      console.error("Error fetching image:", error)
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    fetchNextImage()
  }, [])


  const submitReview = async (label) => {
    if (!currentImage) return

    try {
      await axios.post(`${VITE_API_BASE_URL}/api/labels`, {
        image_id: currentImage.id,
        label: label,
      })
      fetchNextImage()
    } catch (error) {
      console.error("Error submitting label:", error)
    }
  }


  const handleConfirm = () => {
    submitReview(currentImage.suggested_label)
  }

  const handleCorrect = () => {
    if (!correctedLabel.trim()) {
      alert("Please enter a corrected label.")
      return
    }
    submitReview(correctedLabel.trim())
  }


  if (isLoading) {
    return <div className="loading-message">Loading next image...</div>
  }

  if (allDone) {
    return <div className="all-done-message">All images reviewed! Thank you!</div>
  }

  if (!currentImage) {
    return <div className="loading-message">Could not load an image. Please try again.</div>
  }

  return (
    <div className="reviewer-container">
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
        <input
          type="text"
          placeholder="Enter correct label"
          value={correctedLabel}
          onChange={(e) => setCorrectedLabel(e.target.value)}
        />
        <button
          className="btn btn-correct"
          onClick={handleCorrect}
          disabled={!correctedLabel.trim()}
        >
          Correct
        </button>
      </div>
    </div>
  )
}

export default App
