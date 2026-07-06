import { useState } from 'react';
import axios from "axios";
import Tooltip from "@mui/material/Tooltip";

import TableView from "./TableView";
import { SKUChartModal } from '../modals/ChartModal';
import { MachDetailTableModal } from '../modals/TableModal';
import { renderHeaderWithUnit } from "../utils";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function SKUView() {
    const [contentRec, setContentRec] = useState([]);
    const [modalRec, setModalRec] = useState(null);
    const [chartOpen, setChartOpen] = useState(false); 
    const [tableOpen, setTableOpen] = useState(false);
    const [metaData, setMetaData] = useState({});

    const columns = [
        {
            field: 'Style_Code',
            headerName: 'Style Code',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'MES_prs',
            renderHeader: () => renderHeaderWithUnit('MES', 'PRS'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'NAU_prs',
            renderHeader: () => renderHeaderWithUnit('NAU', 'PRS'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Discard_percent',
            renderHeader: () => renderHeaderWithUnit('Discard', '%'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            renderCell: ({ row, value }) => {
                const discardPrs = row.Discard_prs ?? "N/A";
                return (
                    <Tooltip title={`Discard: ${discardPrs} prs`} arrow>
                        <span>{value.toFixed(1)}%</span>
                    </Tooltip>
                );
            },
        },
        {
            field: 'defects',
            renderHeader: () => renderHeaderWithUnit('Defect', 'PRS'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'PQC defects',
        },
        {
            field: 'pqc_cnt',
            headerName: 'Checks',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'PQC checks',
        },
        {
            field: 'ON_Time_Occupation',
            renderHeader: () => renderHeaderWithUnit('ON Time', '%'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value == null ? null : value * 100,
            valueFormatter: (value) => value == null ? '' : `${value.toFixed(1)}%`,
        },
        {
            field: 'Efficiency',
            renderHeader: () => renderHeaderWithUnit('Mach Eff', '%'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value == null ? null : value * 100,
            valueFormatter: (value) => value == null ? '' : `${value.toFixed(1)}%`,
        },
        {
            field: 'Mach_cnt',
            headerName: 'Mach Count',
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

    function handleRowClick(params){
        //console.log("clicked row:", params.row);
        const [date, shift_time] = params.row.Shift_Start_Time.split(/\s+/);
        const shift = shift_time==="07:00:00"? 1 : 2;
        //console.log(date);
        //console.log(shift);
        axios.get(`${API_BASE_URL}/base/sku/detail?start=${date}&end=${date}&shift=${shift}&style=${params.row.Style_Code}`).then(
            resp => {
                const records = resp.data.content ?? [];
                const staff = resp.data.staff ?? [];
                setModalRec(records);
                setMetaData({date_time: params.row.Shift_Start_Time, 
                    style:params.row.Style_Code,
                    ko: staff[0]?.KO ? staff[0].KO : "None", 
                    tech: staff[0]?.Tech ? staff[0].Tech : "None", 
                    creeler: staff[0]?.Creeler ? staff[0].Creeler : "None", 
                    yarner: staff[0]?.Yarner ? staff[0].Yarner : "None"
                })
            }
        ).catch((err) => {
            console.error(err);
            setModalRec([]);
            setTableOpen(false);
            return;
        });
        setTableOpen(true);
    }

    function loadData(start, end, shift) {
        const promise = axios.get(`${API_BASE_URL}/base/sku`, {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            setContentRec(records);
                        }).catch((err) => {
                            setChartOpen(false);
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }

    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} handleOpenChart={handleOpenChart} handleRowClick={handleRowClick}/>
            { chartOpen ? (
                <SKUChartModal open={chartOpen} onClose={handleCloseChart} rec={contentRec} />) : 
                null}
            {(tableOpen && modalRec) ? <MachDetailTableModal open={tableOpen} 
                                        onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                        rec={modalRec} 
                                        metaData={metaData}/> : null}
        </>
    );
}

export default SKUView;