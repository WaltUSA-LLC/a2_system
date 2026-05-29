import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView"

function PQCView() {
    const [contentRec, setContentRec] = useState([]);

    const columns = [
        {
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'MachID',
            headerName: 'Mach ID',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Style_Code',
            headerName: 'Style Code',
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
            headerName: 'Defects',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Total Defects',
        },
        {
            field: 'toeHole',
            headerName: 'Hole',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'brokenNDL',
            headerName: 'N-Brok',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Broken',
        },
        {
            field: 'missNDL',
            headerName: 'N-Miss',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Missing',
        },
        {
            field: 'missYarn',
            headerName: 'Y-Brok',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Broken',
        },
        {
            field: 'fanYarn',
            headerName: 'Y-Rtn',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Return',
        },
        {
            field: 'feisha',
            headerName: 'Y-Fly',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Fly',
        },
        {
            field: 'logoIssue',
            headerName: 'Logo',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Logo Issue',
        },
        {
            field: 'dirty',
            headerName: 'Stain',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'other',
            headerName: 'Other',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        
    ];


    function loadData(start, end, shift) {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
        const promise = axios.get(`${API_BASE_URL}/base/pqc`, {
                            params: {
                                start,
                                end,
                                shift,
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
            <TableView col={columns} rec={contentRec} loadData={loadData}/>
        </>
    );
}

export default PQCView;

