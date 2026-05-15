import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/Login/LoginPage';
import Dashboard from './pages/Dashboard';
import PlaceholderPage from './pages/PlaceholderPage';
import CourseCategoryPage from './pages/CourseCategoryPage';
import CoursePage from './pages/CoursePage';
import HotelPage from './pages/HotelPage';
import VendorPage from './pages/VendorPage';
import TnaPage from './pages/TnaPage';
import TrainingMasterPage from './pages/TrainingMasterPage';
import EmployeePage from './pages/EmployeePage';
import TrainingEvaluationPage from './pages/TrainingEvaluationPage';
import TrainingEvaluationEmployeePage from './pages/TrainingEvaluationEmployeePage';
import AiDashboard from './pages/AiDashboard';
import AiChatPage from './pages/AiChatPage';
import AiAdminPage from './pages/AiAdminPage';
import AiStartChatPage from './pages/AiStartChatPage';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      
      {/* Training Sub-pages */}
      <Route path="/training-master" element={<TrainingMasterPage />} />
      <Route path="/evaluation" element={<TrainingEvaluationPage />} />
      <Route path="/evaluation-employee" element={<TrainingEvaluationEmployeePage />} />
      <Route path="/employee" element={<EmployeePage />} />
      <Route path="/hotel" element={<HotelPage />} />
      
      {/* Settings Sub-pages */}
      <Route path="/category" element={<CourseCategoryPage />} />
      <Route path="/courses" element={<CoursePage />} />
      <Route path="/vendor" element={<VendorPage />} />
      <Route path="/tna" element={<TnaPage />} />
      
      {/* AI Assistant pages */}
      <Route path="/ai-dashboard" element={<AiDashboard />} />
      <Route path="/ai-chat" element={<AiChatPage />} />
      <Route path="/ai-admin" element={<AiAdminPage />} />
      <Route path="/ai-start" element={<AiStartChatPage />} />
      
      {/* Default redirect to login or dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;

