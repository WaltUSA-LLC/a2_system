import { Route, Routes } from "react-router-dom";

import { Grid } from "@mui/material";
import TopBar from './components/TopBar';
import ShiftView from "./components/views/ShiftView";
import SKUView from './components/views/SKUView';
import StopsViewByCode from './components/views/StopsViewByCode';
import StopsViewByMach from './components/views/StopsViewByMach';
import PQCStaffView from "./components/views/PQCStaffView";
import PQCStaffInPeriodView from "./components/views/PQCStaffInPeriodView";
import PQCSKUView from "./components/views/PQCSKUView";
import UploadView from "./components/views/UploadView";


function App() {
    return (
        <Grid container spacing={2} sx={{ width: '100%' }}>
            <Grid size={12}>
                <TopBar />
            </Grid>
            <Grid size={12}>
                <Routes>
                    <Route path="/sku-view" element={<SKUView />} />
                    <Route path="/shift-view" element={<ShiftView />} />
                    <Route path="/stops-view/code" element={<StopsViewByCode />} />
                    <Route path="/stops-view/mach" element={<StopsViewByMach />} />
                    <Route path="/pqc-view/staff" element={<PQCStaffView />} />
                    <Route path="/pqc-view/staff/period" element={<PQCStaffInPeriodView />} />
                    <Route path="/pqc-view/sku" element={<PQCSKUView />} />
                    <Route path="/upload" element={<UploadView />} />
                </Routes>
            </Grid>
        </Grid>
  );
}

export default App
