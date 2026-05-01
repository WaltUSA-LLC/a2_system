import { Route, Routes } from "react-router-dom";
import './App.css'

import TopBar from './components/TopBar';
import Navigation from './components/Navigation';
import ShiftView from "./components/views/ShiftView";
import SKUView from './components/views/SKUView';
import MachsView from './components/views/MachsView';
import StopsViewByCode from './components/views/StopsViewByCode';
import StopsViewByMach from './components/views/StopsViewByMach';


function App() {
    return (
        <>
            <TopBar />
            <div className='nav-and-content'>
                <Navigation />
                <Routes>
                    {/* <Route path="/machs-view" element={<MachsView />} /> */}
                    <Route path="/sku-view" element={<SKUView />} />
                    <Route path="/shift-view" element={<ShiftView />} />
                    <Route path="/stops-view/code" element={<StopsViewByCode />} />
                    <Route path="/stops-view/mach" element={<StopsViewByMach />} />
                </Routes>
            </div>
        </>
  );
}

export default App
