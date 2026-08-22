import React from 'react'
import ReactDOM from 'react-dom/client'
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import './index.css'

import NavBar from './components/NavBar'
import Dashboard from './pages/Dashboard'
import RunHistroy from './pages/RunHistory'
import RunDetail from './pages/RunDetail'
import Settings from './pages/Settings'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/runs" element={<RunHistroy />} />
            <Route path="/runs/:id" element={<RunDetail />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  </React.StrictMode>
)
