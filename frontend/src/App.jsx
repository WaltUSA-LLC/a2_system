import { Route, Routes } from "react-router-dom";

import { Grid } from "@mui/material";
import TopBar from './components/TopBar';
import ShiftView from "./components/views/ShiftView";
import SKUView from './components/views/SKUView';
import MachsView from './components/views/MachsView';
import StopsViewByCode from './components/views/StopsViewByCode';
import StopsViewByMach from './components/views/StopsViewByMach';
import PQCView from "./components/views/PQCView";


function App() {
    return (
        <Grid container spacing={2} sx={{ width: '100%' }}>
            <Grid size={12}>
                <TopBar />
            </Grid>
            <Grid size={12}>
                <Routes>
                    {/* <Route path="/machs-view" element={<MachsView />} /> */}
                    <Route path="/sku-view" element={<SKUView />} />
                    <Route path="/shift-view" element={<ShiftView />} />
                    <Route path="/stops-view/code" element={<StopsViewByCode />} />
                    <Route path="/stops-view/mach" element={<StopsViewByMach />} />
                    <Route path="/pqc-view" element={<PQCView />} />
                </Routes>
            </Grid>
        </Grid>
  );
}

export default App
