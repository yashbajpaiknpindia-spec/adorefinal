import express from "express"
import path from "path"
import { fileURLToPath } from "url"
import Database from "better-sqlite3"

const app = express()
const PORT = process.env.PORT || 3000

// Proper ESM dirname fix
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Database
const db = new Database("./database.db")

// API route
app.get("/api", (req, res) => {
  res.json({ message: "Server is running successfully!" })
})

// Serve frontend correctly
const distPath = path.resolve(__dirname, "dist")

app.use(express.static(distPath))

app.get("*", (req, res) => {
  res.sendFile(path.join(distPath, "index.html"))
})

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})