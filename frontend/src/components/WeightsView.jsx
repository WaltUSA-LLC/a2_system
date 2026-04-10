import { useState, useEffect } from 'react';
import axios from "axios";
import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';




function WeightsView() {
    const [rec, setRec] = useState([]);
    const [col, setCol] = useState([]);

    useEffect(()=>{
        axios.get("http://localhost:8000/base/mes")
        .then((resp) => {
            console.log(resp.data);
            setCol(resp.data.columns);
            setRec(resp.data.content);
        })
        .catch((err) => {
            console.error(err);
        });
    },[]);

    if (!rec.length || !col.length) {
        return <div>Loading...</div>;
    }

    return (
        <Box sx={{ height: 800, width: '100%' }}>
            <DataGrid
                rows={rec}
                columns={col}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 10,
                        },
                    },
                }}
                pageSizeOptions={[10, 20, 30]}
                disableRowSelectionOnClick
            />
        </Box>
    );
}

export default WeightsView;