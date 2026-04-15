import BaseTableView from "./BaseTableView"

function WeightsView() {
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
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
            flex: 1,
            type: 'string',
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
            field: 'NAU_prs',
            headerName: 'NAU (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'MES_prs',
            headerName: 'MES (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'ON_Time_Occupation',
            headerName: 'ON Time (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        {
            field: 'Mach_Efficiency',
            headerName: 'Mach Eff (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        {
            field: 'Comment',
            headerName: 'Comment',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
    ];
    return (
        <BaseTableView url="http://localhost:8000/base/mes" col={columns}/>
    );
}

export default WeightsView;

