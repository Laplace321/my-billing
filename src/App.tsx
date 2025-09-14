import React from 'react'
import '../index.css'
import AssetManager from './components/AssetManager'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>资产管理系统</h1>
      </header>
      <main>
        <AssetManager />
      </main>
    </div>
  )
}

export default App