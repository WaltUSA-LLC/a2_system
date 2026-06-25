import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView";
import { PQCStaffDetailTableModal } from '../modals/TableModal';
import { PQCStaffInPeriodChartModal } from '../modals/ChartModal';
import { renderHeaderWithUnit } from "../utils";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PQCStaffInPeriodView() {
    const [contentRec, setContentRec] = useState([]);
    const [chartOpen, setChartOpen] = useState(false); 

    const columns = [
        {
            field: 'Name',
            headerName: 'Name',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Role',
            headerName: 'Role',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'pqc_cnt',
            headerName: 'Checks',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Check Counting',
        },
        {
            field: 'defects',
            renderHeader: (params) => renderHeaderWithUnit('Defect', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Total Defects',
        },
        {
            field: 'toeHole',
            renderHeader: () => renderHeaderWithUnit('Hole', 'PCS'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'brokenNDL',
            renderHeader: (params) => renderHeaderWithUnit('N-Brok', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Broken',
        },
        {
            field: 'missNDL',
            renderHeader: (params) => renderHeaderWithUnit('N-Miss', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Missing',
        },
        {
            field: 'missYarn',
            renderHeader: (params) => renderHeaderWithUnit('Y-Miss', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Miss',
        },
        {
            field: 'fanYarn',
            renderHeader: (params) => renderHeaderWithUnit('Y-Rtn', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Misplace',
        },
        {
            field: 'feisha',
            renderHeader: (params) => renderHeaderWithUnit('Y-Fly', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Fly',
        },
        {
            field: 'logoIssue',
            renderHeader: (params) => renderHeaderWithUnit('Logo', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Logo Issue',
        },
        {
            field: 'dirty',
            headerName: 'Stain',
            renderHeader: (params) => renderHeaderWithUnit('Stain', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'other',
            renderHeader: (params) => renderHeaderWithUnit('Other', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        
    ];

    function handleOpenChart() {
        setChartOpen(true);
    }

    function handleCloseChart() {
        setChartOpen(false);
    }

    function loadData(start, end) {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
        const promise = axios.get(`${API_BASE_URL}/base/pqc/staff/period`, {
                            params: {
                                start,
                                end,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            setContentRec(records);
                        }).catch((err) => {
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }

    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} hasShift={false} handleOpenChart={handleOpenChart}/>
            {chartOpen ? (<PQCStaffInPeriodChartModal open={chartOpen} 
                                            onClose={handleCloseChart}  
                                            rec={contentRec} />) : null}
        </>
    );
}

export default PQCStaffInPeriodView;

