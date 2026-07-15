import { Route, Routes } from 'react-router'
import AppLayout from '../components/layout/AppLayout.jsx'
import DashboardPage from '../features/dashboard/DashboardPage.jsx'
import NotFoundPage from '../features/not-found/NotFoundPage.jsx'
import PredictionPage from '../features/predictions/PredictionPage.jsx'
import RunReportPage from '../features/reports/RunReportPage.jsx'
import RunProgressPage from '../features/runs/RunProgressPage.jsx'
import RunResultsPage from '../features/runs/RunResultsPage.jsx'
import UploadPage from '../features/upload/UploadPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="runs/:runId/progress" element={<RunProgressPage />} />
        <Route path="runs/:runId/results" element={<RunResultsPage />} />
        <Route path="runs/:runId/report" element={<RunReportPage />} />
        <Route path="predict/:modelId" element={<PredictionPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
