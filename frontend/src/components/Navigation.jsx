import { Link } from "react-router-dom";
import "./Navigation.css";

function Navigation() {
    return (
        <div className="nav">
            <Link to="/machs-view">View Machs</Link>
            <Link to="/sku-view">View SKU</Link>
            <Link to="/stops-view/time">View Stops (by time)</Link>
            <Link to="/stops-view/code">View Stops (by code)</Link>
            <Link to="/stops-view/mach">View Stops (by mach)</Link>
        </div>
    );
}

export default Navigation;