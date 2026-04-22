import { useState } from 'react';
import axios from 'axios';

import TableView from "./TableView"
import { MachStopTableModalView } from "./TableModalView";

function StopsViewByMach() {
    const [tableOpen, setTableOpen] = useState(false);
    const [rec, setRec] = useState(null);
    const [time, setTime] = useState({})

    const columns = [
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
            field: 'freq',
            headerName: 'Frequency',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        
    ];

    function handleRowClick(params, event){
        //console.log("clicked row:", params.row);
        axios.get(`http://localhost:8000/base/stop/mach/detail?start=${time.start}&end=${time.end}&shift=${time.shift}&mach=${params.row.MachID}&style=${params.row.Style_Code}`).then(
            resp => {
                const records = resp.data.content ?? [];
                setRec(records);
            }
        ).catch((err) => {
            console.error(err);
            setRec([]);
            setTableOpen(false);
        });
        setTableOpen(true);
    }

    return (
        <>
            <TableView url="http://localhost:8000/base/stop/mach" col={columns} handleRowClick={handleRowClick} markDownSelectedTime={setTime}/>
            {(tableOpen && rec) ? <MachStopTableModalView open={tableOpen} onClose={()=>{setTableOpen(false); setRec(null)}} rec={rec}/> : null}
        </>
    );
}

export default StopsViewByMach;