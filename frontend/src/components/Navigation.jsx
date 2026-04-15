import { Link } from "react-router-dom";
import "./Navigation.css";

function Navigation() {
    return (
        <div className="nav">
            <Link to="/machs-view">View Machs</Link>
            <Link to="/sku-view">View SKU</Link>
            <Link to="/stops-view">View Stops</Link>
        </div>
    );
}

export default Navigation;