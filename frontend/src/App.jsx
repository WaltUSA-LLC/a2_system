import { Route, Routes } from "react-router-dom";
import './App.css'

import TopBar from './components/TopBar';
import Navigation from './components/Navigation';
import SKUView from './components/SKUView';
import MachsView from './components/MachsView';
import StopsView from './components/StopsView';
import StopsViewByCode from './components/StopsViewByCode';


function App() {
    return (
        <>
            <TopBar />
            <div className='nav-and-content'>
                <Navigation />
                <Routes>
                    <Route path="/machs-view" element={<MachsView />} />
                    <Route path="/sku-view" element={<SKUView />} />
                    <Route path="/stops-view/time" element={<StopsView />} />
                    <Route path="/stops-view/code" element={<StopsViewByCode />} />
                </Routes>
            </div>
        </>
  );
}

export default App
