import TopBar from './components/TopBar';
import Navigation from './components/Navigation';
import WeightsView from './components/WeightsView';
import MachsView from './components/MachsView';
import StopsView from './components/StopsView';
import { Route, Routes } from "react-router-dom";
import './App.css'

function App() {
    return (
        <>
            <TopBar />
            <div className='nav-and-content'>
                <Navigation />
                <Routes>
                    <Route path="/weights-view" element={<WeightsView />} />
                    <Route path="/machs-view" element={<MachsView />} />
                    <Route path="/stops-view" element={<StopsView />} />
                </Routes>
            </div>
        </>
  );
}

export default App
