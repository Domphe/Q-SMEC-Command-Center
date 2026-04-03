import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Overview from './pages/Overview'
import EmailTriage from './pages/EmailTriage'
import Clients from './pages/Clients'
import Pipeline from './pages/Pipeline'
import Repos from './pages/Repos'
import Notes from './pages/Notes'
import CommandCenter from './pages/CommandCenter'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/emails" element={<EmailTriage />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/repos" element={<Repos />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/command-center" element={<CommandCenter />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
