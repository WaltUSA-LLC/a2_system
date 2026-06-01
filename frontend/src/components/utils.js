import { GridFilterInputValue } from "@mui/x-data-grid";

export const minuteFilterOperators = [
        {
            label: "minutes =",
            value: "minutesEquals",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) === target;
            },
        },
        {
            label: "minutes >=",
            value: "minutesGreaterOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) >= target;
            },
        },
        {
            label: "minutes <=",
            value: "minutesLessOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) <= target;
            },
        },
];


export const hourFilterOperators = [
        {
            label: "hours =",
            value: "hoursEquals",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) === target;
            },
        },
        {
            label: "hours >",
            value: "hoursGreaterThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) > target;
            },
        },
        {
            label: "hours <",
            value: "hoursLessThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) < target;
            },
        },
];


export function formatSeconds(sec) {
    sec = Math.round(Number(sec ?? 0));
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}