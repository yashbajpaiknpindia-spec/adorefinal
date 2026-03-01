import { useEffect, useState } from 'react'

export default function App() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch('/api')
      .then(res => res.json())
      .then(data => setMessage(data.message))
  }, [])

  return (
    <div style={{ padding: 40 }}>
      <h1>Adore Clean Deployment</h1>
      <p>Backend says: {message}</p>
    </div>
  )
}